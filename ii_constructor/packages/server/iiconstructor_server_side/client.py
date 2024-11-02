from iiconstructor_core.domain.event_bus import(
    InmemoryEventBus,
    Subscriber,
    EventHandler,
)
from iiconstructor_server_side.events import (
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

class ClientInterface:
    pass

class Client(ClientInterface):
    def __init__(self):
        pass

class ClientEventHandler(EventHandler):
    __client: ClientInterface

    def __init__(self, client: ClientInterface):
        super().__init__()
        self.__client = client

class SaveLayEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return SaveLayEvent

class CreateStateEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateStateEvent

class RemoveSynonymEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveSynonymEvent

class RemoveVectorEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveVectorEvent

class RemoveEnterEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveEnterEvent

class RemoveStepEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveStepEvent

class RemoveStateEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RemoveStateEvent

class CreateSynonymEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateSynonymEvent

class AddVectorEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return AddVectorEvent

class MakeEnterEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return MakeEnterEvent

class CreateStepEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateStepEvent

class CreateStepToNewStateEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateStepToNewStateEvent

class UpdateAnswerEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return UpdateAnswerEvent

class RenameStateEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RenameStateEvent

class RenameVectorEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return RenameVectorEvent

class UpdateSynonymEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return UpdateSynonymEvent

class CreateEnterStateEventHandler(ClientEventHandler):
    def handle(self, ev: Event):
        pass

    @staticmethod
    def event_type() -> type:
        return CreateEnterStateEvent

class ScenarioEventListener(Subscriber):
    __handlers: dict[type, ClientEventHandler]

    def __init__(self, client: ClientInterface):
        self.__handlers = dict[type, ClientEventHandler]
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