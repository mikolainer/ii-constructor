from .domain import (
    AnswerValue,
    OutputDescription,
    OutputID,
    OutputRepository,
    OutputLib,
)

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


class PlainTextDescription(OutputDescription):

    # нет сеттеров. только создание целиком.
    def __init__(self, answer: PlainTextAnswer):
        if isinstance(answer, PlainTextAnswer):
            self._values = [answer]
        
        else: raise TypeError(answer)


class PlainTextOutputLib(OutputLib):
    @staticmethod
    def parse(value: str) -> OutputDescription:
        return PlainTextDescription(PlainTextAnswer(value))

    @staticmethod
    def serialize(value: OutputDescription) -> str:
        return value.value().as_text()


class PlainTextOutputInmemoryRepository(OutputRepository):
    __outputs: dict[OutputID, list[OutputDescription]]

    def __init__(self):
        self.__outputs = dict[OutputID, list[OutputDescription]]()

    def create(self, value: OutputDescription, id: OutputID = None):
        if id in self.__outputs.keys():
            self.__outputs[id] = [value]
        else:
            self.__outputs[id].append[value]

    def read(self, id: OutputID) -> list[OutputDescription]:
        return self.__outputs[id]

    def update(self, id: OutputID, old: OutputDescription, new: OutputDescription):
        old_index = self.__outputs[id].index(old)
        self.__outputs[id].pop(old_index)

        new_index = old_index + 1
        if new_index >= len(new_index):
            self.__outputs[id].insert(new_index, new)

    def delete(self, id: OutputID, value: OutputDescription):
        index = self.__outputs[id].index(value)
        self.__outputs[id].pop(index)

        if len(self.__outputs[id]) == 0:
            self.__outputs.pop(id)
