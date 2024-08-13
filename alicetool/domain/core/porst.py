from __future__ import annotations
from typing import Optional
from alicetool.domain.core.primitives import Name, StateID, Output, StateAttributes

class ScenarioInterface:
    def create_enter_state(self, input:InputDescription):
        ''' добавляет вектор и новое состояние-вход с таким-же именем '''

    def create_enter_vector(self, input:InputDescription, state_id: StateID):
        ''' Делает состояние точкой входа. Создаёт вектор с соответствующим состоянию именем '''
    
    def make_enter(self, state_id: StateID):
        ''' привязывает к состоянию существующий вектор с соответствующим именем как команду входа '''

    def create_step(self, from_state_id:StateID, to_state:StateAttributes | StateID, input:InputDescription) -> Step:
        '''
        Создаёт переход из from_state в to_state по переходу input
        @from_state_id: id состояния для обработки управляющего воздействия input
        @to_state: id состояния в которое будет добавлен переход или аттрибуты для создания такого состояния
        @input: управляющее воздействие
        '''

    # удаление сущностей

    def remove_state(self, state_id:StateID):
        ''' удаляет состояние '''

    def remove_enter(self, state_id:StateID):
        ''' удаляет связь с командой входа в состояние '''

    def remove_step(self, from_state_id:StateID, input:InputDescription):
        '''
        удаляет связь между состояниями
        @from_state_id: состояние - обработчик управляющих воздействий
        @input: управляющее воздействие
        '''

    # геттеры

    def get_states_by_name(self, name: Name) -> list[State]:
        ''' получить все состояния с данным именем '''
    
    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        ''' получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния'''
    
    def steps(self, state_id:StateID) -> list[Step]:
        ''' получить все переходы, связанные с состоянием по его идентификатору '''
    
    # сеттеры

    def set_answer(self, state_id:StateID, data:Output):
        ''' Изменить ответ состояния '''

    def input_usage(self, input: InputDescription) -> list[Connection]:
        ''' Получить связи, в которых используется вектор '''
        
    def is_enter(self, state:State) -> bool:
        ''' Проверить является ли состояние входом '''
        return state.id() in self.__connections['to'].keys()

    # векторы

    def select_vectors(self, names:Optional[list[Name]] = None) -> list['InputDescription']:
        '''
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        '''
    
    def get_vector(self, name:Name) -> Optional['InputDescription']:
        '''
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        '''

    def add_vector(self, input: InputDescription):
        '''
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        '''

    def remove_vector(self, name:Name):
        '''
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        '''

    def check_vector_exists(self, name:Name) -> bool:
        '''
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        '''