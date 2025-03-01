from dataclasses import dataclass

@dataclass(frozen=True)
class OutputID:
    value: int

@dataclass(frozen=True)
class OutputType:
    name: str

@dataclass(frozen=True)
class StorageType:
    name: str
    is_inmemory: bool

class DataAccess:
    __outputs_type: OutputType
    __storage_type: StorageType

    def __init__(self, outputs_type: OutputType, storage_type: StorageType):
        setattr(self, "_DataAccess__outputs_type", type)
        setattr(self, "_DataAccess__storage_type", type)

    def outputs_type(self) -> OutputType:
        return getattr(self, "_DataAccess__outputs_type")
    
    def storage_type(self) -> StorageType:
        return getattr(self, "_DataAccess__storage_type")