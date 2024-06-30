from alicetool.domain.inputvectors.levenshtain import LevenshtainVector, Synonym
from alicetool.domain.core.primitives import Name, Description, ScenarioID
from alicetool.domain.core.bot import Scenario

class ScenarioFactory:
    @staticmethod
    def make_scenario(name:Name, description: Description) -> Scenario:
        ''' создаёт заготовку сценария для алисы '''
        new_project = Scenario(name, description)

        state_name = Name('Старт')
        input_vector = LevenshtainVector(state_name, [Synonym('Алиса, запусти навык ...')])
        new_project.create_enter(input_vector, state_name)

        state_name = Name('Информация')
        input_vector = LevenshtainVector(state_name, [Synonym('Информация'), Synonym('Справка'), Synonym('Расскажи о себе')])
        new_project.create_enter(input_vector, state_name)

        state_name = Name('Помощь')
        input_vector = LevenshtainVector(state_name, [Synonym('Помощь'), Synonym('Помоги'), Synonym('Как выйти')])
        new_project.create_enter(input_vector, state_name)

        for state in new_project.states().values():
            state.required = True
            state.attributes.output
        
        return new_project

class SourceControll:
    @staticmethod
    def save_project(scenario:Scenario):
        ''' сохранить в БД '''

    @staticmethod
    def get_project(host, ids:list[ScenarioID] = None) -> list[Scenario]:
        ''' достать из БД '''
