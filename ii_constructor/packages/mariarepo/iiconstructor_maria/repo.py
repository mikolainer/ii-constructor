# Copyright 2024 Николай Иванцов (tg/vk/wa: <@mikolainer> | <mikolainer@mail.ru>)
# Copyright 2024 Kirill Lesovoy
#
# Этот файл — часть "Конструктора интерактивных инструкций".
#
# Конструктор интерактивных инструкций — свободная программа:
# вы можете перераспространять ее и/или изменять ее на условиях
# Стандартной общественной лицензии GNU в том виде,
# в каком она была опубликована Фондом свободного программного обеспечения;
# либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.
# Конструктор интерактивных инструкций распространяется в надежде,
# что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ;
# даже без неявной гарантии ТОВАРНОГО ВИДА
# или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ.
# Подробнее см. в Стандартной общественной лицензии GNU.
#
# Вы должны были получить копию Стандартной общественной лицензии GNU
# вместе с этой программой. Если это не так,
# см. <https://www.gnu.org/licenses/>.


from collections.abc import Sequence

import mariadb
from iiconstructor_core.domain import (
    Connection,
    Hosting,
    InputDescription,
    Scenario,
    ScenarioInterface,
    Source,
    State,
    Step,
)
from iiconstructor_core.domain.exceptions import CoreException, NotExists
from iiconstructor_answers.plaintext import (
    PlainTextAnswer,
    PlainTextDescription,
)
from iiconstructor_core.domain.primitives import (
    Description,
    Name,
    ScenarioID,
    SourceInfo,
    StateAttributes,
    StateID,
)
from iiconstructor_levenshtain import LevenshtainVector, Synonym


class SourceMariaDB(Source):
    __db_connection: mariadb.Connection

    def __init__(self, conn: mariadb.Connection, id: ScenarioID) -> None:
        if not conn.open:
            raise CoreException(
                "подключение не открыто",
                "Не удалось открыть ",
            )

        self.__db_connection = conn

        cur = conn.cursor()
        cur.execute(
            "SELECT name, description FROM projects WHERE id=?",
            (id.value,),
        )
        conn.commit()
        name, descr = cur.fetchone()

        info = SourceInfo(Name(name), Description(descr))
        super().__init__(id, info)

    @staticmethod
    def __find_vector(
        list: list[InputDescription],
        name: Name,
    ) -> InputDescription:
        for vector in list:
            if vector.name() == name:
                return vector

        assert False

    def __do(self, query: str, data: Sequence = ()):
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(query, data)
        conn.commit()

    def get_layouts(self) -> str:
        query = (
            f"SELECT id, x, y FROM `states` WHERE project_id = {self.id.value}"
        )

        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

        result = list[str]()
        for id, x, y in cur:
            result.append(f"{id}: x={x}, y={y};")

        return "\n".join(result)

    def save_lay(self, id: StateID, x: float, y: float):
        self.__do(
            "UPDATE `states` SET `x` = ?, `y` = ? WHERE `states`.`project_id` = ? AND `states`.`id` = ?",
            (x, y, self.id.value, id.value),
        )

    def delete_state(self, state_id: StateID):
        self.__do(
            "DELETE FROM `states` WHERE `project_id` = ? AND `id` = ?",
            (self.id.value, state_id.value),
        )

    def get_states_by_name(self, name: Name) -> list[State]:
        query = f"SELECT id, IFNULL( name, id ) AS name, descr, answer, required FROM `states` WHERE project_id = {self.id.value} AND name = '{name.value}'"

        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

        result = list[State]()
        for _id, _name, _descr, _answer, _required in cur:
            result.append(
                State(
                    StateID(_id),
                    StateAttributes(
                        Name(_name),
                        Description(_descr),
                    ),
                    PlainTextDescription(PlainTextAnswer(_answer)),
                    _required,
                ),
            )

        return result

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        if not ids and ids is not None:
            return dict[StateID, State]()

        query = f"SELECT id, IFNULL( name, id ) AS name, descr, answer, required FROM `states` WHERE project_id = {self.id.value}"
        if ids is not None:
            where_append = []
            for id in ids:
                if id is None:
                    where_append.append("`id` = NULL")
                else:
                    where_append.append(f"`id` = {id.value}")

            query += f' AND ( {" OR ".join(where_append)} )'

        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

        result = dict[StateID, State]()
        for _id, _name, _descr, _answer, _required in cur:
            s_id = StateID(_id)
            result[s_id] = State(
                s_id,
                StateAttributes(
                    Name(_name),
                    Description(_descr),
                ),
                PlainTextDescription(PlainTextAnswer(_answer)),
                _required,
            )

        return result

    def steps(self, state_id: StateID) -> list[Step]:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "SELECT `from_state_id`, `to_state_id`, `vector_name` FROM `steps` WHERE `project_id` = ? AND (`to_state_id` = ? OR `from_state_id` = ?)",
            (self.id.value, state_id.value, state_id.value),
        )
        conn.commit()
        db_result = cur.fetchall()

        pairs_to = list[StateID]()
        pairs_from = list[StateID]()

        # получить все состояния и вектора
        s_id_list = list[StateID]()
        vector_names_list = list[Name]()

        for _from_state, _to_state, _vector_name in db_result:
            __vector_name = Name(_vector_name)
            if __vector_name not in vector_names_list:
                vector_names_list.append(__vector_name)

            __to_state_id: StateID = StateID(_to_state)
            if __to_state_id not in s_id_list:
                s_id_list.append(__to_state_id)

            __from_state_id: StateID | None = None
            if _from_state is not None:
                __from_state_id = StateID(_from_state)
                if __from_state_id not in s_id_list:
                    s_id_list.append(__from_state_id)

            if __from_state_id == state_id and __to_state_id not in pairs_from:
                pairs_from.append(__to_state_id)

            if __to_state_id == state_id and __from_state_id not in pairs_to:
                pairs_to.append(__from_state_id)

        f_states = self.states(s_id_list)
        f_vectors = self.select_vectors(vector_names_list)

        # получить state_mid
        state_mid = self.states([state_id])[state_id]

        conns = {
            "from": dict[StateID, Connection](),
            "to": dict[StateID, Connection](),
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
        for _from_state, _to_state, _vector_name in db_result:
            d_key = None
            if StateID(_from_state) == state_id:
                d_key = "from"

            if StateID(_to_state) == state_id:
                d_key = "to"

            assert d_key is not None

            __state_id: StateID | None = None
            if d_key == "from":
                __state_id = StateID(_to_state)
            elif _from_state is not None:
                __state_id = StateID(_from_state)

            _conn = conns[d_key][__state_id]
            step = Step(
                self.__find_vector(f_vectors, Name(_vector_name)),
                _conn,
            )
            _conn.steps.append(step)
            result.append(step)

        return result

    def is_enter(self, state: State) -> bool:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        # query = f"SELECT EXISTS( SELECT 1 FROM `steps` WHERE `project_id` = {self.id.value} AND ( `from_state_id` IS NULL AND `to_state_id` = {state.id().value} ))"
        # cur.execute(query)
        cur.execute(
            "SELECT EXISTS( SELECT 1 FROM `steps` WHERE `project_id` = ? AND ( `from_state_id` IS NULL AND `to_state_id` = ? ))",
            (self.id.value, state.id().value),
        )
        conn.commit()
        (result,) = cur.fetchone()
        return result

    def set_answer(self, state_id: StateID, data: PlainTextDescription):
        self.__do(
            "UPDATE `states` SET `answer` = ? WHERE `states`.`project_id` = ? AND `states`.`id` = ?",
            (data.value().as_text(), self.id.value, state_id.value),
        )

    def select_vectors(
        self,
        names: list[Name] | None = None,
    ) -> list["InputDescription"]:
        if not names and names is not None:
            return list["InputDescription"]()

        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        result = list[InputDescription]()

        if names is not None:
            _names = names
        else:
            _names = list[Name]()

            cur.execute(
                "SELECT DISTINCT `name` FROM `vectors` WHERE `project_id` = ?",
                (self.id.value,),
            )
            conn.commit()

            for (val,) in cur:
                _names.append(Name(val))

        for _name in _names:
            if not self.check_vector_exists(_name):
                continue

            cur.execute(
                "SELECT `value` FROM `synonyms` WHERE `project_id` = ? AND `group_name` = ?",
                (self.id.value, _name.value),
            )
            conn.commit()

            synonyms_g = list[Synonym]()
            for (val,) in cur:
                synonyms_g.append(Synonym(val))

            result.append(LevenshtainVector(_name, synonyms_g))

        return result

    def get_vector(self, name: Name) -> InputDescription:
        n_val = name.value

        if not self.check_vector_exists(name):
            raise NotExists(name, f'Вектор с именем "{name.value}"')

        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "SELECT `value` FROM `synonyms` WHERE `project_id` = ? AND `group_name` = ?",
            (self.id.value, n_val),
        )
        conn.commit()

        synonyms_g = list[Synonym]()
        for (val,) in cur:
            synonyms_g.append(Synonym(val))

        return LevenshtainVector(name, synonyms_g)

    def add_vector(self, input: InputDescription):
        _type = "synonyms_set"
        _name = input.name().value

        # создать группу синонимов (вектор)
        self.__do(
            "INSERT INTO `vectors` (`name`, `type`, `project_id`) VALUES (?, ?, ?)",
            (_name, _type, self.id.value),
        )

        # создать синонимы
        _name = input.name().value
        for index in range(len(input)):
            self.__do(
                "INSERT INTO `synonyms` (`group_name`, `value`, `project_id`) VALUES (?, ?, ?)",
                (_name, input.value(index).value(), self.id.value),
            )

    def remove_vector(self, name: Name):
        self.__do(
            "DELETE FROM `vectors` WHERE `vectors`.`project_id` = ? AND `vectors`.`name` = ?",
            (self.id.value, name.value),
        )

    def update_vector(self, name: Name, input: InputDescription):
        if not self.check_vector_exists(name):
            raise NotExists(name, "Вектор")
        
        self.__do(
            "DELETE FROM `synonyms` WHERE `synonyms`.`project_id` = ? AND `synonyms`.`group_name` = ?",
            (self.id.value, name.value),
        )

        _name = input.name().value
        for index in range(len(input)):
            self.__do(
                "INSERT INTO `synonyms` (`group_name`, `value`, `project_id`) VALUES (?, ?, ?)",
                (_name, input.value(index).value(), self.id.value),
            )

    def check_vector_exists(self, name: Name) -> bool:
        if name is None:
            return False

        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM `vectors` WHERE `project_id` = ? AND `name` = ?) as ans",
            (self.id.value, name.value),
        )
        conn.commit()
        (answer,) = cur.fetchone()
        return answer

    def create_state(
        self,
        attributes: StateAttributes,
        output: PlainTextDescription,
        required: bool = False,
    ) -> State:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()

        _proj_id = self.id.value
        _name = "DEFAULT"
        if attributes.name is not None:
            _name = f"'{attributes.name.value}'"
        _descr = "DEFAULT"
        if attributes.description is not None:
            _descr = f"'{attributes.description.value}'"
        _answ = "DEFAULT"
        if (
            output is not None
            and output.value() is not None
        ):
            _answ = f"'{output.value().as_text()}'"

        query = f"INSERT INTO `states` (`project_id`, `name`, `descr`, `answer`, `required`) VALUES (?, {_name}, {_descr}, {_answ}, ?) RETURNING `id`, `answer`, `name`, `descr`, `required`"
        cur.execute(query, (_proj_id, required))
        conn.commit()
        id, answer, name, descr, required = cur.fetchone()
        return State(
            StateID(id),
            StateAttributes(
                Name(name),
                Description(descr),
            ),
            PlainTextDescription(PlainTextAnswer(answer)),
            required,
        )

    def find_connections_to(self, state_id: StateID) -> list[Connection]:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "SELECT `from_state_id`, `to_state_id`, `vector_name` FROM `steps` WHERE `project_id` = ? AND (`to_state_id` = ?)",
            (self.id.value, state_id.value),
        )
        conn.commit()
        db_result = cur.fetchall()

        pairs_from: list[StateID] = []

        # получить все состояния и вектора
        s_id_list: list[StateID] = []
        vector_names_list: list[Name] = []

        for _from_state, _to_state, _vector_name in db_result:
            __vector_name = Name(_vector_name)
            if __vector_name not in vector_names_list:
                vector_names_list.append(__vector_name)

            if _from_state is not None:
                __from_state_id = StateID(_from_state)
                if __from_state_id not in s_id_list:
                    s_id_list.append(__from_state_id)
            else:
                __from_state_id = None

            if __from_state_id not in pairs_from:
                pairs_from.append(__from_state_id)

        f_states = self.states(s_id_list)
        f_vectors = self.select_vectors(vector_names_list)

        # получить state_mid
        state_mid = self.states([state_id])[state_id]

        conns = dict[StateID, Connection]()
        # сформировать все Connection
        for pair in pairs_from:
            if pair is not None:
                conns[pair] = Connection(f_states[pair], state_mid, [])

        # заполнить все Connection переходами и сформировать результат
        for _from_state, _to_state, _vector_name in db_result:
            if _from_state is not None:
                _conn = conns[StateID(_from_state)]
                step = Step(
                    self.__find_vector(f_vectors, Name(_vector_name)),
                    _conn,
                )
                _conn.steps.append(step)

        result = list[Connection]()
        for _conn in conns.values():
            result.append(_conn)

        return result

    def input_usage(self, input: InputDescription) -> list[Connection]:
        result = list[Connection]()

        conns = self.get_all_connections()

        for conn in conns["to"].values():
            conn: Connection = conn
            for step in conn.steps:
                if step.input == input:
                    result.append(conn)
                    break

        for conn_list in conns["from"].values():
            for conn in conn_list:
                conn: Connection = conn
                for step in conn.steps:
                    if step.input == input:
                        result.append(conn)
                        break

        return result

    def new_step(
        self,
        from_state: StateID | None,
        to_state: StateID,
        input_name: Name,
    ) -> Step:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO `steps` (`project_id`, `from_state_id`, `to_state_id`, `vector_name`) VALUES (?, ?, ?, ?) RETURNING `from_state_id`, `to_state_id`, `vector_name`",
            (
                self.id.value,
                None if from_state is None else from_state.value,
                to_state.value,
                input_name.value,
            ),
        )
        conn.commit()

        from_id, to_id, in_name = cur.fetchone()
        __from_id = None if from_id is None else StateID(from_id)
        __to_id = StateID(to_id)
        states = self.states([__from_id, __to_id])
        state_from = (
            states[StateID(from_id)]
            if StateID(from_id) in states.keys()
            else None
        )
        state_to = states[StateID(to_id)]
        input: LevenshtainVector = self.get_vector(Name(in_name))

        return Step(
            input,
            Connection(state_from, state_to, None)#input.synonyms.synonyms), # wtf?
        )

    def delete_step(
        self,
        from_state: StateID | None,
        to_state: StateID | None,
        input_name: Name | None = None,
    ):
        if from_state is None:
            self.__do(
                f"DELETE FROM `steps` WHERE `project_id` = {self.id.value}"
                f" AND `from_state_id` IS NULL"
                f" AND `to_state_id` = {to_state.value}",
            )
        else:
            self.__do(
                f"DELETE FROM `steps` WHERE `project_id` = {self.id.value}"
                f" AND `from_state_id` = {from_state.value}"
                f" AND `vector_name` = '{input_name.value}'",
            )

    def get_all_connections(self) -> dict[str, dict]:
        conn: mariadb.Connection = self.__db_connection
        cur = conn.cursor()
        cur.execute(
            "SELECT `from_state_id`, `to_state_id`, `vector_name` FROM `steps` WHERE `project_id` = ? AND `from_state_id` IS NULL",
            (self.id.value,),
        )
        conn.commit()
        db_result_to = cur.fetchall()

        cur.execute(
            "SELECT `from_state_id`, `to_state_id`, `vector_name` FROM `steps` WHERE `project_id` = ? AND NOT `from_state_id` IS NULL",
            (self.id.value,),
        )
        conn.commit()
        db_result_from = cur.fetchall()

        result = {
            "from": dict[StateID, list[Connection]](),
            "to": dict[StateID, Connection](),
        }

        f_states = self.states()
        # сформировать все Connection
        for _from_state, _to_state, _vector_name in db_result_from:
            # raise not _from_state is None
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

            if skip_append:
                continue
            __conn_list.append(Connection(__from_state, __to_state, []))

        for _from_state, _to_state, _vector_name in db_result_to:
            __to_state_id = StateID(_to_state)
            if __to_state_id in result["to"].keys():
                continue

            result["to"][__to_state_id] = Connection(
                None,
                f_states[__to_state_id],
                [],
            )

        f_vectors = self.select_vectors()

        # заполнить все Connection переходами
        _conn: Connection | None = None
        for _from_state, _to_state, _vector_name in db_result_from:
            __from_state_id = StateID(_from_state)
            __to_state_id = StateID(_to_state)
            # raise not _from_state is None
            for __conn in result["from"][__from_state_id]:
                if __conn.to_state.id() == __to_state_id:
                    _conn = __conn
                    break

            step = Step(
                self.__find_vector(f_vectors, Name(_vector_name)),
                _conn,
            )
            _conn.steps.append(step)  # вроде должны быть уникальными

        for _from_state, _to_state, _vector_name in db_result_to:
            __from_state_id = None  # always is None
            __to_state_id = StateID(_to_state)
            _conn = result["to"][__to_state_id]
            step = Step(
                self.__find_vector(f_vectors, Name(_vector_name)),
                _conn,
            )
            _conn.steps.append(step)  # вроде должны быть уникальными

        return result

#    def set_synonym_value(
#        self,
#        input_name: str,
#        old_synonym: str,
#        new_synonym: str,
#    ):
#        self.__do(
#            "UPDATE `synonyms` SET `value`= ? WHERE `project_id`= ? AND `group_name`= ? AND `value` = ?",
#            (new_synonym, self.id.value, input_name, old_synonym),
#        )
#
#    def create_synonym(self, input_name: str, new_synonym: str):
#        self.__do(
#            "INSERT INTO `synonyms` (`project_id`, `group_name`, `value`) VALUES (?, ?, ?)",
#            (self.id.value, input_name, new_synonym),
#        )
#
#    def remove_synonym(self, input_name: str, synonym: str):
#        self.__do(
#            "DELETE FROM `synonyms` WHERE `project_id` = ? AND `group_name` = ? AND `value` = ?",
#            (self.id.value, input_name, synonym),
#        )

    def rename_state(self, state: StateID, name: Name):
        self.__do(
            "UPDATE `states` SET `name`= ? WHERE `project_id`= ? AND `id`= ?",
            (name.value, self.id.value, state.value),
        )

    def rename_vector(self, old_name: Name, new_name: Name):
        self.__do(
            "UPDATE `vectors` SET `name`= ? WHERE `project_id`= ? AND `name`= ?",
            (new_name.value, self.id.value, old_name.value),
        )


class HostingMaria(Hosting):
    __connection: mariadb.Connection | None

    def __init__(self) -> None:
        self.__connection = None

    def connected(self) -> bool:
        if not isinstance(self.__connection, mariadb.Connection):
            return False

        return self.__connection.open

    def connect(self, ip: str, port: int, username: str, password: str):
        if not self.connected():
            try:
                self.__connection = mariadb.connect(
                    host=ip,
                    port=port,
                    user=username,
                    password=password,
                    database="ii_constructor",
                )
                self.__connection.auto_reconnect = True
            except mariadb.Error:
                self.__connection = None
                raise

    def get_scenario(self, id: ScenarioID) -> ScenarioInterface:
        if not self.connected():
            raise CoreException("БД не подключена")

        return Scenario(SourceMariaDB(self.__connection, id))

    def add_source(self, info: SourceInfo) -> ScenarioID:
        if not self.connected():
            raise CoreException("БД не подключена")

        conn: mariadb.Connection = self.__connection
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO `projects` (`name`, `description`) VALUES (?, ?) RETURNING `id`",
            (info.name.value, info.description.value),
        )
        conn.commit()
        (result,) = cursor.fetchone()
        return ScenarioID(result)

    def sources(self) -> list[tuple[int, str, str]]:
        result = list[tuple[int, str, str]]()

        conn: mariadb.Connection = self.__connection
        cursor = conn.cursor()

        cursor.execute("SELECT `id`, `name`, `description` FROM `projects`")
        conn.commit()

        for row in cursor:
            result.append(row)

        return result
