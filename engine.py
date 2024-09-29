import os

from ii_constructor.presentation.editor.gui import Engine, Request, Response
from ii_constructor.domain.core.primitives import Name
from ii_constructor.domain.core.bot import State
from ii_constructor.infrastructure.repositories.mysqlrepo import HostingMySQL
from ii_constructor.application.editor import HostingManipulator

hosting = HostingMySQL()
ip = os.environ.get('IP')
port = os.environ.get('PORT')
username = os.environ.get('USER')
password = os.environ.get('PASSWORD')
hosting.connect(ip, port, username, password)
manipulator = HostingManipulator.open_scenario_from_db(hosting, 12)
start_state: State = manipulator.interface().get_states_by_name(Name("Старт"))[0]
engine = Engine(manipulator.interface(), start_state)

def handler(event, context):
    session_store = event['state']['session']

    req = Request()
    req.text = event['request']['command']
    resp = engine.handle(req)

    return{
            'version': event['version'],
            'session': event['session'],
            'session_state': session_store,
            'response': {
                'text': resp.text,
                'end_session': False
            }
        }