from PySide6 import QtWidgets, QtCore, QtGui
from alicetool.editor.services.api import EditorAPI
from alicetool.editor.infrastructure.gui import MainWindow, FlowList, Workspaces, SynonymsEditor
from alicetool.editor.services.updates import EditorGuiRefresher

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    flow_list = FlowList()
    synonyms = SynonymsEditor()
    workspaces = Workspaces(flow_list, synonyms)

    EditorAPI(
        EditorGuiRefresher(
            workspaces,
            lambda id, notifier:
                EditorAPI.instance().set_content_notifier(id, notifier)
        )
    )

    main_win = MainWindow(flow_list, workspaces, synonyms)

    app.exec()