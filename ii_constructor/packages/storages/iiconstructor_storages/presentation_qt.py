from abc import ABC, ABCMeta
from PySide6.QtWidgets import(
    QWidget,
    QMainWindow,
    QStyledItemDelegate,
)

from PySide6.QtCore import Qt, QObject
from iiconstructor_storages.presentation_base import *

class AbstractQWidgetMeta(type(QWidget), ABCMeta):
    pass

class Wgt(QWidget, metaclass=AbstractQWidgetMeta):
    def __init__(self, parent: QWidget | None = None, f: Qt.WindowType = Qt.WindowType.Widget):
        super(Wgt, self).__init__(parent, f)

class StoragePluginViewWgt(StoragePluginView, Wgt):
    __data: StoragePluginViewModel

    def __init__(self, data, parent: QWidget | None = None):
        super(StoragePluginViewWgt, self).__init__(data)
        super(Wgt, self).__init__(parent)

class StoragePluginSelectWgt(StoragePluginSelector, Wgt):
    def __init__(self, parent = None, f = Qt.WindowType.Widget):
        super().__init__(parent, f)

    def show(self, items: set[StoragePluginView]):
        pass

    def select(self, item: StoragePluginView):
        pass

    def get_selected(self) -> StoragePluginViewModel:
        pass

    def next(self) -> StoragePluginView:
        pass

    def prev(self) -> StoragePluginView:
        pass

class StorageConnectionWgt(StorageConnectionView, Wgt):
    __data: StorageConnectionViewModel

    def __init__(self, data: StorageConnectionViewModel, parent: QWidget | None = None):
        super().__init__(data)
        super(Wgt).__init__(parent)

class StorageConnectionEditWgt(StorageConnectionConstructor, Wgt):
    def __init__(self, parent = None):
        super().__init__(parent)

    def get_value() -> StorageConnectionViewModel:
        pass

class StorageConnectionSelectWgt(StorageConnectionSelector, Wgt):
    def __init__(self, parent = None):
        super().__init__(parent)

    def show(self, items: set[StorageConnectionView]):
        pass

    def select(self, item: StorageConnectionView):
        pass

    def get_selected(self) -> StorageConnectionViewModel:
        pass

    def next(self) -> StorageConnectionView:
        pass

    def prev(self) -> StorageConnectionView:
        pass

    def count(self) -> int:
        pass

class StoragePluginConnectionsView(QStyledItemDelegate):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()