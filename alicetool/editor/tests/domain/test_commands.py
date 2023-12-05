import pytest
from alicetool.editor.domain.commands import Command, Synonyms
from alicetool.editor.domain.states import State

def test_synonyms_constructor():
    '''
    Tests of create with existing id are not required
    it will be processed by SynonymsRepository.
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
    
    assert ok, 'something wrong with constructors State, Synonyms, Command'

    # without args
    ok = True
    try:
        obj = Synonyms()
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" and "values" must be required'

    id: int = 1
    commands: list[Command] = [COMMAND]

    # without id
    ok = True
    try:
        obj = Synonyms(values = SYNONYMS_VALUES)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be required'

    # without values
    ok = True
    try:
        obj = Synonyms(id)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"values" must be required'
    
    # empty values
    ok = True
    try:
        obj = Synonyms(id, values = [])
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"values" must contains at least 1 item'

    # default values
    obj = Synonyms(id, values = SYNONYMS_VALUES)
    assert obj.id() is id
    assert obj.name() == SYNONYMS_VALUES[0]
    assert obj.values() is SYNONYMS_VALUES
    assert obj.commands() == []
    id += 1

    # all args
    obj = Synonyms(id, values = SYNONYMS_VALUES, commands = commands, name = SYNONYMS_NAME)
    assert obj.id() is id
    assert obj.name() == SYNONYMS_NAME
    assert obj.values() is SYNONYMS_VALUES
    assert obj.commands() is commands
    id += 1

    # wrong id
    ok = True
    try:
        obj = Synonyms(id = None, values = SYNONYMS_VALUES)
        ok = False # normally unreachable
    except(TypeError):
        pass

    assert ok, '"id" must be an integer'

    # wrong values
    ok = True
    try:
        obj = Synonyms(id, values = None)
        ok = False # normally unreachable
    except(TypeError):
        pass

    assert ok, '"values" must be a list of strings'

def test_command_constructor():
    '''
    Tests of create with existing id are not required
    it will be processed by State
    '''

    ok = False
    try:
        STATE = State(0)
        SYNONYMS_VALUES = ['val 0', 'val 1', 'val 2']
        SYNONYMS = Synonyms(0, values = SYNONYMS_VALUES)
        ok = True
    except(...):
        pass
    
    assert ok, 'something wrong with constructors State, Synonyms'

    # without args
    ok = True
    try:
        obj = Command()
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id", "cmd" and "next_state" must be required'

    # without id
    ok = True
    try:
        obj = Command(next_state = STATE, cmd = SYNONYMS)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be required'

    # without next_state
    ok = True
    try:
        obj = Command(id, next_state = STATE)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"cmd" must be required'

    # without cmd
    ok = True
    try:
        obj = Command(id, cmd = SYNONYMS)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"next_state" must be required'

    # thera are no default values

    # all args
    id: int = 1
    obj = Command(id, next_state = STATE, cmd = SYNONYMS)
    assert obj.id() is id
    assert obj.next_state() is STATE
    assert obj.cmd() is SYNONYMS
    id += 1

    # wrong id
    ok = True
    try:
        obj = Command(None, next_state = STATE, cmd = SYNONYMS)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"id" must be an integer'

    # wrong next_state
    ok = True
    try:
        obj = Command(id, next_state = None, cmd = SYNONYMS)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"next_state" must be a State'

    # wrong cmd
    ok = True
    try:
        obj = Command(id, next_state = STATE, cmd = None)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, '"cmd" must be a Synonyms'
