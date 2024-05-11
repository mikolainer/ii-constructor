from typing import List
from PySide6.QtCore import (
    QAbstractItemModel,
    QItemSelection,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QSize,
    Signal,
    Slot,
    Qt,
)

from PySide6.QtGui import (
    QMouseEvent,
    QPainter,
    QFont,
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
    QPushButton,
    QListView,
    QHBoxLayout,
    QGraphicsProxyWidget,
    QLabel,
    QVBoxLayout,
    QInputDialog,
)

from .data import CustomDataRole, SynonymsSetModel, ProxyModelReadOnly, SynonymsGroupsModel
from .widgets import SynonymsGroupWidget, SynonymEditorWidget

class FlowSynonymsSetDelegate(QStyledItemDelegate):
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget:
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:
        editor.setText(index.data())

class FlowSynonymsSetView(QListView):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setItemDelegate(FlowSynonymsSetDelegate(self))

class FlowWidget(QWidget):
    __id: int
    __title: QLabel
    __description: QLabel
    __synonyms_name: QLabel
    __synonyms_list: FlowSynonymsSetView
    __slider_btn: QPushButton

    def id(self): return self.__id
    def name(self): return self.__title.text()

    slider_visible_changed = Signal(bool)

    def set_slider_visible(self, visible:bool):
        self.__on_slider_click(visible)

    @Slot()
    def __on_slider_click(self, checked: bool):
        self.__slider_btn.setText("^" if checked else "v")
        self.__synonyms_list.setVisible(checked)

        if not self.sender() is self:
            self.slider_visible_changed.emit(checked)


    def __init__(self, id :int, 
                 name: str, description :str,
                 synonyms: SynonymsSetModel, 
                 start_state :QGraphicsProxyWidget,
                 parent = None
                ):
        super().__init__(parent)
        self.setStyleSheet("border: 1px solid black; background-color: #DDDDDD;")
        self.__id = id
        self.__title = QLabel(name, self)
        self.__title.setWordWrap(True)
        self.__description = QLabel(description, self)
        self.__description.setWordWrap(True)
        self.__synonyms_name = QLabel("синонимы", self)
        self.__synonyms_list = FlowSynonymsSetView(self)
        self.__synonyms_list.hide()
        self.__synonyms_list.setModel(synonyms)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        synonyms_wrapper = QWidget(self)
        synonyms_lay = QVBoxLayout(synonyms_wrapper)

        synonyms_title_lay = QHBoxLayout()
        synonyms_title_lay.addWidget(self.__synonyms_name)
        self.__slider_btn = QPushButton('v', self)
        self.__slider_btn.setCheckable(True)
        self.__slider_btn.clicked.connect(self.__on_slider_click)
        synonyms_title_lay.addWidget(self.__slider_btn)

        synonyms_lay.addLayout(synonyms_title_lay)
        synonyms_lay.addWidget(self.__synonyms_list)

        main_lay.addWidget(self.__title)
        main_lay.addWidget(self.__description)
        main_lay.addWidget(synonyms_wrapper)
    
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
        editor.setText(index.data())
    
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None:
        super().setModelData(editor, model, index)
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

class GroupsList(QStackedWidget):
    __indexed: dict[int, SynonymsGroupsView]
    __empty_index:int

    def create_value(self, view: SynonymsGroupsView):
        model:SynonymsGroupsModel = view.model()

        name, ok = QInputDialog.getText(self, "Имя новой группы", "Имя новой группы:")
        if not ok: return

        descr, ok = QInputDialog.getText(self, "Описание новой группы", "Описание новой группы:")
        if not ok: return

        value, ok = QInputDialog.getText(self, "Значение первого синонима", "Первый синоним:")
        if not ok: return

        new_row:int = model.rowCount()
        model.insertRow(new_row)
        index = model.index(new_row)
        model.setData(index, name, CustomDataRole.Name)
        model.setData(index, descr, CustomDataRole.Description)
        model.setData(index, SynonymsSetModel([value]), CustomDataRole.SynonymsSet)

    def addWidget(self, w: SynonymsGroupsView) -> int:
        if not isinstance(w, SynonymsGroupsView):
            raise TypeError(w)

        wrapper = QWidget(self)
        w_lay = QVBoxLayout(wrapper)
        w_lay.addWidget(w, 0)

        create_btn = QPushButton("Новая группа", self)
        create_btn.clicked.connect(lambda: self.create_value(w))
        w_lay.addWidget(create_btn, 1)

        area = QScrollArea(self)
        area.setWidgetResizable(True)
        area.setWidget(wrapper)

        return super().addWidget(area)
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__indexed = {}
        self.__empty_index = super().addWidget(QWidget(self))
        self.resize(200, self.height())

    def set_empty(self):
        self.setCurrentIndex(self.__empty_index)
    
    def setList(self, view: SynonymsGroupsView, set_current: bool = False):
        ''' обновление списка виджетов '''
        # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not view in self.__indexed.values():
            self.__indexed[self.addWidget(view)] = view

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(view)]

        # если указано - устанавливаем текущим виджетом
        if set_current:
            self.setCurrentIndex(idx)

class SynonymsList(QStackedWidget):
    __indexed: dict[int, SynonymsSetView]
    __empty_index:int

    def create_value(self, view: SynonymsSetView):
        model:SynonymsSetModel = view.model()

        value, ok = QInputDialog.getText(self, "Новое значение", "Новый синоним:")
        if not ok: return

        new_row:int = model.rowCount()
        model.insertRow(new_row)
        model.setData(model.index(new_row), value)

    def addWidget(self, w: SynonymsSetView) -> int:
        if not isinstance(w, SynonymsSetView):
            raise TypeError(w)

        wrapper = QWidget(self)
        w_lay = QVBoxLayout(wrapper)
        w_lay.addWidget(w, 0)

        create_btn = QPushButton("Новое значение", self)
        create_btn.clicked.connect(lambda: self.create_value(w))
        w_lay.addWidget(create_btn, 1)

        area = QScrollArea(self)
        area.setWidgetResizable(True)
        area.setStyleSheet('QScrollArea{background-color: #FFFFFF; border: none;}')
        area.setWidget(wrapper)
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

    def __on_slider_visible_changed(self, visible:bool, index:QModelIndex, editor:FlowWidget):
        index.model().setData(
            index, visible, CustomDataRole.SliderVisability
        )
        editor.adjustSize()
        self.parent().setRowHeight(index.row(), editor.height())

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget:
        editor = FlowWidget(
            index.data(CustomDataRole.Id),
            index.data(CustomDataRole.Name),
            index.data(CustomDataRole.Description),
            index.data(CustomDataRole.SynonymsSet),
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
            index.data(CustomDataRole.SynonymsSet),
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
            index.data(CustomDataRole.SynonymsSet),
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

class SynonymsGroupWidgetToSelect(QWidget):
    def __init__(self, name: str, id: int, description: str, synonyms_set_model:SynonymsSetModel, parent: QWidget = None):
        super().__init__(parent)
        main_lay: QVBoxLayout = QVBoxLayout(self)

        title:QLabel = QLabel(name, self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setAutoFillBackground(True)
        title_font:QFont = title.font()
        title_font.setBold(True)
        title.setFont(title_font)
        main_lay.addWidget(title)

        synonyms_list = QListView(self)
        synonyms_list.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        model = ProxyModelReadOnly(self)
        model.setSourceModel(synonyms_set_model)
        synonyms_list.setModel(model)
        synonyms_list.setMaximumHeight(50)
        main_lay.addWidget(synonyms_list)

class SynonymsSelectorDelegate(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget:
        return SynonymsGroupWidgetToSelect(
            index.data(CustomDataRole.Name),
            index.data(CustomDataRole.Id),
            index.data(CustomDataRole.Description),
            index.data(CustomDataRole.SynonymsSet),
            parent
        )
    
    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        super().updateEditorGeometry(editor, option, index)
    
    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:
        super().setEditorData(editor, index)
    
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None:
        '''ReadOnly'''

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        data = index.internalPointer()
        wgt = SynonymsGroupWidgetToSelect(
            data.on[CustomDataRole.Name],
            data.on[CustomDataRole.Id],
            data.on[CustomDataRole.Description],
            data.on[CustomDataRole.SynonymsSet]
        )
        wgt.resize(option.rect.size())

        painter.setClipRect(option.rect)

        painter.save()
        painter.drawPixmap(option.rect, wgt.grab())
        painter.restore()

        super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        data = index.internalPointer()
        wgt = SynonymsGroupWidgetToSelect(
            data.on[CustomDataRole.Name],
            data.on[CustomDataRole.Id],
            data.on[CustomDataRole.Description],
            data.on[CustomDataRole.SynonymsSet]
        )
        wgt.setStyleSheet('background-color: #666;')
        wgt.adjustSize()
        return wgt.size()
    
class SynonymsSelectorView(QListView):
    item_selected = Signal(int)
    __selected: bool

    def __init__(self, parent: QWidget | None = None) -> None:
        self.__selected = False
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Window, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.setItemDelegate(SynonymsSelectorDelegate(self))
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)

        self.resize(600, 400)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        item = self.indexAt(event.pos())
        if self.isPersistentEditorOpen(item):
            self.closePersistentEditor(item)

        if item.isValid():
            self.setCurrentIndex(item)
            self.openPersistentEditor(item)

        return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        item = self.indexAt(event.pos())
        if item.isValid() and not self.__selected:
            self.item_selected.emit(item.data(CustomDataRole.Id))
            self.setCursor(Qt.CursorShape.BusyCursor)
            self.__selected = True

        return super().mouseDoubleClickEvent(event)
    
    def accept(self):
        self.close()

    def decline(self):
        self.unsetCursor()
        self.__selected = False

