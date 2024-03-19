from typing import List
from PySide6.QtCore import (
    QAbstractItemModel,
    QItemSelection,
    QItemSelectionModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPoint, 
    QRect,
    QSize,
    Qt, Slot, Signal,
)

from PySide6.QtGui import (
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QRegion,
    QColor,
    QPen,
    QPixmap,
    QImage,
)

from PySide6.QtWidgets import (
    QStyleOptionViewItem,
    QStyleOption,
    QWidget,
    QLabel,
    QAbstractItemView,
    QAbstractItemDelegate,
    QStyledItemDelegate,
    QListView,
)

from .data import CustomDataRole

from .widgets import SynonymsGroupWidget

    
class SynonymsGroupsDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        data = index.internalPointer()
        wgt = SynonymsGroupWidget(data.on[CustomDataRole.Name], data.on[CustomDataRole.Id])
        wgt.resize(option.rect.size())

        painter.setClipRect(option.rect)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(option.rect, wgt.grab())
        painter.restore()

        super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        return QSize(100, 50)

class SynonymsGroupsView(QListView):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.__delegate = SynonymsGroupsDelegate(self)
        self.setItemDelegate(self.__delegate)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)

    on_selectionChanged = Signal(QItemSelection, QItemSelection)

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        self.on_selectionChanged.emit(selected, deselected)
        return super().selectionChanged(selected, deselected)
    
    ### абстрактные методы

#    def moveCursor(self, cursorAction: QAbstractItemView.CursorAction, modifiers: Qt.KeyboardModifier) -> QModelIndex:
#        return QModelIndex()
#
#    def isIndexHidden(self, index: QModelIndex | QPersistentModelIndex) -> bool:
#        return False
#
#    def horizontalOffset(self) -> int:
#        return 0
#    
#    def verticalOffset(self) -> int:
#        return 0
#    
#    def setSelection(self, rect: QRect, command: QItemSelectionModel.SelectionFlag) -> None:
#        return
#    
#    def indexAt(self, point: QPoint) -> QModelIndex:
#        return QModelIndex()
#    
#    def visualRect(self, index: QModelIndex | QPersistentModelIndex) -> QRect:
#        #return QRect(0,0,100,50)
#        item_h = 50
#
#        x = self.horizontalOffset()
#        y = self.verticalOffset() + item_h*index.row()
#
#        return QRect(
#            x, y,
#            self.width() - 2 * self.horizontalOffset(),
#            item_h
#        )
#    
#    def visualRegionForSelection(self, selection: QItemSelection) -> QRegion:
#        return QRegion()
#    
#    def scrollTo(self, index: QModelIndex | QPersistentModelIndex, hint: QAbstractItemView.ScrollHint = ...) -> None:
#        return
    
    