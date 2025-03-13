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
    def __init__(self, controller: StorageConnectionsController, parent: QObject | None = None):
        super().__init__(parent)

class StorageConnectionsModel(QAbstractItemModel):
    def __init__(self, controller: StorageConnectionsController, plugin: StoragePluginViewModel, parent: QObject | None = None):
        super().__init__(parent)

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
        super(Combo).__init__(parent)

class StoragePluginViewWgt(StoragePluginView, Label):
    __data: StoragePluginViewModel

    def __init__(self, data: StoragePluginViewModel, parent: QWidget | None = None):
        super(StoragePluginViewWgt, self).__init__(data)
        super(Label, self).__init__(parent)
        self.setText(data.name)

class StoragePluginSelectCombo(StoragePluginSelector, Combo):
    def __init__(self, plugins: StoragePluginsModel, parent: QWidget | None = None, f = Qt.WindowType.Widget):
        super().__init__(parent)
        self.setModel(plugins)

    def get_selected(self) -> StoragePluginViewModel:
        return self.model().index(self.currentIndex(), 0).internalPointer()

class StoragePluginSelectWgt(StoragePluginSelector, Wgt):
    __model: StoragePluginsModel
    __selection_model: QItemSelectionModel

    def __init__(self, plugins: StoragePluginsModel, 
                 parent: QWidget | None = None, f = Qt.WindowType.Widget):
        super().__init__(parent)
        self.__model = plugins
        self.__selection_model = QItemSelectionModel(self.__model, self)
        azaza =QWidget(self)
        # TODO: создать отображение

    def get_selected(self) -> StoragePluginViewModel:
        return self.__selection_model.currentIndex().internalPointer()

class StorageConnectionWgt(StorageConnectionView, Wgt):
    __data: StorageConnectionViewModel

    def __init__(self, data: StorageConnectionViewModel, parent: QWidget | None = None):
        super().__init__(data)
        super(Wgt).__init__(parent)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(data.host, self))
        lay.addWidget(QLabel(data.login, self))

class StorageConnectionEditWgt(StorageConnectionConstructor, Wgt):
    __host_edit: QLineEdit
    __login_edit: QLineEdit
    __password_edit: QLineEdit
    __ok_button: QPushButton
    __plugin_selector: StoragePluginSelector

    accepted = Signal()

    def __init__(self, model: StoragePluginsModel, parent: QWidget | None = None):
        super().__init__(parent)
        self.__plugin_selector = StoragePluginSelectCombo(model)
        self.__host_edit = QLineEdit(self)
        self.__login_edit = QLabel(self)
        self.__password_edit = QLabel(self)
        self.__ok_button = QPushButton(self)

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
        self.__selection_model = QItemSelectionModel(model, self)
        # TODO: создать отображение

    def get_selected(self) -> StorageConnectionViewModel:
        return self.__selection_model.currentIndex().internalPointer()

class StoragePluginConnectionsWgt(QWidget):
    __connestions_observer: QStackedWidget
    __plugins_selector: StoragePluginSelectWgt
    __controller: StorageConnectionsController

    __plugins_model: StoragePluginsModel
    __new_connection_btn: QPushButton

    def __init__(self, controller: StorageConnectionsController, parent: QObject | None = None):
        super().__init__(parent)
        self.__controller = controller
        main_lay = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.__plugins_model = StoragePluginsModel(self.__controller, self)
        self.__plugins_selector = StoragePluginSelectWgt(self.__plugins_model, self)
        self.__connestions_observer = QStackedWidget(self)
        self.__new_connection_btn = QPushButton("новое подключение", self)

        splitter.addWidget(self.__plugins_selector)
        #splitter.addWidget(self.__connestions_observer)
        conn_wrapper = QWidget(self)
        conn_lay = QVBoxLayout(conn_wrapper)
        conn_lay.addWidget(self.__connestions_observer)
        conn_lay.addWidget(self.__new_connection_btn)
        splitter.addWidget(conn_wrapper)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([1,1])
        main_lay.addWidget(splitter)
        # TODO: создать виджеты выбора подключений в self.__connestions_observer
        # TODO: подключить изменение активного виджета в self.__connestions_observer
        self.setStyleSheet("background-color: red;")
        splitter.setStyleSheet("background-color: yellow;")
        self.__plugins_selector.setStyleSheet("background-color: blue;")
        self.__connestions_observer.setStyleSheet("background-color: green;")

class MainWindow(QMainWindow):
    def __init__(self, controller: StorageConnectionsController):
        super().__init__()
        self.setCentralWidget(StoragePluginConnectionsWgt(controller, self))