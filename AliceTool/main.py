import sys
from PySide6 import QtCore, QtWidgets, QtGui
from experiments import DialogForTesting

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    dialog = DialogForTesting.DialogForTesting()
    dialog.exec()
    app.quit()

    sys.exit(app.exec())



