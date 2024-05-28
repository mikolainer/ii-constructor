from enum import IntEnum, verify, UNIQUE
from typing import Any, List, Union, Any, Optional
from dataclasses import dataclass

from PySide6.QtCore import (
    Qt,
    QModelIndex,
    QObject,
    QPersistentModelIndex, 
    QAbstractItemModel,
    QIdentityProxyModel
)

@verify(UNIQUE)
class CustomDataRole(IntEnum):
    ''' набор пользовательских ролей '''
    Id              : 'CustomDataRole' = Qt.ItemDataRole.UserRole,      # int
    Name            : 'CustomDataRole' = Qt.ItemDataRole.UserRole +1,   # str
    Description     : 'CustomDataRole' = Qt.ItemDataRole.UserRole +2,   # str
    Text            : 'CustomDataRole' = Qt.ItemDataRole.UserRole +3,   # str
    SynonymsSet     : 'CustomDataRole' = Qt.ItemDataRole.UserRole +4,   # SynonymsSetModel
    EnterStateId    : 'CustomDataRole' = Qt.ItemDataRole.UserRole +5,   # int
    SliderVisability: 'CustomDataRole' = Qt.ItemDataRole.UserRole +6,   # bool

class ItemData:
    ''' Обёртка над данными с использованием ролей '''
    on: dict[CustomDataRole, Any]
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
        self.__index_roles = index_roles
        self.__required_roles = required_roles
        self.__data = []
        self.__index_by = {}
        for role in self.__index_roles:
            self.__index_by[role] = {}

    def add_item(self, item:ItemData) -> int:
        ''' Добавляет item и возвращает его индекс '''
        if not issubclass(ItemData, item):
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
            self.__index_by[role][item.on[role], item]

        return len(self.__data) -1 #self.__data.index(item)
    
    def cut_item(self, item:ItemData) -> None:
        ''' Удаляет `item` '''
        if not issubclass(ItemData, item):
            raise TypeError(item)
        
        self.__data.remove(item)
        for role in self.__index_roles:
            self.__index_by[role][item.on[role], item]
    
    def get_item(self, index:int) -> ItemData:
        ''' ищет item по индексу '''
        if not issubclass(int, index):
            raise TypeError(index)
        
        if index < 0:
            raise ValueError(f"отрицательный индекс ({index})")
        
        return self.__data[index]
    
    def get_item_by(self, role:CustomDataRole, value:Any) -> ItemData:
        ''' ищет item по значению роли '''
        if not issubclass(CustomDataRole, role):
            raise TypeError(role)

        if not role in self.__index_roles:
            raise ValueError(f"нет индекса по указанной роли ({role})")
        
        # TODO: несколько item'ов с одинаковыми значениями роли?
        return self.__index_by[role][value]
    
    def __len__(self) -> int:
        return len(self.__data)

class BaseModel(PresentationModelMixinBase, QAbstractItemModel):
    ''' Базовая надстройка над базовой моделью Qt для работы с ItemData в виде списка '''
    __prepared_item: Optional[ItemData]

    def __init__( self, parent: QObject | None = None, prepared_item: Optional[ItemData] = None) -> None:
        super().__init__(parent)
        self.__prepared_item = prepared_item

    def prepare_item(self, item:ItemData):
        ''' Подготовить элемент для вставки в модель '''
        self.__prepared_item = item

    def copy_default_item() -> ItemData:
        ''' Возвращает копию элемента по умолчанию '''

    def parent(self, child: Union[QModelIndex, QPersistentModelIndex]) -> QModelIndex:
        ''' Модель плоская. Возвращается QModelIndex() '''
        return QModelIndex()

    def index(self, row: int, column: int = 0, parent: QModelIndex | QPersistentModelIndex = None) -> QModelIndex:
        ''' возвращает индекс по строке (аргумент `column` игнорируется, всегда 0) '''
        return self.createIndex(row, column, self.__data[row])
    
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        ''' Возвращает количество элементов в модели '''
        return len(self)
    
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        ''' Всегда возвращает 1 (список представляется таблицей с единствоенный мтолбцом) '''
        return 1
    
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        ''' Устанавливает значение для роли элемента, с индексом `index.row()` '''
        self.get_item(index).on[role] = value
        return True # ошибки обрабатываем исключениями
    
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        ''' Возвращает значение роли у элемента, с индексом `index.row()` '''
        return self.get_item(index.row()).on[role]
    
    def insertRows(self, row: int, count: int = None, parent: QModelIndex | QPersistentModelIndex = None) -> bool:
        ''' Добавляет 1 элемент в конец. Все аргументы игнорируются. '''
        new_row: int = self.rowCount()
        self.beginInsertRows(QModelIndex(), new_row, new_row)
        self.add_item(self.__prepared_item)
        self.endInsertRows()
        self.__prepared_item = self.__default_item
        return True # ошибки обрабатываем исключениями
        
    def removeRows(self, row: int, count: int = None, parent: QModelIndex | QPersistentModelIndex = None) -> bool:
        ''' Удаляет 1 элемент с индексом `row`. Аргументы `count` и `parent` игнорируются. '''
        self.beginRemoveRows(QModelIndex(), row, row)
        self.cut_item(self.get_item(row))
        self.endRemoveRows()
        return True # ошибки обрабатываем исключениями

class SynonymsSetModel(BaseModel):
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

class SynonymsGroupsModel(BaseModel):
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    
class FlowsModel(BaseModel):
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

class ProxyModelReadOnly(BaseModel):
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return ~Qt.ItemFlag.ItemIsEditable & self.sourceModel().flags(index)
