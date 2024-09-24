from typing import Optional, Callable, Any
from dataclasses import dataclass
from alicetool.application.editor import ScenarioManipulator
from alicetool.infrastructure.qtgui.synonyms import SynonymsGroupsModel

from PySide6.QtCore import (
    Qt,
    Slot,
    QObject,
    QPoint,
    QModelIndex,
    QPersistentModelIndex,
    QRect,
    QPointF,
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
    
class SceneControll:
    __node_insert_index: int
    __new_step_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool]
    __new_state_callback: Callable[[QModelIndex, ItemData, SynonymsSetModel], bool]
    __select_input_callback: Callable[[],Optional[SynonymsSetModel]]
    __add_enter_callback: Callable[[QModelIndex], tuple[bool, Optional[SynonymsSetModel]]]
    __step_remove_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool] # state_from, state_to, input -> ok
    __update_lay_callback: Callable[['SceneNode', QPointF], None]

    __states_model: StatesModel
    __flows_model: FlowsModel

    __arrows: dict[Arrow, StepModel]
    __main_window: QWidget

    __manipulator: ScenarioManipulator

    def __init__(self,
                 manipulator: ScenarioManipulator,
                 select_input_callback: Callable[[],Optional[SynonymsSetModel]],
                 new_step_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool], 
                 step_remove_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool],
                 new_state_callback: Callable[[QModelIndex, ItemData, SynonymsSetModel], bool],
                 add_enter_callback: Callable[[QModelIndex], tuple[bool, Optional[SynonymsSetModel]]],
                 update_lay_callback: Callable[['SceneNode', QPointF], None],
                 states_model:StatesModel, 
                 flows_model: FlowsModel,
                 main_window: QWidget,
                ) -> None:
        self.__node_insert_index = 0
        self.__manipulator = manipulator
        self.__select_input_callback = select_input_callback
        self.__new_step_callback = new_step_callback
        self.__step_remove_callback = step_remove_callback
        self.__new_state_callback = new_state_callback
        self.__add_enter_callback = add_enter_callback
        self.__update_lay_callback = update_lay_callback

        self.__states_model = states_model
        self.__flows_model = flows_model

        self.__arrows = {}
        self.__main_window = main_window

    def state_settings(self, node: SceneNode):
        text, ok = QInputDialog.getText(self.__main_window, 'Переименовать состояние', 'Новое имя:')
        if not ok: return

        node.wrapper_widget().set_title(text)

    def init_arrows(self, scene:Editor, v_model: SynonymsGroupsModel):
        ''' создать стрелки переходов '''
        for row in range(self.__states_model.rowCount()):
            state_index = self.__states_model.index(row)

            node_from:SceneNode = state_index.data(CustomDataRole.Node)
            inputs_to = self.__manipulator.steps_from(state_index.data(CustomDataRole.Id))

            for state_id in inputs_to.keys():
                node_to = self.__states_model.get_item_by( CustomDataRole.Id, state_id ).on[CustomDataRole.Node]

                for input_name in inputs_to[state_id]:
                    s_model = v_model.get_item_by(CustomDataRole.Name, input_name).on[CustomDataRole.SynonymsSet]
                    self.on_add_step(scene, s_model, node_from, node_to)

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
                NodeWidget.START_WIDTH * (self.__node_insert_index) +
                scene.START_SPACINS * (self.__node_insert_index+1),
                scene.START_SPACINS
            )
            self.__node_insert_index += 1
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
        node.wrapper_widget().open_settings.connect(lambda: self.state_settings(node))
        node.set_handlers(lambda from_node, to_node: self.__new_step_request(from_node, to_node), lambda from_node, to_pos: self.__new_state_request(from_node, to_pos), lambda node, to_pos: self.__update_lay_callback(node, to_pos))
        content.setText(state_text)
        node.set_title(state_name)

        # связываем элемент сцены с элементом модели
        data.on[CustomDataRole.Node] = node

        # обновляем модель
        self.__states_model.prepare_item(data)
        self.__states_model.insertRow()

        content.textChanged.connect(lambda: self.__state_content_changed_handler(node))
        node.wrapper_widget().set_change_title_handler(lambda title: self.__state_title_changed_handler(node, title))

        return node
    
    def on_add_step(self, scene: Editor, input: SynonymsSetModel, from_node: SceneNode, to_node: SceneNode):
        ''' добавляет связь между объектами сцены и вектором перехода '''
        arrow = self.__find_arrow(from_node, to_node)

        if arrow is None:
            arrow = Arrow()
            scene.addItem(arrow)
            from_node.arrow_connect_as_start(arrow)
            to_node.arrow_connect_as_end(arrow)
            step_model = StepModel(arrow, from_node, to_node, scene)
            step_model.set_edit_callback(lambda i, r, o, n: True)
            self.__arrows[arrow] = step_model

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

    def on_add_enter(self, enter: ItemData):
        ''' добавляет элемент содержания '''
        self.__flows_model.prepare_item(enter)
        self.__flows_model.insertRow()

    def on_remove_node(self, node:SceneNode):
        ''' по изменениям в сценарии изменить модель и удалить элемент сцены '''
        scene = node.scene()
        state_index = self.find_in_model(node)
        if not state_index.isValid():
            return # вообще-то не норм ситуация

        if not self.__states_model.removeRow(state_index.row()):
            QMessageBox.warning(self.__main_window, 'Невозможно выполнить', 'Невозможно удалить состояние. Есть переходы связанные с ним!')
            return
        
        scene.removeItem(node)

    def on_remove_step(self, step_index: QModelIndex):
        ''' удаляет связь между объектами сцены и вектором перехода '''
        model:StepModel = step_index.model()
        step_index.data(CustomDataRole.SynonymsSet)
        self.find_in_model(model.node_from())
        if not self.__step_remove_callback(
                    self.find_in_model(model.node_from()),
                    self.find_in_model(model.node_to()),
                    step_index.data(CustomDataRole.SynonymsSet)
                ):
            return False
        
        if model.rowCount() == 1:
            self.__remove_arrow(model)
            
        return True

    def on_set_data(self, node:SceneNode, value:Any, role:int):
        ''' по изменениям в сценарии изменить модель и сцену '''
        model_index = self.find_in_model(node)
        if not model_index.isValid():
            return
        
        if role == CustomDataRole.Name:
            node.set_title(value)
        elif role == CustomDataRole.Text:
            content: QTextEdit = node.widget()
            content.setPlainText(value)
        
        self.__states_model.setData(model_index, value, role)

    def on_node_chosen(self, node:SceneNode):
        state_item_index = self.find_in_model(node)

        ok, s_model = self.__add_enter_callback(state_item_index)
        if not ok: return

        input_item = ItemData()
        input_item.on[CustomDataRole.Name] = state_item_index.data(CustomDataRole.Name)
        input_item.on[CustomDataRole.Description] = ''
        input_item.on[CustomDataRole.SynonymsSet] = s_model
        input_item.on[CustomDataRole.EnterStateId] = state_item_index.data(CustomDataRole.Id)
        input_item.on[CustomDataRole.SliderVisability] = False

        self.on_add_enter(input_item)

    def load_layout(self, data:str, id_map = None):
        for line in data.split(';\n'):
            line = line.replace(' ', '')
            id_sep = line.index(":")
            dir_sep = line.index(",")
            id = int(line[0 : id_sep])
            x = float(line[id_sep+3 : dir_sep])
            y = float(line[dir_sep+3 : -1])

            item = self.__states_model.get_item_by(CustomDataRole.Id, id if id_map is None else id_map[id])
            if not item is None:
                node: SceneNode = item.on[CustomDataRole.Node]
                node.setPos(x, y)
                node.update_arrows()

    def serialize_layout(self) -> str:
        ''' сертализует информацию об отображении элементов сцены '''
        result = list[str]()

        items_num = self.__states_model.rowCount()
        for row in range(items_num):
            index = self.__states_model.index(row)
            id: int = self.__states_model.data(index, CustomDataRole.Id)
            node: SceneNode = self.__states_model.data(index, CustomDataRole.Node)

            if node is None:
                continue
            
            pos = node.scenePos()
            result.append(f'{id}: x={pos.x()}, y={pos.y()};')
        
        return '\n'.join(result)

    def __find_arrow(self, from_node: SceneNode, to_node: SceneNode) -> Optional[Arrow]:
        ''' ищет связь между элементами сцены '''
        for step_model in self.__arrows.values():
            if step_model.node_from() == from_node and step_model.node_to() == to_node:
                return step_model.arrow()
                
        return None

    def find_in_model(self, node:SceneNode) -> QModelIndex:
        for row in range(self.__states_model.rowCount()):
            if self.__states_model.data(self.__states_model.index(row), CustomDataRole.Node) is node:
                return self.__states_model.index(row)
        
        return QModelIndex()

    def __state_content_changed_handler(self, node:SceneNode):
        ''' по изменениям на сцене изменить модель '''
        model_index = self.find_in_model(node)
        if not model_index.isValid():
            return
        
        editor: QTextEdit = node.widget()

        id = model_index.data(CustomDataRole.Id)
        role = CustomDataRole.Text
        new_value = editor.toPlainText()
        self.__states_model.setData(model_index, new_value, role)

    def __state_title_changed_handler(self, node:SceneNode, new_title:str) -> bool:
        ''' по изменениям на сцене изменить модель '''
        model_index = self.find_in_model(node)
        if not model_index.isValid():
            return False
        
        id = model_index.data(CustomDataRole.Id)
        role = CustomDataRole.Name
        new_value = new_title
        ok = self.__states_model.setData(model_index, new_value, role)
        return ok

    def __new_step_request(self, from_node:SceneNode, to_node:SceneNode):
        state_index_from = self.find_in_model(from_node)
        state_index_to = self.find_in_model(to_node)
        if state_index_from.isValid() and state_index_to.isValid():
            input = self.__select_input_callback()
            if input is None:
                return
            
            if self.__new_step_callback(state_index_from, state_index_to, input):
                self.on_add_step(from_node.scene(), input, from_node, to_node)
    
    def __new_state_request(self, from_node:SceneNode, to_pos: Optional[QPoint] = None):
        state_index_from = self.find_in_model(from_node)
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

    def __edit_connection(self, model:StepModel):
        dialog = StepEditor(model, self.__main_window)
        dialog.exec()
    