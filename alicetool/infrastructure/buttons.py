from typing import Optional, overload

from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize

class CloseButton(QPushButton):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setToolTip('Закрыть')
        self.setStatusTip('Закрыть')
        self.setWhatsThis('Закрыть')
        self.setIcon(QIcon(QPixmap(":/icons/exit_norm.svg").scaled(12,12)))
        size = QSize(20,20)
        self.setIconSize(size)
        self.setFixedSize(size)
        self.setStyleSheet("background-color: #FF3131; border: 0px; border-radius: 10px")

class MainToolButton(QPushButton):
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
        self.setToolTip(self.tool_tip)
        self.setStatusTip(self.status_tip)
        self.setWhatsThis(self.whats_this)
        self.setFixedSize(self.__size)
        self.setIcon(self.icon)
        self.setIconSize(self.icon_size)
        