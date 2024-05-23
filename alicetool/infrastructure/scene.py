from math import sqrt

from PySide6.QtCore import (
    QPointF,
    QRectF,
)

from PySide6.QtGui import (
    QColor,
    QPen,
    QPainter,
)

from PySide6.QtWidgets import (
    QWidget,
    QGraphicsItem,
    QStyleOptionGraphicsItem,
)

class Arrow(QGraphicsItem):
    __start_point: QPointF
    __end_point: QPointF
    __pen_width: int
    __end_wgt: QGraphicsItem #TODO: SceneNode

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

