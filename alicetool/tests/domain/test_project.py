import pytest
from alicetool.editor.domain.projects import (
    Project,
    ProjectsManager,
    StateMachineInterface,
)

from alicetool.editor.domain.interfaces import(
    StateMachineInterface,
    FlowInterface,
    StateInterface,
    StateMachineInterface,
    ProjectsInterface
)

from alicetool.editor.domain.core import (
    Flow,
    State,
    Command,
)

def test_project_constructor():
    ### проверка аргументов ###

    # без id
    ok = True
    try:
        obj = Project()
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'аргумент "id" должен быть обязательным позиционным'

    # некорректный id
    ok = True
    try:
        obj = Project(None)
        ok = False # normally unreachable
    except(TypeError):
        pass
    
    assert ok, 'нет проверки что "id" - целое число'


    DEFAULT_PROJECT_NAME = 'scenario name'
    DEFAULT_PROJECT_DBNAME = 'db_name'
    DEFAULT_PROJECT_FILEPATH = 'path.proj'
    
    USER_PROJECT_NAME = 'scenario name'
    USER_PROJECT_DBNAME = 'db_name'
    USER_PROJECT_FILEPATH = 'path.proj'
    # инициализация по умолчанию
    id: int = 0
    obj = Project(id)
    assert obj.id() == id, 'не тот id'
    assert obj.name() == DEFAULT_PROJECT_NAME, (
        f'имя по умолчанию не соответствует "{DEFAULT_PROJECT_NAME}"')
    assert obj.db_name() == DEFAULT_PROJECT_DBNAME, (
        f'имя в бд по умолчанию не соответствует "{DEFAULT_PROJECT_DBNAME}"')
    assert obj.file_path() == DEFAULT_PROJECT_FILEPATH, (
        f'путь к файлу умолчанию не соответствует "{DEFAULT_PROJECT_FILEPATH}"')
    
    
    # инициализация с пользовательскими данными
    id = 1
    obj = Project(
        id,
        name = USER_PROJECT_NAME,
        db_name = USER_PROJECT_DBNAME,
        file_path = USER_PROJECT_FILEPATH
    )
    assert obj.id() == id,('не тот id')
    assert obj.name() == USER_PROJECT_NAME, ('не то имя')
    assert obj.db_name() == USER_PROJECT_DBNAME, ('не то имя бд')
    assert obj.file_path() == USER_PROJECT_FILEPATH, ('не тот путь к файлу')
    
def test_project():
    obj = Project(0)
    assert obj.__str__() == 'id=0; name=scenario name; db_name=db_name; file_path=path.proj'

    parse_result = Project.parse('id=0; name="name"; db_name=some name; file_path="qwer.proj"')
    assert parse_result['id'] == 0
    assert parse_result['name'] == 'name'
    assert parse_result['db_name'] == 'some name'
    assert parse_result['file_path'] == 'qwer.proj'

def test_newProject():
    ''' Создание проекта '''
    input = (
            'name=Test123; '
            'db_name=Test123; '
            'file_path=Test123; '
            'hello=Test123; '
            'help=Test123; '
            'info=Test123'
        )

    proj: Project = ProjectsManager().project(
        ProjectsManager.instance().create(input)
    )
    assert proj.name() == 'Test123'
    assert proj.db_name() == 'Test123'
    assert proj.file_path() == 'Test123'
    
    content_i: StateMachineInterface = proj.content_interface()
    
    flow_id_set = content_i.flows()
    assert len(flow_id_set) == 2, 'help, info'
    
    state_id_set = content_i.states()
    assert len(state_id_set) == 3, 'hello_start, help_start, info_start'

    processed_states = set()
    for flow_id in flow_id_set:
        flow :Flow = content_i.get_flow(flow_id)

        assert flow.name() in ['Info', 'Help']

        if flow.name() == 'Info':
            assert flow.is_required() == True
            
            assert flow.enter().cmd().name() == "Info"
            assert flow.call_names() == ['Информация', 'Что ты умеешь']

            state :State = flow.enter().next_state()
            assert state.name() == "Info"
            assert state.content() == 'Test123'

            processed_states.add( state.id() )
        
        elif flow.name() == 'Help':
            assert flow.is_required() == True
            
            assert flow.enter().cmd().name() == "Help"
            assert flow.call_names() == ['Помощь', 'Помоги', 'Справка']

            state :State = flow.enter().next_state()
            assert state.name() == "Help"
            assert state.content() == 'Test123'
            
            processed_states.add( state.id() )

    enter_point_set = state_id_set.difference(processed_states)
    assert len(enter_point_set) == 1
    state :State = content_i.get_state(enter_point_set.pop())
    assert state.name() == 'Enter'
    assert state.content() == 'Test123'
