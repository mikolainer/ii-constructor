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


from __future__ import annotations

from .primitives import Name, OutputDescription, StateAttributes, StateID


class ScenarioInterface:
    def get_layouts(self) -> str:
        """получить строку данные отобрадения"""

    def save_lay(self, id: StateID, x: float, y: float):
        """сохраняет положение состояни"""

    def create_enter_state(
        self,
        input: InputDescription,
        required: bool = False,
    ):
        """добавляет вектор и новое состояние-вход с таким-же именем"""

    def create_enter_vector(self, input: InputDescription, state_id: StateID):
        """Делает состояние точкой входа. Создаёт вектор с соответствующим состоянию именем"""

    def make_enter(self, state_id: StateID):
        """привязывает к состоянию существующий вектор с соответствующим именем как команду входа"""

    def create_step_between(
        self,
        from_state_id: StateID,
        to_state: StateID,
        input: InputDescription,
    ) -> Step:
        """
        Создаёт переход из from_state в to_state по переходу input
        @from_state_id: id состояния для обработки управляющего воздействия input
        @to_state: id состояния в которое будет добавлен переход
        @input: управляющее воздействие
        """

    def create_step_to_new(
        self,
        from_state_id: StateID,
        to_state: StateAttributes,
        output: OutputDescription,
        input: InputDescription,
    ) -> Step:
        """
        Создаёт переход из from_state в to_state по переходу input
        @from_state_id: id состояния для обработки управляющего воздействия input
        @to_state: аттрибуты для создания нового состояния
        @output: ответ нового состояния
        @input: управляющее воздействие
        """

    # удаление сущностей

    def remove_state(self, state_id: StateID):
        """удаляет состояние"""

    def remove_enter(self, state_id: StateID):
        """удаляет связь с командой входа в состояние"""

    def remove_step(self, from_state_id: StateID, input: InputDescription):
        """
        удаляет связь между состояниями
        @from_state_id: состояние - обработчик управляющих воздействий
        @input: управляющее воздействие
        """

    # геттеры

    def get_states_by_name(self, name: Name) -> list[State]:
        """получить все состояния с данным именем"""

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        """получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния"""

    def steps(self, state_id: StateID) -> list[Step]:
        """получить все переходы, связанные с состоянием по его идентификатору"""

    # сеттеры

    def set_answer(self, state_id: StateID, data: OutputDescription):
        """Изменить ответ состояния"""

    def is_enter(self, state: State) -> bool:
        """Проверить является ли состояние входом"""
        return state.id() in self.__connections["to"].keys()

    # векторы

    def select_vectors(
        self,
        names: list[Name] | None = None,
    ) -> list[InputDescription]:
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

    def rename_state(self, state: StateID, name: Name):
        """Переименовывает состояние"""

    def rename_vector(self, old_name: Name, new_name: Name):
        """переименовывает группу синонимов"""
