from abc import ABC, abstractmethod
from iiconstructor_storages.operations import (
    StorageConnectionsController,
    StorageConnectionViewModel,
    StoragePluginViewModel,
)

class StoragePluginView:
    __data: StoragePluginViewModel

    def __init__(self, data: StoragePluginViewModel):
        setattr(self, "_StoragePluginView__data", data)

    def _data(self) -> StoragePluginViewModel:
        return getattr(self, "_StoragePluginView__data")

class StoragePluginSelector(ABC):
    @abstractmethod
    def show(self, items: set[StoragePluginView]):
        pass

    @abstractmethod
    def select(self, item: StoragePluginView):
        pass

    @abstractmethod
    def get_selected(self) -> StoragePluginViewModel:
        pass

    @abstractmethod
    def next(self) -> StoragePluginView:
        pass

    @abstractmethod
    def prev(self) -> StoragePluginView:
        pass

class StorageConnectionView:
    __data: StorageConnectionViewModel

    def __init__(self, data: StorageConnectionViewModel):
        setattr(self, "_StorageConnectionView__data", data)

    def _data(self) -> StoragePluginViewModel:
        return getattr(self, "_StorageConnectionView__data")

class StorageConnectionConstructor(ABC):
    @abstractmethod
    def get_value() -> StorageConnectionViewModel:
        pass

class StorageConnectionSelector(ABC):
    @abstractmethod
    def show(self, items: set[StorageConnectionView]):
        pass

    @abstractmethod
    def select(self, item: StorageConnectionView):
        pass

    @abstractmethod
    def get_selected(self) -> StorageConnectionViewModel:
        pass

    @abstractmethod
    def next(self) -> StorageConnectionView:
        pass

    @abstractmethod
    def prev(self) -> StorageConnectionView:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
