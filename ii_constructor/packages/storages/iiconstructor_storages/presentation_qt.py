from abc import ABC, ABCMeta
from PySide6.QtWidgets import(
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QMainWindow,
    QStackedWidget,
    QSplitter,
    QListView,
)

from PySide6.QtCore import(
    Signal,
    Slot,
    QAbstractItemModel,
    QModelIndex,
    QItemSelectionModel,
)

from PySide6.QtCore import Qt, QObject
from iiconstructor_storages.presentation_base import *

class StoragePluginsModel(QAbstractItemModel):
    __controller: StorageConnectionsController
    __plugins: list[StoragePluginViewModel]

    def __init__(self, controller: StorageConnectionsController, parent: QObject | None = None):
        super().__init__(parent)
        self.__controller = controller
        self.__plugins = list(self.__controller.available_plugins())

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.__plugins)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def index(self, row: int, column: int = 1, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        return self.createIndex(row, column, self.__plugins[row])

    def parent(self, index: QModelIndex) -> QModelIndex:
        return QModelIndex()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        _data: StoragePluginViewModel = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return _data.name

class StorageConnectionsModel(QAbstractItemModel):
    __controller: StorageConnectionsController
    __plugin: StoragePluginViewModel
    __use_display_role: bool

    def __init__(self, controller: StorageConnectionsController, plugin: StoragePluginViewModel, use_display_role: bool,parent: QObject | None = None):
        super().__init__(parent)
        self.__controller = controller
        self.__plugin = plugin
        self.__use_display_role = use_display_role

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.__controller.get_connections(self.__plugin))

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def index(self, row: int, column: int = 1, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        _conn_list = list(self.__controller.get_connections(self.__plugin))
        return self.createIndex(row, column, _conn_list[row])

    def parent(self, index: QModelIndex) -> QModelIndex:
        return QModelIndex()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        _data: StorageConnectionViewModel = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole and self.__use_display_role:
            return _data.host

class AbstractQWidgetMeta(type(QWidget), ABCMeta):
    pass

class Wgt(QWidget, metaclass=AbstractQWidgetMeta):
    def __init__(self, parent: QWidget | None = None, f: Qt.WindowType = Qt.WindowType.Widget):
        super(Wgt, self).__init__(parent, f)

class Label(QLabel):
    def __init__(self, parent: QWidget | None = None, f: Qt.WindowType = Qt.WindowType.Widget):
        super(Label, self).__init__(parent, f)

class AbstractQComboBoxMeta(type(QWidget), ABCMeta):
    pass

class Combo(QComboBox, metaclass=AbstractQComboBoxMeta):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

class StoragePluginViewWgt(StoragePluginView, Label):
    __data: StoragePluginViewModel

    def __init__(self, data: StoragePluginViewModel, parent: QWidget | None = None):
        super(StoragePluginViewWgt, self).__init__(data)
        super(Label, self).__init__(parent)
        self.setText(data.name)

class StoragePluginSelectCombo(StoragePluginSelector, Combo):
    def __init__(self, plugins: StoragePluginsModel, current: QModelIndex = QModelIndex(),
                 parent: QWidget | None = None, f = Qt.WindowType.Widget):
        super().__init__(parent)
        self.setModel(plugins)
        if current.isValid():
            self.setCurrentIndex(current.row())

    def get_selected(self) -> StoragePluginViewModel:
        return self.model().index(self.currentIndex(), 0).internalPointer()

class StoragePluginSelectWgt(StoragePluginSelector, Wgt):
    __model: StoragePluginsModel
    __selection_model: QItemSelectionModel

    def __init__(self, plugins: StoragePluginsModel, selection_model: QItemSelectionModel | None = None,
                 parent: QWidget | None = None, f = Qt.WindowType.Widget):
        super().__init__(parent)
        self.__model = plugins
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0,0,0,0)
        list_view = QListView(self)
        list_view.setModel(self.__model)
        list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)
        list_view.setSelectionBehavior(QListView.SelectionBehavior.SelectRows)
        list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        if selection_model is None:
            self.__selection_model = list_view.selectionModel()
        else:
            self.__selection_model = selection_model
            list_view.setSelectionModel(self.__selection_model)
        list_view.setCurrentIndex(self.__model.index(0))
        lay.addWidget(list_view)

    def get_selected(self) -> StoragePluginViewModel:
        return self.__selection_model.currentIndex().internalPointer()
    
    def selection_model(self) -> QItemSelectionModel:
        return self.__selection_model

class StorageConnectionWgt(StorageConnectionView, Wgt):
    __data: StorageConnectionViewModel

    def __init__(self, data: StorageConnectionViewModel, parent: QWidget | None = None):
        super().__init__(data)
        super(Wgt).__init__(parent)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(data.host, self))
        lay.addWidget(QLabel(data.login, self))

class StorageConnectionEditWgt(StorageConnectionConstructor, Wgt):
    __plugin_selector: StoragePluginSelector
    __host_edit: QLineEdit
    __login_edit: QLineEdit
    __password_edit: QLineEdit
    __ok_button: QPushButton

    accepted = Signal()

    def __init__(self, model: StoragePluginsModel, selection_model: QItemSelectionModel | None = None, parent: QWidget | None = None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("Создание нового подключения")
        cur_index = QModelIndex()
        if isinstance(selection_model, QItemSelectionModel):
            cur_index = selection_model.currentIndex()
        self.__plugin_selector = StoragePluginSelectCombo(model, cur_index, self)
        self.__host_edit = QLineEdit(self)
        self.__login_edit = QLineEdit(self)
        self.__password_edit = QLineEdit(self)
        self.__ok_button = QPushButton("Добавить", self)
        self.__ok_button.setStyleSheet(
            "QPushButton{background-color: #59A5FF; border: none;}"
            "QPushButton:hover{background-color: #59A5FF; border: 1px solid black;}"
        )

        self.__host_edit.setPlaceholderText("адрес")
        self.__login_edit.setPlaceholderText("логин")
        self.__password_edit.setPlaceholderText("пароль")
        self.__password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        lay = QVBoxLayout(self)
        lay.addWidget(self.__plugin_selector)
        lay.addWidget(self.__host_edit)
        lay.addWidget(self.__login_edit)
        lay.addWidget(self.__password_edit)
        lay.addWidget(self.__ok_button)

        self.__ok_button.clicked.connect(lambda: self.accepted.emit())

    def get_value(self) -> StorageConnectionViewModel:
        return StorageConnectionViewModel(
            self.__host_edit.text(),
            self.__login_edit.text(),
            self.__password_edit.text(),
            self.__plugin_selector.get_selected().name,
            self.__plugin_selector.get_selected().inmem
        )

class StorageConnectionSelectWgt(StorageConnectionSelector, Wgt):
    __model: StorageConnectionsModel
    __selection_model: QItemSelectionModel

    def __init__(self, model: StorageConnectionsModel, parent: QWidget | None = None):
        super().__init__(parent)
        self.__model = model

        lay = QVBoxLayout(self)
        list_view = QListView(self)
        list_view.setModel(self.__model)
        list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)
        list_view.setSelectionBehavior(QListView.SelectionBehavior.SelectRows)
        list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.__selection_model = list_view.selectionModel()
        list_view.setCurrentIndex(self.__model.index(0))
        lay.addWidget(list_view)

    def get_selected(self) -> StorageConnectionViewModel:
        return self.__selection_model.currentIndex().internalPointer()

class StoragePluginConnectionsWgt(QWidget):
    __connestions_observer: QStackedWidget
    __plugins_selector: StoragePluginSelectWgt
    __controller: StorageConnectionsController

    __plugins_model: StoragePluginsModel
    __new_connection_btn: QPushButton

    def __init__(self, controller: StorageConnectionsController, parent: QObject | None = None):
        # инициализация родителей
        super().__init__(parent)
        
        # собственная инициализация 
        self.__controller = controller
        self.__plugins_model = StoragePluginsModel(self.__controller, self)
        self.__plugins_selector = StoragePluginSelectWgt(self.__plugins_model, None, self)
        self.__connestions_observer = QStackedWidget(self)
        self.__new_connection_btn = QPushButton("новое подключение", self)
        self.__new_connection_btn.clicked.connect(self.on_create_connection_clicked)

        conn_wrapper = QWidget(self)
        conn_lay = QVBoxLayout(conn_wrapper)
        conn_lay.addWidget(self.__connestions_observer)
        conn_lay.addWidget(self.__new_connection_btn)

        # формирование макета
        main_lay = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(self.__plugins_selector)
        splitter.addWidget(conn_wrapper)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([1,1])
        main_lay.addWidget(splitter)

        # нстройка внешнего вида
        #self.setStyleSheet("background-color: red;")
        main_lay.setContentsMargins(0,0,0,0)

        #splitter.setStyleSheet("background-color: yellow;")
        splitter.setHandleWidth(0)

        #self.__plugins_selector.setStyleSheet("background-color: blue;")
        #self.__plugins_selector.setMinimumWidth(150)

        conn_lay.setContentsMargins(0,0,0,0)
        conn_lay.setSpacing(0)

        #self.__connestions_observer.setStyleSheet("background-color: green;")
        self.__new_connection_btn.setStyleSheet("background-color: white;")

    @Slot()
    def on_create_connection_clicked(self):
        self.__dialog = StorageConnectionEditWgt(self.__plugins_model, self.__plugins_selector.selection_model(), self)
        self.__dialog.show()

class MainWindow(QMainWindow):
    def __init__(self, controller: StorageConnectionsController):
        super().__init__()
        self.setCentralWidget(StoragePluginConnectionsWgt(controller, self))
        self.resize(640, 480)
        self.setWindowTitle("Управление подключениями к источникам данных")
