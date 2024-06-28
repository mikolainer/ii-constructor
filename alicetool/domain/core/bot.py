from dataclasses import dataclass
from typing import Optional

from alicetool.domain.core.primitives import Name, Description, StateID, ScenarioID, Answer, Output, StateAttributes, Input

class PossibleInputs:
    __inputs: dict[Name, 'InputDescription']
    
    def __init__(self) -> None:
        self.__inputs = {}

    def __len__(self) -> int:
        return len(self.__inputs)

    def add(self, input_type:'InputDescription'):
        name = input_type.name()
        if name in self.__inputs.keys():
            raise RuntimeWarning('Имя занято')
        
        self.__inputs[name] = input_type
        
    def remove(self, name:Name):
        if not name in self.__inputs.keys():
            raise RuntimeWarning('Нет входного вектора с таким именем')
        
        del self.__inputs[name]


    def get(self, names:Optional[list[Name]] = None) -> list['InputDescription']:
        if names is None:
            return list(self.__inputs.copy().values())
        
        if len(names) == 0:
            return []

        inputs_list: list[InputDescription] = []
        for name in names:
            inputs_list.append(self.__inputs[name])

        return inputs_list

class State:
    __id: StateID
    required: bool
    attributes: StateAttributes

    def __init__(self, id: StateID, name:Name = None) -> None:
        self.__id = id
        _name = Name(str(id.value)) if name is None else name
        self.attributes = StateAttributes(Output(Answer('текст ответа')), _name, Description(''))
        self.required = False

    def id(self) -> StateID:
        return self.__id

@dataclass
class Step:
    name: Name
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

class StepVectorBaseClassificator:
    @staticmethod
    def get_next_state(cmd:Input, cur_state:StateID) -> State:
        raise NotImplementedError('Использование абстрактного класса')
    
class Scenario:
    name: Name
    description: Description
    host: Optional[str]
    id: Optional[ScenarioID]

    __new_state_id: int
    __states: dict[StateID, State]
    __connections: dict[str, dict] # ключи: 'from', 'to'; значения: dict[StateID, Connection]
    __input_vectors: PossibleInputs

    def __init__(self, name:Name, description: Description, host: str = None, id: ScenarioID = None, states: dict[StateID, State] = {}) -> None:
        self.name = name
        self.description = description
        self.host = host
        self.id = id
        self.__states = states
        self.__new_state_id = 0
        self.__connections = {'from':{}, 'to':{}}

    def __create_state(self) -> State:
        new_state = State(StateID(self.__new_state_id))
        self.__new_state_id = self.__new_state_id + 1
        self.__states[new_state.id()] = new_state
        return new_state
    
    def __find_connection(self, from_state_id: Optional[StateID] = None, to_state_id: Optional[StateID] = None) -> Optional[Connection]:
        if (not to_state_id is None and from_state_id in self.__connections['from']):
            return self.__connections['from'][from_state_id]
        
        elif (not to_state_id is None and from_state_id in self.__connections['to']):
            return self.__connections['to'][from_state_id]
        
        return None

    def set_answer(self, state_id:StateID, data:Output):
        self.__states[state_id].attributes.output = data

    def remove_state(self, state_id:StateID):
        pass

    def create_step(self, from_state_id:StateID, to_state:StateAttributes | StateID, input:InputDescription, input_name:Optional[Name] = None):
        state_from = self.__states[from_state_id]
        state_to:State
        
        conn = self.__find_connection(from_state_id=from_state_id)

        if isinstance(to_state, StateID):
            state_to = self.__states[to_state]

        elif isinstance(to_state, StateAttributes):
            state_to = self.__create_state()
            state_to.attributes = to_state

        step_name = Name(f'шаг из "{state_from.attributes.name.value}" в "{state_to.name.value}"') if input_name is None else input_name
        conn.steps.append(Step(step_name, input))
            

    def remove_step(self, from_state_id:StateID, input:InputDescription):
        conn = self.__find_connection(from_state_id=from_state_id)

        '''
        TODO: добавить индексацию Step в Connection
        по ролям InputDescription когда они появятся

        роли нужны для выбора оптимального классификатора
        в зависимости от типа управляющего сигнала
        (кнопка / голос / текст / строгая команда в стиле CLI и т.д.)
        '''
        for step in conn.steps:
            if step.input == input:
                conn.steps.remove(step)
                break

        if len(conn.steps) == 0:
            self.__connections['from'].pop(from_state_id)

    def create_enter(self, input:InputDescription, state:Optional[StateID | Name]):
        state_to: State

        conn:Connection = None
        if isinstance(state, StateID):
            state_to = self.__states[state]
            conn = self.__find_connection(to_state_id=state)
        else:
            state_to = self.__create_state()

        if isinstance(state, Name):
            state_to.attributes.name = state

        step_name = Name(f'вход в "{state_to.attributes.name.value}"')
        step = Step(step_name, input)

        if conn is None:
            conn = Connection(None, state_to, [step])
            self.__connections['to'][state_to.id()] = conn
        else:
            conn.steps.append(step)

    def remove_enter(self, state_id:StateID):
        conn = self.__find_connection(to_state_id=state_id)

        if not conn.from_state is None:
            ''' TODO: возможно стоит бросить исключение '''
            return
        
        self.__connections['to'].pop(state_id)

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        if ids is None:
            return self.__states.copy()
        
        states: dict[StateID, State] = {}
        for id in ids:
            states[id] = self.__states[id]
        
        return states

    def steps(self, from_state_id:StateID, to_state_id:StateID = None) -> list[Step]:
        conn = self.__find_connection(from_state_id, to_state_id)
        return [] if conn is None else conn.steps
    
    def enters(self) -> list[Connection]:
        return list(self.__connections['to'].values())
    
    def connections(self) -> list[Connection]:
        all_connections = list(self.__connections['from'].values()).copy()
        for conn in self.__connections['to'].values():
            all_connections.append(conn)

        return all_connections

    def inputs(self) -> PossibleInputs:
        return self.__input_vectors