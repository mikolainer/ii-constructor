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

@dataclass(frozen=True)
class LibID:
    value: int

@dataclass(frozen=True)
class Host:
    addr: str

@dataclass(frozen=True)
class DataAccess:
    host: Host
    outputs_type: OutputType
    storage_type: StorageType

@dataclass(frozen=True)
class PluginInfo:
    name: str
    version: str
    author: str
    contacts: str
    url: str
    outputs: OutputType
    storages: set[StorageType]

@dataclass(frozen=True)
class LibInfo:
    name: str
    descr: str
    plugin: PluginInfo
