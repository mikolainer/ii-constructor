from dataclasses import dataclass
from iiconstructor_storages.primitives import StorageType, Host, Auth
from iiconstructor_storages.plugis_base import StorageConnection, StoragePlugin
from iiconstructor_storages.domain import StorageConnectionsManager

@dataclass(frozen=True)
class StoragePluginViewModel:
    name: str
    inmem: bool

@dataclass(frozen=True)
class StorageConnectionViewModel:
    host: str
    login: str
    password: str
    type_name: str
    type_inmemory: bool

class StorageConnectionPresenter:
    @staticmethod
    def present(obj: StorageConnection) -> StorageConnectionViewModel:
        return StorageConnectionViewModel(
            obj.host().addr, "", "",
            obj.storage_type().name,
            obj.storage_type().is_inmemory
        )
    
    @staticmethod
    def get(view: StorageConnectionViewModel, manager: StorageConnectionsManager) -> StorageConnection:
        for _plugin in manager.available_plugins():
            _type = _plugin.storage_type()
            if _type.name == view.type_name and _type.is_inmemory == view.type_inmemory:
                for _conn in manager.conn_list():
                    if (_conn.storage_type() == _plugin.storage_type()
                        and _conn.host().addr == view.host ):
                        return _conn

        print(f"ERROR: попытка получить неизвестное подключение.")
        raise ValueError(view)


class StoragePluginPresenter:
    @staticmethod
    def present(obj: StoragePlugin) -> StoragePluginViewModel:
        return StoragePluginViewModel(
            obj.storage_type().name,
            obj.storage_type().is_inmemory
        )
    
    @staticmethod
    def get(view: StoragePluginViewModel, manager: StorageConnectionsManager) -> StoragePlugin:
        for plugin in manager.available_plugins():
            _type = plugin.storage_type()
            if _type.name == view.name and _type.is_inmemory == view.inmem:
                return plugin
        
        print(f"ERROR: плагин `{view.name}` не поддерживается")
        raise ValueError(view)

class StorageConnectionsController:
    __conn_presenter = StorageConnectionPresenter
    __plugin_presenter = StoragePluginPresenter
    __manager: StorageConnectionsManager

    def __init__(self, plugins: set[StoragePlugin]):
        self.__manager = StorageConnectionsManager(plugins)

    def available_plugins(self) -> set[StoragePluginViewModel]:
        return {self.__plugin_presenter.present(plugin) for plugin in self.__manager.available_plugins()}

    def get_connections(self, plugin: StoragePluginViewModel | None = None) -> set[StorageConnectionViewModel]:
        if plugin is None:
            return {self.__conn_presenter.present(conn) for conn in self.__manager.conn_list()}
        
        result = set[StorageConnectionViewModel]()
        _plugin_type = self.__plugin_presenter.get(plugin, self.__manager).storage_type()
        if isinstance(plugin, StoragePluginViewModel):
            for conn in self.__manager.conn_list():
                if _plugin_type == conn.storage_type():
                    result.add(self.__conn_presenter.present(conn))
        
        return result

    def add_connection(self, conn_view_model:StorageConnectionViewModel):
        plugin = self.__plugin_presenter.get(
            StoragePluginViewModel(conn_view_model.type_name, conn_view_model.type_inmemory), self.__manager
        )
        conn = plugin.get_connection(Host(conn_view_model.host), Auth(conn_view_model.login, conn_view_model.password))
        try:
            conn.open()
            ok = conn.is_open()
            conn.close()
        except:
            print(f"ERROR: не удалось подключиться к {conn_view_model.host} для {conn_view_model.type_name}")
            raise

        if not ok:
            print(f"ERROR: не удалось подключиться к {conn_view_model.host} для {conn_view_model.type_name}")
            raise ValueError(conn_view_model)
        
        self.__manager.add(conn)

    def delete_connection(self, conn_view_model:StorageConnectionViewModel):
        _conn = self.__conn_presenter.get(conn_view_model, self.__manager)
        self.__manager.delete(_conn)
