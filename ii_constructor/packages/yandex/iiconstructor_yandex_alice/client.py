from iiconstructor_core.domain import (
    InputDescription,
    SourceInterface,
    State,
    Step,
)
from iiconstructor_core.domain.primitives import (
    Name,
    Description,
    Answer,
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
from iiconstructor_levenshtain import LevenshtainVector

class ScenarioEventHandler(EventHandler):
    _slave: ScenarioInterface

    def __init__(self, client: ScenarioInterface):
        super().__init__()
        self._slave = client

class SaveLayEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: SaveLayEvent = ev
        self._slave.save_lay(StateID(_ev.state_id), _ev.x, _ev.y)

    @staticmethod
    def event_type() -> type:
        return SaveLayEvent

class CreateStateEventHandler(ScenarioEventHandler): # not used?
    def handle(self, ev: Event):
        _ev: CreateStateEvent = ev
        #self.__slave.create_state()

    @staticmethod
    def event_type() -> type:
        return CreateStateEvent

class RemoveSynonymEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: RemoveSynonymEvent = ev
        self._slave.remove_synonym(_ev.input_name, _ev.synonym)

    @staticmethod
    def event_type() -> type:
        return RemoveSynonymEvent

class RemoveVectorEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: RemoveVectorEvent = ev
        self._slave.remove_vector(Name(_ev.input_name))

    @staticmethod
    def event_type() -> type:
        return RemoveVectorEvent

class RemoveEnterEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: RemoveEnterEvent = ev
        self._slave.remove_enter(StateID(_ev.state_id))

    @staticmethod
    def event_type() -> type:
        return RemoveEnterEvent

class RemoveStepEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: RemoveStepEvent = ev
        self._slave.remove_step(
            StateID(_ev.from_state_id),
            self._slave.get_vector(Name(_ev.input_name))
        )

    @staticmethod
    def event_type() -> type:
        return RemoveStepEvent

class RemoveStateEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: RemoveStateEvent = ev
        self._slave.remove_state(StateID(_ev.state_id))

    @staticmethod
    def event_type() -> type:
        return RemoveStateEvent

class CreateSynonymEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: CreateSynonymEvent = ev
        self._slave.create_synonym(_ev.input_name, _ev.new_synonym)

    @staticmethod
    def event_type() -> type:
        return CreateSynonymEvent

class AddVectorEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: AddVectorEvent = ev
        self._slave.add_vector(LevenshtainVector(Name(_ev.input_name)))

    @staticmethod
    def event_type() -> type:
        return AddVectorEvent

class MakeEnterEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: MakeEnterEvent = ev
        self._slave.make_enter(StateID(_ev.state_id))

    @staticmethod
    def event_type() -> type:
        return MakeEnterEvent

class CreateStepEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: CreateStepEvent = ev
        self._slave.create_step(
            StateID(_ev.from_state_id),
            StateID(_ev.to_state_id),
            self._slave.get_vector(Name(_ev.input_name))
        )

    @staticmethod
    def event_type() -> type:
        return CreateStepEvent

class CreateStepToNewStateEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: CreateStepToNewStateEvent = ev

        self._slave.source().prepare_new_state_id(_ev.new_state_id)
        self._slave.source().create_state(
            StateAttributes(
                OutputDescription(Answer(_ev.new_state_output)),
                Name(_ev.new_state_name),
                Description(""),
            ),
        )

        self._slave.create_step(
            StateID(_ev.from_state_id),
            StateID(_ev.new_state_id),
            self._slave.get_vector(Name(_ev.input_name))
        )

    @staticmethod
    def event_type() -> type:
        return CreateStepToNewStateEvent

class UpdateAnswerEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: UpdateAnswerEvent = ev
        self._slave.set_answer(StateID(_ev.state_id), OutputDescription(Answer(_ev.new_output)))

    @staticmethod
    def event_type() -> type:
        return UpdateAnswerEvent

class RenameStateEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: RenameStateEvent = ev
        self._slave.rename_state(StateID(_ev.state_id), Name(_ev.new_name))

    @staticmethod
    def event_type() -> type:
        return RenameStateEvent

class RenameVectorEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: RenameVectorEvent = ev
        self._slave.rename_vector(Name(_ev.old_name), Name(_ev.new_name))

    @staticmethod
    def event_type() -> type:
        return RenameVectorEvent

class UpdateSynonymEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: UpdateSynonymEvent = ev
        self._slave.set_synonym_value(
            _ev.input_name,
            _ev.old_synonym,
            _ev.new_synonym,
        )

    @staticmethod
    def event_type() -> type:
        return UpdateSynonymEvent

class CreateEnterStateEventHandler(ScenarioEventHandler):
    def handle(self, ev: Event):
        _ev: CreateEnterStateEvent = ev
        self._slave.source().prepare_new_state_id(_ev.new_state_id)
        self._slave.source().create_state(
            StateAttributes(
                OutputDescription(Answer(_ev.new_state_output)),
                Name(_ev.new_state_name),
                Description(""),
            ),
        )
        # make enter прилетит отдельно

    @staticmethod
    def event_type() -> type:
        return CreateEnterStateEvent

class ScenarioEventListener(Subscriber):
    __handlers: dict[type, ScenarioEventHandler]

    def __init__(self, client: ScenarioInterface):
        self.__handlers = dict[type, ScenarioEventHandler]()
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
