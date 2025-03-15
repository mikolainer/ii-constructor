from abc import ABCMeta, abstractmethod
from iiconstructor_storages.primitives import StorageType, Host, Auth
from iiconstructor_storages.plugis_base import StorageConnection, StoragePlugin

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class AbstractSingletonMeta(ABCMeta, Singleton):
    pass

class InmemoryStorageConnection(StorageConnection, metaclass=AbstractSingletonMeta):
    @staticmethod
    @abstractmethod
    def storage_type() -> StorageType:
        pass
    
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
    @abstractmethod
    def storage_type() -> StorageType:
        pass
    
    @staticmethod
    @abstractmethod
    def get_connection(host: Host = None, auth: Auth = None) -> InmemoryStorageConnection:
        pass

class InmemoryStorateFakeType(StorageType):
    def __init__(self):
        super().__init__("inmemory", True)

class InmemoryStorateFake2Type(StorageType):
    def __init__(self):
        super().__init__("inmemory2", True)

class InmemoryStorageFakeConnection(InmemoryStorageConnection):
    @staticmethod
    def storage_type() -> StorageType:
        return InmemoryStorateFakeType()

class InmemoryStorageFakePlugin(InmemoryStoragePlugin):
    @staticmethod
    def get_connection(host: Host = None, auth: Auth = None) -> InmemoryStorageConnection:
        return InmemoryStorageFakeConnection()
    
    @staticmethod
    def storage_type() -> StorageType:
        return InmemoryStorageFakeConnection.storage_type()
    
class InmemoryStorageFake2Connection(InmemoryStorageConnection):
    @staticmethod
    def storage_type() -> StorageType:
        return InmemoryStorateFake2Type()

class InmemoryStorageFake2Plugin(InmemoryStoragePlugin):
    @staticmethod
    def get_connection(host: Host = None, auth: Auth = None) -> InmemoryStorageConnection:
        return InmemoryStorageFake2Connection()
    
    @staticmethod
    def storage_type() -> StorageType:
        return InmemoryStorageFake2Connection.storage_type()
