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

class AnswerValue:
    def as_text(self) -> str:
        """Строковое представление"""

class PlainTextAnswer(AnswerValue):
    """Базовый класс описания ответа"""

    __text: str
    __MIN_LEN: int = 1
    __MAX_LEN: int = 1024

    def __init__(self, text:str):
        self.__text = text

    def as_text(self) -> str:
        return self.__text

    def is_valid(self) -> bool:
        _len: int = len(self.text)
        return self.__MIN_LEN < _len < self.__MAX_LEN



class OutputDescription:
    """Описание ответа - аттрибут состояния"""
    __values: list[AnswerValue]

    # нет сеттеров. только создание целиком.
    def __init__(self, answer: list[AnswerValue] | AnswerValue | None = None):
        if answer is None:
            self.__values = [PlainTextAnswer("")]
        elif isinstance(answer, list):
            if len(answer) == 0:
                self.__values = [""]
            else:
                self.__values = answer
        else:
            self.__values = [answer]

    def value(self, index:int = 0) -> AnswerValue:
        return self.__values[index]

    def __len__(self) -> int:
        return len(self.__values)