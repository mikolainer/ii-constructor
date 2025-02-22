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
class OutputID:
    value: int


class OutputRepository:
    def create(self, value: OutputDescription, id: OutputID = None):
        """Создать привязку ответа к состоянию"""

    def read(self, id: OutputID) -> list[OutputDescription]:
        """Получить описание всех ответов состояния"""

    def update(self, id: OutputID, old: OutputDescription, new: OutputDescription):
        """Заменить одно значение ответа другим"""

    def delete(self, id: OutputID, value: OutputDescription):
        """Удалить значение ответа, привязанного к состоянию"""


class OutputLib:
    """Интерфейс репозитория абстрактного описания ответа"""
    __repo: OutputRepository

    def __init__(self, repo: OutputRepository):
        self.__repo = repo

    @staticmethod
    def parse(value: str) -> OutputDescription:
        """Деериализовать значение ответа"""

    @staticmethod
    def serialize(value: OutputDescription) -> str:
        """Сериализовать значение ответа"""

    def items_type(self) -> str:
        """Тип обработываетмых ответов"""

    def create(self, value: OutputDescription, id: OutputID = None):
        """Создать привязку ответа к состоянию"""
        self.__repo.create(value, id)

    def read(self, id: OutputID) -> list[OutputDescription]:
        """Получить описание всех ответов состояния"""
        return self.__repo.read(id)

    def update(self, id: OutputID, old: OutputDescription, new: OutputDescription):
        """Заменить одно значение ответа другим"""
        self.__repo.update(id, old, new)

    def delete(self, id: OutputID, value: OutputDescription):
        """Удалить значение ответа, привязанного к состоянию"""
        self.__repo.delete(id, value)

