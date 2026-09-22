import pytest
from PySide6.QtWidgets import QWidget, QLabel, QDialog
from breezewidget.dialogs import Dialog, MaskedDialog


@pytest.mark.parametrize("cls", [Dialog, MaskedDialog])
def test_dialog_content_and_actions_keep_same_contract(qapp, qtbot, cls):
    parent = QWidget()
    qtbot.addWidget(parent)
    dialog = cls("Title", "Body", parent)
    qtbot.addWidget(dialog)
    dialog.setTitle("New")
    dialog.setContentText("Details")
    dialog.setYesText("Proceed")
    dialog.setCancelText("Back")
    assert dialog.windowTitle() == dialog.titleLabel.text() == "New"
    assert dialog.contentLabel.text() == "Details"
    assert dialog.yesButton.text() == "Proceed"
    assert dialog.cancelButton.text() == "Back"
    child = QLabel("Extra")
    dialog.addContentWidget(child)
    assert dialog.viewLayout.indexOf(child) >= 0
    dialog.yesButton.click()
    assert dialog.result() == QDialog.Accepted
    dialog.cancelButton.click()
    assert dialog.result() == QDialog.Rejected
