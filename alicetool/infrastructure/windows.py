from collections.abc import Callable

from PySide6.QtCore import (
    Qt,
    QPoint,
    Slot,
    QSize,
)

from PySide6.QtGui import (
    QIcon,
    QResizeEvent,
    QPixmap,
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
from alicetool.infrastructure.views import SynonymsGroupsView, SynonymsList, GroupsList
from alicetool.infrastructure.data import CustomDataRole, SynonymsSetModel, SynonymsGroupsModel

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

class SynonymsEditor(QDialog):
    __oldPos: QPoint | None
    __tool_bar: QWidget # полоска с кнопкой "закрыть"
    __exit_btn: QPushButton

    __synonyms_list: SynonymsList
    __group_list: GroupsList

    __g_model:SynonymsGroupsModel
    __create_group_handler:Callable
    __create_value_handler:Callable

    def __init__(
            self, g_model:SynonymsGroupsModel,
            create_group_handler:Callable[[SynonymsGroupsModel], None],
            create_value_handler:Callable[[SynonymsSetModel], None],
            parent: QWidget | None = None
        ) -> None:
        self.__g_model = g_model
        self.__create_group_handler = create_group_handler
        self.__create_value_handler = create_value_handler

        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.Window, True)

        self.setWindowTitle('Редактор синонимов')
        self.resize(600, 500)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        # полоска с кнопкой закрыть
        self.__tool_bar = QWidget(self)
        self.__tool_bar.setMinimumHeight(24)
        main_lay.addWidget(self.__tool_bar, 0)
        self.__tool_bar.setStyleSheet('background-color : #666;')
        self.__oldPos = None

        tool_bar_layout = QHBoxLayout(self.__tool_bar)
        tool_bar_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        tool_bar_layout.setSpacing(10)
        tool_bar_layout.setContentsMargins(2, 2, 2, 2)
        tool_bar_layout.addSpacerItem(
            QSpacerItem(
                0,0,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            )
        )

        size = QSize(20,20)
        self.__exit_btn: QPushButton = QPushButton(self)
        self.__exit_btn.clicked.connect(lambda: self.close())
        self.__exit_btn.setToolTip('Закрыть')
        self.__exit_btn.setStatusTip('Закрыть редактор синонимов')
        self.__exit_btn.setWhatsThis('Закрыть редактор синонимов')
        self.__exit_btn.setIcon(QIcon(QPixmap(":/icons/exit_norm.svg").scaled(12,12)))
        self.__exit_btn.setIconSize(size)
        self.__exit_btn.setFixedSize(size)
        self.__exit_btn.setStyleSheet("background-color: #FF3131; border: 0px; border-radius: 10px")
        tool_bar_layout.addWidget(self.__exit_btn)

        self.__group_list = GroupsList(self)
        self.__group_list.create_value.connect(lambda model: self.__create_group_handler(model))
        
        g_view = SynonymsGroupsView(self)
        g_view.setModel(g_model)
        self.__group_list.setList(g_view, True)

        self.__synonyms_list = SynonymsList(self)
        self.__synonyms_list.create_value.connect(lambda model: self.__create_value_handler(model))
        self.__synonyms_list.set_empty()

        g_view.selectionModel().selectionChanged.connect(
            lambda now, prev: self.__on_syn_group_changed(now.indexes())
        )

        # рабочая область
        splitter = QSplitter( self, Qt.Orientation.Horizontal )
        splitter.addWidget(self.__group_list)
        splitter.setStretchFactor(0,0)
        splitter.addWidget(self.__synonyms_list)
        splitter.setStretchFactor(1,1)
        
        main_lay.addWidget(splitter, 1)

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

    def resizeEvent(self, event: QResizeEvent) -> None:
        # костыль
        if event.oldSize() != event.size():
            self.resize(event.size())

        return super().resizeEvent(event)
    
    @Slot(list)
    def __on_syn_group_changed(self, selected_index_list):
        if len(selected_index_list):
            synonyms = self.__g_model.data(
                selected_index_list[0],
                CustomDataRole.SynonymsSet
            )
            self.__synonyms_list.set_current(synonyms)

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