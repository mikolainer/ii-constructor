from dataclasses import dataclass
from typing import Any, Optional, Union

from alicetool.infrastructure.qtgui.data import SynonymsSetModel, ItemData, CustomDataRole
from alicetool.domain.core.primitives import Input, Name, StateID
from alicetool.domain.core.bot import InputDescription, StepVectorBaseClassificator
from alicetool.application.data import BaseSerializer

@dataclass
class Synonym:
    value:str

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

    def __init__(self, name: Name, synonyms: SynonymsGroup) -> None:
        super().__init__(name)
        self.synonyms = synonyms

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
    
#class LevenshtainClassificator(StepVectorBaseClassificator):
#    @staticmethod
#    def get_next_state(cmd: Input, cur_state: StateID) -> State:
#        return super().get_next_state(cmd, cur_state)