if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    from iiconstructor_storages import *
    from iiconstructor_storages.inmemory_plugin import InmemoryStorageFakePlugin
    from iiconstructor_storages.presentation_qt import MainWindow

    if sys.platform in ("windows", "win32", "win64"):
        sys.argv += ["-platform", "windows:darkmode=0"]
    elif sys.platform == "darwin":
        sys.argv += ["-platform", "cocoa:darkmode=0"]

    app = QApplication(sys.argv)
    app.setOrganizationName("ii_constructor")
    app.setApplicationName("data_connections_qt_manager")

    main_window = MainWindow(StorageConnectionsController(set([InmemoryStorageFakePlugin])))
    main_window.show()
    app.exec()
