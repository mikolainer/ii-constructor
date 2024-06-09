from typing import Optional, overload

from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtGui import QIcon, QPixmap, QEnterEvent, QMouseEvent
from PySide6.QtCore import QSize, Signal

class EnterDetectionButton(QPushButton):
    ''' QPushButton c сигналом mouse_enter() '''
    mouse_enter = Signal()

    def __init__(self, text:str, parent = None):
        super().__init__(text, parent)
        self.setMouseTracking(True)

    def enterEvent(self, event: QEnterEvent) -> None:
        if event.type() == QMouseEvent.Type.Enter:
            self.mouse_enter.emit()
        return super().enterEvent(event)
        
class CloseButton(QPushButton):
    ''' Стиллизованая кнопка "Закрыть" '''
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
