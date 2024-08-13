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

    def get(self, name:Name) -> Optional['InputDescription']:
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

    def __init__(self, id: StateID, name:Name = None) -> None:
        self.__id = id
        _name = Name(str(id.value)) if name is None or name.value == '' else name
        self.attributes = StateAttributes(Output(Answer('текст ответа')), _name, Description(''))
        self.required = False

    def id(self) -> StateID:
        return self.__id

@dataclass
class Step:
    input: 'InputDescription'
    connection: Optional['Connection'] = None

@dataclass
class Connection:
    from_state: Optional[State]
    to_state: Optional[State]
    steps: list[Step]

class InputDescription:
    __name: Name

    def __init__(self, name: Name) -> None:
        self.__name = name

    def name(self) -> Name:
        return self.__name
    
    def __eq__(self, value: object) -> bool:
        return isinstance(value, InputDescription) and value.name() == self.__name

#class StepVectorBaseClassificator:
#    @staticmethod
#    def get_next_state(cmd:Input, cur_state:StateID) -> State:
#        raise NotImplementedError('Использование абстрактного класса')

@dataclass
class Source:
    id: Optional[ScenarioID]
    info: SourceInfo
    interface: ScenarioInterface

class Hosting:
    __sources: dict[ScenarioID, Source]
    __next_id: ScenarioID
    
    def __init__(self) -> None:
        self.__sources = []
        self.__next_id = ScenarioID(0)
    
    def add_source(self, info:SourceInfo) -> ScenarioID:
        id = self.__next_id
        self.__next_id = self.__next_id(self.__next_id.value +1)
        self.__next_id[id] = Source(id, info, Scenario())
        return id

class Scenario(ScenarioInterface):
    __new_state_id: int
    __states: dict[StateID, State]
    __connections: dict[str, dict] # ключи: 'from', 'to'; значения: <to> dict[StateID, Connection], <from> dict[StateID, list[Connection]]
    __input_vectors: PossibleInputs

# Scenario public

    def __init__(self) -> None:
        self.__states = {}
        self.__new_state_id = 0
        self.__connections = {'from':{}, 'to':{}}
        self.__input_vectors = PossibleInputs()

    # создание сущностей
    def create_enter_state(self, input:InputDescription):
        ''' добавляет вектор и новое состояние-вход с таким-же именем '''

        # создаём вектор
        self.__input_vectors.add(input)

        # создаём состояние
        state_to = self.__create_state()
        state_to.attributes.name = input.name()

        # делаем состояние точкой входа
        self.make_enter(state_to.id())

    def create_enter_vector(self, input:InputDescription, state_id: StateID):
        ''' Делает состояние точкой входа. Создаёт вектор с соответствующим состоянию именем '''
        # проверяем существование вектора
        vector_name = state_to = self.states([state_id])[state_id].attributes.name
        if self.__input_vectors.exists(vector_name):
            raise Exists(self.__input_vectors.get(vector_name), f'Вектор с именем "{vector_name.value}"')
        
        self.__input_vectors.add(input)
    
    def make_enter(self, state_id: StateID):
        ''' привязывает к состоянию существующий вектор с соответствующим именем как команду входа '''
        # получаем состояние
        state_to = self.states([state_id])[state_id]

        # проверяем является ли входом
        if self.is_enter(state_to):
            raise Exists(state_to, f'Точка входа в состояние "{state_to.id().value}"')
        
        input_name = state_to.attributes.name
        conn = Connection(None, self.__states[state_id], [])
        new_step = Step(self.__input_vectors.get(input_name), conn)
        conn.steps.append(new_step)
        self.__connections['to'][state_id] = conn

    def create_step(self, from_state_id:StateID, to_state:StateAttributes | StateID, input:InputDescription) -> Step:
        '''
        Создаёт переход из from_state в to_state по переходу input
        @from_state_id: id состояния для обработки управляющего воздействия input
        @to_state: id состояния в которое будет добавлен переход или аттрибуты для создания такого состояния
        @input: управляющее воздействие
        '''
        state_from = self.__states[from_state_id]
        state_to:State

        if isinstance(to_state, StateID):
            state_to = self.__states[to_state]

        elif isinstance(to_state, StateAttributes):
            state_to = self.__create_state()

            if to_state.name.value != '':
                state_to.attributes.name = to_state.name
            state_to.attributes.desrciption = to_state.desrciption
            state_to.attributes.output = to_state.output

        new_conn = Connection(state_from, state_to, [])

        # если это первый переход из этого состояния
        if not from_state_id in self.__connections['from'].keys():
            self.__connections['from'][from_state_id] = [new_conn]
            conn = new_conn

        else:
            found:Connection = None
            for _conn in self.__connections['from'][from_state_id]:
                _conn:Connection = _conn
                if _conn.to_state == state_to:
                    found = _conn
                    break

            if found is None:
                # это первый переход из state_from в state_to
                self.__connections['from'][from_state_id] = [new_conn]
                conn = new_conn
            else:
                conn = found

        for step in conn.steps:
            if step.input == input:
                raise RuntimeError('переход уже существует')

        new_step = Step(input, conn)
        conn.steps.append(new_step)
        
        return new_step

    # удаление сущностей

    def remove_state(self, state_id:StateID):
        ''' удаляет состояние '''

        # TODO: проверить существование состояния
        # TODO: проверить существование переходов в и из состояние

        self.__states.pop(state_id)

    def remove_enter(self, state_id:StateID):
        ''' удаляет связь с командой входа в состояние '''
        self.__connections['to'].pop(state_id)

    def remove_step(self, from_state_id:StateID, input:InputDescription):
        '''
        удаляет связь между состояниями
        @from_state_id: состояние - обработчик управляющих воздействий
        @input: управляющее воздействие
        '''

        '''
        TODO: добавить индексацию Step в Connection
        по ролям InputDescription когда они появятся

        роли нужны для выбора оптимального классификатора
        в зависимости от типа управляющего сигнала
        (кнопка / голос / текст / строгая команда в стиле CLI и т.д.)
        '''

        if not from_state_id in self.__connections['from'].keys():
            return # возможо стоит бросить исключение

        for conn in self.__connections['from'][from_state_id]:
            for step in conn.steps:
                if step.input == input:
                    conn.steps.remove(step)
                    
                    if len(conn.steps) == 0:
                        self.__connections['from'][from_state_id].remove(conn)
                    
                    if len(self.__connections['from'][from_state_id]) == 0:
                        self.__connections['from'].pop(from_state_id)
                    
                    return

    # геттеры

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
        
        for conn in self.__find_connections_to(state_id):
            for step in conn.steps:
                result.append(step)

        return list(result)
    
    # сеттеры

    def set_answer(self, state_id:StateID, data:Output):
        ''' Изменить ответ состояния '''
        self.__states[state_id].attributes.output = data

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

    def is_enter(self, state:State) -> bool:
        ''' Проверить является ли состояние входом '''
        return state.id() in self.__connections['to'].keys()

    # векторы

    def select_vectors(self, names:Optional[list[Name]] = None) -> list['InputDescription']:
        '''
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        '''
        return self.__input_vectors.select(names)
    
    def get_vector(self, name:Name) -> Optional['InputDescription']:
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
        return self.__input_vectors.remove(name)

    def check_vector_exists(self, name:Name) -> bool:
        '''
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        '''
        return self.__input_vectors.exists(name)

# Scenario private

    def __create_state(self) -> State:
        new_state = State(StateID(self.__new_state_id))
        self.__new_state_id = self.__new_state_id + 1
        self.__states[new_state.id()] = new_state
        return new_state

    def __find_connections_to(self, state_id:StateID) -> list[Connection]:
        result = list[Connection]()
        for connections in self.__connections['from'].values():
            for conn in connections:
                to_state:State = conn.to_state
                if not to_state is None and to_state.id() == state_id:
                    result.append(conn)

        return result
