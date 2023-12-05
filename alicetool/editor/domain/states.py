class State:
    __content = 'text'
    __steps = []

    def __init__(self, id: int, **kwargs):
        if type(id) is not int:
            raise TypeError('first argument "id" must be integer')
        
        self.__id: int = id
        
        if 'name' in kwargs.keys():
            self.__name: str = kwargs['name']
        else:
            self.__name: str = str(self.__id)

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


class ProjectActionsNotifier:
    pass

class StateInterface:
    pass

class StatesRepository:
    pass