from typing import TypeVar
from dataclasses import dataclass

from iiconstructor_answers.data import OutputRepository, IsOutputSpec, OneIdOutputSpec, OutputDescription, Output
from iiconstructor_answers.primitives import OutputType, OutputID, DataAccess, StorageType

from iiconstructor_answers.plaintext import PlainTextOutputInmemoryRepository, PlainTextDescription, PlainTextPlugin

class Plugin:
    def output_type() -> OutputType:
        pass

    def storage_type() -> StorageType:
        pass

class OutputFactory:
    def __init__(self, repo: OutputRepository):
        setattr(self, "_OutputFactory__repo", repo)

    def _repo(self) -> OutputRepository:
        return getattr(self, "_OutputFactory__repo")
    
    def create(self, description: OutputDescription) -> Output:
        if not super()._repo().is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(super()._repo())

        new_id: OutputID
        if super()._repo().have_unused_id():
            new_id = super()._repo().unused_identificator()
        else:
            new_id = OutputID(super()._repo().total_count())
        
        return Output(new_id, description)

class OutputLibService:
    @staticmethod
    def create(value: OutputDescription, repo: OutputRepository) -> Output:
        factory = OutputFactory(repo)
        new_item = factory.create(value)
        factory._repo().save(OneIdOutputSpec(new_item.id()), new_item.value())
        return new_item

    @staticmethod
    def read(spec: IsOutputSpec, repo: OutputRepository) -> set[Output]:
        if not repo.is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(repo)
        
        return repo.get(spec)

    @staticmethod
    def update(id_spec: IsOutputSpec, new_value:OutputDescription, repo: OutputRepository):
        if not repo.is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(repo)
        
        result = repo.get(id_spec)
        
        if len(result) == 0:
            print(f"ERROR: попытка обновить несуществующий(е) объект(ы)")
            raise ValueError(id_spec)
        
        old_output = result.pop()
        repo.save(OneIdOutputSpec(old_output.id()), new_value)

    @staticmethod
    def delete(spec: IsOutputSpec, repo: OutputRepository):
        if not repo.is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(repo)
        
        repo.remove(spec)

class OutputLibManager:
    __all_plugins: set[Plugin]
    __connected: dict[Plugin, DataAccess]

    def __init__(self, inmemory: bool):
        setattr(self, "_OutputLibManager__is_inmemory", inmemory)
        self.__connected = dict[Plugin, DataAccess]()

    def is_inmemory(self) -> bool:
        return getattr(self, "_OutputLibManager__is_inmemory")

    def load_plugins(self):
        self.__all_plugins = set([
            PlainTextPlugin(),
        ])
    
    def connect(self, connection: DataAccess):
        if self.is_inmemory() and not connection.storage_type().is_inmemory:
            print(f"ERROR: попытка подключиться к удалённому хранилищу в Inmemory менеджере")
            raise ValueError(connection)
        
        if not self.is_inmemory() and connection.storage_type().is_inmemory:
            print(f"ERROR: попытка подключиться к Inmemory хранилищу в удалённом менеджере")
            raise ValueError(connection)

        new_type = connection.outputs_type()
        
        connected_types = {plugin.output_type() for plugin in self.connected_plugins()}
        if connection.outputs_type() in connected_types:
            print(f"ERROR: попытка повторно подключить библиотеку с типом `{new_type.name}`")
            raise ValueError(connection)
        
        for plugin in self.__all_plugins:
            if connection.storage_type().name == plugin.storage_type().name:
                self.__connected[self.__all_plugins] = connection
                return

        print(f"ERROR: неизвестный тип подключения к БД")
        raise ValueError(connection)
    
    def disconnect(self, plugin:Plugin):
        self.__connected.pop(plugin)
    
    def connected_plugins(self) -> set[Plugin]:
        return {self.__connected.keys()}
    
    def available_plugins(self) -> set[Plugin]:
        return self.__all_plugins.keys()
    
#    def make(self, connection: DataAccess):
#        raise NotImplementedError()
#
#    def remove(self, connection: DataAccess):
#        raise NotImplementedError()