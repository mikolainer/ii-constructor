# Этот файл — часть "Конструктора интерактивных инструкций".
# 
# Конструктор интерактивных инструкций — свободная программа: 
# вы можете перераспространять ее и/или изменять ее на условиях 
# Стандартной общественной лицензии GNU в том виде, 
# в каком она была опубликована Фондом свободного программного обеспечения;
# либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.
# Конструктор интерактивных инструкций распространяется в надежде,
# что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; 
# даже без неявной гарантии ТОВАРНОГО ВИДА
# или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. 
# Подробнее см. в Стандартной общественной лицензии GNU.
# 
# Вы должны были получить копию Стандартной общественной лицензии GNU
# вместе с этой программой. Если это не так,
# см. <https://www.gnu.org/licenses/>.



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
        