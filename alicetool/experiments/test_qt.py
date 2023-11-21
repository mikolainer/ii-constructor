import pytest

from PySide6 import QtCore

from .sandbox import DialogForTesting


@pytest.fixture
def app(qtbot):
    test_hello_app = DialogForTesting()
    qtbot.addWidget(test_hello_app)

    return test_hello_app

def test_lineedit(app, qtbot):
    qtbot.keyClicks(app.test_getIO()['lol_editor'], "Changed")
    assert app.test_getIO()['lol_editor'].text() == "Changed"