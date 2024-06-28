from typing import Any

import json
from alicetool.infrastructure.qtgui.data import ItemData, CustomDataRole, SynonymsSetModel

class ItemDataSerializer():
    @staticmethod
    def __role_by_str(string: str) -> CustomDataRole:
        if string == 'Id':
            return CustomDataRole.Id
        elif string == 'Name':
            return CustomDataRole.Name
        elif string == 'Description':
            return CustomDataRole.Description
        elif string == 'Text':
            return CustomDataRole.Text
        elif string == 'SynonymsSet':
            return CustomDataRole.SynonymsSet
        elif string == 'EnterStateId':
            return CustomDataRole.EnterStateId
        elif string == 'SliderVisability':
            return CustomDataRole.SliderVisability
        elif string == 'Node':
            return CustomDataRole.Node
        else:
            return None

    @staticmethod
    def __str_by_role(role: CustomDataRole) -> str:
        if role == CustomDataRole.Id:
            return 'Id'
        elif role == CustomDataRole.Name:
            return 'Name'
        elif role == CustomDataRole.Description:
            return 'Description'
        elif role == CustomDataRole.Text:
            return 'Text'
        elif role == CustomDataRole.SynonymsSet:
            return 'SynonymsSet'
        elif role == CustomDataRole.EnterStateId:
            return 'EnterStateId'
        elif role == CustomDataRole.SliderVisability:
            return 'SliderVisability'
        elif role == CustomDataRole.Node:
            return 'Node'
        else:
            return 'UnknownRole'

    @staticmethod
    def to_string(obj: ItemData) -> str:
        ''' Cериализует данные в json '''
        data = {}

        for role in obj.on.keys():
            if role == CustomDataRole.SynonymsSet:
                model: SynonymsSetModel = obj.on[CustomDataRole.SynonymsSet]
                synonyms = list[str]()
                for row in range(model.rowCount()):
                    synonyms.append(
                        model.data(model.index(row), CustomDataRole.Text)
                    )

                value = synonyms
            else:
                value = obj.on[role]

            data[ItemDataSerializer.__str_by_role(role)] = value

        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def from_str(json_str:str) -> ItemData:
        ''' Десериализует данные из json '''

class BaseSerializer():
    type = Any

    def to_data(self, obj:type) -> ItemData:
        raise NotImplementedError('Использование абстрактного класса')

    def from_data(self, data:ItemData)-> type:
        raise NotImplementedError('Использование абстрактного класса')
    