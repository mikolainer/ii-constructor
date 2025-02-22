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


from dataclasses import dataclass
from typing import Any, Optional

from .exceptions import CoreException, Exists, NotExists
from .porst import ScenarioInterface
from iiconstructor_answers.domain import (
    OutputDescription,
)
from iiconstructor_answers.plaintext import (
    PlainTextDescription,
)
from iiconstructor_inputvectors.domain import (
    Input,
    StrInput,
    VectorName,
    InputDescription,
)
from .primitives import (
    Description,
    StateName,
    Request,
    Response,
    ScenarioID,
    SourceInfo,
    StateID,
    ProjectName,
)


def get_type_name(obj: Any) -> str:
    """Определение названия объекта доменной области, для короткого использования инсключений"""

    _obj_type = "Объект"

    if issubclass(type(obj), Scenario):
        _obj_type = "Сценарий"

    elif issubclass(type(obj), State):
        _obj_type = "Состояние"

    elif issubclass(type(obj), Connection):
        _obj_type = "Связь"

    elif issubclass(type(obj), Step):
        _obj_type = "Переход"

    elif issubclass(type(obj), InputDescription):
        _obj_type = "Вектор"

    return _obj_type


class _Exists(Exists):
    def __init__(self, obj: Any) -> None:
        super().__init__(obj, get_type_name(obj))


class PossibleInputs:
    """Классификатор векторов управляющих воздействий"""

    __inputs: dict[VectorName, "InputDescription"]
    """ Хранилище существующих векторов управляющих воздействий """

    def __init__(self) -> None:
        self.__inputs = {}

    def __len__(self) -> int:
        return len(self.__inputs)

    def add(self, input_type: "InputDescription"):
        """
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        """
        name = input_type.name()
        self.__inputs[name] = input_type

    def remove(self, name: VectorName):
        """
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        """

        if name not in self.__inputs.keys():
            raise RuntimeWarning("Нет входного вектора с таким именем")

        del self.__inputs[name]

    def get(self, name: VectorName) -> "InputDescription":
        """
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        """

        if not self.exists(name):
            raise NotExists(name, f'Вектор с именем "{name.value}"')

        return self.__inputs[name]

    def select(
        self,
        names: list[VectorName] | None = None,
    ) -> list["InputDescription"]:
        """
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        """

        if names is None:
            return list(self.__inputs.copy().values())

        if len(names) == 0:
            return []

        inputs_list: list[InputDescription] = []
        for name in names:
            inputs_list.append(self.get(name))

        return inputs_list

    def exists(self, name: VectorName) -> bool:
        """
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        """
        return name in self.__inputs.keys()


class State:
    __id: StateID
    __required: bool
    __name: StateName
    __description: Description
    __output: OutputDescription

    def __init__(
        self,
        id: StateID,
        name: StateName,
        description: Description,
        output: OutputDescription,
        required: bool = False,
    ) -> None:
        self.__id = id
        self.__required = required
        self.__name = name
        self.__description = description
        self.__output = output

        if name is None or name.value == "":
            name = StateName(str(id.value))

        if description is None:
            description = Description("")

        if output is None or output.as_text() == "":
            self.__output = PlainTextDescription("текст ответа")

    def id(self) -> StateID:
        return self.__id
    
    def is_required(self) -> bool:
        return self.__required

    def output(self) -> OutputDescription:
        return self.__output
    
    def name(self) -> StateName:
        return self.__name
    
    def set_name(self, new_name: StateName):
        self.__name = new_name
    
    def description(self) -> Description:
        return self.__description
    
    def set_description(self, new_descr: Description):
        self.__name = new_descr

    def set_output(self, output: OutputDescription):
        self.__output = output

@dataclass
class Step:
    name: str


@dataclass
class Connection:
    from_state: StateID | None
    to_state: StateID | None
    steps: list[Step]


class StepVectorBaseClassificator:
    __project: ScenarioInterface

    def __init__(self, project: ScenarioInterface) -> None:
        self.__project = project

    def calc(
        self,
        cur_input: Input,
        possible_inputs: dict[str, State],
    ) -> State | None:
        """Вычисления"""
        raise NotImplementedError

    def __prepare_to_step_detect(
        self,
        cur_state_id: StateID,
    ) -> dict[str, State]:
        inputs = dict[str, State]()
        for conn in self.__project.steps(cur_state_id):
            conn: Connection = conn

            cur_state = conn.from_state
            if cur_state is None or cur_state != cur_state_id:
                continue

            for step in conn.steps:
                inputs[step.name] = self.__project.states([conn.to_state])[conn.to_state]

        return inputs

    def __prepare_to_enter_detect(self) -> dict[str, State]:
        inputs = dict[str, State]()

        for conn in (
            self.__project.enters()
        ):
            conn: Connection = conn
            to: State = None
            if isinstance(conn.to_state, StateID):
                to = self.__project.states([conn.to_state])[conn.to_state]

            for step in conn.steps:
                inputs[step.name] = to

        return inputs

    def get_next_state(self, cmd: Input, cur_state_id: StateID) -> State:
        cur_state = self.__project.states([cur_state_id])[cur_state_id]

        callable_list = [
            lambda: self.__prepare_to_step_detect(cur_state_id),
            lambda: self.__prepare_to_enter_detect(),
        ]

        for get_inputs in callable_list:
            inputs = get_inputs()
            try:
                return self.calc(cmd, inputs)
            except Exception as e:
                pass

        return cur_state


class Source:
    id: ScenarioID | None
    info: SourceInfo

    def __init__(self, id: ScenarioID | None, info: SourceInfo) -> None:
        self.id = id
        self.info = info

    def get_layouts(self) -> str:
        """получить данные отображения"""

    def save_lay(self, id: StateID, x: float, y: float):
        """сохранить положение состояния"""

    def delete_state(self, state_id: StateID):
        """удалить состояние"""

    def get_states_by_name(self, name: StateName) -> list[State]:
        """получить все состояния с данным именем"""

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        """получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния"""

    def steps(self, state_id: StateID) -> list[Connection]:
        """получить все переходы, связанные с состоянием по его идентификатору"""

    def enters(self) -> list[Connection]:
        """получить все переходы в точки входа"""

    def is_enter(self, state: State) -> bool:
        """Проверить является ли состояние входом"""

    # сеттеры

    def set_answer(self, state_id: StateID, data: OutputDescription):
        """Изменить ответ состояния"""

    # векторы

    def select_vectors(
        self,
        names: list[VectorName] | None = None,
    ) -> list["InputDescription"]:
        """
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        """

    def get_vector(self, name: VectorName) -> InputDescription:
        """
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        """

    def add_vector(self, input: InputDescription):
        """
        Сохраняет новый вектор для обработки управляющих воздействий
        @input - новый вектор
        """

    def remove_vector(self, name: VectorName):
        """
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        """

    def update_vector(self, name: VectorName, input: InputDescription):
        """
        Обновляет вектор управляющих воздействий
        @name - имя вектора для замены (идентификатор)
        @input - новый вектор
        """

    def check_vector_exists(self, name: VectorName) -> bool:
        """
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        """

    # Scenario private
    def create_state(
        self,
        name: StateName,
        description: Description,
        output: OutputDescription,
        required: bool = False,
    ) -> State:
        """Создать состояние"""

    def find_connections_to(self, state_id: StateID) -> list[Connection]:
        """Получить входящие связи"""

    def input_usage(self, input: InputDescription) -> list[Connection]:
        """Получить связи, в которых используется вектор"""

    def new_step(
        self,
        from_state: StateID | None,
        to_state: StateID,
        input_name: VectorName,
    ):
        """создаёт переходы и связи"""

    def delete_step(
        self,
        from_state: StateID | None,
        to_state: StateID | None,
        input_name: VectorName | None = None,
    ):
        """удаляет переходы и связи"""

    def rename_state(self, state: StateID, name: StateName):
        """Переименовывает состояние"""

    def rename_vector(self, old_name: VectorName, new_name: VectorName):
        """переименовывает группу синонимов"""


class Hosting:
    def add_source(self, info: SourceInfo) -> ScenarioID:
        """Создать пустой проект"""

    def get_scenario(self, id: ScenarioID) -> ScenarioInterface:
        """Получить сценарий по id"""

    def sources(self) -> list[tuple[int, str, str]]:
        """
        Получить информацию о существующих в хранилище сценариях
        Возвращает список кортежей (id, name, description)
        """


class Scenario(ScenarioInterface):
    __src: Source

    # Scenario public

    def __init__(self, src: Source) -> None:
        self.__src = src

    def source(self) -> Source:
        return self.__src
    
    def is_source_in_db(self) -> bool:
        return self.__src.info.is_remote

    def source_id(self) -> ScenarioID:
        return self.__src.id
    
    def source_name(self) -> ProjectName:
        return self.__src.info.name

    def source_description(self) -> Description:
        return self.__src.info.description

    def get_layouts(self) -> str:
        return self.__src.get_layouts()

    def save_lay(self, id: StateID, x: float, y: float):
        self.__src.save_lay(id, x, y)

    # создание сущностей
    def create_enter_state(
        self,
        input: InputDescription,
        required: bool = False,
    ):
        """добавляет вектор и новое состояние-вход с таким-же именем"""

        # создаём вектор
        self.add_vector(input)

        # создаём состояние
        state_to = self.__src.create_state(
            StateName(input.name().value), Description(""),
            PlainTextDescription("Текст ответа"),
            required,
        )

        # делаем состояние точкой входа
        self.make_enter(state_to.id())

    def create_enter_vector(self, input: InputDescription, state_id: StateID):
        """Делает состояние точкой входа. Создаёт вектор с соответствующим состоянию именем"""
        _states = self.states()
        state_to = _states[state_id]
        for _state in _states.values():
            if (
                _state.name() == state_to.name()
                and _state.id() != state_to.id()
            ):
                raise CoreException(
                    "Состояние-вход должно иметь уникальное имя!",
                )

        # проверяем существование вектора c именем состояния входа
        vector_name: VectorName = self.states([state_id])[state_id].name()
        if self.check_vector_exists(vector_name):
            raise Exists(vector_name, f'Вектор с именем "{vector_name.value}"')

        self.add_vector(input)

    def make_enter(self, state_id: StateID):
        """привязывает к состоянию существующий вектор с соответствующим именем как команду входа"""
        # получаем состояние
        state_to = self.states([state_id])[state_id]

        # проверяем является ли входом
        if self.is_enter(state_to):
            raise Exists(
                state_to,
                f'Точка входа в состояние "{state_to.id().value}"',
            )

        input_name = VectorName(state_to.name().value)
        self.__src.new_step(None, state_to.id(), input_name)

    def create_step_between(
        self,
        from_state_id: StateID,
        to_state: StateID,
        input: InputDescription,
    ):
        self.__src.new_step(from_state_id, to_state, input.name())

    def create_step_to_new(
        self,
        from_state_id: StateID,
        name: StateName,
        description: Description,
        output: OutputDescription,
        input: InputDescription,
    ) -> State:
        _states = self.states()
        for _state in _states.values():
            if _state.name() == name and self.is_enter(
                _state,
            ):
                raise CoreException(
                    f'Cуществует состояние-вход с именем "{name.value}"! Состояние-вход должно иметь уникальное имя.',
                )

        state_to = self.__src.create_state(name, description, output)
        self.__src.new_step(from_state_id, state_to.id(), input.name())
        return state_to
    
    def create_enter_to_new(
        self, name: StateName,
        description: Description,
        output: OutputDescription
    ) -> State:
        self.check_can_create_enter_state(VectorName(name.value))

        state: State = self.__src.create_state(
            name, description, output,
        )
    
        self.make_enter(state.id())

        return state
    
    def check_can_create_enter_state(self, name: VectorName) -> bool:
         # должно подняться исключение если не существует
        self.get_vector(name)

        if len(self.get_states_by_name(StateName(name.value))) > 0:
            raise CoreException(f'Состояние с именем "{name.value}" уже существует!')

    # удаление сущностей

    def remove_state(self, state_id: StateID):
        """удаляет состояние"""
        if self.states([state_id])[state_id].is_required():
            raise Exception("Обязательное состояние нельзя удалить!")

        # TODO: изменить логику.
        # нельзя оставлять состояния без связей.
        # нужно удалять состояние вместе со всеми связями
        if len(self.steps(state_id)) > 0:
            raise Exists(
                state_id,
                f"Состояние с id={state_id.value} связано с переходами!",
            )

        self.__src.delete_state(state_id)

    def remove_enter(self, state_id: StateID):
        """удаляет связь с командой входа в состояние"""
        enter_state = self.states([state_id])[state_id]

        # TODO: изменить логику.
        # нельзя оставлять состояния без связей.
        if enter_state.is_required():
            raise Exception("Обязательную точку входа нельзя удалить!")

        self.__src.delete_step(None, state_id)

    def remove_step(self, from_state_id: StateID, input: InputDescription):
        """
        удаляет связь между состояниями
        @from_state_id: состояние - обработчик управляющих воздействий
        @input: управляющее воздействие
        """
        # TODO: изменить логику.
        # нельзя оставлять состояния без связей.
        self.__src.delete_step(from_state_id, None, input.name())

    # геттеры

    def get_states_by_name(self, name: StateName) -> list[State]:
        """получить все состояния с данным именем"""
        return self.__src.get_states_by_name(name)

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        """получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния"""
        return self.__src.states(ids)

    def steps(self, state_id: StateID) -> list[Connection]:
        """получить все переходы, связанные с состоянием по его идентификатору"""
        return self.__src.steps(state_id)
    
    def enters(self) -> list[Connection]:
        """получить все переходы в точки входа"""
        return self.__src.enters()

    def is_enter(self, state: State) -> bool:
        """Проверить является ли состояние входом"""
        return self.__src.is_enter(state)

    # сеттеры

    def set_answer(self, state_id: StateID, data: OutputDescription):
        """Изменить ответ состояния"""
        self.__src.set_answer(state_id, data)

    # векторы

    def select_vectors(
        self,
        names: list[VectorName] | None = None,
    ) -> list["InputDescription"]:
        """
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        """
        return self.__src.select_vectors(names)

    def get_vector(self, name: VectorName) -> InputDescription:
        """
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        """
        return self.__src.get_vector(name)

    def add_vector(self, input: InputDescription):
        if self.check_vector_exists(input.name()):
            raise _Exists(self.get_vector(input.name()))

        return self.__src.add_vector(input)

    def remove_vector(self, name: VectorName):
        self.__src.remove_vector(name)

    def update_vector(self, name: VectorName, input: InputDescription):
        self.__src.update_vector(name, input)

    def check_vector_exists(self, name: VectorName) -> bool:
        """
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        """
        return self.__src.check_vector_exists(name)

#    def set_synonym_value(
#        self,
#        input_name: str,
#        old_synonym: str,
#        new_synonym: str,
#    ):
#        """изменяет значение синонима"""
#        self.__src.set_synonym_value(input_name, old_synonym, new_synonym)
#
#    def create_synonym(self, input_name: str, new_synonym: str):
#        """создаёт синоним"""
#        self.__src.create_synonym(input_name, new_synonym)
#
#    def remove_synonym(self, input_name: str, synonym: str):
#        """удаляет синоним"""
#        self.__src.remove_synonym(input_name, synonym)

    def rename_state(self, state: StateID, name: StateName):
        """Переименовывает состояние"""
        if self.is_enter(self.__src.states([state])[state]):
            raise CoreException(
                "Нельзя переименовать состояние, которое является входом",
            )

        vector_exsists = True
        vector: InputDescription
        try:
            vector = self.get_vector(name)
        except Exception:
            vector_exsists = False

        if vector_exsists:
            for _conn in self.__src.input_usage(vector):
                if _conn.from_state is None:
                    if self.is_enter(_conn.to_state):
                        raise CoreException(
                            f'Состояние с именем "{name.value}" уже существует и является входом',
                        )

        self.__src.rename_state(state, name)

    def rename_vector(self, old_name: VectorName, new_name: VectorName):
        """переименовывает группу синонимов"""
        for state in self.get_states_by_name(old_name):
            if self.is_enter(state):
                raise CoreException(
                    "Нельзя переименовать вектор, который используется с точкой входа!",
                )

        try:
            self.get_vector(new_name)
            raise CoreException(
                f'Вектор с именем "{new_name.value}" уже существует!',
            )

        except NotExists:
            self.__src.rename_vector(old_name, new_name)

        except Exception:
            raise


class Engine:
    __classif: StepVectorBaseClassificator
    __cur_state: State

    def __init__(
        self,
        classif: StepVectorBaseClassificator,
        start_state: State,
    ) -> None:
        self.__classif = classif
        self.__cur_state = start_state

    def handle(self, request: Request) -> Response:
        req = request.text
        prev_state = self.__cur_state

        self.__cur_state = self.__classif.get_next_state(
            StrInput(req),
            self.__cur_state.id(),
        )

        result = Response()

        if prev_state == self.__cur_state:
            result.text = "Запрос не понятен"
        else:
            result.text = self.__cur_state.output().as_text()

        return result

    def set_current_state(self, state: State):
        self.__cur_state = state

    def current_state(self) -> State:
        return self.__cur_state
