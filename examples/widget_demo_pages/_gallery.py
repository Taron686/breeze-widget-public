"""Shared gallery building blocks for the widget demo pages."""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from breezewidget import (
    BodyLabel,
    BreezeIcon,
    BreezeThemeSwitch,
    PushButton,
    StrongBodyLabel,
    SmoothScrollArea,
    TransparentToolButton,
    ThemeManager,
    TitleLabel,
    ToolButton,
    getPalette,
)
from breezewidget.constants import PROP_WINDOW_CONTENT

PAGE_MARGIN = 4


class _GalleryPanel(QFrame):
    _RADIUS = 8

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("galleryPanelSurface")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("QFrame#galleryPanelSurface { background: transparent; border: none; }")

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), self._RADIUS, self._RADIUS)
        painter.fillPath(path, QColor(getPalette().surface2))
        painter.end()


class DemoExample(QWidget):
    """Gallery-style example block with a preview area and footer."""

    def __init__(
        self,
        title: str,
        preview: QWidget,
        source: str = "Source code",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._panel = QFrame(self)
        self._panel.setObjectName("demoExamplePanel")
        self._panel.setFrameShape(QFrame.Shape.NoFrame)
        self._panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._previewSurface = QFrame(self._panel)
        self._previewSurface.setObjectName("demoExamplePreview")
        self._previewSurface.setFrameShape(QFrame.Shape.NoFrame)
        self._previewSurface.setMinimumHeight(56)

        self._footer = QFrame(self._panel)
        self._footer.setObjectName("demoExampleFooter")
        self._footer.setFrameShape(QFrame.Shape.NoFrame)
        self._footer.setFixedHeight(54)

        preview_layout = QHBoxLayout(self._previewSurface)
        preview_layout.setContentsMargins(12, 12, 12, 12)
        preview_layout.setSpacing(10)
        preview_layout.addWidget(preview)

        footer_layout = QHBoxLayout(self._footer)
        footer_layout.setContentsMargins(18, 0, 12, 0)
        footer_layout.setSpacing(8)
        footer_layout.addWidget(BodyLabel(source, self._footer))
        footer_layout.addStretch(1)
        self._sourceButton = ToolButton(BreezeIcon.EXTERNAL_LINK, self._footer)
        self._sourceButton.setObjectName("demoExampleSourceButton")
        self._sourceButton.setFixedSize(30, 30)
        self._sourceButton.setIconSize(QSize(18, 18))
        self._sourceButton.setToolTip("Source code")
        footer_layout.addWidget(self._sourceButton)

        panel_layout = QVBoxLayout(self._panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        panel_layout.addWidget(self._previewSurface)
        panel_layout.addWidget(self._footer)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(StrongBodyLabel(title, self))
        layout.addWidget(self._panel)

        manager = ThemeManager.instance()
        manager.themeChanged.connect(self._refreshFromSignal)
        manager.themeColorChanged.connect(self._refreshFromSignal)
        self.refreshTheme()

    def refreshTheme(self) -> None:
        palette = getPalette()
        self._panel.setStyleSheet(
            "QFrame#demoExamplePanel { "
            f"background: {palette.surface2}; "
            f"border: 1px solid {palette.border1}; "
            "border-radius: 8px; "
            "}"
        )
        self._previewSurface.setStyleSheet(
            "QFrame#demoExamplePreview { "
            f"background: {palette.surface1}; "
            "border: none; "
            "border-top-left-radius: 8px; "
            "border-top-right-radius: 8px; "
            "}"
        )
        self._footer.setStyleSheet(
            "QFrame#demoExampleFooter { "
            f"background: {palette.surface3}; "
            "border: none; "
            "border-bottom-left-radius: 8px; "
            "border-bottom-right-radius: 8px; "
            "}"
        )
        self._sourceButton.setIcon(BreezeIcon.EXTERNAL_LINK)
        self._sourceButton.setStyleSheet(
            "QToolButton#demoExampleSourceButton { "
            f"background: {palette.surface2}; "
            f"border: 1px solid {palette.border1}; "
            "border-radius: 8px; "
            "padding: 0; "
            "}"
            "QToolButton#demoExampleSourceButton:hover { "
            f"background: {palette.surface4}; "
            "}"
            "QToolButton#demoExampleSourceButton:pressed { "
            f"background: {palette.surface5}; "
            "}"
        )

    def _refreshFromSignal(self, *_args) -> None:
        self.refreshTheme()


class GalleryPage(QWidget):
    """Base page that mirrors the structured Fluent-style component gallery."""

    def __init__(self, title: str, module_path: str, object_name: str):
        super().__init__()
        self.setObjectName(object_name)
        self.setProperty(PROP_WINDOW_CONTENT, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN)
        root.setSpacing(0)

        self._panel = _GalleryPanel(self)
        self._panel.setObjectName("galleryPagePanel")
        root.addWidget(self._panel, 1)

        panel_layout = QVBoxLayout(self._panel)
        panel_layout.setContentsMargins(1, 1, 1, 1)
        panel_layout.setSpacing(0)

        scroll = SmoothScrollArea(self._panel)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        scroll.setAutoFillBackground(False)
        scroll.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        scroll.viewport().setAutoFillBackground(False)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.viewport().setObjectName("galleryScrollViewport")
        scroll.viewport().setStyleSheet(
            "QWidget#galleryScrollViewport { background: transparent; border: none; }"
        )
        panel_layout.addWidget(scroll, 1)

        self._content = QWidget(scroll)
        self._content.setObjectName("galleryPageContent")
        self._content.setStyleSheet("QWidget#galleryPageContent { background: transparent; }")
        scroll.setWidget(self._content)

        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(36, 28, 28, 32)
        self._layout.setSpacing(28)
        self._layout.addWidget(self._makeHeader(title, module_path))

        manager = ThemeManager.instance()
        manager.themeChanged.connect(self._refreshFromSignal)
        manager.themeColorChanged.connect(self._refreshFromSignal)
        self.refreshTheme()

    def addExample(self, title: str, preview: QWidget, source: str = "Source code") -> DemoExample:
        example = DemoExample(title, preview, source, self._content)
        self._layout.addWidget(example)
        return example

    def finish(self) -> None:
        self._layout.addStretch(1)

    def setStatus(self, text: str) -> None:
        self._statusLabel.setText(text)

    def refreshTheme(self) -> None:
        palette = getPalette()
        self.setStyleSheet(
            f"QWidget#{self.objectName()} {{ "
            f"background: {palette.surface1}; "
            "}"
        )
        self._panel.update()

    def _refreshFromSignal(self, *_args) -> None:
        self.refreshTheme()

    def _makeHeader(self, title: str, module_path: str) -> QWidget:
        header = QWidget(self)
        header.setObjectName("galleryPageHeader")
        header.setStyleSheet("QWidget#galleryPageHeader { background: transparent; }")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(7)
        text_column.addWidget(TitleLabel(title, header))
        text_column.addWidget(BodyLabel(module_path, header))

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(6)
        action_row.addWidget(PushButton("Documentation", header, BreezeIcon.DOCUMENT))
        action_row.addWidget(PushButton("Source", header, BreezeIcon.INFO))
        self._statusLabel = BodyLabel("Ready", header)
        action_row.addWidget(self._statusLabel)
        action_row.addStretch(1)
        text_column.addLayout(action_row)

        layout.addLayout(text_column, 1)
        layout.addWidget(BreezeThemeSwitch(header), 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(TransparentToolButton(BreezeIcon.INFO, header), 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(TransparentToolButton(BreezeIcon.MORE, header), 0, Qt.AlignmentFlag.AlignTop)
        return header


def _row(*widgets: QWidget, spacing: int = 10) -> QWidget:
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)
    for widget in widgets:
        layout.addWidget(widget)
    layout.addStretch(1)
    return container
