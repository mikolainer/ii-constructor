from iiconstructor_storages.primitives import StorageType, Host, Auth
from iiconstructor_storages.plugis_base import StoragePlugin, StorageConnection

class StoragesManager:
    __all_plugins: dict[StorageType, StoragePlugin]
    __connections: set[StorageConnection]

    def __init__(self, plugins: set[StoragePlugin]):
        self.__connections = set[StorageConnection]()
        self.__all_plugins = dict[StorageType, StoragePlugin]()
        for plugin in plugins:
            if plugin not in self.__all_plugins.keys():
                self.__all_plugins[plugin.storage_type()] = plugin

    def available_plugins(self) -> set[StoragePlugin]:
        return set(self.__all_plugins.values())

    def read(self) -> set[StorageConnection]:
        return self.__connections

    def connect(self, plugin: StorageType, host: Host, auth: Auth) -> StorageConnection:
        _plugin = self.__all_plugins[plugin]
        new_conn = _plugin.get_connection(host, auth)
        self.__connections.add(new_conn)
        return new_conn

    def disconnect(self, connection: StorageConnection):
        self.__connections.pop(connection)

    def connected_types(self) -> set[StorageType]:
        return {conn.storage_type() for conn in self.__connections}
