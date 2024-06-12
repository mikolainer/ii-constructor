from typing import Optional

from PySide6.QtCore import (
    Qt,
    Signal,
    QPoint,
    QSize,
)

from PySide6.QtGui import (
    QIcon,
)

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QSplitter,
    QSpacerItem,
    QLabel,
    QLineEdit,
    QDialog,
    QTextEdit,
    QPushButton,
    QStackedWidget,
    QScrollArea,
    QTabWidget,
    QGraphicsView,
)


import alicetool.resources.rc_icons

class MainToolButton(QPushButton):
    ''' Кнопка туллбара главного окна '''
    tool_tip : str
    status_tip : str
    whats_this : str
    icon : Optional[QIcon]
    icon_size : QSize

    __size : QSize
    __style : str

    def __init__(self, text: str, icon: Optional[QWidget] = None, parent: Optional[QWidget] = None):
        super().__init__(icon, '', parent)

        self.__size = QSize(64, 64)
        self.__style = "background-color: #59A5FF; border-radius:32px;"

        self.icon = icon
        self.tool_tip = text
        self.status_tip = text
        self.whats_this = text
        self.icon_size = self.__size

        self.setStyleSheet(self.__style)
        self.apply_options()

    def apply_options(self):
        ''' Применяет значения указанные в публичных атрибутах класса '''
        self.setToolTip(self.tool_tip)
        self.setStatusTip(self.status_tip)
        self.setWhatsThis(self.whats_this)
        self.setFixedSize(self.__size)
        self.setIcon(self.icon)
        self.setIconSize(self.icon_size)

class MainWindow(QMainWindow):
    ''' Главное окно клиента работы над сценариями '''
    __oldPos: QPoint | None
    __tool_bar: QWidget

    def __init__(self, flow_list: QWidget, workspaces: QWidget, parent: QWidget = None):
        super().__init__(None, Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("MainWindow{background-color: #74869C;}")

        self.__oldPos = None

        flow_list.setParent(self)
        workspaces.setParent(self)

        self.__setup_ui(flow_list, workspaces)
        self.__setup_toolbar()

        self.show()

    def insert_button(self, btn: MainToolButton, index: int = 0):
        ''' Добавляет кнопку в туллбар '''
        layout: QHBoxLayout = self.__tool_bar.layout()
        layout.insertWidget(index, btn)

    def __setup_ui(self, flow_list: QWidget, workspaces: QWidget):
        self.setCentralWidget(QWidget(self))

        main_lay = QVBoxLayout(self.centralWidget())
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        self.__tool_bar = QWidget(self)
        self.__tool_bar.setMinimumHeight(64)
        main_lay.addWidget(self.__tool_bar, 0)
        self.__tool_bar.setStyleSheet('background-color : #666;')

        tool_bar_layout = QHBoxLayout(self.__tool_bar)
        tool_bar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        tool_bar_layout.setSpacing(10)
        tool_bar_layout.setContentsMargins(5, 3, 3, 5)
        
        main_splitter = QSplitter(
            self,
            Qt.Orientation.Horizontal
        )
        main_splitter.addWidget(flow_list)
        main_splitter.addWidget(workspaces)
        main_splitter.setStretchFactor(0,0)
        main_splitter.setStretchFactor(1,1)
        
        main_lay.addWidget(main_splitter, 1)

        self.setGeometry(0, 0, 900, 700)

    def __setup_toolbar(self):
        layout: QHBoxLayout = self.__tool_bar.layout()

        # добавление крестика
        layout.addSpacerItem(
            QSpacerItem( 0,0,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            )
        )

        btn = MainToolButton('Выйти', QIcon(":/icons/exit_norm.svg"), self)
        btn.setStyleSheet("background-color: #FF3131; border: none;")
        
        btn.status_tip = 'Закрыть программу'
        btn.whats_this = 'Кнопка завершения программы'
        btn.icon_size = btn.icon_size * 0.6
        btn.apply_options()
        btn.clicked.connect(lambda: self.close())     
        layout.addWidget(btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.__oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.__oldPos is not None:
            delta = event.globalPos() - self.__oldPos
            self.move(self.pos() + delta)
            self.__oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.__oldPos = None

class NewProjectDialog(QDialog):
    ''' Диалог создания нового сценария '''

    __file_path_editor : QLineEdit # TODO: убрать в диалог экспорта
    __db_name_editor : QLineEdit # TODO: убрать в диалог публикации
    __name_editor : QLineEdit
    __hello_editor : QTextEdit
    __help_editor : QTextEdit
    __info_editor : QTextEdit
    __ok_button : QPushButton
    __STATE_TEXT_MAX_LEN: int

    def __init__(self, parent: QWidget | None = None, STATE_TEXT_MAX_LEN = 1000):
        super().__init__(parent)

        lay = QVBoxLayout(self)

        self.__STATE_TEXT_MAX_LEN = STATE_TEXT_MAX_LEN
        self.__file_path_editor = QLineEdit(self)
        self.__name_editor = QLineEdit(self)
        self.__db_name_editor = QLineEdit(self)
        self.__hello_editor = QTextEdit(self)
        self.__help_editor = QTextEdit(self)
        self.__info_editor = QTextEdit(self)
        self.__ok_button = QPushButton("Начать", self)

        lay.addWidget(QLabel('Путь к файлу'))
        lay.addWidget(self.__file_path_editor)
        lay.addWidget(QLabel('Имя проекта для БД'))
        lay.addWidget(self.__db_name_editor)
        lay.addWidget(QLabel('Имя проекта для отображения'))
        lay.addWidget(self.__name_editor)
        lay.addWidget(QLabel('Текст приветственной фразы'))
        lay.addWidget(self.__hello_editor)
        lay.addWidget(QLabel('Текст ответа "Помощь"'))
        lay.addWidget(self.__help_editor)
        lay.addWidget(QLabel('Текст ответа "Что ты умеешь?"'))
        lay.addWidget(self.__info_editor)
        lay.addWidget(self.__ok_button)
        self.__ok_button.clicked.connect(lambda: self.accept())

    def get_result(self):
        ''' возвращает сериализованные данные для создания сценария '''
        return (
            f'name={self.__name_editor.text()}; '
            f'db_name={self.__db_name_editor.text()}; '
            f'file_path={self.__file_path_editor.text()}; '
            f'hello={self.__hello_editor.toPlainText()[: self.__STATE_TEXT_MAX_LEN]}; '
            f'help={self.__help_editor.toPlainText()[: self.__STATE_TEXT_MAX_LEN]}; '
            f'info={self.__info_editor.toPlainText()[: self.__STATE_TEXT_MAX_LEN]}'
        )
    
class Workspaces(QTabWidget):
    ''' Область графической сцены сценариев и выбора активного проекта (правая часть главного окна) '''
    activated = Signal(QGraphicsView)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.currentChanged.connect(lambda index: self.activated.emit(self.widget(index)))

    def set_active(self, view:QGraphicsView):
        self.setCurrentWidget(view)

    def open_editor(self, view:QGraphicsView, name:str):
        self.addTab(view, name)
        self.set_active(view)

    def close_editor(self, view:QGraphicsView):
        self.removeTab(self.indexOf(view))

class FlowList(QStackedWidget):
    ''' Содержание активного проекта. (левая часть главного окна) '''
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
        ''' Добавляет уникальное для проекта содержание '''
        # для нового списка создаём отдельный виджет и сохраняем его индекс
        if not item in self.__indexed.values():
            self.__indexed[self.addWidget(item)] = item

        # получаем индекс виджета с полученным списком синонимов
        idx:int = list(self.__indexed.keys())[list(self.__indexed.values()).index(item)]

        # если указано - устанавливаем текущим виджетом
        if set_current:
            self.setCurrentIndex(idx)
            