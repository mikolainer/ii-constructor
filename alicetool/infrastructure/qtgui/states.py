from typing import Optional

from PySide6.QtCore import (
    Qt,
    QObject,
    QPoint,
    QModelIndex,
    QPersistentModelIndex,
    QRect,
)

from PySide6.QtGui import (
    QColor,
    
)

from PySide6.QtWidgets import (
    QWidget,
    QGraphicsScene,
    QTextEdit,
    QGraphicsSceneMouseEvent,
)

from .primitives.sceneitems import Arrow, SceneNode, NodeWidget
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

        self._data_init(required_roles=roles)

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

class Editor(QGraphicsScene):
    __START_SIZE = QRect(0, 0, 2000, 2000)
    __START_SPACINS = 30

    ''' Сцена состояний и переходов сценария '''
    __model: Optional[StatesModel]

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent)
        self.setSceneRect(self.__START_SIZE)
        self.setBackgroundBrush(QColor("#DDDDDD"))
        #self.addNode(QPoint(100, 100), QTextEdit())
        self.__model = None
    
    def setStatesModel(self, model: StatesModel):
        ''' Устанавливает модель для регистрации и отслеживания изменений состояний и связей. (на сцене и в источнеике данных) '''
        self.__model = model

        for row in range(model.rowCount()):
            state_id = self.__model.data(self.__model.index(row), CustomDataRole.Id)
            state_name = self.__model.data(self.__model.index(row), CustomDataRole.Name)
            state_text = self.__model.data(self.__model.index(row), CustomDataRole.Text)
            # TODO: initStateConnections
            # TODO: initStatePos
            pos = QPoint(
                        NodeWidget.START_WIDTH * (state_id - 1) +
                        self.__START_SPACINS * (state_id),
                        self.__START_SPACINS
                    )

            node = self.__addNode(pos)
            node.set_title(state_name)
            
            content = QTextEdit()
            content.setText(state_text)
            node.setWidget(content)

            self.__model.setData(self.__model.index(row), node, CustomDataRole.Node)

    def setStepsModel(self, model):
        pass

    def __addNode(self, pos:QPoint, content:QWidget = None) -> SceneNode:
        ''' Добавляет вершину графа на сцену '''
        node = SceneNode(self)
        
        if not content is None:
            node.setWidget(content)
        
        # TODO: по умолчанию под указателем мыши
        node.setPos(pos.x(), pos.y())

        return node