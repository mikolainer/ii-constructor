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


from iiconstructor_core.domain import (
    Connection,
    Hosting,
    InputDescription,
    PossibleInputs,
    Scenario,
    ScenarioInterface,
    Source,
    State,
    Step,
)
from iiconstructor_core.domain.exceptions import Exists, NotExists
from iiconstructor_core.domain.primitives import (
    Name,
    OutputDescription,
    ScenarioID,
    SourceInfo,
    StateAttributes,
    StateID,
)
from iiconstructor_levenshtain import LevenshtainVector, Synonym


class SourceInMemory(Source):
    __new_state_id: int
    __states: dict[StateID, State]
    __input_vectors: PossibleInputs

    __connections: dict[str, dict]
    """ все связи\n
    ключи: 'from', 'to'; значения: to=dict[StateID, Connection], from=dict[StateID, list[Connection]]
    """

    def __init__(self, id: ScenarioID | None, info: SourceInfo) -> None:
        super().__init__(id, info)

        self.__states = {}
        self.__new_state_id = 0
        self.__connections = {"from": {}, "to": {}}
        self.__input_vectors = PossibleInputs()

    def get_layouts(self) -> str:
        """-"""

    def save_lay(self, id: StateID, x: float, y: float):
        """-"""

    def delete_state(self, state_id: StateID):
        self.__states.pop(state_id)

    def get_states_by_name(self, name: Name) -> list[State]:
        """получить все состояния с данным именем"""
        result = list[State]()
        for state in self.__states.values():
            if state.attributes.name == name:
                result.append(state)

        return result

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        """получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния"""
        if ids is None:
            return self.__states

        states: dict[StateID, State] = {}
        for id in ids:
            if id not in self.__states.keys():
                raise NotExists(id, f'Нет состояния с id "{id.value}"')
            states[id] = self.__states[id]

        return states

    def steps(self, state_id: StateID) -> list[Step]:
        """получить все переходы, связанные с состоянием по его идентификатору"""
        result = list[Step]()

        if state_id in self.__connections["from"].keys():
            for conn in self.__connections["from"][state_id]:
                for step in conn.steps:
                    result.append(step)

        if state_id in self.__connections["to"].keys():
            for step in self.__connections["to"][state_id].steps:
                result.append(step)

        for conn in self.find_connections_to(state_id):
            for step in conn.steps:
                result.append(step)

        return list(result)

    def is_enter(self, state: State) -> bool:
        """Проверить является ли состояние входом"""
        return state.id() in self.__connections["to"].keys()

    # сеттеры

    def set_answer(self, state_id: StateID, data: OutputDescription):
        """Изменить ответ состояния"""
        self.__states[state_id].set_output(data)

    # векторы

    def select_vectors(
        self,
        names: list[Name] | None = None,
    ) -> list["InputDescription"]:
        """
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        """
        return self.__input_vectors.select(names)

    def get_vector(self, name: Name) -> InputDescription:
        """
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        """
        return self.__input_vectors.get(name)

    def add_vector(self, input: InputDescription):
        """
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        """
        return self.__input_vectors.add(input)

    def remove_vector(self, name: Name):
        """
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        """
        input = self.get_vector(name)
        if len(self.input_usage(input)) > 0:
            raise Exists(
                name,
                f'Вектор с именем "{name.value}" используется в существующих переходах',
            )

        return self.__input_vectors.remove(name)

    def check_vector_exists(self, name: Name) -> bool:
        """
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        """
        return self.__input_vectors.exists(name)

    # Scenario private
    def create_state(
        self,
        attributes: StateAttributes,
        output: OutputDescription,
        required: bool = False,
    ) -> State:
        new_state = State(StateID(self.__new_state_id), attributes, output, required)
        self.__new_state_id += 1
        self.__states[new_state.id()] = new_state
        return new_state

    def find_connections_to(self, state_id: StateID) -> list[Connection]:
        result = list[Connection]()
        for connections in self.__connections["from"].values():
            for conn in connections:
                to_state: State = conn.to_state
                if to_state is not None and to_state.id() == state_id:
                    result.append(conn)

        return result

    def input_usage(self, input: InputDescription) -> list[Connection]:
        """Получить связи, в которых используется вектор"""
        result = list[Connection]()

        for conn in self.__connections["to"].values():
            conn: Connection = conn
            for step in conn.steps:
                if step.input == input:
                    result.append(conn)
                    break

        for conn_list in self.__connections["from"].values():
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
        if not isinstance(to_state, StateID):
            raise TypeError(to_state)
        if not isinstance(input_name, Name):
            raise TypeError(input_name)
        if not self.check_vector_exists(input_name):
            raise ValueError(input_name)

        new_step: Step

        if from_state is None:  # точка входа
            conn = Connection(None, self.__states[to_state], [])
            new_step = Step(self.__input_vectors.get(input_name), conn)
            conn.steps.append(new_step)
            self.__connections["to"][to_state] = conn

        else:  # переход между состояниями
            if not isinstance(from_state, StateID):
                raise TypeError(from_state)
            if not isinstance(to_state, StateID):
                raise TypeError(to_state)

            state_to = self.__states[to_state]
            new_conn = Connection(
                self.__states[from_state],
                self.__states[to_state],
                [],
            )

            # если это первый переход из этого состояния
            if from_state not in self.__connections["from"].keys():
                self.__connections["from"][from_state] = [new_conn]
                conn = new_conn

            else:
                found: Connection = None
                for _conn in self.__connections["from"][from_state]:
                    _conn: Connection = _conn
                    if _conn.to_state == state_to:
                        found = _conn
                        break

                if found is None:
                    # это первый переход из state_from в state_to
                    self.__connections["from"][from_state].append(new_conn)
                    conn = new_conn
                else:
                    conn = found

            for step in conn.steps:
                if step.input.name() == input_name:
                    raise RuntimeError("переход уже существует")

            new_step = Step(self.get_vector(input_name), conn)
            conn.steps.append(new_step)

        return new_step

    def delete_step(
        self,
        from_state: StateID | None,
        to_state: StateID | None,
        input_name: Name | None = None,
    ):
        if from_state is None:  # точка входа
            if not isinstance(to_state, StateID):
                raise TypeError(to_state)
            if to_state not in self.__connections["to"]:
                raise ValueError(to_state)

            self.__connections["to"].pop(to_state)

        else:  # переход
            if not isinstance(from_state, StateID):
                raise TypeError(from_state)
            if from_state not in self.__connections["from"].keys():
                raise ValueError(from_state)

            for conn in self.__connections["from"][from_state]:
                conn: Connection = conn

                for step in conn.steps:
                    step: Step = step
                    if step.input.name() == input_name:
                        conn.steps.remove(step)

                        if len(conn.steps) == 0:
                            self.__connections["from"][from_state].remove(conn)

                        if len(self.__connections["from"][from_state]) == 0:
                            self.__connections["from"].pop(from_state)

                        return

    def get_all_connections(self) -> dict[str, dict]:
        return self.__connections

#    def set_synonym_value(
#        self,
#        input_name: str,
#        old_synonym: str,
#        new_synonym: str,
#    ):
#        vector: LevenshtainVector = self.get_vector(Name(input_name))
#        synonym = Synonym(new_synonym)
#        index = vector.synonyms.synonyms.index(Synonym(old_synonym))
#        vector.synonyms.synonyms[index] = synonym
#
#    def create_synonym(self, input_name: str, new_synonym: str):
#        vector: LevenshtainVector = self.get_vector(Name(input_name))
#        vector.synonyms.synonyms.append(Synonym(new_synonym))
#
#    def remove_synonym(self, input_name: str, synonym: str):
#        vector: LevenshtainVector = self.get_vector(Name(input_name))
#        index = vector.synonyms.synonyms.index(Synonym(synonym))
#        vector.synonyms.synonyms.pop(index)

    def rename_state(self, state: StateID, name: Name):
        self.states([state])[state].attributes.name = name

    def rename_vector(self, old_name: Name, new_name: Name):
        self.get_vector(old_name).set_name(new_name)


class HostingInmem(Hosting):
    __sources: dict[ScenarioID, ScenarioInterface]
    __next_id: ScenarioID

    def __init__(self) -> None:
        self.__sources = {}
        self.__next_id = ScenarioID(0)

    def get_scenario(self, id: ScenarioID) -> ScenarioInterface:
        return self.__sources[id]

    def add_source(self, info: SourceInfo) -> ScenarioID:
        id = self.__next_id
        self.__next_id = ScenarioID(self.__next_id.value + 1)
        self.__sources[id] = Scenario(SourceInMemory(id, info))
        return id

    def sources(self) -> list[tuple[int, str, str]]:
        result = list[tuple[int, str, str]]

        for scenario in self.__sources.values():
            src: Source = scenario.source()
            result.append(
                (src.id.value, src.info.name.value, src.info.description),
            )

        return result
