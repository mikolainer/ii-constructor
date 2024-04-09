from enum import IntEnum, verify, UNIQUE
from typing import Any, List, Union

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
    Id              : 'CustomDataRole' = Qt.ItemDataRole.UserRole,      # int
    Name            : 'CustomDataRole' = Qt.ItemDataRole.UserRole +1,   # str
    Description     : 'CustomDataRole' = Qt.ItemDataRole.UserRole +2,   # str
    Text            : 'CustomDataRole' = Qt.ItemDataRole.UserRole +3,   # str
    SynonymsSet     : 'CustomDataRole' = Qt.ItemDataRole.UserRole +4,   # SynonymsSetModel
    EnterStateId    : 'CustomDataRole' = Qt.ItemDataRole.UserRole +5,   # int
    SliderVisability: 'CustomDataRole' = Qt.ItemDataRole.UserRole +6,   # bool


class SynonymsSetModel(QAbstractItemModel):
    __data: list[str]

    __group_id: int | None # связанная группа синонимов
    __flow_id:  int | None # связанный поток (Flow)
    
    def __init__( self,
        values: list[str] = [],
        group_id: int = None,
        flow_id: int = None,
        parent: QObject | None = None
    ) -> None:
        
        super().__init__(parent)
        self.__data = values
        self.__group_id = group_id
        self.__flow_id = flow_id

    def parent(self, child: Union[QModelIndex, QPersistentModelIndex]) -> QModelIndex:
        return QModelIndex()

    def index(self, row: int, column: int = 0, parent: QModelIndex | QPersistentModelIndex = None) -> QModelIndex:
        if not row in range(len(self.__data)):
            return QModelIndex()

        return self.createIndex(row, column, self.__data[row])
    
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        return len(self.__data)
    
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        return 1
    
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = CustomDataRole.Text) -> Any:
        if not index.isValid():
            return None
        
        if index.row() in range(len(self.__data)) and role in [CustomDataRole.Text, Qt.ItemDataRole.DisplayRole]:
            return self.__data[index.row()]
    
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = CustomDataRole.Text) -> bool:
        if role in [CustomDataRole.Text, Qt.ItemDataRole.EditRole] and index.row() in range(len(self.__data)):
            self.__data[index.row()] = value
            return True

        return False
    
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    
    def insertRows(self, row: int, count: int, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> bool:

        self.beginInsertRows(self.index(row-1), row, row+count-1)
        for i in range(count):
            self.__data.append("")
        self.endInsertRows()

        return super().insertRows(row, count, parent)

class SynonymsGroupsModel(QAbstractItemModel):
    class Item:
        ''' Id, Name, Description, SynonymsSet '''
        on: dict[CustomDataRole, Any]
        def __init__(self) -> None:
            self.on = {}

    __data : dict[int, Item]

    def __init__(self, data: dict[int, Item] = {}, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.__data = data

    def parent(self, child: Union[QModelIndex, QPersistentModelIndex]) -> QModelIndex:
        return QModelIndex()

    def index(self, row: int, column: int = 0, parent: QModelIndex | QPersistentModelIndex = None) -> QModelIndex:
        if not row in range(len(self.__data)):
            return QModelIndex()
        
        for idx, data in enumerate(self.__data.values()):
            if idx == row:
                return self.createIndex(row, column, data)
    
        return QModelIndex()
    
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        return len(self.__data)
    
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        return 1
    
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = CustomDataRole.Name) -> Any:
        if not index.isValid():
            return None
        
        for idx, data in enumerate(self.__data.values()):
            if idx == index.row():
                return data.on[role] if role in data.on.keys() else None

        return None
    
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = ...) -> bool:
        for idx, data in enumerate(self.__data.values()):
            if idx == index.row():
                data.on[role] = value
                return True
        
        return False
    
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    
class FlowsModel(QAbstractItemModel):
    class Item:
        ''' Id, Name, Description, SynonymsSet '''
        on: dict[CustomDataRole, Any]
        def __init__(self) -> None:
            self.on = {}

    __data : dict[int, Item]

    def __init__(self, data: dict[int, Item] = {}, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.__data = data

    def parent(self, child: Union[QModelIndex, QPersistentModelIndex]) -> QModelIndex:
        return QModelIndex()

    def index(self, row: int, column: int = 0, parent: QModelIndex | QPersistentModelIndex = None) -> QModelIndex:
        if not row in range(len(self.__data)):
            return QModelIndex()
        
        for idx, item in enumerate(self.__data.values()):
            if idx == row:
                return self.createIndex(row, column, item)
    
        return QModelIndex()
    
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        return len(self.__data)
    
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = None) -> int:
        return 1
    
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = CustomDataRole.Text) -> Any:
        if not index.isValid():
            return None
        
        for idx, data in enumerate(self.__data.values()):
            if idx == index.row():
                # setted data
                if role in data.on.keys():
                    return data.on[role]
                # default values
                elif role == CustomDataRole.SliderVisability:
                    return False
                # not setted and no default describtion
                else:
                    return None

        return None
    
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = ...) -> bool:
        for idx, data in enumerate(self.__data.values()):
            if idx == index.row():
                data.on[role] = value
                return True
        
        return False
    
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable


class ProxyModelReadOnly(QIdentityProxyModel):
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return ~Qt.ItemFlag.ItemIsEditable & self.sourceModel().flags(index)
