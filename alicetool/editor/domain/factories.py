from alicetool.editor.domain.core import *
from alicetool.editor.domain.interfaces import *

class FlowFactory(FlowInterface):
    __items: dict[int, Flow]
    __notifier: FlowActionsNotifier | None

    def __init__(self):
        self.__items = {}
        self.__notifier = None

    def flow_obj(self, id: int) -> Flow:
        if id not in self.__items.keys():
            raise ValueError(f'Flow с id={id} не существует')
        
        return self.__items[id]

    def create_flow(self, data, cmd:Command) -> int:
        ''' создать Flow и вернуть id '''
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

        self.__items[id] = Flow(id, **Flow.parse(data), enter = cmd)
        if self.__notifier is not None:
            self.__notifier.state_created(None, id, data)
        
        return id
    
    def read_flow(self, id: int) -> str:
        ''' получить данные Flow '''
        if id not in self.__items.keys():
            raise ValueError(f'Flow с id={id} не существует')

        return self.__items[id].__str__()

    def update_flow(self, id: int, new_data):
        ''' обновить Flow '''
        if id not in self.__items.keys():
            raise ValueError(f'Flow с id={id} не существует')

        # TODO: реализовать изменение Flow

        if self.__notifier is not None:
            self.__notifier.flow_updated(None, id, new_data)

    def delete_flow(self, id: int):
        ''' удалить Flow '''
        
        if id not in self.__items.keys():
            raise ValueError(f'группа синонимов с id={id} не существует')
        
        del self.__items[id]

        if self.__notifier is not None:
            self.__notifier.flow_removed(0, id)

    def flows(self) -> set[int]:
        ''' вернуть id существующих Folw '''
        return set(self.__items.keys())

    def set_flow_notifier(self, notifier: FlowActionsNotifier):
        ''' установить обработчик коллбэков '''
        if not issubclass(type(notifier), FlowActionsNotifier):
            raise ValueError('notifier должен быть наследником FlowActionsNotifier')

        self.__notifier = notifier

class SynonymsFactory(SynonymsInterface):
    __items: dict[int, Synonyms]
    __notifier: SynonymsActionsNotifier

    def __init__(self):
        self.__items = {}
        self.__notifier = None

    def synonyms_obj(self, id: int) -> Synonyms:
        if id not in self.__items.keys():
            raise ValueError(f'группы синонимов с id={id} не существует')

        return self.__items[id]

    def create_synonyms(self, data) -> int:
        ''' создать и вернуть id '''
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

        self.__items[id] = Synonyms(id, **Synonyms.parse(data))
        if self.__notifier is not None:
            self.__notifier.synonyms_created(None, id, data)
        
        return id
    
    def read_synonyms(self, id: int) -> str:
        ''' получить данные группы синонимов '''
        if id not in self.__items.keys():
            raise ValueError(f'группы синонимов с id={id} не существует')

        return self.__items[id].__str__()

    def update_synonyms(self, id: int, new_data):
        ''' обновить группу синонимов '''
        if id not in self.__items.keys():
            raise ValueError(f'группы синонимов с id={id} не существует')
        
        # TODO: реализовать изменение группу синонимов

        if self.__notifier is not None:
            self.__notifier.synonyms_updated(None, id, new_data)

    def delete_synonyms(self, id: int):
        ''' удалить группу синонимов '''
        
        if id not in self.__items.keys():
            raise ValueError(f'группа синонимов с id={id} не существует')
        
        del self.__items[id]

        if self.__notifier is not None:
            self.__notifier.synonyms_removed(0, id)

    def synonyms(self) -> set[int]:
        ''' вернуть id существующих групп синонимов '''
        return set(self.__items.keys())
    
    def set_synonyms_notifier(self, notifier: SynonymsActionsNotifier):
        ''' установить обработчик коллбэков '''
        if not issubclass(type(notifier), SynonymsActionsNotifier):
            raise ValueError('notifier должен быть наследником SynonymsActionsNotifier')

        self.__notifier = notifier

class StateFactory(StateInterface):
    __items: dict[int, State]
    __notifier: StateActionsNotifier

    def __init__(self):
        self.__items = {}
        self.__notifier = None

    def state_obj(self, id: int) -> State:
        if id not in self.__items.keys():
            raise ValueError(f'состояние с id={id} не существует')

        return self.__items[id]

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
        return set(self.__items.keys())

    def set_state_notifier(self, notifier: StateActionsNotifier):
        ''' сеттер обработчика коллбэков '''
        if not issubclass(type(notifier), StateActionsNotifier):
            raise ValueError('notifier должен быть наследником StateActionsNotifier')

        self.__notifier = notifier