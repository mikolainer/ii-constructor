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
    State,
    OutputDescription,
    AnswerValue,
)

from .plaintext import (
    PlainTextAnswer,
    PlainTextDescription,
)

class OutputsLibAPI():
    """Интерфейс к библиотеке ответов для прикладного уровня"""
    __lib: OutputLib

    def __init__(self, lib: OutputLib):
        self.__lib = lib

    def type(self) -> str:
        return self.__lib.attributes().items_type

    def create_default_for(self, state_id:int):
        """Создать привязку выходного значения по умолчанию к состоянию"""
        self.__lib.create(State(state_id), self.__lib.make_default_output())

    def read(self, state_id:int) -> list[list[str]]:
        """Получить описание всех выходов состояния"""
        result = list[list[str]]()

        for output_descr in self.__lib.read(State(state_id)):
            output_descr: OutputDescription = output_descr

            out_values = list[str]()
            for index in range(len(output_descr)):
                val: AnswerValue = output_descr.value(index)
                out_values.append(val.as_text())

            result.append(out_values)

        return result

    def update(self, state_id:int, old_data:str, new_data:str):
        """Заменить одно значение другим"""
        state = State(state_id)
        old_value: OutputDescription = self.__lib.parse(old_data)
        new_value: OutputDescription = self.__lib.parse(new_data)
        self.__lib.delete(state, old_value)
        self.__lib.create(state, new_value)

    def delete(self, state_id:int):
        """Удалить ответы состояния"""
        state = State(state_id)

        for value in self.__lib.read(state):
            value: OutputDescription = value
            self.__lib.delete(state, value)

