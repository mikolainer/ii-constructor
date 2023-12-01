from alicetool.editor.domain.flows import BaseFlow, Flow

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

    # TODO: start state with default content
    
    # TODO: start state with user content


def test_flow_constructor():
    '''
    Tests of create with existing id are not required
    it will be processed by FlowRepository
    '''

    # without id
    ok = True
    try:
        obj = Flow()
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be required'