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
    def get_selected(self) -> StoragePluginViewModel:
        pass

class StorageConnectionView:
    __data: StorageConnectionViewModel

    def __init__(self, data: StorageConnectionViewModel):
        setattr(self, "_StorageConnectionView__data", data)

    def _data(self) -> StoragePluginViewModel:
        return getattr(self, "_StorageConnectionView__data")

class StorageConnectionConstructor(ABC):
    @abstractmethod
    def get_value(self) -> StorageConnectionViewModel:
        pass

class StorageConnectionSelector(ABC):
    @abstractmethod
    def get_selected(self) -> StorageConnectionViewModel:
        pass
