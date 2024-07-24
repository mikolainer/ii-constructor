from PySide6.QtWidgets import QApplication
from alicetool.presentation.editor.gui import ProjectManager

if __name__ == "__main__":
    app = QApplication([])
    projects = ProjectManager()
    app.exec()