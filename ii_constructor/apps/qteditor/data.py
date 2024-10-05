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



from iiconstructor_levenshtain import LevenshtainVector, Synonym, SynonymsGroup
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