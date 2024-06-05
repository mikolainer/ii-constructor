from typing import Optional

from PySide6.QtCore import (
    QObject,
    Qt,
    QPoint,
    QPointF,
    QRect,
    Slot, Signal,
    QTimer
)

from PySide6.QtGui import (
    QEnterEvent,
    QMouseEvent,
    QFont,
    QTransform,
    QColor,
    QBrush,
    QPen,
)

from PySide6.QtWidgets import (
    QGraphicsSceneMouseEvent,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsProxyWidget,
    QGraphicsRectItem,
    QGraphicsPixmapItem,
)

from alicetool.presentation.api import EditorAPI
from alicetool.infrastructure.widgets import FlowListWidget

from ..infrastructure.scene import Arrow, AddConnectionBtn
from ..infrastructure.data import CustomDataRole, SynonymsSetModel, FlowsModel, SynonymsGroupsModel, ItemData
from ..infrastructure.views import FlowsView, SynonymsSelectorView
from ..infrastructure.widgets import FlowList

class QGraphicsStateItem(QGraphicsProxyWidget):
    ''' TODO: инкапсулировать в SceneNode '''
    __arrows: dict[str, list[Arrow]]
    __add_btns: list[AddConnectionBtn]

    def __init__(self, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.__arrows = {"from": list[Arrow](), "to": list[Arrow]()}
        self.setZValue(100)
        self.__add_btns = []
        #self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def show_add_btn(self):
        editor:Editor = self.scene()
        wgt: StateWidget = self.widget()

        for btn in self.__add_btns:
            if btn.is_active:
                return

        pos = wgt.add_btn_pos()
        add_btn = AddConnectionBtn(self)
        add_btn.setParentItem(self)
        add_btn.setPos(pos)
        self.__add_btns.append(add_btn)

        editor.addItem(add_btn)

    def remove_add_btn(self):
        self.__add_btn = None

    def arrow_connect_as_start(self, arrow: Arrow):
        if (not arrow in self.__arrows['from']):
            self.__arrows['from'].append(arrow)
            bounding = self.boundingRect()
            center = QPointF(bounding.width() / 2.0, bounding.height() / 2.0)
            arrow.set_start_point(self.scenePos() + center)

    def arrow_connect_as_end(self, arrow: Arrow):
        if (not arrow in self.__arrows['to']):
            self.__arrows['to'].append(arrow)
            bounding = self.boundingRect()
            center = QPointF(bounding.width() / 2.0, bounding.height() / 2.0)
            arrow.set_end_point(self.scenePos() + center)
            arrow.set_end_wgt(self)

    def arrow_disconnect(self, arrow: Arrow):
        if (arrow in self.__arrows['from']):
            self.__arrows['from'].remove(arrow)

        if (arrow in self.__arrows['to']):
            self.__arrows['to'].remove(arrow)
            
    def update_arrows(self):
        bounding = self.boundingRect()
        center = QPointF(bounding.width() / 2.0, bounding.height() / 2.0)

        for arrow in self.__arrows['to']:
            arrow.set_end_point(self.scenePos() + center)

        for arrow in self.__arrows['from']:
            arrow.set_start_point(self.scenePos() + center)

class StateWidget(QWidget):
    class CloseBtn(QPushButton):
        mouse_enter = Signal()

        def __init__(self, text:str, parent = None):
            super().__init__(text, parent)
            self.setMouseTracking(True)

        def enterEvent(self, event: QEnterEvent) -> None:
            if event.type() == QMouseEvent.Type.Enter:
                self.mouse_enter.emit()
            return super().enterEvent(event)
        
    TITLE_HEIGHT = 15
    START_WIDTH = 150

    __title: QLabel
    __close_btn: CloseBtn
    __content: QTextEdit
    __item_on_scene: QGraphicsStateItem | None
    
    def __init__(self, content: str, name: str, id :int, parent = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__item_on_scene = None
        self.__title = QLabel(name, self)
        font = self.__title.font()
        font.setWeight(QFont.Weight.ExtraBold)
        self.__title.setFont(font)
        self.__title.setFixedHeight(StateWidget.TITLE_HEIGHT)
        self.__close_btn = StateWidget.CloseBtn(str(id), self)
        self.__close_btn.setFlat(True)
        self.__close_btn.setStyleSheet(
            "QPushButton"
            "{"
            "   background-color: #666666;"
            "   border: 0px; color: #FFFFFF;"
            "   border-radius: 7px;"
            "}"
        )
        font = self.__close_btn.font()
        font.setWeight(QFont.Weight.ExtraBold)
        self.__close_btn.setFont(font)
        self.__close_btn.setFixedHeight(StateWidget.TITLE_HEIGHT)
        self.__close_btn.setFixedWidth(StateWidget.TITLE_HEIGHT)
        
        self.__content = QTextEdit(content, self)
        self.__content.setStyleSheet(
            "QTextEdit{"
            "   border: 0px;"
            "   border-top: 1px solid #59A5FF;"
            "   border-bottom-right-radius: 10px;"
            "   border-bottom-left-radius: 10px;"
            "   background-color: #FFFFFF;"
            "}"
        )

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        title = QWidget(self)
        title.setStyleSheet(
            "QWidget{"
            "   border: 0px;"
            "   border-top-right-radius: 10px;"
            "   border-top-left-radius: 10px;"
            "   background-color: #FFFFFF;"
            "}"
        )
        title_lay = QHBoxLayout(title)
        title_lay.setContentsMargins(5,2,2,2)

        title_lay.addWidget(self.__title)
        title_lay.addWidget(self.__close_btn)
        
        main_lay.addWidget(title)
        main_lay.addWidget(self.__content)

        self.resize(StateWidget.START_WIDTH, StateWidget.START_WIDTH)

    def add_btn_pos(self) -> QPoint:
        pos = self.__close_btn.pos()
        pos.setX(pos.x() + self.__close_btn.width() + 4)
        return pos
    
    def set_graphics_item_ptr(self, item: QGraphicsStateItem):
        self.__item_on_scene = item
        self.__close_btn.mouse_enter.connect(self.on_close_btn_mouse_enter)

    def state_id(self) -> int:
        return int(self.__close_btn.text())

    @Slot()
    def on_close_btn_mouse_enter(self):
        if not self.__item_on_scene is None:
            self.__item_on_scene.show_add_btn()

class ProxyWidgetControll(QGraphicsRectItem):
    ''' TODO: инкапсулировать в SceneNode '''
    def __init__(self, x: float, y: float, w: float, h: float, parent = None):
        super().__init__(x, y, w, h, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setPen(QPen(Qt.GlobalColor.transparent))
        self.setBrush(QBrush(Qt.GlobalColor.transparent))
        self.setZValue(100)
    
    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change in [
            QGraphicsItem.GraphicsItemChange.ItemPositionChange,
            QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged
        ] and len(self.childItems()):
            child:QGraphicsStateItem = self.childItems()[0]
            child.update_arrows()

        return super().itemChange(change, value)

class Editor(QGraphicsScene):
    ''' TODO
    убрать зависимость от StateMachineQtController (унестив main)
    ??? возможно нельзя потому что это используется для получения доступа к контроллеру проекта через сцену
    (нужна не только связь от контроллера к сцене чтобы её обновлять, но и от сцены к контроллеру чтобы сообщать об изменениях)
    !!! возможно надо связывать StateMachineQtController напрямую с элементами сцены через инверсию управления
    или сделать глобально доступную фабрику синглтонов для контроллеров проектов (??? тогда придётся хранить принадлежность к конкретному проекту)
    '''
    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent)
        self.setBackgroundBrush(QColor("#DDDDDD"))

    def addState(self, content:str, name:str, id:int, initPos:QPoint) -> QGraphicsStateItem:
        widget = StateWidget(content, name, id)
        proxy = self.__addStateProxyWidget(widget, initPos)
        widget.set_graphics_item_ptr(proxy)

        return proxy

    def __addStateProxyWidget(self, widget: StateWidget, initPos:QPoint) -> QGraphicsStateItem:
        close_btn_margins = 2 *2

        proxyControl = ProxyWidgetControll(
            initPos.x(), initPos.y(),
            widget.width() - StateWidget.TITLE_HEIGHT - close_btn_margins, 20
        )
        self.addItem(proxyControl)
        
        item = QGraphicsStateItem(proxyControl)
        item.setWidget(widget)
        item.setPos(initPos.x(), initPos.y())
        item.setParentItem(proxyControl)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, True)
        
        item.installSceneEventFilter(proxyControl)

        return item
    
class StateMachineQtController:
    ''' реализация "ProjectController" по uml2'''

    # constants
    __START_SIZE = QRect(0, 0, 2000, 2000)
    __START_SPACINS = 30

    # controlls
    __proj_ctrl: 'ProjectQtController'
    __flow_list: FlowList
    __main_window: QWidget
    __flows_wgt: FlowListWidget

    __selector: None | SynonymsSelectorView

    # scene
    __scene: Editor
    __states: dict[int, QGraphicsStateItem]
    __steps: dict[int, list[Arrow]]

    # models
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
        # получение точек входа
        flows_data = EditorAPI.instance().get_all_project_flows(self.__proj_ctrl.project_id())

        # получение существующих векторов
        synonyms_data = EditorAPI.instance().get_all_project_synonyms(self.__proj_ctrl.project_id())

        # получение существующих состояний
        states_data = EditorAPI.instance().get_all_project_states(self.__proj_ctrl.project_id())
        
        # формирование сцены
        # TODO: сделать модель состояний
        for state_id in states_data.keys():
            self.__states[state_id] = self.__scene.addState(
                states_data[state_id]['content'],
                states_data[state_id]['name'],
                state_id,
                QPoint(
                        StateWidget.START_WIDTH * (state_id - 1) +
                        StateMachineQtController.__START_SPACINS * (state_id),
                        StateMachineQtController.__START_SPACINS
                    )
            )

        flows = FlowsView(self.__main_window)
        # модель точек входа
        self.__f_model = FlowsModel(flows)
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

        flows.setModel(self.__f_model)

        self.__flows_wgt = FlowListWidget(flows)
        self.__flows_wgt.create_value.connect(self.__on_flow_add_pressed)

        # модель векторов
        self.__g_model = SynonymsGroupsModel(self.__main_window)
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
