from io import TextIOWrapper
from typing import Callable, Any, Optional

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QGraphicsView, QDialog, QInputDialog, QMessageBox, QFileDialog 
from PySide6.QtCore import Slot, Qt, QModelIndex, Slot

from alicetool.infrastructure.qtgui.primitives.sceneitems import Arrow, Editor, SceneNode
from alicetool.infrastructure.qtgui.data import CustomDataRole, ItemData, SynonymsSetModel
from alicetool.infrastructure.qtgui.flows import FlowsView, FlowListWidget, FlowsModel
from alicetool.infrastructure.qtgui.synonyms import SynonymsSelector, SynonymsEditor, SynonymsGroupsModel
from alicetool.infrastructure.qtgui.states import StatesModel, StatesControll
from alicetool.infrastructure.qtgui.main_w import FlowList, MainWindow, Workspaces, NewProjectDialog
from alicetool.application.editor import ScenarioFactory, SourceControll
from alicetool.application.data import ItemDataSerializer
from alicetool.domain.core.bot import Scenario, State, PossibleInputs, Connection, Step, InputDescription, Output, Answer
from alicetool.domain.core.primitives import Name, Description, ScenarioID, StateID, StateAttributes
from alicetool.domain.inputvectors.levenshtain import LevenshtainVector, Synonym, LevenshtainVectorSerializer, SynonymsGroup

class Project:
    __synonym_create_callback: Callable
    __connect_synonym_changes_callback: Callable
    __scene: Editor
    __flows_wgt: FlowListWidget
    __save_callback: Callable

    vectors_model: SynonymsGroupsModel
    
    def __init__(
        self,
        synonym_create_callback: Callable,
        connect_synonym_changes_callback: Callable,
        scene: Editor,
        content: FlowListWidget,
        save_callback: Callable
    ):
        self.vectors_model = SynonymsGroupsModel()

        self.__scene = scene
        self.__flows_wgt = content

        self.__synonym_create_callback = synonym_create_callback
        self.__connect_synonym_changes_callback = connect_synonym_changes_callback
        self.__save_callback = save_callback


    def id(self) -> ScenarioID:
        return self.__id
    
    def editor(self) -> Editor:
        return self.__scene
    
    def content(self) -> FlowListWidget:
        return self.__flows_wgt
    
    def edit_inputs(self):
        editor = SynonymsEditor(
            self.vectors_model,
            self.__create_synonyms_group,
            self.__create_synonym,
            self.__scene.parent()
        )
        editor.show()

    def choose_input(self) -> Optional[SynonymsSetModel]:
        dialog = SynonymsSelector(self.vectors_model, self.__create_synonyms_group, self.__scene.parent())
        dialog.exec()
        return dialog.selected_item()

    def __ask_new_vector_name(self, model:SynonymsGroupsModel) -> str:
        name:str = ''
        prev_name = ''

        while name == '':
            name, ok = QInputDialog.getText(
                self.__scene.parent(),
                'Новый набор синонимов',
                'Название',
                text= prev_name
            )

            if not ok: raise Warning('ввод отменён')
            if not model.get_item_by(CustomDataRole.Name, name) is None:
                QMessageBox.warning(self.__scene.parent(), 'Ошибка',
                    f'Рруппа синонимов с именем "{name}" уже существует!')
                prev_name = name
                name = ''
        
        return name
        

    def __create_synonyms_group(self, model:SynonymsGroupsModel):
        name:str

        try:
            name = self.__ask_new_vector_name(model)
        except Warning:
            return

        s_model = SynonymsSetModel()

        item = ItemData()
        item.on[CustomDataRole.Name] = name
        item.on[CustomDataRole.Description] = ""
        item.on[CustomDataRole.SynonymsSet] = s_model
        model.prepare_item(item)
        model.insertRow()

        self.__connect_synonym_changes_callback(s_model)

    def __create_synonym(self, model:SynonymsSetModel):
        default_value = 'значение'

        item = ItemData()
        item.on[CustomDataRole.Text] = default_value
        model.prepare_item(item)
        model.insertRow()

        self.__synonym_create_callback(model, item)

    def scene(self) -> Editor:
        return self.__scene
    
    def save_to_file(self):
        self.__save_callback()

class ProjectManager:
    # открытые проекты
    __projects: dict[QGraphicsView, Project]

    __main_window: MainWindow
    __workspaces: Workspaces
    __flow_list: FlowList
    __esc_sqortcut: QShortcut

    def __init__( self, flow_list: FlowList, workspaces: Workspaces, main_window: MainWindow ) -> None:
        self.__workspaces = workspaces
        self.__main_window = main_window
        self.__flow_list = flow_list

        self.__projects = {}

        self.__workspaces.currentChanged.connect(self.on_cur_changed)

        self.__esc_sqortcut = QShortcut(self.__main_window)
        self.__esc_sqortcut.setKey(Qt.Key.Key_Escape)
        self.__esc_sqortcut.activated.connect(lambda: self.__reset_enter_create_mode())

    @Slot(int)
    def on_cur_changed(self, index: int):
        if index == -1:
            return
        
        proj = self.__projects[ self.__workspaces.widget(index) ]
        self.__flow_list.setWidget(proj.content(), True)

        #self.__flow_list.setCurrentWidget(
        #    self.__projects[
        #        self.__workspaces.widget(index)
        #    ].content()
        #)

    def current(self) -> Project:
        return self.__projects[self.__workspaces.currentWidget()]

    def set_current(self, proj:Project):
        self.__workspaces.setCurrentWidget(proj.editor())
        self.__flow_list.setCurrentWidget(proj.content())

    def __create_enter_handler(self, flows_model:FlowsModel, project: Project):
        self.__set_enter_create_mode()

    def __set_enter_create_mode(self):
        self.__main_window.set_only_editor_enabled(True)

        scene = proj = self.current().editor()
        for item in scene.items():
            if not isinstance(item, SceneNode):
                continue

            item.set_choose_mode(True)

    def __reset_enter_create_mode(self):
        self.__main_window.set_only_editor_enabled(False)

        scene = proj = self.current().editor()
        for item in scene.items():
            if not isinstance(item, SceneNode):
                continue

            item.set_choose_mode(False)

    def __save_scenario_handler(self, scenario: Scenario):
        path, filetype = QFileDialog.getSaveFileName(self.__main_window, 'Сохранить в файл', 'Новый сценарий')
        with open(path, "w") as file:
            file.write(SourceControll.serialize(scenario))


    def __open_project(self, scenario: Scenario):
        content_view = FlowsView(self.__flow_list)
        flows_model = FlowsModel(self.__main_window)
        content_view.setModel(flows_model)
        content_wgt = FlowListWidget(content_view)
        self.__flow_list.setWidget(content_wgt, True)
        
        # создание объекта взаимодействий с проектом
        proj = Project(
            lambda model, data: self.__on_synonym_created_from_gui(proj, scenario, model, data),
            lambda model: self.__connect_synonym_changes_from_gui(proj, scenario, model),
            Editor(self.__main_window),
            content_wgt,
            lambda: self.__save_scenario_handler(scenario)
        )

        # создание обработчика изменений на сцене
        states_controll = StatesControll(
            lambda: proj.choose_input(),

            lambda state_id, value, role:
                self.__on_state_changed_from_gui(scenario, state_id, value, role),
            
            lambda from_state_index, to_state_index, input: self.__on_step_to_created_from_gui(scenario, proj, from_state_index, to_state_index, input),
            lambda from_state_index, to_state_item, input: self.__on_step_created_from_gui(scenario, proj, from_state_index, to_state_item, input), 

            lambda state_index: self.__on_enter_created_from_gui(scenario, proj, state_index),

            StatesModel(self.__main_window),
            flows_model,
            self.__main_window
        )

        editor = QGraphicsView(proj.scene(), self.__workspaces)
        editor.centerOn(0, 0)
        editor.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        content_wgt.create_value.connect(lambda: self.__create_enter_handler(flows_model, proj))

        self.__projects[editor] = proj # важно добавить перед addTab() для коттектной работы слота "current_changed"
        self.__workspaces.addTab(editor, scenario.name.value)

        ### векторы переходов
        ## наполнение представления
        for vector in scenario.inputs().get():
            # пока только левенштейн
            serialiser = LevenshtainVectorSerializer()

            if isinstance(vector, LevenshtainVector):
                vector_item = serialiser.to_data(vector)
                vector_item.on[CustomDataRole.Description] = ''
                proj.vectors_model.prepare_item(vector_item)
                proj.vectors_model.insertRow()

                synonyms_model:SynonymsSetModel = vector_item.on[CustomDataRole.SynonymsSet]
                self.__connect_synonym_changes_from_gui(proj, scenario, synonyms_model)
        
        ## обработчик изменений
        proj.vectors_model.rowsInserted.connect(
            lambda parent, first, last:
                self.__on_vector_created_from_gui(scenario, proj.vectors_model.index(first))
        )

        ### сцена (состояния и переходы)
        ## наполнение представления
        for state in scenario.states().values():
            input_items = list[ItemData]()

            # подготовка шагов для модели состояний
            steps = list[ItemData]()
            for step in scenario.steps(state.id()):
                conn = step.connection
                if conn is None:
                    continue # вообще-то не норм ситуация. возможно стоит бросать исключение
                step_item = ItemData()

                step_item.on[CustomDataRole.FromState] = None if step.connection.from_state is None else step.connection.from_state.id().value
                step_item.on[CustomDataRole.ToState] = step.connection.to_state.id().value
                vector_data = proj.vectors_model.get_item_by(
                    CustomDataRole.Name, step.input.name().value
                )
                s_model = vector_data.on[CustomDataRole.SynonymsSet]
                step_item.on[CustomDataRole.SynonymsSet] = s_model

                steps.append(step_item)

                if step.connection.from_state is None:
                    # формирование элемента модели содержания
                    input_item = ItemData()
                    input_item.on[CustomDataRole.Name] = state.attributes.name.value
                    input_item.on[CustomDataRole.Description] = state.attributes.desrciption.value
                    input_item.on[CustomDataRole.SynonymsSet] = s_model
                    input_item.on[CustomDataRole.EnterStateId] = state.id().value
                    input_item.on[CustomDataRole.SliderVisability] = False
                    input_items.append(input_item)
            
            # формирование элемента модели состояний
            item = ItemData()
            item.on[CustomDataRole.Id] = state.id().value
            item.on[CustomDataRole.Name] = state.attributes.name.value
            item.on[CustomDataRole.Text] = state.attributes.output.value.text
            item.on[CustomDataRole.Steps] = steps

            # добавление элемента модели состояний
            states_controll.on_insert_node(proj.scene(), item, input_items)

        states_controll.init_arrows(proj.scene())

    def create_project(self) -> Project:
        dialog = NewProjectDialog(self.__main_window)
        if dialog.exec() == QDialog.DialogCode.Rejected:
            return

        # создание проекта
        scenario = ScenarioFactory.make_scenario(Name(dialog.name()), Description(dialog.description()))
        self.__open_project(scenario)

    def __on_enter_created_from_gui(self, scenario: Scenario, project:Project, to_state_index: QModelIndex) -> tuple[bool, Optional[SynonymsSetModel]]:
        #s_model = project.choose_input()
        vector = LevenshtainVector(Name(to_state_index.data(CustomDataRole.Name)), SynonymsGroup())

        # костыль
        can_add_vector = True
        try:
            scenario.inputs().add(vector)
            scenario.inputs().remove(vector.name())
        except:
            can_add_vector = False

        if not can_add_vector:
            return False, None

        vector_item = LevenshtainVectorSerializer().to_data(vector)
        vector_item.on[CustomDataRole.Description] = ''

        project.vectors_model.prepare_item(vector_item)
        project.vectors_model.insertRow()
        
        state_id = StateID(to_state_index.data(CustomDataRole.Id))
        scenario.create_enter(vector, state_id)

        s_model = vector_item.on[CustomDataRole.SynonymsSet]
        self.__connect_synonym_changes_from_gui(project, scenario, s_model)

        return True, s_model

    def __on_step_created_from_gui(self, scenario: Scenario, project:Project, from_state_index: QModelIndex, to_state_item: ItemData, input: SynonymsSetModel) -> bool:
        # найти state_from
        from_state_id = StateID(from_state_index.data(CustomDataRole.Id))
        state_from = scenario.states([from_state_id])[from_state_id]
        # найти input_vector
        input_name = None
        for index in range(project.vectors_model.rowCount()):
            model_item = project.vectors_model.get_item(index)
            if model_item.on[CustomDataRole.SynonymsSet] is input:
                input_name = model_item.on[CustomDataRole.Name]
        if input_name is None: return False

        vectors = scenario.inputs().get([Name(input_name)])
        if len(vectors) != 1: return False
        input_vector = vectors[0]
        
        # сформировать аттрибуты нового состояния
        temp_state = State(StateID(-1), Name(to_state_item.on[CustomDataRole.Name]))

        # создать переход
        new_step = scenario.create_step(from_state_id, temp_state.attributes, input_vector)
        step_item = ItemData()
        step_item.on[CustomDataRole.FromState] = new_step.connection.from_state.id().value
        step_item.on[CustomDataRole.ToState] = new_step.connection.to_state.id().value
        step_item.on[CustomDataRole.SynonymsSet] = input

        new_state_id = new_step.connection.to_state.id()
        new_state = scenario.states([new_state_id])[new_state_id]
        to_state_item.on[CustomDataRole.Id] = new_state.id().value
        to_state_item.on[CustomDataRole.Name] = new_state.attributes.name.value
        to_state_item.on[CustomDataRole.Text] = new_state.attributes.output.value.text
        to_state_item.on[CustomDataRole.Steps] = [step_item]

        return True

    def __on_step_to_created_from_gui(self, scenario: Scenario, project:Project, from_state_index: QModelIndex, to_state_index: QModelIndex, input: SynonymsSetModel) -> bool:
        from_state_id = StateID(from_state_index.data(CustomDataRole.Id))
        to_state_id = StateID(to_state_index.data(CustomDataRole.Id))
        states = scenario.states([from_state_id, to_state_id])
        # найти state_from
        state_from = states[from_state_id]
        # найти state_to
        state_from = states[to_state_id]
        
        # найти input_vector
        input_name = None
        for index in range(project.vectors_model.rowCount()):
            model_item = project.vectors_model.get_item(index)
            if model_item.on[CustomDataRole.SynonymsSet] is input:
                input_name = model_item.on[CustomDataRole.Name]
        if input_name is None: return False

        vectors = scenario.inputs().get([Name(input_name)])
        if len(vectors) != 1: return False
        input_vector = vectors[0]

        # создать переход
        scenario.create_step(from_state_id, to_state_id, input_vector)
        return True

    def __on_vector_created_from_gui(self, scenario: Scenario, new_vector_item: QModelIndex):
        name = new_vector_item.data(CustomDataRole.Name)
        new_vector = LevenshtainVector(Name(name), SynonymsGroup())
        scenario.inputs().add(new_vector)

    def __on_state_changed_from_gui(self, scenario:Scenario, state_id:int, value:Any, role:int) -> tuple[bool, Any]:
        id = StateID(state_id)
        success = False

        if role == CustomDataRole.Text:
            old_value = scenario.states([id])[id].attributes.output.value.text
            if isinstance(value, str):
                scenario.set_answer(id, Output(Answer(value)))
                success = True

        elif role == CustomDataRole.Name:
            old_value = scenario.states([id])[id].attributes.name.value
            if isinstance(value, str):
                success = True
                scenario.states([id])[id].attributes.name = Name(value)

        return old_value, success

    # TODO: staticmethod?
    def __on_synonym_created_from_gui(self, proj:Project, scenario: Scenario, model:SynonymsSetModel, data: ItemData):
        self.__get_vector_by_model(proj, scenario, model).synonyms.synonyms.append(Synonym(data.on[CustomDataRole.Text]))

    # TODO: staticmethod?
    def __connect_synonym_changes_from_gui(self, proj:Project, scenario: Scenario, model:SynonymsSetModel):
        model.dataChanged.connect(
            lambda topLeft, bottomRight, roles:
                self.__on_synonym_changed_from_gui(proj, scenario, topLeft, roles)
        )
        model.rowsRemoved.connect(
            lambda parent,first,last:
                self.__on_synonym_deleted_from_gui(proj, scenario, model, first)
        )

    def __on_synonym_changed_from_gui(self, proj:Project, scenario: Scenario, index: QModelIndex, roles: list[int]):
        if not CustomDataRole.Text in roles:
            return
        
        vector = self.__get_vector_by_model(proj, scenario, index.model())
        vector.synonyms.synonyms[index.row()] = Synonym(index.data(CustomDataRole.Text))

    def __on_synonym_deleted_from_gui(self, proj:Project, scenario: Scenario, model:SynonymsSetModel, index: int):
        vector = self.__get_vector_by_model(proj, scenario, model)
        vector.synonyms.synonyms.pop(index)

    def __get_vector_by_model(self, proj:Project, scenario:Scenario, model:SynonymsSetModel) -> LevenshtainVector:
        group_name: Name = None

        input_vectors_count = proj.vectors_model.rowCount()
        for vector_model_row in range(input_vectors_count):
            vector_index = proj.vectors_model.index(vector_model_row)
            if not proj.vectors_model.data(vector_index, CustomDataRole.SynonymsSet) is model:
                continue

            group_name = Name(proj.vectors_model.data(vector_index, CustomDataRole.Name))
            break
        
        if group_name is None:
            raise Warning('по модели набора синонимов группа синонимов не найдена')
        
        found = scenario.inputs().get([group_name])
        if len(found) != 1:
            raise Warning('ошибка получения вектора перехода')
        
        vector: LevenshtainVector = found[0]

        if not isinstance(vector, LevenshtainVector):
             raise Warning('ошибка получения вектора перехода')
        
        return vector

    def open_project(self) -> Project:
        pass

    def close_current(self):
        pass

    def export_current(self) -> TextIOWrapper:
        pass

    def publish_current():
        pass
