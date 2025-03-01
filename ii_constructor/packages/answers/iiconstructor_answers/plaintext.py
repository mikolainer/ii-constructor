from primitives import OutputType
from data import OutputRepository, OutputFactory, OutputDescription

class PlainTextOutputRepository(OutputRepository):
    pass

class PlainTextOutputFactory(OutputFactory):
    pass

class PlainTextDescription(OutputDescription):
    def get_type(self) -> OutputType:
        return OutputType("PlainText")