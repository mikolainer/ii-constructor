from dataclasses import dataclass

@dataclass(frozen=True)
class VectorName:
    """Аттрибут названия для именуемых объектов"""

    value: str

    __MIN_LEN: int = 0
    __MAX_LEN: int = 512

    def is_valid(self) -> bool:
        _len: int = len(self.value)
        return self.__MIN_LEN < _len < self.__MAX_LEN

    def __eq__(self, value: object) -> bool:
        return isinstance(value, VectorName) and value.value == self.value
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
    __name: VectorName
    __values: list[Input]

    # нет сеттеров. только создание целиком.
    def __init__(self, name: VectorName, value: list[Input] | Input | None) -> None:
        self.__name = name
        if value is None:
            self.__values = [StrInput("")]
        elif isinstance(value, list):
            if len(value) == 0:
                self.__values = [StrInput("")]
            else:
                self.__values = value
        else:
            self.__values = [value]

    def value(self, index:int = 0) -> Input:
        return self.__values[index]

    def name(self) -> VectorName:
        return self.__name

    def set_name(self, new_name: VectorName) -> None:
        self.__name = new_name

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, InputDescription) and value.name() == self.__name
        )
    
    def __len__(self) -> int:
        return len(self.__values)
    
    def _values(self) -> list[Input]:
        return self.__values.copy()