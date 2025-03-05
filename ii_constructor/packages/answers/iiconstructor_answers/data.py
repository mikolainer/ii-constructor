from iiconstructor_answers.spec import Iexpression, Expression
from iiconstructor_answers.primitives import OutputType, OutputID, StorageType, DataAccess, Host
    
class Storage:
    __host: Host

    def __init__(self, host: Host):
        setattr(self, "_Storage__host", host)

    def host(self) -> Host:
        return getattr(self, "_Storage__host")
    
    @staticmethod
    def storage_type(self) -> StorageType:
        pass

    def is_open(self) -> bool:
        pass

    def open(self):
        pass

    def close(self):
        pass

class OutputDescription:
    @staticmethod
    def get_type() -> OutputType:
        pass

class Output:
    __id: OutputID
    __description: OutputDescription

    def __init__(self, id: OutputID, description: OutputDescription):
        setattr(self, "_Output__id", id)
        setattr(self, "_Output__description", description)

    def id(self) -> OutputID:
        return getattr(self, "_Output__id")
    
    def description(self) -> OutputDescription:
        return getattr(self, "_Output__description")

    
class IsOutputSpec:
    __expr: Iexpression
    
    def __init__(self, expr: Iexpression):
        setattr(self, "_IsOutputSpec__expr", expr)

    def expr(self) -> Iexpression:
        return getattr(self, "_IsOutputSpec__expr")

class OneIdOutputSpec(IsOutputSpec):
    def __init__(self, id: OutputID):
        super().__init__(Expression("id", id))
    
    def expr(self) -> Expression:
        return super().expr()
    
    def id(self) -> OutputID:
        return self.expr().value()

class OutputRepository:
    __connection: Storage

    def __init__(self, connection: Storage):
        setattr(self, "_OutputRepository__connection", connection)

    def storage(self) -> Storage:
        return getattr(self, "_OutputRepository__connection")

    def save(self, spec: IsOutputSpec, item:OutputDescription):
        pass

    def get(self, spec: IsOutputSpec) -> set[Output]:
        pass

    def remove(self, spec: IsOutputSpec):
        pass

    def unused_identificator(self) -> OutputID:
        pass

    @staticmethod
    def get_output_type() -> OutputType:
        pass

    @staticmethod
    def get_storage_type() -> StorageType:
        pass
