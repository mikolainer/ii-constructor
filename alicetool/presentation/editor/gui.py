from io import TextIOWrapper
from typing import Callable, Any, Optional
import os.path

from PySide6.QtGui import QShortcut, QIcon, QShortcut
from PySide6.QtWidgets import QGraphicsView, QDialog, QInputDialog, QMessageBox, QFileDialog 
from PySide6.QtCore import Slot, Qt, QModelIndex, Slot

from alicetool.infrastructure.repositories.inmemory import HostingInmem
from alicetool.infrastructure.repositories.mariarepo import HostingMaria
from alicetool.infrastructure.qtgui.primitives.sceneitems import Editor, SceneNode
from alicetool.infrastructure.qtgui.data import CustomDataRole, ItemData, SynonymsSetModel
from alicetool.infrastructure.qtgui.flows import FlowsView, FlowListWidget, FlowsModel
from alicetool.infrastructure.qtgui.synonyms import SynonymsSelector, SynonymsEditor, SynonymsGroupsModel
from alicetool.infrastructure.qtgui.states import StatesModel, SceneControll
from alicetool.infrastructure.qtgui.main_w import FlowList, MainWindow, Workspaces, NewProjectDialog, MainToolButton
from alicetool.application.editor import HostingManipulator, ScenarioManipulator
from alicetool.domain.core.primitives import Name, Description, ScenarioID, SourceInfo
from alicetool.domain.core.exceptions import Exists, CoreException
from alicetool.domain.inputvectors.levenshtain import LevenshtainVector, LevenshtainVectorSerializer

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
        self.vectors_model.set_edit_callback(lambda i, r, o, n: True)

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

        self.__synonyms_group_create_callback(name)

        item = ItemData()
        item.on[CustomDataRole.Name] = name
        item.on[CustomDataRole.SynonymsSet] = SynonymsSetModel()
        item.on[CustomDataRole.Description] = ''
    
        model.prepare_item(item)
        model.insertRow()

        self.__connect_synonym_changes_callback(item.on[CustomDataRole.SynonymsSet])

    def __create_synonym(self, model:SynonymsSetModel):
        default_value = 'значение'

        item = ItemData()
        item.on[CustomDataRole.Text] = default_value

        if self.__synonym_create_callback(model, item):
            model.prepare_item(item)
            model.insertRow()

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

    __inmem_hosting: HostingInmem
    __maria_hosting: HostingMaria

    def __init__(self) -> None:
        self.__maria_hosting = HostingMaria()
        self.__inmem_hosting = HostingInmem()
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

        #btn = MainToolButton('Подключиться к БД', QIcon(":/icons/export_proj_norm.svg"), self.__main_window)
        #btn.status_tip = 'Подключиться к БД '
        #btn.whats_this = 'Кнопка работы с БД'
        btn = MainToolButton('Создать в БД', QIcon(":/icons/export_proj_norm.svg"), self.__main_window)
        btn.status_tip = 'Создать в БД '
        btn.whats_this = 'Создать в БД'
        btn.apply_options()
        btn.clicked.connect(lambda: self.db_connections())
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
        btn.clicked.connect(lambda: self.open_project())
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

    def __save_scenario_handler(self, manipulator: ScenarioManipulator, scene_ctrl: SceneControll):
        path, filetype = QFileDialog.getSaveFileName(self.__main_window, 'Сохранить в файл', 'Новый сценарий')

        if not path:
            return

        with open(path, "w") as file:
            file.write(manipulator.serialize())

        with open(path + ".lay", "w") as lay_file:
            lay_file.write(scene_ctrl.serialize_layout())

    def __open_project(self, manipulator: ScenarioManipulator) -> SceneControll:
        content_view = FlowsView(self.__flow_list)
        flows_model = FlowsModel(self.__main_window)
        flows_model.set_edit_callback(lambda i, r, o, n: True)
        content_view.setModel(flows_model)
        content_wgt = FlowListWidget(content_view)
        self.__flow_list.setWidget(content_wgt, True)

        editor = QGraphicsView(Editor(self.__main_window), self.__workspaces)
        editor.centerOn(0, 0)
        editor.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # создание обработчика изменений на сцене
        states_model = StatesModel(self.__main_window)
        states_model.set_edit_callback(lambda i, r, o, n: self.__on_state_changed_from_gui(manipulator, i, r, o, n))
        states_model.set_remove_callback(lambda index: self.__on_state_removed_from_gui(manipulator, index))

        scene_controll = SceneControll(
            manipulator,

            # select_input_callback: Callable[[],Optional[SynonymsSetModel]]
            lambda: proj.choose_input(),
            
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
        
        # создание объекта взаимодействий с проектом
        proj = Project(
            lambda model, data: self.__on_synonym_created_from_gui(proj, manipulator, model, data),
            lambda name: self.__on_vector_created_from_gui(manipulator, name),
            lambda model: self.__connect_synonym_changes_from_gui(proj, manipulator, model),
            editor,
            content_wgt,
            lambda: self.__save_scenario_handler(manipulator, scene_controll)
        )
        flows_model.set_remove_callback(lambda index: self.__on_flow_remove_from_gui(manipulator, index))
        proj.vectors_model.set_remove_callback(lambda index: self.__on_vector_remove_from_gui(manipulator, index))

        content_wgt.create_value.connect(lambda: self.__create_enter_handler(flows_model, proj))

        self.__projects[editor] = proj # важно добавить перед addTab() для коттектной работы слота "current_changed"
        self.__workspaces.addTab(editor, manipulator.name())
        self.__workspaces.setCurrentWidget(editor)

        ### векторы переходов
        ## наполнение представления
        for vector in manipulator.interface().select_vectors():
            # пока только левенштейн
            serialiser = LevenshtainVectorSerializer()

            if isinstance(vector, LevenshtainVector):
                vector_item = serialiser.to_data(vector)
                vector_item.on[CustomDataRole.Description] = ''
                proj.vectors_model.prepare_item(vector_item)
                proj.vectors_model.insertRow()

                synonyms_model:SynonymsSetModel = vector_item.on[CustomDataRole.SynonymsSet]
                self.__connect_synonym_changes_from_gui(proj, manipulator, synonyms_model)

        ### сцена (состояния и переходы)
        ## наполнение представления
        for state in manipulator.interface().states().values():
            input_items = list[ItemData]()

            # подготовка шагов для модели состояний
            for step in manipulator.interface().steps(state.id()):
                conn = step.connection
                if conn is None:
                    continue # вообще-то не норм ситуация. возможно стоит бросать исключение

                vector_data = proj.vectors_model.get_item_by(
                    CustomDataRole.Name, step.input.name().value
                )
                s_model = vector_data.on[CustomDataRole.SynonymsSet]

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

            # добавление элемента модели состояний
            scene_controll.on_insert_node(proj.scene(), item, input_items)

        scene_controll.init_arrows(proj.scene(), proj.vectors_model)

        return scene_controll

    def create_project(self) -> Project:
        dialog = NewProjectDialog(self.__main_window)
        if dialog.exec() == QDialog.DialogCode.Rejected:
            return

        info = SourceInfo(Name(dialog.name()), Description(dialog.description()))

        # создание проекта
        manipulator = HostingManipulator.make_scenario(self.__inmem_hosting, info)
        self.__open_project(manipulator)

    def open_project(self) -> Project:
        path, filetype = QFileDialog.getOpenFileName(self.__main_window, 'Создать из файла')

        if not path:
            return

        data:str
        with open(path, "r") as file:
            data = "".join(file.readlines())

        # создание проекта
        manipulator = HostingManipulator.open_scenario(self.__inmem_hosting, data)
        scene_ctrl = self.__open_project(manipulator)

        lay_path = path + ".lay"
        if os.path.exists(lay_path):
            with open(path + ".lay", "r") as lay_file:
                scene_ctrl.load_layout("".join(lay_file.readlines()))
        else:
            QMessageBox.warning(self.__main_window, 'Не удалось найти файл .lay', 'Не удалось найти файл .lay')

    def db_connections(self):
#        if self.__maria_hosting.connected():
#            QMessageBox.critical(self.__main_window, "Ошибка", "Cценарий уже создан!")
#            return

        while not self.__maria_hosting.connected():
            ip, ok = QInputDialog.getText(self.__main_window, 'Подключение к БД', 'ip')
            if not ok: return
            port, ok = QInputDialog.getText(self.__main_window, 'Подключение к БД', 'Порт')
            if not ok: return
            username, ok = QInputDialog.getText(self.__main_window, 'Подключение к БД', 'Имя пользователя')
            if not ok: return
            password, ok = QInputDialog.getText(self.__main_window, 'Подключение к БД', 'Пароль')
            if not ok: return
        
        dialog = NewProjectDialog(self.__main_window)
        if dialog.exec() == QDialog.DialogCode.Rejected:
            return

        info = SourceInfo(Name(dialog.name()), Description(dialog.description()))
        manipulator = HostingManipulator.make_scenario_in_db(self.__maria_hosting, info)
        
        scene_ctrl = self.__open_project(manipulator)

    def __on_vector_remove_from_gui(self, manipulator: ScenarioManipulator, index: QModelIndex) -> bool:
        try:
            manipulator.remove_vector(index.data(CustomDataRole.Name))
        except Exception as e:
            return False
        
        return True

    def __on_flow_remove_from_gui(self, manipulator: ScenarioManipulator, index: QModelIndex) -> bool:
        try:
            manipulator.remove_enter(index.data(CustomDataRole.EnterStateId))
        except Exception as e:
            return False
        
        return True
    
    def __on_state_removed_from_gui(self, manipulator: ScenarioManipulator, index: QModelIndex) -> bool:
        try:
            manipulator.remove_state(index.data(CustomDataRole.Id))
        except Exception as e:
            return False
        
        return True

    def __on_enter_created_from_gui(self, manipulator: ScenarioManipulator, project:Project, to_state_index: QModelIndex) -> tuple[bool, Optional[SynonymsSetModel]]:
        vector_name:str
        
        try:
            vector_name = manipulator.make_enter(to_state_index.data(CustomDataRole.Id))
        
        except CoreException as e:
            QMessageBox.warning(self.__main_window, "Невозможно выполнить!", e.ui_text)
            return False, None
        
        except Exception as e:
            return False, None

        g_item = project.vectors_model.get_item_by(CustomDataRole.Name, vector_name)
        if isinstance(g_item, ItemData):
            return True, g_item.on[CustomDataRole.SynonymsSet]

        s_model = SynonymsSetModel()
        item = ItemData()
        item.on[CustomDataRole.Name] = vector_name
        item.on[CustomDataRole.SynonymsSet] = s_model
        item.on[CustomDataRole.Description] = ''
        project.vectors_model.prepare_item(item)
        project.vectors_model.insertRow()
        self.__connect_synonym_changes_from_gui(project, manipulator, s_model)

        return True, s_model

    def __on_step_created_from_gui(self, manipulator: ScenarioManipulator, project:Project, from_state_index: QModelIndex, to_state_item: ItemData, input: SynonymsSetModel) -> bool:
        try:
            from_state_id = from_state_index.data(CustomDataRole.Id)
            vector_name = self.__get_vector_name_by_synonyms_model(project, manipulator, input)
            new_state_info = manipulator.create_step_to_new_state(from_state_id, vector_name, to_state_item.on[CustomDataRole.Name])

            to_state_item.on[CustomDataRole.Id] = new_state_info['id']
            to_state_item.on[CustomDataRole.Name] = new_state_info['name']
            to_state_item.on[CustomDataRole.Text] = new_state_info['text']

        except CoreException as e:
            QMessageBox.warning(self.__main_window, "Невозможно выполнить!", e.ui_text)
            return False

        except Exception as e:
            return False
        
        return True
    
    def __on_step_removed_from_gui(self, manipulator: ScenarioManipulator, project:Project, state_from: QModelIndex, state_to: QModelIndex, input: SynonymsSetModel):
        try:
            from_state_id:int = state_from.data(CustomDataRole.Id)
            input_name:str = self.__get_vector_name_by_synonyms_model(project, manipulator, input)
            manipulator.remove_step(from_state_id, input_name)
        except Exception as e:
            return False
        
        return True
        
    def __on_step_to_created_from_gui(self, manipulator: ScenarioManipulator, project:Project, from_state_index: QModelIndex, to_state_index: QModelIndex, input: SynonymsSetModel) -> bool:
        try:
            input_name = self.__get_vector_name_by_synonyms_model(project, manipulator, input)
            manipulator.create_step(from_state_index.data(CustomDataRole.Id), to_state_index.data(CustomDataRole.Id), input_name)
        except Exception as e:
            return False
        
        return True

    def __on_vector_created_from_gui(self, manipulator: ScenarioManipulator, name: str) -> bool:
        try:
            manipulator.add_vector(name)
        except Exception as e:
            return False
        
        return True

    def __on_state_changed_from_gui(self, manipulator:ScenarioManipulator, state_item:QModelIndex, role:int, old_value:Any, new_value:Any) -> bool:
        state_id = state_item.data(CustomDataRole.Id)
        try:
            if role == CustomDataRole.Text:
                manipulator.set_state_answer(state_id, new_value)

            elif role == CustomDataRole.Name:
                manipulator.rename_state(state_id, new_value)

        except CoreException as e:
            QMessageBox.warning(self.__main_window, "Невозможно выполнить", e.ui_text)
            return False

        except Exception as e:
            return False

        return True

    # TODO: staticmethod?
    def __on_synonym_created_from_gui(self, proj:Project, manipulator: ScenarioManipulator, model:SynonymsSetModel, data: ItemData) -> bool:
        try:
            manipulator.create_synonym(
                self.__get_vector_name_by_synonyms_model(proj, manipulator, model),
                data.on[CustomDataRole.Text]
            )
        
        except Exists as e:
            QMessageBox.critical(self.__main_window, "Невозможно выполнить", e.ui_text)
            return False

        except Exception as e:
            return False

        return True
        
    # TODO: staticmethod?
    def __connect_synonym_changes_from_gui(self, proj:Project, manipulator: ScenarioManipulator, model:SynonymsSetModel):
        model.set_edit_callback(
            lambda index, role, old_val, new_val:
                self.__synonym_changed_from_gui_handler(proj, manipulator, index, role, old_val, new_val)
        )

        model.set_remove_callback(
            lambda index:
                self.__synonym_deleted_from_gui_handler(proj, manipulator, index)
        )

    def __synonym_changed_from_gui_handler(self, proj:Project, manipulator: ScenarioManipulator, index: QModelIndex, role: int, old_value:Any, new_value:Any) -> bool:
        try:
            group_name = self.__get_vector_name_by_synonyms_model(proj, manipulator, index.model())
            manipulator.set_synonym_value(group_name, old_value, new_value)
        except Exception as e:
            return False
        
        return True

    def __synonym_deleted_from_gui_handler(self, proj:Project, manipulator: ScenarioManipulator, index: QModelIndex) -> bool:
        try:
            group_name = self.__get_vector_name_by_synonyms_model(proj, manipulator, index.model())
            synonym_value = index.data(CustomDataRole.Text)
            manipulator.remove_synonym(group_name, synonym_value)
        except Exception as e:
            return False
        
        return True

    def __get_vector_name_by_synonyms_model(self, proj:Project, manipulator:ScenarioManipulator, model:SynonymsSetModel) -> str:
        group_name: str = None

        input_vectors_count = proj.vectors_model.rowCount()
        for vector_model_row in range(input_vectors_count):
            vector_index = proj.vectors_model.index(vector_model_row)
            if not proj.vectors_model.data(vector_index, CustomDataRole.SynonymsSet) is model:
                continue

            group_name = proj.vectors_model.data(vector_index, CustomDataRole.Name)
            break
        
        if group_name is None:
            raise Warning('по модели набора синонимов группа синонимов не найдена')
        
        return group_name
