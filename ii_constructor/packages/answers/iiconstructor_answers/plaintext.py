from .domain import (
    OutputDescription,
    OutputID,
    OutputRepository,
    OutputLib,
)

from iiconstructor_answers import Output_DTO

class PlainTextOutput_DTO(Output_DTO):
    __value: str

    def __init__(self, obj: "PlainTextDescription" | dict):
        if isinstance(obj, PlainTextDescription):
            self.__value = obj.as_text()

        elif isinstance(obj, dict):
            self.__value = obj["value"]

    @staticmethod
    def as_dict(obj: Output) -> dict:
        return {"value": self.__value}

    def as_text(self) -> str:
        return self.__value
    
    def as_value(self) -> OutputDescription:
        return PlainTextDescription(self.__value)
    
class PlainTextDescription(OutputDescription):
    # нет сеттеров. только создание целиком.
    __text: str

    def __init__(self, text:str):
        self.__text = text

    def as_text(self) -> str:
        return self.__text


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
