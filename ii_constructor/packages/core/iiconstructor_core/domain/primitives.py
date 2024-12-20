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

@dataclass(frozen=True)
class ProjectName:
    """Аттрибут названия для именуемых объектов"""

    value: str

    __MIN_LEN: int = 0
    __MAX_LEN: int = 512

    def is_valid(self) -> bool:
        _len: int = len(self.value)
        return self.__MIN_LEN < _len < self.__MAX_LEN

    def __eq__(self, value: object) -> bool:
        return isinstance(value, ProjectName) and value.value == self.value


@dataclass(frozen=True)
class StateName:
    """Аттрибут названия для именуемых объектов"""

    value: str

    __MIN_LEN: int = 0
    __MAX_LEN: int = 512

    def is_valid(self) -> bool:
        _len: int = len(self.value)
        return self.__MIN_LEN < _len < self.__MAX_LEN

    def __eq__(self, value: object) -> bool:
        return isinstance(value, StateName) and value.value == self.value


@dataclass(frozen=True)
class Description:
    """Атрибут описания для объектов"""

    value: str

    __MIN_LEN: int = 0
    __MAX_LEN: int = 512

    def is_valid(self) -> bool:
        _len: int = len(self.value)
        return self.__MIN_LEN < _len < self.__MAX_LEN


@dataclass(frozen=True)
class ScenarioID:
    """Идентификатор сценария"""

    value: int


@dataclass(frozen=True)
class StateID:
    """Идентификатор состояния"""

    value: int

@dataclass
class SourceInfo:
    """Класс, инкапсулирующий аттрибуты сценария"""

    name: ProjectName
    description: Description


class Request:
    """Базовый класс представления запроса от платформы"""

    text: str


class Response:
    """Базовый класс представления ответа для платформы"""

    text: str
    

@dataclass
class StateAttributes:
    """Класс, инкапсулирующий аттрибуты состояния"""

    name: StateName
    description: Description
