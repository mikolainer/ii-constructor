from abc import ABC, abstractmethod
from iiconstructor_outputs.primitives import OutputType, OutputID

class OutputContent(ABC):
    @abstractmethod
    @staticmethod
    def get_type() -> OutputType:
        pass

class Output:
    __id: OutputID
    __description: OutputContent

    def __init__(self, id: OutputID, description: OutputContent):
        setattr(self, "_Output__id", id)
        setattr(self, "_Output__description", description)

    def id(self) -> OutputID:
        return getattr(self, "_Output__id")
    
    def description(self) -> OutputContent:
        return getattr(self, "_Output__description")
