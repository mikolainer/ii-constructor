from collections.abc import Callable

from PySide6.QtWidgets import QWidget

from alicetool.application.projects import ProjectsActionsNotifier, StateMachineNotifier
from alicetool.presentation.gui import ProjectQtController, StateMachineQtController, FlowList, SynonymsEditor, Workspaces

class StateMachineGuiRefresher(StateMachineNotifier):
    __sm_ctrl: StateMachineQtController

    def __init__(self, sm_ctrl:StateMachineQtController ):
        self.__sm_ctrl = sm_ctrl

    def step_added(self, from_state:int, to_state:int, synonyms_id:int):
        self.__sm_ctrl.step_added(from_state, to_state, synonyms_id)

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
    '''
    обработчик изменений верхнего уровня
    создаёт и удаляет инфраструктурные контроллеры
    '''
    __opened_projects: dict[int, ProjectQtController]
    __set_content_refresher: Callable[[int, StateMachineNotifier], None]
    __flow_list: FlowList
    __synonyms: SynonymsEditor
    __workspaces: Workspaces
    __main_window: QWidget

    def __init__( self,
        set_content_refresher_callback: Callable[
            [int, StateMachineNotifier], None
        ],
        flow_list: FlowList,
        synonyms: SynonymsEditor,
        workspaces: Workspaces,
        main_window: QWidget
    ):
        self.__opened_projects = {}
        self.__set_content_refresher = set_content_refresher_callback
        self.__flow_list = flow_list
        self.__synonyms = synonyms
        self.__workspaces = workspaces
        self.__main_window = main_window

    def created(self, id:int, data):
        # парсинг
        name:str
        for item in data.split('; '):
            _item = item.split('=')
            key = _item[0]
            if key != 'name': continue
            
            value = _item[1]
            quoted = len(value) > 2 and value[0] == '"' and value[-1] == '"'
            name = value[1:-1] if quoted else value
            break

        p_ctrl = ProjectQtController(id, name if len(name) > 0 else str(id) )
        self.__opened_projects[id] = p_ctrl
        
        c_ctrl = StateMachineQtController(p_ctrl, self.__flow_list, self.__synonyms, self.__main_window)
        p_ctrl.set_sm_ctrl(c_ctrl)

        self.__set_content_refresher(id, StateMachineGuiRefresher(c_ctrl))

        self.__workspaces.add_editor(p_ctrl.editor())
        self.__workspaces.set_active(id)

    def saved(self, id:int, data):
        self.__opened_projects[id].saved()

    def updated(self, id:int, new_data):
        # TODO: отлов изменений для истории
        self.__opened_projects[id].update(new_data)

    def removed(self, id:int):
        self.__opened_projects[id].close()
        del self.__opened_projects[id]
