from alicetool.domain.inputvectors.levenshtain import LevenshtainVector, Synonym, SynonymsGroup
from alicetool.domain.core.primitives import Name, Description, ScenarioID, SourceInfo
from alicetool.domain.core.bot import Scenario, Connection, Hosting, Source
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
