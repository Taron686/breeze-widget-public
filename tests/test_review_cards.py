from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QSignalSpy

from breezewidget import ExpandSettingCard, PushSettingCard


def test_card_body_click_emits_one_action(qtbot):
    card = PushSettingCard("Run")
    qtbot.addWidget(card)
    card.resize(450, 100)
    card.show()
    actions = QSignalSpy(card.actionClicked)
    qtbot.mouseClick(card, Qt.MouseButton.LeftButton, pos=QPoint(5, 5))
    assert actions.count() == 1


def test_expand_card_body_click_stays_expanded(qtbot):
    card = ExpandSettingCard(title="Details")
    qtbot.addWidget(card)
    card.resize(450, 100)
    card.show()
    changes = QSignalSpy(card.expandedChanged)
    qtbot.mouseClick(card, Qt.MouseButton.LeftButton, pos=QPoint(5, 5))
    assert card.isExpanded()
    assert changes.count() == 1
