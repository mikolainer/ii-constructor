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

    def __init__(self, repo: OutputRepository):
        self.__repo = repo

    # нет сеттеров. только создание целиком.
    @staticmethod
    def make_default_output() -> OutputDescription:
        """Создать ответ по умолчанию"""

    @staticmethod
    def parse(value: str) -> OutputDescription:
        """Деериализовать значение ответа"""

    @staticmethod
    def serialize(value: OutputDescription) -> str:
        """Сериализовать значение ответа"""

    def items_type(self) -> str:
        """Тип обработываетмых ответов"""

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

