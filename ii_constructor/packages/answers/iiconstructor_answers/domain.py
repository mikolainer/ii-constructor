from dataclasses import dataclass

class AnswerValue:
    def as_text(self) -> str:
        """Строковое представление"""


class OutputDescription:
    """Описание ответа - аттрибут состояния"""
    _values: list[AnswerValue]

    def value(self, index:int = 0) -> AnswerValue:
        return self._values[index]

    def __len__(self) -> int:
        return len(self._values)
    
@dataclass(frozen=True)
class State:
    """Состояние"""

    value: int


@dataclass
class OutputLibAttributes:
    """Класс, инкапсулирующий аттрибуты библиотеки выходных значений"""

    name: str
    description: str
    items_type: str


class OutputRepository:
    def create(self, state: State, value: OutputDescription):
        """Создать привязку ответа к состоянию"""

    def read(self, state: State) -> list[OutputDescription]:
        """Получить описание всех ответов состояния"""

    def update(self, state: State, old: OutputDescription, new: OutputDescription):
        """Заменить одно значение ответа другим"""

    def delete(self, state: State, value: OutputDescription):
        """Удалить значение ответа, привязанного к состоянию"""


class OutputLib:
    """Интерфейс репозитория абстрактного описания ответа"""
    __repo: OutputRepository
    __attributes: OutputLibAttributes

    def __init__(self, attributes: OutputLibAttributes, repo: OutputRepository):
        self.__attribbutes = attributes
        self.__repo = repo

    # нет сеттеров. только создание целиком.
    @staticmethod
    def make_default_output() -> OutputDescription:
        """Создать ответ по умолчанию"""

    def parse(self, value: str) -> OutputDescription:
        """Деериализовать значение ответа"""

    def serialize(self, value: OutputDescription) -> str:
        """Сериализовать значение ответа"""

    def attributes(self) -> OutputLibAttributes:
        """Получить аттрибуты библиотеки"""
        return self.__attributes
    
    def update_attributes(self, data:OutputLibAttributes):
        """Установить новые аттрибуты библиотеки"""
        self.__attributes = data

    def create(self, state: State, value: OutputDescription):
        """Создать привязку ответа к состоянию"""
        self.__repo.create(state, value)

    def read(self, state: State) -> list[OutputDescription]:
        """Получить описание всех ответов состояния"""
        return self.__repo.read(state)

    def update(self, state: State, old: OutputDescription, new: OutputDescription):
        """Заменить одно значение ответа другим"""
        self.__repo.update(state, old, new)

    def delete(self, state: State, value: OutputDescription):
        """Удалить значение ответа, привязанного к состоянию"""
        self.__repo.delete(state, value)

