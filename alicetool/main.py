from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from alicetool.presentation.api import EditorAPI
from alicetool.presentation.gui import MainWindow, FlowList, Workspaces, SynonymsEditor, NewProjectDialog
from alicetool.application.updates import EditorGuiRefresher
from alicetool.infrastructure.buttons import MainToolButton

def __make_project(main_window):
    dialog = NewProjectDialog(main_window)
    dialog.exec()

def __setup_main_toolbar(main_window):
    btn = MainToolButton('Список синонимов', QIcon(":/icons/synonyms_list_norm.svg"), main_window)
    btn.status_tip = 'Открыть редактор синонимов'
    btn.whats_this = 'Кнопка открытия редактора синонимов'
    btn.apply_options()
    btn.clicked.connect(lambda: synonyms.show())
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
    btn.clicked.connect(lambda: __make_project(main_window))
    main_window.insert_button(btn)

if __name__ == "__main__":
    app = QApplication([])

    synonyms = SynonymsEditor()
    flow_list = FlowList()
    workspaces = Workspaces()
    
    main_win = MainWindow(flow_list, workspaces)
    #synonyms.setParent(main_win)
    __setup_main_toolbar(main_win)

    set_sm_notifier = (
        lambda id, notifier:
            EditorAPI.instance().set_content_notifier(id, notifier)
    )
    main_changes_handler = EditorGuiRefresher(
        set_sm_notifier, flow_list, synonyms, workspaces, main_win
    )
    EditorAPI(main_changes_handler)

    app.exec()