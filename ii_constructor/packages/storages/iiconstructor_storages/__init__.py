from iiconstructor_storages.primitives import StorageType, Host, Auth
from iiconstructor_storages.plugis_base import StorageConnection, StoragePlugin
from iiconstructor_storages.presentation import StorageConnectionView, StoragePluginView, StorageConnectionPresenter, StoragePluginPresenter
from iiconstructor_storages.operations import StoragesManager

class StoragePluginController:
    __manager: StoragesManager
    __conn_presenter: StorageConnectionPresenter
    __plugin_presenter: StoragePluginPresenter

    def __init__(self, manager: StoragesManager, conn_present: StorageConnectionPresenter, plugin_present:StoragePluginPresenter):
        self.__manager = manager
        self.__conn_presenter = conn_present
        self.__plugin_presenter = plugin_present

    def available_plugins(self) -> set[StorageType]:
        return {plugin.storage_type() for plugin in self.__manager.available_plugins()}

    def connected_types(self) -> set[StorageType]:
        return self.__manager.connected_types()

    def read(self) -> set[StorageConnectionView]:
        return {self.__conn_presenter.present(conn) for conn in self.__manager.read()}

    def connect(self, conn: StorageConnectionView, login: str, password: str):
        for plugin in self.__manager.available_plugins():
            _type = plugin.storage_type()
            if _type.name == conn.storage_type[0] and _type.is_inmemory == conn.storage_type[1]:
                self.__manager.connect(plugin.storage_type(), Host(conn.host), Auth(login, password))
                
        print("ERROR: невалидный тип")
        raise ValueError(conn)

    def disconnect(self, conn: StorageConnectionView):
        _conn = self.__conn_presenter.get(conn, self.__manager)
        if _conn is None:
            print(f"ERROR: не существует подключения {conn.storage_type[0]}@{conn.host}")
            return
        
        self.__manager.disconnect(_conn)

    def invalidate_plugin(self, plugin:StoragePluginView) -> StoragePluginView:
        _plugin = self.__plugin_presenter.get(plugin)
        
        if _plugin is not None:
            return self.__plugin_presenter.present(_plugin)

        return StoragePluginView(
                plugin.storage_type,
                False,
                False
            )

    def invalidate_connection(self, conn:StorageConnectionView) -> StorageConnectionView:
        _conn = self.__conn_presenter.get(conn)
        
        if _conn is not None:
            return self.__conn_presenter.present(_conn)

        return StorageConnectionView(
                conn.storage_type,
                conn.host,
                False,
                False
            )