import sys
from PySide6.QtCore import QCoreApplication, QFile, QIODevice, QTextStream
from PySide6.QtGui import QPalette, QGuiApplication
from PySide6.QtWidgets import QApplication, QStyleFactory
from presentation import ProjectManager

import resources.styles_rc

if __name__ == "__main__":
    sys.argv += ['-platform', 'windows:darkmode=0']

    app = QApplication(sys.argv)
    app.setOrganizationName("ii_constructor")
    app.setApplicationName("scenario_editor")

    stream = QFile(":/styles/light.qss")
    stream.open(QIODevice.ReadOnly)
    app.setStyleSheet(QTextStream(stream).readAll())

    projects = ProjectManager()
    app.exec()