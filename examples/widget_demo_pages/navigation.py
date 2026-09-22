"""Navigation — Pivot, SegmentedWidget, BreadcrumbBar, TabBar."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget

from breezewidget import BreadcrumbBar, Pivot, SegmentedWidget, TabBar

from ._gallery import GalleryPage, _row


class NavigationDemoPage(GalleryPage):
    """Phase-3c showcase: Pivot, SegmentedWidget, BreadcrumbBar, TabBar."""

    def __init__(self):
        super().__init__("Navigation", "breezewidget.navigation", "phase3c-navigation")
        self.addExample("A simple Pivot", self._pivotPreview())
        self.addExample("A SegmentedWidget for modes", self._segmentedPreview())
        self.addExample("A BreadcrumbBar with truncation", self._breadcrumbPreview())
        self.addExample("A closable TabBar", self._tabBarPreview())
        self.setStatus("Navigation bereit")
        self.finish()

    def _pivotPreview(self) -> QWidget:
        pivot = Pivot()
        for label, key in (("Uebersicht", "overview"), ("Statistik", "stats"), ("Einstellungen", "settings")):
            pivot.addItem(label, key)
        pivot.currentChanged.connect(lambda key: self.setStatus(f"Pivot: {key}"))
        return _row(pivot)

    def _segmentedPreview(self) -> QWidget:
        seg = SegmentedWidget()
        for label, key in (("Tag", "day"), ("Woche", "week"), ("Monat", "month")):
            seg.addItem(label, key)
        seg.currentChanged.connect(lambda key: self.setStatus(f"SegmentedWidget: {key}"))
        return _row(seg)

    def _breadcrumbPreview(self) -> QWidget:
        bar = BreadcrumbBar()
        bar.addItem("Home", "home")
        bar.addItem("Dokumente", "docs")
        bar.addItem("Bericht.docx", "report")
        bar.currentChanged.connect(lambda key: self.setStatus(f"BreadcrumbBar: {key}"))
        return _row(bar)

    def _tabBarPreview(self) -> QWidget:
        tabs = TabBar()
        for label, key in (("Datei A", "a"), ("Datei B", "b"), ("Datei C", "c")):
            tabs.addTab(label, key)
        tabs.tabCloseRequested.connect(tabs.removeTab)
        tabs.currentChanged.connect(lambda key: self.setStatus(f"TabBar: {key}"))
        return _row(tabs)
