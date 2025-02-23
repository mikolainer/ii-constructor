# Copyright 2024 Николай Иванцов (tg/vk/wa: <@mikolainer> | <mikolainer@mail.ru>)
# Copyright 2024 Kirill Lesovoy
#
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

from .domain import (
    OutputLib,
    OutputID,
    OutputDescription,
    Output,
)

class OutputSpec_DTO:
    @staticmethod
    def as_dict(obj: IsOutputSpec) -> dict:
        pass
    
    def as_text(self) -> str:
        pass
    
    def as_value(self) -> IsOutputSpec:
        pass

class Output_DTO:
    @staticmethod
    def as_dict(obj: Output) -> dict:
        pass
    
    def as_text(self) -> str:
        pass
    
    def as_value(self) -> OutputDescription:
        pass
    

class OutputsLibAPI():
    """Интерфейс к библиотеке ответов для прикладного уровня"""
    __lib: OutputLib

    def __init__(self, lib: OutputLib):
        self.__lib = lib

    def type(self) -> str:
        return self.__lib.attributes().items_type

    def read(self, id:int) -> list[str]:
        """Получить описание всех выходов состояния"""
        result = list[str]()

        for output_descr in self.__lib.read(OutputID(id)):
            output_descr: OutputDescription = output_descr
            result.append(output_descr.as_text())

        return result

    def update(self, id:int, old_data:str, new_data:str):
        """Заменить одно значение другим"""
        _id = OutputID(id)
        old_value = OutputDescription(old_data)
        new_value = OutputDescription(new_data)
        self.__lib.delete(_id, old_value)
        self.__lib.create(new_value, _id)

    def delete(self, id:int):
        """Удалить ответы состояния"""
        _id = OutputID(id)

        for value in self.__lib.read(_id):
            value: OutputDescription = value
            self.__lib.delete(_id, value)

