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


from xml.etree.ElementTree import Element, fromstring, indent, tostring

from iiconstructor_core.domain import Connection, InputDescription, State, Step
from iiconstructor_core.domain.exceptions import CoreException, Exists
from iiconstructor_core.domain.primitives import (
    Answer,
    Description,
    Name,
    OutputDescription,
    ScenarioID,
    SourceInfo,
    StateAttributes,
    StateID,
)
from iiconstructor_levenshtain import LevenshtainVector, Synonym, SynonymsGroup
from iiconstructor_maria.repo import SourceMariaDB
from iiconstructor_yandex_alice.ports import HostingInterface, ScenarioInterface
from PySide6.QtWidgets import QMessageBox, QWidget


class Hosting:
    @staticmethod
    def make_scenario(
        hosting: HostingInterface,
        info: SourceInfo,
    ) -> "Server":
        """создаёт заготовку сценария для алисы"""
        new_scenario = hosting.get_scenario(hosting.add_source(info))

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name("Старт"),
                SynonymsGroup(
                    [
                        Synonym("Алиса, запусти навык ..."),
                    ],
                ),
            ),
        )

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name("Информация"),
                SynonymsGroup(
                    [
                        Synonym("Информация"),
                        Synonym("Справка"),
                        Synonym("Расскажи о себе"),
                    ],
                ),
            ),
            True,
        )

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name("Помощь"),
                SynonymsGroup(
                    [
                        Synonym("Помощь"),
                        Synonym("Помоги"),
                        Synonym("Как выйти"),
                    ],
                ),
            ),
            True,
        )

        return Server(new_scenario)

    @staticmethod
    def load_scenario(
        hosting: HostingInterface,
        data: str,
        id_map: dict[int, int] = None,
    ) -> "Server":
        """id_map: key - orig, val - new"""
        root: Element = fromstring(data)

        info = SourceInfo(
            Name(root.attrib["Название"]),
            Description(root.attrib["Краткое_описание"]),
        )
        scenario = hosting.get_scenario(hosting.add_source(info))

        # добавляем векторы
        for elem in root.find("Управляющие_воздействия").findall("Описание"):
            synonyms = list[Synonym]()
            for synonym in elem.findall("Синоним"):
                synonyms.append(Synonym(synonym.text))

            scenario.add_vector(
                LevenshtainVector(
                    Name(elem.attrib["Название"]),
                    SynonymsGroup(synonyms),
                ),
            )

        # добавляем состояния
        for elem in root.find("Состояния").findall("Состояние"):
            state: State = scenario.source().create_state(
                StateAttributes(
                    OutputDescription(Answer(elem.text)),
                    Name(elem.attrib["Название"]),
                    Description(""),
                ),
            )
            if id_map is not None:
                id_map[int(elem.attrib["Идентификатор"])] = state.id().value

        # добавляем входы
        for elem in root.find("Входы").findall("Точка_входа"):
            if id_map is None:
                id = StateID(int(elem.attrib["Состояние"]))
            else:
                id = StateID(id_map[int(elem.attrib["Состояние"])])

            scenario.make_enter(id)

        # добавляем переходы
        for elem in root.find("Переходы").findall("Связи"):
            if id_map is None:
                state_from_id = StateID(int(elem.attrib["Состояние"]))
            else:
                state_from_id = StateID(id_map[int(elem.attrib["Состояние"])])

            for step in elem.findall("Переход"):
                if id_map is None:
                    state_to_id = StateID(int(step.attrib["В_состояние"]))
                else:
                    state_to_id = StateID(
                        id_map[int(step.attrib["В_состояние"])],
                    )

                for input in step.findall("Управляющее_воздействие"):
                    _vector = scenario.get_vector(
                        Name(input.attrib["Название"]),
                    )
                    scenario.create_step(state_from_id, state_to_id, _vector)

        return Server(scenario)

    @staticmethod
    def open_scenario(
        hosting: HostingInterface,
        id: int,
    ) -> "Server":
        return Server(hosting.get_scenario(ScenarioID(id)))


class ScenarioAPI:
    _scenario: ScenarioInterface

    def __init__(self, scenario: ScenarioInterface) -> None:
        self._scenario = scenario

    def id(self) -> int:
        return self._scenario.source().id.value

    def name(self) -> str:
        return self._scenario.source().info.name.value

    def description(self) -> str:
        return self._scenario.source().info.description.value

    def in_db(self) -> bool:
        return isinstance(self._scenario.source(), SourceMariaDB)

    # TODO заменить собственным интерфейсом
    def interface(self) -> ScenarioInterface:
        return self._scenario

    def get_layouts(self) -> str:
        pass

    def save_lay(self, id: int, x: float, y: float):
        pass

    def remove_synonym(self, input_name: str, synonym: str):
        """удаляет синоним"""

    def remove_vector(self, input_name: str):
        """удаляет вектор"""

    def remove_enter(self, state_id: int):
        """удаляет точку входа (переход)"""

    def remove_step(self, from_state_id: int, input_name: str):
        """удаляет переход"""

    def remove_state(self, state_id: int):
        """удаляет состояние"""

    def create_synonym(self, input_name: str, new_synonym: str):
        """создаёт синоним"""

    def add_vector(self, input_name: str):
        """создаёт вектор"""

    def make_enter(
        self,
        main_window: QWidget,
        state_id: int,
        ask: bool = True,
    ) -> str:
        """делает состояние точкой входа, возвращает имя вектора"""

    def create_step(
        self,
        from_state_id: int,
        to_state_id: int,
        input_name: str,
    ):
        """создаёт переход"""

    def create_step_to_new_state(
        self,
        from_state_id: int,
        input_name: str,
        new_state_name: str,
    ) -> dict:
        """создаёт состояние с переходом в него
        возвращает словарь с аттрибутами нового состояния: `id`, `name`, `text`
        """

    def set_state_answer(self, state_id: int, new_value: str):
        """изменяет ответ состояния"""

    def rename_state(self, state_id: int, new_name: str):
        """изменяет имя состояния"""

    def rename_vector(self, old_name: str, new_name: str):
        """переименовывает группу синонимов"""

    def set_synonym_value(self, input_name, old_synonym, new_synonym):
        """изменяет значение синонима"""

    def steps_from(self, from_state: int) -> dict[int, list[str]]:
        """возвращает словарь переходов из состояния from_state. key - id состояния, val - список имём векторов"""

    def serialize(self) -> str:
        """сформировать строку для сохранения в файл"""

    def create_enter_state(self, name: str) -> dict:
        """создаёт состояние-вход и вектор
        возвращает словарь с аттрибутами нового состояния: `id`, `name`, `text`
        """

class Server(ScenarioAPI):
    def __init__(self, scenario: ScenarioInterface) -> None:
        super().__init__(scenario)

    def in_db(self) -> bool:
        return isinstance(self._scenario.source(), SourceMariaDB)

    # TODO заменить собственным интерфейсом
    def interface(self) -> ScenarioInterface:
        return self._scenario

    def get_layouts(self) -> str:
        return self._scenario.get_layouts()

    def save_lay(self, id: int, x: float, y: float):
        self._scenario.save_lay(StateID(id), x, y)

    def remove_synonym(self, input_name: str, synonym: str):
        """удаляет синоним"""
        vector: LevenshtainVector = self._scenario.get_vector(
            Name(input_name),
        )
        if not isinstance(vector, LevenshtainVector):
            raise Warning("ошибка получения вектора перехода")

        index = vector.synonyms.synonyms.index(Synonym(synonym))

        self._scenario.remove_synonym(input_name, synonym)

    def remove_vector(self, input_name: str):
        """удаляет вектор"""
        self._scenario.remove_vector(Name(input_name))

    def remove_enter(self, state_id: int):
        """удаляет точку входа (переход)"""
        self._scenario.remove_enter(StateID(state_id))

    def remove_step(self, from_state_id: int, input_name: str):
        """удаляет переход"""
        vector: InputDescription = self._scenario.get_vector(Name(input_name))
        self._scenario.remove_step(StateID(from_state_id), vector)

    def remove_state(self, state_id: int):
        """удаляет состояние"""
        self._scenario.remove_state(StateID(state_id))

    def create_synonym(self, input_name: str, new_synonym: str):
        """создаёт синоним"""
        vector: LevenshtainVector = self._scenario.get_vector(
            Name(input_name),
        )
        if not isinstance(vector, LevenshtainVector):
            raise Warning("ошибка получения вектора перехода")

        synonym = Synonym(new_synonym)

        if synonym in vector.synonyms.synonyms:
            raise Exists(
                synonym,
                f'Синоним "{new_synonym}" группы "{input_name}"',
            )

        self._scenario.create_synonym(input_name, new_synonym)

    def add_vector(self, input_name: str):
        """создаёт вектор"""
        self._scenario.add_vector(LevenshtainVector(Name(input_name)))

    def make_enter(
        self,
        main_window: QWidget,
        state_id: int,
        ask: bool = True,
    ) -> str:
        """делает состояние точкой входа, возвращает имя вектора"""
        state_id_d = StateID(state_id)
        state: State = self._scenario.states([state_id_d])[state_id_d]

        vector_name = state.attributes.name

        try:  # создаём новый вектор
            vector = LevenshtainVector(vector_name)
            self._scenario.create_enter_vector(vector, state_id_d)

        except Exists as err:
            # если вектор уже существует - спрашиваем продолжать ли с ним
            ask_result = QMessageBox.StandardButton.Apply

            if ask:
                ask_result = QMessageBox.information(
                    None,
                    "Подтверждение",
                    f"{err.ui_text} Продолжить с существующим вектором?",
                    QMessageBox.StandardButton.Apply,
                    QMessageBox.StandardButton.Abort,
                )

            # если пользователь отказался - завершаем операцию
            if ask_result == QMessageBox.StandardButton.Abort:
                raise RuntimeError

        except Exception:
            raise

        self._scenario.make_enter(state_id_d)

        return vector_name.value

    def create_step(
        self,
        from_state_id: int,
        to_state_id: int,
        input_name: str,
    ):
        """создаёт переход"""
        vector = self._scenario.get_vector(Name(input_name))
        self._scenario.create_step(
            StateID(from_state_id),
            StateID(to_state_id),
            vector,
        )

    def create_step_to_new_state(
        self,
        from_state_id: int,
        input_name: str,
        new_state_name: str,
    ) -> dict:
        """создаёт состояние с переходом в него
        возвращает словарь с аттрибутами нового состояния: `id`, `name`, `text`
        """
        vector = self._scenario.get_vector(Name(input_name))
        step: Step = self._scenario.create_step(
            StateID(from_state_id),
            StateAttributes(
                OutputDescription(Answer("текст ответа")),
                Name(new_state_name),
                Description(""),
            ),
            vector,
        )
        to_state: State = step.connection.to_state

        return {
            "id": to_state.id().value,
            "name": to_state.attributes.name.value,
            "text": to_state.attributes.output.value.text,
        }

    def set_state_answer(self, state_id: int, new_value: str):
        """изменяет ответ состояния"""
        self._scenario.set_answer(
            StateID(state_id),
            OutputDescription(Answer(new_value)),
        )

    def rename_state(self, state_id: int, new_name: str):
        """изменяет имя состояния"""
        self._scenario.rename_state(StateID(state_id), Name(new_name))

    def rename_vector(self, old_name: str, new_name: str):
        """переименовывает группу синонимов"""
        self._scenario.rename_vector(Name(old_name), Name(new_name))

    def set_synonym_value(self, input_name, old_synonym, new_synonym):
        """изменяет значение синонима"""
        vector: LevenshtainVector = self._scenario.get_vector(
            Name(input_name),
        )
        if not isinstance(vector, LevenshtainVector):
            raise Warning("ошибка получения вектора перехода")

        index = vector.synonyms.synonyms.index(
            Synonym(old_synonym),
        )  # raises ValueError if `old_synonym` not found
        self._scenario.set_synonym_value(input_name, old_synonym, new_synonym)

    def steps_from(self, from_state: int) -> dict[int, list[str]]:
        """возвращает словарь переходов из состояния from_state. key - id состояния, val - список имём векторов"""
        result = dict[int, list[str]]()
        steps: list[Step] = self._scenario.steps(StateID(from_state))
        for step in steps:
            if step.connection is None:
                continue

            if (
                step.connection.from_state is None
                or step.connection.from_state.id().value != from_state
            ):
                continue

            to_state: int = step.connection.to_state.id().value
            input_name: str = step.input.name().value
            if to_state not in result.keys():
                result[to_state] = [input_name]
            else:
                result[to_state].append(input_name)

        return result

    def serialize(self) -> str:
        """сформировать строку для сохранения в файл"""

        root = Element(
            "сценарий",
            {
                "Идентификатор": str(self.id()),
                "Название": self.name(),
                "Краткое_описание": self.description(),
            },
        )
        vectors = Element("Управляющие_воздействия")
        states = Element("Состояния")
        enters = Element("Входы")
        steps = Element("Переходы")

        root.append(vectors)
        root.append(states)
        root.append(enters)
        root.append(steps)

        for vector in self._scenario.select_vectors():
            if isinstance(vector, LevenshtainVector):
                _vector = Element(
                    "Описание",
                    {
                        "Название": vector.name().value,
                        "Тип": "Группа синонимов",
                    },
                )
                for synonym in vector.synonyms.synonyms:
                    _synonym = Element("Синоним")
                    _synonym.text = synonym.value
                    _vector.append(_synonym)
                vectors.append(_vector)

        for state in self._scenario.states().values():
            state: State = state
            _state = Element(
                "Состояние",
                {
                    "Идентификатор": str(state.id().value),
                    "Название": state.attributes.name.value,
                },
            )
            _state.text = state.attributes.output.value.text
            states.append(_state)

        connections = self._scenario.source().get_all_connections()
        for enter_state_id in connections["to"].keys():
            enter_conn: Connection = connections["to"][enter_state_id]
            _enter = Element(
                "Точка_входа",
                {"Состояние": str(enter_state_id.value)},
            )

            for step in enter_conn.steps:
                vector: LevenshtainVector = step.input
                if isinstance(vector, LevenshtainVector):
                    _vector = Element(
                        "Управляющее_воздействие",
                        {
                            "Название": vector.name().value,
                            "Тип": "Группа синонимов",
                        },
                    )
                    for synonym in vector.synonyms.synonyms:
                        _synonym = Element("Синоним")
                        _synonym.text = synonym.value
                        _vector.append(_synonym)
                    _enter.append(_vector)

            enters.append(_enter)

        for from_state_id in connections["from"].keys():
            _conn = Element("Связи", {"Состояние": str(from_state_id.value)})
            for conn in connections["from"][from_state_id]:
                conn: Connection = conn  # просто аннотирование
                _step = Element(
                    "Переход",
                    {"В_состояние": str(conn.to_state.id().value)},
                )
                for step in conn.steps:
                    vector: LevenshtainVector = step.input
                    if isinstance(vector, LevenshtainVector):
                        _vector = Element(
                            "Управляющее_воздействие",
                            {
                                "Название": vector.name().value,
                                "Тип": "Группа синонимов",
                            },
                        )
                        for synonym in vector.synonyms.synonyms:
                            _synonym = Element("Синоним")
                            _synonym.text = synonym.value
                            _vector.append(_synonym)
                        _step.append(_vector)

                _conn.append(_step)

            steps.append(_conn)

        indent(root)
        return tostring(root, "unicode")

    def create_enter_state(self, name: str) -> dict:
        """создаёт состояние-вход и вектор
        возвращает словарь с аттрибутами нового состояния: `id`, `name`, `text`
        """
        new_enter_state_id: StateID = self._scenario.create_enter_state(Name(name))
        new_enter_state = self._scenario.states([new_enter_state_id])[
            new_enter_state_id
        ]

        return {
            "id": new_enter_state.id().value,
            "name": new_enter_state.attributes.name.value,
            "text": new_enter_state.attributes.output.value.text,
        }

class Client(Server): #(ScenarioAPI)
    __server: Server

    def __init__(self, slave: ScenarioInterface, server: Server) -> None:
        super().__init__(slave)
        self.__server = server

    def in_db(self) -> bool:
        return self.__server.in_db()

    def save_lay(self, id: int, x: float, y: float):
        return self.__server.save_lay(id, x, y)

    def remove_synonym(self, input_name: str, synonym: str):
        """удаляет синоним"""
        return self.__server.remove_synonym(input_name, synonym)

    def remove_vector(self, input_name: str):
        """удаляет вектор"""
        return self.__server.remove_vector(input_name)

    def remove_enter(self, state_id: int):
        """удаляет точку входа (переход)"""
        return self.__server.remove_enter(state_id)

    def remove_step(self, from_state_id: int, input_name: str):
        """удаляет переход"""
        return self.__server.remove_step(from_state_id, input_name)

    def remove_state(self, state_id: int):
        """удаляет состояние"""
        return self.__server.remove_state(state_id)

    def create_synonym(self, input_name: str, new_synonym: str):
        """создаёт синоним"""
        return self.__server.create_synonym(input_name, new_synonym)

    def add_vector(self, input_name: str):
        """создаёт вектор"""
        return self.__server.add_vector(input_name)

    def make_enter(
        self,
        main_window: QWidget,
        state_id: int,
        ask: bool = True,
    ) -> str:
        """делает состояние точкой входа, возвращает имя вектора"""
        return self.__server.make_enter(main_window, state_id, ask)

    def create_step(
        self,
        from_state_id: int,
        to_state_id: int,
        input_name: str,
    ):
        """создаёт переход"""
        return self.__server.create_step(from_state_id, to_state_id, input_name)

    def create_step_to_new_state(
        self,
        from_state_id: int,
        input_name: str,
        new_state_name: str,
    ) -> dict:
        """создаёт состояние с переходом в него
        возвращает словарь с аттрибутами нового состояния: `id`, `name`, `text`
        """
        return self.__server.create_step_to_new_state(from_state_id, input_name, new_state_name)

    def set_state_answer(self, state_id: int, new_value: str):
        """изменяет ответ состояния"""
        return self.__server.set_state_answer(state_id, new_value)
        
    def rename_state(self, state_id: int, new_name: str):
        """изменяет имя состояния"""
        return self.__server.rename_state(state_id, new_name)

    def rename_vector(self, old_name: str, new_name: str):
        """переименовывает группу синонимов"""
        return self.__server.rename_state(old_name, new_name)

    def set_synonym_value(self, input_name, old_synonym, new_synonym):
        """изменяет значение синонима"""
        return self.__server.set_synonym_value(input_name, old_synonym, new_synonym)

    def create_enter_state(self, name: str) -> dict:
        """создаёт состояние-вход и вектор
        возвращает словарь с аттрибутами нового состояния: `id`, `name`, `text`
        """
        return self.__server.create_enter_state(name)
