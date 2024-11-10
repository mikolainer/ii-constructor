from iiconstructor_core.domain import (
    Source,
    State,
    Step,
    InputDescription,
    Connection,
)
from iiconstructor_core.domain.primitives import (
    Name,
    Output,
    StateAttributes,
    StateID,
)
from iiconstructor_qtgui.primitives.sceneitems import (
    Arrow,
)

from iiconstructor_qtgui.flows import FlowsModel
from iiconstructor_qtgui.states import StatesModel
from iiconstructor_qtgui.steps import StepModel
from iiconstructor_qtgui.synonyms import SynonymsGroupsModel

class Cache(Source):
    __flows_model: FlowsModel
    __states_model: StatesModel
    __vectors_model: SynonymsGroupsModel
    __arrows: dict[Arrow, StepModel]

    def __init__(self, origin: Source):
        self.id = origin.id
        self.info = origin.info

        self.__flows_model = FlowsModel()
        self.__states_model = StatesModel()
        self.__vectors_model = SynonymsGroupsModel()
        self.__arrows = dict[Arrow, StepModel]()

    def get_layouts(self) -> str:
        """получить данные отображения"""

    def save_lay(self, id: StateID, x: float, y: float):
        """сохранить положение состояния"""

    def delete_state(self, state_id: StateID):
        """удалить состояние"""

    def get_states_by_name(self, name: Name) -> list[State]:
        """получить все состояния с данным именем"""

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        """получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния"""

    def steps(self, state_id: StateID) -> list[Step]:
        """получить все переходы, связанные с состоянием по его идентификатору"""

    def is_enter(self, state: State) -> bool:
        """Проверить является ли состояние входом"""

    # сеттеры

    def set_answer(self, state_id: StateID, data: Output):
        """Изменить ответ состояния"""

    # векторы

    def select_vectors(
        self,
        names: list[Name] | None = None,
    ) -> list["InputDescription"]:
        """
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        """

    def get_vector(self, name: Name) -> InputDescription:
        """
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        """

    def add_vector(self, input: InputDescription):
        """
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        """

    def remove_vector(self, name: Name):
        """
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        """

    def check_vector_exists(self, name: Name) -> bool:
        """
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        """

    # Scenario private
    def create_state(
        self,
        attributes: StateAttributes,
        required: bool = False,
    ) -> State:
        """Создать состояние"""

    def find_connections_to(self, state_id: StateID) -> list[Connection]:
        """Получить входящие связи"""

    def input_usage(self, input: InputDescription) -> list[Connection]:
        """Получить связи, в которых используется вектор"""

    def new_step(
        self,
        from_state: StateID | None,
        to_state: StateID,
        input_name: Name,
    ) -> Step:
        """создаёт переходы и связи"""

    def delete_step(
        self,
        from_state: StateID | None,
        to_state: StateID | None,
        input_name: Name | None = None,
    ):
        """удаляет переходы и связи"""

    def get_all_connections(self) -> dict[str, dict]:
        """
        !!! DEPRECATED !!!\n
        получить все связи\n
        ключи: 'from', 'to'; значения: to=dict[StateID, Connection], from=dict[StateID, list[Connection]]
        """
        # TODO: оптимизировать API. (фактически в память выгружается вся база)

    def set_synonym_value(
        self,
        input_name: str,
        old_synonym: str,
        new_synonym: str,
    ):
        """изменяет значение синонима"""

    def create_synonym(self, input_name: str, new_synonym: str):
        """создаёт синоним"""

    def remove_synonym(self, input_name: str, synonym: str):
        """удаляет синоним"""

    def rename_state(self, state: StateID, name: Name):
        """Переименовывает состояние"""

    def rename_vector(self, old_name: Name, new_name: Name):
        """переименовывает группу синонимов"""