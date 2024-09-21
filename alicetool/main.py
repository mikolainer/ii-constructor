from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
from alicetool.presentation.editor.gui import ProjectManager

if __name__ == "__main__":
    QCoreApplication.setOrganizationName("ii_constructor")
    QCoreApplication.setApplicationName("scenario_editor")
    app = QApplication([])
    projects = ProjectManager()
    app.exec()