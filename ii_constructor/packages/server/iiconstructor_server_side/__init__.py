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


from iiconstructor_core.domain import (
    InputDescription,
    Source,
    State,
    Step,
    _Exists,
)
from iiconstructor_core.domain.exceptions import (
    CoreException,
    Exists,
    NotExists,
)
from iiconstructor_core.domain.primitives import (
    Name,
    Output,
    StateAttributes,
    StateID,
)
from iiconstructor_server_side.ports import ScenarioInterface


class Scenario(ScenarioInterface):
    __src: Source

    # Scenario public

    def __init__(self, src: Source) -> None:
        self.__src = src

    def source(self) -> Source:
        return self.__src

    def get_layouts(self) -> str:
        return self.__src.get_layouts()

    def save_lay(self, id: StateID, x: float, y: float):
        self.__src.save_lay(id, x, y)

    # создание сущностей
    def create_enter_state(
        self,
        input: InputDescription,
        required: bool = False,
    ):
        """добавляет вектор и новое состояние-вход с таким-же именем"""

        # создаём вектор
        self.add_vector(input)

        # создаём состояние
        state_to = self.__src.create_state(
            StateAttributes(None, input.name(), None),
            required,
        )

        # делаем состояние точкой входа
        self.make_enter(state_to.id())

    def create_enter_vector(self, input: InputDescription, state_id: StateID):
        """Делает состояние точкой входа. Создаёт вектор с соответствующим состоянию именем"""
        _states = self.states()
        state_to = _states[state_id]
        for _state in _states.values():
            if (
                _state.attributes.name == state_to.attributes.name
                and _state.id() != state_to.id()
            ):
                raise CoreException(
                    "Состояние-вход должно иметь уникальное имя!",
                )

        # проверяем существование вектора c именем состояния входа
        vector_name: Name = self.states([state_id])[state_id].attributes.name
        if self.check_vector_exists(vector_name):
            raise Exists(vector_name, f'Вектор с именем "{vector_name.value}"')

        self.add_vector(input)

    def make_enter(self, state_id: StateID):
        """привязывает к состоянию существующий вектор с соответствующим именем как команду входа"""
        # получаем состояние
        state_to = self.states([state_id])[state_id]

        # проверяем является ли входом
        if self.is_enter(state_to):
            raise Exists(
                state_to,
                f'Точка входа в состояние "{state_to.id().value}"',
            )

        input_name = state_to.attributes.name
        self.__src.new_step(None, state_to.id(), input_name)

    def create_step(
        self,
        from_state_id: StateID,
        to_state: StateAttributes | StateID,
        input: InputDescription,
    ) -> Step:
        """
        Создаёт переход из from_state в to_state по переходу input
        @from_state_id: id состояния для обработки управляющего воздействия input
        @to_state: id состояния в которое будет добавлен переход или аттрибуты для создания такого состояния
        @input: управляющее воздействие
        """
        state_to: State

        if isinstance(to_state, StateID):
            state_to = self.states([to_state])[to_state]

        elif isinstance(to_state, StateAttributes):
            _states = self.states()
            for _state in _states.values():
                if _state.attributes.name == to_state.name and self.is_enter(
                    _state,
                ):
                    raise CoreException(
                        f'Cуществует состояние-вход с именем "{to_state.name.value}"! Состояние-вход должно иметь уникальное имя.',
                    )

            state_to = self.__src.create_state(to_state)

        return self.__src.new_step(from_state_id, state_to.id(), input.name())

    # удаление сущностей

    def remove_state(self, state_id: StateID):
        """удаляет состояние"""
        if self.states([state_id])[state_id].required:
            raise Exception("Обязательное состояние нельзя удалить!")

        if len(self.steps(state_id)) > 0:
            raise Exists(
                state_id,
                f"Состояние с id={state_id.value} связано с переходами!",
            )

        self.__src.delete_state(state_id)

    def remove_enter(self, state_id: StateID):
        """удаляет связь с командой входа в состояние"""
        enter_state = self.states([state_id])[state_id]

        if enter_state.required:
            raise Exception("Обязательную точку входа нельзя удалить!")

        self.__src.delete_step(None, state_id)

    def remove_step(self, from_state_id: StateID, input: InputDescription):
        """
        удаляет связь между состояниями
        @from_state_id: состояние - обработчик управляющих воздействий
        @input: управляющее воздействие
        """
        self.__src.delete_step(from_state_id, None, input.name())

    # геттеры

    def get_states_by_name(self, name: Name) -> list[State]:
        """получить все состояния с данным именем"""
        return self.__src.get_states_by_name(name)

    def states(self, ids: list[StateID] = None) -> dict[StateID, State]:
        """получить состояния по идентификаторам. если ids=None - вернёт все существующие состояния"""
        return self.__src.states(ids)

    def steps(self, state_id: StateID) -> list[Step]:
        """получить все переходы, связанные с состоянием по его идентификатору"""
        return self.__src.steps(state_id)

    def is_enter(self, state: State) -> bool:
        """Проверить является ли состояние входом"""
        return self.__src.is_enter(state)

    # сеттеры

    def set_answer(self, state_id: StateID, data: Output):
        """Изменить ответ состояния"""
        self.__src.set_answer(state_id, data)

    # векторы

    def select_vectors(
        self,
        names: list[Name] | None = None,
    ) -> list["InputDescription"]:
        """
        Возвращает список векторов управляющих воздействий по указанным именам
        @names - список идентификаторов для получения выборки векторов (если =None - вернёт все)
        """
        return self.__src.select_vectors(names)

    def get_vector(self, name: Name) -> InputDescription:
        """
        Возвращает вектор управляющих воздействий по имени
        @names - имя вектора (идентификатор)
        """
        return self.__src.get_vector(name)

    def add_vector(self, input: InputDescription):
        """
        Сохраняет новый вектор для обработки управляющих воздействий
        @input_type - новый вектор
        """
        if self.check_vector_exists(input.name()):
            raise _Exists(self.get_vector(input.name()))

        return self.__src.add_vector(input)

    def remove_vector(self, name: Name):
        """
        Удаляет вектор управляющих воздействий
        @name - имя вектора для удаления (идентификатор)
        """
        self.__src.remove_vector(name)

    def check_vector_exists(self, name: Name) -> bool:
        """
        Проверяет существование вектора
        @name - имя вектора для проверки (идентификатор)
        """
        return self.__src.check_vector_exists(name)

    def set_synonym_value(
        self,
        input_name: str,
        old_synonym: str,
        new_synonym: str,
    ):
        """изменяет значение синонима"""
        self.__src.set_synonym_value(input_name, old_synonym, new_synonym)

    def create_synonym(self, input_name: str, new_synonym: str):
        """создаёт синоним"""
        self.__src.create_synonym(input_name, new_synonym)

    def remove_synonym(self, input_name: str, synonym: str):
        """удаляет синоним"""
        self.__src.remove_synonym(input_name, synonym)

    def rename_state(self, state: StateID, name: Name):
        """Переименовывает состояние"""
        if self.is_enter(self.__src.states([state])[state]):
            raise CoreException(
                "Нельзя переименовать состояние, которое является входом",
            )

        vector_exsists = True
        vector: InputDescription
        try:
            vector = self.get_vector(name)
        except Exception:
            vector_exsists = False

        if vector_exsists:
            for _conn in self.__src.input_usage(vector):
                if _conn.from_state is None:
                    if self.is_enter(_conn.to_state):
                        raise CoreException(
                            f'Состояние с именем "{name.value}" уже существует и является входом',
                        )

        self.__src.rename_state(state, name)

    def rename_vector(self, old_name: Name, new_name: Name):
        """переименовывает группу синонимов"""
        for state in self.get_states_by_name(old_name):
            if self.is_enter(state):
                raise CoreException(
                    "Нельзя переименовать вектор, который используется с точкой входа!",
                )

        try:
            self.get_vector(new_name)
            raise CoreException(
                f'Вектор с именем "{new_name.value}" уже существует!',
            )

        except NotExists:
            self.__src.rename_vector(old_name, new_name)

        except Exception:
            raise
