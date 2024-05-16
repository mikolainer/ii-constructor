from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    Signal
)

from PySide6.QtGui import (
    QMouseEvent,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QInputDialog,
    QStackedWidget,
    QScrollArea,
)

class FlowListWidget(QWidget):
    __view: QWidget

    '''args: name, descr'''
    create_value = Signal(str, str) 

    @Slot()
    def __create_flow(self):
        name, ok = QInputDialog.getText(self, "Имя нового потока", "Имя нового потока:")
        if not ok: return

        descr, ok = QInputDialog.getText(self, "Описание нового потока", "Описание нового потока:")
        if not ok: return

        self.create_value.emit(name, descr)

    def __init__(self, view: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(3,3,0,3)

        lay.addWidget(view, 0)

        btn = QPushButton("+", self)
        btn.clicked.connect(self, self.__create_flow)
        lay.addWidget(btn, 1)

class FlowList(QStackedWidget):
    __indexed: dict[int, QWidget]
    __empty_index:int

    def addWidget(self, w: QWidget = None) -> int:
        area = QScrollArea(self)
        area.setWidgetResizable(True)
        area.setStyleSheet('QScrollArea{background-color: #FFFFFF; border: none;}')
        area.setWidget(w)
        return super().addWidget(area)
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__indexed = {}
        self.__empty_index = super().addWidget(QWidget(self))
        self.setMinimumWidth(200)

    def set_empty(self):
        self.setCurrentIndex(self.__empty_index)
    
    def setWidget(self, item: QWidget, set_current: bool = False):
        ''' обновление списка виджетов '''
        # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not item in self.__indexed.values():
            self.__indexed[self.addWidget(item)] = item

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(item)]

        # если указано - устанавливаем текущим виджетом
        if set_current:
            self.setCurrentIndex(idx)

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