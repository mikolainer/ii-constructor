import sys
from typing import Callable
from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow,
    QWidget,
)

class OutputPluginSelectorWgt(QWidget):
    """Выбор типа ответа"""
    get_available_output_plugins_callback: Callable
    pick_output_plugin_callback: Callable

class StorageConnectorWgt(QWidget):
    """подключение к источнику данных"""
    connect_datasource_callback: Callable

class StorageSelectorWgt(QWidget):
    """выбор подключенного источника данных"""
    get_connected_datasources: Callable
    pick_datasource: Callable

class OutputStorageConstructorWgt(QWidget):
    """создание набора ответов"""
    make_outputs_storage: Callable

class OutputStorageSelectorWgt(QWidget):
    """управление существующими наборами ответов (подключение/отключение)"""
    connect_outputs_storage: Callable
    disconnect_outputs_storage: Callable

class OutputStorageEditorWgt(QWidget):
    """управление метаинформацией хранилища ответов"""
    edit_outputs_storage_name: Callable
    edit_outputs_storage_description: Callable

class OutputsManipulatorWgt(QWidget):
    """управление ответами в подключенных наборах(копирование/удаление/перемещение)"""

class OutputConstructorWgt(QWidget):
    """создание ответа"""

class OutputEditorWgt(QWidget):
    """изменение ответа"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget()

if __name__ == "__main__":
    if sys.platform in ("windows", "win32", "win64"):
        sys.argv += ["-platform", "windows:darkmode=0"]
    elif sys.platform == "darwin":
        sys.argv += ["-platform", "cocoa:darkmode=0"]

    app = QApplication(sys.argv)
    app.setOrganizationName("ii_constructor")
    app.setApplicationName("outputlibs_manager")

    main_window = MainWindow()
    main_window.show()

    app.exec()