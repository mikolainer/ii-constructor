import pytest
from alicetool.editor.domain.core import Synonyms, State, Command

def test_synonyms_constructor():
    '''
    не требуется проверять уникальность id созданного объекта
    это будет контроллироваться фабрикой
    '''
    ok = False
    try:
        STATE = State(0)
        SYNONYMS_NAME = 'Synonyms group'
        SYNONYMS_VALUES = ['val 0', 'val 1', 'val 2']
        SYNONYMS = Synonyms(0, values = SYNONYMS_VALUES)
        COMMAND = Command(0, next_state = STATE, cmd = SYNONYMS)
        ok = True
    except(...):
        pass
    
    assert ok, 'что-то не так с конструкторами State, Synonyms или Command'

    id: int = 1
    commands: list[Command] = [COMMAND]

    # без id
    ok = True
    try:
        obj = Synonyms(values = SYNONYMS_VALUES)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'не проверяется передача "id"'

    # без values
    ok = True
    try:
        obj = Synonyms(id)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'не проверяется передача "values"'
    
    # пустые values
    ok = True
    try:
        obj = Synonyms(id, values = [])
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'нет проверки "values" (инициализируется как минимум с 1 значением)'

    # инициализация по умолчанию
    obj = Synonyms(id, values = SYNONYMS_VALUES)
    assert obj.id() is id, 'не тот id'
    assert obj.name() == SYNONYMS_VALUES[0], "если имя не указано - оно должно соответствовать первому значению"
    assert obj.values() == SYNONYMS_VALUES, "значения не те"
    assert obj.commands() == [], "без привязанных переходов должен возврачаться пустой список"
    id += 1

    # пользовательская инициализация
    obj = Synonyms(id, values = SYNONYMS_VALUES, commands = commands, name = SYNONYMS_NAME)
    assert obj.id() is id, 'не тот id'
    assert obj.name() == SYNONYMS_NAME, "не то имя"
    assert obj.values() == SYNONYMS_VALUES, "значения не те"
    assert obj.commands() == commands, "команды не совпадают"
    id += 1

    # некорректный id
    ok = True
    try:
        obj = Synonyms(id = None, values = SYNONYMS_VALUES)
        ok = False # normally unreachable
    except(TypeError):
        pass

    assert ok, 'тип "id" не проверяется'

    # некорректный values
    ok = True
    try:
        obj = Synonyms(id, values = None)
        ok = False # normally unreachable
    except(TypeError):
        pass

    assert ok, 'тип "values" не прроверяется'

def test_command_constructor():
    ok = False
    try:
        STATE = State(0)
        SYNONYMS_VALUES = ['val 0', 'val 1', 'val 2']
        SYNONYMS = Synonyms(0, values = SYNONYMS_VALUES)
        ok = True
    except(...):
        pass
    
    assert ok, 'что-то не так с конструктором State или Synonyms'

    # без cmd
    ok = True
    try:
        obj = Command(next_state = STATE)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'нет проверки - "cmd" обязательный'

    # без next_state
    ok = True
    try:
        obj = Command(cmd = SYNONYMS)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'нет проверки - "next_state" обязательный'

    # все аргументы
    obj = Command(next_state = STATE, cmd = SYNONYMS)
    assert obj.next_state() is STATE
    assert obj.cmd() is SYNONYMS

    # тип next_state
    ok = True
    try:
        obj = Command(next_state = None, cmd = SYNONYMS)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'тип "next_state" не проверяется'

    # тип cmd
    ok = True
    try:
        obj = Command(next_state = STATE, cmd = None)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'тип "cmd" не проверяется'
