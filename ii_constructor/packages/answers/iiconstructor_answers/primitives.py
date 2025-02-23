from dataclasses import dataclass

@dataclass(frozen=True)
class OutputID:
    value: int

@dataclass(frozen=True)
class OutputType:
    name: str