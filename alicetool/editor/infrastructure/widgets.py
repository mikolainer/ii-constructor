from PySide6.QtCore import (
    Qt, Slot, Signal,
)

from PySide6.QtGui import (
    QMouseEvent,
    QPaintEngine,
)

from PySide6.QtWidgets import (
    QLayoutItem,
    QWidget,
    QStackedWidget,
    QVBoxLayout,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QLineEdit,
    QLabel,
    QSpacerItem,
)

class SynonymEditorWidget(QWidget):
    __edit: QLineEdit

    def __init__(self, value:str, parent: QWidget = None):
        super().__init__(parent)
        self.__edit = QLineEdit(value, self)
        self.__edit.setStyleSheet('QLineEdit{background-color: #FFFFFF; border: 2px solid black; border-radius: 5px;}')
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self.__edit)
        
class SynonymsGroupWidget(QWidget):
    __id: int
    __title: QLabel
    __description: QLabel

    def id(self):
        return self.__id
    
    def name(self):
        return self.__title.text()
    
    def description(self):
        return self.__description.text()

    clicked = Signal()

    def __init__(self, name:str, id:int, description: str, parent: QWidget = None):
        super().__init__(parent)
        self.__id = id

        self.setStyleSheet('QWidget{background-color: #FFFFFF; border: 2px solid #FFFFFF;}')
        main_lay = QVBoxLayout(self)

        self.__title = QLabel(name, self)
        self.__title.setMinimumHeight(30)
        font = self.__title.font()
        font.setBold(True)
        self.__title.setFont(font)
        main_lay.addWidget(self.__title)

        self.__description = QLabel(description, self)
        self.__description.setMinimumHeight(30)
        main_lay.addWidget(self.__description)

        main_lay.setContentsMargins(5,0,5,0)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit()
        event.accept()
        #return super().mouseReleaseEvent(event)
