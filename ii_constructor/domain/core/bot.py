from dataclasses import dataclass
from typing import Optional, Any

from ii_constructor.domain.core.primitives import Name, Description, StateID, ScenarioID, Answer, Output, StateAttributes, Input, SourceInfo
from ii_constructor.domain.core.exceptions import *
from ii_constructor.domain.core.porst import ScenarioInterface

def get_type_name(obj:Any) -> str:
    ''' Определение названия объекта доменной области, для короткого использования инсключений '''

    _obj_type = "Объект"

    if issubclass(type(obj), Scenario):
        _obj_type = "Сценарий"

    elif issubclass(type(obj), State):
        _obj_type = "Состояние"

    elif issubclass(type(obj), Connection):
        _obj_type = "Связь"

    elif issubclass(type(obj), Step):
        _obj_type = "Переход"

    elif issubclass(type(obj), InputDescription):
        _obj_type = "Вектор"

    return _obj_type

class _Exists(Exists):
    def __init__(self, obj:Any):
        super().__init__(obj, get_type_name(obj))

class PossibleInputs:
    ''' Классификатор векторов управляющих воздействий '''

    __inputs: dict[Name, 'InputDescription']
    ''' Хранилище существующих векторов управляющих воздействий '''
    
    def __init__(self) -> None:
        self.__inputs = {}

    def __len__(self) -> int:
        return len(self.__inputs)

    def add(self, input_type:'InputDescription'):
        '''
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        '''
        name = input_type.name()
        self.__inputs[name] = input_type
        
    def remove(self, name:Name):
        '''
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        '''

        if not name in self.__inputs.keys():
            raise RuntimeWarning('Нет входного вектора с таким именем')
        
        del self.__inputs[name]

    def get(self, name:Name) -> 'InputDescription':
        '''
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        '''

        if not self.exists(name):
            raise NotExists(name, f'Вектор с именем "{name.value}"')

        return self.__inputs[name]

    def select(self, names:Optional[list[Name]] = None) -> list['InputDescription']:
        '''
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        '''

        if names is None:
            return list(self.__inputs.copy().values())
        
        if len(names) == 0:
            return []

        inputs_list: list[InputDescription] = []
        for name in names:
            inputs_list.append(self.get(name))

        return inputs_list
    
    def exists(self, name:Name) -> bool:
        '''
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        '''
        return name in self.__inputs.keys()

class State:
    __id: StateID
    required: bool
    attributes: StateAttributes

    def __init__(self, id: StateID, attributes:StateAttributes, required:bool = False) -> None:
        self.__id = id
        self.required = required
        self.attributes = attributes
        if attributes.name is None or attributes.name.value == '':
            attributes.name = Name(str(id.value))

        if attributes.description is None:
            attributes.description = Description('')
        
        if attributes.output is None or attributes.output.value.text == '':
            attributes.output = Output(Answer('текст ответа'))

    def id(self) -> StateID:
        return self.__id

class InputDescription:
    __name: Name

    def __init__(self, name: Name) -> None:
        self.__name = name

    def name(self) -> Name:
        return self.__name
    
    def set_name(self, new_name:Name) -> None:
        self.__name = new_name
    
    def __eq__(self, value: object) -> bool:
        return isinstance(value, InputDescription) and value.name() == self.__name

@dataclass
class Step:
    input: InputDescription
    connection: Optional['Connection'] = None

@dataclass
class Connection:
    from_state: Optional[State]
    to_state: Optional[State]
    steps: list[Step]

class StepVectorBaseClassificator:
    __project: ScenarioInterface
    
    def __init__(self, project: ScenarioInterface) -> None:
        self.__project = project

    def calc(self, cur_input: Input, possible_inputs: dict[str, State]) -> Optional[State]:
        ''' Вычисления '''
        raise NotImplementedError()
    
    def __prepare_to_step_detect(self, cur_state_id: StateID) -> dict[str, State]:
        inputs = dict[str, State]()
        for step in self.__project.steps(cur_state_id):
            step: Step = step
            
            cur_state = step.connection.from_state
            if cur_state is None or cur_state.id() != cur_state_id:
                continue

            inputs[step.input.name().value] = step.connection.to_state

        return inputs
    
    def __prepare_to_enter_detect(self) -> dict[str, State]:
        inputs = dict[str, State]()

        for conn in self.__project.source().get_all_connections()["to"].values():
            conn: Connection = conn
            to:State = conn.to_state

            for step in conn.steps:
                inputs[step.input.name().value] = to

        return inputs

    def get_next_state(self, cmd: Input, cur_state_id: StateID) -> State:
        cur_state = self.__project.states([cur_state_id])[cur_state_id]

        callable_list = [
            lambda: self.__prepare_to_step_detect(cur_state_id),
            lambda: self.__prepare_to_enter_detect()
        ]

        for get_inputs in callable_list:
            inputs = get_inputs()
            try:
                return self.calc(cmd, inputs)
            except Exception as e:
                result = cur_state

        return result

class Source():
    id: Optional[ScenarioID]
    info: SourceInfo

    def __init__(self, id:Optional[ScenarioID], info: SourceInfo):
        self.id = id
        self.info = info

    def get_layouts(self) -> str:
        ''' получить данные отображения '''

    def save_lay(self, id: StateID, x: float, y: float):
        ''' сохранить положение состояния '''

    def delete_state(self, state_id:StateID):
        ''' удалить состояние '''

    def get_states_by_name(self, name: Name) -> list[State]:
        ''' получить все состояния с данным именем '''
    
    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        ''' получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния'''
    
    def steps(self, state_id:StateID) -> list[Step]:
        ''' получить все переходы, связанные с состоянием по его идентификатору '''

    def is_enter(self, state:State) -> bool:
        ''' Проверить является ли состояние входом '''

    # сеттеры

    def set_answer(self, state_id:StateID, data:Output):
        ''' Изменить ответ состояния '''

    # векторы

    def select_vectors(self, names:Optional[list[Name]] = None) -> list['InputDescription']:
        '''
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        '''
    
    def get_vector(self, name:Name) -> InputDescription:
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

# Scenario private
    def create_state(self, attributes:StateAttributes, required:bool = False) -> State:
        ''' Создать состояние '''

    def find_connections_to(self, state_id:StateID) -> list[Connection]:
        ''' Получить входящие связи '''
    
    def input_usage(self, input: InputDescription) -> list[Connection]:
        ''' Получить связи, в которых используется вектор '''

    def new_step(self, from_state: Optional[StateID], to_state: StateID, input_name: Name) -> Step:
        ''' создаёт переходы и связи '''
    
    def delete_step(self, from_state: Optional[StateID], to_state: Optional[StateID], input_name: Optional[Name] = None):
        ''' удаляет переходы и связи '''

    def get_all_connections(self) -> dict[str, dict]:
        '''
        !!! DEPRECATED !!!\n
        получить все связи\n
        ключи: 'from', 'to'; значения: to=dict[StateID, Connection], from=dict[StateID, list[Connection]]
        '''
        #TODO: оптимизировать API. (фактически в память выгружается вся база)

    def set_synonym_value(self, input_name: str, old_synonym: str, new_synonym: str):
        ''' изменяет значение синонима '''
            
    def create_synonym(self, input_name: str, new_synonym: str):
        ''' создаёт синоним '''
            
    def remove_synonym(self, input_name: str, synonym: str):
        ''' удаляет синоним '''

    def rename_state(self, state:StateID, name:Name):
        ''' Переименовывает состояние '''
        
    def rename_vector(self, old_name:Name, new_name: Name):
        ''' переименовывает группу синонимов '''

class Hosting:
    def add_source(self, info:SourceInfo) -> ScenarioID:
        ''' Создать пустой проект '''

    def get_scenario(self, id:ScenarioID) -> ScenarioInterface:
        ''' Получить сценарий по id '''

class Scenario(ScenarioInterface):
    __src: Source

# Scenario public

    def __init__(self, src: Source) -> None:
        self.__src = src

    def source(self) -> Source:
        return self.__src
    
    def get_layouts(self) -> str:
        return self.__src.get_layouts()
    
    def save_lay(self, id: StateID, x: float, y: float):
        self.__src.save_lay(id, x, y)

    # создание сущностей
    def create_enter_state(self, input:InputDescription, required: bool = False):
        ''' добавляет вектор и новое состояние-вход с таким-же именем '''

        # создаём вектор
        self.add_vector(input)

        # создаём состояние
        state_to = self.__src.create_state(StateAttributes(None, input.name(), None), required)

        # делаем состояние точкой входа
        self.make_enter(state_to.id())

    def create_enter_vector(self, input:InputDescription, state_id: StateID):
        ''' Делает состояние точкой входа. Создаёт вектор с соответствующим состоянию именем '''
        _states = self.states()
        state_to = _states[state_id]
        for _state in _states.values():
            if _state.attributes.name == state_to.attributes.name and _state.id() != state_to.id():
                raise CoreException(f'Состояние-вход должно иметь уникальное имя!')
            
        # проверяем существование вектора c именем состояния входа
        vector_name: Name = self.states([state_id])[state_id].attributes.name
        if self.check_vector_exists(vector_name):
            raise Exists(vector_name, f'Вектор с именем "{vector_name.value}"')
        
        self.add_vector(input)
    
    def make_enter(self, state_id: StateID):
        ''' привязывает к состоянию существующий вектор с соответствующим именем как команду входа '''
        # получаем состояние
        state_to = self.states([state_id])[state_id]

        # проверяем является ли входом
        if self.is_enter(state_to):
            raise Exists(state_to, f'Точка входа в состояние "{state_to.id().value}"')
        
        input_name = state_to.attributes.name
        self.__src.new_step(None, state_to.id(), input_name)

    def create_step(self, from_state_id:StateID, to_state:StateAttributes | StateID, input:InputDescription) -> Step:
        '''
        Создаёт переход из from_state в to_state по переходу input
        @from_state_id: id состояния для обработки управляющего воздействия input
        @to_state: id состояния в которое будет добавлен переход или аттрибуты для создания такого состояния
        @input: управляющее воздействие
        '''
        state_to:State

        if isinstance(to_state, StateID):
            state_to = self.states([to_state])[to_state]

        elif isinstance(to_state, StateAttributes):
            _states = self.states()
            for _state in _states.values():
                if _state.attributes.name == to_state.name and self.is_enter(_state):
                    raise CoreException(f'Cуществует состояние-вход с именем "{to_state.name.value}"! Состояние-вход должно иметь уникальное имя.')

            state_to = self.__src.create_state(to_state)

        return self.__src.new_step(from_state_id, state_to.id(), input.name())

    # удаление сущностей

    def remove_state(self, state_id:StateID):
        ''' удаляет состояние '''
        if self.states([state_id])[state_id].required:
            raise Exception("Обязательное состояние нельзя удалить!")
        
        if len(self.steps(state_id)) > 0:
            raise Exists(state_id, f'Состояние с id={state_id.value} связано с переходами!')

        self.__src.delete_state(state_id)

    def remove_enter(self, state_id:StateID):
        ''' удаляет связь с командой входа в состояние '''
        enter_state = self.states([state_id])[state_id]

        if enter_state.required:
            raise Exception("Обязательную точку входа нельзя удалить!")
        
        self.__src.delete_step(None, state_id)

    def remove_step(self, from_state_id:StateID, input:InputDescription):
        '''
        удаляет связь между состояниями
        @from_state_id: состояние - обработчик управляющих воздействий
        @input: управляющее воздействие
        '''
        self.__src.delete_step(from_state_id, None, input.name())

    # геттеры

    def get_states_by_name(self, name: Name) -> list[State]:
        ''' получить все состояния с данным именем '''
        return self.__src.get_states_by_name(name)
    
    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        ''' получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния''' 
        return self.__src.states(ids)
    
    def steps(self, state_id:StateID) -> list[Step]:
        ''' получить все переходы, связанные с состоянием по его идентификатору '''
        return self.__src.steps(state_id)

    def is_enter(self, state:State) -> bool:
        ''' Проверить является ли состояние входом '''
        return self.__src.is_enter(state)

    # сеттеры

    def set_answer(self, state_id:StateID, data:Output):
        ''' Изменить ответ состояния '''
        self.__src.set_answer(state_id, data)

    # векторы

    def select_vectors(self, names:Optional[list[Name]] = None) -> list['InputDescription']:
        '''
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        '''
        return self.__src.select_vectors(names)
    
    def get_vector(self, name:Name) -> InputDescription:
        '''
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        '''
        return self.__src.get_vector(name)

    def add_vector(self, input: InputDescription):
        '''
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        '''
        if self.check_vector_exists(input.name()):
            raise _Exists(self.get_vector(input.name()))
        
        return self.__src.add_vector(input)

    def remove_vector(self, name:Name):
        '''
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        '''
        self.__src.remove_vector(name)

    def check_vector_exists(self, name:Name) -> bool:
        '''
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        '''
        return self.__src.check_vector_exists(name)

    def set_synonym_value(self, input_name: str, old_synonym: str, new_synonym: str):
        ''' изменяет значение синонима '''
        self.__src.set_synonym_value(input_name, old_synonym, new_synonym)
            
    def create_synonym(self, input_name: str, new_synonym: str):
        ''' создаёт синоним '''
        self.__src.create_synonym(input_name, new_synonym)
            
    def remove_synonym(self, input_name: str, synonym: str):
        ''' удаляет синоним '''
        self.__src.remove_synonym(input_name, synonym)

    def rename_state(self, state:StateID, name:Name):
        ''' Переименовывает состояние '''
        if self.is_enter(self.__src.states([state])[state]):
            raise CoreException("Нельзя переименовать состояние, которое является входом")
        
        vector_exsists = True
        vector: InputDescription
        try:
            vector = self.get_vector(name)
        except:
            vector_exsists = False

        if vector_exsists:
            for _conn in self.__src.input_usage(vector):
                if _conn.from_state is None:
                    if self.is_enter(_conn.to_state):
                        raise CoreException(f'Состояние с именем "{name.value}" уже существует и является входом')

        self.__src.rename_state(state, name)

    def rename_vector(self, old_name:Name, new_name: Name):
        ''' переименовывает группу синонимов '''
        for state in self.get_states_by_name(old_name):
            if self.is_enter(state):
                raise CoreException("Нельзя переименовать вектор, который используется с точкой входа!")
            
        try:
            self.get_vector(new_name)
            raise CoreException(f'Вектор с именем "{new_name.value}" уже существует!')
        
        except NotExists:
            self.__src.rename_vector(old_name, new_name)
        
        except: raise
