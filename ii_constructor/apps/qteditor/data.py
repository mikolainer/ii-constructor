from iiconstructor_levenshtain.inputs import LevenshtainVector, Synonym, SynonymsGroup
from iiconstructor_core.infrastructure.data import BaseSerializer, ItemData
from iiconstructor_core.domain.primitives import Name
from iiconstructor_qtgui.data import SynonymsSetModel, CustomDataRole

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