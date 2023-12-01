from PySide6 import QtCore, QtWidgets, QtGui

class NewProjectDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
    
    def get_result(self):
        '''
        returns data transfer object with all data
        (наверное можно в json)
        '''

    def test_get_io(self):
        '''
        !!! ONLY FOR UNITTESTS !!!
        returns dictionary with all io items
        wich named as in test_*.py file
        '''
        return {
            'редактор пути к файлу': QtWidgets.QLineEdit(),
            'редактор имени': QtWidgets.QLineEdit(),
            'редактор имени для БД': QtWidgets.QLineEdit(),
            'редактор приветственной фразы': QtWidgets.QTextEdit(),
            'редактор ответа "Помощь"': QtWidgets.QTextEdit(),
            'редактор ответа "Что ты умеешь?"': QtWidgets.QTextEdit(),
            'кнопка "Начать"': QtWidgets.QPushButton(),
            'диалог подтверждения перезаписи': {
                'ok': QtWidgets.QPushButton(),
                'cancel': QtWidgets.QPushButton(),
            }
        }