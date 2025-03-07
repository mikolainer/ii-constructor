from typing import TypeVar
from dataclasses import dataclass

from iiconstructor_outputs.data import OutputRepository, IsOutputSpec, OneIdOutputSpec, OutputDescription, Output, Storage
from iiconstructor_outputs.primitives import OutputType, OutputID, DataAccess, StorageType, Host, LibID, PluginInfo, LibInfo

class OutputLib:
    __id: LibID
    __repo: OutputRepository
    __info: LibInfo

    def __init__(self, id: LibID, repo: OutputRepository, info: LibInfo):
        self.__id = id
        self.__repo = repo
        self.__info = info

    def id(self) -> LibID:
        return self.__id
    
    def info(self) -> LibInfo:
        return self.__info

    def create(self, value: OutputDescription) -> Output:
        factory = OutputFactory(self.__repo)
        new_item = factory.create(value)
        self.__repo.save(OneIdOutputSpec(new_item.id()), new_item.value())
        return new_item

    def read(self, spec: IsOutputSpec) -> set[Output]:
        if not self.__repo.storage().is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(self.__repo())
        
        return self.__repo.get(spec)

    def update(self, spec: IsOutputSpec, new_value: OutputDescription):
        if not self.__repo.storage().is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(self.__repo())
        
        result = self.__repo.get(spec)
        
        if len(result) == 0:
            print(f"ERROR: попытка обновить несуществующий(е) объект(ы)")
            raise ValueError(spec)
        
        old_output = result.pop()
        self.__repo.save(OneIdOutputSpec(old_output.id()), new_value)

    def delete(self, spec: IsOutputSpec):
        if not self.__repo.storage().is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(self.__repo)
        
        self.__repo.delete(spec)

    def remove(self):
        self.__repo.remove()
        self.__repo = None


class OutputPlugin:
    @staticmethod
    def create_lib(storage: Storage, name: str, descr: str, id: LibID) -> OutputLib:
        pass

    @staticmethod
    def info() -> PluginInfo:
        pass

class OutputFactory:
    __repo: OutputRepository
    
    def __init__(self, repo: OutputRepository):
        setattr(self, "_OutputFactory__repo", repo)

    def _repo(self) -> OutputRepository:
        return getattr(self, "_OutputFactory__repo")
    
    def create(self, description: OutputDescription) -> Output:
        if not self._repo().storage().is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(self._repo())

        new_id = self._repo().unused_identificator()
        
        return Output(new_id, description)

class OutputLibManager:
    __all_plugins: set[OutputPlugin]
    __connected: dict[OutputLib, OutputPlugin]

    def __init__(self, inmemory: bool, plugins: set[OutputPlugin] = set[OutputPlugin]()):
        setattr(self, "_OutputLibManager__is_inmemory", inmemory)
        self.__all_plugins = plugins
        self.__connected = dict[OutputLib, OutputPlugin]()

    def is_inmemory(self) -> bool:
        return getattr(self, "_OutputLibManager__is_inmemory")

    def available_plugins(self) -> set[OutputPlugin]:
        return self.__all_plugins

    def ping(self, storage: Storage) -> bool:
        if storage.is_open():
            return True
        
        storage.open()
        result = storage.is_open()
        storage.close()

        return result
    
    def create(self, plugin: OutputPlugin, storage: Storage, name: str, descr: str) -> OutputLib:
        return plugin.create_lib(storage, name, descr)

    def read(self) -> set[OutputLib]:
        return set(self.__connected.keys())

    def remove(self, lib: OutputLib):
        lib.remove()
        self.__connected.pop(lib)
