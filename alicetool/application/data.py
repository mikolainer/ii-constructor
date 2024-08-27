from typing import Any

import json
from alicetool.infrastructure.qtgui.data import ItemData
class BaseSerializer():
    type = Any

    def to_data(self, obj:type) -> ItemData:
        raise NotImplementedError('Использование абстрактного класса')

    def from_data(self, data:ItemData)-> type:
        raise NotImplementedError('Использование абстрактного класса')
    