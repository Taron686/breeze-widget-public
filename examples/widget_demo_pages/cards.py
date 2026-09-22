"""Cards & settings — HeaderCardWidget + SettingCardGroup."""
from __future__ import annotations

from PySide6.QtWidgets import QApplication, QWidget

from breezewidget import (
    BodyLabel,
    BreezeIcon,
    ComboBoxSettingCard,
    CustomColorSettingCard,
    ExpandSettingCard,
    HeaderCardWidget,
    HyperlinkCard,
    OptionsSettingCard,
    PushSettingCard,
    RangeSettingCard,
    SettingCardGroup,
    SwitchSettingCard,
    setThemeColor,
)

from ._gallery import GalleryPage, _row


class CardsDemoPage(GalleryPage):
    """Phase-3d showcase: header cards and settings cards."""

    def __init__(self):
        super().__init__("Cards & settings", "breezewidget.cards", "phase3d-cards")
        self.addExample("A HeaderCardWidget with content area", self._headerCardPreview())
        self.addExample("SettingCardGroup with common settings rows", self._settingsGroupPreview())
        self.setStatus("Cards & settings bereit")
        self.finish()

    def _headerCardPreview(self) -> QWidget:
        header = HeaderCardWidget("HeaderCardWidget")
        header.addWidget(BodyLabel("Header oben, Content darunter, Separator dazwischen."))
        header.setMinimumWidth(520)
        return _row(header)

    def _settingsGroupPreview(self) -> QWidget:
        group = SettingCardGroup("Appearance")

        theme = SwitchSettingCard(
            BreezeIcon.MOON,
            "Dark mode",
            "Schaltet die Anwendung zwischen hell und dunkel.",
            checked=True,
        )
        theme.checkedChanged.connect(lambda checked: self.setStatus(f"Dark mode: {'an' if checked else 'aus'}"))
        group.addSettingCard(theme)

        density = ComboBoxSettingCard(
            ["Compact", "Comfortable", "Spacious"],
            BreezeIcon.SETTINGS,
            "Density",
            "Waehlt die Abstaende in Formularen.",
            current_index=1,
        )
        density.currentTextChanged.connect(lambda text: self.setStatus(f"Density: {text}"))
        group.addSettingCard(density)

        volume = RangeSettingCard(
            BreezeIcon.MORE,
            "Notification volume",
            "ClickableSlider als Settings-Action.",
            minimum=0,
            maximum=100,
            value=35,
        )
        volume.valueChanged.connect(lambda value: self.setStatus(f"Volume: {value}"))
        group.addSettingCard(volume)

        mode = OptionsSettingCard(
            [("Auto", "auto"), ("Light", "light"), ("Dark", "dark")],
            BreezeIcon.SUN,
            "Theme mode",
            "Segmented control im Action-Slot.",
        )
        mode.currentChanged.connect(lambda key: self.setStatus(f"Theme mode: {key}"))
        group.addSettingCard(mode)

        accent = CustomColorSettingCard(
            "#11d9f3",
            BreezeIcon.EDIT,
            "Accent color",
            "Oeffnet den nativen QColorDialog.",
            button_text="Waehlen",
        )
        accent.colorChanged.connect(lambda color: self._setAccent("Custom", color.name()))
        group.addSettingCard(accent)

        run = PushSettingCard(
            "Ausfuehren",
            BreezeIcon.CHECK,
            "PushSettingCard",
            "Fuehrt eine Aktion ueber den rechten Button aus.",
        )
        run.actionClicked.connect(lambda: self.setStatus("PushSettingCard ausgefuehrt"))
        group.addSettingCard(run)

        link = HyperlinkCard(
            "https://github.com/Taron686/BreezeWidget",
            "GitHub",
            BreezeIcon.INFO,
            "HyperlinkCard",
            "Oeffnet eine externe URL.",
        )
        group.addSettingCard(link)

        advanced = ExpandSettingCard(
            BreezeIcon.MORE,
            "ExpandSettingCard",
            "Zeigt zusaetzlichen Inhalt in derselben Card.",
        )
        advanced.addWidget(BodyLabel("Erweiterte Optionen koennen beliebige Widgets aufnehmen."))
        advanced.addWidget(BodyLabel("Der Body bleibt Teil derselben Card und klappt ohne Dialog auf."))
        advanced.expandedChanged.connect(lambda expanded: self.setStatus(f"ExpandSettingCard: {expanded}"))
        group.addSettingCard(advanced)

        group.setMinimumWidth(760)
        return _row(group)

    def _setAccent(self, name: str, color: str) -> None:
        setThemeColor(color, QApplication.instance())
        self.setStatus(f"Akzentfarbe: {name} ({color})")
