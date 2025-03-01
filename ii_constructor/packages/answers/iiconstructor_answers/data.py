from iiconstructor_answers.spec import Iexpression, Expression
from iiconstructor_answers.shared_core import OutputType, OutputID, StorageType, DataAccess
    
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
