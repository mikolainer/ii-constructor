from typing import List
from PySide6.QtCore import (
    QAbstractItemModel,
    QEvent,
    QItemSelection,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QSize,
    Signal,
    Slot
)

from PySide6.QtGui import (
    QMouseEvent,
    QPainter,
)

from PySide6.QtWidgets import (
    QScrollArea,
    QStackedWidget,
    QStyleOptionViewItem,
    QWidget,
    QStyledItemDelegate,
    QListView,
    QTableView,
    QHeaderView,
)

from .data import CustomDataRole, SynonymsSetModel
from .widgets import SynonymsGroupWidget, SynonymEditorWidget, FlowWidget

    
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


class SynonymsSetDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget:
        return super().createEditor(parent, option, index)
    
    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        super().updateEditorGeometry(editor, option, index)
    
    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:
        super().setEditorData(editor, index)
    
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None:
        model.setData(index, editor.text())

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

class FlowsDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        if isinstance(parent, FlowsView):
            parent.installEventFilter(self)

    def __on_slider_visible_changed(self, visible:bool, index:QModelIndex, editor:FlowWidget):
        index.model().setData(
            index, visible, CustomDataRole.SliderVisability
        )
        editor.adjustSize()
        self.parent().setRowHeight(index.row(), editor.height())

    def destroyEditor(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:
        self.__editor = None
        return super().destroyEditor(editor, index)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget:
        editor = FlowWidget(
            index.data(CustomDataRole.Id),
            index.data(CustomDataRole.Name),
            index.data(CustomDataRole.Description),
            index.data(CustomDataRole.SynonymsSet)[0],
            self.parent(),
            parent
        )
        editor.set_slider_visible(index.data(CustomDataRole.SliderVisability))

        editor.slider_visible_changed.connect(
            lambda visible: self.__on_slider_visible_changed(visible, index, editor)
        )

        return editor
    
    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        super().updateEditorGeometry(editor, option, index)
    
    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:
        super().setEditorData(editor, index)
    
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None:
        '''ReadOnly'''

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        wgt = FlowWidget(
            index.data(CustomDataRole.Id),
            index.data(CustomDataRole.Name),
            index.data(CustomDataRole.Description),
            index.data(CustomDataRole.SynonymsSet)[0],
            None,
            self.parent()
        )
        wgt.set_slider_visible(index.data(CustomDataRole.SliderVisability))
        wgt.resize(option.rect.size())

        painter.setClipRect(option.rect)

        painter.save()
        painter.drawPixmap(option.rect, wgt.grab())
        painter.restore()

        super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        wgt = FlowWidget(
            index.data(CustomDataRole.Id),
            index.data(CustomDataRole.Name),
            index.data(CustomDataRole.Description),
            index.data(CustomDataRole.SynonymsSet)[0],
            None
        )
        wgt.set_slider_visible(index.data(CustomDataRole.SliderVisability))
        wgt.adjustSize()
        return wgt.size()

class FlowsView(QTableView):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.__last_row = -1
        self.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.__delegate = FlowsDelegate(self)
        self.setItemDelegate(self.__delegate)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.setEditTriggers(QTableView.EditTrigger.AllEditTriggers)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        item = self.indexAt(event.pos())
        if self.isPersistentEditorOpen(item):
            self.closePersistentEditor(item)

        if item.isValid():
            self.setCurrentIndex(item)
            self.openPersistentEditor(item)

        return super().mouseMoveEvent(event)