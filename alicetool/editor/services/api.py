from alicetool.editor.domain.projects import ProjectsManager, ProjectsActionsNotifier, StateMachineNotifier
from alicetool.editor.domain.core import State

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