from PySide6 import QtWidgets, QtCore, QtGui
from infrastructure.gui import MainWindow
from services.api import EditorAPI
from services.updates import EditorGuiRefresher

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    
    main_win = MainWindow()
    EditorAPI(EditorGuiRefresher(main_win)) # init

    app.exec()