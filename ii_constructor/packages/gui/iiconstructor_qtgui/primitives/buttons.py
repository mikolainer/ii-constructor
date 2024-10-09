# Copyright 2024 Николай Иванцов (tg/vk/wa: <@mikolainer> | <mikolainer@mail.ru>)
# Copyright 2024 Kirill Lesovoy
#
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


from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QEnterEvent, QIcon, QMouseEvent, QPixmap
from PySide6.QtWidgets import QPushButton, QToolButton, QWidget


class EnterDetectionButton(QToolButton):
    """QPushButton c сигналом mouse_enter()"""

    mouse_enter = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)

    def enterEvent(self, event: QEnterEvent) -> None:
        if event.type() == QMouseEvent.Type.Enter:
            self.mouse_enter.emit()
        return super().enterEvent(event)


class CloseButton(QPushButton):
    """Стиллизованая кнопка "Закрыть" """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setToolTip("Закрыть")
        self.setStatusTip("Закрыть")
        self.setWhatsThis("Закрыть")
        self.setIcon(QIcon(QPixmap(":/icons/exit_norm.svg").scaled(12, 12)))
        size = QSize(20, 20)
        self.setIconSize(size)
        self.setFixedSize(size)
