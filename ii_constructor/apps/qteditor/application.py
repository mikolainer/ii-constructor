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

from iiconstructor_scenario.domain import (
    Connection,
    Hosting,
    State,
    Step,
)
from iiconstructor_scenario.domain.exceptions import CoreException, Exists
from iiconstructor_scenario.domain.porst import ScenarioInterface
from iiconstructor_answers.plaintext import (
    OutputDescription,
    PlainTextAnswer,
    PlainTextDescription,
)
from iiconstructor_inputvectors.domain import (
    InputDescription,
    VectorName,
)
from iiconstructor_scenario.domain.primitives import (
    Description,
    StateName,
    ProjectName,
    ScenarioID,
    SourceInfo,
    StateID,
)
from iiconstructor_inputvectors.levenshtein import LevenshtainVector, Synonym
#from iiconstructor_maria.repo import SourceMariaDB
from PySide6.QtWidgets import QMessageBox, QWidget

class Vector_DTO:
    __name: str
    __values: list[str]

    def __init__(self, obj: InputDescription | dict):
        if isinstance(obj, InputDescription):
            self.__name = obj.name().value
            self.__values = []
            for val_index in range(len(obj)):
                self.__values.append(obj.value(val_index).value())
        
        elif isinstance(obj, dict):
            self.__name = obj["name"]
            self.__values = obj["values"]

    @staticmethod
    def parse(data_str: str) -> "Vector_DTO":
        obj: dict
        splitted: list[str] = data_str.split(";")
        obj["name"] = splitted[0][splitted[0].index("=")+1 :]
        obj["values"] = splitted[1][splitted[1].index("=")+1 :].split(',')
        return Vector_DTO(obj)

    def serialize(self) -> str:
        return f"name={self.__name};values={','.join(self.__values)}"

    def data(self) -> dict:
        return {
            "name": self.__name,
            "values": self.__values
        }

class Output_DTO:
    __values: list[str]

    def __init__(self, obj: OutputDescription | dict):
        if isinstance(obj, OutputDescription):
            self.__values = list[str]()
            for val_index in range(len(obj)):
                self.__values.append(obj.value(val_index).as_text())

        elif isinstance(obj, dict):
            self.__values = obj["values"]

    @staticmethod
    def parse(data_str: str) -> "Output_DTO":
        return {
            "values": data_str.split(",")
        }

    def serialize(self) -> str:
        return ",".join(self.__values)

    def data(self) -> dict:
        return {
            "values": self.__values
        }

class State_DTO:
    __id: str
    __required: str
    __name: str
    __description: str
    __output: Output_DTO

    def __init__(self, obj: State | dict):
        if isinstance(obj, State):
            self.__id = str(obj.id().value)
            self.__required = str(obj.is_required())
            self.__name = obj.name().value
            self.__description = obj.description().value

            values = list[str]
            for val_index in range(len(obj)):
                values.append(obj.output().value(val_index).as_text())
            
            self.__output = Output_DTO({"values":values})

        elif isinstance(obj, dict):
            self.__id = obj["id"]
            self.__required = obj["required"]
            self.__name = obj["name"]
            self.__description = obj["description"]
            self.__output = obj["output"]

    @staticmethod
    def parse(data_str: str) -> "State_DTO":
        splitted = data_str.split(",")
        data = {}
        for sub_str in splitted:
            sep_index = sub_str.index("=")
            name = sub_str[:sep_index]
            value = sub_str[sep_index:]

            if name == "id":
                data["id"] = value
            
            elif name == "required":
                data["required"] = value

            elif name == "name":
                data["name"] = value

            elif name == "description":
                data["description"] = value

            elif name == "output":
                data["output"] = Connection_DTO.parse(data)

        return State_DTO(data)

    def serialize(self) -> str:
        return f"id={self.__id};required={self.__required};name={self.__name};description={self.__description};output={self.__output.serialize()}"

    def data(self) -> dict:
        return {
            "id": self.__id,
            "required": self.__required,
            "name": self.__name,
            "description": self.__description,
            "output": self.__output,
        }

class Connection_DTO:
    __from_state_id: str
    __to_state_id: str
    __steps: list[str]

    def __init__(self, obj: Connection | dict):
        if isinstance(obj, Connection):
            self.__from_state_id = str(obj.from_state.value)
            self.__to_state_id = str(obj.to_state.value)
            self.__steps = []
            for step in obj.steps():
                step: Step = step
                self.__steps.append(step.name())

        elif isinstance(obj, dict):
            self.__from_state_id = str(obj["from_state"])
            self.__to_state_id = str(obj["to_state"])
            self.__steps = obj["steps"]

    @staticmethod
    def parse(data_str: str) -> "Connection_DTO":
        splitted = data_str.split(",")
        data = {}
        for sub_str in splitted:
            sep_index = sub_str.index("=")
            name = sub_str[:sep_index]
            value = sub_str[sep_index:]

            if name == "from_state":
                data["from_state"] = value
            
            elif name == "to_state":
                data["to_state"] = value

            elif name == "steps":
                data["steps"] = value.split(",")

        return Connection_DTO(data)

    def serialize(self) -> str:
        return f"from_state={self.__from_state_id};to_state={self.__to_state_id};steps={','.join(self.__steps)}"

    def data(self) -> dict:
        return {
            "from_state": self.__from_state_id,
            "to_state": self.__to_state_id,
            "steps": self.__steps
        }


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
            VectorName("Старт"),
                [
                    Synonym("Алиса, запусти навык ..."),
                ],
            )
        )

        new_scenario.create_enter_state(
            LevenshtainVector(
                VectorName("Информация"),
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
                VectorName("Помощь"),
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
            ProjectName(root.attrib["Название"]),
            Description(root.attrib["Краткое_описание"]),
            False
        )
        scenario = hosting.get_scenario(hosting.add_source(info))

        # добавляем векторы
        for elem in root.find("Управляющие_воздействия").findall("Описание"):
            synonyms = list[Synonym]()
            for synonym in elem.findall("Синоним"):
                synonyms.append(Synonym(synonym.text))

            scenario.add_vector(
                LevenshtainVector(
                    VectorName(elem.attrib["Название"]),
                    synonyms,
                ),
            )

        # добавляем состояния
        for elem in root.find("Состояния").findall("Состояние"):
            state: State = scenario.source().create_state(
                StateName(elem.attrib["Название"]),
                Description(""),
                PlainTextDescription(PlainTextAnswer(elem.text)),
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
                        VectorName(input.attrib["Название"]),
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
        return self.__scenario.source_id().value

    def name(self) -> str:
        return self.__scenario.source_name().value

    def description(self) -> str:
        return self.__scenario.source_description().value

    def in_db(self) -> bool:
        return False

    # TODO заменить собственным интерфейсом
    def interface(self) -> ScenarioInterface:
        return self.__scenario

    def get_layouts(self) -> str:
        return self.__scenario.get_layouts()

    def save_lay(self, id: int, x: float, y: float):
        self.__scenario.save_lay(StateID(id), x, y)

    def remove_vector(self, input_name: str):
        """удаляет вектор"""
        self.__scenario.remove_vector(VectorName(input_name))

    def remove_enter(self, state_id: int):
        """удаляет точку входа (переход)"""
        self.__scenario.remove_enter(StateID(state_id))

    def remove_step(self, from_state_id: int, input_name: str):
        """удаляет переход"""
        vector: InputDescription = self.__scenario.get_vector(VectorName(input_name))
        self.__scenario.remove_step(StateID(from_state_id), vector)

    def remove_state(self, state_id: int):
        """удаляет состояние"""
        self.__scenario.remove_state(StateID(state_id))

    def add_vector(self, input_name: str):
        """создаёт вектор"""
        self.__scenario.add_vector(LevenshtainVector(VectorName(input_name)))

    def make_enter(
        self,
        state_id: int,
        ask: bool = True,
    ) -> str:
        """делает состояние точкой входа, возвращает имя вектора"""
        state_id_d = StateID(state_id)
        state: State = self.__scenario.states([state_id_d])[state_id_d]

        vector_name = VectorName(state.name().value)

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
        vector = self.__scenario.get_vector(VectorName(input_name))
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
        vector = self.__scenario.get_vector(VectorName(input_name))
        to_state: State = self.__scenario.create_step_to_new(
            StateID(from_state_id),
            StateName(new_state_name),
            Description(""),
            PlainTextDescription(PlainTextAnswer("Текст ответа")),
            vector,
        )

        return {
            "id": to_state.id().value,
            "text": to_state.output().value().as_text(),
        }
    
    def create_enter_to_new_state(self, new_state_name: str) -> dict[str, str]:
        state = self.__scenario.create_enter_to_new(
            StateName(new_state_name),
            Description(""),
            PlainTextDescription(PlainTextAnswer("текст ответа"))
        )

        return {
            "id": state.id().value,
            "name": state.name().value,
            "text": state.output().value().as_text(),
        }
        

    def set_state_answer(self, state_id: int, new_value: str):
        """изменяет ответ состояния"""
        self.__scenario.set_answer(
            StateID(state_id),
            PlainTextDescription(PlainTextAnswer(new_value)),
        )

    def rename_state(self, state_id: int, new_name: str):
        """изменяет имя состояния"""
        self.__scenario.rename_state(StateID(state_id), StateName(new_name))

    def rename_vector(self, old_name: str, new_name: str):
        """переименовывает группу синонимов"""
        self.__scenario.rename_vector(VectorName(old_name), VectorName(new_name))

    def steps_from(self, from_state: int) -> dict[int, list[str]]:
        """возвращает словарь переходов из состояния from_state. key - id состояния, val - список имём векторов"""
        result = dict[int, list[str]]()
        steps: list[Connection] = self.__scenario.steps(StateID(from_state))
        for conn in steps:
            if conn is None:
                continue

            if (
                conn.from_state is None
                or conn.from_state.value != from_state
            ):
                continue

            to_state: int = conn.to_state.value
            for step in conn.steps:
                input_name: str = step.name
                if to_state not in result.keys():
                    result[to_state] = [input_name]
                else:
                    result[to_state].append(input_name)

        return result

    def save_to_file(self):
        """сохраняет сценарий в файл"""

    def get_vectors(self, names: list[str] | None = None) -> list[Vector_DTO]:
        """Чтение векторов"""
        answer = list[Vector_DTO]()
        vector_names = None

        if names is not None:
            vector_names = list[VectorName]()
            for name in names:
                vector_names.append(VectorName(name))
                
        for input in self.__scenario.select_vectors(vector_names):
            answer.append(Vector_DTO(input))
        return answer

    def get_states(self, ids: list[str] | None = None) -> dict[str, State_DTO]:
        """Чтение состояний"""
        ids_list = None
        
        if ids is not None:
            ids_list = list[StateID]()
            for id in ids:
                ids_list.append(StateID(int(id)))

        result = dict[str, State_DTO]()
        for state in self.__scenario.states(ids_list).values():
            state: State = state
            result[str(state.id().value)] = State_DTO(state)

        return result

    def get_steps(self, id: str) -> list[Connection_DTO]:
        """Чтение переходов"""
        result = list[Connection_DTO]()
        for conn in self.__scenario.steps(StateID(int(id))):
            conn: Connection = conn
            result.append(Connection_DTO(conn))
        
        return result

    def get_states_by_name(self, name: str) -> list[State_DTO]:
        """Чтение состояний"""
        result = list[State_DTO]()
        for state in self.__scenario.get_states_by_name(StateName(name)):
            state: State = state
            result.append(State_DTO(state))

        return result

    def update_vector(self, vector_name:str, new_data:Vector_DTO):
        """Обновление векторов"""
        values = list[Synonym]()
        for val in new_data.data()["values"]:
            val:str = val
            values.append(Synonym(val))

        new_vector = LevenshtainVector(
            VectorName(new_data.data()["name"]),
            values
        )
        self.__scenario.update_vector(VectorName(vector_name), new_vector)

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
                    "Название": state.name().value,
                },
            )
            _state.text = state.output().value().as_text()
            states.append(_state)

        enter_connections: list[Connection] = self.__scenario.enters()
        for enter_conn in enter_connections:
            enter_state_id = enter_conn.to_state

            _enter = Element(
                "Точка_входа",
                {"Состояние": str(enter_state_id.value)},
            )

            for step in enter_conn.steps:
                vector: LevenshtainVector = self.__scenario.get_vector(VectorName(step.name))
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
                    _enter.append(_vector)

            enters.append(_enter)

        for state in self.__scenario.states().values():
            state: State = state
            from_state_id: StateID = state.id()
            _conn = Element("Связи", {"Состояние": str(from_state_id.value)})
            step_count: int = 0

            for conn in self.__scenario.steps(from_state_id):
                conn: Connection = conn
                if conn.from_state is not from_state_id:
                    continue # пропускаем входящие связи

                step_count = step_count +1
                _step = Element(
                    "Переход",
                    {"В_состояние": str(conn.to_state.value)},
                )
                for step in conn.steps:
                    vector: LevenshtainVector = self.__scenario.get_vector(VectorName(step.name))
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

            if step_count > 0:    
                steps.append(_conn)

        indent(root)
        return tostring(root, encoding="unicode")

    def check_can_create_enter_state(self, name: str) -> bool:
        """проверяет условия для создания точки входа в новое состояние"""
        return self.__scenario.check_vector_exists(VectorName(name))
