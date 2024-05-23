from collections.abc import Callable

from PySide6.QtWidgets import QWidget, QInputDialog

from alicetool.application.projects import ProjectsActionsNotifier, StateMachineNotifier
from alicetool.presentation.gui import ProjectQtController, StateMachineQtController, Editor
from alicetool.infrastructure.widgets import FlowList, Workspaces
from alicetool.infrastructure.windows import SynonymsEditor
from alicetool.infrastructure.data import SynonymsGroupsModel, SynonymsSetModel, CustomDataRole

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
    __opened_projects: dict[int, ProjectQtController]
    __set_content_refresher: Callable[[int, StateMachineNotifier], None]
    __flow_list: FlowList
    __workspaces: Workspaces
    __main_window: QWidget

    def __init__( self,
        set_content_refresher_callback: Callable[
            [int, StateMachineNotifier], None
        ],
        flow_list: FlowList,
        workspaces: Workspaces,
        main_window: QWidget
    ):
        self.__opened_projects = {}
        self.__set_content_refresher = set_content_refresher_callback
        self.__flow_list = flow_list
        self.__workspaces = workspaces
        self.__main_window = main_window

        self.__workspaces.activated.connect(lambda editor: self.set_active_project(editor))

    def set_active_project(self, editor: Editor):
        for proj in self.__opened_projects.values():
            if proj.editor() is editor:
                proj.get_sm_controller().set_active()

    def open_synonyms_editor(self):
        synonyms: SynonymsGroupsModel = None

        editor: Editor = self.__workspaces.currentWidget()
        for proj in self.__opened_projects.values():
            if proj.editor() is editor:
                synonyms = proj.get_sm_controller().synonyms_groups()
                break

        if synonyms is None: raise RuntimeError(synonyms)

        s_editor = SynonymsEditor(
            synonyms,
            self.create_s_group,
            self.create_s_value,
            self.__main_window
        )
        s_editor.exec()
        debug = "just to set the break"

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
        
        c_ctrl = StateMachineQtController(p_ctrl, self.__flow_list, self.__main_window)
        p_ctrl.set_sm_ctrl(c_ctrl)

        self.__set_content_refresher(id, StateMachineGuiRefresher(c_ctrl))

        editor = p_ctrl.editor()
        self.__workspaces.open_editor(editor, p_ctrl.project_name())

    def saved(self, id:int, data):
        self.__opened_projects[id].saved()

    def updated(self, id:int, new_data):
        # TODO: отлов изменений для истории
        self.__opened_projects[id].update(new_data)

    def removed(self, id:int):
        self.__opened_projects[id].close()
        del self.__opened_projects[id]

    def create_s_group(self, model: SynonymsGroupsModel):
        name, ok = QInputDialog.getText(None, "Имя новой группы", "Имя новой группы:")
        if not ok: return

        descr, ok = QInputDialog.getText(None, "Описание новой группы", "Описание новой группы:")
        if not ok: return

        value, ok = QInputDialog.getText(None, "Значение первого синонима", "Первый синоним:")
        if not ok: return

        new_row:int = model.rowCount()
        model.insertRow(new_row)
        index = model.index(new_row)
        model.setData(index, name, CustomDataRole.Name)
        model.setData(index, descr, CustomDataRole.Description)
        model.setData(index, SynonymsSetModel([value]), CustomDataRole.SynonymsSet)

    def create_s_value(self, model: SynonymsSetModel):
        value, ok = QInputDialog.getText(None, "Новый синоним", "Текст синонима:")
        if not ok: return
        new_row:int = model.rowCount()
        model.insertRow(new_row)
        index = model.index(new_row)
        model.setData(index, value)