"""Menus (4c) — RoundMenu, CheckableMenu, CommandBar."""
from __future__ import annotations

from breezewidget import (
    BreezeIcon,
    CheckableMenu,
    CommandBar,
    PushButton,
    RoundMenu,
)

from ._gallery import GalleryPage


class MenusDemoPage(GalleryPage):
    """Phase 4c — RoundMenu, CheckableMenu, CommandBar."""

    def __init__(self):
        super().__init__("Menus", "breezewidget.menu", "menus")

        # RoundMenu on a button.
        round_button = PushButton("Open RoundMenu")
        round_menu = RoundMenu("File", round_button)
        round_menu.addBreezeAction(BreezeIcon.SAVE, "Save")
        round_menu.addBreezeAction(BreezeIcon.DOWNLOAD, "Download")
        round_menu.addSeparator()
        round_menu.addBreezeAction(BreezeIcon.DELETE, "Delete")
        round_button.clicked.connect(
            lambda: round_menu.exec(round_button.mapToGlobal(round_button.rect().bottomLeft()))
        )
        self.addExample("RoundMenu — frameless context menu with rounded items", round_button)

        # CheckableMenu with exclusive group.
        check_button = PushButton("Open CheckableMenu")
        check_menu = CheckableMenu("View", check_button)
        a_left = check_menu.addCheckableAction(None, "Align left")
        a_center = check_menu.addCheckableAction(None, "Align center", checked=True)
        a_right = check_menu.addCheckableAction(None, "Align right")
        check_menu.addExclusiveActions([a_left, a_center, a_right])
        check_menu.addSeparator()
        check_menu.addCheckableAction(None, "Show grid", checked=True)
        check_button.clicked.connect(
            lambda: check_menu.exec(check_button.mapToGlobal(check_button.rect().bottomLeft()))
        )
        self.addExample("CheckableMenu — exclusive group + plain checkable items", check_button)

        # CommandBar with auto-overflow.
        bar = CommandBar()
        for icon, text in (
            (BreezeIcon.ADD, "Add"),
            (BreezeIcon.EDIT, "Edit"),
            (BreezeIcon.DELETE, "Delete"),
            (BreezeIcon.SAVE, "Save"),
            (BreezeIcon.DOWNLOAD, "Download"),
            (BreezeIcon.SEARCH, "Search"),
        ):
            bar.addAction(icon, text)
        bar.addSeparator()
        bar.addAction(BreezeIcon.SETTINGS, "Settings")
        self.addExample("CommandBar — toolbar with auto-overflow into a RoundMenu", bar)

        self.finish()
