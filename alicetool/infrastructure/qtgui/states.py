from typing import Optional, Callable, Any

from PySide6.QtCore import (
    Qt,
    Slot,
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

from alicetool.infrastructure.qtgui.primitives.sceneitems import Arrow, SceneNode, NodeWidget, Editor
from alicetool.infrastructure.qtgui.data import ItemData, CustomDataRole, BaseModel

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
    
class StatesControll:
    # (state_id:int, value:Any, role:int) -> bool, Any # возвращает флаг успешности и старые данные
    __change_data_callback: Callable[[int, Any, int], tuple[bool, Any]]

    __model: StatesModel

    def __init__(self, change_data_callback: Callable[[int, Any, int], tuple[bool, Any]], model:StatesModel) -> None:
        self.__change_data_callback = change_data_callback
        self.__model = model

    def __find_in_model(self, node:SceneNode) -> QModelIndex:
        for row in range(self.__model.rowCount()):
            if self.__model.data(self.__model.index(row), CustomDataRole.Node) is node:
                return self.__model.index(row)
        
        return QModelIndex()

    def __state_content_changed_handler(self, node:SceneNode):
        ''' по изменениям на сцене изменить модель '''
        model_index = self.__find_in_model(node)
        if not model_index.isValid():
            return
        
        editor: QTextEdit = node.widget()

        id = model_index.data(CustomDataRole.Id)
        role = CustomDataRole.Text
        new_value = editor.toPlainText()
        success, old_value = self.__change_data_callback(id, new_value, role)
        self.__model.setData(model_index, new_value if success else old_value, role)
        if not success: self.__model.setData(model_index, old_value, role)

    def __state_title_changed_handler(self, node:SceneNode, new_title:str):
        ''' по изменениям на сцене изменить модель '''
        model_index = self.__find_in_model(node)
        if not model_index.isValid():
            return
        
        id = model_index.data(CustomDataRole.Id)
        role = CustomDataRole.Name
        new_value = new_title
        success, old_value = self.__change_data_callback(id, new_value, role)
        self.__model.setData(model_index, new_value if success else old_value, role)
        if not success: self.__model.setData(model_index, old_value, role)

    def on_set_data(self, node:SceneNode, value:Any, role:int):
        ''' по изменениям в сценарии изменить модель и сцену '''
        model_index = self.__find_in_model(node)
        if not model_index.isValid():
            return
        
        if role == CustomDataRole.Name:
            node.set_title(value)
        elif role == CustomDataRole.Text:
            content: QTextEdit = node.widget()
            content.setPlainText(value)
        
        self.__model.setData(model_index, value, role)

    def on_insert_node(self, scene: Editor, data:ItemData):
        ''' по изменениям в сценарии изменить модель и добавить элемент сцены '''
        # должно быть установлено
        state_id = data.on[CustomDataRole.Id]
        state_name = data.on[CustomDataRole.Name]
        state_text = data.on[CustomDataRole.Text]

        # TODO: обрабатывать сохранённый layout
        pos = QPoint(
            NodeWidget.START_WIDTH * (state_id) +
            scene.START_SPACINS * (state_id+1),
            scene.START_SPACINS
        )
        
        # создаём элемент сцены
        content = QTextEdit()
        node = scene.addNode(pos, content)
        content.setText(state_text)
        node.set_title(state_name)

        # связываем элемент сцены с элементом модели
        data.on[CustomDataRole.Node] = node

        # обновляем модель
        self.__model.prepare_item(data)
        self.__model.insertRow()

        content.textChanged.connect(lambda: self.__state_content_changed_handler(node))
        node.wrapper_widget().title_changed.connect(lambda title: self.__state_title_changed_handler(node, title))

    def on_remove_node(self, scene: Editor, node:SceneNode):
        ''' по изменениям в сценарии изменить модель и удалить элемент сцены '''
        
        model_index = self.__find_in_model(node)
        if model_index.isValid():
            self.__model.removeRow(model_index.row())

        scene.removeItem(node)
