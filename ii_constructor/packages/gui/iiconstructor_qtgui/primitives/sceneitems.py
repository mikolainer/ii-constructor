# Этот файл — часть "Конструктора интерактивных инструкций".
#
# Конструктор интерактивных инструкций — свободная программа:
# вы можете перераспространять ее и/или изменять ее на условиях
# Стандартной общественной лицензии GNU в том виде,
# в каком она была опубликована Фондом свободного программного обеспечения;
# либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.
# Конструктор интерактивных инструкций распространяется в надежде,
# что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ;
# даже без неявной гарантии ТОВАРНОГО ВИДА
# или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ.
# Подробнее см. в Стандартной общественной лицензии GNU.
#
# Вы должны были получить копию Стандартной общественной лицензии GNU
# вместе с этой программой. Если это не так,
# см. <https://www.gnu.org/licenses/>.


from collections.abc import Callable
from enum import UNIQUE, IntEnum, verify
from math import sqrt
from typing import Any

from PySide6.QtCore import (
    QObject,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QContextMenuEvent,
    QFocusEvent,
    QFont,
    QKeyEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygon,
    QTransform,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsProxyWidget,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMenu,
    QScrollArea,
    QStyleOptionGraphicsItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .buttons import EnterDetectionButton


class Arrow(QGraphicsItem):
    """Ребро графа на сцене"""

    __start_point: QPointF
    __end_point: QPointF
    __pen_width: int
    __pen_color: QColor
    __end_wgt: QGraphicsItem | None  # TODO: SceneNode
    __edit_connection_callback: Callable

    def __init__(
        self,
        start: QPointF = None,
        end: QPointF = None,
        parent: QGraphicsItem = None,
    ) -> None:
        super().__init__(parent)

        self.__start_point = QPointF(0.0, 0.0)
        self.__end_point = QPointF(3.0, 3.0)
        self.__pen_width = 5
        self.__end_wgt = None
        self.__pen_color = QColor("black")

        self.__doubleclick_callback = lambda: None

        if start is not None:
            self.__start_point = start
        if end is not None:
            self.__end_point = end

        self.setPos(self.__center())
        self.setZValue(90)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsToShape, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

    def set_edit_connection_handler(self, doubleclick_callback: Callable):
        self.__edit_connection_callback = doubleclick_callback

    def set_end_wgt(self, widget: QGraphicsItem):
        """Прикрепляет конец ребра к элементу сцены"""
        self.set_end_point(self.__arrow_ptr_pos())
        self.__end_wgt = widget

    def set_start_point(self, point: QPointF):
        """Устанавливает позицию начала"""
        self.prepareGeometryChange()
        self.__start_point = point
        self.setPos(self.__center())

    def set_end_point(self, point: QPointF):
        """Устанавливает позицию конца"""
        self.prepareGeometryChange()
        self.__end_point = point
        self.setPos(self.__center())

    def shape(self) -> QPainterPath:
        # return super().shape()

        path = QPainterPath()
        path.addPolygon(self.mapFromScene(self.__boundingPolygon()))
        return path

    def focusInEvent(self, event: QFocusEvent) -> None:
        return super().focusInEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.__edit_connection_callback()
        return super().mouseDoubleClickEvent(event)

    def itemChange(
        self, change: QGraphicsItem.GraphicsItemChange, value: Any
    ) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            if value:
                self.__pen_color = QColor("blue")
            else:
                self.__pen_color = QColor("black")

        return super().itemChange(change, value)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self.__edit_connection_callback()

        super().keyPressEvent(event)

    def boundingRect(self) -> QRectF:
        """
        Возвращает область границ объекта на сцене в локальных координатах
        """
        pen_padding = QPointF(float(self.__pen_width), float(self.__pen_width))
        arrow_pointer_padding = QPointF(
            self.__dir_pointer_half().x(),
            self.__dir_pointer_half().x(),
        )
        size = self.__delta() + pen_padding * 2 + arrow_pointer_padding * 2

        x = 0 - size.x() / 2
        y = 0 - size.y() / 2

        return QRectF(x, y, size.x(), size.y())

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget = None,
    ):
        pen = QPen(self.__pen_color)
        pen.setWidth(self.__pen_width)
        painter.setPen(pen)

        pointer_left_pos, pointer_pos, pointer_right_pos = (
            self.__get_pointer_pos()
        )
        painter.drawLine(
            self.mapFromScene(pointer_pos),
            self.mapFromScene(pointer_left_pos),
        )
        painter.drawLine(
            self.mapFromScene(pointer_pos),
            self.mapFromScene(pointer_right_pos),
        )

        end_point = self.__end_point
        if self.__end_wgt is not None:
            bounding = self.__end_wgt.boundingRect()
            wgt_half_size = QPointF(bounding.width(), bounding.height()) / 2
            end_point = self.__end_wgt.scenePos() + wgt_half_size

        painter.drawLine(
            self.mapFromScene(self.__start_point),
            self.mapFromScene(end_point),
        )

        # для дебага
        # painter.setPen(QColor('red'))
        # painter.drawPolygon(self.mapFromScene(self.__boundingPolygon()))

    def __get_pointer_pos(self) -> tuple[QPoint, QPoint, QPoint]:
        k = (
            self.__arrow_directions()
        )  # в уравнении прямой 'y=kx' k = tg угла наклона

        # локальный алиас для короткого обращения к значению
        h_ptr = self.__dir_pointer_half()
        # длина половинки указателя стрелки (гепотинуза)
        r = sqrt(h_ptr.x() ** 2.0 + h_ptr.y() ** 2.0)

        pointer_pos = self.__arrow_ptr_pos()

        # решения систем уравнений прямой, проходящей через центр координат и окружности в центре координат для обеих половинок указателя стрелки
        if k["mode"] == "up":
            pointer_left_pos = QPointF(
                pointer_pos.x() + self.__dir_pointer_half().x(),
                pointer_pos.y() + self.__dir_pointer_half().y(),
            )
            pointer_right_pos = QPointF(
                pointer_pos.x() - self.__dir_pointer_half().x(),
                pointer_pos.y() + self.__dir_pointer_half().y(),
            )
        elif k["mode"] == "down":
            pointer_left_pos = QPointF(
                pointer_pos.x() + self.__dir_pointer_half().x(),
                pointer_pos.y() - self.__dir_pointer_half().y(),
            )
            pointer_right_pos = QPointF(
                pointer_pos.x() - self.__dir_pointer_half().x(),
                pointer_pos.y() - self.__dir_pointer_half().y(),
            )

        elif k["mode"] == "ctg":
            y_left = sqrt(r**2.0 / (k["left"] ** 2.0 + 1.0))
            pointer_left_pos = QPointF(k["left"] * y_left, y_left)

            y_right = sqrt(r**2.0 / (k["right"] ** 2.0 + 1.0))
            pointer_right_pos = QPointF(k["right"] * y_right, y_right)
        else:  # if k['mode'] == 'tg'
            x_left = sqrt(r**2.0 / (k["left"] ** 2.0 + 1.0))
            pointer_left_pos = QPointF(x_left, k["left"] * x_left)

            x_right = sqrt(r**2.0 / (k["right"] ** 2.0 + 1.0))
            pointer_right_pos = QPointF(x_right, k["right"] * x_right)

        # выбор одного из двух возможных решений сиснетмы уравнений
        if k["mode"] == "ctg":
            if self.__start_point.y() > self.__end_point.y():
                pointer_left_pos = pointer_pos + pointer_left_pos
                pointer_right_pos = pointer_pos + pointer_right_pos
            else:
                pointer_left_pos = pointer_pos - pointer_left_pos
                pointer_right_pos = pointer_pos - pointer_right_pos

        else:
            if self.__start_point.x() > self.__end_point.x():
                pointer_left_pos = pointer_pos + pointer_left_pos
                pointer_right_pos = pointer_pos + pointer_right_pos
            else:
                pointer_left_pos = pointer_pos - pointer_left_pos
                pointer_right_pos = pointer_pos - pointer_right_pos

        return pointer_left_pos, pointer_pos, pointer_right_pos

    def __boundingPolygon(self) -> QPolygon:
        end_left_pos, end_pos, end_right_pos = self.__get_pointer_pos()
        end_left_pos_ = QPointF(end_left_pos)
        end_right_pos_ = QPointF(end_right_pos)
        end_pos_ = QPointF(end_pos)

        # начало магии
        ptr_left_vector = end_left_pos_ - end_pos_
        ptr_right_vector = end_right_pos_ - end_pos_
        ptr_end_vector = self.__end_point - self.__start_point

        half_len = sqrt(
            self.__dir_pointer_half().x() ** 2
            + self.__dir_pointer_half().y() ** 2,
        )

        ptr_left_vector_c = self.__pen_width / half_len
        # half_len / (half_len + self.__pen_width)
        ptr_right_vector_c = self.__pen_width / half_len
        # half_len / (half_len + self.__pen_width) / half_len
        ptr_end_vector_c = self.__pen_width / self.__line_len()
        # self.__line_len() / (self.__line_len() + self.__pen_width)

        end_left_pos_ = end_left_pos_ + ptr_left_vector * ptr_left_vector_c
        end_right_pos_ = end_right_pos_ + ptr_right_vector * ptr_right_vector_c
        end_pos_ = end_pos_ + ptr_end_vector * ptr_end_vector_c

        end_between_vector = end_right_pos_ - end_left_pos_
        to_center_coef = (
            float(self.__pen_width) / self.__dir_pointer_half().x()
        )
        end_left_pos_ -= end_between_vector / 2.0 * to_center_coef
        end_right_pos_ += end_between_vector / 2.0 * to_center_coef
        # конец магии

        end_between_vector = end_right_pos_ - end_left_pos_
        to_center_coef = (
            float(self.__pen_width) / self.__dir_pointer_half().x()
        )
        end_left_center_pos = (
            end_left_pos_ + end_between_vector / 2 * to_center_coef
        )
        end_right_center_pos = (
            end_right_pos_ - end_between_vector / 2 * to_center_coef
        )
        start_left = (
            self.__start_point - end_between_vector / 2 * to_center_coef
        )
        start_right = (
            self.__start_point + end_between_vector / 2 * to_center_coef
        )

        polygon_points = list[QPoint]()

        xpos = end_left_center_pos.x()
        ypos = end_left_center_pos.y()
        polygon_points.append(QPoint(xpos, ypos))

        xpos = end_left_pos_.x()
        ypos = end_left_pos_.y()
        polygon_points.append(QPoint(xpos, ypos))

        xpos = end_pos_.x()
        ypos = end_pos_.y()
        polygon_points.append(QPoint(xpos, ypos))

        xpos = end_right_pos_.x()
        ypos = end_right_pos_.y()
        polygon_points.append(QPoint(xpos, ypos))

        xpos = end_right_center_pos.x()
        ypos = end_right_center_pos.y()
        polygon_points.append(QPoint(xpos, ypos))

        xpos = start_right.x()
        ypos = start_right.y()
        polygon_points.append(QPoint(xpos, ypos))

        xpos = start_left.x()
        ypos = start_left.y()
        polygon_points.append(QPoint(xpos, ypos))

        return QPolygon(polygon_points)

    def __dir_pointer_half(self) -> QPointF:
        """
        Возвращает вектор половинки указателя стрелки:
        x - отступ от линии,
        y - расстояние от указываемой точки вдоль линии
        """
        return QPointF(self.__pen_width * 1.5, self.__pen_width * 3.0)

    def __arrow_directions(self) -> dict:
        """
        Возвращает направдения (tg углов от направления оси глобальных координат x):
        back - вектор направленный от указываемой точки к началу линии;
        left, right - от указываемой точки в направлении половинок указателя стрелки
        """
        a = self.__end_point
        b = self.__start_point

        delta_x = a.x() - b.x()
        delta_y = a.y() - b.y()

        ab_ctg = delta_x / delta_y if delta_y != 0 else 0
        ab_tg = delta_y / delta_x if delta_x != 0 else 0

        cot: bool = abs(ab_ctg) < abs(ab_tg)

        h_ptr = self.__dir_pointer_half()
        delta_tg = h_ptr.x() / h_ptr.y()

        if delta_x == 0:
            mode = "down" if delta_y > 0 else "up"
        else:
            mode = "ctg" if cot else "tg"

        return {
            "mode": mode,
            "back": ab_ctg if cot else ab_tg,
            "left": ab_ctg + delta_tg if cot else ab_tg + delta_tg,
            "right": ab_ctg - delta_tg if cot else ab_tg - delta_tg,
        }

    def __delta(self) -> QPointF:
        """
        Возвращает длину проекций линии стрелки на оси глобальных координат
        """
        x = max(self.__start_point.x(), self.__end_point.x()) - min(
            self.__start_point.x(),
            self.__end_point.x(),
        )

        y = max(self.__start_point.y(), self.__end_point.y()) - min(
            self.__start_point.y(),
            self.__end_point.y(),
        )

        return QPointF(x, y)

    def __center(self) -> QPointF:
        """
        Вычисляет центр объекта на сцене из начальной и конечной точек
        в глобальных координатах
        """
        x = max(self.__start_point.x(), self.__end_point.x())
        y = max(self.__start_point.y(), self.__end_point.y())

        return QPointF(x, y) - self.__delta() / 2

    def __line_len(self) -> float:
        """Вычисляет длину ребра"""
        delt = self.__delta()
        return sqrt(delt.x() ** 2 + delt.y() ** 2)

    def __arrow_ptr_pos(self) -> QPointF:
        """Вычисляет положение указателя направления ребра"""
        if self.__end_wgt is None:
            return self.__end_point

        bounding = self.__end_wgt.boundingRect()
        wgt_half_size = QPointF(bounding.width(), bounding.height()) / 2.0
        wgt_center = self.__end_wgt.scenePos() + wgt_half_size

        hw_cos: float = bounding.width() / sqrt(
            bounding.width() ** 2.0 + bounding.height() ** 2.0,
        )
        if self.__line_len() == 0:
            sin = 1
            cos = 0
        else:
            cos: float = self.__delta().x() / self.__line_len()
            sin: float = self.__delta().y() / self.__line_len()

        if hw_cos < cos:
            """решение на вертикальных гранях"""
            if cos == 0:
                y = 0

            if self.__start_point.x() < self.__end_point.x():
                """решение на левой грани"""
                x = bounding.height() / 2.0
                if self.__start_point.y() > self.__end_point.y():
                    """нижняя часть"""
                    y = (bounding.width() * self.__delta().y()) / (
                        self.__line_len() * 2 * (0 - cos)
                    )
                else:
                    """верхняя часть"""
                    y = (bounding.width() * self.__delta().y()) / (
                        self.__line_len() * 2 * cos
                    )
            else:
                """решение на правой грани"""
                x = -(bounding.height() / 2.0)
                if self.__start_point.y() > self.__end_point.y():
                    """нижняя часть"""
                    y = (bounding.width() * self.__delta().y()) / (
                        self.__line_len() * 2 * (0 - cos)
                    )
                else:
                    """верхняя часть"""
                    y = (bounding.width() * self.__delta().y()) / (
                        self.__line_len() * 2 * cos
                    )

        else:
            """решение на горизонтальных гранях"""
            if sin == 0:
                x = 0
            # else:
            #    x = (bounding.height() * self.__delta().x()) / (self.__line_len() * 2 * sin)

            if self.__start_point.y() > self.__end_point.y():
                """решение на нижней грани"""
                y = -(bounding.height() / 2.0)
                if self.__start_point.x() > self.__end_point.x():
                    """правая часть"""
                    x = (bounding.height() * self.__delta().x()) / (
                        self.__line_len() * 2 * (0 - sin)
                    )
                else:
                    """левая часть"""
                    x = (bounding.height() * self.__delta().x()) / (
                        self.__line_len() * 2 * sin
                    )
            else:
                """решение на верхней грани"""
                y = bounding.height() / 2.0
                if self.__start_point.x() > self.__end_point.x():
                    """правая часть"""
                    x = (bounding.height() * self.__delta().x()) / (
                        self.__line_len() * 2 * (0 - sin)
                    )
                else:
                    """левая часть"""
                    x = (bounding.height() * self.__delta().x()) / (
                        self.__line_len() * 2 * sin
                    )

        return QPointF(wgt_center.x() - x, wgt_center.y() - y)


class AddConnectionBtn(QGraphicsPixmapItem, QObject):
    """Инструмент добавления рёбер в граф"""

    __arrow: Arrow | None
    __state: QGraphicsProxyWidget
    end_pos: QPointF
    is_active: bool
    __is_hide_disabled: bool

    connection_added = Signal()

    def __init__(self, start_item: QGraphicsProxyWidget) -> None:
        self.__state = start_item
        self.end_pos = None
        self.is_active = True
        self.__is_hide_disabled = False

        # pixmap = QMessageBox.standardIcon(QMessageBox.Icon.Information)
        pixmap = QPixmap(":/icons/plus_btn.svg")
        QObject.__init__(self)
        super().__init__(pixmap.scaled(20, 20))

        self.setZValue(110)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def __start_effect(self):
        """Инициирует отображение временной стрелки"""
        self.__is_hide_disabled = True
        pos = self.__state.scenePos()
        size = self.__state.size()
        pos.setX(pos.x() + size.width() / 2)
        pos.setY(pos.y() + size.height() / 2)

        self.__arrow = Arrow()
        self.__arrow.set_start_point(pos)

        center = QPointF(10, 10)
        self.__arrow.set_end_point(self.scenePos() + center)

        self.scene().addItem(self.__arrow)

    def __end_effect(self, mouse_pos: QPointF):
        """Завершает отображение временной стрелки"""
        self.__is_hide_disabled = False
        self.scene().removeItem(self.__arrow)
        self.__arrow = None
        self.is_active = False
        self.end_pos = mouse_pos
        self.connection_added.emit()
        self.hide()

    def hide(self) -> None:
        if not self.__is_hide_disabled:
            return super().hide()

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        center = QPointF(10, 10)
        self.__arrow.set_end_point(self.scenePos() + center)
        return super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        QTimer.singleShot(
            0,  # нельзя обновлять сцену до возвращения в цикл событий Qt
            lambda: self.__start_effect(),
        )
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        pos = event.scenePos()
        QTimer.singleShot(
            0,  # нельзя обновлять сцену до возвращения в цикл событий Qt
            lambda: self.__end_effect(pos),
        )
        return super().mouseReleaseEvent(event)


class NodeControll(QGraphicsRectItem):
    """Манипулятор (невидимый объект для управления позицией)"""

    def __init__(
        self,
        rect: QRectF | QRect,
        parent: QGraphicsItem | None = None,
    ) -> None:
        super().__init__(rect, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setPen(QPen(Qt.GlobalColor.transparent))
        self.setBrush(QBrush(Qt.GlobalColor.transparent))

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change in [
            QGraphicsItem.GraphicsItemChange.ItemPositionChange,
            QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged,
        ] and len(self.childItems()):
            child: SceneNode = self.childItems()[0]
            child.update_arrows()

        return super().itemChange(change, value)


class SceneNode(QGraphicsProxyWidget):
    """Вершина графа на сцене"""

    __Z_VAL = 100
    __WATCHDOG_TIMEOUT = 3000

    __have_callbacks: bool

    __add_btns: list[AddConnectionBtn]
    __arrows: dict[str, list[Arrow]]

    __controll: NodeControll

    __watchdog: QTimer

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__()
        self.__have_callbacks = False
        self.__watchdog = QTimer()
        self.__watchdog.setInterval(self.__WATCHDOG_TIMEOUT)
        self.__watchdog.setSingleShot(True)
        self.__watchdog.timeout.connect(self.hide_tools)

        # контейнеры для соединений
        self.__arrows = {"from": list[Arrow](), "to": list[Arrow]()}
        self.__add_btns = []

        # обёртка содержимого
        widget = NodeWidget("")

        # элемент сцены
        self.setZValue(self.__Z_VAL)
        super().setWidget(widget)
        scene.addItem(self)
        self.hide_tools()

        self.setWidget(QTextEdit())

        # инициализация манипулятора
        controll_pos = self.scenePos()
        controll_size = QSize(
            NodeWidget.START_WIDTH
            - NodeWidget.BUTTON_SIZE
            - NodeWidget.BUTTONS_MARGIN * 2,
            NodeWidget.TITLE_HEIGHT,
        )

        self.__controll = NodeControll(QRectF(controll_pos, controll_size))
        self.__controll.setZValue(self.__Z_VAL)
        scene.addItem(self.__controll)

        self.setParentItem(self.__controll)
        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, True
        )
        self.installSceneEventFilter(self.__controll)

        # обратная связь для управления дополнительными элементами
        widget.set_graphics_item_ptr(self)

    def set_choose_mode(self, is_choose_mode: bool):
        self.wrapper_widget().set_choose_mode(is_choose_mode)

    def setWidget(self, widget: QWidget) -> None:
        """Устанавливает виджет внутрь обёртки"""
        wgt: NodeWidget = super().widget()
        wgt.setWidget(widget)

    def wrapper_widget(self) -> "NodeWidget":
        return super().widget()

    def widget(self) -> QWidget:
        """Возвращает виджет из обёртки"""
        wgt: NodeWidget = super().widget()
        return wgt.widget()

    def setPos(self, x: float, y: float) -> None:
        """Перемещает манипулятор"""
        self.__controll.setPos(x, y)

    def set_title(self, text: str):
        """Устанавливает текст заголовка обёртки"""
        wgt: NodeWidget = super().widget()
        wgt.set_title(text)

    def hide_tools(self):
        """Прячет дополнительные органы управления"""
        wgt: NodeWidget = super().widget()
        wgt.set_close_btn_style(NodeWidget.CloseBtnStyle.Add)
        self.reset_tools()
        self.__watchdog.stop()

        for btn in self.__add_btns:
            if btn.is_active:
                btn.hide()

    def show_tools(self):
        """Отображает дополнительные органы управления"""
        for btn in self.__add_btns:
            if btn.is_active:
                wgt: NodeWidget = super().widget()
                wgt.set_close_btn_style(NodeWidget.CloseBtnStyle.Close)

                btn.show()

        self.__watchdog.start()

    def reset_tools(self):
        """Инициализирует или возвращает в исходное состояние дополнительные органы управления"""
        for btn in self.__add_btns:
            if btn.is_active:
                return

        wgt: NodeWidget = super().widget()
        pos = wgt.add_btn_pos()
        add_btn = AddConnectionBtn(self)
        add_btn.setParentItem(self)
        add_btn.setPos(pos)
        add_btn.connection_added.connect(
            lambda: self.__add_connection_request(add_btn)
        )
        self.__add_btns.append(add_btn)

        self.scene().addItem(add_btn)

    def set_handlers(
        self,
        new_step_handler: Callable[["SceneNode", "SceneNode"], None],
        new_state_handler: Callable[["SceneNode", QPoint], None],
        save_lay: Callable[["SceneNode", QPointF], None],
    ):
        self.__new_step_callback = new_step_handler
        self.__new_state_callback = new_state_handler
        self.__save_layout_callback = save_lay
        self.__have_callbacks = True

    def __add_connection_request(self, btn: AddConnectionBtn):
        self.hide_tools()
        self.scene().removeItem(btn)

        from_node = self
        to_node = self.scene().itemAt(btn.end_pos, QTransform())

        if self.__have_callbacks:
            if isinstance(to_node, SceneNode):
                self.__new_step_callback(from_node, to_node)
            else:
                self.__new_state_callback(from_node, btn.end_pos)

        self.__add_btns.remove(btn)

    def arrow_connect_as_start(self, arrow: Arrow):
        """Связывает начало ребра с этой вершиной"""
        if arrow not in self.__arrows["from"]:
            self.__arrows["from"].append(arrow)
            bounding = self.boundingRect()
            center = QPointF(bounding.width() / 2.0, bounding.height() / 2.0)
            arrow.set_start_point(self.scenePos() + center)

    def arrow_connect_as_end(self, arrow: Arrow):
        """Связывает конец ребра с этой вершиной"""
        if arrow not in self.__arrows["to"]:
            self.__arrows["to"].append(arrow)
            bounding = self.boundingRect()
            center = QPointF(bounding.width() / 2.0, bounding.height() / 2.0)
            arrow.set_end_point(self.scenePos() + center)
            arrow.set_end_wgt(self)

    def arrow_disconnect(self, arrow: Arrow):
        """Удаляет связь ребра с этой вершиной"""
        if arrow in self.__arrows["from"]:
            self.__arrows["from"].remove(arrow)

        if arrow in self.__arrows["to"]:
            self.__arrows["to"].remove(arrow)

    def update_arrows(self):
        """Обновляет связанные рёбра графа"""
        bounding = self.boundingRect()
        center = QPointF(bounding.width() / 2.0, bounding.height() / 2.0)

        for arrow in self.__arrows["to"]:
            arrow.set_end_point(self.scenePos() + center)

        for arrow in self.__arrows["from"]:
            arrow.set_start_point(self.scenePos() + center)

        if self.__have_callbacks:
            self.__save_layout_callback(self, self.scenePos())


class NodeWidget(QWidget):
    @verify(UNIQUE)
    class CloseBtnStyle(IntEnum):
        Close = 0
        Add = 1

    """ Визуальная обёртка над содержимым вершины графа """
    BUTTONS_MARGIN: int = 2
    BUTTON_SIZE: int = 15
    TITLE_HEIGHT: int = 20
    START_WIDTH: int = 150

    __title: "NodeTitle"
    __close_btn: EnterDetectionButton
    __content: QScrollArea
    __item_on_scene: SceneNode | None

    open_settings = Signal()
    delete_request = Signal(SceneNode)
    chosen = Signal(SceneNode)
    __choose_mode: bool
    __change_title_handler: Callable[[str], bool]

    def set_change_title_handler(self, handler: Callable[[str], bool]):
        self.__change_title_handler = handler

    def __init__(self, title: str, parent=None) -> None:
        self.__change_title_handler = None
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        title_wrapper = QWidget(self)
        title_wrapper.setProperty("isNodeTitle", True)

        self.__choose_mode = False
        self.__item_on_scene = None
        self.__title = NodeTitle(title, title_wrapper)
        self.__title.open_settings.connect(lambda: self.open_settings.emit())
        font = self.__title.font()
        font.setWeight(QFont.Weight.ExtraBold)
        self.__title.setFont(font)
        self.__title.setFixedHeight(self.TITLE_HEIGHT)
        self.__close_btn = EnterDetectionButton(title_wrapper)
        self.__close_btn.setFixedHeight(self.BUTTON_SIZE)
        self.__close_btn.setFixedWidth(self.BUTTON_SIZE)
        self.set_close_btn_style(self.CloseBtnStyle.Add)

        self.__content = QScrollArea(self)
        self.__content.setWidgetResizable(True)
        self.__content.setProperty("isNodeContent", True)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        title_lay = QHBoxLayout(title_wrapper)
        title_lay.setContentsMargins(5, 2, 2, 2)

        title_lay.addWidget(self.__title)
        title_lay.addWidget(self.__close_btn)

        main_lay.addWidget(title_wrapper)
        main_lay.addWidget(self.__content)

        self.resize(self.START_WIDTH, self.START_WIDTH)

    def set_choose_mode(self, is_choose_mode: bool):
        self.__choose_mode = is_choose_mode
        self.widget().setEnabled(not is_choose_mode)

    def set_close_btn_style(self, style: CloseBtnStyle):
        if style == self.CloseBtnStyle.Add:
            pixmap = QPixmap(":/icons/plus_btn.svg").scaled(QSize(20, 20))

        elif style == self.CloseBtnStyle.Close:
            pixmap = QPixmap(":icons/delete_btn.svg").scaled(QSize(20, 20))

        self.__close_btn.setIcon(
            pixmap.scaled(self.BUTTON_SIZE, self.BUTTON_SIZE)
        )

    def set_title(self, text: str):
        """Устанавливает заголовок. Прямое использование не ожидается (обрабатывается в SceneNode)"""
        if self.__change_title_handler is None or self.__change_title_handler(
            text
        ):
            self.__title.setText(text)
            self.__title.setToolTip(text)

    def setWidget(self, widget: QWidget) -> None:
        """Устанавливает содержимое. Прямое использование не ожидается (обрабатывается в SceneNode)"""
        return self.__content.setWidget(widget)

    def widget(self) -> QWidget:
        """Возвращает содержимое"""
        return self.__content.widget()

    def add_btn_pos(self) -> QPoint:
        """Возвращает позицию для AddConnectionBtn"""
        pos = self.__close_btn.pos()
        pos.setX(pos.x() + self.__close_btn.width() + 4)
        return pos

    def set_graphics_item_ptr(self, item: SceneNode):
        """Устанавливает обратную связь для управления отображением дополнительных органов управления SceneNode"""
        self.__item_on_scene = item
        self.__close_btn.mouse_enter.connect(self.on_close_btn_mouse_enter)
        self.__close_btn.clicked.connect(self.on_close_btn_mouse_clicked)

    @Slot()
    def on_close_btn_mouse_clicked(self):
        if self.__choose_mode:
            self.chosen.emit(self.__item_on_scene)
        else:
            self.delete_request.emit(self.__item_on_scene)

    @Slot()
    def on_close_btn_mouse_enter(self):
        if self.__item_on_scene is not None and not self.__choose_mode:
            self.__item_on_scene.show_tools()


class NodeTitle(QLabel):
    open_settings = Signal()

    def __init__(self, text: str, parent: QWidget | None) -> None:
        super().__init__(text, parent)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)
        action = menu.addAction("Переименовать")
        result = menu.exec_(self.mapToGlobal(event.pos()))
        if action == result:
            self.open_settings.emit()


class EditorView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent: QWidget = None) -> None:
        super().__init__(scene, parent)
        self.centerOn(0, 0)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def wheelEvent(self, event: QWheelEvent) -> None:
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            scale_factor = 1 + (
                0.1 * (1 if event.angleDelta().y() > 0 else -1)
            )
            self.scale(scale_factor, scale_factor)
            event.accept()

        else:
            return super().wheelEvent(event)


class Editor(QGraphicsScene):
    __START_SIZE = QRect(0, 0, 2000, 2000)
    START_SPACINS = 30

    doubleClicked = Signal(QPointF)

    def __init__(self, parent: QObject | None) -> None:
        super().__init__(parent)
        # self.setSceneRect(self.__START_SIZE)
        self.setBackgroundBrush(QColor("#DDDDDD"))

    def addNode(self, pos: QPoint, content: QWidget = None) -> SceneNode:
        """Добавляет вершину графа на сцену"""
        node = SceneNode(self)

        if content is not None:
            node.setWidget(content)

        x = pos.x()
        if x < 0:
            x = 0

        y = pos.y()
        if y < 0:
            y = 0

        # TODO: по умолчанию под указателем мыши
        node.setPos(x, y)

        return node

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit(event.scenePos())

        return super().mouseDoubleClickEvent(event)
