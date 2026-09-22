from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

from breezewidget import (
    BodyLabel,
    BreezeIcon,
    BreezeThemeSwitch,
    BreezeWindow,
    CardWidget,
    InfoBar,
    NavigationItemPosition,
    PrimaryPushButton,
    SubtitleLabel,
    Theme,
    setTheme,
    setThemeColor,
)

PAGE_MARGIN = 4
PANEL_MARGIN = 16


class SchoolInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("schools")

        root = QVBoxLayout(self)
        root.setContentsMargins(PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN)
        root.setSpacing(0)

        panel = CardWidget(self)
        panel.setObjectName("schoolInfoPanel")
        root.addWidget(panel, 1)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(PANEL_MARGIN, PANEL_MARGIN, PANEL_MARGIN, PANEL_MARGIN)
        panel_layout.setSpacing(24)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)

        title = SubtitleLabel("Schulinformationen", panel)
        title.setWordWrap(False)
        header.addWidget(title)
        header.addStretch(1)

        add_button = PrimaryPushButton("Neue Schule anlegen", panel, BreezeIcon.ADD)
        add_button.clicked.connect(
            lambda: InfoBar.info("Schule", "Hier wuerde der Dialog zum Anlegen einer Schule starten.", self)
        )
        header.addWidget(add_button)

        empty_text = BodyLabel("Noch keine Schule vorhanden. Klicke auf 'Neue Schule anlegen'.", panel)
        empty_text.setWordWrap(False)

        panel_layout.addLayout(header)
        panel_layout.addWidget(empty_text)
        panel_layout.addStretch(1)


class PlaceholderPage(QWidget):
    def __init__(self, route: str, title: str):
        super().__init__()
        self.setObjectName(route)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN)
        layout.setSpacing(0)

        panel = CardWidget(self)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(PANEL_MARGIN, PANEL_MARGIN, PANEL_MARGIN, PANEL_MARGIN)
        panel_layout.addWidget(SubtitleLabel(title, panel))
        panel_layout.addWidget(BodyLabel("Diese Ansicht ist ein Platzhalter fuer die Demo.", panel))
        panel_layout.addStretch(1)
        layout.addWidget(panel, 1)


def main() -> int:
    app = QApplication(sys.argv)
    setTheme(Theme.DARK, app)
    setThemeColor("#11d9f3", app)

    window = BreezeWindow()
    window.setWindowTitle("Klassenpult")
    window.setTitleBarIcon(BreezeIcon.DOCUMENT)
    window.enableNavigationMenuButton(True)
    window.titleBar.addWidget(BreezeThemeSwitch(window.titleBar))

    window.setNavigationCompact(True)
    window.addSubInterface(SchoolInfoPage(), BreezeIcon.HOME, "Schulinformationen")
    window.addSubInterface(PlaceholderPage("people", "Klassen"), BreezeIcon.PEOPLE, "Klassen")
    window.addSubInterface(PlaceholderPage("documents", "Stundenplan"), BreezeIcon.DOCUMENT, "Stundenplan")
    window.addSubInterface(PlaceholderPage("calendar", "Kalender"), BreezeIcon.CALENDAR, "Kalender")
    window.addSubInterface(PlaceholderPage("notes", "Notizen"), BreezeIcon.EDIT, "Notizen")
    window.addSubInterface(PlaceholderPage("import", "Import"), BreezeIcon.DOWNLOAD, "Import")
    window.addSubInterface(
        PlaceholderPage("settings", "Einstellungen"),
        BreezeIcon.SETTINGS,
        "Einstellungen",
        position=NavigationItemPosition.BOTTOM,
    )

    window.resize(1100, 900)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
