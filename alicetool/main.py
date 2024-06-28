from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from alicetool.infrastructure.qtgui.main_w import MainWindow, Workspaces, FlowList, MainToolButton
from alicetool.presentation.editor.gui import ProjectManager, Project

def __setup_main_toolbar(main_window: MainWindow, project_manager: ProjectManager):
    btn = MainToolButton('Список синонимов', QIcon(":/icons/synonyms_list_norm.svg"), main_window)
    btn.status_tip = 'Открыть редактор синонимов'
    btn.whats_this = 'Кнопка открытия редактора синонимов'
    btn.apply_options()
    btn.clicked.connect(lambda: project_manager.current().edit_inputs())
    main_window.insert_button(btn)

    btn = MainToolButton('Опубликовать проект', QIcon(":/icons/export_proj_norm.svg"), main_window)
    btn.status_tip = 'Разместить проект в БД '
    btn.whats_this = 'Кнопка экспорта проекта в базу данных'
    btn.apply_options()
    main_window.insert_button(btn)

    btn = MainToolButton('Сохранить проект', QIcon(":/icons/save_proj_norm.svg"), main_window)
    btn.status_tip = 'Сохранить в файл'
    btn.whats_this = 'Кнопка сохранения проекта в файл'
    btn.apply_options()
    main_window.insert_button(btn)

    btn = MainToolButton('Открыть проект', QIcon(":/icons/open_proj_norm.svg"), main_window)
    btn.status_tip = 'Открыть файл проекта'
    btn.whats_this = 'Кнопка открытия проекта из файла'
    btn.apply_options()
    main_window.insert_button(btn)

    btn = MainToolButton('Новый проект', QIcon(":/icons/new_proj_norm.svg"), main_window)
    btn.status_tip = 'Создать новый проект'
    btn.whats_this = 'Кнопка создания нового проекта'
    btn.apply_options()
    btn.clicked.connect(lambda: project_manager.create_project())
    main_window.insert_button(btn)

if __name__ == "__main__":
    app = QApplication([])

    flow_list = FlowList()
    workspaces = Workspaces()
    main_win = MainWindow(flow_list, workspaces)

    projects = ProjectManager(flow_list, workspaces, main_win)
    __setup_main_toolbar(main_win, projects)

    app.exec()