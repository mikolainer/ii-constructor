from alicetool.editor.domain.projects import Project, ProjectsActionsNotifier, StateMachineNotifier
from alicetool.editor.infrastructure.gui import Workspaces, ProjectQtController, StateMachineQtController

class StateMachineGuiRefresher(StateMachineNotifier):
    def state_created(self, project_id :int, id :int, data):
        ...
    
    def state_updated(self, project_id :int, id :int, new_data):
        ...
    
    def state_removed(self, project_id :int, id :int):
        ...
    
    def synonyms_created(self, project_id :int, id :int, data):
        ...
    
    def synonyms_updated(self, project_id :int, id :int, new_data):
        ...
    
    def synonyms_removed(self, project_id :int, id :int):
        ...
    
    def flow_created(self, project_id :int, id :int, data):
        ...
    
    def flow_updated(self, project_id :int, id :int, new_data):
        ...
    
    def flow_removed(self, project_id :int, id :int):
        ...
        
class EditorGuiRefresher(ProjectsActionsNotifier):
    def __init__(self, workspaces: Workspaces, set_content_refresher_callback):
        self.__workspaces = workspaces
        self.__set_content_refresher = set_content_refresher_callback

    def created(self, id:int, data):
        self.__workspaces.add_project(id, Project.parse(data))
        self.__set_content_refresher(id, StateMachineGuiRefresher())
        self.__workspaces.set_active_project(id)

    def saved(self, id:int, data):
        project: ProjectQtController = self.__workspaces.project(id)
        project.clear_changes()

    def updated(self, id:int, new_data):
        project: ProjectQtController = self.__workspaces.project(id)
        # TODO: отлов изменений для истории

    def removed(self, id:int):
        self.__workspaces.close_project(id)
