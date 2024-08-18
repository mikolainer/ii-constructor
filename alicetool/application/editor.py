from alicetool.domain.inputvectors.levenshtain import LevenshtainVector, Synonym, SynonymsGroup
from alicetool.domain.core.primitives import Name, Description, ScenarioID, SourceInfo, StateID, Output, Answer, StateAttributes
from alicetool.domain.core.bot import Scenario, Connection, Hosting, Source, InputDescription, Step, State
from alicetool.domain.core.porst import ScenarioInterface

class HostingManipulator:
    @staticmethod
    def make_scenario(hosting: Hosting, info: SourceInfo) -> 'ScenarioManipulator':
        ''' создаёт заготовку сценария для алисы '''
        source = hosting.get_source(hosting.add_source(info))
        new_scenario = source.interface
        
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
        
        return ScenarioManipulator(source)

class ScenarioManipulator:
    __source: Source

    def __init__(self, source: Source) -> None:
        self.__source = source

    def id(self) -> str:
        return self.__source.id.value

    def name(self) -> str:
        return self.__source.info.name.value
    
    def description(self) -> str:
        return self.__source.info.description.value
    
    # TODO заменить собственным интерфейсом
    def interface(self) -> ScenarioInterface:
        return self.__source.interface
    
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
        
    def add_vector(self, input_name: str):
        ''' создаёт вектор '''
        self.interface().add_vector(LevenshtainVector(Name(input_name)))
        
    def make_enter(self, state_id: int):
        ''' делает состояние точкой входа '''
        
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

    def rename_state(self, state_id: int, new_name: str):
        ''' изменяет имя состояния '''
        
    def set_synonym_value(self, input_name, old_synonym, new_synonym):
        ''' изменяет значение синонима '''
        vector:LevenshtainVector = self.interface().get_vector(Name(input_name))
        if not isinstance(vector, LevenshtainVector):
             raise Warning('ошибка получения вектора перехода')
        
        index = vector.synonyms.synonyms.index(Synonym(old_synonym)) # raises ValueError if `old_synonym` not found
        vector.synonyms.synonyms[index] = Synonym(new_synonym)
        
    def check_vector_exists(self, name) -> bool:
        ''' проверяет существование вектора '''
        
    def save_to_file(self):
        ''' сохраняет сценарий в файл '''

    def serialize(self) -> str:
        ''' сформировать строку для сохранения в файл '''
        scenario = self.__source.interface

        answer = list[str]()
        answer.append(f'Идентификатор: {self.id()}')
        answer.append(f'Название: {self.name()}')
        answer.append(f'Краткое описание: {self.description()}')

        vectors = list[list[str]]()
        for vector in scenario.select_vectors():
            _vector = list[str]()
            _vector.append('{')
            _vector.append(f'\tназвание: "{vector.name().value}"')
            _vector.append(f'\t{"["}')
            for synonym in vector.synonyms.synonyms:
                _vector.append(f'\t\t"{synonym.value}",')
            _vector.append(f'\t{"]"}')
            _vector.append('}')
            vectors.append(_vector)


        states = list[list[str]]()
        for state in scenario.states().values():
            _state = list[str]()
            _state.append('{')
            _state.append(f'\tid: {state.id().value}')
            _state.append(f'\tИмя: {state.attributes.name.value}')
            _state.append(f'\tОтвет: {state.attributes.output.value.text}')
            _state.append('}')
            states.append(_state)

        enters = list[list[str]]()
        very_bad_thing = scenario._Scenario__connections
        for enter_state_id in very_bad_thing['to'].keys():
            enter_conn: Connection = very_bad_thing['to'][enter_state_id]
            enter = list[str]()
            enter.append('{')
            enter.append(f'\tсостояние: {enter_state_id.value}')
            enter.append(f'\tпереходы:')
            enter.append(f'\t{"["}')
            for step in enter_conn.steps:
                vector:LevenshtainVector = step.input
                enter.append(f'\t\t{"["}')
                for synonym in vector.synonyms.synonyms:
                    enter.append(f'\t\t\t"{synonym.value}",')
                enter.append(f'\t\t{"]"}')
            enter.append(f'\t{"]"}')
            enter.append('}')
            enters.append(enter)

        connections = list[list[str]]()
        for from_state_id in very_bad_thing['from'].keys():
            _conn = list[str]()
            _conn.append('{')
            _conn.append(f'\tиз состояния: {from_state_id.value}')
            for conn in very_bad_thing['from'][from_state_id]:
                conn:Connection = conn # просто аннотирование
                _conn.append(f'\tпереходы в состояние {conn.to_state.id().value}:')
                _conn.append(f'\t{"["}')
                for step in conn.steps:
                    vector:LevenshtainVector = step.input
                    _conn.append(f'\t\t{"["}')
                    for synonym in vector.synonyms.synonyms:
                        _conn.append(f'\t\t\t"{synonym.value}",')
                    _conn.append(f'\t\t{"]"}')
                _conn.append(f'\t{"]"}')
            _conn.append('}')
            connections.append(_conn)

        answer.append('')
        answer.append('[Векторы перехода (Наборы синонимов)]')
        answer.append('{')
        for vector in vectors:
            for line in vector:
                answer.append(f'\t{line}')
        answer.append('}')

        answer.append('')
        answer.append('[Состояния]')
        answer.append('{')
        for state in states:
            for line in state:
                answer.append(f'\t{line}')
        answer.append('}')

        answer.append('')
        answer.append('[Входы]')
        answer.append('{')
        for enter in enters:
            for line in enter:
                answer.append(f'\t{line}')
        answer.append('}')

        answer.append('')
        answer.append('[Переходы]')
        answer.append('{')
        for connection in connections:
            for line in connection:
                answer.append(f'\t{line}')
        answer.append('}')

        return '\n'.join(answer)

    @staticmethod
    def save_project(scenario:Scenario):
        ''' сохранить в БД '''

    @staticmethod
    def get_project(host, ids:list[ScenarioID] = None) -> list[Scenario]:
        ''' достать из БД '''
