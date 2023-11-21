from PySide6 import QtCore, QtWidgets, QtGui

class DialogForTesting(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.__kek_label = QtWidgets.QLabel("kek:")
        self.__lol_label = QtWidgets.QLabel("lol:")
        self.__kek_editor = QtWidgets.QLineEdit()
        self.__lol_editor = QtWidgets.QLineEdit()
        self.__ok_btn = QtWidgets.QPushButton("OK")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.__kek_label)
        layout.addWidget(self.__kek_editor)
        layout.addWidget(self.__lol_label)
        layout.addWidget(self.__lol_editor)
        layout.addWidget(self.__ok_btn)

        self.setLayout(layout)

    def test_getIO(self):
        return {
            'kek_editor': self.__kek_editor,
            'lol_editor': self.__lol_editor,
            'ok_btn': self.__ok_btn,
        }