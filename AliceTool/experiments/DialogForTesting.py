from PySide6 import QtCore, QtWidgets, QtGui

class DialogForTesting(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.kek_label = QtWidgets.QLabel("kek:")
        self.lol_label = QtWidgets.QLabel("lol:")

        self.kek_editor = QtWidgets.QLineEdit()
        self.lol_editor = QtWidgets.QLineEdit()
        self.ok_btn = QtWidgets.QPushButton("OK")