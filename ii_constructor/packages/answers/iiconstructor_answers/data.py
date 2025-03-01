from typing import TypeVar

from .dataaccess import DataAccess, StorageType
from .spec import Iexpression, Expression
from .primitives import OutputType, OutputID

class OutputDescription:
    def get_type(self) -> OutputType:
        pass

class Output:
    __id: OutputID
    __description: OutputDescription

    def __init__(self, id: OutputID, description: OutputDescription):
        setattr(self, "_Output__id", id)
        setattr(self, "_Output__description", description)

    def id(self) -> OutputID:
        return getattr(self, "_Output__id")
    
    def description(self) -> OutputID:
        return getattr(self, "_Output__description")
    
class IsOutputSpec:
    __expr: Iexpression
    
    def __init__(self, expr: Iexpression):
        setattr(self, "_IsOutputSpec__expr", expr)

    def expr(self) -> Iexpression:
        return getattr(self, "_Expression__field_value")

class OneIdOutputSpec(IsOutputSpec):
    def __init__(self, id: OutputID):
        super().__init__(Expression("id", id))
    
    def expr(self) -> Expression:
        return super().expr()

class OutputRepository:
    def __init__(self, data_access: DataAccess):
        pass

    def is_open(self) -> bool:
        pass

    def open(self):
        pass

    def close(self):
        pass

    def save(self, spec: IsOutputSpec, item:OutputDescription):
        pass

    def get(self, spec: IsOutputSpec) -> set[Output]:
        pass

    def remove(self, spec: IsOutputSpec):
        pass

    def total_count(self) -> int:
        pass

    def unused_identificator(self) -> OutputID:
        pass

    def have_unused_id(self) -> bool:
        pass

    @staticmethod
    def get_output_type() -> OutputType:
        pass

    @staticmethod
    def get_storage_type() -> StorageType:
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