from alicetool.editor.domain.states import State

DEFAULT_STATE_CONTENT: str = 'text'

def test_state_constructor():
    '''
    Tests of create with existing id are not required
    it will be processed by StatesRepository
    '''
    USER_STATE_CONTENT: str = 'content'
    USER_STATE_NAME: str = 'name'


    # without id
    ok = True
    try:
        obj = State()
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be required'


    # default text
    id: int = 0
    obj = State(id)
    assert obj.id() == id
    assert obj.name() == str(id)
    assert obj.content() == DEFAULT_STATE_CONTENT
    assert obj.steps() == []


    # user content
    id = 1
    obj = State(id, USER_STATE_CONTENT)
    data = obj.test_data()
    assert obj.id() == id
    assert obj.name() == str(id)
    assert obj.content() == USER_STATE_CONTENT
    assert obj.steps() == []


    # user name
    id = 2
    obj = State(id, name = USER_STATE_NAME)
    data = obj.test_data()
    assert obj.id() == id
    assert obj.name() == USER_STATE_NAME
    assert obj.content() == DEFAULT_STATE_CONTENT
    assert obj.steps() == []

    # wrong id
    ok = True
    try:
        obj = State(None)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be an integer'
