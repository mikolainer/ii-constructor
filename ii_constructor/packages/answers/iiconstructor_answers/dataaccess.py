from dataclasses import dataclass
from primitives import OutputType, StorageType

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

class InmemData(DataAccess):
    pass

class RemoteData(DataAccess):
    pass