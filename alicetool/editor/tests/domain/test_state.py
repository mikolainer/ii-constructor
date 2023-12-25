from alicetool.editor.domain.core import State, StateFactory

DEFAULT_STATE_CONTENT: str = State._State__content # hack for tests

def test_state_constructor():
    '''
    не требуется проверять уникальность id созданного объекта
    это будет контроллироваться фабрикой
    '''
    USER_STATE_CONTENT: str = 'content'
    USER_STATE_NAME: str = 'name'


    # без id
    ok = True
    try:
        obj = State()
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" должен быть обязательным позиционным'

    # некорректный id
    ok = True
    try:
        obj = State(None)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'не проверяется тип "id"'

    # инициализация по умолчанию
    id: int = 0
    obj = State(id)
    assert obj.id() == id, 'не тот id'
    assert obj.name() == str(id), 'если имя не указано оно должно совпадать с id'
    assert obj.content() == DEFAULT_STATE_CONTENT, f'текст по умолчанию должен быть "{DEFAULT_STATE_CONTENT}"'
    assert obj.steps() == [], 'состояние без переходов должно содержать пустой список переходов'


    # пользовательская инициализация
    id = 1
    obj = State(id, content = USER_STATE_CONTENT, name = USER_STATE_NAME)
    assert obj.id() == id, 'не тот id'
    assert obj.name() == USER_STATE_NAME, 'не то имя'
    assert obj.content() == USER_STATE_CONTENT, 'не тот контент'
    assert obj.steps() == []

def test_state():
    state = State(0)
    assert len(state.steps()) == 0, 'состояние по умолчанию должно быть без переходов'
    assert state.__str__() == 'id=0; name=0; steps=; content=text'

    parse_result = State.parse('id=0; name=0; steps=; content=text')
    assert parse_result['id'] == 0
    assert parse_result['name'] == '0'
    assert parse_result['content'] == 'text'
    assert parse_result['steps'] == []
    

def test_state_factory():
    repo = StateFactory()
    assert len(repo.states()) == 0, 'фабрика конструируется не пустой'
    
    id = repo.create_state('')
    assert id == 1
    assert len(repo.states()) == 1, 'фабрика не создала первый объект'
    assert repo.read_state(id) == 'id=1; name=1; steps=; content=text'

    id = repo.create_state('name=kek; content=lol')
    assert id == 2
    assert len(repo.states()) == 2, 'фабрика не создала второй объект'
    assert repo.read_state(id) == 'id=2; name=kek; steps=; content=lol'
    assert repo.states() == {1, 2}

    repo.delete_state(1)
    assert repo.states() == {2}, 'фабрика не удалила объект'

    id = repo.create_state('')
    assert id == 1
    assert repo.states() == {1, 2}, 'фабрика не создала пропущенный объект'

    ok = True
    try:
        repo.delete_state(10)
        ok = False # normally unreachable
    except(ValueError):
        pass
    assert ok, 'нет проверки существования состояния с полученным id при удалении'

    try:
        repo.read_state(10)
        ok = False # normally unreachable
    except(ValueError):
        pass
    assert ok, 'нет проверки существования состояния с полученным id при чтении'