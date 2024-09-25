from dataclasses import dataclass
from typing import Any, Optional, Union

from alicetool.infrastructure.qtgui.data import SynonymsSetModel, ItemData, CustomDataRole
from alicetool.domain.core.primitives import Input, Name, StateID
from alicetool.domain.core.bot import InputDescription, StepVectorBaseClassificator, State, Step
from alicetool.application.data import BaseSerializer
from alicetool.domain.core.porst import ScenarioInterface
from alicetool.domain.core.exceptions import NotExists
import Levenshtein

@dataclass
class Synonym:
    value:str

    def __eq__(self, value: object) -> bool:
        return value.value == self.value

class SynonymsGroup:
    synonyms: list[Synonym]
    
    def __init__(self, other:Optional[Union['SynonymsGroup' , list[Synonym]]] = None):
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

class LevenshtainVectorSerializer(BaseSerializer):
    type = LevenshtainVector

    def to_data(self, obj: LevenshtainVector) -> ItemData:
        item = ItemData()
        item.on[CustomDataRole.Name] = obj.name().value
        
        synonyms = SynonymsSetModel()
        for value in obj.synonyms.synonyms:
            synonym = ItemData()
            synonym.on[CustomDataRole.Text] = value.value
            synonyms.prepare_item(synonym)
            synonyms.insertRow()
            #synonyms.add_item(synonym)
        item.on[CustomDataRole.SynonymsSet] = synonyms
        item.on[CustomDataRole.Description] = ''
        
        return item
    
    def from_data(self, data: ItemData) -> LevenshtainVector:
        name = Name(data.on[CustomDataRole.Name])
        vector = LevenshtainVector(name, SynonymsGroup())

        synonyms_set = list[Synonym]()
        model:SynonymsSetModel = data.on[CustomDataRole.SynonymsSet]
        val_cnt = model.rowCount()
        for index in range(val_cnt):
            synonyms_set.append(Synonym(model.get_item(index).on[CustomDataRole.Text]))

        vector.synonyms.synonyms = synonyms_set

        return vector
    
class LevenshtainClassificator(StepVectorBaseClassificator):
    def __init__(self, project: ScenarioInterface) -> None:
        super().__init__(project)

    @staticmethod
    def calc(cur_input: Input, possible_inputs: dict[InputDescription, State]) -> Optional[State]:
        best_score = 0
        best: State = None

        for key, val in possible_inputs.items():
            if not isinstance(key, LevenshtainVector):
                continue
            
            best_distance: int
            for synonym in key.synonyms.synonyms:
                distance = Levenshtein.distance(synonym.value.lower(), cur_input.value.lower())

                if best is None or distance < best_distance:
                    best_distance = distance
                    best = val
                    continue

        if best_distance >= len(cur_input.value) / 2:
            raise NotExists(cur_input, "Подходящий вектор")

        return best
