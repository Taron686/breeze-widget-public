"""Gemeinsame Basisklassen und Konstanten für CalendarWidget.

Exportiert:
    CalendarColors  — Farbkonfiguration (Dataclass mit Defaults)
    HeaderMode      — 5 Positionen für Titel + Navigation
    DayButton       — Tages-Button (QPushButton) mit Status-Tracking
    DayLetter       — Wochentag-Kopfzeilen-Label (Klassenname = QSS-Selektor)
    WeekNumberLabel — KW-Label links jeder Zeile
    WEEKDAY_NAMES_* — Wochentagnamen-Konstanten (Mo-first, ISO)
    WEEKDAY_NAMES   — Dict lang → tuple
    get_weekday_names(lang) — Helferfunktion
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import date, datetime
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton


# ---------------------------------------------------------------------------
# Farbkonfiguration
# ---------------------------------------------------------------------------

def _darken(hex_color: str, factor: float = 0.12) -> str:
    """Gibt eine um ``factor`` abgedunkelte Variante von ``hex_color`` zurück.

    Args:
        hex_color: Hex-Farbwert ``"#RRGGBB"`` (mit oder ohne führendem ``#``).
        factor:    Abdunkelungs-Faktor 0.0–1.0 (0.12 = 12 % dunkler).

    Returns:
        Hex-Farbwert ``"#RRGGBB"``.
    """
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return f"#{r:02X}{g:02X}{b:02X}"


@dataclass
class CalendarColors:
    """Vollständige Farbkonfiguration für ``CalendarWidget``.

    Alle Farben sind Hex-Strings (``"#RRGGBB"``).
    Hover- und Pressed-Zustände werden automatisch aus den Basisfarben
    abgeleitet, wenn sie nicht explizit gesetzt werden (``None``).

    Semantische Farben (häufig durch das App-Theme überschrieben):

    .. code-block:: python

        colors = CalendarColors(
            today    = "#EE9B00",
            event    = "#2A9D8F",
            selected = "#0A9396",
        )
        calendar.set_colors(colors)

    Oder einzelne Farben ändern:

    .. code-block:: python

        calendar.update_color(today="#FF5722", selected="#6200EA")
    """

    # --- Semantische Hauptfarben ---
    today:      str = "#EE9B00"   # Hintergrund: heutiges Datum
    today_text: str = "#FFFFFF"   # Text:        heutiges Datum
    event:      str = "#C8DBFF"   # Hintergrund: Tag mit Aktivität
    event_text: str = "#333333"   # Text:        Tag mit Aktivität
    selected:   str = "#0A9396"   # Rahmen:      selektierter Tag (2px border)

    # --- Strukturelle / Theme-Farben ---
    background: str       = "#FFFFFF"   # Widget-Hintergrund
    text:       str       = "#333333"   # Normale Tage, Titel, Nav-Buttons
    text_muted: str       = "#AAAAAA"   # KW-Nummern, Wochentag-Buchstaben
    divider:    str       = "#D0D0D0"   # Horizontale Trennlinie unter dem Header
    week_line:  str | None = field(default=None)  # Vertikale KW-Linie (None = divider)
    hover:      str       = "#EBEBEB"   # Hover-Hintergrund (normale Tage)
    pressed:    str       = "#D0D0D0"   # Gedrückt-Hintergrund (normale Tage)

    # --- Optionale Hover-/Pressed-Overrides (None = auto-darkened) ---
    today_hover:   str | None = field(default=None)
    today_pressed: str | None = field(default=None)
    event_hover:   str | None = field(default=None)
    event_pressed: str | None = field(default=None)

    # ------------------------------------------------------------------ #

    def resolved_week_line(self) -> str:
        """Farbe der vertikalen KW-Trennlinie (explizit oder = divider)."""
        return self.week_line or self.divider

    def resolved_today_hover(self) -> str:
        """Hover-Farbe für heutigen Tag (explizit oder auto-darken)."""
        return self.today_hover or _darken(self.today, 0.10)

    def resolved_today_pressed(self) -> str:
        """Pressed-Farbe für heutigen Tag (explizit oder auto-darken)."""
        return self.today_pressed or _darken(self.today, 0.20)

    def resolved_event_hover(self) -> str:
        """Hover-Farbe für Event-Tag (explizit oder auto-darken)."""
        return self.event_hover or _darken(self.event, 0.10)

    def resolved_event_pressed(self) -> str:
        """Pressed-Farbe für Event-Tag (explizit oder auto-darken)."""
        return self.event_pressed or _darken(self.event, 0.18)

    def replace(self, **kwargs: str) -> "CalendarColors":
        """Gibt eine Kopie mit geänderten Feldern zurück (non-mutating).

        Unbekannte Feldnamen lösen einen ``ValueError`` aus.

        Example::

            new = colors.replace(today="#FF5722", selected="#6200EA")
        """
        valid = {f.name for f in fields(self)}
        for key in kwargs:
            if key not in valid:
                raise ValueError(
                    f"CalendarColors hat kein Feld '{key}'. "
                    f"Gültige Felder: {sorted(valid)}"
                )
        import dataclasses
        return dataclasses.replace(self, **kwargs)

# ---------------------------------------------------------------------------
# Wochentagnamen (Montag zuerst, ISO-Standard)
# ---------------------------------------------------------------------------

WEEKDAY_NAMES_EN: tuple[str, ...] = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")
WEEKDAY_NAMES_DE: tuple[str, ...] = ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")

WEEKDAY_NAMES: dict[str, tuple[str, ...]] = {
    "en": WEEKDAY_NAMES_EN,
    "de": WEEKDAY_NAMES_DE,
}


def get_weekday_names(lang: str = "en") -> tuple[str, ...]:
    """Gibt die kurzen Wochentagnamen (Mo-So) für eine Sprache zurück.

    Unbekannte Sprachcodes fallen auf Englisch zurück.
    """
    return WEEKDAY_NAMES.get(lang.lower()[:2], WEEKDAY_NAMES_EN)


# ---------------------------------------------------------------------------
# Header-Layout-Modi
# ---------------------------------------------------------------------------

class HeaderMode(Enum):
    """5 Konfigurationen für die Position von Titel und Navigation.

    Beispiele (title = "Kalender"):
        TITLE_LEFT_NAV_RIGHT  →  Kalender   <  MRZ 2026  >
        NAV_LEFT_TITLE_RIGHT  →  <  MRZ 2026  >   Kalender
        NAV_ONLY_LEFT         →  <  MRZ 2026  >
        NAV_ONLY_CENTER       →      <  MRZ 2026  >
        NAV_ONLY_RIGHT        →             <  MRZ 2026  >
    """
    TITLE_LEFT_NAV_RIGHT = "title_left"
    NAV_LEFT_TITLE_RIGHT = "nav_left"
    NAV_ONLY_LEFT        = "nav_only_left"
    NAV_ONLY_CENTER      = "nav_only_center"
    NAV_ONLY_RIGHT       = "nav_only_right"


# ---------------------------------------------------------------------------
# DayButton
# ---------------------------------------------------------------------------

class DayButton(QPushButton):
    """Tages-Button im Kalender-Grid.

    ObjectName (= QSS-Selektor):
        ``day_number``            — normaler Tag
        ``day_number_event``      — Tag mit Aktivität
        ``day_number_today``      — heutiger Tag
        ``day_number_today_event``— heutiger Tag + Aktivität
        ``no_day``                — leere Zelle (Padding)

    Qt-Eigenschaft:
        ``selected`` (bool) — selektierter Tag, per QSS: ``DayButton[selected="true"]``
    """

    def __init__(self, row: int, col: int, parent=None) -> None:
        super().__init__(parent)
        self.row: int = row
        self.col: int = col
        self.day: datetime | None = None
        self.event_: str = ""
        self.setProperty("selected", False)
        self.set_empty()

    # ------------------------------------------------------------------ #

    def update_type(self, obj_name: str) -> None:
        """Setzt objectName und erzwingt QSS-Neuberechnung."""
        self.setObjectName(obj_name)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_day(self, day: datetime, event: str = "") -> None:
        """Befüllt den Button mit einem Datum und optionalem Aktivitäts-Text."""
        self.day = day
        self.event_ = event or ""
        self.setProperty("selected", False)
        self.setText(str(day.day))
        is_today = day.date() == date.today()
        has_event = bool(event)
        if is_today and has_event:
            self.update_type("day_number_today_event")
        elif is_today:
            self.update_type("day_number_today")
        elif has_event:
            self.update_type("day_number_event")
        else:
            self.update_type("day_number")
        self.setToolTip(event)

    def set_empty(self) -> None:
        """Setzt den Button auf einen leeren Padding-Slot zurück."""
        self.day = None
        self.event_ = ""
        self.setText("")
        self.setToolTip("")
        self.setProperty("selected", False)
        self.update_type("no_day")

    def set_selected(self, selected: bool) -> None:
        """Setzt/entfernt den visuellen Selektion-Rahmen."""
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.setFixedSize(38, 38)
        self.update()


# ---------------------------------------------------------------------------
# DayLetter
# ---------------------------------------------------------------------------

class DayLetter(QLabel):
    """Wochentag-Kopfzeilen-Label (z.B. „Mo", „Di").

    Klassenname ``DayLetter`` wird als QSS-Selektor verwendet.
    """

    def __init__(self, text: str = "", parent=None) -> None:
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


# ---------------------------------------------------------------------------
# WeekNumberLabel
# ---------------------------------------------------------------------------

class WeekNumberLabel(QLabel):
    """KW-Label links jeder Kalender-Zeile.

    ObjectName ``week_number`` für QSS-Styling.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("week_number")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
