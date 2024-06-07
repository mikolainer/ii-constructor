import json
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

# TODO: унести в presentation layer
def role_by_str(string: str) -> CustomDataRole:
    if string == 'Id':
        return CustomDataRole.Id
    elif string == 'Name':
        return CustomDataRole.Name
    elif string == 'Description':
        return CustomDataRole.Description
    elif string == 'Text':
        return CustomDataRole.Text
    elif string == 'SynonymsSet':
        return CustomDataRole.SynonymsSet
    elif string == 'EnterStateId':
        return CustomDataRole.EnterStateId
    elif string == 'SliderVisability':
        return CustomDataRole.SliderVisability
    elif string == 'Node':
        return CustomDataRole.Node
    else:
        return None

# TODO: унести в presentation layer
def str_by_role(role: CustomDataRole) -> str:
    if role == CustomDataRole.Id:
        return 'Id'
    elif role == CustomDataRole.Name:
        return 'Name'
    elif role == CustomDataRole.Description:
        return 'Description'
    elif role == CustomDataRole.Text:
        return 'Text'
    elif role == CustomDataRole.SynonymsSet:
        return 'SynonymsSet'
    elif role == CustomDataRole.EnterStateId:
        return 'EnterStateId'
    elif role == CustomDataRole.SliderVisability:
        return 'SliderVisability'
    elif role == CustomDataRole.Node:
        return 'Node'
    else:
        return 'UnknownRole'

@verify(UNIQUE)
class DataType(IntEnum):
    ''' Указание на способ сериализации/десериализации '''
    Unknown: 'DataType' = 0
    State: 'DataType' = 1
    SynonymsGroup: 'DataType' = 2

class ItemData:
    ''' Обёртка над данными с использованием ролей '''
    on: dict[int, Any] # role, data
    def __init__(self) -> None:
        self.on = {}

    def to_json_string(self, d_type: DataType = DataType.Unknown) -> str:
        ''' Cериализует данные в json '''
        # TODO: унести в presentation layer
        data = {}

        for role in self.on.keys():
            if d_type == DataType.SynonymsGroup and role == CustomDataRole.SynonymsSet:
                model: SynonymsSetModel = self.on[CustomDataRole.SynonymsSet]
                synonyms = list[str]()
                for row in range(model.rowCount()):
                    synonyms.append(
                        model.data(model.index(row), CustomDataRole.Text)
                    )

                value = synonyms
            else:
                value = self.on[role]

            data[str_by_role(role)] = value

        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def from_json_str(json_str:str, type: DataType = DataType.Unknown) -> 'ItemData':
         # TODO: унести в presentation layer
        ''' Десериализует данные из json '''

    def update_from(self, json_str:str, type: DataType = DataType.Unknown) -> None:
         # TODO: унести в presentation layer
        '''
        Дополняет данными из другого источника.
        Например информацией для отображения объектов у конкретного клиента
        '''

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
            self.__index_by[role][item.on[role], item]

        return len(self.__data) -1 #self.__data.index(item)
    
    def cut_item(self, item:ItemData) -> None:
        ''' Удаляет `item` '''
        if not issubclass(type(item), ItemData):
            raise TypeError(item)
        
        self.__data.remove(item)
        for role in self.__index_roles:
            self.__index_by[role][item.on[role], item]
    
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

    def copy_default_item() -> ItemData:
        ''' Возвращает копию элемента по умолчанию '''

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
            return True

        self.get_item(index.row()).on[role] = value
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
        return super().removeRow(row, parent)
    
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
    