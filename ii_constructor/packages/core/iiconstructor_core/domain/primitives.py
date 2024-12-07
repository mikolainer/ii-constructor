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
class Name:
    """Аттрибут названия для именуемых объектов"""

    value: str

    __MIN_LEN: int = 0
    __MAX_LEN: int = 512

    def is_valid(self) -> bool:
        _len: int = len(self.value)
        return self.__MIN_LEN < _len < self.__MAX_LEN

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Name) and value.value == self.value


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

    name: Name
    description: Description


class Request:
    """Базовый класс представления запроса от платформы"""

    text: str


class Response:
    """Базовый класс представления ответа для платформы"""

    text: str

class Input:
    def value(self) -> str:
        """Получить команду в виде строки"""

class StrInput(Input):
    """Класс "сырого" представления входящего управляющего воздействия"""

    __value: str

    __MIN_LEN: int = 1
    __MAX_LEN: int = 512

    def __init__(self, value:str):
        super().__init__()
        self.__value = value

    def value(self) -> str:
        """Получить команду в виде строки"""
        return self.__value

    def is_valid(self) -> bool:
        _len: int = len(self.__value)
        return self.__MIN_LEN < _len < self.__MAX_LEN
    
class InputDescription:
    __name: Name
    __values: list[Input]

    # нет сеттеров. только создание целиком.
    def __init__(self, name: Name, value: list[Input] | Input | None) -> None:
        self.__name = name
        if isinstance(value, list):
            if len(value) == 0:
                self.__values = None
            else:
                self.__values = value
        else:
            self.__values = [value]

    def value(self, index:int = 0) -> Input:
        return self.__values[index]

    def name(self) -> Name:
        return self.__name

    def set_name(self, new_name: Name) -> None:
        self.__name = new_name

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, InputDescription) and value.name() == self.__name
        )
    
    def __len__(self) -> int:
        return len(self.__values)

class AnswerValue:
    def as_text(self) -> str:
        """Строковое представление"""

class PlainTextAnswer(AnswerValue):
    """Базовый класс описания ответа"""

    __text: str
    __MIN_LEN: int = 1
    __MAX_LEN: int = 1024

    def __init__(self, text:str):
        self.__text = text

    def as_text(self) -> str:
        return self.__text

    def is_valid(self) -> bool:
        _len: int = len(self.text)
        return self.__MIN_LEN < _len < self.__MAX_LEN



class OutputDescription:
    """Описание ответа - аттрибут состояния"""
    __values: list[AnswerValue]

    # нет сеттеров. только создание целиком.
    def __init__(self, answer: list[AnswerValue] | AnswerValue | None = None):
        if isinstance(answer, list):
            if len(answer) == 0:
                self.__values = None
            else:
                self.__values = answer
        else:
            self.__values = [answer]

    def value(self, index:int = 0) -> AnswerValue:
        return self.__values[index]

    def __len__(self) -> int:
        return len(self.__values)

@dataclass
class StateAttributes:
    """Класс, инкапсулирующий аттрибуты состояния"""

    output: OutputDescription
    name: Name
    description: Description
