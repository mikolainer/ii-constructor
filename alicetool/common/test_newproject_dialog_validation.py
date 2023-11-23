import os
import pytest

import PySide6
from PySide6 import QtCore
from PySide6.QtTest import QTest

from .gui import NewProjectDialog

@pytest.fixture
def dialog(qtbot) -> NewProjectDialog:
    widget = NewProjectDialog()
    qtbot.addWidget(widget)
    return widget

def test_iovalidation_path(dialog: NewProjectDialog, qtbot):
    editor = dialog.test_get_io()['редактор пути к файлу']

    input = './folder/simple_name.something'
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.text() == expected
    editor.clear()



def test_iovalidation_name(dialog: NewProjectDialog, qtbot):
    editor = dialog.test_get_io()['редактор имени']

    input = 'some_name'
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.text() == expected
    editor.clear()

    input = 'some name'
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.text() == expected
    editor.clear()

    input1 = 'some'
    input2 = 'name'
    expected = 'somename'
    qtbot.keyClicks(editor, input1)
    qtbot.keyPress(editor, QtCore.Qt.Key.Key_Enter)
    qtbot.keyClicks(editor, input2)
    assert editor.text() == expected
    editor.clear()

    # input = 'имя_навыка'
    # expected = input
    # qtbot.keyClicks(editor, input)
    # assert editor.text() == expected
    # editor.clear()

    # input = 'имя навыка'
    # expected = input
    # qtbot.sendKeyEvent()
    # qtbot.keyClicks(editor, input)
    # assert editor.text() == expected
    # editor.clear()

    input = '123'
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.text() == expected
    editor.clear()

    input = '!@#$%^&*()_+'
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.text() == expected
    editor.clear()



def test_iovalidation_dbname(dialog: NewProjectDialog, qtbot):
    editor = dialog.test_get_io()['редактор имени для БД']

    input = '!@#$%^&*()_+1234567890-=asdASD'
    expected = '_1234567890asdASD'
    qtbot.keyClicks(editor, input)
    assert editor.text() == expected
    editor.clear()

    input = 'someName'
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.text() == expected
    editor.clear()

    # input = 'только_латинские буквы (A-Z, a-z) и цифры (0-9)'
    # expected = 'AZaz09'
    # qtbot.keyClicks(editor, input)
    # assert editor.text() == expected
    # editor.clear()


def test_iovalidation_hello(dialog: NewProjectDialog, qtbot):
    editor = dialog.test_get_io()['редактор приветственной фразы']

    input = "hello phrase of the skill for Alice"
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.toPlainText() == expected
    editor.clear()



def test_iovalidation_help(dialog: NewProjectDialog, qtbot):
    editor = dialog.test_get_io()['редактор ответа "Помощь"']

    input = "hello phrase of the skill for Alice"
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.toPlainText() == expected
    editor.clear()

    # 1024 символа
    input = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent lupta'
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.toPlainText() == expected
    editor.clear()

    # 1024 символа
    input1 = 'Lorem ipsum dolor sit amet, consectetuer'
    input2 = ('adipiscing elit, sed diam nonummy nibh '
    'euismod tincidunt ut laoreet dolore magna aliquam '
    'erat volutpat. Ut wisi enim ad minim veniam, quis '
    'nostrud exerci tation ullamcorper suscipit lobortis '
    'nisl ut aliquip ex ea commodo consequat. '
    'Duis autem vel eum iriure dolor in hendrerit in vulputate '
    'velit esse molestie consequat, vel illum dolore eu feugiat '
    'nulla facilisis at vero eros et accumsan et iusto odio dignissim '
    'qui blandit praesent luptatum zzril delenit augue duis dolore te '
    'feugait nulla facilisi.Lorem ipsum dolor sit amet, consectetuer '
    'adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet '
    'dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, '
    'quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut '
    'aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor '
    'in hendrerit in vulputate velit esse molestie consequat, vel illum '
    'dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto '
    'odio dignissim qui blandit praesent lupta')
    expected = '\n'.join([input1, input2])
    qtbot.keyClicks(editor, input1)
    qtbot.keyPress(editor, QtCore.Qt.Key.Key_Enter)
    qtbot.keyClicks(editor, input2)
    assert editor.toPlainText() == expected
    editor.clear()



def test_iovalidation_info(dialog: NewProjectDialog, qtbot):
    editor = dialog.test_get_io()['редактор ответа "Что ты умеешь?"']

    input = "hello phrase of the skill for Alice"
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.toPlainText() == expected
    editor.clear()

    # 1024 символа
    input = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent lupta'
    expected = input
    qtbot.keyClicks(editor, input)
    assert editor.toPlainText() == expected
    editor.clear()

    # 1024 символа
    input1 = 'Lorem ipsum dolor sit amet, consectetuer'
    input2 = 'adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi.Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent lupta'
    expected = '\n'.join([input1, input2])
    qtbot.keyClicks(editor, input1)
    qtbot.keyPress(editor, QtCore.Qt.Key.Key_Enter)
    qtbot.keyClicks(editor, input2)
    assert editor.toPlainText() == expected
    editor.clear()