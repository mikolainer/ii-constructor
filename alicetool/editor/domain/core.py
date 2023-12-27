''' предварительные объявления '''

class State: pass
class Flow: pass
class Synonyms: pass



''' объекты модели '''

class Command:
    def __init__(self, next_state: State , cmd: Synonyms):
        if not isinstance(next_state, State):
            raise TypeError('"next_state" должен обыть объектом типа State')
        
        if not isinstance(cmd, Synonyms):
            raise TypeError('"cmd" должен обыть объектом типа Synonyms')

        self.__next_state : State = next_state
        self.__cmd: Synonyms = cmd

    def next_state(self) -> State:
        return self.__next_state
    
    def cmd(self) -> Synonyms:
        return self.__cmd

class State:
    __steps: list[Command] = []
    __content: str = 'text'
    __name: str = None

    def __str__(self):
        next_states = []

        for step in self.__steps:
            next_states.append(str(step.next_state(self).id()))

        steps = ','.join(next_states)
        return '; '.join([
            f'id={self.__id}',
            f'name={self.__name}',
            f'steps={steps}',
            f'content={self.__content}',
        ])

    def parse(data:str):
        _data = {}

        if data == '':
            return _data

        for item in data.split('; '):
            _item = item.split('=')

            if len(_item) != 2:
                raise AttributeError(
                    f'Плохие данные: синтаксическая ошибка "{item}"'
                )
            
            key = _item[0]
            value = _item[1]

            if key not in ['id', 'name', 'steps', 'content']:
                raise AttributeError(
                    f'Плохие данные: неизвестный ключ "{key}"'
                )
            
            if key == 'steps':
                steps : list[int] = []

                if (value != ''):
                    for step in value.split(','):
                        steps.append(int(step))

                _data[key] = steps

            elif key == 'id':
                _data[key] = int(value)

            else:
                _data[key] = value

#        if 'id' not in _data.keys():
#            raise AttributeError('Плохие данные: нет обязательного ключа "id"')

        return _data

    def __init__(self, id: int, **kwargs):
        if type(id) is not int:
            raise TypeError('первый позиционный аргумент "id" должен быть целым числом')
        
        self.__id: int = id
        self.update(**kwargs)

        if 'name' not in kwargs.keys():
            self.__name: str = str(self.__id)

    def update(self, **kwargs):
        if 'name' in kwargs.keys():
            self.__name: str = kwargs['name']

        if 'content' in kwargs.keys():
            self.__content: str = kwargs['content']

    def id(self):
        return self.__id
    
    def name(self):
        return self.__name
    
    def content(self):
        return self.__content
    
    def steps(self):
        return self.__steps
    
    def new_step(self, nextState: State, cmd: Synonyms) -> Command:
        pass

    def remove_step(self, cmd: Command):
        pass

class Flow:
    __name :str = 'Flow name'
    __description :str = 'Flow description'
    __required :bool = False
    __enter :Command = None

    def __init__(self, id: int, **kwargs):
        if type(id) is not int:
            raise TypeError('первый позиционный аргумент "id" должен быть целым числом')
        
        self.__id :int = id

        arg_names = kwargs.keys()

        if 'name' in arg_names:
            if type(kwargs['name']) is not str:
                raise TypeError('"name" должен быть строкой')
            self.__name: str = kwargs['name']

        if 'description' in arg_names:
            if type(kwargs['description']) is not str:
                raise TypeError('"description" должен быть строкой')
            self.__description: str = kwargs['description']

        if 'required' in arg_names:
            if type(kwargs['required']) is not bool:
                raise TypeError('"required" должен быть булевым')
            self.__required: str = kwargs['required']

        # TODO: обращение к фабрикам состояний и синонимов
        _state = State(0)
        if 'start_content' in arg_names:
            if type(kwargs['start_content']) is not str:
                raise TypeError('"start_content" должен быть объектом Command или None')
            
            _state = State(0, content = kwargs['start_content'])
        
        else:
            _state = State(0)

        _synonyms = Synonyms(0)
        self.__enter = Command(_state, _synonyms)
        _synonyms.add_command(self.__enter)

    def id(self) -> int:
        return self.__id
    
    def name(self) -> str:
        return self.__name
    
    def description(self) -> str:
        return self.__description

    def enter(self) -> Command:
        return self.__enter

    def is_required(self) -> bool:
        return self.__required
    
    def call_names(self) -> list[str]:
        return self.__enter.cmd().values()

class Synonyms:
    __name :str = None
    __values :list[str] = []
    __commands :list[Command] = []

    def __init__(self, id: int, **kwargs):
        if type(id) is not int:
            raise TypeError('первый позиционный аргумент "id" должен быть целым числом')
        
        self.__id :int = id

        arg_names = kwargs.keys()

        if 'name' in arg_names:
            if not isinstance(kwargs['name'], str):
                raise TypeError('"name" должен быть строкой')
            self.__name = kwargs['name']

        if 'values' in arg_names:
            if not (
                isinstance(kwargs['values'], list) and
                all(isinstance(x, str) for x in kwargs['values'])
            ):
                raise TypeError('"values" должен быть списком строк')
           
            self.__values = kwargs['values']

        if 'commands' in arg_names:
            if not (
                isinstance(kwargs['commands'], list) and
                all(isinstance(x, Command) for x in kwargs['commands'])
            ):
                raise TypeError('"commands" должен быть списком объектов Command')
            
            self.__commands = kwargs['commands']
        else:
            self.__commands = []
        
    def id(self) -> int:
        return self.__id

    def name(self):
        return str(self.__id) if self.__name is None else self.__name

    def add_value(self, value: str):
        if not isinstance(value, str):
            raise TypeError('"value" должен быть строкой')
        self.__values.append(value)

    def remove_value(self, value: str):
        if value not in self.__values:
            raise ValueError(f'синонима {value} нет в этом наборе')
        self.__values.remove(value)

    def add_command(self, cmd: Command):
        if not isinstance(cmd, Command):
            raise TypeError('"cmd" должен быть объектом Command')
        self.__commands.append(cmd)

    def remove_command(self, cmd: Command):
        if cmd not in self.__commands:
            raise ValueError(f'команда {cmd} не связана с этими синонимами')
        self.__commands.remove(cmd)

    def values(self) -> list[str]:
        return self.__values.copy()

    def commands(self) -> list[Command]:
        return self.__commands.copy()

''' интерфейсы обратной связи '''

class FlowActionsNotifier:
    def flow_created(self, project_id :int, id :int, data):
        raise NotImplementedError()
    
    def flow_updated(self, project_id :int, id :int, new_data):
        raise NotImplementedError()
    
    def flow_removed(self, project_id :int, id :int):
        raise NotImplementedError()

class SynonymsActionsNotifier:
    def synonyms_created(self, project_id :int, id :int, data):
        raise NotImplementedError()
    
    def synonyms_updated(self, project_id :int, id :int, new_data):
        raise NotImplementedError()
    
    def synonyms_removed(self, project_id :int, id :int):
        raise NotImplementedError()
    
class StateActionsNotifier:
    def state_created(self, project_id :int, id :int, data):
        raise NotImplementedError()
    
    def state_updated(self, project_id :int, id :int, new_data):
        raise NotImplementedError()
    
    def state_removed(self, project_id :int, id :int):
        raise NotImplementedError()



''' интерфейсы управления '''

class FlowInterface:
    def create_flow(self, data) -> int:
        raise NotImplementedError()
    
    def read_flow(self, id: int) -> Flow:
        raise NotImplementedError()

    def update_flow(self, id: int, new_data):
        raise NotImplementedError()

    def delete_flow(self, id: int):
        raise NotImplementedError()

    def flows(self) -> set[int]:
        raise NotImplementedError()

    def set_flow_notifier(self, notifier: FlowActionsNotifier):
        raise NotImplementedError()
    
class StateInterface:
    def create_state(self, data) -> int:
        raise NotImplementedError()
    
    def read_state(self, id: int) -> str:
        raise NotImplementedError()

    def update_state(self, id: int, new_data):
        raise NotImplementedError()

    def delete_state(self, id: int):
        raise NotImplementedError()

    def states(self) -> set[int]:
        raise NotImplementedError()

    def set_state_notifier(self, notifier: StateActionsNotifier):
        raise NotImplementedError()

class SynonymsInterface:
    def create_synonyms(self, data) -> int:
        raise NotImplementedError()
    
    def read_synonyms(self, id: int) -> Synonyms:
        raise NotImplementedError()

    def update_synonyms(self, id: int, new_data):
        raise NotImplementedError()

    def delete_synonyms(self, id: int):
        raise NotImplementedError()

    def synonyms(self) -> set[int]:
        raise NotImplementedError()

    def set_synonyms_notifier(self, notifier: SynonymsActionsNotifier):
        raise NotImplementedError()



''' фабрики '''
class FlowFactory(FlowInterface):
    __items: dict[int, Flow] = {}
    __notifier: FlowActionsNotifier = None

class SynonymsFactory(SynonymsInterface):
    __items: dict[int, Synonyms] = {}
    __notifier: SynonymsActionsNotifier = None

class StateFactory(StateInterface):
    __items: dict[int, State] = {}
    __notifier: StateActionsNotifier = None

    def create_state(self, data) -> int:
        ''' создать состояние и вернуть его id '''
        id = 1
        
        current_len = len(self.__items)
        if current_len > 0:
            current_keys = list(self.__items.keys())
            last_key = current_keys[-1]

            # проверяем пропуски в id
            if current_len - last_key == 0:
                id = last_key + 1
            else:
                id = (set(range(1, last_key+1)) - set(current_keys) ).pop()

        self.__items[id] = State(id, **State.parse(data))
        if self.__notifier is not None:
            self.__notifier.state_created(None, id, data)
        
        return id
    
    def read_state(self, id: int) -> str:
        ''' получить данные состояния '''
        if id not in self.__items.keys():
            raise ValueError(f'состояние с id={id} не существует')

        return self.__items[id].__str__()
    

    def update_state(self, id: int, new_data):
        ''' обновить состояние '''

        # TODO: реализовать изменение состояния

        if self.__notifier is not None:
            self.__notifier.state_updated(None, id, new_data)

    def delete_state(self, id: int):
        ''' удалить состояние '''

        if id not in self.__items.keys():
            raise ValueError(f'состояние с id={id} не существует')
        
        del self.__items[id]

        if self.__notifier is not None:
            self.__notifier.state_removed(0, id)

    def states(self) -> set[int]:
        ''' возвращает id существующих состояний проекта '''
        return self.__items.keys()

    def set_state_notifier(self, notifier: StateActionsNotifier):
        ''' сеттер обработчика коллбэков '''
        self.__notifier = notifier