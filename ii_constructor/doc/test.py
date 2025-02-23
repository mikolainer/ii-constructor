class Output:
    __id: int
    __description: str

    def __init__(self, id: int, description: str):
        setattr(self, "_Output__id", id)
        setattr(self, "_Output__description", description)

    def _id(self) -> int:
        return getattr(self, "_Output__id")
    
    def _description(self) -> str:
        return getattr(self, "_Output__description")