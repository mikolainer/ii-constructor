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
from iiconstructor_core.domain.primitives import Input, Name


@dataclass
class Synonym:
    value: str

    # FIXME: Декоратор датакласса заменяет этот метод
    def __eq__(self, value: object) -> bool:
        return value.value == self.value


class SynonymsGroup:
    synonyms: list[Synonym]

    def __init__(
        self,
        other: Union["SynonymsGroup", list[Synonym]] | None = None,
    ) -> None:
        if isinstance(other, SynonymsGroup):
            self.synonyms = other.synonyms
        elif isinstance(other, list):
            for synonym in other:
                if not isinstance(synonym, Synonym):
                    raise TypeError(other)
            self.synonyms = other
        else:
            self.synonyms = []


class LevenshtainVector(InputDescription):
    synonyms: SynonymsGroup

    def __init__(self, name: Name, synonyms: SynonymsGroup = None) -> None:
        super().__init__(name)
        self.synonyms = SynonymsGroup() if synonyms is None else synonyms


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
            for synonym in vector.synonyms.synonyms:
                distance = Levenshtein.distance(
                    synonym.value.lower(),
                    cur_input.value.lower(),
                )

                if best is None or distance < best_distance:
                    best_distance = distance
                    best = val
                    continue

        if best_distance >= len(cur_input.value) / 2:
            raise NotExists(cur_input, "Подходящий вектор")

        return best
