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


from dataclasses import dataclass
from typing import Optional, Union

import Levenshtein
from iiconstructor_core.domain import (
    InputDescription,
    State,
    StepVectorBaseClassificator,
)
from iiconstructor_core.domain.exceptions import NotExists
from iiconstructor_core.domain.porst import ScenarioInterface
from iiconstructor_core.domain.primitives import Input, StrInput, Name


class Synonym(StrInput):

    def __eq__(self, value: object) -> bool:
        return value.__value == self.__value


class LevenshtainVector(InputDescription):

    def __init__(self, name: Name, synonyms: list[Synonym] | Synonym | None = None) -> None:
        super().__init__(name, synonyms)


class LevenshtainClassificator(StepVectorBaseClassificator):
    def __init__(self, project: ScenarioInterface) -> None:
        super().__init__(project)

    def calc(
        self,
        cur_input: Input,
        possible_inputs: dict[str, State],
    ) -> State | None:
        best_score = 0
        best: State | None = None

        for key, val in possible_inputs.items():
            vector = self._StepVectorBaseClassificator__project.get_vector(
                Name(key),
            )
            if not isinstance(vector, LevenshtainVector):
                continue

            best_distance: int
            for index in range(len(vector)):
                synonym = vector.value(index)
                distance = Levenshtein.distance(
                    synonym.value.lower(),
                    cur_input.value().lower(),
                )

                if best is None or distance < best_distance:
                    best_distance = distance
                    best = val
                    continue

        if best_distance >= len(cur_input.value()) / 2:
            raise NotExists(cur_input, "Подходящий вектор")

        return best
