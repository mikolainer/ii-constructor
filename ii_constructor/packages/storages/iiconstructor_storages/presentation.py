from dataclasses import dataclass
from iiconstructor_storages.primitives import StorageType, Host, Auth
from iiconstructor_storages.plugis_base import StorageConnection, StoragePlugin
from iiconstructor_storages.operations import StoragesManager

@dataclass
class StorageConnectionViewModel:
    storage_type: tuple[str, bool]
    host: str
    is_open: bool
    is_enabled: bool

@dataclass
class StoragePluginViewModel:
    storage_type: tuple[str, bool]
    have_connections: bool
    is_enabled: bool

class StorageConnectionPresenter:
    @staticmethod
    def present(obj: StorageConnection) -> StorageConnectionViewModel:
        return StorageConnectionViewModel(
            (obj.storage_type().name, obj.storage_type().is_inmemory),
            obj.host().addr,
            obj.is_open(),
            True
        )
    
    @staticmethod
    def get(view: StorageConnectionViewModel, manager: StoragesManager) -> StorageConnection | None:
        for _plugin in manager.available_plugins():
            _type = _plugin.storage_type()
            if _type.name == view.storage_type[0] and _type.is_inmemory == view.storage_type[1]:
                for _conn in manager.read():
                    if (_conn.storage_type() == _plugin.storage_type()
                    and _conn.host().addr == view.host
                    ): return _conn

        return None


class StoragePluginPresenter:
    @staticmethod
    def present(obj: StoragePlugin, manager: StoragesManager) -> StoragePluginViewModel:
        return StoragePluginViewModel(
            (obj.storage_type().name, obj.storage_type().is_inmemory),
            obj.storage_type() in manager.connected_types(),
            True
        )
    
    @staticmethod
    def get(view: StoragePluginViewModel, manager: StoragesManager) -> StoragePlugin | None:
        for plugin in manager.available_plugins():
            _type = plugin.storage_type()
            if _type.name == view.storage_type[0] and _type.is_inmemory == view.storage_type[1]:
                return plugin
            
        return None
