from typing import Optional, Callable, Any
from dataclasses import dataclass

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
    QInputDialog,
    QMessageBox,
)

from alicetool.infrastructure.qtgui.primitives.sceneitems import Arrow, SceneNode, NodeWidget, Editor
from alicetool.infrastructure.qtgui.data import ItemData, CustomDataRole, BaseModel, SynonymsSetModel
from alicetool.infrastructure.qtgui.flows import FlowsModel
from alicetool.infrastructure.qtgui.steps import StepModel, StepEditor

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
#    @dataclass
#    class __Connection:
#        arrow: Arrow
#        node_from: SceneNode
#        node_to: SceneNode
#        input: SynonymsSetModel

    # (state_id:int, value:Any, role:int) -> bool, Any # возвращает флаг успешности и старые данные
    __change_data_callback: Callable[[int, Any, int], tuple[bool, Any]]
    __new_step_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool]
    __new_state_callback: Callable[[QModelIndex, ItemData, SynonymsSetModel], bool]
    __select_input_callback: Callable[[],Optional[SynonymsSetModel]]
    __add_enter_callback: Callable[[QModelIndex], tuple[bool, Optional[SynonymsSetModel]]]
    __step_remove_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool] # state_from, state_to, input -> ok

    __states_model: StatesModel
    __flows_model: FlowsModel

    __arrows: dict[Arrow, StepModel]
    __main_window: QWidget

    def __init__(self,
                 select_input_callback: Callable[[],Optional[SynonymsSetModel]], 
                 change_data_callback: Callable[[int, Any, int], tuple[bool, Any]], 
                 new_step_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool], 
                 step_remove_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool],
                 new_state_callback: Callable[[QModelIndex, ItemData, SynonymsSetModel], bool],
                 add_enter_callback: Callable[[QModelIndex], tuple[bool, Optional[SynonymsSetModel]]],
                 states_model:StatesModel, 
                 flows_model: FlowsModel,
                 main_window: QWidget,
                ) -> None:
        self.__select_input_callback = select_input_callback
        self.__change_data_callback = change_data_callback
        self.__new_step_callback = new_step_callback
        self.__step_remove_callback = step_remove_callback
        self.__new_state_callback = new_state_callback
        self.__add_enter_callback = add_enter_callback

        self.__states_model = states_model
        self.__flows_model = flows_model
        self.__arrows = {}
        self.__main_window = main_window

    def __find_in_model(self, node:SceneNode) -> QModelIndex:
        for row in range(self.__states_model.rowCount()):
            if self.__states_model.data(self.__states_model.index(row), CustomDataRole.Node) is node:
                return self.__states_model.index(row)
        
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
        self.__states_model.setData(model_index, new_value if success else old_value, role)
        if not success: self.__states_model.setData(model_index, old_value, role)

    def __state_title_changed_handler(self, node:SceneNode, new_title:str):
        ''' по изменениям на сцене изменить модель '''
        model_index = self.__find_in_model(node)
        if not model_index.isValid():
            return
        
        id = model_index.data(CustomDataRole.Id)
        role = CustomDataRole.Name
        new_value = new_title
        success, old_value = self.__change_data_callback(id, new_value, role)
        self.__states_model.setData(model_index, new_value if success else old_value, role)
        if not success: self.__states_model.setData(model_index, old_value, role)

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
        
        self.__states_model.setData(model_index, value, role)

    def on_insert_node(self, scene: Editor, data:ItemData, enter_data:list[ItemData] = [], pos: Optional[QPoint] = None) -> SceneNode:
        ''' по изменениям в сценарии изменить модель и добавить элемент сцены '''

        # добавление элемента модели содержания
        for enter in enter_data:
            self.on_add_enter(enter)

        # должно быть установлено
        state_id = data.on[CustomDataRole.Id]
        state_name = data.on[CustomDataRole.Name]
        state_text = data.on[CustomDataRole.Text]

        if pos is None:
            pos = QPoint(
                NodeWidget.START_WIDTH * (state_id) +
                scene.START_SPACINS * (state_id+1),
                scene.START_SPACINS
            )
        else:
            pos.setX(pos.x() - (NodeWidget.START_WIDTH/2))
            pos.setY(pos.y() - (NodeWidget.START_WIDTH/2))

        if pos.x() < 0:
            pos.setX(0)

        if pos.y() < 0:
            pos.setY(0)
        
        # создаём элемент сцены
        content = QTextEdit()
        node = scene.addNode(pos, content)
        node.wrapper_widget().delete_request.connect(lambda node: self.on_remove_node(node))
        node.wrapper_widget().chosen.connect(lambda node: self.on_node_chosen(node))
        node.set_handlers(lambda from_node, to_node: self.__new_step_request(from_node, to_node), lambda from_node, to_pos: self.__new_state_request(from_node, to_pos))
        content.setText(state_text)
        node.set_title(state_name)

        # связываем элемент сцены с элементом модели
        data.on[CustomDataRole.Node] = node

        # обновляем модель
        self.__states_model.prepare_item(data)
        self.__states_model.insertRow()

        content.textChanged.connect(lambda: self.__state_content_changed_handler(node))
        node.wrapper_widget().title_changed.connect(lambda title: self.__state_title_changed_handler(node, title))

        return node

    def __new_step_request(self, from_node:SceneNode, to_node:SceneNode):
        state_index_from = self.__find_in_model(from_node)
        state_index_to = self.__find_in_model(to_node)
        if state_index_from.isValid() and state_index_to.isValid():
            input = self.__select_input_callback()
            if input is None:
                return
            
            if self.__new_step_callback(state_index_from, state_index_to, input):
                self.on_add_step(from_node.scene(), input, from_node, to_node)
    
    def __new_state_request(self, from_node:SceneNode, to_pos: Optional[QPoint] = None):
        state_index_from = self.__find_in_model(from_node)
        if state_index_from.isValid():
            new_state_item = ItemData()
            name, ok = QInputDialog.getText(None, 'Ввод имени', 'Имя нового состояния')
            if not ok: return
            new_state_item.on[CustomDataRole.Name] = name

            input = self.__select_input_callback()
            if input is None: return
            
            if self.__new_state_callback(state_index_from, new_state_item, input):
                to_node = self.on_insert_node(from_node.scene(), new_state_item, [], to_pos)
                self.on_add_step(from_node.scene(), input, from_node, to_node)

    def init_arrows(self, scene:Editor):
        for row in range(self.__states_model.rowCount()):
            state_index = self.__states_model.index(row)

            node_from:SceneNode = state_index.data(CustomDataRole.Node)
            
            for step_item in state_index.data(CustomDataRole.Steps):
                ''' step_item.on[CustomDataRole.<...>]
                FromState - id состояния (int) или None
                ToState - id cocтояния (int)
                SynonymsSet - input (SynonymsSetModel)
                '''
                step_input = step_item.on[CustomDataRole.SynonymsSet]

                if step_item.on[CustomDataRole.FromState] != state_index.data(CustomDataRole.Id): continue

                node_to = self.__states_model.get_item_by(
                    CustomDataRole.Id, step_item.on[CustomDataRole.ToState]
                ).on[CustomDataRole.Node]

                self.on_add_step(scene, step_input, node_from, node_to)

    def __find_arrow(self, from_node: SceneNode, to_node: SceneNode) -> Optional[Arrow]:
        ''' ищет связь между элементами сцены '''
        for step_model in self.__arrows.values():
            if step_model.node_from() == from_node and step_model.node_to() == to_node:
                return step_model.arrow()
                
        return None

    def __edit_connection(self, model:StepModel):
        dialog = StepEditor(model, self.__main_window)
        dialog.exec()

    def on_add_step(self, scene: Editor, input: SynonymsSetModel, from_node: SceneNode, to_node: SceneNode):
        ''' добавляет связь между объектами сцены и вектором перехода '''
        arrow = self.__find_arrow(from_node, to_node)

        if arrow is None:
            arrow = Arrow()
            scene.addItem(arrow)
            from_node.arrow_connect_as_start(arrow)
            to_node.arrow_connect_as_end(arrow)
            step_model = StepModel(arrow, from_node, to_node, scene)
            self.__arrows[arrow] = step_model
            step_model.rowsInserted.connect(lambda parent_index,first,last: self.__step_added_handler(step_model, first))

            step_model.set_remove_callback(lambda index: self.on_remove_step(index))
            arrow.set_edit_connection_handler(lambda: self.__edit_connection(step_model))

        else:
            step_model = self.__arrows[arrow]

        if not step_model.get_item_by(CustomDataRole.SynonymsSet, input) is None:
            # вообще-то не норм ситуация (должно обрабатываться ядром)
            QMessageBox.warning(self.__main_window, 'Ошибка', 'Шаг уже существует')
            return

        step_item = ItemData()
        step_item.on[CustomDataRole.SynonymsSet] = input
        step_model.prepare_item(step_item)
        step_model.insertRow()
        

    def __step_added_handler(self, model:StepModel, row: int):
        state_index_from = self.__find_in_model(model.node_from())
        state_index_to = self.__find_in_model(model.node_to())
        from_state_id =  state_index_from.data(CustomDataRole.Id)
        to_state_id = state_index_to.data(CustomDataRole.Id)
        
        step_item = model.get_item(row)
        step_item.on[CustomDataRole.FromState] = from_state_id
        step_item.on[CustomDataRole.ToState] = to_state_id

        state_index_from.data(CustomDataRole.Steps).append(step_item)
        state_index_to.data(CustomDataRole.Steps).append(step_item)


    def on_remove_step(self, step_index: QModelIndex):
        ''' удаляет связь между объектами сцены и вектором перехода '''
        model:StepModel = step_index.model()
        step_index.data(CustomDataRole.SynonymsSet)
        self.__find_in_model(model.node_from())
        if not self.__step_remove_callback(
                    self.__find_in_model(model.node_from()),
                    self.__find_in_model(model.node_to()),
                    step_index.data(CustomDataRole.SynonymsSet)
                ):
            return False

        if model.rowCount() == 1:
            self.__remove_arrow(model)
            
        return True
    
    def __remove_arrow(self, model:StepModel):
        ''' удаляет все упоминания стрелки '''

        arrow = model.arrow()

        # в связанных элементах сцены
        model.node_from().arrow_disconnect(arrow)
        model.node_to().arrow_disconnect(arrow)

        # на сцене
        editor = arrow.scene()
        editor.removeItem(arrow)

        # в индексе
        self.__arrows.pop(arrow)

    def on_add_enter(self, enter: ItemData):
        ''' добавляет элемент содержания '''
        self.__flows_model.prepare_item(enter)
        self.__flows_model.insertRow()

    def on_remove_enter(self, node:SceneNode):
        ''' удаляет элемент содержания связанный с объектом сцены '''
        pass

    def on_remove_node(self, node:SceneNode):
        ''' по изменениям в сценарии изменить модель и удалить элемент сцены '''
#        scene = node.scene()
#        model_index = self.__find_in_model(node)
#        if model_index.isValid():
#            self.__states_model.removeRow(model_index.row())
#
#        scene.removeItem(node)

    def on_node_chosen(self, node:SceneNode):
        state_item_index = self.__find_in_model(node)

        ok, s_model = self.__add_enter_callback(state_item_index)
        if not ok: return

        input_item = ItemData()
        input_item.on[CustomDataRole.Name] = state_item_index.data(CustomDataRole.Name)
        input_item.on[CustomDataRole.Description] = ''
        input_item.on[CustomDataRole.SynonymsSet] = s_model
        input_item.on[CustomDataRole.EnterStateId] = state_item_index.data(CustomDataRole.Id)
        input_item.on[CustomDataRole.SliderVisability] = False

        self.on_add_enter(input_item)
