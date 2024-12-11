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

from iiconstructor_core.domain import (
    Connection,
    Hosting,
    InputDescription,
    State,
    Step,
)
from iiconstructor_core.domain.exceptions import CoreException, Exists
from iiconstructor_core.domain.porst import ScenarioInterface
from iiconstructor_answers import (
    PlainTextAnswer,
    OutputDescription,
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
from iiconstructor_maria.repo import SourceMariaDB
from PySide6.QtWidgets import QMessageBox, QWidget


class HostingManipulator:
    @staticmethod
    def make_scenario(
        hosting: Hosting,
        info: SourceInfo,
    ) -> "ScenarioAPI":
        """создаёт заготовку сценария для алисы"""
        new_scenario = hosting.get_scenario(hosting.add_source(info))

        new_scenario.create_enter_state(
            LevenshtainVector(
            Name("Старт"),
                [
                    Synonym("Алиса, запусти навык ..."),
                ],
            )
        )

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name("Информация"),
                [
                    Synonym("Информация"),
                    Synonym("Справка"),
                    Synonym("Расскажи о себе"),
                ],
            ),
            True,
        )

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name("Помощь"),
                [
                    Synonym("Помощь"),
                    Synonym("Помоги"),
                    Synonym("Как выйти"),
                ]
            ),
            True,
        )

        return ScenarioAPI(new_scenario)

    @staticmethod
    def load_scenario(
        hosting: Hosting,
        data: str,
        id_map: dict[int, int] = None,
    ) -> "ScenarioAPI":
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
                    synonyms,
                ),
            )

        # добавляем состояния
        for elem in root.find("Состояния").findall("Состояние"):
            state: State = scenario.source().create_state(
                StateAttributes(
                    Name(elem.attrib["Название"]),
                    Description(""),
                ),
                OutputDescription(PlainTextAnswer(elem.text)),
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
                    scenario.create_step_between(state_from_id, state_to_id, _vector)

        return ScenarioAPI(scenario)

    @staticmethod
    def open_scenario(
        hosting: Hosting,
        id: int,
    ) -> "ScenarioAPI":
        return ScenarioAPI(hosting.get_scenario(ScenarioID(id)))


class ScenarioAPI:
    __scenario: ScenarioInterface

    def __init__(self, scenario: ScenarioInterface) -> None:
        self.__scenario = scenario

    def id(self) -> int:
        return self.__scenario.source().id.value

    def name(self) -> str:
        return self.__scenario.source().info.name.value

    def description(self) -> str:
        return self.__scenario.source().info.description.value

    def in_db(self) -> bool:
        return isinstance(self.__scenario.source(), SourceMariaDB)

    # TODO заменить собственным интерфейсом
    def interface(self) -> ScenarioInterface:
        return self.__scenario

    def get_layouts(self) -> str:
        return self.__scenario.get_layouts()

    def save_lay(self, id: int, x: float, y: float):
        self.__scenario.save_lay(StateID(id), x, y)

    def create_state(self, name: str) -> dict:
        state: State = self.__scenario.source().create_state(
            StateAttributes(Name(name), Description("")),
            OutputDescription(),
        )

        return {
            "id": state.id().value,
            "name": state.attributes.name.value,
            "text": state.output().value().as_text(),
        }

#    def remove_synonym(self, input_name: str, synonym: str):
#        """удаляет синоним"""
#        vector: LevenshtainVector = self.__scenario.get_vector(
#            Name(input_name),
#        )
#        if not isinstance(vector, LevenshtainVector):
#            raise Warning("ошибка получения вектора перехода")
#
#        index = vector.synonyms.synonyms.index(Synonym(synonym))
#
#        self.__scenario.remove_synonym(input_name, synonym)

#    def create_synonym(self, input_name: str, new_synonym: str):
#        """создаёт синоним"""
#        vector: LevenshtainVector = self.__scenario.get_vector(
#            Name(input_name),
#        )
#        if not isinstance(vector, LevenshtainVector):
#            raise Warning("ошибка получения вектора перехода")
#
#        synonym = Synonym(new_synonym)
#
#        if synonym in vector.synonyms.synonyms:
#            raise Exists(
#                synonym,
#                f'Синоним "{new_synonym}" группы "{input_name}"',
#            )
#
#        self.__scenario.create_synonym(input_name, new_synonym)

#    def set_synonym_value(self, input_name, old_synonym, new_synonym):
#        """изменяет значение синонима"""
#        vector: LevenshtainVector = self.__scenario.get_vector(
#            Name(input_name),
#        )
#        if not isinstance(vector, LevenshtainVector):
#            raise Warning("ошибка получения вектора перехода")
#
#        index = vector.synonyms.synonyms.index(
#            Synonym(old_synonym),
#        )  # raises ValueError if `old_synonym` not found
#        self.__scenario.set_synonym_value(input_name, old_synonym, new_synonym)

    def remove_vector(self, input_name: str):
        """удаляет вектор"""
        self.__scenario.remove_vector(Name(input_name))

    def remove_enter(self, state_id: int):
        """удаляет точку входа (переход)"""
        self.__scenario.remove_enter(StateID(state_id))

    def remove_step(self, from_state_id: int, input_name: str):
        """удаляет переход"""
        vector: InputDescription = self.__scenario.get_vector(Name(input_name))
        self.__scenario.remove_step(StateID(from_state_id), vector)

    def remove_state(self, state_id: int):
        """удаляет состояние"""
        self.__scenario.remove_state(StateID(state_id))

    def add_vector(self, input_name: str):
        """создаёт вектор"""
        self.__scenario.add_vector(LevenshtainVector(Name(input_name)))

    def make_enter(
        self,
        state_id: int,
        ask: bool = True,
    ) -> str:
        """делает состояние точкой входа, возвращает имя вектора"""
        state_id_d = StateID(state_id)
        state: State = self.__scenario.states([state_id_d])[state_id_d]

        vector_name = state.attributes.name

        try:  # создаём новый вектор
            vector = LevenshtainVector(vector_name)
            self.__scenario.create_enter_vector(vector, state_id_d)

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

        self.__scenario.make_enter(state_id_d)

        return vector_name.value

    def create_step(
        self,
        from_state_id: int,
        to_state_id: int,
        input_name: str,
    ):
        """создаёт переход"""
        vector = self.__scenario.get_vector(Name(input_name))
        self.__scenario.create_step_between(
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
        vector = self.__scenario.get_vector(Name(input_name))
        step: Step = self.__scenario.create_step_to_new(
            StateID(from_state_id),
            StateAttributes(
                Name(new_state_name),
                Description(""),
            ),
            OutputDescription(PlainTextAnswer("текст ответа")),
            vector,
        )
        to_state: State = step.connection.to_state

        return {
            "id": to_state.id().value,
            "name": to_state.attributes.name.value,
            "text": to_state.output().value().as_text(),
        }

    def set_state_answer(self, state_id: int, new_value: str):
        """изменяет ответ состояния"""
        self.__scenario.set_answer(
            StateID(state_id),
            OutputDescription(PlainTextAnswer(new_value)),
        )

    def rename_state(self, state_id: int, new_name: str):
        """изменяет имя состояния"""
        self.__scenario.rename_state(StateID(state_id), Name(new_name))

    def rename_vector(self, old_name: str, new_name: str):
        """переименовывает группу синонимов"""
        self.__scenario.rename_vector(Name(old_name), Name(new_name))

    def steps_from(self, from_state: int) -> dict[int, list[str]]:
        """возвращает словарь переходов из состояния from_state. key - id состояния, val - список имём векторов"""
        result = dict[int, list[str]]()
        steps: list[Step] = self.__scenario.steps(StateID(from_state))
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

    def save_to_file(self):
        """сохраняет сценарий в файл"""

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

        for vector in self.__scenario.select_vectors():
            if isinstance(vector, LevenshtainVector):
                _vector = Element(
                    "Описание",
                    {
                        "Название": vector.name().value,
                        "Тип": "Группа синонимов",
                    },
                )
                for index in range(len(vector)):
                    input = vector.value(index)
                    _synonym = Element("Синоним")
                    _synonym.text = input.value()
                    _vector.append(_synonym)
                vectors.append(_vector)

        for state in self.__scenario.states().values():
            state: State = state
            _state = Element(
                "Состояние",
                {
                    "Идентификатор": str(state.id().value),
                    "Название": state.attributes.name.value,
                },
            )
            _state.text = state.output().value().as_text()
            states.append(_state)

        connections = self.__scenario.source().get_all_connections()
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
                    for index in range(len(vector)):
                        input = vector.value(index)
                        _synonym = Element("Синоним")
                        _synonym.text = input.value
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
                        for index in range(len(vector)):
                            input = vector.value(index)
                            _synonym = Element("Синоним")
                            _synonym.text = input.value()
                            _vector.append(_synonym)
                        _step.append(_vector)

                _conn.append(_step)

            steps.append(_conn)

        indent(root)
        return tostring(root, "unicode")

    def check_can_create_enter_state(self, name: str):
        """проверяет условия для создания точки входа в новое состояние"""
        _name = Name(name)

        # должно подняться исключение если не существует
        self.__scenario.get_vector(_name)

        if len(self.__scenario.get_states_by_name(_name)) > 0:
            raise CoreException(f'Состояние с именем "{name}" уже существует!')

    def create_enter_state(self, name: str) -> dict:
        """создаёт состояние-вход и вектор
        возвращает словарь с аттрибутами нового состояния: `id`, `name`, `text`
        """
        vector = self.__scenario.get_vector(Name(name))
        new_enter_state_id: StateID = self.__scenario.create_enter_state(
            vector,
        )
        new_enter_state = self.__scenario.states([new_enter_state_id])[
            new_enter_state_id
        ]

        return {
            "id": new_enter_state.id().value,
            "name": new_enter_state.attributes.name.value,
            "text": new_enter_state.attributes.output.value.text,
        }
