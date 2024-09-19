import mariadb

from typing import Optional, Any, Sequence

from alicetool.domain.core.primitives import Name, Description, StateID, ScenarioID, Answer, Output, StateAttributes, SourceInfo
from alicetool.domain.core.bot import Source, Hosting, State, ScenarioInterface, Scenario, Step, InputDescription, Connection
from alicetool.domain.core.exceptions import *
from alicetool.domain.inputvectors.levenshtain import LevenshtainVector, SynonymsGroup, Synonym

class SourceMariaDB(Source):
    __db_connection: mariadb.Connection

    def __init__(self, conn: mariadb.Connection, id: ScenarioID) -> None:
        if not conn.open:
            raise CoreException('подключение не открыто', 'Не удалось открыть ')

        self.__db_connection = conn

        cur = conn.cursor()
        cur.execute("SELECT name, description FROM projects WHERE id=?", (id.value,))
        conn.commit()
        name, descr = cur.fetchone()

        info = SourceInfo(Name(name), Description(descr))
        super().__init__(id, info)

    @staticmethod
    def __find_vector(list: list[InputDescription], name: Name) -> InputDescription:
        for vector in list:
            if vector.name() == name:
                return vector

        assert False

    def __do(self, query:str, data: Sequence = ()):
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(query, data)
        conn.commit()

    def delete_state(self, state_id:StateID):
        self.__do("DELETE FROM `states` WHERE `project_id` = ? AND `id` = ?", (self.id.value, state_id.value))

    def get_states_by_name(self, name: Name) -> list[State]:
        query = f"SELECT id, IFNULL( name, id ) AS name, descr, answer, required FROM `states` WHERE project_id = {self.id.value} AND name = '{name.value}'"

        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

        result = list[State]()
        for (_id, _name, _descr, _answer, _required) in cur:
            result.append(State(StateID(_id), StateAttributes(Output(Answer(_answer)), Name(_name), Description(_descr)), _required))

        return result
    
    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        if ids == []:
            return dict[StateID, State]()

        query = f"SELECT id, IFNULL( name, id ) AS name, descr, answer, required FROM `states` WHERE project_id = {self.id.value}"
        if not ids is None:
            where_append = []
            for id in ids:
                if id is None:
                    where_append.append('`id` = NULL')
                else:
                    where_append.append(f"`id` = {id.value}")
            
            query += f' AND ( {" OR ".join(where_append)} )'

        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

        result = dict[StateID, State]()
        for (_id, _name, _descr, _answer, _required) in cur:
            s_id = StateID(_id)
            result[s_id] = (State(s_id, StateAttributes(Output(Answer(_answer)), Name(_name), Description(_descr)), _required))

        return result
    
    def steps(self, state_id:StateID) -> list[Step]:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "SELECT `from_state_id`, `to_state_id`, `vector_name` FROM `steps` WHERE `project_id` = ? AND (`to_state_id` = ? OR `from_state_id` = ?)",
            (self.id.value, state_id.value, state_id.value)
        )
        conn.commit()
        db_result = cur.fetchall()

        pairs_to = list[StateID]()
        pairs_from = list[StateID]()

        # получить все состояния и вектора
        s_id_list = list[StateID]()
        vector_names_list = list[Name]()

        for (_from_state, _to_state, _vector_name) in db_result:
            __vector_name = Name(_vector_name)
            if not __vector_name in vector_names_list:
                vector_names_list.append(__vector_name)

            __to_state_id: StateID = StateID(_to_state)
            if not __to_state_id in s_id_list:
                s_id_list.append(__to_state_id)

            __from_state_id: Optional[StateID] = None
            if not _from_state is None:
                __from_state_id = StateID(_from_state)
                if not __from_state_id in s_id_list:
                    s_id_list.append(__from_state_id)

            if __from_state_id == state_id and not __to_state_id in pairs_from:
                pairs_from.append(__to_state_id)

            if __to_state_id == state_id and not __from_state_id in pairs_to:
                pairs_to.append(__from_state_id)

        f_states = self.states(s_id_list)
        f_vectors = self.select_vectors(vector_names_list)

        # получить state_mid
        state_mid = self.states([state_id])[state_id]

        conns = {
            "from": dict[StateID, Connection](),
            "to": dict[StateID, Connection]()
        }
        # сформировать все Connection
        for pair in pairs_to:
            if pair is None:
                conns["to"][None] = Connection(None, state_mid, [])
            else:
                conns["to"][pair] = Connection(f_states[pair], state_mid, [])

        for pair in pairs_from:
            conns["from"][pair] = Connection(state_mid, f_states[pair], [])

        # заполнить все Connection переходами и сформировать результат
        result = list[Step]()
        for (_from_state, _to_state, _vector_name) in db_result:
            d_key = None
            if StateID(_from_state) == state_id:
                d_key = "from"

            if StateID(_to_state) == state_id:
                d_key = "to"

            assert not d_key is None

            __state_id: Optional[StateID] = None
            if d_key == "from":
                __state_id = StateID(_to_state)
            elif not _from_state is None:
                __state_id = StateID(_from_state)

            _conn = conns[d_key][__state_id]
            step = Step(self.__find_vector(f_vectors, Name(_vector_name)), _conn)
            _conn.steps.append(step)
            result.append(step)

        return result
 
    def is_enter(self, state:State) -> bool:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        #query = f"SELECT EXISTS( SELECT 1 FROM `steps` WHERE `project_id` = {self.id.value} AND ( `from_state_id` IS NULL AND `to_state_id` = {state.id().value} ))"
        #cur.execute(query)
        cur.execute(
            "SELECT EXISTS( SELECT 1 FROM `steps` WHERE `project_id` = ? AND ( `from_state_id` IS NULL AND `to_state_id` = ? ))",
            (self.id.value, state.id().value)
        )
        conn.commit()
        (result,) = cur.fetchone()
        return result

    def set_answer(self, state_id:StateID, data:Output):
        self.__do("UPDATE `states` SET `answer` = ? WHERE `states`.`project_id` = ? AND `states`.`id` = ?", (data.value.text, self.id.value, state_id.value))

    def select_vectors(self, names:Optional[list[Name]] = None) -> list['InputDescription']:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        result = list[InputDescription]()

        if names == []:
            return list['InputDescription']()
        elif not names is None:
            _names = names
        else:
            _names = list[Name]()

            cur.execute("SELECT DISTINCT `name` FROM `vectors` WHERE `project_id` = ?", (self.id.value,))
            conn.commit()

            for (val,) in cur:
                _names.append(Name(val))

        for _name in _names:
            if not self.check_vector_exists(_name):
                continue

            cur.execute("SELECT `value` FROM `synonyms` WHERE `project_id` = ? AND `group_name` = ?", (self.id.value, _name.value))
            conn.commit()

            synonyms_g = SynonymsGroup()
            for (val,) in cur:
                synonyms_g.synonyms.append(Synonym(val))
            
            result.append(LevenshtainVector(_name, synonyms_g))

        return result
    
    def get_vector(self, name:Name) -> InputDescription:
        n_val = name.value

        if not self.check_vector_exists(name):
            raise NotExists(name, f'Вектор с именем "{name.value}"')

        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute("SELECT `value` FROM `synonyms` WHERE `project_id` = ? AND `group_name` = ?", (self.id.value, n_val))
        conn.commit()

        synonyms_g = SynonymsGroup()
        for (val,) in cur:
            synonyms_g.synonyms.append(Synonym(val))

        return LevenshtainVector(name, synonyms_g)

    def add_vector(self, input: InputDescription):
        _type = 'synonyms_set'
        _name = input.name().value
        
        # создать группу синонимов (вектор)
        self.__do("INSERT INTO `vectors` (`name`, `type`, `project_id`) VALUES (?, ?, ?)", (_name, _type, self.id.value))

        # создать синонимы
        for synonym in input.synonyms.synonyms:
            self.__do("INSERT INTO `synonyms` (`group_name`, `value`, `project_id`) VALUES (?, ?, ?)", (_name, synonym.value, self.id.value))

    def remove_vector(self, name:Name):
        self.__do("DELETE FROM `vectors` WHERE `vectors`.`project_id` = ? AND `vectors`.`name` = ?", (self.id.value, name.value))

    def check_vector_exists(self, name:Name) -> bool:
        if name is None: return False
        
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute("SELECT EXISTS(SELECT 1 FROM `vectors` WHERE `project_id` = ? AND `name` = ?) as ans", (self.id.value, name.value))
        conn.commit()
        (answer,) = cur.fetchone()
        return answer

    def add_state(self, id:StateID, name:Name, output:Output):
        ''' не используется (достаточно подключиться) '''
        return

    def create_state(self, attributes:StateAttributes, required:bool = False) -> State:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()

        _proj_id = self.id.value
        _name = 'DEFAULT'
        if not attributes.name is None: _name = f"'{attributes.name.value}'"
        _descr = 'DEFAULT'
        if not attributes.description is None: _descr = f"'{attributes.description.value}'"
        _answ = 'DEFAULT'
        if not attributes.output is None and not attributes.output.value is None: _answ = f"'{attributes.output.value.text}'"

        query = f"INSERT INTO `states` (`project_id`, `name`, `descr`, `answer`, `required`) VALUES (?, {_name}, {_descr}, {_answ}, ?) RETURNING `id`, `answer`, `name`, `descr`, `required`"
        cur.execute(query, (_proj_id, required))
        conn.commit()
        id, answer, name, descr, required = cur.fetchone()
        return State(StateID(id), StateAttributes(Output(Answer(answer)), Name(name), Description(descr)), required)

    def find_connections_to(self, state_id:StateID) -> list[Connection]:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "SELECT `from_state_id`, `to_state_id`, `vector_name` FROM `steps` WHERE `project_id` = ? AND (`to_state_id` = ?)",
            (self.id.value, state_id.value)
        )
        conn.commit()
        db_result = cur.fetchall()

        pairs_from = list[StateID]

        # получить все состояния и вектора
        s_id_list = list[StateID]
        vector_names_list = list[Name]

        for (_from_state, _to_state, _vector_name) in db_result:
            __vector_name = Name(_vector_name)
            if not __vector_name in vector_names_list:
                vector_names_list.append(__vector_name)

            if not _from_state is None: 
                __from_state_id = StateID(_from_state)
                if not __from_state_id in s_id_list:
                    s_id_list.append(__from_state_id)
            else:
                __from_state_id = None

            if not __from_state_id in pairs_from:
                pairs_from.append(__from_state_id)
            

        f_states = self.states(s_id_list)
        f_vectors = self.select_vectors(vector_names_list)

        # получить state_mid
        state_mid = self.states([state_id])[state_id]

        conns = dict[StateID, Connection]()
        # сформировать все Connection
        for pair in pairs_from:
            if not pair is None:
                conns[pair] = Connection(f_states[pair], state_mid, [])

        # заполнить все Connection переходами и сформировать результат
        for (_from_state, _to_state, _vector_name) in db_result:
            if not _from_state is None:
                _conn = conns[StateID(_from_state)]
                step = Step(self.__find_vector(f_vectors, Name(_vector_name)), _conn)
                _conn.steps.append(step)

        result = list[Connection]()
        for _conn in conns.values():
            result.append(_conn)

        return result

    def input_usage(self, input: InputDescription) -> list[Connection]:
        result = list[Connection]()

        conns = self.get_all_connections()
        
        for conn in conns['to'].values():
            conn: Connection = conn
            for step in conn.steps:
                if step.input == input:
                    result.append(conn)
                    break
        
        for conn_list in conns['from'].values():
            for conn in conn_list:
                conn: Connection = conn
                for step in conn.steps:
                    if step.input == input:
                        result.append(conn)
                        break
        
        return result

    def new_step(self, from_state: Optional[StateID], to_state: StateID, input_name: Name) -> Step:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO `steps` (`project_id`, `from_state_id`, `to_state_id`, `vector_name`) VALUES (?, ?, ?, ?) RETURNING `from_state_id`, `to_state_id`, `vector_name`",
            (self.id.value, None if from_state is None else from_state.value, to_state.value, input_name.value)
        )
        conn.commit()
        
        from_id, to_id, in_name = cur.fetchone()
        __from_id = None if from_id is None else StateID(from_id)
        __to_id = StateID(to_id)
        states = self.states([__from_id, __to_id])
        state_from = states[StateID(from_id)] if StateID(from_id) in states.keys() else None
        state_to = states[StateID(to_id)]
        input:LevenshtainVector = self.get_vector(Name(in_name))
        
        return Step(input, Connection(state_from, state_to, input.synonyms.synonyms))
    
    def delete_step(self, from_state: Optional[StateID], to_state: Optional[StateID], input_name: Optional[Name] = None):
        if from_state is None:
            self.__do(
                f"DELETE FROM `steps` WHERE `project_id` = {self.id.value}"
                f" AND `from_state_id` IS NULL"
                f" AND `to_state_id` = {to_state.value}"
            )
        else:
            self.__do(
                f"DELETE FROM `steps` WHERE `project_id` = {self.id.value}"
                f" AND `from_state_id` = {from_state.value}"
                f" AND `vector_name` = '{input_name.value}'"
            )

    def get_all_connections(self) -> dict[str, dict]:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "SELECT `from_state_id`, `to_state_id`, `vector_name` FROM `steps` WHERE `project_id` = ? AND `from_state_id` IS NULL",
            (self.id.value,)
        )
        conn.commit()
        db_result_to = cur.fetchall()

        cur.execute(
            "SELECT `from_state_id`, `to_state_id`, `vector_name` FROM `steps` WHERE `project_id` = ? AND NOT `from_state_id` IS NULL",
            (self.id.value,)
        )
        conn.commit()
        db_result_from = cur.fetchall()

        result = {
            'from': dict[StateID, list[Connection]](),
            'to': dict[StateID, Connection](),
        }

        f_states = self.states()
        # сформировать все Connection
        for (_from_state, _to_state, _vector_name) in db_result_from:
            #raise not _from_state is None
            __to_state_id = StateID(_to_state)
            __to_state = f_states[__to_state_id]

            __from_state_id = StateID(_from_state)
            __from_state = f_states[__from_state_id]

            if __from_state_id in result["from"].keys():
                __conn_list = result["from"][__from_state_id]
            else:
                __conn_list = list[Connection]()
                result["from"][__from_state_id] = __conn_list

            skip_append = False
            for _conn in __conn_list:
                if _conn.to_state == __to_state:
                    skip_append = True
                    break
            
            if (skip_append): continue
            __conn_list.append(Connection(__from_state, __to_state, []))

        for (_from_state, _to_state, _vector_name) in db_result_to:
            __to_state_id = StateID(_to_state)
            if __to_state_id in result["to"].keys():
                continue

            result["to"][__to_state_id] = Connection(None, f_states[__to_state_id], [])

        f_vectors = self.select_vectors()

        # заполнить все Connection переходами
        for (_from_state, _to_state, _vector_name) in db_result_from:
            __from_state_id = StateID(_from_state)
            __to_state_id = StateID(_to_state)
            #raise not _from_state is None
            _conn: Connection
            for __conn in result["from"][__from_state_id]:
                if __conn.to_state.id() == __to_state_id:
                    _conn = __conn
                    break
            
            step = Step(self.__find_vector(f_vectors, Name(_vector_name)), _conn)
            _conn.steps.append(step) # вроде должны быть уникальными


        for (_from_state, _to_state, _vector_name) in db_result_to:
            __from_state_id = None # always is None
            __to_state_id = StateID(_to_state)
            _conn = result["to"][__to_state_id]
            step = Step(self.__find_vector(f_vectors, Name(_vector_name)), _conn)
            _conn.steps.append(step) # вроде должны быть уникальными

        return result
    
    def set_synonym_value(self, input_name: str, old_synonym: str, new_synonym: str):
        self.__do("UPDATE `synonyms` SET `value`= ? WHERE `project_id`= ? AND `group_name`= ? AND `value` = ?", (new_synonym, self.id.value, input_name, old_synonym))
            
    def create_synonym(self, input_name: str, new_synonym: str):
        self.__do("INSERT INTO `synonyms` (`project_id`, `group_name`, `value`) VALUES (?, ?, ?)", (self.id.value, input_name, new_synonym))
            
    def remove_synonym(self, input_name: str, synonym: str):
        self.__do("DELETE FROM `synonyms` WHERE `project_id` = ? AND `group_name` = ? AND `value` = ?", (self.id.value, input_name, synonym))
    
    def rename_state(self, state:StateID, name:Name):
        self.__do("UPDATE `states` SET `name`= ? WHERE `project_id`= ? AND `id`= ?", (name.value, self.id.value, state.value))

    def rename_vector(self, old_name:Name, new_name: Name):
        self.__do("UPDATE `vectors` SET `name`= ? WHERE `project_id`= ? AND `name`= ?", (new_name.value, self.id.value, old_name.value))

class HostingMaria(Hosting):
    __connection: Optional[mariadb.Connection]
    def __init__(self) -> None:
        self.__connection = None

    def connected(self) -> bool:
        if not isinstance(self.__connection, mariadb.Connection):
            return False
        
        return self.__connection.open

    def connect(self, ip:str, port:int, username:str, password:str):
        if not self.connected():
            try:
                self.__connection = mariadb.connect(
                    host=ip,
                    port=port,
                    user=username,
                    password=password,
                    database='ii_constructor'
                )
                self.__connection.auto_reconnect = True
            except mariadb.Error as e:
                self.__connection = None
                raise

    def get_scenario(self, id:ScenarioID) -> ScenarioInterface:
        if not self.connected():
            raise CoreException('БД не подключена')
        
        return Scenario(SourceMariaDB(self.__connection, id))
    
    def add_source(self, info:SourceInfo) -> ScenarioID:
        if not self.connected():
            raise CoreException('БД не подключена')
        
        conn:mariadb.Connection = self.__connection
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO `projects` (`name`, `description`) VALUES (?, ?) RETURNING `id`",
            (info.name.value, info.description.value)
        )
        conn.commit()
        (result,) = cursor.fetchone()
        return ScenarioID(result)
    