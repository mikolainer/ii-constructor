import pytest
from alicetool.editor.domain.core import Synonyms, State, Command
from alicetool.editor.domain.factories import SynonymsFactory

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
        COMMAND = Command(next_state = STATE, cmd = SYNONYMS)
        ok = True
    except Exception as err:
        raise err
    
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

    # инициализация по умолчанию
    obj = Synonyms(id)
    assert obj.id() is id, 'не тот id'
    assert obj.name() == str(obj.id()), "если имя не указано - оно должно соответствовать id"
    assert obj.values() == [], "значения не те"
    assert obj.commands() == [], "без привязанных переходов должен возвращаться пустой список"
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

def test_synonyms():
    obj = Synonyms(0)
    assert len(obj.values()) == 0, 'состояние по умолчанию должно быть без переходов'
    assert obj.__str__() == 'id=0; name=; values='

    parse_result = Synonyms.parse('id=0; name=name; values="kek","lol"')
    assert parse_result['id'] == 0
    assert parse_result['name'] == 'name'
    assert parse_result['values'] == ['kek', 'lol']

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


def test_synonyms_factory():
    repo = SynonymsFactory()
    assert len(repo.synonyms()) == 0, 'фабрика конструируется не пустой'
    
    id = repo.create_synonyms('')
    assert id == 1
    assert len(repo.synonyms()) == 1, 'фабрика не создала первый объект'
    assert repo.read_synonyms(id) == 'id=1; name=; values='

    id = repo.create_synonyms('name=kek; values="azaza","pupupu"')
    assert id == 2
    assert len(repo.synonyms()) == 2, 'фабрика не создала второй объект'
    assert repo.read_synonyms(id) == 'id=2; name=kek; values="azaza","pupupu"'
    assert repo.synonyms() == {1, 2}

    repo.delete_synonyms(1)
    assert repo.synonyms() == {2}, 'фабрика не удалила объект'

    id = repo.create_synonyms('')
    assert id == 1
    assert repo.synonyms() == {1, 2}, 'фабрика не создала пропущенный объект'

    ok = True
    try:
        repo.delete_synonyms(10)
        ok = False # normally unreachable
    except(ValueError):
        pass
    assert ok, 'нет проверки существования группы синонимов с полученным id при удалении'

    try:
        repo.read_synonyms(10)
        ok = False # normally unreachable
    except(ValueError):
        pass
    assert ok, 'нет проверки существования группы синонимов с полученным id при чтении'
