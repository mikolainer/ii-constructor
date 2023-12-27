from alicetool.editor.domain.core import Flow, Synonyms, State

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
    assert obj.enter().next_state().content() == DEFAULT_FLOW_START_CONTENT, (
        f'начальный текст по умолчанию не соответствует "{DEFAULT_FLOW_START_CONTENT}"')
    
    # инициализация с пользовательскими данными
    id = 1
    obj = Flow(
        id,
        required = True,
        name = USER_FLOW_NAME,
        description = USER_FLOW_DESCRIPTION,
        start_content = USER_FLOW_START_CONTENT
    )
    assert obj.id() == id,('не тот id')
    assert obj.name() == USER_FLOW_NAME,('не то имя')
    assert obj.description() == USER_FLOW_DESCRIPTION,(
        'не то описание')
    assert obj.is_required() is True,(
        'обязательный создался не обязательным')
    assert obj.enter().next_state().content() == USER_FLOW_START_CONTENT,(
        'не тот начальный текст')
    