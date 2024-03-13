import sys
from math import sqrt, pi

from PySide6.QtCore import (
    Qt,
    QSize,
    QPoint,
    QPointF,
    QRectF,
    QRect,
    QStringListModel,
    Slot, Signal,
    QTimer
)

from PySide6.QtGui import (
    QCloseEvent,
    QEnterEvent,
    QHideEvent,
    QIcon,
    QMouseEvent,
    QPixmap,
    QResizeEvent,
    QShowEvent,
    QFont,
    QTransform,
    QColor,
    QBrush,
    QPen,
    QPainter
)

from PySide6.QtWidgets import (
    QLayoutItem,
    QGraphicsSceneMouseEvent,
    QMessageBox,
    QMainWindow,
    QWidget,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QSplitter,
    QPushButton,
    QSpacerItem,
    QDialog,
    QLineEdit,
    QTextEdit,
    QLabel,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QListView,
    QSpacerItem,
    QStyleOptionGraphicsItem,
    QGraphicsProxyWidget,
    QGraphicsRectItem,
    QGraphicsPixmapItem 
)

from alicetool.editor.services.api import EditorAPI
import alicetool.editor.resources.rc_icons

from .data import CustomDataRole, SynonymsSetModel, FlowsModel

class Arrow(QGraphicsItem):
    __start_point: QPointF
    __end_point: QPointF
    __pen_width: int
    __end_wgt: QGraphicsItem

    def set_end_wgt(self, widget: QGraphicsItem):
        ''' установка виджета для вычисления смещения указателя '''
        self.set_end_point(self.__arrow_ptr_pos())
        self.__end_wgt = widget

    def set_start_point(self, point: QPointF):
        self.prepareGeometryChange()
        self.__start_point = point
        self.setPos(self.__center())
    
    def set_end_point(self, point: QPointF):
        self.prepareGeometryChange()
        self.__end_point = point
        self.setPos(self.__center())

    def __init__(self, 
        start: QPointF = None,
        end: QPointF = None,
        parent: QGraphicsItem = None
    ):
        super().__init__(parent)

        self.__start_point = QPointF(0.0, 0.0)
        self.__end_point = QPointF(3.0, 3.0)
        self.__pen_width = 5
        self.__end_wgt = None
        
        if not start is None:
            self.__start_point = start
        if not end is None:
            self.__end_point = end

        self.setPos(self.__center())
        self.setZValue(90)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsToShape, True)

    def __dir_pointer_half(self) -> QPointF:
        ''' 
        вектор половинки указателя стрелки:
        x - отступ от линии,
        y - расстояние от указываемой точки вдоль линии
        '''
        return QPointF(
            self.__pen_width * 1.5,
            self.__pen_width * 3.0
        )
    
    def __arrow_directions(self) -> dict:
        '''
        направдения (tg углов от направления оси глобальных координат x):
        back - вектор направленный от указываемой точки к началу линии;
        left, right - от указываемой точки в направлении половинок указателя стрелки
        '''
        a = self.__end_point
        b = self.__start_point

        delta_x = a.x() - b.x()
        delta_y = a.y() - b.y()

        ab_ctg =    delta_x/delta_y if delta_y != 0 else 0
        ab_tg =     delta_y/delta_x if delta_x != 0 else 0
        
        cot: bool = abs(ab_ctg) < abs(ab_tg)
        
        h_ptr = self.__dir_pointer_half()
        delta_tg = h_ptr.x() / h_ptr.y()

        if delta_x == 0:
            mode = 'down' if delta_y > 0 else 'up'
        else:
            mode = 'ctg' if cot else 'tg'
        
        return {
            'mode' : mode,
            'back' : ab_ctg                 if cot else ab_tg,
            'left' : ab_ctg + delta_tg      if cot else ab_tg + delta_tg,
            'right': ab_ctg - delta_tg      if cot else ab_tg - delta_tg
        }
    
    def __delta(self) -> QPointF:
        '''
        длины проекций линии стрелки на оси глобальных координат
        '''
        x = ( max(self.__start_point.x(), self.__end_point.x())
            - min(self.__start_point.x(), self.__end_point.x()) )

        y = ( max(self.__start_point.y(), self.__end_point.y())
            - min(self.__start_point.y(), self.__end_point.y()) )

        return QPointF(x, y)
    
    def __center(self) -> QPointF:
        '''
        вычисление центра в глобальных координатах
        из начальной и конечной точек
        '''
        x = max(self.__start_point.x(), self.__end_point.x())
        y = max(self.__start_point.y(), self.__end_point.y())

        return QPointF(x, y) - self.__delta() / 2.0

    def boundingRect(self) -> QRectF:
        '''
        область границ объекта в локальных координатах
        '''
        pen_padding = QPointF(
            float(self.__pen_width),
            float(self.__pen_width)
        )
        arrow_pointer_padding = QPointF(
            self.__dir_pointer_half().x(),
            self.__dir_pointer_half().x()
        )
        size = self.__delta() + pen_padding*2 + arrow_pointer_padding*2

        x = 0 - size.x() / 2.0
        y = 0 - size.y() / 2.0

        return QRectF(x, y, size.x(), size.y())
    
    def __line_len(self) -> float:
        delt = self.__delta()
        return sqrt(delt.x()**2 + delt.y()**2)
    
    def __arrow_ptr_pos(self) -> QPointF:
        if self.__end_wgt is None:
            return (self.__end_point)
        
        bounding = self.__end_wgt.boundingRect()
        wgt_half_size = QPointF(bounding.width(), bounding.height()) / 2.0
        wgt_center = self.__end_wgt.scenePos() + wgt_half_size

        hw_cos: float = bounding.width() / sqrt(bounding.width()**2.0 + bounding.height()**2.0)
        if self.__line_len() == 0:
            sin = 1
            cos = 0
        else:
            cos: float = self.__delta().x() / self.__line_len()
            sin: float = self.__delta().y() / self.__line_len()

        if hw_cos < cos:
            ''' решение на вертикальных гранях '''
            if cos == 0:
                y = 0

            if self.__start_point.x() < self.__end_point.x():
                ''' решение на левой грани '''
                x = bounding.height() / 2.0
                if self.__start_point.y() > self.__end_point.y():
                    ''' нижняя часть '''
                    y = (bounding.width() * self.__delta().y()) / (self.__line_len() * 2 * (0 - cos))
                else:
                    ''' верхняя часть '''
                    y = (bounding.width() * self.__delta().y()) / (self.__line_len() * 2 * cos)
            else:
                ''' решение на правой грани '''
                x = -(bounding.height() / 2.0)
                if self.__start_point.y() > self.__end_point.y():
                    ''' нижняя часть '''
                    y = (bounding.width() * self.__delta().y()) / (self.__line_len() * 2 * (0 - cos))
                else:
                    ''' верхняя часть '''
                    y = (bounding.width() * self.__delta().y()) / (self.__line_len() * 2 * cos)

        else:
            ''' решение на горизонтальных гранях '''
            if sin == 0:
                x = 0
            #else:
            #    x = (bounding.height() * self.__delta().x()) / (self.__line_len() * 2 * sin)
            
            if self.__start_point.y() > self.__end_point.y():
                ''' решение на нижней грани '''
                y = -(bounding.height() / 2.0)
                if self.__start_point.x() > self.__end_point.x():
                    ''' правая часть '''
                    x = (bounding.height() * self.__delta().x()) / (self.__line_len() * 2 * (0-sin))
                else:
                    ''' левая часть '''
                    x = (bounding.height() * self.__delta().x()) / (self.__line_len() * 2 * sin)
            else:
                ''' решение на верхней грани '''
                y = bounding.height() / 2.0
                if self.__start_point.x() > self.__end_point.x():
                    ''' правая часть '''
                    x = (bounding.height() * self.__delta().x()) / (self.__line_len() * 2 * (0-sin))
                else:
                    ''' левая часть '''
                    x = (bounding.height() * self.__delta().x()) / (self.__line_len() * 2 * sin)

        return QPointF(
            wgt_center.x() - x,
            wgt_center.y() - y
        )

    def paint( self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget = None
    ):
        pen = QPen(QColor('black'))
        pen.setWidth(self.__pen_width)
        painter.setPen(pen)

        #painter.drawRect(self.boundingRect())   # for debug
        #painter.drawPoint(QPoint(0,0))          # for debug

        k = self.__arrow_directions() # в уравнении прямой 'y=kx' k = tg угла наклона
        
        h_ptr = self.__dir_pointer_half() # локальный алиас для короткого обращения к значению
        r = sqrt(h_ptr.x()**2.0 + h_ptr.y()**2.0) # длина половинки указателя стрелки (гепотинуза)

        arrow_pos = self.mapFromScene(self.__arrow_ptr_pos())

        ### решения систем уравнений прямой, проходящей через центр координат и окружности в центре координат для обеих половинок указателя стрелки
        if k['mode'] == 'up':
            pointer_left_end = QPointF(arrow_pos.x() + self.__dir_pointer_half().x(), arrow_pos.y() + self.__dir_pointer_half().y())
            pointer_right_end = QPointF(arrow_pos.x() - self.__dir_pointer_half().x(), arrow_pos.y() + self.__dir_pointer_half().y())
        elif k['mode'] == 'down':
            pointer_left_end = QPointF(arrow_pos.x() + self.__dir_pointer_half().x(), arrow_pos.y() - self.__dir_pointer_half().y())
            pointer_right_end = QPointF(arrow_pos.x() - self.__dir_pointer_half().x(), arrow_pos.y() - self.__dir_pointer_half().y())

        elif k['mode'] == 'ctg':
            y_left = sqrt(r**2.0 / (k['left']**2.0 + 1.0))
            pointer_left_end = QPointF(k['left'] * y_left, y_left)
            
            y_right = sqrt(r**2.0 / (k['right']**2.0 + 1.0))
            pointer_right_end = QPointF(k['right'] * y_right, y_right)
        else: #if k['mode'] == 'tg'
            x_left = sqrt(r**2.0 / (k['left']**2.0 + 1.0))
            pointer_left_end = QPointF(x_left, k['left'] * x_left)
            
            x_right = sqrt(r**2.0 / (k['right']**2.0 + 1.0))
            pointer_right_end = QPointF(x_right, k['right'] * x_right)

        # выбор одного из двух возможных решений сиснетмы уравнений
        if k['mode'] == 'ctg':
            if self.__start_point.y() > self.__end_point.y():
                painter.drawLine(arrow_pos, arrow_pos + pointer_left_end)
                painter.drawLine(arrow_pos, arrow_pos + pointer_right_end)
            else:
                painter.drawLine(arrow_pos, arrow_pos - pointer_left_end)
                painter.drawLine(arrow_pos, arrow_pos - pointer_right_end)

        else:
            if self.__start_point.x() > self.__end_point.x():
                painter.drawLine(arrow_pos, arrow_pos + pointer_left_end)
                painter.drawLine(arrow_pos, arrow_pos + pointer_right_end)
            else:
                painter.drawLine(arrow_pos, arrow_pos - pointer_left_end)
                painter.drawLine(arrow_pos, arrow_pos - pointer_right_end)

        
        end_point = self.__end_point
        if not self.__end_wgt is None:
            bounding = self.__end_wgt.boundingRect()
            wgt_half_size = QPointF(bounding.width(), bounding.height()) / 2.0
            end_point = self.__end_wgt.scenePos() + wgt_half_size

        painter.drawLine(
            self.mapFromScene(self.__start_point),
            self.mapFromScene(end_point)
        )

class QGraphicsStateItem(QGraphicsProxyWidget):
    __arrows: dict[str, list[Arrow]]
    __add_btn: 'StateWidget.AddConnectionBtn'

    def __init__(self, parent: QGraphicsItem = None):
        super().__init__(parent)
        self.__arrows = {"from": list[Arrow](), "to": list[Arrow]()}
        self.setZValue(100)
        self.__add_btn = None
        #self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def show_add_btn(self):
        editor:Editor = self.scene()
        wgt: StateWidget = self.widget()

        if not self.__add_btn is None:
            return

        self.__add_btn = StateWidget.AddConnectionBtn(wgt.state_id())
        self.__add_btn.setParentItem(self)
        self.__add_btn.setPos(wgt.add_btn_pos())
        editor.addItem(self.__add_btn)

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
    class AddConnectionBtn(QGraphicsPixmapItem):
        __arrow: Arrow | None
        __state_id: int

        def __init__(self, state_id: int):
            self.__state_id = state_id

            pixmap = QMessageBox.standardIcon(QMessageBox.Icon.Information)
            super().__init__(pixmap.scaled(20,20))
            
            self.setZValue(110)
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
        def __remove(self, mouse_pos:QPointF):
            self.__arrow.set_end_wgt(None)
            scene: Editor = self.scene()
            sm_ctrl: StateMachineQtController = scene.controller()

            scene.removeItem(self.__arrow)
            self.__arrow = None
            
            state_id = self.__state_id
            scene.removeItem(self)
            sm_ctrl.get_state(state_id).remove_add_btn()

            end_item:QGraphicsStateItem = scene.itemAt(mouse_pos, QTransform())
            if isinstance(end_item, QGraphicsStateItem):
                end_wgt: StateWidget = end_item.widget()
                sm_ctrl.add_step(state_id, end_wgt.state_id())
        
        def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
            center = QPointF( 10, 10 )
            self.__arrow.set_end_point(self.scenePos() + center)
            return super().mouseMoveEvent(event)
        
        def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
            scene: Editor = self.scene()
            self.__arrow = Arrow()
            scene.controller().get_state(self.__state_id).arrow_connect_as_start(self.__arrow)
            self.__arrow.set_end_wgt(self)
            scene.addItem(self.__arrow)

            return super().mousePressEvent(event)
        
        def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
            scene_pos = event.scenePos()
            QTimer.singleShot(0, lambda: self.__remove(scene_pos)) # нельзя обновлять сцену до возвращения в цикл событий Qt
            return super().mouseReleaseEvent(event)

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

class FlowWidget(QWidget):
    __title: QLabel
    __description: QLabel
    __synonyms_name: QLabel
    __synonyms_list: QListView
    __slider_btn: QPushButton

    @Slot()
    def __on_slider_click(self):
        self.__slider_btn.setText("^" if self.__slider_btn.isChecked() else "v")
        self.__synonyms_list.setVisible(self.__slider_btn.isChecked())

    def __init__(self, id :int, 
                 name: str, description :str,
                 synonym_values: list, 
                 start_state :QGraphicsProxyWidget,
                 parent = None
                ):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid black; background-color: #DDDDDD;")

        self.__title = QLabel(name, self)
        self.__title.setWordWrap(True)
        self.__description = QLabel(description, self)
        self.__description.setWordWrap(True)
        self.__synonyms_name = QLabel("синонимы", self)
        self.__synonyms_list = QListView(self)
        self.__synonyms_list.hide()

        test_data: dict[int, FlowsModel.Item] = {}
        for i in range(len(synonym_values)):
            item = FlowsModel.Item()
            item.on[CustomDataRole.Text] = synonym_values[i]
            test_data[i*2] = item

        self.__synonyms_list.setModel(
            #SynonymsSetModel(synonym_values, self.__synonyms_list)
            FlowsModel(test_data, self.__synonyms_list)
        )
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        synonyms_wrapper = QWidget(self)
        synonyms_lay = QVBoxLayout(synonyms_wrapper)

        synonyms_title_lay = QHBoxLayout()
        synonyms_title_lay.addWidget(self.__synonyms_name)
        self.__slider_btn = QPushButton('v', self)
        self.__slider_btn.setCheckable(True)
        self.__slider_btn.clicked.connect(
            lambda: self.__on_slider_click()
        )
        synonyms_title_lay.addWidget(self.__slider_btn)

        synonyms_lay.addLayout(synonyms_title_lay)
        synonyms_lay.addWidget(self.__synonyms_list)

        main_lay.addWidget(self.__title)
        main_lay.addWidget(self.__description)
        main_lay.addWidget(synonyms_wrapper)

class ProxyWidgetControll(QGraphicsRectItem):
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
    __state_machine_ctrl: 'StateMachineQtController'

    def controller(self) -> 'StateMachineQtController':
        return self.__state_machine_ctrl
    
    def __init__(self, controller: 'StateMachineQtController'):
        super().__init__()
        self.setBackgroundBrush(QColor("#DDDDDD"))

        self.__state_machine_ctrl = controller

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
    __START_SIZE = QRect(0, 0, 2000, 2000)
    __START_SPACINS = 30

    __scene: Editor

    __proj_ctrl: 'ProjectQtController'
    __flow_list: 'FlowList'
    __synonyms_editor: 'SynonymsEditor'

    __states: dict[int, QGraphicsStateItem]
    __steps: dict[int, list[Arrow]]
    __flows: dict[int, FlowWidget]
    __synonym_groups: dict[int, 'SynonymsGroupWidget']
    __synonyms: dict[int, list['SynonymWidget']]

    __current_synonyms_group: int | None

    def project_controller(self) -> 'ProjectQtController':
        return self.__proj_ctrl
    
    def get_state(self, id:int):
        return self.__states[id]
    
    def __init__(self,
        proj_ctrl: 'ProjectQtController',
        flow_list: 'FlowList',
        synonyms_list: 'SynonymsEditor',
    ):
        self.__scene = Editor(self)

        self.__proj_ctrl = proj_ctrl
        self.__proj_ctrl.editor().setScene(self.__scene)

        self.__flow_list = flow_list
        self.__synonyms_editor = synonyms_list
        self.__states = {}
        self.__steps = {}
        self.__flows = {}
        self.__synonyms = {}
        self.__synonym_groups = {}
        self.__current_synonyms_group = None
        
        self.__build_editor()
        self.__build_flows()
        self.__build_synonyms()

        self.set_active()
    
    def add_step(self, from_state_id:int, to_state_id:int):
        arrow = Arrow()
        self.__scene.addItem(arrow)
        self.__states[from_state_id].arrow_connect_as_start(arrow)
        self.__states[to_state_id].arrow_connect_as_end(arrow)

        if from_state_id in self.__steps.keys():
            self.__steps[from_state_id].append(arrow)
        else:
            self.__steps[from_state_id] = [arrow]

    def set_active(self):
        self.__group_changed(self.__current_synonyms_group)
        self.__synonyms_editor.set_groups(list(self.__synonym_groups.values()))

    def __build_editor(self):
        self.__scene.setSceneRect(StateMachineQtController.__START_SIZE)
        data = EditorAPI.instance().get_all_project_states(self.__proj_ctrl.project_id())
        
        for state_id in data.keys():
            self.__states[state_id] = self.__scene.addState(
                data[state_id]['content'],
                data[state_id]['name'],
                state_id,
                QPoint(
                        StateWidget.START_WIDTH * (state_id - 1) +
                        StateMachineQtController.__START_SPACINS * (state_id),
                        StateMachineQtController.__START_SPACINS
                    )
            )

    def __build_flows(self):
        data = EditorAPI.instance().get_all_project_flows(self.__proj_ctrl.project_id())

        for id in data.keys():
            self.__flows[id] = FlowWidget(
                id,
                data[id]['name'],
                data[id]['description'],
                data[id]['values'],
                self.__states[data[id]['enter_state_id']],
                self.__flow_list
            )

        self.__flow_list.setList(self.__flows)

    def __build_synonyms(self):
        data = EditorAPI.instance().get_all_project_synonyms(self.__proj_ctrl.project_id())

        for group_id in data.keys():
            self.__synonym_groups[int(group_id)] = SynonymsGroupWidget(data[group_id]['name'], data[group_id]['id'])
            self.__synonyms[int(group_id)] = []

            for val in data[group_id]['values']:
                self.__synonyms[int(group_id)].append(SynonymWidget(val))

        self.__current_synonyms_group = 1
        self.__synonym_groups[self.__current_synonyms_group].set_selected()
        self.__synonyms_editor.group_selected.connect(lambda id, _from: self.__group_changed(id, _from))

    @Slot(int)
    def __group_changed(self, id:int, _from:'SynonymsGroupWidget' = None):
        if (not _from is None) and (not _from in self.__synonym_groups):
            return
        
        self.__current_synonyms_group = id
        self.__synonyms_editor.set_synonyms(self.__synonyms[id], True)

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

class FlowList(QWidget):
    __area: QScrollArea

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__area = QScrollArea(self)
        self.__area.setWidgetResizable(True)
        self.__area.setStyleSheet("background-color: #74869C;")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0,0,0,0)
        lay.addWidget(self.__area)
    
    def setList(self, items :dict[int, FlowWidget]):
        wrapper = QWidget(self)

        lay = QVBoxLayout(wrapper)

        for wgt_id in items.keys():
            lay.addWidget(items[wgt_id])

        self.__area.setWidget(wrapper)

        lay.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))

class SynonymWidget(QWidget):
    __edit: QLineEdit

    def __init__(self, value:str, parent: QWidget = None):
        super().__init__(parent)
        self.__edit = QLineEdit(value, self)
        self.__edit.setStyleSheet('QLineEdit{background-color: #FFFFFF; border: 2px solid black; border-radius: 5px;}')
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self.__edit)

class SynonymsList(QStackedWidget):
    __indexed: dict[int, list[SynonymWidget]]

    def addWidget(self, w: QWidget = None) -> int:
        area = QScrollArea(self)
        area.setWidgetResizable(True)
        area.setStyleSheet('QScrollArea{background-color: #FFFFFF; border: none;}')

        wrapper = QWidget(self)
        QVBoxLayout(wrapper)

        area.setWidget(wrapper)
        return super().addWidget(area)
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__indexed = {}
    
    def setList(self, items :list[SynonymWidget], set_current: bool = False):
        ''' обновление списка виджетов '''
        # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not items in self.__indexed.items():
            self.__indexed[self.addWidget()] = items

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(items)]
        
        # добавляем новые виджеты (уже существующие не вставятся снова)
        lay = self.widget(idx).widget().layout()
        for wgt in items:
            lay.addWidget(wgt)
        
        # удаляем виджеты не элементов
        to_remove = []
        for item_idx in range(lay.count()):
            item:QLayoutItem = lay.itemAt(item_idx)
            if not isinstance(item.widget(), SynonymWidget):
                to_remove.append(item)

        for item in to_remove:
            if not item is None:
                lay.removeItem(item)

        # добавляем заполнитель пустоты в конце
        lay.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))

        # если указано - устанавливаем текущим виджетом
        if set_current:
            self.setCurrentIndex(idx)
        
class SynonymsGroupWidget(QWidget):
    __id: int
    __title: QLabel

    def id(self):
        return self.__id

    clicked = Signal()

    def __init__(self, name:str, id:int, parent: QWidget = None):
        super().__init__(parent)
        self.__id = id
        self.setStyleSheet('QWidget{background-color: #FFFFFF; border: 2px solid #FFFFFF;}')
        self.__title = QLabel(name, self)
        self.__title.setMinimumHeight(30)
        font = self.__title.font()
        font.setBold(True)
        self.__title.setFont(font)
        main_lay = QVBoxLayout(self)
        main_lay.addWidget(self.__title)
        main_lay.setContentsMargins(5,0,5,0)
    
    def set_selected(self, selected: bool = True):
        self.setStyleSheet(
            'QWidget{background-color: #FFFFFF; border: 2px solid #59A5FF;}'
            if selected else
            'QWidget{background-color: #FFFFFF; border: 2px solid #FFFFFF;}'
        )

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit()
        event.accept()
        #return super().mouseReleaseEvent(event)

class SynonymsGroupsList(QStackedWidget):
    __indexed: dict[int, list[SynonymsGroupWidget]]

    def addWidget(self, w: QWidget = None) -> int:
        wrapper = QWidget(self)
        wrapper.setStyleSheet('QWidget{background-color: #666666;}')
        lay = QVBoxLayout(wrapper)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(3)


        area = QScrollArea(self)
        area.setContentsMargins(0,0,0,0)
        area.setWidgetResizable(True)
        area.setStyleSheet('QScrollArea{background-color: #666666; border: none;}')
        area.setWidget(wrapper)

        return super().addWidget(area)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__indexed = {}
        self.resize(250, self.height())
    
    def setList(self, items :list[SynonymsGroupWidget]):
         # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not items in self.__indexed.items():
            self.__indexed[self.addWidget()] = items

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(items)]
        
        # добавляем новые виджеты (уже существующие не вставятся снова)
        lay:QVBoxLayout = self.widget(idx).widget().layout()
        for wgt in items:
            prev_c = lay.count()
            lay.addWidget(wgt)
            # соединим новый виджет с сигналом выбора
            if lay.count() != prev_c:
                wgt.clicked.connect(self.__group_selected)
                
        
        # удаляем виджеты не элементов
        to_remove = []
        for item_idx in range(lay.count()):
            item:QLayoutItem = lay.itemAt(item_idx)
            if not isinstance(item.widget(), SynonymsGroupWidget):
                to_remove.append(item)

        for item in to_remove:
            if not item is None:
                lay.removeItem(item)

        # добавляем заполнитель пустоты в конце
        lay.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))

        self.setCurrentIndex(idx)

    group_selected = Signal(int, SynonymsGroupWidget)

    @Slot()
    def __group_selected(self):
        selected:SynonymsGroupWidget = self.sender()
        self.group_selected.emit(selected.id(), selected)

        lay = self.currentWidget().widget().layout()
        for i in range(lay.count()):
            item = lay.itemAt(i).widget()
            if isinstance(item, SynonymsGroupWidget):
                item.set_selected(item is selected)

class SynonymsEditor(QWidget):
    __oldPos: QPoint | None
    __tool_bar: QWidget
    __exit_btn: QPushButton

    __group_list: SynonymsGroupsList
    __synonyms_list: SynonymsList

    group_selected = Signal(int, SynonymsGroupWidget)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle('Редактор синонимов')
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)
        
        splitter = QSplitter(
            self,
            Qt.Orientation.Horizontal
        )

        self.__oldPos = None
        self.__tool_bar = QWidget(self)
        self.__tool_bar.setMinimumHeight(24)
        main_lay.addWidget(self.__tool_bar, 0)
        self.__tool_bar.setStyleSheet('background-color : #666;')

        tool_bar_layout = QHBoxLayout(self.__tool_bar)
        tool_bar_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        tool_bar_layout.setSpacing(10)
        tool_bar_layout.setContentsMargins(2, 2, 2, 2)

        layout: QHBoxLayout = self.__tool_bar.layout()

        tool_bar_layout.addSpacerItem(
            QSpacerItem(
                0,0,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            )
        )

        size = QSize(20,20)
        self.__exit_btn: QPushButton = QPushButton(self)
        self.__exit_btn.clicked.connect(lambda: self.close())
        self.__exit_btn.setToolTip('Закрыть')
        self.__exit_btn.setStatusTip('Закрыть редактор синонимов')
        self.__exit_btn.setWhatsThis('Закрыть редактор синонимов')
        self.__exit_btn.setFixedSize(size)
        self.__exit_btn.setIcon(QIcon(QPixmap(":/icons/exit_norm.svg").scaled(10, 10)))
        self.__exit_btn.setIconSize(size)
        self.__exit_btn.setStyleSheet("background-color: #FF3131; border: 0px; border-radius: 10px")
        layout.addWidget(self.__exit_btn)

        self.__group_list = SynonymsGroupsList(self)
        self.__group_list.group_selected.connect(lambda id, _from: self.group_selected.emit(id, _from))
        splitter.addWidget(self.__group_list)

        self.__synonyms_list = SynonymsList(self)
        splitter.addWidget(self.__synonyms_list)
        
        splitter.setStretchFactor(0,0)
        splitter.setStretchFactor(1,1)
        
        main_lay.addWidget(splitter, 1)
        self.resize(600, 500)
        
    def set_synonyms(self, _list, set_current:bool = False):
        self.__synonyms_list.setList(_list, set_current)

    def set_groups(self, _list):
        self.__group_list.setList(_list)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.__oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.__oldPos is not None:
            delta = event.globalPos() - self.__oldPos
            self.move(self.pos() + delta)
            self.__oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.__oldPos = None

    def closeEvent(self, event: QCloseEvent) -> None:
        # это окно создаётся при старте и живёт до закрытия программы
        self.hide()
        event.ignore()

    def showEvent(self, event: QShowEvent) -> None:
        # пока окно открыто пользователь не должен ничего тыкать в остальной программе
        self.setWindowModality(Qt.WindowModality.WindowModal)
        return super().showEvent(event)
    
    def hideEvent(self, event: QHideEvent) -> None:
        # при сокрытии этого окна остальная программа должна получать все события
        self.setWindowModality(Qt.WindowModality.NonModal)
        return super().hideEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        # костыль
        if event.oldSize() != event.size():
            self.resize(event.size())

        return super().resizeEvent(event)

class NewProjectDialog(QDialog):
    proj_id: int
    __file_path_editor : QLineEdit
    __name_editor : QLineEdit
    __db_name_editor : QLineEdit
    __hello_editor : QTextEdit
    __help_editor : QTextEdit
    __info_editor : QTextEdit
    __ok_button : QPushButton

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.proj_id = -1

        lay = QVBoxLayout(self)

        self.__file_path_editor = QLineEdit(self)
        self.__name_editor = QLineEdit(self)
        self.__db_name_editor = QLineEdit(self)
        self.__hello_editor = QTextEdit(self)
        self.__help_editor = QTextEdit(self)
        self.__info_editor = QTextEdit(self)
        self.__ok_button = QPushButton("Начать", self)

        lay.addWidget(QLabel('Путь к файлу'))
        lay.addWidget(self.__file_path_editor)
        lay.addWidget(QLabel('Имя проекта для БД'))
        lay.addWidget(self.__db_name_editor)
        lay.addWidget(QLabel('Имя проекта для отображения'))
        lay.addWidget(self.__name_editor)
        lay.addWidget(QLabel('Текст приветственной фразы'))
        lay.addWidget(self.__hello_editor)
        lay.addWidget(QLabel('Текст ответа "Помощь"'))
        lay.addWidget(self.__help_editor)
        lay.addWidget(QLabel('Текст ответа "Что ты умеешь?"'))
        lay.addWidget(self.__info_editor)
        lay.addWidget(self.__ok_button)

        self.__ok_button.clicked.connect(self.__new_project)
    
    def __new_project(self):
        self.proj_id = EditorAPI.instance().create_project(
            self.get_result()
        )
        self.close()

    def get_result(self):
        return (
            f'name={self.__name_editor.text()}; '
            f'db_name={self.__db_name_editor.text()}; '
            f'file_path={self.__file_path_editor.text()}; '
            f'hello={self.__hello_editor.toPlainText()[: EditorAPI.instance().STATE_TEXT_MAX_LEN]}; '
            f'help={self.__help_editor.toPlainText()[: EditorAPI.instance().STATE_TEXT_MAX_LEN]}; '
            f'info={self.__info_editor.toPlainText()[: EditorAPI.instance().STATE_TEXT_MAX_LEN]}'
        )

class Workspaces(QTabWidget):
    __map = dict[int, QGraphicsView] # key = id

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__map = {}
        self.currentChanged.connect(lambda index: self.__activated(self.widget(index)))

    def set_active(self, project_id: int):
        self.setCurrentWidget(self.__map[project_id])

    def add_editor(self, view:QGraphicsView):
        editor:Editor = view.scene()
        p_ctrl = editor.controller().project_controller()
        self.__map[p_ctrl.project_id()] = view
        self.addTab(view, p_ctrl.project_name())

    def remove_editor(self, view:QGraphicsView):
        editor:Editor = view.scene()
        del self.__map[editor.controller().project_controller().project_id()]
        self.removeTab(self.indexOf())

    def __activated(self, view:QGraphicsView):
        editor:Editor = view.scene()
        editor.controller().set_active()

class MainWindow(QMainWindow):
    __oldPos: QPoint | None
    __flow_list: FlowList
    __workspaces: Workspaces
    __synonyms_editor: SynonymsEditor
    __tool_bar: QWidget
    __buttons: dict[str, QPushButton]

    def __init__(self, flow_list: FlowList, workspaces: Workspaces, synonyms: SynonymsEditor, parent: QWidget = None):
        super().__init__(None, Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("MainWindow{background-color: #74869C;}")

        self.__oldPos = None
        self.__flow_list = flow_list
        self.__workspaces = workspaces
        self.__synonyms_editor = synonyms

        self.__flow_list.setParent(self)
        self.__workspaces.setParent(self)
        self.__synonyms_editor.setParent(self)
        self.__synonyms_editor.setWindowFlag(Qt.WindowType.Window, True)

        self.__setup_ui()
        self.__setup_toolbar()

        self.show()

    def __setup_ui(self):
        self.setCentralWidget(QWidget(self))

        main_lay = QVBoxLayout(self.centralWidget())
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        self.__tool_bar = QWidget(self)
        self.__tool_bar.setMinimumHeight(64)
        main_lay.addWidget(self.__tool_bar, 0)
        self.__tool_bar.setStyleSheet('background-color : #666;')

        tool_bar_layout = QHBoxLayout(self.__tool_bar)
        tool_bar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        tool_bar_layout.setSpacing(10)
        tool_bar_layout.setContentsMargins(5, 3, 3, 5)
        
        main_splitter = QSplitter(
            self,
            Qt.Orientation.Horizontal
        )
        main_splitter.addWidget(self.__flow_list)
        main_splitter.addWidget(self.__workspaces)
        main_splitter.setStretchFactor(0,0)
        main_splitter.setStretchFactor(1,1)
        
        main_lay.addWidget(main_splitter, 1)

        self.setGeometry(0, 0, 900, 700)

    def __setup_toolbar(self):
        self.__buttons = {
            'new' : QPushButton(self),
            'open' : QPushButton(self),
            'save' : QPushButton(self),
            'publish' : QPushButton(self),
            'synonyms' : QPushButton(self),
            'exit' : QPushButton(self),
        }

        layout: QHBoxLayout = self.__tool_bar.layout()

        for key in self.__buttons.keys():
            btn: QPushButton = self.__buttons[key]
            
            style = "background-color: #59A5FF; border-radius:32px;"
            size = QSize(64,64)

            if key == 'new':
                tool_tip = 'Новый проект'
                status_tip = 'Создать новый проект'
                whats_this = 'Кнопка создания нового проекта'
                icon = QIcon(QPixmap(":/icons/new_proj_norm.svg"))
                btn.clicked.connect(lambda: self.__make_project())

            if key == 'open':
                tool_tip = 'Открыть проект'
                status_tip = 'Открыть файл проекта'
                whats_this = 'Кнопка открытия проекта из файла'
                icon = QIcon(QPixmap(":/icons/open_proj_norm.svg"))

            if key == 'save':
                tool_tip = 'Сохранить проект'
                status_tip = 'Сохранить в файл'
                whats_this = 'Кнопка сохранения проекта в файл'
                icon = QIcon(QPixmap(":/icons/save_proj_norm.svg"))

            if key == 'publish':
                tool_tip = 'Опубликовать проект'
                status_tip = 'Разместить проект в БД '
                whats_this = 'Кнопка экспорта проекта в базу данных'
                icon = QIcon(QPixmap(":/icons/export_proj_norm.svg"))

            if key == 'synonyms':
                tool_tip = 'Список синонимов'
                status_tip = 'Открыть редактор синонимов'
                whats_this = 'Кнопка открытия редактора синонимов'
                icon = QIcon(QPixmap(":/icons/synonyms_list_norm.svg"))
                btn.clicked.connect(lambda: self.__synonyms_editor.show())

            if key == 'exit':
                layout.addSpacerItem(
                    QSpacerItem(
                        0,0,
                        QSizePolicy.Policy.Expanding,
                        QSizePolicy.Policy.Minimum
                    )
                )
                tool_tip = 'Выйти'
                status_tip = 'Закрыть программу'
                whats_this = 'Кнопка завершения программы'
                style = "background-color: #FF3131; border: none;"
                icon = QIcon(QPixmap(":/icons/exit_norm.svg"))

                btn.clicked.connect(lambda: self.close())

            btn.setToolTip(tool_tip)
            btn.setStatusTip(status_tip)
            btn.setWhatsThis(whats_this)
            btn.setFixedSize(size)
            btn.setIcon(icon)
            btn.setIconSize(size)
            btn.setStyleSheet(style)
            layout.addWidget(btn)

    def __make_project(self):
        dialog = NewProjectDialog(self)
        dialog.exec()     

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.__oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.__oldPos is not None:
            delta = event.globalPos() - self.__oldPos
            self.move(self.pos() + delta)
            self.__oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.__oldPos = None
