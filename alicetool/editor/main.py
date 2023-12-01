import sys
from PySide6 import QtWidgets
from experiments import sandbox

from . import test

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    dialog = sandbox.DialogForTesting()
    dialog.exec()
#    app.quit(0)
#    sys.exit(app.exec())