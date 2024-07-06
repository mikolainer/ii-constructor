from dataclasses import dataclass
from typing import Any

from alicetool.infrastructure.qtgui.data import SynonymsSetModel, ItemData, CustomDataRole
from alicetool.domain.core.primitives import Input, Name, StateID
from alicetool.domain.core.bot import InputDescription, StepVectorBaseClassificator
from alicetool.application.data import BaseSerializer

@dataclass
class Synonym:
    value:str

class LevenshtainVector(InputDescription):
    synonyms: list[Synonym]

    def __init__(self, name: Name, synonyms: list[Synonym] = []) -> None:
        super().__init__(name)
        self.synonyms = synonyms

class LevenshtainVectorSerializer(BaseSerializer):
    type = LevenshtainVector

    def to_data(self, obj: LevenshtainVector) -> ItemData:
        item = ItemData()
        item.on[CustomDataRole.Name] = obj.name()
        
        synonyms = SynonymsSetModel()
        for value in obj.synonyms:
            synonym = ItemData()
            synonym.on[CustomDataRole.Text] = value.value
            synonyms.prepare_item(synonym)
            synonyms.insertRow()
            #synonyms.add_item(synonym)
        item.on[CustomDataRole.SynonymsSet] = synonyms
        
        return item
    
    def from_data(self, data: ItemData) -> LevenshtainVector:
        name = Name(data.on[CustomDataRole.Name])
        vector = LevenshtainVector(name)

        synonyms_set = list[Synonym]()
        model:SynonymsSetModel = data.on[CustomDataRole.SynonymsSet]
        val_cnt = model.rowCount()
        for index in range(val_cnt):
            synonyms_set.append(Synonym(model.get_item(index).on[CustomDataRole.Text]))

        vector.synonyms = synonyms_set

        return vector
    
#class LevenshtainClassificator(StepVectorBaseClassificator):
#    @staticmethod
#    def get_next_state(cmd: Input, cur_state: StateID) -> State:
#        return super().get_next_state(cmd, cur_state)