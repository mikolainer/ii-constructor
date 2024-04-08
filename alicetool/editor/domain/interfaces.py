''' интерфейсы обратной связи '''

class FlowActionsNotifier:
    def flow_created(self, project_id :int, id :int, data):
        raise NotImplementedError()
    def flow_updated(self, project_id :int, id :int, new_data):
        raise NotImplementedError()
    def flow_removed(self, project_id :int, id :int):
        raise NotImplementedError()

class SynonymsActionsNotifier:
    def synonyms_created(self, project_id :int, id :int, data):
        raise NotImplementedError()
    def synonyms_updated(self, project_id :int, id :int, new_data):
        raise NotImplementedError()
    def synonyms_removed(self, project_id :int, id :int):
        raise NotImplementedError()
    
class StateActionsNotifier:
    def state_created(self, project_id :int, id :int, data):
        raise NotImplementedError()
    def state_updated(self, project_id :int, id :int, new_data):
        raise NotImplementedError()
    def state_removed(self, project_id :int, id :int):
        raise NotImplementedError()
    def step_added(self, from_state:int, to_state:int, synonyms_id:int):
        raise NotImplementedError()
    
class StateMachineNotifier(StateActionsNotifier, SynonymsActionsNotifier, FlowActionsNotifier):
    ...

class ProjectsActionsNotifier:
    def created(self, id:int, data):
        raise NotImplementedError()
    def saved(self, id:int, data):
        raise NotImplementedError()
    def updated(self, id:int, new_data):
        raise NotImplementedError()
    def removed(self, id:int):
        raise NotImplementedError()

''' интерфейсы управления '''

class FlowInterface:
    def create_flow(self, data) -> int:
        raise NotImplementedError()
    def read_flow(self, id: int) -> str:
        raise NotImplementedError()
    def update_flow(self, id: int, new_data):
        raise NotImplementedError()
    def delete_flow(self, id: int):
        raise NotImplementedError()
    def flows(self) -> set[int]:
        raise NotImplementedError()
    def set_flow_notifier(self, notifier: FlowActionsNotifier):
        raise NotImplementedError()
    
class StateInterface:
    def create_state(self, data) -> int:
        raise NotImplementedError()
    def read_state(self, id: int) -> str:
        raise NotImplementedError()
    def update_state(self, id: int, new_data):
        raise NotImplementedError()
    def delete_state(self, id: int):
        raise NotImplementedError()
    def states(self) -> set[int]:
        raise NotImplementedError()
    def set_state_notifier(self, notifier: StateActionsNotifier):
        raise NotImplementedError()
    def add_step(self, from_id:int, to_id:int, cmd):
        raise NotImplementedError()

class SynonymsInterface:
    def create_synonyms(self, data) -> int:
        raise NotImplementedError()
    def read_synonyms(self, id: int) -> str:
        raise NotImplementedError()
    def update_synonyms(self, id: int, new_data):
        raise NotImplementedError()
    def delete_synonyms(self, id: int):
        raise NotImplementedError()
    def synonyms(self) -> set[int]:
        raise NotImplementedError()
    def set_synonyms_notifier(self, notifier: SynonymsActionsNotifier):
        raise NotImplementedError()
    
class StateMachineInterface(StateInterface, SynonymsInterface, FlowInterface):
    def states_interface(self) -> StateInterface:
        raise NotImplementedError()
    def synonyms_interface(self) -> SynonymsInterface:
        raise NotImplementedError()
    def content_interface(self) -> FlowInterface:
        raise NotImplementedError()
    def add_step(self, from_state:int, to_state:int, synonyms:int):
        raise NotImplementedError()

class ProjectsInterface:
    def create(self, data) -> int:
        raise NotImplementedError() 
    def read(self, id: int):
        raise NotImplementedError()
    def read(self, db_name: str):
        raise NotImplementedError()
    def update(self, id: int, data):
        raise NotImplementedError()
    def delete(self, id: int):
        raise NotImplementedError()
    def open_file(self, path: str):
        raise NotImplementedError()
    def save_file(self, id: int):
        raise NotImplementedError()
    def publish(self, id: int):
        raise NotImplementedError()
    def set_notifier(self, notifier: ProjectsActionsNotifier):
        raise NotImplementedError()
    def set_content_notifier(self, 
        project_id: int, notifier: StateMachineNotifier
    ):
        raise NotImplementedError()