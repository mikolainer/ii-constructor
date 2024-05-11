from alicetool.editor.domain.core import *
from alicetool.editor.domain.factories import FlowFactory

DEFAULT_FLOW_NAME = 'Flow name'
DEFAULT_FLOW_DESCRIPTION = 'Flow description'
DEFAULT_FLOW_START_CONTENT = 'text'

USER_FLOW_NAME :str = 'Some flow'
USER_FLOW_DESCRIPTION :str = 'Short text'
USER_FLOW_START_CONTENT :str = 'Hello'

def test_flow_constructor():
    '''
    не требуется проверять уникальность id созданного проекта
    это будет контроллироваться менеджером проектов
    '''

    ### проверка аргументов ###

    # без id
    ok = True
    try:
        obj = Flow()
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'аргумент "id" должен быть обязательным позиционным'

    # некорректный id
    ok = True
    try:
        obj = Flow(None)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'нет проверки что "id" - целое число'

    # инициализация по умолчанию
    id: int = 0
    obj = Flow(id)
    assert obj.id() == id, 'не тот id'
    assert obj.name() == DEFAULT_FLOW_NAME, (
        f'имя по умолчанию не соответствует "{DEFAULT_FLOW_NAME}"')
    assert obj.description() == DEFAULT_FLOW_DESCRIPTION, (
        f'описание по умолчанию не соответствует "{DEFAULT_FLOW_DESCRIPTION}"')
    assert obj.is_required() is False, (
        'по умолчанию должен быть не обязательным')
    
    # инициализация с пользовательскими данными
    id = 1
    obj = Flow(
        id,
        required = True,
        name = USER_FLOW_NAME,
        description = USER_FLOW_DESCRIPTION
    )
    assert obj.id() == id,('не тот id')
    assert obj.name() == USER_FLOW_NAME,('не то имя')
    assert obj.description() == USER_FLOW_DESCRIPTION,(
        'не то описание')
    assert obj.is_required() is True,(
        'обязательный создался не обязательным')
    
def test_flow():
    state = Flow(0)
    assert state.__str__() == 'id=0; required=false; name="Flow name"; description="Flow description"'

    parse_result = Flow.parse('id=0; required=true; name="name"; description="azaza"')
    assert parse_result['id'] == 0
    assert parse_result['name'] == 'name'
    assert parse_result['description'] == 'azaza'
    assert parse_result['required'] == True

def test_flow_factory():
    repo = FlowFactory()
    assert len(repo.flows()) == 0, 'фабрика конструируется не пустой'
    
    id = repo.create_flow('', cmd = Command(State(0), Synonyms(0)))
    assert id == 1
    assert len(repo.flows()) == 1, 'фабрика не создала первый объект'
    assert repo.read_flow(id) == 'id=1; required=false; name="Flow name"; description="Flow description"'

    id = repo.create_flow('name="kek"; required=true; description="lol"', cmd = Command(State(0), Synonyms(0)))
    assert id == 2
    assert len(repo.flows()) == 2, 'фабрика не создала второй объект'
    assert repo.read_flow(id) == 'id=2; required=true; name="kek"; description="lol"'
    assert repo.flows() == {1, 2}

    repo.delete_flow(1)
    assert repo.flows() == {2}, 'фабрика не удалила объект'

    id = repo.create_flow('', cmd = Command(State(0), Synonyms(0)))
    assert id == 1
    assert repo.flows() == {1, 2}, 'фабрика не создала пропущенный объект'

    ok = True
    try:
        repo.delete_flow(10)
        ok = False # normally unreachable
    except(ValueError):
        pass
    assert ok, 'нет проверки существования Flow с полученным id при удалении'

    try:
        repo.read_flow(10)
        ok = False # normally unreachable
    except(ValueError):
        pass
    assert ok, 'нет проверки существования Flow с полученным id при чтении'