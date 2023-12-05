from alicetool.editor.domain.flows import BaseFlow, Flow
from alicetool.editor.domain.commands import Synonyms
from alicetool.editor.domain.states import State

DEFAULT_FLOW_NAME = 'Flow name'
DEFAULT_FLOW_DESCRIPTION = 'Flow description'
DEFAULT_FLOW_START_CONTENT = 'text'

USER_FLOW_NAME = 'Some flow'
USER_FLOW_DESCRIPTION = 'Short text'
USER_FLOW_START_CONTENT = 'Hello'

def test_baseflow_constructor():
    '''
    Tests of create with existing id are not required
    it will be processed by Project
    '''

    # without id
    ok = True
    try:
        obj = BaseFlow()
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be required'


    # start state with default content
    id: int = 0
    obj = BaseFlow(id)
    assert obj.id() == id, 'invalid BaseFlow id init'
    assert obj.name() == DEFAULT_FLOW_NAME, (
           f'Default flow name must be "{DEFAULT_FLOW_NAME}"')
    assert obj.description() == DEFAULT_FLOW_DESCRIPTION, (
           f'Default flow description must be "{DEFAULT_FLOW_DESCRIPTION}"')
    assert obj.start() == DEFAULT_FLOW_START_CONTENT, (
           f'Default flow start must be "{DEFAULT_FLOW_START_CONTENT}"')
    assert obj.is_required() is False,('Flow must be not required by default')
    assert obj.is_main() is False, ('Flow must be not main by default')
    
    # start state with user content
    id = 1
    obj = BaseFlow(
        id,
        required = True,
        name = USER_FLOW_NAME,
        description = USER_FLOW_DESCRIPTION,
        start_content = USER_FLOW_START_CONTENT
    )
    assert obj.id() == id,('incorrect id')
    assert obj.name() == USER_FLOW_NAME,('incorrect flow name')
    assert obj.description() == USER_FLOW_DESCRIPTION,(
           'incorrect flow description')
    assert obj.start() == USER_FLOW_START_CONTENT,(
           'incorrect flow start content')
    assert obj.is_required() is True,(
           'Required flow was constructed as not required')
    assert obj.is_main() is False,(
           'Required flow DON\'T MUST be main')

    # start state with user content
    id = 2
    obj = BaseFlow(id, main = True)
    assert obj.is_main(), ('Main flow was constructed as not main')
    assert obj.is_required(), ('Main flow must be required')

    # wrong id
    ok = True
    try:
        obj = BaseFlow(None)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be an integer'



def test_flow_constructor():
    '''
    Tests of create with existing id are not required
    it will be processed by FlowRepository
    '''

    ok = False
    try:
       USER_FLOW_ENTER = Synonyms(0)
       USER_FLOW_BACK_TO = State(0)
       ok = True
    except(...):
       pass
    
    assert ok, 'something wrong with constructors State, Synonyms'

    # without id
    ok = True
    try:
        obj = Flow()
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be required'


    # start state with default content (check init base class)
    id: int = 0
    obj = BaseFlow(id)
    assert obj.id() == id
    assert obj.name() == DEFAULT_FLOW_NAME, (
           f'Default flow name must be "{DEFAULT_FLOW_NAME}"')
    assert obj.description() == DEFAULT_FLOW_DESCRIPTION, (
           f'Default flow description must be "{DEFAULT_FLOW_DESCRIPTION}"')
    assert obj.start() == DEFAULT_FLOW_START_CONTENT, (
           f'Default flow start must be "{DEFAULT_FLOW_START_CONTENT}"')
    assert obj.is_required() is False, (
           'Flow must be not required by default')
    assert obj.is_main() is False, (
           'Flow must be not main by default')
    assert obj.enter() is None, (
        'Flow have no enter by default (enter must be None)')
    assert obj.back_to() is None, (
           'Flow have no \'back_to\' state by default '
           '(\'back_to\' state must be None)')

    # start state with user content
    id = 1
    obj = BaseFlow(
        id,
        required = True,
        name = USER_FLOW_NAME,
        description = USER_FLOW_DESCRIPTION,
        start_content = USER_FLOW_START_CONTENT,
        enter = USER_FLOW_ENTER,
        back_to = USER_FLOW_BACK_TO
    )
    assert obj.id() == id, ('incorrect id')
    assert obj.name() == USER_FLOW_NAME, ( 'incorrect flow name')
    assert obj.description() == USER_FLOW_DESCRIPTION,(
           'incorrect flow description')
    assert obj.start() == USER_FLOW_START_CONTENT,(
           'incorrect flow start content')
    assert obj.is_required() is True,(
           'Required flow was constructed as not required')
    assert obj.is_main() is False,(
           'Required flow DON\'T MUST be main')
    assert obj.enter() is USER_FLOW_ENTER,(
           'Flow have no enter by default (enter must be None)')
    assert obj.back_to() is USER_FLOW_BACK_TO,(
           'Flow have no \'back_to\' state by default '
           '(\'back_to\' state must be None)')
    
    # wrong id
    ok = True
    try:
        obj = Flow(None)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be an integer'
