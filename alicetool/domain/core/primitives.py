from dataclasses import dataclass
from typing import Optional

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
