from iiconstructor_answers.shared_core import OutputType, OutputID, StorageType
from iiconstructor_answers.data import OutputRepository, OutputDescription, Output, IsOutputSpec, OneIdOutputSpec, DataAccess

class PlainTextDescription(OutputDescription):
    __text: str

    def __init__(self, text: str):
        super().__init__()
        self.__text = text

    def text(self):
        return self.__text

    @staticmethod
    def get_type() -> OutputType:
        return OutputType("plaintext")


def build_query(spec: IsOutputSpec):
    print(f"ERROR: спецификация не поддерживается")
    raise AttributeError(spec)


class PlainTextOutputInmemoryRepository(OutputRepository):
    __data: dict[OutputID, Output]
    __unused_ids: set[OutputID]

    def __init__(self, data_access: DataAccess):
        self.__data = dict[OutputID, Output]()
        self.__unused_ids = set[OutputID]()

    @staticmethod
    def get_output_type() -> OutputType:
        return PlainTextDescription.get_type()

    @staticmethod
    def get_storage_type() -> StorageType:
        return StorageType("inmemory", True)

    def is_open(self) -> bool:
        return True

    def open(self):
        pass

    def close(self):
        pass

    def save(self, spec: IsOutputSpec, item:OutputDescription):
        if isinstance(spec, OneIdOutputSpec):
            id = spec.id()
            self.__data[id].description() = item
            self.__unused_ids.discard(id)

        build_query(spec)

    def get(self, spec: IsOutputSpec) -> set[Output]:
        if isinstance(spec, OneIdOutputSpec):
            return {self.__data[spec.id()]}
        
        build_query(spec)

    def remove(self, spec: IsOutputSpec):
        if isinstance(spec, OneIdOutputSpec):
            id = spec.id()
            self.__data.pop(id)
            self.__unused_ids.add(id)
        
        build_query(spec)

    def total_count(self) -> int:
        return len(self.__data)

    def unused_identificator(self) -> OutputID:
        return next(iter(self.__unused_ids))

    def have_unused_id(self) -> bool:
        return len(self.__unused_ids) > 0
