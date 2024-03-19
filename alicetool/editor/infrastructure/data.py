from enum import IntEnum, verify, UNIQUE
from typing import Any, List, Sequence, Union

from PySide6.QtCore import (
    QMimeData, Qt, Slot, Signal,
    QModelIndex,
    QObject,
    QPersistentModelIndex, 
    QAbstractItemModel,
    QSize,
)

from PySide6.QtGui import (
    QCloseEvent,
    QEnterEvent,
    QHideEvent,
    QMouseEvent,
    QResizeEvent,
    QShowEvent,
    QPixmap,
    QPainter,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
    QAbstractItemDelegate,
)

@verify(UNIQUE)
class CustomDataRole(IntEnum):
    Id          : 'CustomDataRole' = Qt.ItemDataRole.UserRole,      # int
    Name        : 'CustomDataRole' = Qt.ItemDataRole.UserRole +1,   # str
    Description : 'CustomDataRole' = Qt.ItemDataRole.UserRole +2,   # str
    Text        : 'CustomDataRole' = Qt.ItemDataRole.UserRole +3,   # str
    SynonymsSet : 'CustomDataRole' = Qt.ItemDataRole.UserRole +4,   # SynonymsSetModel


class SynonymsSetModel(QAbstractItemModel):
    __data: list[str]

    __group_id: int | None # связанная группа синонимов
    __flow_id:  int | None # связанный поток (Flow)
    
    def __init__( self,
        values: list[str] = [],
        group_id:int = None,
        flow_id:int = None,
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
        
        if role in [Qt.ItemDataRole.DisplayRole, CustomDataRole.Text, Qt.ItemDataRole.EditRole]:
            return self.__data[index.row()]

        return None
    
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEnabled
    

class SynonymsGroupsModel(QAbstractItemModel):
    __custom_roles = list[CustomDataRole]

    class Item:
        ''' Id, Name, Description, SynonymsSet '''
        on: dict[CustomDataRole, Any]
        def __init__(self) -> None:
            self.on = {}

    __data : dict[int, Item]

    def __init__(self, data: dict[int, Item] = {}, parent: QObject | None = None) -> None:
        self.__custom_roles = [
            CustomDataRole.Id,
            CustomDataRole.Name,
            CustomDataRole.Description,
            CustomDataRole.SynonymsSet
        ]

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
    
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = CustomDataRole.Text) -> Any:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.SizeHintRole:
            return QSize(40, 40)
        
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
        on: dict[CustomDataRole: Any]
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

        if role in [Qt.ItemDataRole.DisplayRole, CustomDataRole.Text, Qt.ItemDataRole.EditRole]:
            for idx, item in enumerate(self.__data.values()):
                if idx == index.row():
                    return item.on[CustomDataRole.Text]

        return None
    
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEnabled