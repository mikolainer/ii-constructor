from iiconstructor_storages.primitives import StorageType, Host, Auth
from iiconstructor_storages.plugis_base import StoragePlugin, StorageConnection

class StorageConnectionsManager:
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

    def conn_list(self) -> set[StorageConnection]:
        return self.__connections

    def add(self, new_conn: StorageConnection):
        self.__connections.add(new_conn)

    def delete(self, connection: StorageConnection):
        self.__connections.pop(connection)
