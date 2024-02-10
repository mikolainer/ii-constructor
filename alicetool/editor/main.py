from PySide6 import QtWidgets
from domain.projects import ProjectsManager

from infrastructure.gui import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    main_win = MainWindow()

    app.exec()