import sys
from math import sqrt, pi

from PySide6.QtCore import (
    QEvent,
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
    QValidator,
    QFont,
    QCursor,
    QTransform,
    QColor,
    QPalette,
    QBrush,
    QPen,
    QPainter
)

from PySide6.QtWidgets import (
    QGraphicsSceneDragDropEvent,
    QGraphicsSceneMouseEvent,
    QMessageBox,
    QMainWindow,
    QWidget,
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
    QGraphicsWidget,
    QGraphicsItem,
    QListView,
    QSpacerItem,
    QGraphicsLineItem,
    QStyleOptionGraphicsItem,
    QGraphicsProxyWidget,
    QGraphicsRectItem,
    QGraphicsPixmapItem 
)

from alicetool.editor.services.api import EditorAPI
import alicetool.editor.resources.rc_icons

class Arrow(QGraphicsItem):
    __start_point: QPointF = QPointF(0.0, 0.0)
    __end_point: QPointF = QPointF(3.0, 3.0)
    __pen_width = 5
    __end_wgt: QGraphicsItem = None

    def __init__(self, 
        start: QPointF = None,
        end: QPointF = None,
        parent: QGraphicsItem = None
    ):
        super().__init__(parent)
        
        if not start is None:
            self.__start_point = start
        if not end is None:
            self.__end_point = end

        self.setPos(self.__center())
        self.setZValue(90)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsToShape, True)

    def set_end_wgt(self, widget: QGraphicsItem):
        ''' установка виджета для вычисления смещения указателя '''
        self.set_end_point(self.__arrow_ptr_pos())
        self.__end_wgt = widget

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
    
    def __arrow_directions(self):
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

    def set_start_point(self, point: QPointF):
        self.prepareGeometryChange()
        self.__start_point = point
        self.setPos(self.__center())
    
    def set_end_point(self, point: QPointF):
        self.prepareGeometryChange()
        self.__end_point = point
        self.setPos(self.__center())

class QGraphicsStateItem(QGraphicsProxyWidget):
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

    def arrow_disconnect(self, arrow: QGraphicsItem):
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
    TITLE_HEIGHT = 15
    START_WIDTH = 150

    class AddConnectionBtn(QGraphicsPixmapItem):
        def __init__(self, state_id: int):
            self.__state_id = state_id

            pixmap = QMessageBox.standardIcon(QMessageBox.Icon.Information)
            super().__init__(pixmap.scaled(20,20))
            
            self.setZValue(110)
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

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
        
        def __remove(self, mouse_pos):
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

    class CloseBtn(QPushButton):
        mouse_enter = Signal()

        def __init__(self, text:str, parent = None):
            super().__init__(text, parent)
            self.setMouseTracking(True)

        def enterEvent(self, event: QEnterEvent) -> None:
            if event.type() == QMouseEvent.Type.Enter:
                self.mouse_enter.emit()
            return super().enterEvent(event)
        
    def __init__(self, content: str, name: str, id :int, parent = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

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

    @Slot()
    def on_close_btn_mouse_enter(self):
        self.__item_on_scene.show_add_btn()

    def set_graphics_item_ptr(self, item):
        self.__item_on_scene: QGraphicsStateItem = item
        self.__close_btn.mouse_enter.connect(self.on_close_btn_mouse_enter)

    def state_id(self):
        return int(self.__close_btn.text())
    
    def add_btn_pos(self):
        pos = self.__close_btn.pos()
        pos.setX(pos.x() + self.__close_btn.width() + 4)
        return pos

class FlowWidget(QWidget):
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
        self.setStyleSheet("border: 1px solid black;")

        self.__title = QLabel(name, self)
        self.__title.setWordWrap(True)
        self.__description = QLabel(description, self)
        self.__description.setWordWrap(True)
        self.__synonyms_name = QLabel("синонимы", self)
        self.__synonyms_list = QListView(self)
        self.__synonyms_list.hide()
        self.__synonyms_list.setModel(
            QStringListModel(synonym_values, self.__synonyms_list)
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
    def __init__(self, controller):
        super().__init__()
        self.setBackgroundBrush(QColor("#DDDDDD"))

        self.__state_machine_ctrl: StateMachineQtController = controller

    def controller(self):
        return self.__state_machine_ctrl

    def __addStateProxyWidget(self, widget: QWidget, initPos:QPoint) -> QGraphicsStateItem:
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
    
    def addState(self, content:str, name:str, id:int, initPos:QPoint) -> QGraphicsStateItem:
        widget = StateWidget(content, name, id)
        proxy = self.__addStateProxyWidget(widget, initPos)
        widget.set_graphics_item_ptr(proxy)

        return proxy
    
class StateMachineQtController:
    __START_SIZE = QRect(0, 0, 2000, 2000)
    __START_SPACINS = 30

    def __init__(self, id, proj_ctrl, flow_list, synonyms_list):
        self.__proj_id = id
        self.__proj_ctrl: ProjectQtController = proj_ctrl
        self.__flow_list: FlowList = flow_list
        self.__synonyms_list: SynonymsEditor = synonyms_list

        self.__scene = Editor(self)
        self.__proj_ctrl.editor().setScene(self.__scene)
        
        self.__build_editor()
        self.__build_flows()
        self.__build_synonyms()

    def project_controller(self):
        return self.__proj_ctrl
    
    def get_state(self, id:int):
        return self.__states[id]
    
    def add_step(self, from_state_id:int, to_state_id:int):
        arrow = Arrow()
        self.__scene.addItem(arrow)
        self.__states[from_state_id].arrow_connect_as_start(arrow)
        self.__states[to_state_id].arrow_connect_as_end(arrow)

        if from_state_id in self.__steps.keys():
            self.__steps[from_state_id].append(arrow)
        else:
            self.__steps[from_state_id] = [arrow]

    def __build_editor(self):
        self.__scene.setSceneRect(StateMachineQtController.__START_SIZE)
        
        self.__states: dict[int, QGraphicsStateItem] = {}
        self.__steps: dict[int, list[Arrow]] = {}

        data = EditorAPI.instance().get_all_project_states(self.__proj_id)
        
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
        self.__flows = dict[int, FlowWidget]()
        data = EditorAPI.instance().get_all_project_flows(self.__proj_id)

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
        self.__synonyms = dict[int, SynonymWidget]()
        for i in range(4):
            self.__synonyms[int(i)] = SynonymWidget()

        self.__synonym_groups = dict[int, SynonymsGroupWidget]()
        for i in range(3):
            self.__synonym_groups[int(i)] = SynonymsGroupWidget()

        self.__synonyms_list.set_synonyms(self.__synonyms)
        self.__synonyms_list.set_groups(self.__synonym_groups)

class ProjectQtController:
    def __init__(self, id, flow_list):
        self.__proj_id = id
        self.__flow_list: FlowList = flow_list
        self.__editor = QGraphicsView()
        self.__editor.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def editor(self) -> QGraphicsView:
        return self.__editor

class FlowList(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.__area = QScrollArea(self)
        self.__area.setWidgetResizable(True)
        
        lay = QVBoxLayout(self)
        lay.addWidget(self.__area)
    
    def setList(self, items :dict[int, FlowWidget]):
        wrapper = QWidget(self)

        lay = QVBoxLayout(wrapper)

        for wgt_id in items.keys():
            lay.addWidget(items[wgt_id])

        self.__area.setWidget(wrapper)

        lay.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))

class PathValidator(QValidator):
    def init(self):
        super().__init__()

class SynonymWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__title = QLabel("lol", self)
        main_lay = QVBoxLayout(self)
        main_lay.addWidget(self.__title)

class SynonymsList(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.__area = QScrollArea(self)
        self.__area.setWidgetResizable(True)
        
        lay = QVBoxLayout(self)
        lay.addWidget(self.__area)
    
    def setList(self, items :dict[int, SynonymWidget]):
        wrapper = QWidget(self)
        lay = QVBoxLayout(wrapper)

        for wgt_id in items.keys():
            lay.addWidget(items[wgt_id])

        self.__area.setWidget(wrapper)

        empty = lay.isEmpty()
        count = lay.count()

        lay.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))

class SynonymsGroupWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__title = QLabel("kek", self)
        main_lay = QVBoxLayout(self)
        main_lay.addWidget(self.__title)

class SynonymsGroupsList(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.__area = QScrollArea(self)
        self.__area.setWidgetResizable(True)
        
        lay = QVBoxLayout(self)
        lay.addWidget(self.__area)
    
    def setList(self, items :dict[int, SynonymsGroupWidget]):
        wrapper = QWidget(self)
        lay = QVBoxLayout(wrapper)

        for wgt_id in items.keys():
            lay.addWidget(items[wgt_id])

        self.__area.setWidget(wrapper)

        empty = lay.isEmpty()
        count = lay.count()

        lay.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))

class SynonymsEditor (QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, Qt.WindowType.Window)

        self.setWindowTitle('Редактор синонимов')
        self.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)
        
        main_lay = QVBoxLayout(self)
        #main_lay.setContentsMargins(0,0,0,0)
        
        splitter = QSplitter(
            self,
            Qt.Orientation.Horizontal
        )

        self.__group_list = SynonymsGroupsList()
        self.__synonyms_list = SynonymsList(self)
        

        splitter.addWidget(self.__group_list)
        splitter.addWidget(self.__synonyms_list)
        splitter.setStretchFactor(0,0)
        splitter.setStretchFactor(1,1)
        
        main_lay.addWidget(splitter, 1)
        self.resize(600, 500)
        
    def set_synonyms(self, list):
        self.__group_list.setList(list)

    def set_groups(self, list):
        self.__synonyms_list.setList(list)

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
    def new_project(self):
        self.proj_id = EditorAPI.instance().create_project(
            self.get_result()
        )
        self.close()

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

        self.__ok_button.clicked.connect(self.new_project)
    
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
    def __init__(self, flow_list:FlowList, synonyms:SynonymsEditor, parent: QWidget = None):
        super().__init__(parent)
        self.__opened_projects: dict[int, StateMachineQtController] = {}
        self.__flow_list: FlowList = flow_list
        self.__synonyms:SynonymsEditor = synonyms

    def add_project(self, id :int, data: dict) -> StateMachineQtController:
        if id in self.__opened_projects.keys():
            return self.__opened_projects[id]
        
        if (
            not 'name' in data.keys() or
            not 'db_name' in data.keys() or
#            not 'id' in data.keys() or
            not 'file_path' in data.keys()
        ):
            raise RuntimeError(data)
        
        tab_name = str(data['name']) if data['name'] else ''
        
        p_ctrl = ProjectQtController(id, self.__flow_list)
        c_ctrl = StateMachineQtController(id, p_ctrl, self.__flow_list, self.__synonyms)
        self.__opened_projects[id] = c_ctrl
        tab_idx = self.addTab(p_ctrl.editor(), tab_name)

        if 'file_path' in data.keys() and data['file_path']:
            self.tabBar().setTabToolTip(tab_idx, str(data['file_path']))

        return c_ctrl

    def set_active_project(self, id: int):
        self.setCurrentWidget(
            self.__opened_projects[id].project_controller().editor()
        )
        

    def close_project(self, id: int):
        ...

    def project(self, id: int):
        ...
class MainWindow(QMainWindow):
    __oldPos = None

    def __init__(self, flow_list: FlowList, workspaces: Workspaces, synonyms: SynonymsEditor, parent: QWidget = None):
        super().__init__(None, Qt.WindowType.FramelessWindowHint)

        self.__flow_list = flow_list
        self.__workspaces = workspaces
        self.__synonyms_editor = synonyms

        self.__setup_ui()

        self.__setup_toolbar()
        self.show()

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

    def __setup_ui(self):
        self.setCentralWidget(QWidget(self))

        main_lay = QVBoxLayout(self.centralWidget())
        main_lay.setContentsMargins(0,0,0,0)

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
            btn.setToolTip(status_tip)
            btn.setWhatsThis(whats_this)
            btn.setFixedSize(size)
            btn.setIcon(icon)
            btn.setIconSize(size)
            btn.setStyleSheet(style)
            layout.addWidget(btn)