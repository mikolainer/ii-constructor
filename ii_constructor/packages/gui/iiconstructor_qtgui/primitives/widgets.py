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


from PySide6.QtCore import QCoreApplication, QSettings, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SynonymEditorWidget(QWidget):
    __edit: QLineEdit

    def __init__(self, value: str, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.__edit = QLineEdit(value, self)
        self.__edit.setProperty("SynonymEditor", True)
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self.__edit)


class AuthWidget(QWidget):
    __username_editor: QLineEdit
    __password_editor: QLineEdit
    __save_checkbox: QCheckBox

    apply = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        f: Qt.WindowType = Qt.WindowType.Widget,
    ) -> None:
        super().__init__(parent, f)
        settings = QSettings(
            QCoreApplication.organizationName(),
            QCoreApplication.applicationName(),
        )
        init_checkbox_state = settings.value("auth/save", False, bool)

        self.__username_editor = QLineEdit(self)
        self.__password_editor = QLineEdit(self)
        self.__password_editor.setEchoMode(QLineEdit.EchoMode.Password)
        self.__save_checkbox = QCheckBox("Сохранить пароль (в открытом виде)")
        self.__save_checkbox.setChecked(init_checkbox_state)
        self.__save_checkbox.toggled.connect(
            lambda checked: settings.setValue("auth/save", checked),
        )

        if init_checkbox_state:
            user = settings.value("auth/last_user")
            self.__username_editor.setText(user)
            self.__password_editor.setText(
                settings.value(f"auth/passwords/{user}"),
            )

        main_lay = QVBoxLayout(self)

        user_lay = QHBoxLayout(self)
        user_lay.addWidget(QLabel("Пользователь: ", self))
        user_lay.addWidget(self.__username_editor)
        main_lay.addLayout(user_lay)

        pwd_lay = QHBoxLayout(self)
        pwd_lay.addWidget(QLabel("Пароль: ", self))
        pwd_lay.addWidget(self.__password_editor)
        main_lay.addLayout(pwd_lay)

        main_lay.addWidget(self.__save_checkbox)

    def __del__(self):
        if self.__save_checkbox.isChecked():
            settings = QSettings(
                QCoreApplication.organizationName(),
                QCoreApplication.applicationName(),
            )
            settings.setValue(f"auth/passwords/{self.user()}", self.password())
            settings.setValue("auth/last_user", self.user())

    def user(self) -> str:
        return self.__username_editor.text()

    def password(self) -> str:
        return self.__password_editor.text()


class DBConnectWidget(QDialog):
    __ip: QLineEdit
    __port: QLineEdit
    __auth_wgt: AuthWidget

    def __init__(
        self,
        parent: QWidget | None = None,
        f: Qt.WindowType = Qt.WindowType.Dialog,
    ) -> None:
        super().__init__(parent, f)

        self.setWindowTitle("Подключение к БД")
        settings = QSettings(
            QCoreApplication.organizationName(),
            QCoreApplication.applicationName(),
        )

        self.__ip = QLineEdit(self)
        self.__ip.setText(settings.value("auth/last_ip", "", str))
        self.__port = QLineEdit(self)
        self.__port.setText(settings.value("auth/last_port", "", str))
        self.__auth_wgt = AuthWidget(self)
        ok_btn = QPushButton("Подключить", self)
        ok_btn.clicked.connect(lambda: self.accept())

        main_lay = QVBoxLayout(self)

        ip_lay = QHBoxLayout(self)
        ip_lay.addWidget(QLabel("ip: ", self))
        ip_lay.addWidget(self.__ip)
        main_lay.addLayout(ip_lay)

        port_lay = QHBoxLayout(self)
        port_lay.addWidget(QLabel("port: ", self))
        port_lay.addWidget(self.__port)
        main_lay.addLayout(port_lay)

        auth_group = QGroupBox("Авторизация", self)
        auth_group_lay = QVBoxLayout(auth_group)
        auth_group_lay.addWidget(self.__auth_wgt)
        main_lay.addWidget(auth_group)
        main_lay.addWidget(ok_btn)

    def accept(self) -> None:
        settings = QSettings(
            QCoreApplication.organizationName(),
            QCoreApplication.applicationName(),
        )
        settings.setValue("auth/last_ip", self.__ip.text())
        settings.setValue("auth/last_port", int(self.__port.text()))
        return super().accept()

    def data(self):
        return {
            "ip": self.__ip.text(),
            "port": int(self.__port.text()),
            "user": self.__auth_wgt.user(),
            "password": self.__auth_wgt.password(),
        }
