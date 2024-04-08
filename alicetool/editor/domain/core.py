class Command:
    def __init__(self, next_state: 'State', cmd: 'Synonyms'):
        if not isinstance(next_state, State):
            raise TypeError('"next_state" должен обыть объектом типа State')
        
        if not isinstance(cmd, Synonyms):
            raise TypeError('"cmd" должен обыть объектом типа Synonyms')

        self.__next_state : State = next_state
        self.__cmd: Synonyms = cmd

    def next_state(self) -> 'State':
        return self.__next_state
    
    def cmd(self) -> 'Synonyms':
        return self.__cmd

class State:
    TEXT_MAX_LEN:int = 1024

    __id: int
    __steps: list[Command]
    __content: str = 'text'
    __name: str = None

    def id(self):
        return self.__id
    
    def name(self):
        return self.__name
    
    def content(self):
        return self.__content
    
    def steps(self):
        return self.__steps

    def __init__(self, id: int, **kwargs):
        if type(id) is not int:
            raise TypeError('первый позиционный аргумент "id" должен быть целым числом')
        
        self.__id = id
        self.__steps = []
        self.update(**kwargs)

        if 'name' not in kwargs.keys():
            self.__name: str = str(self.__id)

    def update(self, **kwargs):
        if 'name' in kwargs.keys():
            self.__name: str = kwargs['name']

        if 'content' in kwargs.keys():
            self.__content: str = kwargs['content']

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
    
    @staticmethod
    def parse(data:str) -> dict:
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
                quoted :bool = len(value) >= 2 and value[0] == '"' and value[-1] == '"'
                _data[key] = value[1:-1] if quoted else value

        return _data
    
    def new_step(self, step:Command):
        self.__steps.append(step)

    def remove_step(self, synonyms_id: int):
        pass

class Flow:
    __id :int
    __name :str
    __description :str
    __required :bool
    __enter :Command

    def id(self) -> int:
        return self.__id
    
    def name(self) -> str:
        return str(self.__id) if self.__name is None else f'"{self.__name}"'
    
    def description(self) -> str:
        return '' if self.__description is None else f'"{self.__description}"'

    def enter(self) -> Command:
        return self.__enter

    def is_required(self) -> bool:
        return 'true' if self.__required else 'false'
    
    def synonym_group_id(self) -> int:
        return self.__enter.cmd().id()

    def call_names(self) -> list[str]:
        return self.__enter.cmd().values()

    
    def __init__(self, id: int, **kwargs):
        if type(id) is not int:
            raise TypeError('первый позиционный аргумент "id" должен быть целым числом')
        
        self.__id = id
        self.__name = 'Flow name'
        self.__description = 'Flow description'
        self.__required = False
        self.__enter = None

        self.update(**kwargs)

    def __str__(self):
        is_required = 'true' if self.__required else 'false'
        name = str(self.__id) if self.__name is None else f'"{self.__name}"'
        description = '' if self.__description is None else f'"{self.__description}"'

        return '; '.join([
            f'id={self.id()}',
            f'required={self.is_required()}',
            f'name={self.name()}',
            f'description={self.description()}',
            f'values={",".join(self.call_names())}',
            f'enter_state_id={self.__enter.next_state().id()}',
            f'synonym_group_id={self.synonym_group_id()}',
        ])

    @staticmethod
    def parse(data:str) -> dict:
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
            
            if key in ['id', 'enter_state_id', 'synonym_group_id']:
                _data[key] = int(value)

            elif key == 'required':
                true_values = ['true', 'True', '1']
                false_values = ['false', 'False', '0']
                if value in true_values:
                    _data[key] = True
                elif value in false_values:
                    _data[key] = False
                else:
                    raise AttributeError(
                        'Плохие данные: required должен быть булевым значением'
                    )
                
            elif key == 'values':
                _data[key] = value.split(',')

            else:
                if value[0] == '"' and value[-1] == '"':
                    _data[key] = value[1:-1]
                else:
                    _data[key] = value

        return _data

    def update(self, **kwargs):
        arg_names = kwargs.keys()

        if 'name' in arg_names:
            if type(kwargs['name']) is not str:
                raise TypeError('"name" должен быть строкой')
            
            if kwargs['name'][0] == '"' and kwargs['name'][-1] == '"':
                value = kwargs['name'][1:-1]
            else:
                value = kwargs['name']

            self.__name = value

        if 'description' in arg_names:
            if type(kwargs['description']) is not str:
                raise TypeError('"description" должен быть строкой')
            
            if kwargs['description'][0] == '"' and kwargs['description'][-1] == '"':
                value = kwargs['description'][1:-1]
            else:
                value = kwargs['description']
            self.__description = value

        if 'required' in arg_names:
            if type(kwargs['required']) is not bool:
                raise TypeError('"required" должен быть булевым')
            self.__required: str = kwargs['required']

        if 'enter' in arg_names:
            if type(kwargs['enter']) is not Command:
                raise TypeError('"enter" должен быть объектом класса Command')
            self.__enter: Command = kwargs['enter']

class Synonyms:
    __id :int
    __name :str
    __description : str
    __values :list[str]
    __commands :list[Command]

    def id(self) -> int:
        return self.__id

    def name(self):
        return str(self.__id) if self.__name is None else self.__name
    
    def values(self) -> list[str]:
        return self.__values.copy()

    def commands(self) -> list[Command]:
        return self.__commands.copy()

    def __init__(self, id: int, **kwargs):
        if type(id) is not int:
            raise TypeError('первый позиционный аргумент "id" должен быть целым числом')
        
        self.__id = id
        self.__name = None
        self.__description = "Описание"
        self.__values = []
        self.__commands = []

        arg_names = kwargs.keys()

        if 'name' in arg_names:
            if not isinstance(kwargs['name'], str):
                raise TypeError('"name" должен быть строкой')
            self.__name = kwargs['name']

        if 'description' in arg_names:
            if not isinstance(kwargs['description'], str):
                raise TypeError('"description" должен быть строкой')
            self.__description = kwargs['description']

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

    def __str__(self):
        if self.__values == []:
            values_str = ''
        else:
            values_str = '"' + '","'.join(self.__values) + '"'

        name = '' if self.__name is None else self.__name
        return '; '.join([
            f'id={self.__id}',
            f'name={name}',
            f'values={values_str}',
            f'description={self.__description}'
        ])

    @staticmethod
    def parse(data:str) -> dict:
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

            if key not in ['id', 'name', 'values', 'description']:
                raise AttributeError(
                    f'Плохие данные: неизвестный ключ "{key}"'
                )
            
            if key == 'id':
                _data[key] = int(value)

            elif key == 'values':
                values = []

                if value != '':
                    val_list = value.split(',')

                    if len(val_list) == 1:
                        quoted = (
                            val_list[1][0] == '"'
                            and
                            val_list[1][-1] == '"'
                        )
                        values = val_list[1][1:-1] if quoted else val_list[1]
                    
                    else:
                        for val in val_list:
                            if len(val) > 1:
                                values.append(val[1:-1])

                _data[key] = values

            else:
                _data[key] = value

        return _data

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

    def set_name(self, new_name:str):
        self.__name = new_name
