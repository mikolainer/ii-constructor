# Copyright 2024 Николай Иванцов (tg/vk/wa: <@mikolainer> | <mikolainer@mail.ru>)
# Copyright 2024 Kirill Lesovoy
#
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


from iiconstructor_core.domain import Connection, State, Step
from iiconstructor_core.domain.primitives import (
    Input,
    Request,
    Response,
    StateID,
)
from iiconstructor_server_side.ports import ScenarioInterface


class StepVectorBaseClassificator:
    __project: ScenarioInterface

    def __init__(self, project: ScenarioInterface) -> None:
        self.__project = project

    def calc(
        self,
        cur_input: Input,
        possible_inputs: dict[str, State],
    ) -> State | None:
        """Вычисления"""
        raise NotImplementedError

    def __prepare_to_step_detect(
        self,
        cur_state_id: StateID,
    ) -> dict[str, State]:
        inputs = dict[str, State]()
        for step in self.__project.steps(cur_state_id):
            step: Step = step

            cur_state = step.connection.from_state
            if cur_state is None or cur_state.id() != cur_state_id:
                continue

            inputs[step.input.name().value] = step.connection.to_state

        return inputs

    def __prepare_to_enter_detect(self) -> dict[str, State]:
        inputs = dict[str, State]()

        for conn in (
            self.__project.source().get_all_connections()["to"].values()
        ):
            conn: Connection = conn
            to: State = conn.to_state

            for step in conn.steps:
                inputs[step.input.name().value] = to

        return inputs

    def get_next_state(self, cmd: Input, cur_state_id: StateID) -> State:
        cur_state = self.__project.states([cur_state_id])[cur_state_id]

        callable_list = [
            lambda: self.__prepare_to_step_detect(cur_state_id),
            lambda: self.__prepare_to_enter_detect(),
        ]

        for get_inputs in callable_list:
            inputs = get_inputs()
            try:
                return self.calc(cmd, inputs)
            except Exception:
                result = cur_state

        return result


class Engine:
    __classif: StepVectorBaseClassificator
    __cur_state: State

    def __init__(
        self,
        classif: StepVectorBaseClassificator,
        start_state: State,
    ) -> None:
        self.__classif = classif
        self.__cur_state = start_state

    def handle(self, request: Request) -> Response:
        req = request.text
        prev_state = self.__cur_state.id()

        self.__cur_state = self.__classif.get_next_state(
            Input(req),
            self.__cur_state.id(),
        )

        result = Response()

        if prev_state == self.__cur_state.id():
            result.text = "Запрос не понятен"
        else:
            result.text = self.__cur_state.attributes.output.value.text

        return result

    def set_current_state(self, state: State):
        self.__cur_state = state

    def current_state(self) -> State:
        return self.__cur_state
