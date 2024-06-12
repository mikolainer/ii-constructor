from typing import List
from PySide6.QtCore import (
    Qt,
    QAbstractItemModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QSize,
    Signal,
    Slot,
)

from PySide6.QtGui import (
    QMouseEvent,
    QPainter,
)

from PySide6.QtWidgets import (
    QStyleOptionViewItem,
    QWidget,
    QStyledItemDelegate,
    QListView,
    QTableView,
    QHeaderView,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QInputDialog,
)

from .data import CustomDataRole, BaseModel, SynonymsSetModel
from .primitives.widgets import SynonymEditorWidget

class FlowsModel(BaseModel):
    ''' Модель содержания проекта. Реализация части MVC фреймворка Qt для содержания проекта '''
    def __init__( self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._data_init() # TODO

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
class FlowWidget(QWidget):
    ''' Единица содержания проекта. Отображение элемента модели содержания '''
    __id: int
    __title: QLabel
    __description: QLabel
    __synonyms_name: QLabel
    __synonyms_list: 'FlowSynonymsSetView'
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
                 start_state,# :QGraphicsProxyWidget,
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
        self.__synonyms_list = FlowSynonymsSetView(self)#FlowSynonymsSetView(self)
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
class FlowListWidget(QWidget):
    ''' Обёртка содержания. Уникальная и единственная для проекта. '''
    __view: QWidget

    '''args: name, descr'''
    create_value = Signal(str, str) 

    @Slot()
    def __create_flow(self):
        name, ok = QInputDialog.getText(self, "Имя нового потока", "Имя нового потока:")
        if not ok: return

        descr, ok = QInputDialog.getText(self, "Описание нового потока", "Описание нового потока:")
        if not ok: return

        self.create_value.emit(name, descr)

    def __init__(self, view: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(3,3,0,3)

        lay.addWidget(view, 0)

        btn = QPushButton("+", self)
        btn.clicked.connect(self, self.__create_flow)
        lay.addWidget(btn, 1)

class FlowSynonymsSetDelegate(QStyledItemDelegate):
    ''' Реализация части MVC фреймворка Qt для набора синонимов в содержании проекта '''
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget:
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex | QPersistentModelIndex) -> None:
        editor.setText(index.data())

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        data = index.data(CustomDataRole.Text)
        wgt = SynonymEditorWidget(data)
        wgt.adjustSize()
        return QSize(option.rect.size().width(), wgt.size().height())
    
class FlowSynonymsSetView(QListView):
    ''' Реализация части MVC фреймворка Qt для набора синонимов в содержании проекта '''
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setItemDelegate(FlowSynonymsSetDelegate(self))

class FlowsDelegate(QStyledItemDelegate):
    ''' Реализация части MVC фреймворка Qt для содержания проекта '''
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
    ''' Реализация части MVC фреймворка Qt для содержания проекта '''
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
