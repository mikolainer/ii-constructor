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

class SynonymWidget(QWidget):
    __edit: QLineEdit

    def __init__(self, value:str, parent: QWidget = None):
        super().__init__(parent)
        self.__edit = QLineEdit(value, self)
        self.__edit.setStyleSheet('QLineEdit{background-color: #FFFFFF; border: 2px solid black; border-radius: 5px;}')
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self.__edit)

class SynonymsList(QStackedWidget):
    __indexed: dict[int, list[SynonymWidget]]

    def addWidget(self, w: QWidget = None) -> int:
        area = QScrollArea(self)
        area.setWidgetResizable(True)
        area.setStyleSheet('QScrollArea{background-color: #FFFFFF; border: none;}')

        wrapper = QWidget(self)
        QVBoxLayout(wrapper)

        area.setWidget(wrapper)
        return super().addWidget(area)
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__indexed = {}
    
    def setList(self, items :list[SynonymWidget], set_current: bool = False):
        ''' обновление списка виджетов '''
        # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not items in self.__indexed.items():
            self.__indexed[self.addWidget()] = items

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(items)]
        
        # добавляем новые виджеты (уже существующие не вставятся снова)
        lay = self.widget(idx).widget().layout()
        for wgt in items:
            lay.addWidget(wgt)
        
        # удаляем виджеты не элементов
        to_remove = []
        for item_idx in range(lay.count()):
            item:QLayoutItem = lay.itemAt(item_idx)
            if not isinstance(item.widget(), SynonymWidget):
                to_remove.append(item)

        for item in to_remove:
            if not item is None:
                lay.removeItem(item)

        # добавляем заполнитель пустоты в конце
        lay.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))

        # если указано - устанавливаем текущим виджетом
        if set_current:
            self.setCurrentIndex(idx)
        
class SynonymsGroupWidget(QWidget):
    __id: int
    __title: QLabel

    def id(self):
        return self.__id
    
    def name(self):
        return self.__title.text()
    
    def description(self):
        return "описание"

    clicked = Signal()

    def __init__(self, name:str, id:int, parent: QWidget = None):
        super().__init__(parent)
        self.__id = id
        self.setStyleSheet('QWidget{background-color: #FFFFFF; border: 2px solid #FFFFFF;}')
        self.__title = QLabel(name, self)
        self.__title.setMinimumHeight(30)
        font = self.__title.font()
        font.setBold(True)
        self.__title.setFont(font)
        main_lay = QVBoxLayout(self)
        main_lay.addWidget(self.__title)
        main_lay.setContentsMargins(5,0,5,0)
    
    def set_selected(self, selected: bool = True):
        self.setStyleSheet(
            'QWidget{background-color: #FFFFFF; border: 2px solid #59A5FF;}'
            if selected else
            'QWidget{background-color: #FFFFFF; border: 2px solid #FFFFFF;}'
        )

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit()
        event.accept()
        #return super().mouseReleaseEvent(event)

class SynonymsGroupsList(QStackedWidget):
    __indexed: dict[int, list[SynonymsGroupWidget]]

    def addWidget(self, w: QWidget = None) -> int:
        wrapper = QWidget(self)
        wrapper.setStyleSheet('QWidget{background-color: #666666;}')
        lay = QVBoxLayout(wrapper)
        lay.setContentsMargins(0,0,0,0)
        lay.setSpacing(3)


        area = QScrollArea(self)
        area.setContentsMargins(0,0,0,0)
        area.setWidgetResizable(True)
        area.setStyleSheet('QScrollArea{background-color: #666666; border: none;}')
        area.setWidget(wrapper)

        return super().addWidget(area)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__indexed = {}
        self.resize(250, self.height())
    
    def setList(self, items :list[SynonymsGroupWidget]):
         # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not items in self.__indexed.items():
            self.__indexed[self.addWidget()] = items

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(items)]
        
        # добавляем новые виджеты (уже существующие не вставятся снова)
        lay:QVBoxLayout = self.widget(idx).widget().layout()
        for wgt in items:
            prev_c = lay.count()
            lay.addWidget(wgt)
            # соединим новый виджет с сигналом выбора
            if lay.count() != prev_c:
                wgt.clicked.connect(self.__group_selected)
                
        
        # удаляем виджеты не элементов
        to_remove = []
        for item_idx in range(lay.count()):
            item:QLayoutItem = lay.itemAt(item_idx)
            if not isinstance(item.widget(), SynonymsGroupWidget):
                to_remove.append(item)

        for item in to_remove:
            if not item is None:
                lay.removeItem(item)

        # добавляем заполнитель пустоты в конце
        lay.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding))

        self.setCurrentIndex(idx)

    group_selected = Signal(int, SynonymsGroupWidget)

    @Slot()
    def __group_selected(self):
        selected:SynonymsGroupWidget = self.sender()
        self.group_selected.emit(selected.id(), selected)

        lay = self.currentWidget().widget().layout()
        for i in range(lay.count()):
            item = lay.itemAt(i).widget()
            if isinstance(item, SynonymsGroupWidget):
                item.set_selected(item is selected)