from dataclasses import dataclass

@dataclass(frozen=True)
class ExprType:
    type_name: str

class EqType(ExprType):
    def __init__(self):
        super().__init__("eq")
