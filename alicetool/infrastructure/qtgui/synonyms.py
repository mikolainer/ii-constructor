from typing import Callable, Optional

from PySide6.QtCore import (
    Qt,
    QPoint,
    Slot,
    Signal,
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
    QContextMenuEvent,
    QResizeEvent,
    QMouseEvent,
    QMouseEvent,
    QPainter,
    QFont,
    QAction,
    QKeySequence,
    QShortcut,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QSplitter,
    QSpacerItem,
    QSpacerItem,
    QDialog,
    QLabel,
    QLineEdit,
    QScrollArea,
    QStackedWidget,
    QStyleOptionViewItem,
    QWidget,
    QStyledItemDelegate,
    QListView,
    QTableView,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QListView,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QMenu,
)

from .data import CustomDataRole, BaseModel, SynonymsSetModel, ProxyModelReadOnly
from .primitives.buttons import CloseButton
from .primitives.widgets import SynonymEditorWidget

class SynonymsGroupsModel(BaseModel):
    ''' Модель групп синонимов. Реализация части MVC фреймворка Qt для набора синонимов в редакторе синонимов '''
    def __init__( self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._data_init(
            index_roles=[CustomDataRole.Name],
            required_roles=[
                CustomDataRole.Name,
                CustomDataRole.SynonymsSet
            ]
        )

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

class SynonymsGroupWidget(QWidget):
    ''' Единица списка групп синонимов. Отображение элемента модели групп синонимов '''
    __title: QLabel
    __description: QLabel
    
    def name(self) -> str:
        return self.__title.text()
    
    def description(self) -> str:
        return self.__description.text()

    def __init__(self, name:str, description: str, parent: QWidget = None):
        super().__init__(parent)

        self.setStyleSheet('QWidget{background-color: #FFFFFF; border: 2px solid #FFFFFF;}')
        main_lay = QVBoxLayout(self)

        self.__title = QLabel(name, self)
        self.__title.setMinimumHeight(30)
        font = self.__title.font()
        font.setBold(True)
        self.__title.setFont(font)
        main_lay.addWidget(self.__title)

        self.__description = QLabel(description, self)
        self.__description.setMinimumHeight(30)
        main_lay.addWidget(self.__description)

        main_lay.setContentsMargins(5,0,5,0)
    
class SynonymsGroupsDelegate(QStyledItemDelegate):
    ''' Реализация части MVC фреймворка Qt для групп синонимов '''
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        data = index.internalPointer()
        wgt = SynonymsGroupWidget(data.on[CustomDataRole.Name], data.on[CustomDataRole.Description])
        wgt.resize(option.rect.size())

        painter.setClipRect(option.rect)

        painter.save()
        painter.drawPixmap(option.rect, wgt.grab())
        painter.restore()

        super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        data = index.internalPointer()
        wgt = SynonymsGroupWidget(data.on[CustomDataRole.Name], data.on[CustomDataRole.Description])
        wgt.adjustSize()
        return wgt.size()

class SynonymsGroupsView(QListView):
    ''' Реализация части MVC фреймворка Qt для групп синонимов '''
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.__delegate = SynonymsGroupsDelegate(self)
        self.setItemDelegate(self.__delegate)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)

        shotcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        shotcut.activated.connect(self.remove_selected_row)

    on_selectionChanged = Signal(QItemSelection, QItemSelection)

    def remove_selected_row(self):
        for index in self.selectedIndexes():
            self.__remove_row(index)

    def __remove_row(self, index:QModelIndex):
        if not self.model().removeRow(index.row()):
            QMessageBox.warning(self, 'Невозможно выполнить', 'Невозможно удалить выбранный вектор. Он используется в существующих переходах!')

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        self.on_selectionChanged.emit(selected, deselected)
        return super().selectionChanged(selected, deselected)
    
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        menu = QMenu(self)
        menu.addAction('Удалить', lambda: self.__remove_row(index), QKeySequence(QKeySequence.StandardKey.Delete))
        menu.move(event.globalPos())
        menu.show()

class SynonymsSetDelegate(QStyledItemDelegate):
    ''' Реализация части MVC фреймворка Qt для набора синонимов в группе '''
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
        #super().setModelData(editor, model, index)
        model.setData(index, editor.text())

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        data = index.data(CustomDataRole.Text)
        wgt = SynonymEditorWidget(data)
        wgt.resize(option.rect.size())

        painter.setClipRect(option.rect)

        painter.save()
        painter.drawPixmap(option.rect, wgt.grab())
        painter.restore()

        super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        data = index.data(CustomDataRole.Text)
        wgt = SynonymEditorWidget(data)
        wgt.adjustSize()
        return wgt.size()

class SynonymsSetView(QListView):
    ''' Реализация части MVC фреймворка Qt для набора синонимов в группе '''
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.__delegate = SynonymsSetDelegate(self)
        self.setItemDelegate(self.__delegate)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)

    def sizeHint(self) -> QSize:
        size = super().sizeHint()
        temp_w = SynonymEditorWidget('some text')
        temp_w.adjustSize()
        item_height = temp_w.height()
        size.setHeight(self.model().rowCount() * item_height)
        return size

class GroupsList(QStackedWidget):
    ''' Обёртка для набора синонимов в группе'''
    # TODO: изменить наследование на ассоциацию?
    
    __indexed: dict[int, SynonymsGroupsView]
    __empty_index:int
    create_value = Signal(SynonymsGroupsModel)

    def addWidget(self, w: SynonymsGroupsView) -> int:
        if not isinstance(w, SynonymsGroupsView):
            raise TypeError(w)

        wrapper = QWidget(self)
        w_lay = QVBoxLayout(wrapper)
        w_lay.addWidget(w, 0)

        create_btn = QPushButton("Новая группа", self)
        create_btn.clicked.connect(lambda: self.create_value.emit(w.model()))
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
        ''' Показать заглушку '''
        self.setCurrentIndex(self.__empty_index)
    
    def setList(self, view: SynonymsGroupsView, set_current: bool = False):
        # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not view in self.__indexed.values():
            self.__indexed[self.addWidget(view)] = view

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(view)]

        # если указано - устанавливаем текущим виджетом
        if set_current:
            self.setCurrentIndex(idx)

class SynonymsList(QStackedWidget):
    ''' Обёртка для списка групп синонимов '''
    __indexed: dict[int, SynonymsSetModel]
    __empty_index:int
    create_value = Signal(SynonymsSetModel)

    def addWidget(self, w: SynonymsSetView) -> int:
        if not isinstance(w, SynonymsSetView):
            raise TypeError(w)

        wrapper = QWidget(self)
        w_lay = QVBoxLayout(wrapper)
        w_lay.addWidget(w, 0)

        create_btn = QPushButton("Новое значение", self)
        create_btn.clicked.connect(lambda: self.create_value.emit(w.model()))
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
        ''' Показать заглушку '''
        self.setCurrentIndex(self.__empty_index)
    
    def set_current(self, model: SynonymsSetModel):
        # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not model in self.__indexed.values():
            view = SynonymsSetView(self)
            view.setModel(model)
            self.__indexed[self.addWidget(view)] = model

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(model)]
        self.setCurrentIndex(idx)

class SynonymsEditor(QDialog):
    ''' Редактор синонимов. Содержит список групп синонимов (слева) и набор синонимов в выбранной группе (справа) '''
    __oldPos: QPoint | None
    __tool_bar: QWidget # полоска с кнопкой "закрыть"
    __close_btn: CloseButton

    __synonyms_list: SynonymsList
    __group_list: GroupsList

    __g_model:SynonymsGroupsModel
    __create_group_handler:Callable
    __create_value_handler:Callable

    def __init__(
            self, g_model:SynonymsGroupsModel,
            create_group_handler:Callable[[SynonymsGroupsModel], None],
            create_value_handler:Callable[[SynonymsSetModel], None],
            parent: QWidget | None = None
        ) -> None:
        self.__g_model = g_model
        self.__create_group_handler = create_group_handler
        self.__create_value_handler = create_value_handler

        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.Window, True)

        self.setWindowTitle('Редактор синонимов')
        self.resize(600, 500)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        # полоска с кнопкой закрыть
        self.__tool_bar = QWidget(self)
        self.__tool_bar.setMinimumHeight(24)
        main_lay.addWidget(self.__tool_bar, 0)
        self.__tool_bar.setStyleSheet('background-color : #666;')
        self.__oldPos = None

        tool_bar_layout = QHBoxLayout(self.__tool_bar)
        tool_bar_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        tool_bar_layout.setSpacing(10)
        tool_bar_layout.setContentsMargins(2, 2, 2, 2)
        tool_bar_layout.addSpacerItem(
            QSpacerItem(
                0,0,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            )
        )

        self.__close_btn = CloseButton(self)
        self.__close_btn.clicked.connect(lambda: self.close())
        tool_bar_layout.addWidget(self.__close_btn)

        self.__group_list = GroupsList(self)
        self.__group_list.create_value.connect(lambda model: self.__create_group_handler(model))
        
        g_view = SynonymsGroupsView(self)
        g_view.setModel(g_model)
        self.__group_list.setList(g_view, True)

        self.__synonyms_list = SynonymsList(self)
        self.__synonyms_list.create_value.connect(lambda model: self.__create_value_handler(model))
        self.__synonyms_list.set_empty()

        g_view.selectionModel().selectionChanged.connect(
            lambda now, prev: self.__on_syn_group_changed(now.indexes())
        )

        # рабочая область
        splitter = QSplitter( self, Qt.Orientation.Horizontal )
        splitter.addWidget(self.__group_list)
        splitter.setStretchFactor(0,0)
        splitter.addWidget(self.__synonyms_list)
        splitter.setStretchFactor(1,1)
        
        main_lay.addWidget(splitter, 1)

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

    def resizeEvent(self, event: QResizeEvent) -> None:
        # костыль
        if event.oldSize() != event.size():
            self.resize(event.size())

        return super().resizeEvent(event)
    
    @Slot(list)
    def __on_syn_group_changed(self, selected_index_list):
        if len(selected_index_list):
            synonyms = self.__g_model.data(
                selected_index_list[0],
                CustomDataRole.SynonymsSet
            )
            self.__synonyms_list.set_current(synonyms)

class SynonymsGroupWidgetToSelect(QWidget):
    ''' Внутренний виджет для отображения элемента модели в окне выбора существующего набора синонимов '''
    def __init__(self, name: str, synonyms_set_model:SynonymsSetModel, parent: QWidget = None):
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
    ''' Реализация части MVC фреймворка Qt для окна выбора существующего набора синонимов '''
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget:
        return SynonymsGroupWidgetToSelect(
            index.data(CustomDataRole.Name),
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
            data.on[CustomDataRole.SynonymsSet]
        )
        wgt.setStyleSheet('background-color: #666;')
        wgt.adjustSize()
        return wgt.size()
    
class SynonymsSelectorView(QListView):
    ''' Реализация части MVC фреймворка Qt для окна выбора существующего набора синонимов '''
    item_selected = Signal(str)
    __selected: bool

    def __init__(self, parent: QWidget | None = None) -> None:
        self.__selected = False
        super().__init__(parent)

        self.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.setItemDelegate(SynonymsSelectorDelegate(self))
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)

        #self.resize(600, 400)
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
            self.item_selected.emit(item.data(CustomDataRole.Name))
            self.setCursor(Qt.CursorShape.BusyCursor)
            self.__selected = True

        return super().mouseDoubleClickEvent(event)
    
    def accept(self):
        self.close()

    def decline(self):
        self.unsetCursor()
        self.__selected = False


class SynonymsSelector(QDialog):
    __g_model:SynonymsGroupsModel
    __create_group_handler:Callable[[SynonymsGroupsModel], None]

    __selected_name: str

    create_value = Signal(SynonymsGroupsModel)

    def __init__(self, g_model:SynonymsGroupsModel, create_group_handler:Callable[[SynonymsGroupsModel], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self.__selected_name = None
        self.__g_model = g_model
        self.__create_group_handler = create_group_handler

        main_lay = QVBoxLayout(self)
        view = SynonymsSelectorView(self)
        view.setModel(self.__g_model)
        main_lay.addWidget(view, 1)

        create_btn = QPushButton("Новое значение", self)
        create_btn.clicked.connect(lambda: self.__create_group_handler(view.model()))
        main_lay.addWidget(create_btn, 1)

        view.item_selected.connect(self.__selected)

        self.resize(600, 400)

    @Slot(str)
    def __selected(self, name:str):
        self.__selected_name = name
        self.accept()

    def selected_item(self) -> Optional[SynonymsSetModel]:
        g_item = self.__g_model.get_item_by(CustomDataRole.Name, self.__selected_name)

        if g_item is None:
            return None
        else:
            return g_item.on[CustomDataRole.SynonymsSet]