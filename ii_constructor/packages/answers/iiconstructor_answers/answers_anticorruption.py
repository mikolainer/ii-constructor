from .domain import State, OutputDescription
from .plaintext import PlainTextDescription, PlainTextOutputLib
from iiconstructor_core.domain import StateID

class StateTranslator:
    @staticmethod
    def from_scenario(state_id: StateID) -> State:
        return State(state_id.value)

    @staticmethod
    def to_scenario(state_id: State) -> StateID:
        return StateID(state_id.value)

        
class OutDescriptionTranslator:
    @staticmethod
    def from_scenario(out: str) -> OutputDescription:
        # TODO: сделать что-то умнее
        plugins = [PlainTextDescription] 
        for plugin in plugins:
            try:
                return PlainTextOutputLib.parse(out)
            except:
                pass

        raise ValueError(out)

    @staticmethod
    def to_scenario(out: OutputDescription) -> str:
        # TODO: сделать что-то умнее
        if isinstance(out, PlainTextDescription):
            return PlainTextOutputLib.serialize(out)