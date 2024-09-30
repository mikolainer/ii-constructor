from typing import Optional, Callable, Any
from dataclasses import dataclass

from PySide6.QtCore import (
    Qt,
    QObject,
    QModelIndex,
    QPersistentModelIndex,
)

from .data import CustomDataRole, BaseModel

class StatesModel(BaseModel):
    ''' Модель состояний. Для обработки сценой (Editor) '''
    def __init__( self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        roles: list[CustomDataRole] = [
            CustomDataRole.Id,
            CustomDataRole.Name,
            CustomDataRole.Text
        ]

        self._data_init(index_roles=roles)

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
 