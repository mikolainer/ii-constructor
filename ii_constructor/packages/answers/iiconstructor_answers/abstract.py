from .primitives import OutputType, OutputID

class OutputDescription:
    def get_type(self) -> OutputType:
        pass

class Output:
    __id: OutputID
    __description: OutputDescription

    def __init__(self, id: OutputID, description: OutputDescription):
        setattr(self, "_Output__id", id)
        setattr(self, "_Output__description", description)

    def id(self) -> OutputID:
        return getattr(self, "_Output__id")
    
    def description(self) -> OutputID:
        return getattr(self, "_Output__description")