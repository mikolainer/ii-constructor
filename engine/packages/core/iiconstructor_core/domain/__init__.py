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

from .exceptions import Exists, NotExists
from .primitives import (
    Answer,
    Description,
    Name,
    Output,
    ScenarioID,
    SourceInfo,
    StateAttributes,
    StateID,
)


def get_type_name(obj: Any) -> str:
    """Определение названия объекта доменной области, для короткого использования инсключений"""

    _obj_type = "Объект"

    #    if issubclass(type(obj), Scenario):
    #        _obj_type = "Сценарий"

    #    elif issubclass(type(obj), State):
    if issubclass(type(obj), State):
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

    __inputs: dict[Name, "InputDescription"]
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

    def remove(self, name: Name):
        """
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        """

        if name not in self.__inputs.keys():
            raise RuntimeWarning("Нет входного вектора с таким именем")

        del self.__inputs[name]

    def get(self, name: Name) -> "InputDescription":
        """
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        """

        if not self.exists(name):
            raise NotExists(name, f'Вектор с именем "{name.value}"')

        return self.__inputs[name]

    def select(
        self,
        names: list[Name] | None = None,
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

    def exists(self, name: Name) -> bool:
        """
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        """
        return name in self.__inputs.keys()


class State:
    __id: StateID
    required: bool
    attributes: StateAttributes

    def __init__(
        self,
        id: StateID,
        attributes: StateAttributes,
        required: bool = False,
    ) -> None:
        self.__id = id
        self.required = required
        self.attributes = attributes
        if attributes.name is None or attributes.name.value == "":
            attributes.name = Name(str(id.value))

        if attributes.description is None:
            attributes.description = Description("")

        if attributes.output is None or attributes.output.value.text == "":
            attributes.output = Output(Answer("текст ответа"))

    def id(self) -> StateID:
        return self.__id


class InputDescription:
    __name: Name

    def __init__(self, name: Name) -> None:
        self.__name = name

    def name(self) -> Name:
        return self.__name

    def set_name(self, new_name: Name) -> None:
        self.__name = new_name

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, InputDescription) and value.name() == self.__name
        )


@dataclass
class Step:
    input: InputDescription
    connection: Optional["Connection"] = None


@dataclass
class Connection:
    from_state: State | None
    to_state: State | None
    steps: list[Step]


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

    def get_states_by_name(self, name: Name) -> list[State]:
        """получить все состояния с данным именем"""

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        """получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния"""

    def steps(self, state_id: StateID) -> list[Step]:
        """получить все переходы, связанные с состоянием по его идентификатору"""

    def is_enter(self, state: State) -> bool:
        """Проверить является ли состояние входом"""

    # сеттеры

    def set_answer(self, state_id: StateID, data: Output):
        """Изменить ответ состояния"""

    # векторы

    def select_vectors(
        self,
        names: list[Name] | None = None,
    ) -> list["InputDescription"]:
        """
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        """

    def get_vector(self, name: Name) -> InputDescription:
        """
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        """

    def add_vector(self, input: InputDescription):
        """
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        """

    def remove_vector(self, name: Name):
        """
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        """

    def check_vector_exists(self, name: Name) -> bool:
        """
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        """

    # Scenario private
    def create_state(
        self,
        attributes: StateAttributes,
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
        input_name: Name,
    ) -> Step:
        """создаёт переходы и связи"""

    def delete_step(
        self,
        from_state: StateID | None,
        to_state: StateID | None,
        input_name: Name | None = None,
    ):
        """удаляет переходы и связи"""

    def get_all_connections(self) -> dict[str, dict]:
        """
        !!! DEPRECATED !!!\n
        получить все связи\n
        ключи: 'from', 'to'; значения: to=dict[StateID, Connection], from=dict[StateID, list[Connection]]
        """
        # TODO: оптимизировать API. (фактически в память выгружается вся база)

    def set_synonym_value(
        self,
        input_name: str,
        old_synonym: str,
        new_synonym: str,
    ):
        """изменяет значение синонима"""

    def create_synonym(self, input_name: str, new_synonym: str):
        """создаёт синоним"""

    def remove_synonym(self, input_name: str, synonym: str):
        """удаляет синоним"""

    def rename_state(self, state: StateID, name: Name):
        """Переименовывает состояние"""

    def rename_vector(self, old_name: Name, new_name: Name):
        """переименовывает группу синонимов"""
