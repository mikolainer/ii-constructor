from typing import TypeVar
from dataclasses import dataclass

from data import OutputRepository, OutputFactory, IsOutputSpec, OneIdOutputSpec, OutputDescription, Output
from dataaccess import DataAccess, InmemData, RemoteData
from primitives import OutputType

from plaintext import PlainTextOutputRepository, PlainTextOutputFactory, PlainTextDescription

Toutdescdiption = TypeVar("Toutdescdiption", bound=OutputDescription)
Trepo = TypeVar("Trepo", bound=OutputRepository)
Tfactory = TypeVar("Tfactory", bound=OutputRepository)
@dataclass(frozen=True)
class Plugin:
    repo: Trepo
    factory: Tfactory
    output_value_type: Toutdescdiption

plugins: set[Plugin] = set([
    Plugin(PlainTextOutputRepository, PlainTextOutputFactory, PlainTextDescription),
])

class OutputLibService:
    @staticmethod
    def create(value: OutputDescription, factory: OutputFactory) -> Output:
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
    __is_inmemory: bool
    __libs: dict[Plugin, DataAccess]

    def __init__(self, inmemory: bool):
        setattr(self, "_OutputLibManager__is_inmemory", inmemory)
        self.__libs = dict[Plugin, DataAccess]()

    def is_inmemory(self) -> bool:
        return getattr(self, "_OutputLibManager__is_inmemory")
    
    def connected(self) -> set[OutputType]:
        return {plugin.repo.get_output_type() for plugin in self.__libs.keys()}
    
    def connect(self, connection: DataAccess):
        if self.is_inmemory() and not issubclass(type(connection), InmemData):
            print(f"ERROR: подключиться к удалённому хранилищу в Inmemory менеджере")
            raise ValueError(connection)
        
        if not self.is_inmemory() and not issubclass(type(connection), RemoteData):
            print(f"ERROR: подключиться к Inmemory хранилищу в удалённом менеджере")
            raise ValueError(connection)

        new_type = connection.outputs_type()
        if connection.outputs_type() in self.connected():
            print(f"ERROR: попытка повторно подключить библиотеку с типом `{new_type.name}`")
            raise ValueError(connection)
        
        for plugin in plugins:
            _repo_type = plugin.repo
            if connection.storage_type() is _repo_type.get_storage_type():
                self.__libs[plugin] = connection
                return

        print(f"ERROR: енизвестный тип подключения к БД")
        raise ValueError(connection)
    
    def make(self, connection: DataAccess):
        raise NotImplementedError()

    def remove(self, connection: DataAccess):
        raise NotImplementedError()