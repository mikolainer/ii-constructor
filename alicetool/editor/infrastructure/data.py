from enum import IntEnum, verify, UNIQUE
from typing import Any, Union

from PySide6.QtCore import (
    Qt, Slot, Signal,
    QModelIndex,
    QObject,
    QPersistentModelIndex, 
    QAbstractItemModel,
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
    Data = list[str]
    __data: Data

    __group_id: int | None # связанная группа синонимов
    __flow_id:  int | None # связанный поток (Flow)
    
    def __init__( self,
        values:Data = [],
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

        return self.createIndex(row, column, self.__data)
    
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
    

class SynonymsGroupsModel(QAbstractItemModel): pass
class FlowsModel(QAbstractItemModel): pass