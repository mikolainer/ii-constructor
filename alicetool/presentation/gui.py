from typing import Optional

from PySide6.QtCore import (
    QPoint,
    QRect,
    Slot,
)

from PySide6.QtWidgets import (
    QMessageBox,
    QWidget,
    QGraphicsView,
    QTextEdit
)
from .data import to_json_string
from ..infrastructure.qtgui.primitives.sceneitems import Arrow, SceneNode, NodeWidget
from ..infrastructure.qtgui.data import CustomDataRole, ItemData, SynonymsSetModel
from ..infrastructure.qtgui.flows import FlowsView, FlowListWidget, FlowsModel
from ..infrastructure.qtgui.synonyms import SynonymsSelectorView, SynonymsGroupsModel
from ..infrastructure.qtgui.states import Editor, StatesModel
from ..infrastructure.qtgui.main_w import FlowList

#from alicetool.presentation
from .api import EditorAPI

class StateMachineQtController:
    ''' реализация "ProjectController" по uml2'''

    # constants
    __START_SIZE = QRect(0, 0, 2000, 2000)

    # controlls
    __proj_ctrl: 'ProjectQtController'
    __flow_list: FlowList
    __main_window: QWidget
    __flows_wgt: FlowListWidget

    __selector: None | SynonymsSelectorView

    # scene
    __scene: Editor
    __steps: dict[int, list[Arrow]]

    # models
    __states: StatesModel
    __f_model: FlowsModel
    __g_model: SynonymsGroupsModel
    __s_models: dict[int, SynonymsSetModel]

    def synonyms_groups(self) -> SynonymsGroupsModel:
        return self.__g_model

    def project_controller(self) -> 'ProjectQtController':
        return self.__proj_ctrl
    
    def get_state(self, id:int):
        return self.__states[id]
    
    def __init__(self,
        proj_ctrl: 'ProjectQtController',
        flow_list: 'FlowList',
        main_window: QWidget
    ):
        self.__proj_ctrl = proj_ctrl
        self.__main_window = main_window

        self.__scene = Editor(self.__main_window)
        self.__selector = None
        
        self.__proj_ctrl.editor().setScene(self.__scene)

        self.__flow_list = flow_list
        self.__states = {}
        self.__steps = {}
        self.__s_models = {}
        
        self.__build_editor()
        self.__init_models()
        self.set_active()
    
    def add_step(self, from_state_id:int, to_state_id:int):
        self.__selector = SynonymsSelectorView(self.__main_window)
        self.__selector.setModel(self.__g_model)
        self.__selector.show()
        self.__selector.item_selected.connect(
            lambda g_id: EditorAPI.instance().add_step(
                self.project_controller().project_id(),
                from_state_id, to_state_id, g_id
            )
        )

    def step_added(self, from_state_id:int, to_state_id:int, synonyms_g:int):
        arrow = Arrow()
        self.__scene.addItem(arrow)
        self.__states[from_state_id].arrow_connect_as_start(arrow)
        self.__states[to_state_id].arrow_connect_as_end(arrow)

        if from_state_id in self.__steps.keys():
            self.__steps[from_state_id].append(arrow)
        else:
            self.__steps[from_state_id] = [arrow]

        self.__selector.accept()
        self.__selector = None

    def set_active(self):
        self.__flow_list.setWidget(self.__flows_wgt, True)

    def __build_editor(self):
        self.__scene.setSceneRect(StateMachineQtController.__START_SIZE)
        

    def __init_models(self):
        print("===== создание Qt моделей проекта =====")

        # получение точек входа
        flows_data = EditorAPI.instance().get_all_project_flows(self.__proj_ctrl.project_id())

        # получение существующих векторов
        synonyms_data = EditorAPI.instance().get_all_project_synonyms(self.__proj_ctrl.project_id())

        # получение существующих состояний
        states_data = EditorAPI.instance().get_all_project_states(self.__proj_ctrl.project_id())
        
        # формирование сцены
        self.__states = StatesModel()

        print("----- СОСТОЯНИЯ -----")
        for state_id in states_data.keys():
            item = ItemData()
            item.on[CustomDataRole.Id] = state_id
            item.on[CustomDataRole.Name] = states_data[state_id]['name']
            item.on[CustomDataRole.Text] = states_data[state_id]['content']
            self.__states.prepare_item(item)
            self.__states.insertRow()
            print(to_json_string(item))
            
        self.__scene.setModel(self.__states)

        flows = FlowsView(self.__main_window)
        # модель точек входа
        self.__f_model = FlowsModel(flows)

        print("----- ПОТОКИ -----")
        for id in flows_data.keys():
            gr_id = flows_data[id]['synonym_group_id']
            self.__s_models[gr_id] = SynonymsSetModel(self.__main_window)
            for value in synonyms_data[gr_id]['values']:
                item = ItemData()
                item.on[CustomDataRole.Text] = value
                self.__s_models[gr_id].prepare_item(item)
                self.__s_models[gr_id].insertRow()

            item = ItemData()
            item.on[CustomDataRole.Id] = id
            item.on[CustomDataRole.Name] = flows_data[id]['name']
            item.on[CustomDataRole.Description] = flows_data[id]['description']
            item.on[CustomDataRole.SynonymsSet] = self.__s_models[gr_id]
            item.on[CustomDataRole.EnterStateId] = flows_data[id]['enter_state_id']
            item.on[CustomDataRole.SliderVisability] = False
            self.__f_model.prepare_item(item)
            self.__f_model.insertRow()

            print(to_json_string(item))

        flows.setModel(self.__f_model)

        self.__flows_wgt = FlowListWidget(flows)
        self.__flows_wgt.create_value.connect(self.__on_flow_add_pressed)

        # модель векторов
        self.__g_model = SynonymsGroupsModel(self.__main_window)

        print("----- ГРУППЫ -----")
        for group_id in synonyms_data.keys():
            gr_id = int(group_id)
            if not gr_id in self.__s_models.keys():
                self.__s_models[gr_id] = SynonymsSetModel(self.__main_window)
                for value in synonyms_data[gr_id]['values']:
                    item = ItemData()
                    item.on[CustomDataRole.Text] = value
                    self.__s_models[gr_id].prepare_item(item)
                    self.__s_models[gr_id].insertRow()
            
            item = ItemData()
            item.on[CustomDataRole.Id] = synonyms_data[gr_id]['id']
            item.on[CustomDataRole.Name] = synonyms_data[gr_id]['name']
            item.on[CustomDataRole.Description] = synonyms_data[gr_id]['description']
            item.on[CustomDataRole.SynonymsSet] = self.__s_models[gr_id]
            self.__g_model.prepare_item(item)
            self.__g_model.insertRow()

            print(to_json_string(item))

    @Slot(str, str)
    def __on_flow_add_pressed(self, name:str, descr:str):
        QMessageBox.information(self.__main_window, "Ещё не реализовано", "Здесь будет выбор состояния и синонима")

class ProjectQtController:
    __proj_id : int
    __proj_name: str
    __editor: QGraphicsView
    __sm_ctrl: StateMachineQtController | None

    def project_id(self):
        return self.__proj_id
    
    def project_name(self):
        return self.__proj_name
    
    def editor(self) -> QGraphicsView:
        return self.__editor
    
    def get_sm_controller(self) -> StateMachineQtController | None:
        return self.__sm_ctrl

    def __init__(self, id: int, name:str):
        self.__proj_id = id
        self.__proj_name = name
        self.__editor = QGraphicsView()
        self.__editor.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.__sm_ctrl = None

    def set_sm_ctrl(self, ctrl: StateMachineQtController):
        self.__sm_ctrl = ctrl
    
    def update(self, new_data):
        ''' обработчик изменений '''

    def close(self):
        ''' закрыть проект '''

    def saved(self):
        ''' закрыть проект '''
