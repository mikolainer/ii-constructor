from iiconstructor_core.domain import (
    InputDescription,
    SourceInterface,
    State,
    Step,
)
from iiconstructor_core.domain.primitives import (
    Name,
    OutputDescription,
    StateAttributes,
    StateID,
)

from iiconstructor_core.domain.event_bus import(
    Subscriber,
    EventHandler,
    EventBus
)

from iiconstructor_yandex_alice.events import (
    Event,
    SaveLayEvent,
    CreateStateEvent,
    RemoveSynonymEvent,
    RemoveVectorEvent,
    RemoveEnterEvent,
    RemoveStepEvent,
    RemoveStateEvent,
    CreateSynonymEvent,
    AddVectorEvent,
    MakeEnterEvent,
    CreateStepEvent,
    CreateStepToNewStateEvent,
    UpdateAnswerEvent,
    RenameStateEvent,
    RenameVectorEvent,
    UpdateSynonymEvent,
    CreateEnterStateEvent,
)
from iiconstructor_yandex_alice.ports import ScenarioInterface

class ScenarioEventHandler(EventHandler):
    __slave: ScenarioInterface

    def __init__(self, client: ScenarioInterface):
        super().__init__()
        self.__slave = client

class SaveLayEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return SaveLayEvent

class CreateStateEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateStateEvent

class RemoveSynonymEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveSynonymEvent

class RemoveVectorEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveVectorEvent

class RemoveEnterEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveEnterEvent

class RemoveStepEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveStepEvent

class RemoveStateEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveStateEvent

class CreateSynonymEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateSynonymEvent

class AddVectorEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return AddVectorEvent

class MakeEnterEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return MakeEnterEvent

class CreateStepEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateStepEvent

class CreateStepToNewStateEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateStepToNewStateEvent

class UpdateAnswerEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return UpdateAnswerEvent

class RenameStateEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RenameStateEvent

class RenameVectorEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RenameVectorEvent

class UpdateSynonymEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return UpdateSynonymEvent

class CreateEnterStateEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateEnterStateEvent

class ScenarioEventListener(Subscriber):
    __handlers: dict[type, ScenarioEventHandler]

    def __init__(self, client: ScenarioInterface):
        self.__handlers = dict[type, ScenarioEventHandler]
        self.__handlers[SaveLayEventHandler.event_type()] = SaveLayEventHandler(client)
        self.__handlers[CreateStateEventHandler.event_type()] = CreateStateEventHandler(client)
        self.__handlers[RemoveSynonymEventHandler.event_type()] = RemoveSynonymEventHandler(client)
        self.__handlers[RemoveVectorEventHandler.event_type()] = RemoveVectorEventHandler(client)
        self.__handlers[RemoveEnterEventHandler.event_type()] = RemoveEnterEventHandler(client)
        self.__handlers[RemoveStepEventHandler.event_type()] = RemoveStepEventHandler(client)
        self.__handlers[RemoveStateEventHandler.event_type()] = RemoveStateEventHandler(client)
        self.__handlers[CreateSynonymEventHandler.event_type()] = CreateSynonymEventHandler(client)
        self.__handlers[AddVectorEventHandler.event_type()] = AddVectorEventHandler(client)
        self.__handlers[MakeEnterEventHandler.event_type()] = MakeEnterEventHandler(client)
        self.__handlers[CreateStepEventHandler.event_type()] = CreateStepEventHandler(client)
        self.__handlers[CreateStepToNewStateEventHandler.event_type()] = CreateStepToNewStateEventHandler(client)
        self.__handlers[UpdateAnswerEventHandler.event_type()] = UpdateAnswerEventHandler(client)
        self.__handlers[RenameStateEventHandler.event_type()] = RenameStateEventHandler(client)
        self.__handlers[RenameVectorEventHandler.event_type()] = RenameVectorEventHandler(client)
        self.__handlers[UpdateSynonymEventHandler.event_type()] = UpdateSynonymEventHandler(client)
        self.__handlers[CreateEnterStateEventHandler.event_type()] = CreateEnterStateEventHandler(client)


    def triggered(self, ev: Event):
        ev_type = type(ev)
        if ev_type in self.__handlers:
            handler = self.__handlers[ev_type]
            handler.handle(ev)
