from io import TextIOWrapper
from typing import Callable, Any, Optional

from PySide6.QtGui import QShortcut, QIcon, QShortcut
from PySide6.QtWidgets import QGraphicsView, QDialog, QInputDialog, QMessageBox, QFileDialog 
from PySide6.QtCore import Slot, Qt, QModelIndex, Slot

from alicetool.infrastructure.qtgui.primitives.sceneitems import Arrow, Editor, SceneNode
from alicetool.infrastructure.qtgui.data import CustomDataRole, ItemData, SynonymsSetModel
from alicetool.infrastructure.qtgui.flows import FlowsView, FlowListWidget, FlowsModel
from alicetool.infrastructure.qtgui.synonyms import SynonymsSelector, SynonymsEditor, SynonymsGroupsModel
from alicetool.infrastructure.qtgui.states import StatesModel, SceneControll
from alicetool.infrastructure.qtgui.main_w import FlowList, MainWindow, Workspaces, NewProjectDialog, MainToolButton
from alicetool.application.editor import HostingManipulator, ScenarioManipulator
from alicetool.domain.core.primitives import Name, Description, ScenarioID, StateID, StateAttributes, Output, Answer, SourceInfo
from alicetool.domain.core.exceptions import Exists
from alicetool.domain.inputvectors.levenshtain import LevenshtainVector, Synonym, LevenshtainVectorSerializer
from alicetool.domain.core.porst import ScenarioInterface
from alicetool.domain.core.bot import Hosting, Source

class Project:
    __synonym_create_callback: Callable
    __synonyms_group_create_callback: Callable
    __connect_synonym_changes_callback: Callable
    __editor: QGraphicsView
    __flows_wgt: FlowListWidget
    __save_callback: Callable

    vectors_model: SynonymsGroupsModel
    
    def __init__(
        self,
        synonym_create_callback: Callable,
        synonyms_group_create_callback: Callable,
        connect_synonym_changes_callback: Callable,
        editor: QGraphicsView,
        content: FlowListWidget,
        save_callback: Callable
    ):
        self.vectors_model = SynonymsGroupsModel()

        self.__editor = editor
        self.__flows_wgt = content

        self.__synonym_create_callback = synonym_create_callback
        self.__synonyms_group_create_callback = synonyms_group_create_callback
        self.__connect_synonym_changes_callback = connect_synonym_changes_callback
        self.__save_callback = save_callback


    def id(self) -> ScenarioID:
        return self.__id
    
    def editor(self) -> QGraphicsView:
        return self.__editor
    
    def content(self) -> FlowListWidget:
        return self.__flows_wgt
    
    def edit_inputs(self):
        editor = SynonymsEditor(
            self.vectors_model,
            self.__create_synonyms_group,
            self.__create_synonym,
            self.__editor.parent()
        )
        editor.show()

    def choose_input(self) -> Optional[SynonymsSetModel]:
        dialog = SynonymsSelector(self.vectors_model, self.__create_synonyms_group, self.__editor.parent())
        dialog.exec()
        return dialog.selected_item()

    def __ask_new_vector_name(self, model:SynonymsGroupsModel) -> str:
        name:str = ''
        prev_name = ''

        while name == '':
            name, ok = QInputDialog.getText(
                self.__editor.parent(),
                'Новый набор синонимов',
                'Название',
                text= prev_name
            )

            if not ok: raise Warning('ввод отменён')
            if not model.get_item_by(CustomDataRole.Name, name) is None:
                QMessageBox.warning(self.__editor.parent(), 'Ошибка',
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

        item = self.__synonyms_group_create_callback(name)

        model.prepare_item(item)
        model.insertRow()

        self.__connect_synonym_changes_callback(item.on[CustomDataRole.SynonymsSet])

    def __create_synonym(self, model:SynonymsSetModel):
        default_value = 'значение'

        item = ItemData()
        item.on[CustomDataRole.Text] = default_value
        model.prepare_item(item)
        model.insertRow()

        self.__synonym_create_callback(model, item)

    def scene(self) -> Editor:
        return self.__editor.scene()
    
    def save_to_file(self):
        self.__save_callback()

class ProjectManager:
    # открытые проекты
    __projects: dict[QGraphicsView, Project]

    __main_window: MainWindow
    __workspaces: Workspaces
    __flow_list: FlowList
    __esc_sqortcut: QShortcut

    __inmem_hosting: Hosting

    def __init__(self) -> None:
        self.__inmem_hosting = Hosting()
        self.__workspaces = Workspaces()
        self.__flow_list = FlowList()
        self.__main_window = MainWindow(self.__flow_list, self.__workspaces)
        self.__setup_main_toolbar()

        self.__projects = {}

        self.__workspaces.currentChanged.connect(self.on_cur_changed)

        self.__esc_sqortcut = QShortcut(self.__main_window)
        self.__esc_sqortcut.setKey(Qt.Key.Key_Escape)
        self.__esc_sqortcut.activated.connect(lambda: self.__reset_enter_create_mode())

    def __setup_main_toolbar(self):
        btn = MainToolButton('Список синонимов', QIcon(":/icons/synonyms_list_norm.svg"), self.__main_window)
        btn.status_tip = 'Открыть редактор синонимов'
        btn.whats_this = 'Кнопка открытия редактора синонимов'
        btn.apply_options()
        btn.clicked.connect(lambda: self.__current().edit_inputs())
        self.__main_window.insert_button(btn)

        btn = MainToolButton('Опубликовать проект', QIcon(":/icons/export_proj_norm.svg"), self.__main_window)
        btn.status_tip = 'Разместить проект в БД '
        btn.whats_this = 'Кнопка экспорта проекта в базу данных'
        btn.apply_options()
        self.__main_window.insert_button(btn)

        btn = MainToolButton('Сохранить проект', QIcon(":/icons/save_proj_norm.svg"), self.__main_window)
        btn.status_tip = 'Сохранить в файл'
        btn.whats_this = 'Кнопка сохранения проекта в файл'
        btn.apply_options()
        btn.clicked.connect(lambda: self.__current().save_to_file())
        self.__main_window.insert_button(btn)

        btn = MainToolButton('Открыть проект', QIcon(":/icons/open_proj_norm.svg"), self.__main_window)
        btn.status_tip = 'Открыть файл проекта'
        btn.whats_this = 'Кнопка открытия проекта из файла'
        btn.apply_options()
        self.__main_window.insert_button(btn)

        btn = MainToolButton('Новый проект', QIcon(":/icons/new_proj_norm.svg"), self.__main_window)
        btn.status_tip = 'Создать новый проект'
        btn.whats_this = 'Кнопка создания нового проекта'
        btn.apply_options()
        btn.clicked.connect(lambda: self.create_project())
        self.__main_window.insert_button(btn)

    @Slot(int)
    def on_cur_changed(self, index: int):
        if index == -1:
            return
        
        proj = self.__projects[ self.__workspaces.widget(index) ]
        self.__flow_list.setWidget(proj.content(), True)

    def __current(self) -> Project:
        return self.__projects[self.__workspaces.currentWidget()]

    def __create_enter_handler(self, flows_model:FlowsModel, project: Project):
        self.__set_enter_create_mode()

    def __set_enter_create_mode(self):
        self.__main_window.set_only_editor_enabled(True)

        scene = proj = self.__current().scene()
        for item in scene.items():
            if not isinstance(item, SceneNode):
                continue

            item.set_choose_mode(True)

    def __reset_enter_create_mode(self):
        self.__main_window.set_only_editor_enabled(False)

        scene = proj = self.__current().scene()
        for item in scene.items():
            if not isinstance(item, SceneNode):
                continue

            item.set_choose_mode(False)

    def __save_scenario_handler(self, manipulator: ScenarioManipulator):
        path, filetype = QFileDialog.getSaveFileName(self.__main_window, 'Сохранить в файл', 'Новый сценарий')
        with open(path, "w") as file:
            file.write(manipulator.serialize())


    def __open_project(self, manipulator: ScenarioManipulator):
        scenario:ScenarioInterface = manipulator.interface()

        content_view = FlowsView(self.__flow_list)
        flows_model = FlowsModel(self.__main_window)
        content_view.setModel(flows_model)
        content_wgt = FlowListWidget(content_view)
        self.__flow_list.setWidget(content_wgt, True)

        editor = QGraphicsView(Editor(self.__main_window), self.__workspaces)
        editor.centerOn(0, 0)
        editor.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        # создание объекта взаимодействий с проектом
        proj = Project(
            lambda model, data: self.__on_synonym_created_from_gui(proj, manipulator, model, data),
            lambda name: self.__on_vector_created_from_gui(manipulator, name),
            lambda model: self.__connect_synonym_changes_from_gui(proj, manipulator, model),
            editor,
            content_wgt,
            lambda: self.__save_scenario_handler(manipulator)
        )
        flows_model.set_remove_callback(lambda index: self.__on_flow_remove_from_gui(manipulator, index))
        proj.vectors_model.set_remove_callback(lambda index: self.__on_vector_remove_from_gui(manipulator, index))

        states_model = StatesModel(self.__main_window)
        states_model.set_remove_callback(lambda index: self.__on_state_removed_from_gui(manipulator, index))

        # создание обработчика изменений на сцене
        states_controll = SceneControll(
            # select_input_callback: Callable[[],Optional[SynonymsSetModel]]
            lambda: proj.choose_input(),

            # change_data_callback: Callable[[int, Any, int], tuple[bool, Any]]
            lambda state_id, value, role:
                self.__on_state_changed_from_gui(manipulator, state_id, value, role),
            
            # new_step_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool]
            lambda from_state_index, to_state_index, input: 
                self.__on_step_to_created_from_gui(manipulator, proj, from_state_index, to_state_index, input),

            # step_remove_callback: Callable[[QModelIndex, QModelIndex, SynonymsSetModel], bool]
            lambda state_from, state_to, input:
                self.__on_step_removed_from_gui(manipulator, proj, state_from, state_to, input),

            # new_state_callback: Callable[[QModelIndex, ItemData, SynonymsSetModel], bool]
            lambda from_state_index, to_state_item, input: 
                self.__on_step_created_from_gui(manipulator, proj, from_state_index, to_state_item, input), 

            # add_enter_callback: Callable[[QModelIndex], tuple[bool, Optional[SynonymsSetModel]]]
            lambda state_index: self.__on_enter_created_from_gui(manipulator, proj, state_index),

            # states_model:StatesModel
            states_model,

            # flows_model: FlowsModel
            flows_model,

            # main_window: QWidget
            self.__main_window
        )

        content_wgt.create_value.connect(lambda: self.__create_enter_handler(flows_model, proj))

        self.__projects[editor] = proj # важно добавить перед addTab() для коттектной работы слота "current_changed"
        self.__workspaces.addTab(editor, manipulator.name())

        ### векторы переходов
        ## наполнение представления
        for vector in scenario.select_vectors():
            # пока только левенштейн
            serialiser = LevenshtainVectorSerializer()

            if isinstance(vector, LevenshtainVector):
                vector_item = serialiser.to_data(vector)
                vector_item.on[CustomDataRole.Description] = ''
                proj.vectors_model.prepare_item(vector_item)
                proj.vectors_model.insertRow()

                synonyms_model:SynonymsSetModel = vector_item.on[CustomDataRole.SynonymsSet]
                self.__connect_synonym_changes_from_gui(proj, manipulator, synonyms_model)
        
        ## обработчик изменений

#        proj.vectors_model.rowsInserted.connect(
#            lambda parent, first, last:
#                self.__on_vector_created_from_gui(scenario, proj.vectors_model.index(first))
#        )

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
                    input_item.on[CustomDataRole.Description] = state.attributes.description.value
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

        info = SourceInfo(Name(dialog.name()), Description(dialog.description()))

        # создание проекта
        manipulator = HostingManipulator.make_scenario(self.__inmem_hosting, info)
        self.__open_project(manipulator)

    def __on_vector_remove_from_gui(self, manipulator: ScenarioManipulator, index: QModelIndex) -> bool:
        input_name = Name(index.data(CustomDataRole.Name))
        if not manipulator.interface().check_vector_exists(input_name):
            return True
        
        input = manipulator.interface().get_vector(input_name)
        if len(manipulator.interface().input_usage(input)) > 0:
            return False
        
        manipulator.interface().remove_vector(input_name)
        return True

    def __on_flow_remove_from_gui(self, manipulator: ScenarioManipulator, index: QModelIndex) -> bool:
        _state_id:int = index.data(CustomDataRole.EnterStateId)
        state_id = StateID(_state_id)
        enter_state = manipulator.interface().states([state_id])[state_id]
        if enter_state.required:
            return False
        
        manipulator.interface().remove_enter(state_id)
        return True
    
    def __on_state_removed_from_gui(self, manipulator: ScenarioManipulator, index: QModelIndex) -> bool:
        state_id = StateID(index.data(CustomDataRole.Id))
        
        steps = manipulator.interface().steps(state_id)
        if len(steps) > 0:
            return False

        manipulator.interface().remove_state(state_id)
        return True

    def __on_enter_created_from_gui(self, manipulator: ScenarioManipulator, project:Project, to_state_index: QModelIndex) -> tuple[bool, Optional[SynonymsSetModel]]:
        vector_name = Name(to_state_index.data(CustomDataRole.Name))
        state_id = StateID(to_state_index.data(CustomDataRole.Id))
        s_model: SynonymsSetModel

        try: # создаём новый вектор
            vector = LevenshtainVector(vector_name)
            manipulator.interface().create_enter_vector(vector, state_id)
            vector_item = LevenshtainVectorSerializer().to_data(vector)
            project.vectors_model.prepare_item(vector_item)
            project.vectors_model.insertRow()
            s_model = vector_item.on[CustomDataRole.SynonymsSet]
            self.__connect_synonym_changes_from_gui(project, manipulator, s_model)
            
        except Exists as err:
            # если вектор уже существует - спрашиваем продолжать ли с ним
            ask_result = QMessageBox.information(
                self.__main_window,
                'Подтверждение',
                f'{err.ui_text} Продолжить с существующим вектором?',
                QMessageBox.StandardButton.Apply,
                QMessageBox.StandardButton.Abort
            )

            # если пользователь отказался - завершаем операцию
            if ask_result == QMessageBox.StandardButton.Abort:
                return False, None
            
            # берём набор синонимов из "кэша"
            s_model = project.vectors_model.get_item_by(CustomDataRole.Name, vector_name.value).on[CustomDataRole.SynonymsSet]
        
        try:
            manipulator.interface().make_enter(state_id)

        except Exists as err:
            QMessageBox.warning(
                self.__main_window,
                'Невозможно выполнить',
                err.ui_text,
                QMessageBox.StandardButton.Apply,
                QMessageBox.StandardButton.Abort
            )
            return False, None
        
        return True, s_model

    def __on_step_created_from_gui(self, manipulator: ScenarioManipulator, project:Project, from_state_index: QModelIndex, to_state_item: ItemData, input: SynonymsSetModel) -> bool:
        # найти state_from
        from_state_id = StateID(from_state_index.data(CustomDataRole.Id))
        #state_from = scenario.states([from_state_id])[from_state_id]
        # найти input_vector
        _input_name = None
        for index in range(project.vectors_model.rowCount()):
            model_item = project.vectors_model.get_item(index)
            if model_item.on[CustomDataRole.SynonymsSet] is input:
                _input_name = model_item.on[CustomDataRole.Name]
        if _input_name is None: return False

        input_vector = manipulator.interface().get_vector(Name(_input_name))
        
        # сформировать аттрибуты нового состояния
        new_state_attr = StateAttributes(
            Output(Answer('текст ответа')),
            Name(to_state_item.on[CustomDataRole.Name]),
            Description('')
        )

        # создать переход
        new_step = manipulator.interface().create_step(from_state_id, new_state_attr, input_vector)
        step_item = ItemData()
        step_item.on[CustomDataRole.FromState] = new_step.connection.from_state.id().value
        step_item.on[CustomDataRole.ToState] = new_step.connection.to_state.id().value
        step_item.on[CustomDataRole.SynonymsSet] = input

        new_state_id = new_step.connection.to_state.id()
        new_state = manipulator.interface().states([new_state_id])[new_state_id]
        to_state_item.on[CustomDataRole.Id] = new_state.id().value
        to_state_item.on[CustomDataRole.Name] = new_state.attributes.name.value
        to_state_item.on[CustomDataRole.Text] = new_state.attributes.output.value.text
        to_state_item.on[CustomDataRole.Steps] = [step_item]

        return True
    
    def __on_step_removed_from_gui(self, manipulator: ScenarioManipulator, project:Project, state_from: QModelIndex, state_to: QModelIndex, input: SynonymsSetModel):
        from_state_id:int = state_from.data(CustomDataRole.Id)

        input_vector = self.__get_vector_by_model(project, manipulator, input)
        manipulator.remove_step(StateID(from_state_id), input_vector)

        return True
        
    def __on_step_to_created_from_gui(self, manipulator: ScenarioManipulator, project:Project, from_state_index: QModelIndex, to_state_index: QModelIndex, input: SynonymsSetModel) -> bool:
        from_state_id = StateID(from_state_index.data(CustomDataRole.Id))
        to_state_id = StateID(to_state_index.data(CustomDataRole.Id))
        states = manipulator.interface().states([from_state_id, to_state_id])
        # найти state_from
        state_from = states[from_state_id]
        # найти state_to
        state_from = states[to_state_id]
        
        # найти input_vector
        _input_name = None
        for index in range(project.vectors_model.rowCount()):
            model_item = project.vectors_model.get_item(index)
            if model_item.on[CustomDataRole.SynonymsSet] is input:
                _input_name = model_item.on[CustomDataRole.Name]
        if _input_name is None: return False

        input_vector = manipulator.interface().get_vector(Name(_input_name))

        # создать переход
        manipulator.interface().create_step(from_state_id, to_state_id, input_vector)
        return True

    def __on_vector_created_from_gui(self, manipulator: ScenarioManipulator, name: str) -> ItemData:
        #name = new_vector_item.data(CustomDataRole.Name)
        new_vector = LevenshtainVector(Name(name))
        manipulator.interface().add_vector(new_vector)
        item = LevenshtainVectorSerializer().to_data(new_vector)
        return item

    def __on_state_changed_from_gui(self, manipulator:ScenarioManipulator, state_id:int, value:Any, role:int) -> tuple[bool, Any]:
        id = StateID(state_id)
        success = False

        if role == CustomDataRole.Text:
            old_value = manipulator.interface().states([id])[id].attributes.output.value.text
            if isinstance(value, str):
                manipulator.interface().set_answer(id, Output(Answer(value)))
                success = True

        elif role == CustomDataRole.Name:
            old_value = manipulator.interface().states([id])[id].attributes.name.value
            if isinstance(value, str):
                success = True
                manipulator.interface().states([id])[id].attributes.name = Name(value)

        return old_value, success

    # TODO: staticmethod?
    def __on_synonym_created_from_gui(self, proj:Project, manipulator: ScenarioManipulator, model:SynonymsSetModel, data: ItemData):
        self.__get_vector_by_model(proj, manipulator, model).synonyms.synonyms.append(Synonym(data.on[CustomDataRole.Text]))

    # TODO: staticmethod?
    def __connect_synonym_changes_from_gui(self, proj:Project, manipulator: ScenarioManipulator, model:SynonymsSetModel):
        model.dataChanged.connect(
            lambda topLeft, bottomRight, roles:
                self.__on_synonym_changed_from_gui(proj, manipulator, topLeft, roles)
        )

        model.set_remove_callback(
            lambda index:
                self.__on_synonym_deleted_from_gui(proj, manipulator, index.model(), index.row())
        )

    def __on_synonym_changed_from_gui(self, proj:Project, manipulator: ScenarioManipulator, index: QModelIndex, roles: list[int]):
        if not CustomDataRole.Text in roles:
            return
        
        vector = self.__get_vector_by_model(proj, manipulator, index.model())
        vector.synonyms.synonyms[index.row()] = Synonym(index.data(CustomDataRole.Text))

    def __on_synonym_deleted_from_gui(self, proj:Project, manipulator: ScenarioManipulator, model:SynonymsSetModel, index: int) -> bool:
        vector = self.__get_vector_by_model(proj, manipulator, model)
        vector.synonyms.synonyms.pop(index)
        return True

    def __get_vector_by_model(self, proj:Project, manipulator:ScenarioManipulator, model:SynonymsSetModel) -> LevenshtainVector:
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
        
        vector: LevenshtainVector = manipulator.interface().get_vector(group_name)

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
