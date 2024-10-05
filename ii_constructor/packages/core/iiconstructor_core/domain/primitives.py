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
    value:str

    __MIN_LEN:int = 0
    __MAX_LEN:int = 512

    def is_valid(self) -> bool:
        _len:int = len(self.value)
        return _len > self.__MIN_LEN and _len < self.__MAX_LEN
    
    def __eq__(self, value: object) -> bool:
        return isinstance(value, Name) and value.value == self.value

@dataclass(frozen=True)
class Description:
    value:str

    __MIN_LEN:int = 0
    __MAX_LEN:int = 512

    def is_valid(self) -> bool:
        _len:int = len(self.value)
        return _len > self.__MIN_LEN and _len < self.__MAX_LEN

@dataclass#(frozen=True)
class Input:
    value:str

    __MIN_LEN:int = 1
    __MAX_LEN:int = 512
    
    def is_valid(self) -> bool:
        _len:int = len(self.value)
        return _len > self.__MIN_LEN and _len < self.__MAX_LEN

@dataclass(frozen=True)
class ScenarioID:
    value: int

@dataclass(frozen=True)
class StateID:
    value: int

@dataclass(frozen=True)
class Answer:
    text: str
    __MIN_LEN:int = 1
    __MAX_LEN:int = 1024
    
    def is_valid(self) -> bool:
        _len:int = len(self.text)
        return _len > self.__MIN_LEN and _len < self.__MAX_LEN
    
@dataclass(frozen=True)
class Output:
    value: Answer

@dataclass
class StateAttributes:
    output: Output
    name: Name
    description: Description

@dataclass
class SourceInfo:
    name: Name
    description: Description

class Request:
    text: str

class Response:
    text: str
