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
    QScrollArea,
    QVBoxLayout,
    QStackedWidget,
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

from .widgets import SynonymsGroupWidget, SynonymEditorWidget

    
class SynonymsGroupsDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        data = index.internalPointer()
        wgt = SynonymsGroupWidget(data.on[CustomDataRole.Name], data.on[CustomDataRole.Id], data.on[CustomDataRole.Description])
        wgt.resize(option.rect.size())

        painter.setClipRect(option.rect)

        painter.save()
        painter.drawPixmap(option.rect, wgt.grab())
        painter.restore()

        super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        data = index.internalPointer()
        wgt = SynonymsGroupWidget(data.on[CustomDataRole.Name], data.on[CustomDataRole.Id], data.on[CustomDataRole.Description])
        wgt.adjustSize()
        return wgt.size()

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

    def setModel(self, model: QAbstractItemModel | None) -> None:
        super().setModel(model)
        #if model.rowCount() > 0:
        #    self.setCurrentIndex(model.index(0))


class SynonymsSetDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        data = index.internalPointer()
        wgt = SynonymEditorWidget(data)
        wgt.resize(option.rect.size())

        painter.setClipRect(option.rect)

        painter.save()
        painter.drawPixmap(option.rect, wgt.grab())
        painter.restore()

        super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        data = index.internalPointer()
        wgt = SynonymEditorWidget(data)
        wgt.adjustSize()
        return wgt.size()

class SynonymsSetView(QListView):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.__delegate = SynonymsSetDelegate(self)
        self.setItemDelegate(self.__delegate)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)

class SynonymsList(QStackedWidget):
    __indexed: dict[int, SynonymsSetView]
    __empty_index:int

    def addWidget(self, w: QWidget = None) -> int:
        area = QScrollArea(self)
        area.setWidgetResizable(True)
        area.setStyleSheet('QScrollArea{background-color: #FFFFFF; border: none;}')

        #wrapper = QWidget(self)
        #QVBoxLayout(wrapper)
        #w.setParent(wrapper)

        area.setWidget(w)
        return super().addWidget(area)
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__indexed = {}
        self.__empty_index = super().addWidget(QWidget(self))

    def set_empty(self):
        self.setCurrentIndex(self.__empty_index)
    
    def setList(self, view: SynonymsSetView, set_current: bool = False):
        ''' обновление списка виджетов '''
        # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not view in self.__indexed.values():
            self.__indexed[self.addWidget(view)] = view

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(view)]

        # если указано - устанавливаем текущим виджетом
        if set_current:
            self.setCurrentIndex(idx)