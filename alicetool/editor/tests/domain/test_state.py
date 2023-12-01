from alicetool.editor.domain.states import State

def test_state_constructor():
    '''
    Tests of create with existing id are not required
    it will be processed by StatesRepository
    '''
    DEFAULT_STATE_CONTENT: str = 'text'

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
    data = obj.test_data()
    assert data['id'] == id
    assert data['name'] == id
    assert data['content'] == DEFAULT_STATE_CONTENT
    assert data['steps'] == []

    # user content
    USER_STATE_CONTENT: str = 'content'

    id = 1
    obj = State(id, USER_STATE_CONTENT)
    data = obj.test_data()
    assert data['id'] == id
    assert data['name'] == id
    assert data['content'] == USER_STATE_CONTENT
    assert data['steps'] == []

    # user name
    USER_STATE_NAME: str = 'content'

    id = 2
    obj = State(id, name = USER_STATE_NAME)
    data = obj.test_data()
    assert data['id'] == id
    assert data['name'] == USER_STATE_NAME
    assert data['content'] == DEFAULT_STATE_CONTENT
    assert data['steps'] == []

