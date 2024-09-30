from typing import Any

class ItemData:
    ''' Обёртка над данными с использованием ролей '''
    on: dict[int, Any] # role, data
    def __init__(self) -> None:
        self.on = {}

class BaseSerializer():
    type = Any

    def to_data(self, obj:type) -> ItemData:
        raise NotImplementedError('Использование абстрактного класса')

    def from_data(self, data:ItemData)-> type:
        raise NotImplementedError('Использование абстрактного класса')