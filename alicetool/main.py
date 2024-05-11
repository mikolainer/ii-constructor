from PySide6 import QtWidgets, QtCore, QtGui
from alicetool.services.api import EditorAPI
from alicetool.infrastructure.gui import MainWindow, FlowList, Workspaces, SynonymsEditor
from alicetool.services.updates import EditorGuiRefresher

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    flow_list = FlowList()
    synonyms = SynonymsEditor()
    workspaces = Workspaces()
    main_win = MainWindow(flow_list, workspaces, synonyms)

    set_sm_notifier = (
        lambda id, notifier:
            EditorAPI.instance().set_content_notifier(id, notifier)
    )
    main_changes_handler = EditorGuiRefresher(
        set_sm_notifier, flow_list, synonyms, workspaces, main_win
    )
    EditorAPI(main_changes_handler)

    app.exec()