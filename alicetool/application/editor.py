from typing import Optional
from xml.etree.ElementTree import ElementTree, Element, tostring, fromstring, indent

from PySide6.QtWidgets import QMessageBox 

from alicetool.infrastructure.repositories.inmemory import HostingInmem
from alicetool.infrastructure.repositories.mariarepo import HostingMaria
from alicetool.domain.inputvectors.levenshtain import LevenshtainVector, Synonym, SynonymsGroup
from alicetool.domain.core.primitives import Name, Description, ScenarioID, SourceInfo, StateID, Output, Answer, StateAttributes
from alicetool.domain.core.bot import Scenario, Connection, Source, InputDescription, Step, State
from alicetool.domain.core.porst import ScenarioInterface
from alicetool.domain.core.exceptions import Exists

class HostingManipulator:
    @staticmethod
    def make_scenario(hosting: HostingInmem, info: SourceInfo) -> 'ScenarioManipulator':
        ''' создаёт заготовку сценария для алисы '''
        new_scenario = hosting.get_scenario(hosting.add_source(info))
        
        new_scenario.create_enter_state(
            LevenshtainVector(
                Name('Старт'),
                SynonymsGroup([
                    Synonym('Алиса, запусти навык ...'),
                ])
            )
        )

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name('Информация'), 
                SynonymsGroup([
                    Synonym('Информация'), 
                    Synonym('Справка'), 
                    Synonym('Расскажи о себе'),
                ])
            )
        )

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name('Помощь'), 
                SynonymsGroup([
                    Synonym('Помощь'), 
                    Synonym('Помоги'), 
                    Synonym('Как выйти'),
                ])
            )
        )

        for state in new_scenario.states().values():
            state.required = True
            state.attributes.output
        
        return ScenarioManipulator(new_scenario)

    def open_scenario(hosting: HostingInmem, data:str) -> 'ScenarioManipulator':
        root: Element = fromstring(data)
        scenario = hosting.get_scenario(hosting.add_source(SourceInfo(Name(root.attrib['Название']), Description(root.attrib['Краткое_описание']))))

        # добавляем векторы
        for elem in root.find('Управляющие_воздействия').findall('Описание'):
            synonyms = list[Synonym]()
            for synonym in elem.findall('Синоним'):
                synonyms.append(Synonym(synonym.text))

            scenario.add_vector(LevenshtainVector(Name(elem.attrib['Название']), SynonymsGroup(synonyms)))

        # добавляем состояния
        for elem in root.find('Состояния').findall('Состояние'):
            scenario.source().add_state(StateID(int(elem.attrib['Идентификатор'])), Name(elem.attrib['Название']), Output(Answer(elem.text)))

        # добавляем входы
        for elem in root.find('Входы').findall('Точка_входа'):
            scenario.make_enter(StateID(int(elem.attrib['Состояние'])))

        # добавляем переходы
        for elem in root.find('Переходы').findall('Связи'):
            state_from_id = StateID(int(elem.attrib['Состояние']))
            for step in elem.findall('Переход'):
                state_to_id = StateID(int(step.attrib['В_состояние']))
                for input in step.findall('Управляющее_воздействие'):
                    _vector = scenario.get_vector(Name(input.attrib['Название']))
                    scenario.create_step(state_from_id, state_to_id, _vector)

        return ScenarioManipulator(scenario)

    def make_scenario_in_db(hosting: HostingMaria, info: SourceInfo) -> 'ScenarioManipulator':
        ''' создаёт заготовку сценария для алисы в MariaDB '''
        new_scenario = hosting.get_scenario(hosting.add_source(info))

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name('Старт'),
                SynonymsGroup([
                    Synonym('Алиса, запусти навык ...'),
                ])
            )
        )

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name('Информация'), 
                SynonymsGroup([
                    Synonym('Информация'), 
                    Synonym('Справка'), 
                    Synonym('Расскажи о себе'),
                ])
            )
        )

        new_scenario.create_enter_state(
            LevenshtainVector(
                Name('Помощь'), 
                SynonymsGroup([
                    Synonym('Помощь'), 
                    Synonym('Помоги'), 
                    Synonym('Как выйти'),
                ])
            )
        )
        
        return ScenarioManipulator(new_scenario)

class ScenarioManipulator:
    __scenario: ScenarioInterface

    def __init__(self, scenario: ScenarioInterface) -> None:
        self.__scenario = scenario

    def id(self) -> int:
        return self.__scenario.source().id.value

    def name(self) -> str:
        return self.__scenario.source().info.name.value
    
    def description(self) -> str:
        return self.__scenario.source().info.description.value
    
    # TODO заменить собственным интерфейсом
    def interface(self) -> ScenarioInterface:
        return self.__scenario
    
    def remove_synonym(self, input_name: str, synonym: str):
        ''' удаляет синоним '''
        vector:LevenshtainVector = self.interface().get_vector(Name(input_name))
        if not isinstance(vector, LevenshtainVector):
             raise Warning('ошибка получения вектора перехода')
        
        index = vector.synonyms.synonyms.index(Synonym(synonym))
        vector.synonyms.synonyms.pop(index)

    def remove_vector(self, input_name: str):
        ''' удаляет вектор '''        
        self.interface().remove_vector(Name(input_name))
        
    def remove_enter(self, state_id: int):
        ''' удаляет точку входа (переход) '''
        self.interface().remove_enter(StateID(state_id))
        
    def remove_step(self, from_state_id: int, input_name: str):
        ''' удаляет переход '''
        vector: InputDescription = self.interface().get_vector(Name(input_name))
        self.interface().remove_step(StateID(from_state_id), vector)
        
    def remove_state(self, state_id: int):
        ''' удаляет состояние '''
        self.interface().remove_state(StateID(state_id))
        
    def create_synonym(self, input_name: str, new_synonym: str):
        ''' создаёт синоним '''
        vector: LevenshtainVector = self.interface().get_vector(Name(input_name))
        if not isinstance(vector, LevenshtainVector):
            raise Warning('ошибка получения вектора перехода')
        
        synonym = Synonym(new_synonym)

        if synonym in vector.synonyms.synonyms:
            raise Exists(synonym, f'Синоним "{new_synonym}" группы "{input_name}"')
        
        vector.synonyms.synonyms.append(synonym)
        
    def add_vector(self, input_name: str):
        ''' создаёт вектор '''
        self.interface().add_vector(LevenshtainVector(Name(input_name)))
        
    def make_enter(self, state_id: int) -> str:
        ''' делает состояние точкой входа, возвращает имя вектора '''
        state_id_d = StateID(state_id)
        state:State = self.interface().states([state_id_d])[state_id_d]
        
        vector_name = state.attributes.name

        try: # создаём новый вектор
            vector = LevenshtainVector(vector_name)
            self.interface().create_enter_vector(vector, state_id_d)
            
        except Exists as err:
            # если вектор уже существует - спрашиваем продолжать ли с ним
            ask_result = QMessageBox.information(
                None,
                'Подтверждение',
                f'{err.ui_text} Продолжить с существующим вектором?',
                QMessageBox.StandardButton.Apply,
                QMessageBox.StandardButton.Abort
            )

            # если пользователь отказался - завершаем операцию
            if ask_result == QMessageBox.StandardButton.Abort:
                raise RuntimeError()
            
        self.interface().make_enter(state_id_d)
        
        return vector_name.value
        
    def create_step(self, from_state_id: int, to_state_id: int, input_name: str):
        ''' создаёт переход '''
        vector = self.interface().get_vector(Name(input_name))
        self.interface().create_step(StateID(from_state_id), StateID(to_state_id), vector)

    def create_step_to_new_state(self, from_state_id: int, input_name: str, new_state_name: str) -> dict:
        ''' создаёт состояние с переходом в него
            возвращает словарь с аттрибутами нового состояния: `id`, `name`, `text`
        '''
        vector = self.interface().get_vector(Name(input_name))
        step:Step = self.interface().create_step(StateID(from_state_id), StateAttributes(Output(Answer('текст ответа')), Name(new_state_name), ''), vector)
        to_state:State = step.connection.to_state

        return {
            'id': to_state.id().value,
            'name': to_state.attributes.name.value,
            'text': to_state.attributes.output.value.text,
        }
        
    def set_state_answer(self, state_id: int, new_value: str):
        ''' изменяет ответ состояния '''
        self.interface().set_answer(StateID(state_id), Output(Answer(new_value)))

    def rename_state(self, state_id: int, new_name: str):
        ''' изменяет имя состояния '''
        id = StateID(state_id)
        self.interface().states([id])[id].attributes.name = Name(new_name)
        
    def set_synonym_value(self, input_name, old_synonym, new_synonym):
        ''' изменяет значение синонима '''
        vector:LevenshtainVector = self.interface().get_vector(Name(input_name))
        if not isinstance(vector, LevenshtainVector):
             raise Warning('ошибка получения вектора перехода')
        
        index = vector.synonyms.synonyms.index(Synonym(old_synonym)) # raises ValueError if `old_synonym` not found
        vector.synonyms.synonyms[index] = Synonym(new_synonym)

    def steps_from(self, from_state:int) -> dict[int, list[str]]:
        ''' возвращает словарь переходов из состояния from_state. key - id состояния, val - список имём векторов '''
        result = dict[int, list[str]]()
        steps: list[Step] = self.interface().steps(StateID(from_state))
        for step in steps:
            if step.connection is None:
                continue

            if step.connection.from_state is None or step.connection.from_state.id().value != from_state:
                continue

            to_state:int = step.connection.to_state.id().value
            input_name:str = step.input.name().value
            if not to_state in result.keys():
                result[to_state] = [input_name]
            else:
                result[to_state].append(input_name)

        return result
                
    def save_to_file(self):
        ''' сохраняет сценарий в файл '''

    def serialize(self) -> str:
        ''' сформировать строку для сохранения в файл '''

        root = Element('сценарий', {'Идентификатор': str(self.id()), 'Название': self.name(), 'Краткое_описание': self.description()})
        vectors = Element('Управляющие_воздействия')
        states = Element('Состояния')
        enters = Element('Входы')
        steps = Element('Переходы')

        root.append(vectors)
        root.append(states)
        root.append(enters)
        root.append(steps)

        for vector in self.__scenario.select_vectors():
            if isinstance(vector, LevenshtainVector):
                _vector = Element('Описание', {'Название': vector.name().value, 'Тип': 'Группа синонимов'})
                for synonym in vector.synonyms.synonyms:
                    _synonym = Element('Синоним')
                    _synonym.text = synonym.value
                    _vector.append(_synonym)
                vectors.append(_vector)

        for state in self.__scenario.states().values():
            state: State = state
            _state = Element('Состояние', {'Идентификатор': str(state.id().value), 'Название': state.attributes.name.value})
            _state.text = state.attributes.output.value.text
            states.append(_state)

        connections = self.__scenario.source().get_all_connections()
        for enter_state_id in connections['to'].keys():
            enter_conn: Connection = connections['to'][enter_state_id]
            _enter = Element('Точка_входа', {'Состояние': str(enter_state_id.value)})

            for step in enter_conn.steps:
                vector:LevenshtainVector = step.input
                if isinstance(vector, LevenshtainVector):
                    _vector = Element('Управляющее_воздействие', {'Название': vector.name().value, 'Тип': 'Группа синонимов'})
                    for synonym in vector.synonyms.synonyms:
                        _synonym = Element('Синоним')
                        _synonym.text = synonym.value
                        _vector.append(_synonym)
                    _enter.append(_vector)

            enters.append(_enter)

        for from_state_id in connections['from'].keys():
            _conn = Element('Связи', {'Состояние': str(from_state_id.value)})
            for conn in connections['from'][from_state_id]:
                conn:Connection = conn # просто аннотирование
                _step = Element('Переход', {'В_состояние': str(conn.to_state.id().value)})
                for step in conn.steps:
                    vector:LevenshtainVector = step.input
                    if isinstance(vector, LevenshtainVector):
                        _vector = Element('Управляющее_воздействие', {'Название': vector.name().value, 'Тип': 'Группа синонимов'})
                        for synonym in vector.synonyms.synonyms:
                            _synonym = Element('Синоним')
                            _synonym.text = synonym.value
                            _vector.append(_synonym)
                        _step.append(_vector)
                
                _conn.append(_step)

            steps.append(_conn)

        indent(root)
        return tostring(root, 'unicode')

    @staticmethod
    def save_project(scenario:Scenario):
        ''' сохранить в БД '''

    @staticmethod
    def get_project(host, ids:list[ScenarioID] = None) -> list[Scenario]:
        ''' достать из БД '''
