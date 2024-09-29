from io import TextIOWrapper
from typing import Callable, Any, Optional
import os.path

from PySide6.QtGui import QShortcut, QIcon, QShortcut, QColor, QKeyEvent
from PySide6.QtCore import QEvent, QObject, Slot, Qt, QModelIndex, Slot, QPointF
from PySide6.QtWidgets import (
    QGraphicsView,
    QWidget,
    QDialog,
    QInputDialog,
    QMessageBox,
    QFileDialog,
    QTableWidget,
    QPushButton,
    QVBoxLayout,
    QAbstractItemView,
    QHeaderView,
    QLineEdit,
    QListWidget,
    QHBoxLayout,
    QListWidgetItem,
)

from ii_constructor.infrastructure.repositories.inmemory import HostingInmem
from ii_constructor.infrastructure.repositories.mariarepo import HostingMaria
from ii_constructor.infrastructure.qtgui.primitives.sceneitems import Editor, SceneNode
from ii_constructor.infrastructure.qtgui.data import CustomDataRole, ItemData, SynonymsSetModel
from ii_constructor.infrastructure.qtgui.flows import FlowsView, FlowListWidget, FlowsModel
from ii_constructor.infrastructure.qtgui.synonyms import SynonymsSelector, SynonymsEditor, SynonymsGroupsModel
from ii_constructor.infrastructure.qtgui.states import StatesModel, SceneControll
from ii_constructor.infrastructure.qtgui.main_w import FlowList, MainWindow, Workspaces, NewProjectDialog, MainToolButton
from ii_constructor.application.editor import HostingManipulator, ScenarioManipulator, ScenarioInterface
from ii_constructor.domain.core.primitives import Name, Description, SourceInfo, Input
from ii_constructor.domain.core.bot import State
from ii_constructor.domain.core.exceptions import Exists, CoreException
from ii_constructor.domain.inputvectors.levenshtain import LevenshtainVector, LevenshtainVectorSerializer, LevenshtainClassificator
from ii_constructor.infrastructure.qtgui.primitives.widgets import DBConnectWidget

class Project:
    __synonym_create_callback: Callable
    __synonyms_group_create_callback: Callable
    __connect_synonym_changes_callback: Callable
    __editor: QGraphicsView
    __flows_wgt: FlowListWidget
    __save_callback: Callable
    manipulator: ScenarioManipulator

    vectors_model: SynonymsGroupsModel
    
    def __init__(
        self,
        manipulator: ScenarioManipulator,
        synonym_create_callback: Callable,
        synonyms_group_create_callback: Callable,
        connect_synonym_changes_callback: Callable,
        vector_rename_callback: Callable[[QModelIndex, int, Any, Any], bool],
        editor: QGraphicsView,
        content: FlowListWidget,
        save_callback: Callable
    ):
        self.manipulator = manipulator
        self.vectors_model = SynonymsGroupsModel()
        #self.vectors_model.set_edit_callback(lambda i, r, o, n: True)
        self.vectors_model.set_edit_callback(lambda i, r, o, n: vector_rename_callback(i, r, o, n))

        self.__editor = editor
        self.__flows_wgt = content

        self.__synonym_create_callback = synonym_create_callback
        self.__synonyms_group_create_callback = synonyms_group_create_callback
        self.__connect_synonym_changes_callback = connect_synonym_changes_callback
        self.__save_callback = save_callback

    def open_test_window(self):
        self.__wgt = TestDialog(self.manipulator)
        self.__wgt.show()

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

    __is_enter_create_mode: bool

    def __init__(self) -> None:
        self.__is_enter_create_mode = False

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
        btn = MainToolButton('Текстировать', None, self.__main_window)
        btn.status_tip = 'Открыть демо-режим'
        btn.whats_this = 'Кнопка открытия демонстрационного режима'
        btn.apply_options()
        btn.clicked.connect(lambda: self.__current().open_test_window())
        self.__main_window.insert_button(btn)

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

        scene = self.__current().scene()
        for item in scene.items():
            if not isinstance(item, SceneNode):
                continue

            item.set_choose_mode(True)

        self.__is_enter_create_mode = True

    def __reset_enter_create_mode(self):
        self.__main_window.set_only_editor_enabled(False)

        scene = self.__current().scene()
        for item in scene.items():
            if not isinstance(item, SceneNode):
                continue

            item.set_choose_mode(False)

        self.__is_enter_create_mode = False

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

        proj_scene = Editor(self.__main_window)
        editor = QGraphicsView(proj_scene, self.__workspaces)
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

            lambda node, pos: self.__save_lay(manipulator, scene_controll, node, pos),

            # states_model:StatesModel
            states_model,

            # flows_model: FlowsModel
            flows_model,

            # main_window: QWidget
            self.__main_window
        )
        proj_scene.doubleClicked.connect(lambda pos: self.__add_enter_to_new_state(proj_scene, scene_controll, proj, manipulator, pos))
        
        # создание объекта взаимодействий с проектом
        proj = Project(
            manipulator,
            lambda model, data: self.__on_synonym_created_from_gui(proj, manipulator, model, data),
            lambda name: self.__on_vector_created_from_gui(manipulator, name),
            lambda model: self.__connect_synonym_changes_from_gui(proj, manipulator, model),
            lambda i, r, o, n: self.__rename_vector_handler(proj, manipulator, i, r, o, n),
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
        while not self.__maria_hosting.connected():
            dialog = DBConnectWidget(self.__main_window)
            ok = dialog.exec()
            if ok == QDialog.DialogCode.Rejected:
                return

            data = dialog.data()
            ip = data["ip"]
            port = data["port"]
            username = data["user"]
            password = data["password"]
            self.__maria_hosting.connect(ip, port, username, password)

            if not self.__maria_hosting.connected():
                QMessageBox.warning(self.__main_window, "Ошибка", "Не удалось подключиться!")

        if self.__maria_hosting.connected():
            dialog = DBProjLibrary(self.__maria_hosting, self.__main_window)
            ok = dialog.exec()
            if ok == QDialog.DialogCode.Rejected:
                return

            selected_id:int = dialog.proj_id()
            if selected_id == -1: # create new
                dialog = NewProjectDialog(self.__main_window)
                if dialog.exec() == QDialog.DialogCode.Rejected:
                    return

                info = SourceInfo(Name(dialog.name()), Description(dialog.description()))
                manipulator = HostingManipulator.make_scenario_in_db(self.__maria_hosting, info)
                
                scene_ctrl = self.__open_project(manipulator)

            elif selected_id == -2: # load from file
                path, filetype = QFileDialog.getOpenFileName(self.__main_window, 'Выбрать файл для загрузки в БД')

                if not path:
                    return

                data:str
                with open(path, "r") as file:
                    data = "".join(file.readlines())

                map = dict[int, int]()
                manipulator = HostingManipulator.open_scenario(self.__maria_hosting, data, map)
                scene_ctrl = self.__open_project(manipulator)
                
                lay_path = path + ".lay"
                if os.path.exists(lay_path):
                    with open(path + ".lay", "r") as lay_file:
                        scene_ctrl.load_layout("".join(lay_file.readlines()), map)
                else:
                    QMessageBox.warning(self.__main_window, 'Не удалось найти файл .lay', 'Не удалось найти файл .lay')

            else: # if selected_id >= 0:
                for proj in self.__projects.values():
                    if proj.manipulator.in_db() and proj.manipulator.id() == selected_id:
                        QMessageBox.warning(self.__main_window, "Невозможно выполнить!", "Проект уже открыт!")
                        return
                    
                manipulator = HostingManipulator.open_scenario_from_db(self.__maria_hosting, selected_id)
                scene_ctrl = self.__open_project(manipulator)
                scene_ctrl.load_layout(manipulator.get_layouts())

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
    
    def __add_enter_to_new_state(self, scene: Editor, scene_ctrl:SceneControll, proj:Project, manipulator: ScenarioManipulator, pos: QPointF):
        if not self.__is_enter_create_mode:
            return
        
        s_model = proj.choose_input()
        if s_model is None: return

        new_state_item = ItemData()
        try:
            name = self.__get_vector_name_by_synonyms_model(proj, manipulator, s_model)

            manipulator.check_can_create_enter_state(name)
            new_state_info = manipulator.create_state(name)
            manipulator.make_enter(self.__main_window, new_state_info['id'], False)

            new_state_item.on[CustomDataRole.Id] = new_state_info['id']
            new_state_item.on[CustomDataRole.Name] = new_state_info['name']
            new_state_item.on[CustomDataRole.Text] = new_state_info['text']

        except CoreException as e:
            QMessageBox.warning(self.__main_window, "Невозможно выполнить!", e.ui_text)
            return

        except Exception as e:
            return
        
        enter_item = ItemData()
        enter_item.on[CustomDataRole.Name] = new_state_item.on[CustomDataRole.Name]
        enter_item.on[CustomDataRole.Description] = ""
        enter_item.on[CustomDataRole.SynonymsSet] = s_model
        enter_item.on[CustomDataRole.EnterStateId] = new_state_item.on[CustomDataRole.Id]
        enter_item.on[CustomDataRole.SliderVisability] = False
        to_node = scene_ctrl.on_insert_node(scene, new_state_item, [enter_item], pos)
    
    def __on_state_removed_from_gui(self, manipulator: ScenarioManipulator, index: QModelIndex) -> bool:
        try:
            manipulator.remove_state(index.data(CustomDataRole.Id))
        except Exception as e:
            return False
        
        return True

    def __on_enter_created_from_gui(self, manipulator: ScenarioManipulator, project:Project, to_state_index: QModelIndex) -> tuple[bool, Optional[SynonymsSetModel]]:
        vector_name:str
        
        try:
            vector_name = manipulator.make_enter(self.__main_window, to_state_index.data(CustomDataRole.Id))
        
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
    
    def __save_lay(self, manipulator: ScenarioManipulator, ctrl: SceneControll, node: SceneNode, pos: QPointF):
        try:
            index = ctrl.find_in_model(node)
            manipulator.save_lay(index.data(CustomDataRole.Id), pos.x(), pos.y())

        except:
            return

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
    
    def __rename_vector_handler(self, proj:Project, manipulator: ScenarioManipulator, index: QModelIndex, row: int, old_name: str, new_name: str):
        try:
            manipulator.rename_vector(old_name, new_name)

        except CoreException as e:
            QMessageBox.warning(self.__main_window, "Невозможно выполнить", e.ui_text)
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

class Request:
    text: str
class Response:
    text: str
class Engine:
    __classif: LevenshtainClassificator
    __cur_state: State

    def __init__(self, scenario: ScenarioInterface, start_state: State) -> None:
        self.__classif = LevenshtainClassificator(scenario)
        self.__cur_state = start_state

    def handle(self, request:Request) -> Response:
        req = request.text
        prev_state = self.__cur_state.id()

        self.__cur_state = self.__classif.get_next_state(Input(req), self.__cur_state.id())

        result = Response()
        
        if prev_state == self.__cur_state.id():
            result.text = "Запрос не понятен"
        else:
            result.text = self.__cur_state.attributes.output.value.text

        return result
    
    def set_current_state(self, state: State):
        self.__cur_state = state

    def current_state(self) -> State:
        return self.__cur_state
        
class TestDialog(QWidget):
    __chat_history: QListWidget
    __input: QLineEdit
    __engine: Engine

    def __init__(self, manipulator: ScenarioManipulator, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Демонстрация")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        start_state: State = manipulator.interface().get_states_by_name(Name("Старт"))[0]
        self.__engine = Engine(manipulator.interface(), start_state)

        self.__chat_history = QListWidget(self)
        self.__chat_history.insertItem(0, start_state.attributes.output.value.text)

        self.__chat_history.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.__chat_history.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        main_lay = QVBoxLayout(self)
        main_lay.addWidget(self.__chat_history)

        self.__input = QLineEdit(self)
        send_btn = QPushButton(">", self)
        send_btn.setFixedWidth(30)
        enter_lay = QHBoxLayout(self)
        enter_lay.addWidget(self.__input, 0)
        enter_lay.addWidget(send_btn, 1)
        main_lay.addLayout(enter_lay)

        send_btn.clicked.connect(self.__on_send_pressed)
        self.__input.returnPressed.connect(self.__on_send_pressed)

    @Slot()
    def __on_send_pressed(self):
        input_text = self.__input.text()
        if len(input_text) == 0:
            return

        req = Request()
        req.text = input_text
        resp = self.__engine.handle(req)

        new_row = self.__chat_history.count()
        in_item = QListWidgetItem(req.text)
        in_item.setBackground(QColor(200, 200, 255))
        in_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.__chat_history.insertItem(new_row, in_item)
        self.__chat_history.insertItem(new_row+1, resp.text)
        self.__chat_history.scrollToItem(self.__chat_history.item(new_row+1))
        self.__input.clear()

class DBProjLibrary(QDialog):
    __table: QTableWidget
    __selected_id: int
    
    def __init__(self, manipulator: HostingMaria, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Dialog) -> None:
        super().__init__(parent, f)

        self.setWindowTitle("Открыть проект из БД")
        data = manipulator.sources()

        self.__selected_id = -1
        self.__table = QTableWidget(len(data), 3, self)
        self.__table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.__table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.__table.setHorizontalHeaderLabels(["id", "Название", "Описание"])
        self.__table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.__table.verticalHeader().hide()

        for row, _data in enumerate(data):
            for col in range(3):
                model_index = self.__table.model().index(row, col)
                self.__table.model().setData(model_index, _data[col], Qt.ItemDataRole.DisplayRole)
                item = self.__table.itemAt(row, col)
                item.setFlags(item.flags() & (~Qt.ItemFlag.ItemIsEditable))

        self.__table.doubleClicked.connect(self.selected)

        create_btn = QPushButton("Создать пустой", self)
        create_btn.clicked.connect(lambda: self.__select_new())

        load_btn = QPushButton("Загрузить из файла", self)
        load_btn.clicked.connect(lambda: self.__select_load())

        main_lay = QVBoxLayout(self)
        main_lay.addWidget(self.__table)
        main_lay.addWidget(create_btn)
        main_lay.addWidget(load_btn)

    @Slot(QModelIndex)
    def selected(self, index: QModelIndex):
        self.__selected_id = self.__table.model().data(self.__table.model().index(index.row(), 0), Qt.ItemDataRole.DisplayRole)
        self.accept()

    def __select_new(self):
        self.__selected_id = -1
        self.accept()

    def __select_load(self):
        self.__selected_id = -2
        self.accept()

    def proj_id(self):
        return self.__selected_id
