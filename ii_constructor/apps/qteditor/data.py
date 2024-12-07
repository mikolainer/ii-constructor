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


from iiconstructor_core.infrastructure.data import BaseSerializer, ItemData
from iiconstructor_levenshtain import LevenshtainVector
from iiconstructor_qtgui.data import CustomDataRole, SynonymsSetModel


class LevenshtainVectorSerializer(BaseSerializer):
    type = LevenshtainVector

    def to_data(self, obj: LevenshtainVector) -> ItemData:
        item = ItemData()
        item.on[CustomDataRole.Name] = obj.name().value

        synonyms = SynonymsSetModel()
        for index in range(len(obj)):
            value = obj.value(index)
            synonym = ItemData()
            synonym.on[CustomDataRole.Text] = value.value()
            synonyms.prepare_item(synonym)
            synonyms.insertRow()
            # synonyms.add_item(synonym)
        item.on[CustomDataRole.SynonymsSet] = synonyms
        item.on[CustomDataRole.Description] = ""

        return item
