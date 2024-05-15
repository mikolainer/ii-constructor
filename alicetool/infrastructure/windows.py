from PySide6.QtCore import (
    Qt,
    QPoint,
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
    QSpacerItem,
    QLabel,
    QLineEdit,
    QDialog,
    QTextEdit,
    QPushButton,
)

from alicetool.infrastructure.buttons import MainToolButton
import alicetool.resources.rc_icons

class MainWindow(QMainWindow):
    __oldPos: QPoint | None
    __tool_bar: QWidget

    def insert_button(self, btn: MainToolButton, pos: int = 0):
        layout: QHBoxLayout = self.__tool_bar.layout()
        layout.insertWidget(pos, btn)

    def __init__(self, flow_list: QWidget, workspaces: QWidget, parent: QWidget = None):
        super().__init__(None, Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("MainWindow{background-color: #74869C;}")

        self.__oldPos = None

        flow_list.setParent(self)
        workspaces.setParent(self)

        self.__setup_ui(flow_list, workspaces)
        self.__setup_toolbar()

        self.show()

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
        return (
            f'name={self.__name_editor.text()}; '
            f'db_name={self.__db_name_editor.text()}; '
            f'file_path={self.__file_path_editor.text()}; '
            f'hello={self.__hello_editor.toPlainText()[: self.__STATE_TEXT_MAX_LEN]}; '
            f'help={self.__help_editor.toPlainText()[: self.__STATE_TEXT_MAX_LEN]}; '
            f'info={self.__info_editor.toPlainText()[: self.__STATE_TEXT_MAX_LEN]}'
        )