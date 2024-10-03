import os

from iiconstructor_core.domain import Engine, State
from iiconstructor_core.domain.primitives import Request, Response, Name, ScenarioID, StateID
from iiconstructor_levenshtain import LevenshtainClassificator
from mysqlrepo import HostingMySQL

ip = os.environ.get('IP')
port = int(os.environ.get('PORT'))
username = os.environ.get('USER')
password = os.environ.get('PASSWORD')
scenario_id = int(os.environ.get('SCENARIO_ID'))

hosting = HostingMySQL()
hosting.connect(ip, port, username, password)
scenario = hosting.get_scenario(ScenarioID(scenario_id))
start_state: State = scenario.get_states_by_name(Name("Старт"))[0]
engine = Engine(LevenshtainClassificator(scenario), start_state)

def handler(event, context):
    session_store = event['state']['session']

    resp = Response()

    cur_state: State
    if event['session']['new']:
        cur_state = scenario.get_states_by_name(Name("Старт"))[0]
        resp.text = cur_state.attributes.name.value

        session_store = {
            'state' : cur_state.id().value
        }

    else:
        cur_state = scenario.states(StateID(event['state']['session']['state']))
        engine.set_current_state(cur_state)

        req = Request()
        req.text = event['request']['command']
        resp = engine.handle(req)
        session_store['state'] = engine.current_state().id()

    return{
            'version': event['version'],
            'session': event['session'],
            'session_state': session_store,
            'response': {
                'text': resp.text,
                'end_session': False
            }
        }
