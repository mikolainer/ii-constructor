import sys
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QStyleFactory
from presentation import ProjectManager

if __name__ == "__main__":
    sys.argv += ['-platform', 'windows:darkmode=0']

    app = QApplication(sys.argv)
    app.setOrganizationName("ii_constructor")
    app.setApplicationName("scenario_editor")
    keys = QStyleFactory.keys()
    #app.setStyle(QStyleFactory.create("Fusion"))

    projects = ProjectManager()
    app.exec()