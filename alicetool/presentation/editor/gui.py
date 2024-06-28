from io import TextIOWrapper

from PySide6.QtWidgets import QGraphicsView, QDialog, QInputDialog, QMessageBox
from PySide6.QtCore import Slot, Qt

from alicetool.infrastructure.qtgui.primitives.sceneitems import Arrow
from alicetool.infrastructure.qtgui.data import CustomDataRole, ItemData, SynonymsSetModel
from alicetool.infrastructure.qtgui.flows import FlowsView, FlowListWidget, FlowsModel
from alicetool.infrastructure.qtgui.synonyms import SynonymsSelectorView, SynonymsEditor, SynonymsGroupsModel
from alicetool.infrastructure.qtgui.states import Editor, StatesModel
from alicetool.infrastructure.qtgui.main_w import FlowList, MainWindow, Workspaces, NewProjectDialog
from alicetool.application.editor import ScenarioFactory, SourceControll
from alicetool.application.data import ItemDataSerializer
from alicetool.domain.core.bot import Scenario, State, PossibleInputs, Connection, Step, InputDescription
from alicetool.domain.core.primitives import Name, Description, ScenarioID, StateID
from alicetool.domain.inputvectors.levenshtain import LevenshtainVector

class Project:
    __id = ScenarioID
    __scene: Editor
    __flows_wgt: FlowListWidget

    states_model: StatesModel
    flows_model: FlowsModel
    vectors_model: SynonymsGroupsModel
    
    def __init__(
        self,
        scene: Editor,
        content: FlowListWidget
    ):
        self.__scene = scene
        self.__flows_wgt = content

        self.states_model = StatesModel()
        self.flows_model = FlowsModel()
        self.vectors_model = SynonymsGroupsModel()

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

    def choose_input() -> Name:
        ''' TODO: сделать обёртку-диалог над SynonymsSelectorView '''
        pass

    def choose_state() -> StateID:
        pass

    def __create_synonyms_group(self, model:SynonymsGroupsModel):
        name:str = ''
        prev_name = ''

        while name == '':
            name, ok = QInputDialog.getText(
                self.__scene.parent(),
                'Новый набор синонимов',
                'Название',
                text= prev_name
            )

            if not ok: return
            if not model.get_item_by(CustomDataRole.Name, name) is None:
                QMessageBox.warning(self.__scene.parent(), 'Ошибка',
                    f'Рруппа синонимов с именем "{name}" уже существует!')
                prev_name = name
                name = ''

        s_model = SynonymsSetModel()
        self.__create_synonym(s_model)

        item = ItemData()
        item.on[CustomDataRole.Name] = name
        item.on[CustomDataRole.Description] = ""
        item.on[CustomDataRole.SynonymsSet] = s_model
        item.on[CustomDataRole.FromState] = None
        item.on[CustomDataRole.ToState] = None

        model.prepare_item(item)
        model.insertRow()

    def __create_synonym(self, model:SynonymsSetModel):
        item = ItemData()
        item.on[CustomDataRole.Text] = 'значение'
        model.prepare_item(item)
        model.insertRow()

class ProjectManager:
    # открытые проекты
    __projects: dict[QGraphicsView, Project]

    __main_window: MainWindow
    __workspaces: Workspaces
    __flow_list: FlowList

    def __init__( self, flow_list: FlowList, workspaces: Workspaces, main_window: MainWindow ) -> None:
        self.__workspaces = workspaces
        self.__main_window = main_window
        self.__flow_list = flow_list

        self.__projects = {}

        self.__workspaces.currentChanged.connect(self.on_cur_changed)

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

    def create_project(self) -> Project:
        dialog = NewProjectDialog(self.__main_window)
        if dialog.exec() == QDialog.DialogCode.Rejected:
            return

        # создание содержания (список точек входа)
        content_view = FlowsView(self.__flow_list)
        content = FlowListWidget(content_view)
        self.__flow_list.setWidget(content, True)
        #content.create_value.connect('''TODO''')

        # создание редактора
        scene = Editor(self.__main_window)

        # создание проекта с пустыми моделями
        proj = Project(scene, content)
        content_view.setModel(proj.flows_model)
        scene.setStatesModel(proj.states_model)

        editor = QGraphicsView(scene, self.__workspaces)
        self.__projects[editor] = proj
        self.__workspaces.addTab(editor, dialog.name())

        # наполнение проекта
        scenario = ScenarioFactory.make_scenario(Name(dialog.name()), Description(dialog.description()))

        # TODO: log
        print("===== создание Qt моделей проекта =====")
        print("----- СОСТОЯНИЯ -----")
        for state in scenario.states().values():
            item = ItemData()
            item.on[CustomDataRole.Id] = state.id().value
            item.on[CustomDataRole.Name] = state.attributes.name.value
            item.on[CustomDataRole.Text] = state.attributes.output.value.text
            proj.states_model.prepare_item(item)
            proj.states_model.insertRow()
            # TODO: log
            print(ItemDataSerializer.to_string(item))

        # TODO: log
        print("----- ВЕКТОРЫ -----")
        for conn in scenario.connections():
            for step in conn.steps:
                if isinstance(step.input, LevenshtainVector):
                    s_model = SynonymsSetModel(self.__main_window)
                    for synonym in step.input.synonyms:
                        item = ItemData()
                        item.on[CustomDataRole.Text] = synonym.value
                        s_model.prepare_item(item)
                        s_model.insertRow()
                    
                    item = ItemData()
                    item.on[CustomDataRole.Name] = step.name.value
                    item.on[CustomDataRole.Description] = ""
                    item.on[CustomDataRole.SynonymsSet] = s_model
                    item.on[CustomDataRole.FromState] = None if conn.from_state is None else conn.from_state.id().value
                    item.on[CustomDataRole.ToState] = conn.to_state.id().value
                    
                    proj.vectors_model.prepare_item(item)
                    proj.vectors_model.insertRow()
                    # TODO: log
                    print(ItemDataSerializer.to_string(item))

        # модель точек входа
        # TODO: log

        print("----- ПОТОКИ -----")
        for index in range(proj.vectors_model.rowCount()):
            vector_data = proj.vectors_model.get_item(index)
            if not vector_data.on[CustomDataRole.FromState] is None:
                continue
            
            s_model:SynonymsSetModel = vector_data.on[CustomDataRole.SynonymsSet]
            id = StateID(vector_data.on[CustomDataRole.ToState])
            state = scenario.states([id])[id]

            item = ItemData()
            item.on[CustomDataRole.Name] = state.attributes.name.value
            item.on[CustomDataRole.Description] = state.attributes.desrciption.value
            item.on[CustomDataRole.SynonymsSet] = s_model
            item.on[CustomDataRole.EnterStateId] = state.id().value
            item.on[CustomDataRole.SliderVisability] = False

            proj.flows_model.prepare_item(item)
            proj.flows_model.insertRow()

            print(ItemDataSerializer.to_string(item))

    def open_project(self) -> Project:
        pass

    def close_current(self):
        pass

    def export_current(self) -> TextIOWrapper:
        pass

    def publish_current():
        pass
