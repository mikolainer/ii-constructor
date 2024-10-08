# Этот файл — часть "Конструктора интерактивных инструкций".
#
# Конструктор интерактивных инструкций — свободная программа:
# вы можете перераспространять ее и/или изменять ее на условиях
# Стандартной общественной лицензии GNU в том виде,
# в каком она была опубликована Фондом свободного программного обеспечения;
# либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.
# Конструктор интерактивных инструкций распространяется в надежде,
# что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ;
# даже без неявной гарантии ТОВАРНОГО ВИДА
# или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ.
# Подробнее см. в Стандартной общественной лицензии GNU.
#
# Вы должны были получить копию Стандартной общественной лицензии GNU
# вместе с этой программой. Если это не так,
# см. <https://www.gnu.org/licenses/>.



from iiconstructor_core.domain import Engine, State
import os
from iiconstructor_core.domain.primitives import (
    Name,
    Request,
    Response,
    ScenarioID,
    StateID,
)
from iiconstructor_levenshtain import LevenshtainClassificator
from mysqlrepo import HostingMySQL

ip = os.environ.get("IP")
port = int(os.environ.get("PORT"))
username = os.environ.get("USER")
password = os.environ.get("PASSWORD")
scenario_id = int(os.environ.get("SCENARIO_ID"))

hosting = HostingMySQL()
hosting.connect(ip, port, username, password)
scenario = hosting.get_scenario(ScenarioID(scenario_id))
start_state: State = scenario.get_states_by_name(Name("Старт"))[0]
engine = Engine(LevenshtainClassificator(scenario), start_state)


def handler(event, context):
    if (
        "request" in event
        and "original_utterance" in event["request"]
        and event["request"]["original_utterance"] != ""
        and event["request"]["original_utterance"] == "ping"
    ):
        return {
            "version": 1,
            "session": 1,
            "response": {"text": "pong", "end_session": True},
        }

    session_store = event["state"]["session"]

    resp = Response()

    cur_state: State
    if event["session"]["new"]:
        cur_state = scenario.get_states_by_name(Name("Старт"))[0]
        resp.text = cur_state.attributes.name.value

        session_store = {"state": cur_state.id().value}

    else:
        cur_state_id = StateID(event["state"]["session"]["state"])
        cur_state = scenario.states([cur_state_id])[cur_state_id]
        engine.set_current_state(cur_state)

        req = Request()
        req.text = event["request"]["command"]
        resp = engine.handle(req)
        session_store["state"] = engine.current_state().id().value

    return {
        "version": event["version"],
        "session": event["session"],
        "session_state": session_store,
        "response": {"text": resp.text, "end_session": False},
    }
