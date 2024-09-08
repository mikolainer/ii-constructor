from dataclasses import dataclass
from typing import Optional, Any

from alicetool.domain.core.primitives import Name, Description, StateID, ScenarioID, Answer, Output, StateAttributes, Input, SourceInfo
from alicetool.domain.core.exceptions import *
from alicetool.domain.core.porst import ScenarioInterface

def get_type_name(obj:Any) -> str:
    ''' Определение названия объекта доменной области, для короткого использования инсключений '''

    _obj_type = "Объект"

    if issubclass(obj, (Scenario)):
        _obj_type = "Сценарий"

    elif issubclass(obj, (State)):
        _obj_type = "Состояние"

    elif issubclass(obj, (Connection)):
        _obj_type = "Связь"

    elif issubclass(obj, (Step)):
        _obj_type = "Переход"

    elif issubclass(obj, (InputDescription)):
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
        if name in self.__inputs.keys():
            raise _Exists(self.__inputs[name])
        
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

#class StepVectorBaseClassificator:
#    @staticmethod
#    def get_next_state(cmd:Input, cur_state:StateID) -> State:
#        raise NotImplementedError('Использование абстрактного класса')

class Source():
    id: Optional[ScenarioID]
    info: SourceInfo

    def __init__(self, id:Optional[ScenarioID], info: SourceInfo):
        self.id = id
        self.info = info

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
    def add_state(self, id:StateID, name:Name, output:Output):
        ''' только для открытия из файла '''

    def create_state(self, attributes:StateAttributes) -> State:
        ''' Создать состояние '''

    def find_connections_to(self, state_id:StateID) -> list[Connection]:
        ''' Получить входящие связи '''
    
    def input_usage(self, input: InputDescription) -> list[Connection]:
        ''' Получить связи, в которых используется вектор '''

    def new_step(self, from_state: Optional[StateID], to_state: StateID, input_name: Name) -> Step:
        ''' создаёт переходы и связи '''
    
    def delete_step(self, from_state: Optional[StateID], to_state: Optional[StateID], input_name: Optional[Name] = None):
        ''' удаляет переходы и связи '''

class SourceInMemory(Source):
    __new_state_id: int
    __states: dict[StateID, State]
    __connections: dict[str, dict] # ключи: 'from', 'to'; значения: <to> dict[StateID, Connection], <from> dict[StateID, list[Connection]]
    __input_vectors: PossibleInputs

    def __init__(self, id:Optional[ScenarioID], info: SourceInfo) -> None:
        super().__init__(id, info)

        self.__states = {}
        self.__new_state_id = 0
        self.__connections = {'from':{}, 'to':{}}
        self.__input_vectors = PossibleInputs()

    def delete_state(self, state_id:StateID):
        self.__states.pop(state_id)

    def get_states_by_name(self, name: Name) -> list[State]:
        ''' получить все состояния с данным именем '''
        result = list[State]()
        for state in self.__states.values():
            if state.attributes.name == name:
                result.append(state)

        return result
    
    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        ''' получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния'''
        if ids is None:
            return self.__states
        
        states: dict[StateID, State] = {}
        for id in ids:
            if not id in self.__states.keys():
                raise NotExists(id, f'Нет состояния с id "{id.value}"')
            states[id] = self.__states[id]
        
        return states
    
    def steps(self, state_id:StateID) -> list[Step]:
        ''' получить все переходы, связанные с состоянием по его идентификатору '''
        result = list[Step]()
        
        if state_id in self.__connections['from'].keys():
            for conn in self.__connections['from'][state_id]:
                for step in conn.steps:
                    result.append(step)
        
        if state_id in self.__connections['to'].keys():
            for step in self.__connections['to'][state_id].steps:
                result.append(step)
        
        for conn in self.find_connections_to(state_id):
            for step in conn.steps:
                result.append(step)

        return list(result)

    def is_enter(self, state:State) -> bool:
        ''' Проверить является ли состояние входом '''
        return state.id() in self.__connections['to'].keys()

    # сеттеры

    def set_answer(self, state_id:StateID, data:Output):
        ''' Изменить ответ состояния '''
        self.__states[state_id].attributes.output = data

    # векторы

    def select_vectors(self, names:Optional[list[Name]] = None) -> list['InputDescription']:
        '''
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        '''
        return self.__input_vectors.select(names)
    
    def get_vector(self, name:Name) -> InputDescription:
        '''
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        '''
        return self.__input_vectors.get(name)

    def add_vector(self, input: InputDescription):
        '''
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        '''
        return self.__input_vectors.add(input)

    def remove_vector(self, name:Name):
        '''
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        '''
        input = self.get_vector(name)
        if len(self.input_usage(input)) > 0:
            raise Exists(name, f'Вектор с именем "{name.value}" используется в существующих переходах')
        
        return self.__input_vectors.remove(name)

    def check_vector_exists(self, name:Name) -> bool:
        '''
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        '''
        return self.__input_vectors.exists(name)

# Scenario private
    def add_state(self, id:StateID, name:Name, output:Output):
        ''' только для открытия из файла '''
        if self.__new_state_id <= id.value:
            self.__new_state_id = id.value + 1

        state = State(id, StateAttributes(output, name, None))
        self.__states[state.id()] = state

    def create_state(self, attributes:StateAttributes) -> State:
        new_state = State(StateID(self.__new_state_id), attributes)
        self.__new_state_id = self.__new_state_id + 1
        self.__states[new_state.id()] = new_state
        return new_state

    def find_connections_to(self, state_id:StateID) -> list[Connection]:
        result = list[Connection]()
        for connections in self.__connections['from'].values():
            for conn in connections:
                to_state:State = conn.to_state
                if not to_state is None and to_state.id() == state_id:
                    result.append(conn)

        return result
    
    def input_usage(self, input: InputDescription) -> list[Connection]:
        ''' Получить связи, в которых используется вектор '''
        result = list[Connection]()
        
        for conn in self.__connections['to'].values():
            conn: Connection = conn
            for step in conn.steps:
                if step.input == input:
                    result.append(conn)
                    break
        
        for conn_list in self.__connections['from'].values():
            for conn in conn_list:
                conn: Connection = conn
                for step in conn.steps:
                    if step.input == input:
                        result.append(conn)
                        break
        
        return result

    def new_step(self, from_state: Optional[StateID], to_state: StateID, input_name: Name) -> Step:
        if not isinstance(to_state, StateID):
            raise TypeError(to_state)
        if not isinstance(input_name, Name):
            raise TypeError(input_name)
        if not self.check_vector_exists(input_name):
            raise ValueError(input_name)
        
        new_step: Step

        if from_state is None: # точка входа
            conn = Connection(None, self.__states[to_state], [])
            new_step = Step(self.__input_vectors.get(input_name), conn)
            conn.steps.append(new_step)
            self.__connections['to'][to_state] = conn

        else: # переход между состояниями
            if not isinstance(from_state, StateID):
                raise TypeError(from_state)
            if not isinstance(to_state, StateID):
                raise TypeError(to_state)

            state_to = self.__states[to_state]
            new_conn = Connection(self.__states[from_state], self.__states[to_state], [])

            # если это первый переход из этого состояния
            if not from_state in self.__connections['from'].keys():
                self.__connections['from'][from_state] = [new_conn]
                conn = new_conn

            else:
                found:Connection = None
                for _conn in self.__connections['from'][from_state]:
                    _conn:Connection = _conn
                    if _conn.to_state == state_to:
                        found = _conn
                        break

                if found is None:
                    # это первый переход из state_from в state_to
                    self.__connections['from'][from_state].append(new_conn)
                    conn = new_conn
                else:
                    conn = found

            for step in conn.steps:
                if step.input.name() == input_name:
                    raise RuntimeError('переход уже существует')

            new_step = Step(self.get_vector(input_name), conn)
            conn.steps.append(new_step)
        
        return new_step
    
    def delete_step(self, from_state: Optional[StateID], to_state: Optional[StateID], input_name: Optional[Name] = None):
        if from_state is None: # точка входа
            if not isinstance(to_state, StateID):
                raise TypeError(to_state)
            if not to_state in self.__connections['to']:
                raise ValueError(to_state)

            self.__connections['to'].pop(to_state)

        else: # переход
            if not isinstance(from_state, StateID):
                raise TypeError(from_state)
            if not from_state in self.__connections['from'].keys():
                raise ValueError(from_state)

            for conn in self.__connections['from'][from_state]:
                conn: Connection = conn

                for step in conn.steps:
                    step:Step = step
                    if step.input.name() == input_name:
                        conn.steps.remove(step)
                        
                        if len(conn.steps) == 0:
                            self.__connections['from'][from_state].remove(conn)
                        
                        if len(self.__connections['from'][from_state]) == 0:
                            self.__connections['from'].pop(from_state)
                        
                        return

class Hosting:
    __sources: dict[ScenarioID, ScenarioInterface]
    __next_id: ScenarioID
    
    def __init__(self) -> None:
        self.__sources = {}
        self.__next_id = ScenarioID(0)
    
    def add_source(self, info:SourceInfo) -> ScenarioID:
        id = self.__next_id
        self.__next_id = ScenarioID(self.__next_id.value +1)
        self.__sources[id] = Scenario(SourceInMemory(id, info))
        return id
    
    def get_scenario(self, id:ScenarioID) -> ScenarioInterface:
        return self.__sources[id]

class Scenario(ScenarioInterface):
    __src: Source

# Scenario public

    def __init__(self, src: Source) -> None:
        self.__src = src

    def source(self) -> Source:
        return self.__src

    # создание сущностей
    def create_enter_state(self, input:InputDescription):
        ''' добавляет вектор и новое состояние-вход с таким-же именем '''

        # создаём вектор
        self.add_vector(input)

        # создаём состояние
        state_to = self.__src.create_state(StateAttributes(None, input.name(), None))

        # делаем состояние точкой входа
        self.make_enter(state_to.id())

    def create_enter_vector(self, input:InputDescription, state_id: StateID):
        ''' Делает состояние точкой входа. Создаёт вектор с соответствующим состоянию именем '''
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
