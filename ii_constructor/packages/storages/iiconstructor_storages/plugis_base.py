from abc import ABC, ABCMeta, abstractmethod
from iiconstructor_storages.primitives import StorageType, Host, Auth

class StorageConnection(ABC):
    @abstractmethod
    @staticmethod
    def storage_type() -> StorageType: pass

    @abstractmethod
    def host(self) -> Host: pass

    @abstractmethod
    def open(self): pass

    @abstractmethod
    def close(self): pass

    @abstractmethod
    def is_open(self) -> bool: pass

class StoragePlugin(ABC):
    @abstractmethod
    @staticmethod
    def storage_type() -> StorageType: pass

    @abstractmethod
    @staticmethod
    def get_connection(host: Host, auth: Auth) -> StorageConnection: pass
