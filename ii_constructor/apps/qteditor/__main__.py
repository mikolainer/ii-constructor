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


import sys

import resources.icons_rc  # noqa: F401 Для вызова функции инициализации иконок
import resources.styles_rc
from presentation import ProjectManager
from PySide6.QtCore import QFile, QIODevice, QTextStream
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    if sys.platform in ("windows", "win32", "win64"):
        sys.argv += ["-platform", "windows:darkmode=0"]
    elif sys.platform == "darwin":
        sys.argv += ["-platform", "cocoa:darkmode=0"]

    app = QApplication(sys.argv)
    app.setOrganizationName("ii_constructor")
    app.setApplicationName("scenario_editor")

    stream = QFile(":/styles/light.qss")
    stream.open(QIODevice.ReadOnly)
    app.setStyleSheet(QTextStream(stream).readAll())

    projects = ProjectManager()
    app.exec()
