'''
автоматические тесты для создания файла с новым проектом
https://app.qase.io/case/YALE-3
https://app.qase.io/case/YALE-4
'''

import os
import pytest

import PySide6
from PySide6 import QtCore
from PySide6.QtWidgets import QPushButton, QLineEdit, QTextEdit, QDialog

from alicetool.editor.infrastructure.gui import NewProjectDialog

FILENAME:str = 'azaza.aliceproj'
TOOLTIP_WARNING_PATHEXISTS = 'Файл существует. Продолжение приведёт к удалению исходного файла!'
INPUT_DEFAULT = 'Test123'
OLDFILE_TEST_CONTENT = 'test\n'

@pytest.fixture
def dialog(qtbot) -> NewProjectDialog:
    widget = NewProjectDialog()
    qtbot.addWidget(widget)
    return widget

@pytest.mark.skip(reason="пока забили на автотестирование гуя")
def test_YALE_3(dialog: NewProjectDialog, qtbot):
    '''
    Создание нового файла проекта
    https://app.qase.io/case/YALE-3
    '''

    # 0 (предусловия)
    assert os.path.exists(FILENAME) == False

    # 1
    # TODO: нажание на кнопку в тулбаре
    assert dialog.windowTitle() == 'Новый сценарий'
    btn:QPushButton = dialog.test_get_io()['кнопка "Начать"']
    assert btn.text('Начать')
    assert btn.isVisible()
    assert btn.isEnabled()

    # 2
    path_editor:QLineEdit = dialog.test_get_io()['редактор пути к файлу']
    assert path_editor.statusTip() == 'редактор пути к файлу'
    assert path_editor.toolTip() != TOOLTIP_WARNING_PATHEXISTS
    qtbot.keyClicks(path_editor, FILENAME)
    assert path_editor.text() == FILENAME
    assert path_editor.toolTip() != TOOLTIP_WARNING_PATHEXISTS

    # 3
    for key, editor in dialog.test_get_io().items():
        if key in ['редактор пути к файлу', 'кнопка "Начать"', 'диалог подтверждения перезаписи']:
            continue

        assert path_editor.statusTip() == key
        qtbot.keyClicks(editor, INPUT_DEFAULT)
        
        if type(editor) is QLineEdit:
            assert editor.text() == INPUT_DEFAULT
        elif type(editor) is QTextEdit:
            assert editor.toPlainText() == INPUT_DEFAULT
    
    assert btn.isVisible()
    assert btn.isEnabled()

    # 4
    qtbot.mouseClick(btn, QtCore.Qt.MouseButton.LeftButton)
    qtbot.waitSignal((dialog.accepted, 'кнопка "Начать"'))
    assert os.path.exists(FILENAME) == True

    # очистка после теста
    os.remove(FILENAME)


@pytest.mark.skip(reason="пока забили на автотестирование гуя")
def test_YALE_4(dialog: NewProjectDialog, qtbot):
    '''
    Создание файла проекта вместо существующего
    https://app.qase.io/case/YALE-4
    '''
    # 0 (предусловия)
    assert os.path.exists(FILENAME) == False
    with open(FILENAME, 'w', encoding="utf-8") as f:
        f.write(OLDFILE_TEST_CONTENT)
    assert os.path.exists(FILENAME) == True

    # 1
    # TODO: нажание на кнопку в тулбаре
    assert dialog.windowTitle() == 'Новый сценарий'
    btn:QPushButton = dialog.test_get_io()['кнопка "Начать"']
    assert btn.text('Начать')
    assert btn.isVisible()
    assert btn.isEnabled()

    # 2-3
    path_editor:QLineEdit = dialog.test_get_io()['редактор пути к файлу']
    assert path_editor.statusTip() == 'редактор пути к файлу'
    assert path_editor.toolTip() != TOOLTIP_WARNING_PATHEXISTS
    qtbot.keyClicks(path_editor, FILENAME)
    assert path_editor.text() == FILENAME
    assert path_editor.toolTip() == TOOLTIP_WARNING_PATHEXISTS

    # 4
    for key, editor in dialog.test_get_io().items():
        if key in ['редактор пути к файлу', 'кнопка "Начать"', 'диалог подтверждения перезаписи']:
            continue

        assert path_editor.statusTip() == key
        qtbot.keyClicks(editor, INPUT_DEFAULT)
        
        if type(editor) is QLineEdit:
            assert editor.text() == INPUT_DEFAULT
        elif type(editor) is QTextEdit:
            assert editor.toPlainText() == INPUT_DEFAULT
    
    assert btn.isVisible()
    assert btn.isEnabled()

    # 5-6
    qtbot.mouseClick(btn, QtCore.Qt.MouseButton.LeftButton)
    sure_dialog: dict[str, QPushButton] = dialog.test_get_io()['диалог подтверждения перезаписи']
    # TODO: ожидание открытия окна подтверждения перезаписи
    qtbot.mouseClick(sure_dialog['cancel'], QtCore.Qt.MouseButton.LeftButton)
    #qtbot.waitSignal((sure_dialog.close, 'подтверждение перезаписи старого файла'))
    
    # проверка целостности старого контента
    assert os.path.exists(FILENAME) == True
    with open(FILENAME, 'r', encoding="utf-8") as f:
        content = f.read()
    assert content == OLDFILE_TEST_CONTENT

    # 7-8
    qtbot.mouseClick(btn, QtCore.Qt.MouseButton.LeftButton)
    # TODO: ожидание открытия окна подтверждения перезаписи
    qtbot.mouseClick(sure_dialog['ok'], QtCore.Qt.MouseButton.LeftButton)
    #qtbot.waitSignal((dialog.close, 'подтверждение перезаписи старого файла'))

    # проверка обновления контента
    with open(FILENAME, 'r', encoding="utf-8") as f:
        content = f.read()
    assert content != OLDFILE_TEST_CONTENT

    # очистка после теста
    os.remove(FILENAME)