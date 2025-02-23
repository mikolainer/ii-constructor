from .dataaccess import DataAccess
from .primitives import OutputType, OutputID, IsOutputSpec
from .abstract import OutputDescription, Output

class OutputRepository:
    def __init__(self, data_access: DataAccess):
        pass

    def is_open():
        pass

    def open():
        pass

    def close():
        pass

    def save(self, spec: IsOutputSpec, item:OutputDescription):
        pass

    def get(self, spec: IsOutputSpec) -> set[Output]:
        pass

    def remove(self, spec: IsOutputSpec):
        pass

    def total_count(self) -> int:
        pass

    def unused_identificator() -> OutputID:
        pass

    def have_unused_id() -> bool:
        pass

    def get_type() -> OutputType:
        pass

class OutputFactory:
    __repo: OutputRepository

    def __init__(self, repo: OutputRepository):
        setattr(self, "_OutputFactory__repo", repo)

    def _repo(self) -> OutputRepository:
        return getattr(self, "_OutputFactory__repo")
    
    def create(self, description: OutputDescription) -> Output:
        if not super()._repo().is_open():
            print(f"ERROR: соединение с репозиторием не установлено")
            raise AttributeError(super()._repo())

        new_id: OutputID
        if super()._repo().have_unused_id():
            new_id = super()._repo().unused_identificator()
        else:
            new_id = OutputID(super()._repo().total_count())
        
        return Output(new_id, description)