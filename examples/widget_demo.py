"""BreezeWidget gallery demo — entry point.

Run with::

    python examples/widget_demo.py

Each navigation entry maps to its own page module under
:mod:`examples.widget_demo_pages` so the demo stays browsable.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Make ``widget_demo_pages`` importable when the file is executed directly
# (``python examples/widget_demo.py``) as well as when ``examples`` itself
# is on ``sys.path``.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from breezewidget import (
    BreezeIcon,
    BreezeWindow,
    NavigationItemPosition,
    Theme,
    setTheme,
    setThemeColor,
)
from widget_demo_pages import (
    AnimationsDemoPage,
    CalenderViewDemoPage,
    CardsDemoPage,
    DateTimeDemoPage,
    DialogsDemoPage,
    DialogsFlyoutsDemoPage,
    InfrastructureDemoPage,
    MediaDemoPage,
    MenusDemoPage,
    NavigationDemoPage,
    PickersDemoPage,
    StatusDemoPage,
    ViewsDemoPage,
    WidgetDemoPage,
    WindowsDemoPage,
)


def main() -> int:
    app = QApplication(sys.argv)
    setTheme(Theme.DARK, app)
    setThemeColor("#11d9f3", app)

    window = BreezeWindow()
    window.setWindowTitle("BreezeWidget Demo")
    window.setTitleBarIcon(BreezeIcon.SETTINGS)
    window.enableNavigationMenuButton(True)
    window.addSubInterface(WidgetDemoPage(), BreezeIcon.CHECK, "Basic input")
    window.addSubInterface(DateTimeDemoPage(), BreezeIcon.CALENDAR, "Date & time")
    window.addSubInterface(CalenderViewDemoPage(), BreezeIcon.CALENDAR, "Calender_view")
    window.addSubInterface(PickersDemoPage(), BreezeIcon.CALENDAR, "Pickers")
    window.addSubInterface(DialogsFlyoutsDemoPage(), BreezeIcon.INFO, "Flyouts")
    window.addSubInterface(DialogsDemoPage(), BreezeIcon.INFO, "Dialogs")
    window.addSubInterface(MenusDemoPage(), BreezeIcon.MENU, "Menus")
    window.addSubInterface(NavigationDemoPage(), BreezeIcon.MENU, "Navigation")
    window.addSubInterface(CardsDemoPage(), BreezeIcon.DOCUMENT, "Cards & settings")
    window.addSubInterface(ViewsDemoPage(), BreezeIcon.PEOPLE, "Data views")
    window.addSubInterface(MediaDemoPage(), BreezeIcon.NEXT, "Media")
    window.addSubInterface(InfrastructureDemoPage(), BreezeIcon.SETTINGS, "Infrastructure")
    window.addSubInterface(AnimationsDemoPage(), BreezeIcon.NEXT, "Animations")
    window.addSubInterface(WindowsDemoPage(), BreezeIcon.HOME, "Windows", position=NavigationItemPosition.BOTTOM)
    window.addSubInterface(StatusDemoPage(), BreezeIcon.WARNING, "Status & info", position=NavigationItemPosition.BOTTOM)
    window.resize(1180, 780)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
