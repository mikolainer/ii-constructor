from .domain import (
    AnswerValue,
    OutputDescription,
    State,
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
    # нет сеттеров. только создание целиком.
    @staticmethod
    def make_default_output() -> OutputDescription:
        return PlainTextDescription(PlainTextAnswer("Текст ответа"))

    def parse(self, value: str) -> OutputDescription:
        return PlainTextDescription(PlainTextAnswer(value))

    def serialize(self, value: OutputDescription) -> str:
        return value.value().as_text()


class PlainTextOutputInmemoryRepository(OutputRepository):
    __outputs: dict[State, list[OutputDescription]]

    def __init__(self):
        self.__outputs = dict[State, list[OutputDescription]]()

    def create(self, state: State, value: OutputDescription):
        if state in self.__outputs.keys():
            self.__outputs[state] = [value]
        else:
            self.__outputs[state].append[value]

    def read(self, state: State) -> list[OutputDescription]:
        return self.__outputs[state]

    def update(self, state: State, old: OutputDescription, new: OutputDescription):
        old_index = self.__outputs[state].index(old)
        self.__outputs[state].pop(old_index)

        new_index = old_index + 1
        if new_index >= len(new_index):
            self.__outputs[state].insert(new_index, new)

    def delete(self, state: State, value: OutputDescription):
        index = self.__outputs[state].index(value)
        self.__outputs[state].pop(index)

        if len(self.__outputs[state]) == 0:
            self.__outputs.pop(state)
