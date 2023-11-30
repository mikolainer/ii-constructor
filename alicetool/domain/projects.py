from .states import State, StatesRepository
from .flows import Flow, MainFlow, FlowsRepository
from .commands import Synonyms, SynonymsRepository


class Project:
    _HELPFLOW_NAME = 'Помощь'
    _INFOFLOW_NAME = 'Что ты умеешь?'

    class ProjectData:
        def __init__(self):
            self.name: str = 'name'
            self.db_name: str = 'db_name'
            self.file_path: str = 'file_path'
            self.hello: State = 'hello'
            self.help: State = 'help'
            self.info: State = 'info'

    class StartProjectData:
        def __init__(self):
            self.name: str = 'name'
            self.db_name: str = 'db_name'
            self.file_path: str = 'file_path'
            self.hello: str = 'hello'
            self.help: str = 'help'
            self.info: str = 'info'

    def __init__(self, data:StartProjectData = None):
        self.states: StatesRepository
        self.flows: FlowsRepository
        self.synonyms: SynonymsRepository

        self.name: str = '' if data is None else data.name
        self.db_name: str = '' if data is None else data.db_name
        self.file_path: str = '' if data is None else data.file_path
        
        hello: str = '' if data is None else data.hello
        self.scenario: MainFlow(hello)
        
        help: str = '' if data is None else data.help
        help_flow: Flow = self.flows.create(
            project = self, 
            name = self._HELPFLOW_NAME, 
            content = help, 
            cmd = Synonyms(['Помощь'])
        )
        
        info: str = '' if data is None else data.info
        info_flow: Flow = self.flows.create(
            project = self,
            name = self._INFOFLOW_NAME,
            content = info,
            cmd = Synonyms(['Что ты умеешь?', 'Информация'])
        )

class ProjectActionsNotifier:
    pass

class ProjectInterface:
    pass

class ProjectsRepository:
    pass