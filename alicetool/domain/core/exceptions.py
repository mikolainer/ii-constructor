from typing import Optional, Any

class CoreException(Exception):
    def __init__(self, message, ui_text: Optional[str] = None):            
        super().__init__(message)
        self.ui_text = message if ui_text is None else ui_text

class Exists(CoreException):
    def __init__(self, obj:Any, obj_name:str = 'Объект'):
        self.obj_type = type(obj)
        super().__init__(f'{obj_name} уже существует!')
    
class NotExists(CoreException):
    def __init__(self, obj:Any, obj_name:str = 'Объект'):
        self.obj_type = type(obj)
        super().__init__(f'{obj_name} не существует!')
        