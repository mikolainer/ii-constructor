from alicetool.editor.domain.projects import ProjectsManager, ProjectsActionsNotifier
from alicetool.editor.domain.core import State

class EditorAPI:
    STATE_TEXT_MAX_LEN = State.TEXT_MAX_LEN

    def __new__(cls, notifier: ProjectsActionsNotifier = None):
        if not hasattr(cls, '__instance') and notifier is not None:
            ProjectsManager.instance().set_notifier(notifier)
            cls.__instance = super(EditorAPI, cls).__new__(cls)
        
        return cls.__instance

    def create_project(self, data: str):
        ProjectsManager.instance().create(data)
