# Этот файл — часть "Конструктора интерактивных инструкций".
# 
# Конструктор интерактивных инструкций — свободная программа: 
# вы можете перераспространять ее и/или изменять ее на условиях 
# Стандартной общественной лицензии GNU в том виде, 
# в каком она была опубликована Фондом свободного программного обеспечения;
# либо версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.
# Конструктор интерактивных инструкций распространяется в надежде,
# что она будет полезной, но БЕЗО ВСЯКИХ ГАРАНТИЙ; 
# даже без неявной гарантии ТОВАРНОГО ВИДА
# или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. 
# Подробнее см. в Стандартной общественной лицензии GNU.
# 
# Вы должны были получить копию Стандартной общественной лицензии GNU
# вместе с этой программой. Если это не так,
# см. <https://www.gnu.org/licenses/>.



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
    QLayoutItem,
)

class MainToolButton(QPushButton):
    ''' Кнопка туллбара главного окна '''
    tool_tip : str
    status_tip : str
    whats_this : str
    icon : Optional[QIcon]
    icon_size : QSize

    __size : QSize
    #__style : str

    def __init__(self, text: str, icon: Optional[QWidget] = None, parent: Optional[QWidget] = None):
        super().__init__(icon, '', parent)

        self.__size = QSize(64, 64)
        #self.__style = "background-color: #59A5FF; border-radius:32px;"

        self.icon = icon
        self.tool_tip = text
        self.status_tip = text
        self.whats_this = text
        self.icon_size = self.__size
        self.apply_options()

    def apply_options(self):
        ''' Применяет значения указанные в публичных атрибутах класса '''
        self.setToolTip(self.tool_tip)
        self.setStatusTip(self.status_tip)
        self.setWhatsThis(self.whats_this)
        self.setFixedSize(self.__size)
        if not self.icon is None:
            self.setIcon(self.icon)
        self.setIconSize(self.icon_size)

class MainWindow(QMainWindow):
    ''' Главное окно клиента работы над сценариями '''
    __oldPos: QPoint | None
    __tool_bar: QWidget
    __flow_list: QWidget
    __workspaces: QTabWidget
    __close_btn: MainToolButton

    def __init__(self, flow_list: QWidget, workspaces: QTabWidget, parent: QWidget = None):
        super().__init__(None, Qt.WindowType.FramelessWindowHint)

        self.__oldPos = None
        self.__flow_list = flow_list
        self.__workspaces = workspaces

        flow_list.setParent(self)
        workspaces.setParent(self)

        self.__setup_ui()
        self.__setup_toolbar()

        self.show()

    def set_only_editor_enabled(self, only_editor: bool):
        toolbar_layout: QHBoxLayout = self.__tool_bar.layout()
        for index in range(toolbar_layout.count()):
            item: QLayoutItem = toolbar_layout.itemAt(index)
            btn = item.widget()
            if isinstance(btn, MainToolButton):
                btn.setEnabled(not only_editor)

        self.__flow_list.setEnabled(not only_editor)
        self.__workspaces.tabBar().setEnabled(not only_editor)

        self.__close_btn.setEnabled(True)


    def insert_button(self, btn: MainToolButton, index: int = 0):
        ''' Добавляет кнопку в туллбар '''
        layout: QHBoxLayout = self.__tool_bar.layout()
        layout.insertWidget(index, btn)

    def __setup_ui(self):
        self.setCentralWidget(QWidget(self))

        main_lay = QVBoxLayout(self.centralWidget())
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        self.__tool_bar = QWidget(self)
        self.__tool_bar.setProperty("isWindowTitle", True)
        self.__tool_bar.setMinimumHeight(64)
        main_lay.addWidget(self.__tool_bar, 0)

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
        layout: QHBoxLayout = self.__tool_bar.layout()

        # добавление крестика
        layout.addSpacerItem(
            QSpacerItem( 0,0,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum
            )
        )

        self.__close_btn = MainToolButton('Выйти', QIcon(":/icons/exit_norm.svg"), self)
        self.__close_btn.setObjectName("Close")
        
        self.__close_btn.status_tip = 'Закрыть программу'
        self.__close_btn.whats_this = 'Кнопка завершения программы'
        self.__close_btn.icon_size = self.__close_btn.icon_size * 0.6
        self.__close_btn.apply_options()
        self.__close_btn.clicked.connect(lambda: self.close())     
        layout.addWidget(self.__close_btn)

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
        self.__STATE_TEXT_MAX_LEN = STATE_TEXT_MAX_LEN
        
        super().__init__(parent)
        self.setWindowTitle("Новый проект")
        lay = QVBoxLayout(self)
        
        self.__name_editor = QLineEdit(self)
        self.__description_editor = QTextEdit(self)
        self.__ok_button = QPushButton("Начать", self)

        lay.addWidget(QLabel('Название'))
        lay.addWidget(self.__name_editor)
        lay.addWidget(QLabel('Описание'))
        lay.addWidget(self.__description_editor)

        lay.addWidget(self.__ok_button)
        self.__ok_button.clicked.connect(lambda: self.accept())

    def name(self) -> str:
        return self.__name_editor.text()
    
    def description(self) -> str:
        return self.__description_editor.toPlainText()

    
class Workspaces(QTabWidget):
    ''' Область графической сцены сценариев и выбора активного проекта (правая часть главного окна) '''
    #activated = Signal(int)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        #self.currentChanged.connect(lambda index: self.activated.emit(index))

class FlowList(QStackedWidget):
    ''' Содержание активного проекта. (левая часть главного окна) '''
    __indexed: dict[int, QWidget]
    __empty_index:int

    def addWidget(self, w: QWidget = None) -> int:
        area = QScrollArea(self)
        area.setWidgetResizable(True)
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
            