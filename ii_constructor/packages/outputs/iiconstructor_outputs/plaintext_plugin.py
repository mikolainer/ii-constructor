
from iiconstructor_outputs.primitives import OutputType, OutputID, StorageType, PluginInfo, LibID, LibInfo
from iiconstructor_outputs.plugin_base import OutputRepository, OutputContent, Output, IsOutputSpec, OneIdOutputSpec, Storage, InmemoryStorage
from iiconstructor_outputs.operations import OutputPlugin, OutputLib

class PlainTextOutputType(OutputType):
    def __init__(self):
        super().__init__("plaintext")

class PlainTextDescription(OutputContent):
    __text: str

    def __init__(self, text: str):
        super().__init__()
        self.__text = text

    def text(self):
        return self.__text

    @staticmethod
    def get_type() -> OutputType:
        return PlainTextOutputType()


def build_query(spec: IsOutputSpec):
    print(f"ERROR: спецификация не поддерживается")
    raise AttributeError(spec)


class PlainTextOutputInmemoryRepository(OutputRepository):
    __data: dict[OutputID, Output]
    __unused_ids: set[OutputID]

    def __init__(self):
        super().__init__(InmemoryStorage())
        self.__data = dict[OutputID, Output]()
        self.__unused_ids = set[OutputID]()

    @staticmethod
    def get_output_type() -> OutputType:
        return PlainTextDescription.get_type()

    def save(self, spec: IsOutputSpec, item:OutputContent):
        if isinstance(spec, OneIdOutputSpec):
            id = spec.id()
            self.__data[id].description() = item
            self.__unused_ids.discard(id)

        build_query(spec)

    def get(self, spec: IsOutputSpec) -> set[Output]:
        if isinstance(spec, OneIdOutputSpec):
            return {self.__data[spec.id()]}
        
        build_query(spec)

    def delete(self, spec: IsOutputSpec):
        if isinstance(spec, OneIdOutputSpec):
            id = spec.id()
            self.__data.pop(id)
            self.__unused_ids.add(id)
        
        build_query(spec)

    def unused_identificator(self) -> OutputID:
        if len(self.__unused_ids) == 0:
            return OutputID(len(self.__data))
        
        return next(iter(self.__unused_ids))
    
    def remove(self):
        self.__data.clear()
        self.__unused_ids.clear()

class PlainTextPlugin(OutputPlugin):
    @staticmethod
    def info() -> PluginInfo:
        return PluginInfo(
            "palain_text",
            "0",
            "ii_constructor",
            "mikolainer@mail.ru",
            "https://github.com/mikolainer/ii-constructor",
            PlainTextOutputType(),
            set(
                InmemoryStorage.storage_type(),
            ),
        )
    
    @staticmethod
    def create_lib(storage: Storage, id: LibID, name: str, descr: str) -> OutputLib:
        _type = storage.storage_type()

        if (_type == InmemoryStorage.storage_type()):
            return OutputLib(id, PlainTextOutputInmemoryRepository(), LibInfo(name, descr, PlainTextPlugin.info()))
        
        print(f"ERROR: StorageType `{_type.name}` не поддерживается в плагине `{PlainTextPlugin.info().name}`")
        raise ValueError(storage)
