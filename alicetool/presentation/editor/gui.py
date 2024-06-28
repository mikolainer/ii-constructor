from io import TextIOWrapper
from typing import Optional

from PySide6.QtCore import (
    Slot,
)

from PySide6.QtWidgets import (
    QMessageBox,
    QWidget,
)

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

    def __create_synonyms_group(model:SynonymsGroupsModel):
        pass

    def __create_synonym(model:SynonymsSetModel):
        pass


class ProjectManager:
    # открытые проекты
    __projects: dict[Editor, Project]

    __main_window: MainWindow
    __workspaces: Workspaces
    __flow_list: FlowList

    def __init__( self, workspaces: Workspaces, main_window: MainWindow, flow_list: FlowList ) -> None:
        self.__workspaces = workspaces
        self.__main_window = main_window
        self.__flow_list = flow_list
        self.__workspaces.currentChanged.connect(
            lambda index:
            self.set_current(
                self.__projects[
                    self.__workspaces.widget(index)
                ]
            )
        )

    def current(self) -> Project:
        return self.__projects[self.__workspaces.currentWidget()]

    def set_current(self, proj:Project):
        self.__workspaces.setCurrentWidget(proj.editor())
        self.__flow_list.setCurrentWidget(proj.content())

    def create_project(self) -> Project:
        # создание содержания (список точек входа)
        content_view = FlowsView(self.__flow_list)
        content = FlowListWidget(content_view)
        content.create_value.connect('''TODO''')

        # создание редактора
        editor = Editor(self.__main_window)

        # создание проекта с пустыми моделями
        proj = Project(editor, content)
        content_view.setModel(proj.flows_model)
        editor.setModel(proj.states_model)
        self.__workspaces.addTab(editor, editor)

        # создание проекта
        dialog = NewProjectDialog(self.__main_window)
        dialog.exec()
        scenario = ScenarioFactory.make_scenario(Name(dialog.name), Description(dialog.descr))

        # TODO: log
        print("===== создание Qt моделей проекта =====")
        print("----- СОСТОЯНИЯ -----")
        for state in scenario.get_states().values():
            item = ItemData()
            item.on[CustomDataRole.Id] = state.id().value
            item.on[CustomDataRole.Name] = state.attributes.name.value
            item.on[CustomDataRole.Text] = state.attributes.output.value.text
            proj.states_model.prepare_item(item)
            proj.states_model.insertRow()
            # TODO: log
            print(ItemDataSerializer.to_string(item))

        scenario

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
                    item.on[CustomDataRole.Name] = step.name
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
            state = scenario.states([StateID(vector_data.on[CustomDataRole.ToState])])[0]

            item = ItemData()
            item.on[CustomDataRole.Name] = state.attributes.name
            item.on[CustomDataRole.Description] = state.attributes.desrciption
            item.on[CustomDataRole.SynonymsSet] = s_model
            item.on[CustomDataRole.EnterStateId] = state.id().value
            item.on[CustomDataRole.SliderVisability] = False

            proj.flows_model.prepare_item(item)
            proj.flows_model.insertRow()

            print(ItemDataSerializer.to_string(item))

        # модель векторов
        self.__g_model = SynonymsGroupsModel(self.__main_window)

    def open_project(self) -> Project:
        pass

    def close_current(self):
        pass

    def export_current(self) -> TextIOWrapper:
        pass

    def publish_current():
        pass
