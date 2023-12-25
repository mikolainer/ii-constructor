from alicetool.editor.domain.core import *

class StateMachineInterface:
    ''' предварительное объявление '''

class StateMachine(StateMachineInterface):
    def __init__(self):
        super().__init__()
        self.__states: StateFactory = StateFactory()
        self.__synonyms: SynonymsFactory = SynonymsFactory()
        self.__content: FlowFactory = FlowFactory()

class StateMachineInterface(StateInterface, SynonymsInterface, FlowInterface):
    pass

class StateMachineNotifier(StateActionsNotifier, SynonymsActionsNotifier, FlowActionsNotifier):
    pass

class Project:
    def __init__(self):
        self.__id: int = None
        self.__name: str = 'scenario name'
        self.__db_name: str = 'db_name'
        self.__file_path: str = 'path.proj'
        self.__content: StateMachine = StateMachine()
        self.__notifier: FlowActionsNotifier = None
        self.__entry_point: State = None

    def interface(self) -> StateMachineInterface:
        pass

class ProjectsActionsNotifier:
    def created(id:int, data):
        ...

    def saved(id:int, data):
        ...

    def updated(id:int, new_data):
        ...

    def removed(id:int):
        ...

class ProjectsInterface:
    def create(data) -> int:
        raise NotImplementedError()
    
    def read(id: int):
        raise NotImplementedError()
    
    def read(db_name: str):
        raise NotImplementedError()
    
    def update(id: int, data):
        raise NotImplementedError()
    
    def delete(id: int):
        raise NotImplementedError()
    
    def open_file(path: str):
        raise NotImplementedError()
    
    def save_file(id: int):
        raise NotImplementedError()
    
    def publish(id: int):
        raise NotImplementedError()
    
    def set_notifier(id: int):
        raise NotImplementedError()

class ProjectsManager(ProjectsInterface):
    __items: list[Project] = []
    __notifier: ProjectsActionsNotifier = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.__instance = super(ProjectsManager, cls).__new__(cls)
        return cls.__instance
    
    def instance(self) -> ProjectsInterface:
        return ProjectsManager()
    
    def create(self, data) -> int:
        pass
    
    def read(self, id: int):
        pass
    
    def read(self, db_name: str):
        pass
    
    def update(self, id: int, data):
        pass
    
    def delete(self, id: int):
        pass
    
    def open_file(self, path: str):
        pass
    
    def save_file(self, id: int):
        pass
    
    def publish(self, id: int):
        pass
    
    def set_notifier(self, id: int):
        pass