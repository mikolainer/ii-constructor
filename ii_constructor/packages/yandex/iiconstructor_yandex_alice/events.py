from dataclasses import dataclass
from iiconstructor_core.domain.event_bus import (
    Event
)

@dataclass
class SaveLayEvent(Event):
    state_id: int
    x: float
    y: float

@dataclass
class CreateStateEvent(Event):
    state_id: int
    state_name: str
    state_output: str

@dataclass
class RemoveSynonymEvent(Event):
    input_name: str
    synonym: str

@dataclass
class RemoveVectorEvent(Event):
    input_name: str

@dataclass
class RemoveEnterEvent(Event):
    state_id: int

@dataclass
class RemoveStepEvent(Event):
    from_state_id: int
    input_name: str

@dataclass
class RemoveStateEvent(Event):
    state_id: int

@dataclass
class CreateSynonymEvent(Event):
    input_name: str
    new_synonym: str

@dataclass
class AddVectorEvent(Event):
    input_name: str

@dataclass
class MakeEnterEvent(Event):
    state_id: int
    vector_name: str

@dataclass
class CreateStepEvent(Event):
    from_state_id: int
    to_state_id: int
    input_name: str

@dataclass
class CreateStepToNewStateEvent(Event):
    from_state_id: int
    new_state_id: int
    new_state_name: str
    new_state_output: str
    input_name: str

@dataclass
class UpdateAnswerEvent(Event):
    state_id: int
    new_output: str

@dataclass
class RenameStateEvent(Event):
    state_id: int
    new_name: str

@dataclass
class RenameVectorEvent(Event):
    old_name: str
    new_name: str

@dataclass
class UpdateSynonymEvent(Event):
    input_name: str
    old_synonym: str
    new_synonym: str

@dataclass
class CreateEnterStateEvent(Event):
    new_state_id: int
    new_state_name: str
    new_state_output: str
