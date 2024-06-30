from enum import IntEnum, verify, UNIQUE
from typing import Any, Union, Optional

from PySide6.QtCore import (
    Qt,
    QModelIndex,
    QObject,
    QPersistentModelIndex, 
    QAbstractItemModel,
    QIdentityProxyModel,
)

@verify(UNIQUE)
class CustomDataRole(IntEnum):
    ''' набор пользовательских ролей '''
    Id              : 'CustomDataRole' = Qt.ItemDataRole.UserRole +1,   # int
    Name            : 'CustomDataRole' = Qt.ItemDataRole.UserRole +2,   # str
    Description     : 'CustomDataRole' = Qt.ItemDataRole.UserRole +3,   # str
    Text            : 'CustomDataRole' = Qt.ItemDataRole.UserRole +4,   # str
    SynonymsSet     : 'CustomDataRole' = Qt.ItemDataRole.UserRole +5,   # SynonymsSetModel
    EnterStateId    : 'CustomDataRole' = Qt.ItemDataRole.UserRole +6,   # int
    SliderVisability: 'CustomDataRole' = Qt.ItemDataRole.UserRole +7,   # bool
    Node            : 'CustomDataRole' = Qt.ItemDataRole.UserRole +8,   # SceneNode
    FromState       : 'CustomDataRole' = Qt.ItemDataRole.UserRole +9,   # StateID
    ToState         : 'CustomDataRole' = Qt.ItemDataRole.UserRole +10,  # StateID

class ItemData:
    ''' Обёртка над данными с использованием ролей '''
    on: dict[int, Any] # role, data
    def __init__(self) -> None:
        self.on = {}

class PresentationModelMixinBase():
    ''' Реализация контейнера для данных, обёрнутых в ItemData '''
    __data: list[ItemData]
    __index_roles: list[CustomDataRole]
    __required_roles: list[CustomDataRole]
    __index_by: dict[CustomDataRole, dict] # dict = [Any, ItemData]

    def _data_init(self,
        index_roles: list[CustomDataRole] = [],
        required_roles: list[CustomDataRole] = []
    ):
        '''
        Настройка для вызова в конструкторе. 
        @index_roles - список ролей для быстрого поиска get_item_by(),
        @required_roles - обязательные роли. например используемые в paint() делегата Qt
        '''
        self.__index_roles = index_roles
        self.__required_roles = required_roles
        self.__data = []
        self.__index_by = {}
        for role in self.__index_roles:
            self.__index_by[role] = {}

    def add_item(self, item:ItemData) -> int:
        ''' Добавляет item и возвращает его индекс '''
        if not issubclass(type(item), ItemData):
            raise TypeError(item)

        # проверка наличия ролей для индексации
        item_roles: CustomDataRole = list(item.on.keys())
        for role in self.__index_roles:
            if not role in item_roles:
                raise ValueError(f"аргумент `item` не содержит роли {role} для создания индекса. ({item_roles})")
            
        for role in self.__required_roles:
            if not role in item_roles:
                raise ValueError(f"аргумент `item` не содержит обязательной роли {role} ({item_roles})")

        self.__data.append(item)
        for role in self.__index_roles:
            self.__index_by[role][item.on[role]] = item

        return len(self.__data) -1 #self.__data.index(item)
    
    def cut_item(self, item:ItemData) -> None:
        ''' Удаляет `item` '''
        if not issubclass(type(item), ItemData):
            raise TypeError(item)
        
        for role in self.__index_roles:
            del self.__index_by[role][item.on[role]]

        self.__data.remove(item)
    
    def get_item(self, index:int) -> ItemData:
        ''' ищет item по индексу '''
        if not issubclass(type(index), int):
            raise TypeError(index)
        
        if index < 0:
            raise ValueError(f"отрицательный индекс ({index})")
        
        return self.__data[index]
    
    def get_item_by(self, role:CustomDataRole, value:Any) -> ItemData:
        ''' ищет item по значению роли '''
        if not issubclass(type(role), CustomDataRole):
            raise TypeError(role)

        if not role in self.__index_roles:
            raise ValueError(f"нет индекса по указанной роли ({role})")
        
        # TODO: несколько item'ов с одинаковыми значениями роли?
        if not value in self.__index_by[role].keys():
            return None

        return self.__index_by[role][value]
    
    def __len__(self) -> int:
        return len(self.__data)

class BaseModel(PresentationModelMixinBase, QAbstractItemModel):
    ''' Базовая надстройка над базовой моделью Qt для работы с ItemData в виде списка '''
    __prepared_item: Optional[ItemData]
    __map_custom_as_qt_role: dict[Qt.ItemDataRole, CustomDataRole]

    def __init__( self, parent: QObject | None = None, prepared_item: Optional[ItemData] = None) -> None:
        super().__init__(parent)
        self.__map_custom_as_qt_role = {}
        self.__prepared_item = prepared_item

    def map_role_as(self, role: CustomDataRole, as_role: Qt.ItemDataRole):
        ''' устанавливает соответствие ролей для получения данных через `data()` '''
        self.__map_custom_as_qt_role[as_role] = role

    def unmap_role(self, role: Qt.ItemDataRole):
        ''' удаляет соответствие роли для получения данных через `data()` '''
        del self.__map_custom_as_qt_role[role]

    def prepare_item(self, item:ItemData):
        ''' Подготовить элемент для вставки в модель '''
        self.__prepared_item = item

    def parent(self, child: Union[QModelIndex, QPersistentModelIndex]) -> QModelIndex:
        ''' Модель плоская. Возвращается QModelIndex() '''
        return QModelIndex()

    def index(self, row: int, column: int = 0, parent: QModelIndex | QPersistentModelIndex = None) -> QModelIndex:
        ''' возвращает индекс по строке (аргумент `column` игнорируется, всегда 0) '''
        return self.createIndex(row, column, self.get_item(row))
    
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        ''' Возвращает количество элементов в модели '''
        return len(self)
    
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        ''' Всегда возвращает 1 (список представляется таблицей с единствоенный мтолбцом) '''
        return 1
    
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        ''' Устанавливает значение для роли элемента, с индексом `index.row()` '''
        if role == Qt.ItemDataRole.EditRole and Qt.ItemDataRole.DisplayRole in self.__map_custom_as_qt_role.keys():
            self.get_item(index.row()).on[self.__map_custom_as_qt_role[Qt.ItemDataRole.DisplayRole]] = value
            self.dataChanged.emit(index,index,role)
            return True

        self.get_item(index.row()).on[role] = value
        self.dataChanged.emit(index,index,role)
        return True # ошибки обрабатываем исключениями
    
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        ''' Возвращает значение роли у элемента, с индексом `index.row()` '''
        if role < Qt.ItemDataRole.UserRole:
            if role in self.__map_custom_as_qt_role.keys():
                return self.get_item(index.row()).on[self.__map_custom_as_qt_role[role]]
            else:
                return None
        else:
            return self.get_item(index.row()).on[role]
    
    def insertRow(self, row: int = None, parent: QModelIndex | QPersistentModelIndex = None) -> bool:
        ''' Добавляет 1 подготовленный элемент в конец. Все аргументы игнорируются. '''
        return super().insertRow(self.rowCount(), QModelIndex())

    def insertRows(self, row: int, count: int = None, parent: QModelIndex | QPersistentModelIndex = None) -> bool:
        ''' Добавляет 1 подготовленный элемент в конец. Все аргументы игнорируются. '''
        new_row: int = self.rowCount()
        self.beginInsertRows(QModelIndex(), new_row, new_row)
        self.add_item(self.__prepared_item)
        self.endInsertRows()
        self.__prepared_item = None
        return True # ошибки обрабатываем исключениями
    
    def removeRow(self, row: int, parent: QModelIndex | QPersistentModelIndex = None) -> bool:
        ''' Удаляет 1 элемент с индексом `row`. Аргумент `parent` игнорируeтся. '''
        return super().removeRow(row, QModelIndex())
    
    def removeRows(self, row: int, count: int = None, parent: QModelIndex | QPersistentModelIndex = None) -> bool:
        ''' Удаляет 1 элемент с индексом `row`. Аргументы `count` и `parent` игнорируются. '''
        self.beginRemoveRows(QModelIndex(), row, row)
        self.cut_item(self.get_item(row))
        self.endRemoveRows()
        return True # ошибки обрабатываем исключениями

class ProxyModelReadOnly(QIdentityProxyModel):
    ''' Модификатор модели только для чтения '''
    def __init__( self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._data_init() # TODO

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return ~Qt.ItemFlag.ItemIsEditable & self.sourceModel().flags(index)

# COMMON 
class SynonymsSetModel(BaseModel):
    ''' Модель набора синонимов '''
    def __init__( self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._data_init() # TODO
        self.map_role_as(CustomDataRole.Text, Qt.ItemDataRole.DisplayRole)

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = CustomDataRole.Text) -> bool:
        if role == CustomDataRole.Text and isinstance(value, str) and value == '':
            return self.removeRow(index.row())

        return super().setData(index, value, role)
