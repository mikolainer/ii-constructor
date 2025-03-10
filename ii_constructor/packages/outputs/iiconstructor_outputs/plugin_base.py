from abc import ABC, abstractmethod
from iiconstructor_storages.primitives import StorageType
from iiconstructor_storages.plugis_base import StorageConnection
from iiconstructor_outputs.primitives import OutputType, OutputID
from iiconstructor_outputs.domain import Output, OutputContent
from iiconstructor_expressions.domain import Iexpression, EqExpression

class IsOutputSpec:
    __expr: Iexpression
    
    def __init__(self, expr: Iexpression):
        setattr(self, "_IsOutputSpec__expr", expr)

    def expr(self) -> Iexpression:
        return getattr(self, "_IsOutputSpec__expr")

class OneIdOutputSpec(IsOutputSpec):
    def __init__(self, id: OutputID):
        super().__init__(EqExpression("id", id))
    
    def expr(self) -> EqExpression:
        return super().expr()
    
    def id(self) -> OutputID:
        return self.expr().value()
    
class OutputRepository(ABC):
    __connection: StorageConnection

    @abstractmethod
    @staticmethod
    def get_output_type() -> OutputType:
        pass

    def __init__(self, connection: StorageConnection):
        setattr(self, "_OutputRepository__connection", connection)

    def storage(self) -> StorageConnection:
        return getattr(self, "_OutputRepository__connection")
    
    def get_storage_type(self) -> StorageType:
        return self.storage().storage_type()

    @abstractmethod
    def save(self, spec: IsOutputSpec, item: OutputContent):
        pass

    @abstractmethod
    def get(self, spec: IsOutputSpec) -> set[Output]:
        pass

    @abstractmethod
    def delete(self, spec: IsOutputSpec):
        pass

    @abstractmethod
    def unused_identificator(self) -> OutputID:
        pass

    @abstractmethod
    def remove(self):
        pass
