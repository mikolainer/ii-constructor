from dataclasses import dataclass

@dataclass(frozen=True)
class StorageType:
    name: str
    is_inmemory: bool

@dataclass(frozen=True)
class Host:
    addr: str

@dataclass(frozen=True)
class Auth:
    login: str
    password: str