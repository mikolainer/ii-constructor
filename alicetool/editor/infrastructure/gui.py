import sys

from PySide6.QtCore import Qt, QSize, QPoint, QRectF, QRect
from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QValidator,
    QFont,
    QCursor,
    QTransform,
    QColor,
    QPalette,
    QBrush,
    QPen
)
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
    QGraphicsView,
    QGraphicsScene,
    QGraphicsWidget,
    QGraphicsItem
)
from alicetool.editor.services.api import EditorAPI
import alicetool.editor.resources.rc_icons

class StateWidget(QWidget):
    __TITLE_HEIGHT = 15
    __START_WIDTH = 150
    def __init__(self, content: str, name: str, id :int, parent = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__title = QLabel(name, self)
        font = self.__title.font()
        font.setWeight(QFont.Weight.ExtraBold)
        self.__title.setFont(font)
        self.__title.setFixedHeight(StateWidget.__TITLE_HEIGHT)
        self.__close_btn = QPushButton(str(id), self)
        self.__close_btn.setFlat(True)
        self.__close_btn.setStyleSheet(
            "QPushButton"
            "{"
            "   background-color: #666666;"
            "   border: 0px; color: #FFFFFF;"
            "   border-radius: 7px;"
            "}"
        )
        font = self.__close_btn.font()
        font.setWeight(QFont.Weight.ExtraBold)
        self.__close_btn.setFont(font)
        self.__close_btn.setFixedHeight(StateWidget.__TITLE_HEIGHT)
        self.__close_btn.setFixedWidth(StateWidget.__TITLE_HEIGHT)
        
        self.__content = QTextEdit(content, self)
        self.__content.setStyleSheet(
            "QTextEdit{"
            "   border: 0px;"
            "   border-top: 1px solid #59A5FF;"
            "   border-bottom-right-radius: 10px;"
            "   border-bottom-left-radius: 10px;"
            "   background-color: #FFFFFF;"
            "}"
        )

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        title = QWidget(self)
        title.setStyleSheet(
            "QWidget{"
            "   border: 0px;"
            "   border-top-right-radius: 10px;"
            "   border-top-left-radius: 10px;"
            "   background-color: #FFFFFF;"
            "}"
        )
        title_lay = QHBoxLayout(title)
        title_lay.setContentsMargins(5,2,2,2)

        title_lay.addWidget(self.__title)
        title_lay.addWidget(self.__close_btn)
        
        main_lay.addWidget(title)
        main_lay.addWidget(self.__content)

        self.resize(StateWidget.__START_WIDTH, StateWidget.__START_WIDTH)

class Editor(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QColor("#DDDDDD"))

    def addState(self, content:str, name:str, id:int, initPos:QPoint) -> QGraphicsItem:
        widget = StateWidget(content, name, id)
        
        proxyControl = self.addRect(
            initPos.x(), initPos.y(),
            widget.width(), 20,
            QPen(Qt.GlobalColor.transparent),
            QBrush(Qt.GlobalColor.transparent)
        )
        proxyControl.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        proxyControl.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        proxy = self.addWidget(widget)
        proxy.setPos(initPos.x(), initPos.y())
        proxy.setParentItem(proxyControl)
        proxy.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent, True)

        return

class StateMachineQtController:
    __START_SIZE = QRect(0, 0, 2000, 2000)

    def __init__(self, id, proj_ctrl, flow_list):
        self.__proj_id = id
        self.__proj_ctrl: ProjectQtController = proj_ctrl
        self.__flow_list: FlowList = flow_list

        self.__scene = Editor()
        self.__proj_ctrl.editor().setScene(self.__scene)
        
        self.__build_editor()
        self.__build_flows()

    def project_controller(self):
        return self.__proj_ctrl

    def __build_editor(self):
        self.__scene.setSceneRect(StateMachineQtController.__START_SIZE)
        data = EditorAPI.instance().get_all_project_states(self.__proj_id)
        for state_id in data.keys():
            self.__scene.addState(
                data[state_id]['content'],
                data[state_id]['name'],
                state_id,
                QPoint(160 * (state_id - 1) + 10, 10)
            )

        self.__states: dict[int, QGraphicsWidget] = []

    def __build_flows(self):
        self.__flows: dict[int, QWidget] = []

class ProjectQtController:
    def __init__(self, id, flow_list):
        self.__proj_id = id
        self.__flow_list: FlowList = flow_list
        self.__editor = QGraphicsView()
        self.__editor.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def editor(self) -> QGraphicsView:
        return self.__editor

class FlowList(QScrollArea):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

class Workspaces(QTabWidget):
    def __init__(self, flow_list:FlowList, parent: QWidget = None):
        super().__init__(parent)
        self.__opened_projects: dict[int, StateMachineQtController] = {}
        self.__flow_list: FlowList = flow_list

    def add_project(self, id :int, data: dict) -> StateMachineQtController:
        if id in self.__opened_projects.keys():
            return self.__opened_projects[id]
        
        if 'name' in data.keys() and data['name']:
            tab_name = str(data['name'])
        elif 'db_name' in data.keys() and data['db_name']:
            tab_name = str(data['db_name'])
        elif 'id' in data.keys() and data['id']:
            tab_name = str(data['id'])
        elif 'file_path' in data.keys() and data['file_path']:
            tab_name = str(data['file_path'])
        else:
            raise RuntimeError(data)
        
        p_ctrl = ProjectQtController(id, self.__flow_list)
        c_ctrl = StateMachineQtController(id, p_ctrl, self.__flow_list)
        self.__opened_projects[id] = c_ctrl
        self.addTab(p_ctrl.editor(), tab_name)

        return c_ctrl

    def set_active_project(self, id: int):
        self.setCurrentWidget(
            self.__opened_projects[id].project_controller().editor()
        )
        

    def close_project(self, id: int):
        ...

    def project(self, id: int):
        ...

class MainWindow(QMainWindow):
    __oldPos = None

    def __init__(self, flow_list: FlowList, workspaces: Workspaces, parent: QWidget = None):
        super().__init__(None, Qt.WindowType.FramelessWindowHint)

        self.__flow_list = flow_list
        self.__workspaces = workspaces

        self.__setup_ui()
        self.__setup_toolbar()
        self.show()

    def __make_project(self):
        dialog = NewProjectDialog(self)
        dialog.exec()

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

    def __setup_ui(self):
        self.setCentralWidget(QWidget(self))

        main_lay = QVBoxLayout(self.centralWidget())
        main_lay.setContentsMargins(0,0,0,0)

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
        main_splitter.addWidget(self.__flow_list)
        main_splitter.addWidget(self.__workspaces)
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

class PathValidator(QValidator):
    def init(self):
        super().__init__()

class NewProjectDialog(QDialog):
    def new_project(self):
        self.proj_id = EditorAPI.instance().create_project(
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
            f'hello={self.__hello_editor.toPlainText()[: EditorAPI.instance().STATE_TEXT_MAX_LEN]}; '
            f'help={self.__help_editor.toPlainText()[: EditorAPI.instance().STATE_TEXT_MAX_LEN]}; '
            f'info={self.__info_editor.toPlainText()[: EditorAPI.instance().STATE_TEXT_MAX_LEN]}'
        )