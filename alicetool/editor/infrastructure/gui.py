import sys

from PySide6.QtGui import QIcon, QPixmap, QValidator
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QSplitter,
    QPushButton,
    QSpacerItem,
    QDialog,
    QLineEdit,
    QTextEdit,
    QLabel,
)

from alicetool.editor.domain.projects import ProjectsManager, ProjectsActionsNotifier
from alicetool.editor.domain.core import State

import alicetool.editor.resources.rc_icons

class MainWindow(QMainWindow):
    def __make_project(self):
        dialog = NewProjectDialog(self)
        dialog.exec()

    def __setup_ui(self):
        self.setCentralWidget(QWidget(self))

        main_lay = QVBoxLayout(self.centralWidget())
        self.__tool_bar = QWidget(self)
        self.__tool_bar.setMinimumHeight(64)
        main_lay.addWidget(self.__tool_bar, 0)
        self.__tool_bar.setStyleSheet('background-color : #666;')

        tool_bar_layout = QHBoxLayout(self.__tool_bar)
        tool_bar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        tool_bar_layout.setSpacing(10)
        tool_bar_layout.setContentsMargins(5, 3, 3, 5)

        self.__content = QScrollArea(self.centralWidget())
        QVBoxLayout(self.__content)
        
        self.__editor = QTabWidget(self.centralWidget())
        QVBoxLayout(self.__editor)
        
        main_splitter = QSplitter(
            self,
            Qt.Orientation.Horizontal
        )
        main_splitter.addWidget(self.__content)
        main_splitter.addWidget(self.__editor)
        main_splitter.setStretchFactor(0,0)
        main_splitter.setStretchFactor(1,1)
        
        main_lay.addWidget(main_splitter, 1)

        self.setGeometry(0, 0, 900, 700)

    def __setup_toolbar(self):
        self.__buttons = {
            'new' : QPushButton(self),
            'open' : QPushButton(self),
            'save' : QPushButton(self),
            'publish' : QPushButton(self),
            'synonyms' : QPushButton(self),
            'exit' : QPushButton(self),
        }

        layout: QHBoxLayout = self.__tool_bar.layout()

        for key in self.__buttons.keys():
            btn: QPushButton = self.__buttons[key]
            
            style = "background-color: #59A5FF; border-radius:32px;"
            size = QSize(64,64)

            if key == 'new':
                tool_tip = 'Новый проект'
                status_tip = 'Создать новый проект'
                whats_this = 'Кнопка создания нового проекта'
                icon = QIcon(QPixmap(":/icons/new_proj_norm.svg"))
                btn.clicked.connect(lambda: self.__make_project())

            if key == 'open':
                tool_tip = 'Открыть проект'
                status_tip = 'Открыть файл проекта'
                whats_this = 'Кнопка открытия проекта из файла'
                icon = QIcon(QPixmap(":/icons/open_proj_norm.svg"))

            if key == 'save':
                tool_tip = 'Сохранить проект'
                status_tip = 'Сохранить в файл'
                whats_this = 'Кнопка сохранения проекта в файл'
                icon = QIcon(QPixmap(":/icons/save_proj_norm.svg"))

            if key == 'publish':
                tool_tip = 'Опубликовать проект'
                status_tip = 'Разместить проект в БД '
                whats_this = 'Кнопка экспорта проекта в базу данных'
                icon = QIcon(QPixmap(":/icons/export_proj_norm.svg"))

            if key == 'synonyms':
                tool_tip = 'Список синонимов'
                status_tip = 'Открыть редактор синонимов'
                whats_this = 'Кнопка открытия редактора синонимов'
                icon = QIcon(QPixmap(":/icons/synonyms_list_norm.svg"))

            if key == 'exit':
                layout.addSpacerItem(
                    QSpacerItem(
                        0,0,
                        QSizePolicy.Policy.Expanding,
                        QSizePolicy.Policy.Minimum
                    )
                )
                tool_tip = 'Выйти'
                status_tip = 'Закрыть программу'
                whats_this = 'Кнопка завершения программы'
                style = "background-color: #FF3131; border: none;"
                icon = QIcon(QPixmap(":/icons/exit_norm.svg"))

                btn.clicked.connect(lambda: self.close())

            btn.setToolTip(tool_tip)
            btn.setToolTip(status_tip)
            btn.setWhatsThis(whats_this)
            btn.setFixedSize(size)
            btn.setIcon(icon)
            btn.setIconSize(size)
            btn.setStyleSheet(style)
            layout.addWidget(btn)

    def __init__(self):
        super().__init__()

        self.__setup_ui()
        self.__setup_toolbar()
        self.show()

class PathValidator(QValidator):
    def init(self):
        super().__init__()

class NewProjectDialog(QDialog):
    # # костыль
    # def validate_1024text(self):
    #     text_edit : QTextEdit = self.sender()
    #     text = text_edit.toPlainText()
    #     if len(text) > 1024:
    #         pos = text_edit.cursor().pos()
    #         text_edit.setText(text[:1024])
    #         text_edit.cursor().setPos()

    def new_project(self):
        self.proj_id = ProjectsManager.instance().create(
            self.get_result()
        )
        self.close()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.proj_id = -1

        lay = QVBoxLayout(self)

        self.__file_path_editor = QLineEdit(self)
        self.__name_editor = QLineEdit(self)
        self.__db_name_editor = QLineEdit(self)
        self.__hello_editor = QTextEdit(self)
        self.__help_editor = QTextEdit(self)
        self.__info_editor = QTextEdit(self)
        self.__ok_button = QPushButton("Начать", self)

        # # костыль
        # for text_edit in {
        #         self.__hello_editor,
        #         self.__help_editor,
        #         self.__info_editor
        #     }:
        #     text_edit.textChanged.connect(
        #         self.validate_1024text
        #     )

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

        self.__ok_button.clicked.connect(self.new_project)
    
    def get_result(self):
        return (
            f'name={self.__name_editor.text()}; '
            f'db_name={self.__db_name_editor.text()}; '
            f'file_path={self.__file_path_editor.text()}; '
            f'hello={self.__hello_editor.toPlainText()[: State.TEXT_MAX_LEN]}; '
            f'help={self.__help_editor.toPlainText()[: State.TEXT_MAX_LEN]}; '
            f'info={self.__info_editor.toPlainText()[: State.TEXT_MAX_LEN]}'
        )

    def test_get_io(self):
        '''
        !!! ONLY FOR UNITTESTS !!!
        returns dictionary with all io items
        wich named as in test_*.py file
        '''
        return {
            'редактор пути к файлу': self.__file_path_editor,
            'редактор имени': self.__name_editor,
            'редактор имени для БД': self.__db_name_editor,
            'редактор приветственной фразы': self.__hello_editor,
            'редактор ответа "Помощь"': self.__help_editor,
            'редактор ответа "Что ты умеешь?"': self.__info_editor,
            'кнопка "Начать"': self.__ok_button,
            'диалог подтверждения перезаписи': {
                'ok': QPushButton(),
                'cancel': QPushButton(),
            }
        }
    
class EditorRefreshGuiService(ProjectsActionsNotifier):
    def __init__(self, parent: MainWindow):
        self.__parent = parent

    def created(self, id:int, data):
        self.__parent.addProject()

    def saved(self, id:int, data):
        ...

    def updated(self, id:int, new_data):
        ...

    def removed(self, id:int):
        ...
