from alicetool.domain.core import State, Flow, Synonyms
from alicetool.domain.projects import ProjectsManager
from alicetool.domain.interfaces import ProjectsActionsNotifier, StateMachineNotifier, StateMachineInterface

class EditorAPI:
    STATE_TEXT_MAX_LEN = State.TEXT_MAX_LEN

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_EditorAPI__instance'):
            cls.__instance = super(EditorAPI, cls).__new__(cls)
        
        return cls.__instance
    
    def __init__(self, notifier: ProjectsActionsNotifier = None):
        if notifier is None and not hasattr(EditorAPI, '_EditorAPI__instance'):
            raise RuntimeError('notifier must be not None to init')
        
        if not notifier is None:
            ProjectsManager.instance().set_notifier(notifier)
    
    @staticmethod
    def instance():
        return EditorAPI()

    def create_project(self, data: str):
        ProjectsManager.instance().create(data)

    def set_content_notifier(self, project_id: int, notifier: StateMachineNotifier):
        ProjectsManager.instance().set_content_notifier(project_id, notifier)

    def get_all_project_synonyms(self, project_id: int) -> dict:
        state_machinne: StateMachineInterface = (
            ProjectsManager()._ProjectsManager__project(project_id).content_interface()
        )
        result = {}
        for synonym_group_id in state_machinne.synonyms():
            result[synonym_group_id] = Synonyms.parse(
                state_machinne.read_synonyms(synonym_group_id)
            )
        
        return result

    def get_all_project_states(self, project_id: int) -> dict:
        state_machinne: StateMachineInterface = (
            ProjectsManager()._ProjectsManager__project(project_id).content_interface()
        )
        result = {}
        for state_id in state_machinne.states():
            result[state_id] = State.parse(
                state_machinne.read_state(state_id)
            )

        return result
    
    def get_all_project_flows(self, project_id: int) -> dict:
        state_machinne: StateMachineInterface = (
            ProjectsManager()._ProjectsManager__project(project_id).content_interface()
        )
        result = {}
        for flow_id in state_machinne.flows():
            result[flow_id] = Flow.parse(
                state_machinne.read_flow(flow_id)
            )

        return result
    
    def add_step(self, project_id: int, from_id: int, to_id:int, synonyms_g_id:int):
        state_machinne: StateMachineInterface = (
            ProjectsManager()._ProjectsManager__project(project_id).content_interface()
        )
        state_machinne.add_step(from_id, to_id, synonyms_g_id)