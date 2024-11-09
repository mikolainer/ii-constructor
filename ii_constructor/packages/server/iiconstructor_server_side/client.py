from iiconstructor_core.domain import (
    InputDescription,
    Source,
    State,
    Step,
    _Exists,
)
from iiconstructor_core.domain.exceptions import (
    CoreException,
    Exists,
    NotExists,
)
from iiconstructor_core.domain.primitives import (
    Name,
    Output,
    StateAttributes,
    StateID,
)

from iiconstructor_core.domain.event_bus import(
    Subscriber,
    EventHandler,
    EventBus
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
from iiconstructor_server_side.ports import ScenarioInterface

class ClientEventHandler(EventHandler):
    __client: ScenarioInterface

    def __init__(self, client: ScenarioInterface):
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

    def __init__(self, client: ScenarioInterface):
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

class Slave(ScenarioInterface):
    __src: Source
    
    # Scenario public

    def __init__(self, src: Source, bus: EventBus | None = None) -> None:
        self.__src = src
        
        if issubclass(type(bus), EventBus):
            bus.subscribe(ScenarioEventListener(self))

    def source(self) -> Source:
        return self.__src

    def get_layouts(self) -> str:
        return self.__src.get_layouts()
    
    def get_states_by_name(self, name: Name) -> list[State]:
        """получить все состояния с данным именем"""
        return self.__src.get_states_by_name(name)

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        """получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния"""
        return self.__src.states(ids)

    def steps(self, state_id: StateID) -> list[Step]:
        """получить все переходы, связанные с состоянием по его идентификатору"""
        return self.__src.steps(state_id)

    def is_enter(self, state: State) -> bool:
        """Проверить является ли состояние входом"""
        return self.__src.is_enter(state)
    
    def select_vectors(
        self,
        names: list[Name] | None = None,
    ) -> list["InputDescription"]:
        """
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        """
        return self.__src.select_vectors(names)

    def get_vector(self, name: Name) -> InputDescription:
        """
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        """
        return self.__src.get_vector(name)
    
    def check_vector_exists(self, name: Name) -> bool:
        """
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        """
        return self.__src.check_vector_exists(name)

    def save_lay(self, id: StateID, x: float, y: float):
        self.__src.save_lay(id, x, y)

    # создание сущностей
    def create_enter_state(
        self,
        input: InputDescription,
        required: bool = False,
    ) -> StateID:
        """добавляет вектор и новое состояние-вход с таким-же именем"""
        # добавление вектора обработается раньше в своём handler'е
        self.__src.create_state(StateAttributes(None, input.name(), None), required)

    def create_enter_vector(self, input: InputDescription, state_id: StateID):
        """Создаёт вектор с соответствующим состоянию именем"""
        # обрабатывается как AddVectorEvent

    def make_enter(self, state_id: StateID):
        """привязывает к состоянию существующий вектор с соответствующим именем как команду входа"""
        state_to: State = self.states([state_id])[state_id]
        self.__src.new_step(None, state_id, state_to.attributes.name)

    def create_step(
        self,
        from_state_id: StateID,
        to_state: StateAttributes | StateID,
        input: InputDescription,
    ) -> Step:
        """
        Создаёт переход из from_state в to_state по переходу input
        @from_state_id: id состояния для обработки управляющего воздействия input
        @to_state: id состояния в которое будет добавлен переход или аттрибуты для создания такого состояния
        @input: управляющее воздействие
        """
        state_to: State

        if isinstance(to_state, StateID):
            state_to = self.states([to_state])[to_state]

        elif isinstance(to_state, StateAttributes):
            state_to = self.__src.create_state(to_state)

        new_step = self.__src.new_step(from_state_id, state_to.id(), input.name())
        # CreateStepEvent | CreateStepToNewStateEvent

    # удаление сущностей

    def remove_state(self, state_id: StateID):
        """удаляет состояние"""
        self.__src.delete_state(state_id)

    def remove_enter(self, state_id: StateID):
        """удаляет связь с командой входа в состояние"""
        self.__src.delete_step(None, state_id)

    def remove_step(self, from_state_id: StateID, input: InputDescription):
        """
        удаляет связь между состояниями
        @from_state_id: состояние - обработчик управляющих воздействий
        @input: управляющее воздействие
        """
        self.__src.delete_step(from_state_id, None, input.name())

    def set_answer(self, state_id: StateID, data: Output):
        """Изменить ответ состояния"""
        self.__src.set_answer(state_id, data)

    def add_vector(self, input: InputDescription):
        """
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        """
        self.__src.add_vector(input)

    def remove_vector(self, name: Name):
        """
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        """
        self.__src.remove_vector(name)

    def set_synonym_value(
        self,
        input_name: str,
        old_synonym: str,
        new_synonym: str,
    ):
        """изменяет значение синонима"""
        self.__src.set_synonym_value(input_name, old_synonym, new_synonym)

    def create_synonym(self, input_name: str, new_synonym: str):
        """создаёт синоним"""
        self.__src.create_synonym(input_name, new_synonym)

    def remove_synonym(self, input_name: str, synonym: str):
        """удаляет синоним"""
        self.__src.remove_synonym(input_name, synonym)

    def rename_state(self, state: StateID, name: Name):
        """Переименовывает состояние"""
        self.__src.rename_state(state, name)

    def rename_vector(self, old_name: Name, new_name: Name):
        """переименовывает группу синонимов"""
        self.__src.rename_vector(old_name, new_name)