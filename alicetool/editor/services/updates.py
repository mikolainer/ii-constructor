from alicetool.editor.domain.projects import ProjectsActionsNotifier, StateMachineNotifier
from alicetool.editor.infrastructure.gui import MainWindow

class EditorGuiRefresher(ProjectsActionsNotifier):
    def __init__(self, main_window: MainWindow):
        pass

    def created(self, id:int, data):
        raise NotImplementedError()

    def saved(self, id:int, data):
        raise NotImplementedError()

    def updated(self, id:int, new_data):
        raise NotImplementedError()

    def removed(self, id:int):
        raise NotImplementedError()

class StateMachineGuiRefresher(StateMachineNotifier):
    pass
