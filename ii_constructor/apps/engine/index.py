import os

from iiconstructor_core.domain import Engine, State
from iiconstructor_core.domain.primitives import Request, Response, Name, ScenarioID
from iiconstructor_levenshtain import LevenshtainClassificator
from iiconstructor_mysqlrepo import HostingMySQL

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