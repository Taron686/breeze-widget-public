from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor


@dataclass(frozen=True)
class BreezePalette:
    primary1: str
    primary2: str
    primary3: str
    primary4: str
    primary5: str
    primary6: str
    primary_text: str
    surface1: str
    surface2: str
    surface3: str
    surface4: str
    surface5: str
    surface6: str
    text1: str
    text2: str
    border1: str
    chrome_bg: str
    chrome_text: str
    chrome_border: str
    chrome_hover: str
    chrome_pressed: str
    danger1: str
    danger_text: str


def _shade(color: QColor, factor: int) -> str:
    return QColor(color).lighter(factor).name()


def _accent_tokens(accent: QColor) -> dict[str, str]:
    return {
        "primary1": _shade(accent, 180),
        "primary2": _shade(accent, 145),
        "primary3": _shade(accent, 118),
        "primary4": accent.name(),
        "primary5": accent.darker(115).name(),
        "primary6": accent.darker(140).name(),
    }


def _neutral_tokens(dark: bool) -> dict[str, str]:
    if dark:
        surface1 = "#202020"
        surface2 = "#2b2b2b"
        surface3 = "#303030"
        surface4 = "#393939"
        surface5 = "#454545"
        surface6 = "#505050"
        text1 = "#f3f3f3"
        text2 = "#c8c8c8"
        border1 = "#464646"
    else:
        surface1 = "#f7f7f7"
        surface2 = "#ffffff"
        surface3 = "#fbfbfb"
        surface4 = "#f1f1f1"
        surface5 = "#e8e8e8"
        surface6 = "#dedede"
        text1 = "#1a1a1a"
        text2 = "#5f5f5f"
        border1 = "#d9d9d9"
    return {
        "surface1": surface1,
        "surface2": surface2,
        "surface3": surface3,
        "surface4": surface4,
        "surface5": surface5,
        "surface6": surface6,
        "text1": text1,
        "text2": text2,
        "border1": border1,
        "chrome_bg": surface2,
        "chrome_text": text1,
        "chrome_border": border1,
        "chrome_hover": surface4,
        "chrome_pressed": surface5,
    }


def _build_palette(dark: bool, accent: QColor) -> BreezePalette:
    tokens = _accent_tokens(accent) | _neutral_tokens(dark)

    return BreezePalette(
        primary1=tokens["primary1"],
        primary2=tokens["primary2"],
        primary3=tokens["primary3"],
        primary4=tokens["primary4"],
        primary5=tokens["primary5"],
        primary6=tokens["primary6"],
        primary_text="#000000" if dark else "#ffffff",
        surface1=tokens["surface1"],
        surface2=tokens["surface2"],
        surface3=tokens["surface3"],
        surface4=tokens["surface4"],
        surface5=tokens["surface5"],
        surface6=tokens["surface6"],
        text1=tokens["text1"],
        text2=tokens["text2"],
        border1=tokens["border1"],
        chrome_bg=tokens["chrome_bg"],
        chrome_text=tokens["chrome_text"],
        chrome_border=tokens["chrome_border"],
        chrome_hover=tokens["chrome_hover"],
        chrome_pressed=tokens["chrome_pressed"],
        danger1="#c42b1c",
        danger_text="#ffffff",
    )
