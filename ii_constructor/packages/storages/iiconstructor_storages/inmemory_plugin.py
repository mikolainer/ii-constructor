from abc import ABCMeta, abstractmethod
from iiconstructor_storages.primitives import StorageType, Host, Auth
from iiconstructor_storages.plugis_base import StorageConnection, StoragePlugin

class InmemoryStorateType(StorageType):
    def __init__(self):
        super().__init__("inmemory", True)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class InmemoryStorageConnection(StorageConnection, metaclass=Singleton):
    @staticmethod
    def storage_type() -> StorageType:
        return InmemoryStorateType()
    
    def host(self) -> Host:
        return Host("inmemory")

    def open(self):
        return None

    def close(self):
        return None

    def is_open(self) -> bool:
        return True
    
class InmemoryStoragePlugin(StoragePlugin, metaclass=ABCMeta):
    @staticmethod
    def storage_type() -> StorageType:
        return InmemoryStorageConnection.storage_type()
    
    @abstractmethod
    @staticmethod
    def get_connection(host: Host = None, auth: Auth = None) -> InmemoryStorageConnection:
        pass