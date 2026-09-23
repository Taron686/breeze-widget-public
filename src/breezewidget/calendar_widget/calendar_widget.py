"""CalendarWidget — eigenständiges PySide6-Kalender-Widget.

Drop-in-kompatibler Ersatz für ``activity_calendar_widget`` mit erweiterter API:

Neu gegenüber activity_calendar_widget:
    - ``datum_angeklickt``   — Signal(date) bei Tag-Klick
    - ``show_week_numbers``  — optionale KW-Spalte links
    - ``show_week_line``     — optionale vertikale Trennlinie nach KW-Spalte
    - ``header_mode``        — 5 Layout-Konfigurationen für Titel + Navigation
    - ``weekday_names``      — Sprach-aware Wochentagnamen (default Englisch)
    - ``day_number_today_event`` — Heute + Aktivität kombinierter Zustand
    - Montag-zuerst (ISO-Standard)
    - ``CalendarColors``     — typsicheres Farb-Interface (Dataclass)
    - ``set_colors()``       — alle Farben auf einmal setzen
    - ``update_color()``     — einzelne Farben ändern (keyword-args)

Rückwärts-kompatible API (identisch zu activity_calendar_widget):
    - Konstruktor: title, default_month, border_radius, parent
    - Attribute:   title_label, activities, current_month, days_numbers
    - Methoden:    set_month(), set_selected_date()
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from PySide6.QtCore import QDate, QEvent, QLocale, Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .commons import (
    CalendarColors,
    DayButton,
    DayLetter,
    HeaderMode,
    WeekNumberLabel,
    WEEKDAY_NAMES_EN,
)
from .month_model import activity_for_day, month_cells, week_numbers_for_cells

# ---------------------------------------------------------------------------
# QSS-Template — Platzhalter werden durch CalendarColors-Felder ersetzt.
# Doppelte geschweifte Klammern {{ }} = literale QSS-Klammern.
# ---------------------------------------------------------------------------
_QSS_TEMPLATE = """
QPushButton#calendar_today {{
    color: {selected}; background: transparent;
    font-size: 12px; border: 1px solid transparent; border-radius: 10px;
    padding: 2px 6px; min-width: 0; min-height: 0;
}}
QPushButton#calendar_today:hover {{ background: {hover}; }}
QPushButton#calendar_today:focus {{ border-color: {selected}; }}
CalendarWidget {{
    background: {background};
    border-radius: {radius}px;
}}
QFrame#divider {{
    color: {divider};
    max-height: 2px;
}}
QLabel#title_label {{
    color: {text};
    font-size: 15px;
    font-weight: bold;
    background: transparent;
}}
QPushButton#calendar_heading {{
    color: {text};
    font-size: 16px;
    font-weight: bold;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 2px 4px;
    min-width: 0;
}}
QPushButton#calendar_choice {{
    color: {text}; background: transparent;
    border: 2px solid transparent; border-radius: 6px;
    padding: 4px; min-width: 0;
}}
QPushButton#calendar_heading:hover, QPushButton#calendar_choice:hover {{
    background: {hover};
}}
QPushButton#calendar_heading:focus, QPushButton#calendar_choice:focus,
QPushButton#calendar_choice:checked {{
    border-color: {selected};
}}
QPushButton#toggle_button {{
    border-radius: 15px;
    color: {text};
    font-size: 14px;
    font-weight: bold;
    background: transparent;
    border: 1px solid transparent;
    padding: 0;
    min-width: 28px; max-width: 28px;
    min-height: 28px; max-height: 28px;
    outline: none;
}}
QPushButton#toggle_button:hover   {{ background: {hover}; }}
QPushButton#toggle_button:pressed {{ background: {pressed}; }}
QPushButton#toggle_button:focus {{ border-color: {selected}; }}

DayLetter {{
    color: {text_muted};
    font-size: 12px;
    font-weight: bold;
    background: transparent;
    min-width: 38px; max-width: 38px;
    min-height: 22px; max-height: 22px;
}}
DayLetter#kw_header {{
    color: {text_muted};
    min-width: 28px; max-width: 28px;
    min-height: 22px; max-height: 22px;
}}
WeekNumberLabel {{
    color: {text_muted};
    font-size: 11px;
    font-weight: bold;
    background: transparent;
    min-width: 28px; max-width: 28px;
    min-height: 43px; max-height: 43px;
}}
QWidget#week_line {{
    background: {week_line};
    min-width: 2px; max-width: 2px;
}}
DayButton {{
    border-radius: 19px;
    color: {text};
    font-size: 13px;
    font-weight: bold;
    background: transparent;
    border: none;
    padding: 0;
    min-width: 38px; max-width: 38px;
    min-height: 38px; max-height: 38px;
}}
DayButton#day_number           {{ background: transparent; }}
DayButton#day_number:hover     {{ background: {hover}; }}
DayButton#day_number:pressed   {{ background: {pressed}; }}

DayButton#day_number_adjacent {{ background: transparent; color: {adjacent_text}; }}
DayButton#day_number_adjacent:hover {{ background: {hover}; }}
DayButton#day_number_adjacent:pressed {{ background: {pressed}; }}

DayButton#day_number_event     {{ background: transparent; color: {text}; }}
DayButton#day_number_event:hover   {{ background: {hover}; }}
DayButton#day_number_event:pressed {{ background: {pressed}; }}

DayButton#day_number_today     {{ background: {today}; color: {today_text}; }}
DayButton#day_number_today:hover   {{ background: {today_hover}; }}
DayButton#day_number_today:pressed {{ background: {today_pressed}; color: {today_text}; }}

DayButton#day_number_today_event {{
    background: {today}; color: {today_text};
}}
DayButton#day_number_today_event:hover   {{ background: {today_hover}; }}
DayButton#day_number_today_event:pressed {{ background: {today_pressed}; }}

DayButton[selected="true"] {{
    border: 2px solid {selected};
}}

DayButton#no_day {{ background: transparent; border: none; }}
DayButton#no_day:hover, DayButton#no_day:pressed {{ background: transparent; }}
"""

# Vertikaler Abstand zwischen Zeilen im Grid (px)
_ROW_SPACING = 4


def _build_qss(colors: CalendarColors, radius: int) -> str:
    """Erzeugt das vollständige QSS aus ``colors`` und ``border_radius``."""
    muted, background = QColor(colors.text_muted), QColor(colors.background)
    adjacent = QColor(*[(a + b) // 2 for a, b in zip(muted.getRgb()[:3], background.getRgb()[:3])])
    return _QSS_TEMPLATE.format(
        adjacent_text = adjacent.name(),
        radius        = radius,
        background    = colors.background,
        text          = colors.text,
        text_muted    = colors.text_muted,
        divider       = colors.divider,
        week_line     = colors.resolved_week_line(),
        hover         = colors.hover,
        pressed       = colors.pressed,
        today         = colors.today,
        today_text    = colors.today_text,
        today_hover   = colors.resolved_today_hover(),
        today_pressed = colors.resolved_today_pressed(),
        event         = colors.event,
        event_text    = colors.event_text,
        event_hover   = colors.resolved_event_hover(),
        event_pressed = colors.resolved_event_pressed(),
        selected      = colors.selected,
    )


class CalendarWidget(QFrame):
    """Kalender-Widget mit optionaler KW-Spalte, konfigurierbarem Header und
    vollständig steuerbarem Farbschema über ``CalendarColors``.

    Signals:
        datum_angeklickt(date): Emittiert beim Klick auf einen Tag.

    Args:
        title:               Titeltext (für TITLE_LEFT / NAV_LEFT Modi).
        header_mode:         Einer der 5 ``HeaderMode``-Werte.
        show_week_numbers:   KW-Spalte links anzeigen.
        show_week_line:      Vertikale Trennlinie nach KW-Spalte (nur wenn
                             ``show_week_numbers=True``).
        weekday_names:       7 Wochentagnamen Mo–So (Standard: Englisch).
        default_month:       Anfangsmonat (Standard: aktueller Monat).
        default_activities:  Aktivitäten-Dict ``{"MM-YYYY": {tag: tooltip}}``.
        border_radius:       Eckenradius des Widgets in px.
        colors:              ``CalendarColors``-Instanz; ``None`` = helles Default.
        parent:              Qt-Eltern-Widget.

    Farben dynamisch ändern::

        # Alle auf einmal
        cal.set_colors(CalendarColors(today="#FF5722", event="#4CAF50"))

        # Einzelne Felder
        cal.update_color(today="#FF5722", selected="#6200EA")

        # Non-mutating copy + set
        cal.set_colors(cal.colors.replace(today="#FF5722"))
    """

    datum_angeklickt = Signal(date)
    _viewChanged = Signal()

    def __init__(
        self,
        title: str = "",
        header_mode: HeaderMode = HeaderMode.TITLE_LEFT_NAV_RIGHT,
        show_week_numbers: bool = True,
        show_week_line: bool = False,
        weekday_names: tuple[str, ...] | list[str] | None = None,
        default_month: datetime | None = None,
        default_activities: dict[str, dict[int, str]] | None = None,
        border_radius: int = 14,
        colors: CalendarColors | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self._title_text    = title
        self._header_mode   = header_mode
        self._show_kw       = show_week_numbers
        self._show_line     = show_week_line and show_week_numbers
        self._weekday_names: tuple[str, ...] = (
            tuple(weekday_names) if weekday_names else WEEKDAY_NAMES_EN
        )
        self._activities: dict[str, dict[int, str]] = default_activities or {}
        self._current_month: datetime = default_month or datetime.now()
        self._selected_date: date | None = None
        self._colors: CalendarColors = colors or CalendarColors()
        self._border_radius: int = border_radius
        self._selection_mode = "day"

        self._day_buttons:       list[DayButton]         = []
        self._week_labels:       list[WeekNumberLabel]   = []
        self._day_letter_labels: list[DayLetter]         = []

        self._build_ui()
        self.setStyleSheet(_build_qss(self._colors, self._border_radius))
        self.set_month(self._current_month)

    # ------------------------------------------------------------------ #
    # Properties                                                           #
    # ------------------------------------------------------------------ #

    @property
    def current_month(self) -> datetime:
        """Aktuell angezeigter Monat."""
        return self._current_month

    @property
    def activities(self) -> dict[str, dict[int, str]]:
        """Aktivitäten-Dict ``{"MM-YYYY": {tag_int: tooltip_str}}``."""
        return self._activities

    @activities.setter
    def activities(self, value: dict[str, dict[int, str]]) -> None:
        self._activities = value

    @property
    def days_numbers(self) -> list[DayButton]:
        """Flache Liste aller 42 DayButton-Instanzen (row-major)."""
        return self._day_buttons

    @property
    def colors(self) -> CalendarColors:
        """Aktuelle Farbkonfiguration (read-only Snapshot).

        Änderungen über ``set_colors()`` oder ``update_color()`` vornehmen.
        """
        return self._colors

    # ------------------------------------------------------------------ #
    # Öffentliche API                                                      #
    # ------------------------------------------------------------------ #

    def set_month(self, month: datetime) -> None:
        """Zeigt den angegebenen Monat an und befüllt alle 42 Tages-Buttons."""
        self._current_month = month
        self._selection_mode = "day"
        self._selection_panel.hide()
        self._day_view.show()
        self._month_button.setText(self.locale().standaloneMonthName(month.month, QLocale.ShortFormat).rstrip('.').upper())
        self._year_button.setText(str(month.year))
        self._prev_btn.setEnabled((month.year, month.month) > (1, 1))
        self._next_btn.setEnabled((month.year, month.month) < (9999, 12))
        self._populate_days()
        self._viewChanged.emit()

    def set_selected_date(self, d: date | datetime | None) -> None:
        """Setzt die visuelle Selektion auf einen Tag (Umriss-Rahmen).

        Bleibt nach ``set_month()`` erhalten, da ``set_month`` die Selektion
        automatisch wiederherstellt.
        """
        if d is None:
            self._selected_date = None
        else:
            self._selected_date = d.date() if isinstance(d, datetime) else d

        for btn in self._day_buttons:
            if btn.day is not None:
                btn.set_selected(
                    self._selected_date is not None
                    and btn.day.date() == self._selected_date
                )
            else:
                btn.set_selected(False)

    def set_activities(self, activities: dict[str, dict[int, str]]) -> None:
        """Setzt Aktivitäten-Dict und rendert den aktuellen Monat neu."""
        self._activities = activities
        self.set_month(self._current_month)

    def set_weekday_names(self, names: tuple[str, ...] | list[str]) -> None:
        """Aktualisiert die Wochentag-Kopfzeile (z.B. nach Sprachwechsel)."""
        self._weekday_names = tuple(names)
        for lbl, name in zip(self._day_letter_labels, self._weekday_names):
            lbl.setText(name)

    def set_title(self, title: str) -> None:
        """Aktualisiert den Titel-Text."""
        self._title_text = title
        self.title_label.setText(title)

    def set_colors(self, colors: CalendarColors) -> None:
        """Ersetzt die komplette Farbkonfiguration und wendet sie sofort an.

        Args:
            colors: Neue ``CalendarColors``-Instanz.

        Example::

            cal.set_colors(CalendarColors(
                today    = "#FF5722",
                event    = "#4CAF50",
                selected = "#6200EA",
                background = "#1F232A",
                text       = "#F5F7FA",
            ))
        """
        self._colors = colors
        self.setStyleSheet(_build_qss(self._colors, self._border_radius))

    def update_color(self, **kwargs: str) -> None:
        """Ändert einzelne Farb-Felder und wendet sie sofort an.

        Unbekannte Feldnamen lösen einen ``ValueError`` aus.

        Args:
            **kwargs: Feldname=Hex-Wert, z.B. ``today="#FF5722"``.

        Example::

            cal.update_color(today="#EE9B00", selected="#0A9396")
            cal.update_color(background="#1F232A", text="#F5F7FA")
        """
        self._colors = self._colors.replace(**kwargs)
        self.setStyleSheet(_build_qss(self._colors, self._border_radius))

    def set_border_radius(self, radius: int) -> None:
        """Ändert den Eckenradius des Widgets."""
        self._border_radius = radius
        self.setStyleSheet(_build_qss(self._colors, self._border_radius))

    def set_show_week_numbers(self, visible: bool) -> None:
        """Blendet die KW-Spalte ein oder aus (Laufzeit-Toggle).

        Deaktiviert die KW-Linie automatisch, wenn KW ausgeblendet wird.

        Args:
            visible: ``True`` = KW-Spalte sichtbar, ``False`` = ausgeblendet.
        """
        self._show_kw = visible
        if not visible:
            self._show_line = False
        self._update_kw_visibility()

    def set_show_week_line(self, visible: bool) -> None:
        """Blendet die vertikale KW-Trennlinie ein oder aus (Laufzeit-Toggle).

        Hat nur Effekt wenn ``show_week_numbers`` aktiv ist.

        Args:
            visible: ``True`` = Linie sichtbar, ``False`` = ausgeblendet.
        """
        self._show_line = visible and self._show_kw
        self._update_kw_visibility()

    # ------------------------------------------------------------------ #
    # Interne KW-Sichtbarkeitssteuerung                                    #
    # ------------------------------------------------------------------ #

    def _update_kw_visibility(self) -> None:
        """Synchronisiert Sichtbarkeit und Abstände von KW-Spalte und Linie."""
        show_line = self._show_line and self._show_kw

        self._kw_widget.setVisible(self._show_kw)
        self._gap_kw.setVisible(self._show_kw)
        self._line_widget.setVisible(show_line)
        self._gap_after_line.setVisible(show_line)

        if self._show_kw:
            # 4 px vor der Linie (mit Linie) oder 10 px direkt zum Grid (ohne)
            self._gap_kw.setFixedWidth(4 if show_line else 10)

    # ------------------------------------------------------------------ #
    # UI-Aufbau                                                            #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(_ROW_SPACING)

        self._today_button = QPushButton(self)
        self._today_button.setObjectName("calendar_today")
        self._today_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._today_button.setToolTip(self.tr("Zum heutigen Tag"))
        self._today_button.clicked.connect(self._goToday)
        root.addWidget(self._today_button, 0, Qt.AlignmentFlag.AlignHCenter)
        self._refreshToday()
        self._today_timer = QTimer(self)
        self._today_timer.setInterval(60_000)
        self._today_timer.timeout.connect(self._refreshToday)
        self._today_timer.start()

        root.addLayout(self._build_header())

        divider = QFrame(self)
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(divider)

        # Body: [kw_widget][gap_kw][line_widget][gap_line][grid_col]
        # Alle Elemente werden immer gebaut; show/hide via _update_kw_visibility().
        # So können KW und Linie zur Laufzeit per set_show_week_numbers/line() umgeschaltet
        # werden ohne das Layout neu aufzubauen.
        self._day_view = QWidget(self)
        body = QHBoxLayout(self._day_view)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._kw_widget = self._build_kw_column()     # QWidget (show/hideable)
        body.addWidget(self._kw_widget, 0, Qt.AlignmentFlag.AlignTop)

        self._gap_kw = QWidget(self)                  # Abstand KW → Linie/Grid
        self._gap_kw.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        body.addWidget(self._gap_kw)

        self._line_widget = QWidget(self)             # Vertikale KW-Trennlinie
        self._line_widget.setObjectName("week_line")
        self._line_widget.setFixedWidth(2)
        body.addWidget(self._line_widget)             # kein AlignTop → volle Höhe

        self._gap_after_line = QWidget(self)          # Abstand Linie → Grid
        self._gap_after_line.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._gap_after_line.setFixedWidth(8)
        body.addWidget(self._gap_after_line)

        grid_col = self._build_grid_column()
        self._grid_col = grid_col
        body.addLayout(grid_col)
        body.setAlignment(grid_col, Qt.AlignmentFlag.AlignTop)
        body.addStretch(1)

        root.addWidget(self._day_view)
        self._selection_panel = QWidget(self)
        self._selection_panel.setMinimumWidth(329)
        choices = QGridLayout(self._selection_panel)
        choices.setContentsMargins(0, 0, 0, 0)
        choices.setSpacing(8)
        self._choice_buttons = []
        for index in range(12):
            button = QPushButton(self._selection_panel)
            button.setObjectName("calendar_choice")
            button.setCheckable(True)
            button.setMinimumHeight(44)
            button.clicked.connect(lambda checked=False, i=index: self._choosePeriod(i))
            choices.addWidget(button, index // 3, index % 3)
            self._choice_buttons.append(button)
        self._selection_panel.hide()
        root.addWidget(self._selection_panel)
        root.addStretch(1)

        self._update_kw_visibility()
        self._prev_btn.clicked.connect(self._go_prev_month)
        self._next_btn.clicked.connect(self._go_next_month)

    def _build_header(self) -> QHBoxLayout:
        """Baut die Kopfzeile je nach HeaderMode auf."""
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self.title_label = QLabel(self._title_text)
        self.title_label.setObjectName("title_label")

        self._prev_btn = QPushButton("<")
        self._prev_btn.setObjectName("toggle_button")
        self._prev_btn.setFixedSize(30, 30)

        self._month_label = QWidget()
        heading = QHBoxLayout(self._month_label)
        heading.setContentsMargins(0, 0, 0, 0)
        heading.setSpacing(0)
        self._month_button = QPushButton()
        self._year_button = QPushButton()
        for button in (self._month_button, self._year_button):
            button.setObjectName("calendar_heading")
            button.setMinimumHeight(30)
            heading.addWidget(button)
        self._month_button.setAccessibleName(self.tr("Choose month"))
        self._year_button.setAccessibleName(self.tr("Choose year"))
        self._month_button.clicked.connect(lambda: self._showSelection("month"))
        self._year_button.clicked.connect(lambda: self._showSelection("year"))

        self._next_btn = QPushButton(">")
        self._next_btn.setObjectName("toggle_button")
        self._next_btn.setFixedSize(30, 30)

        mode = self._header_mode

        if mode == HeaderMode.TITLE_LEFT_NAV_RIGHT:
            lay.addWidget(self.title_label)
            lay.addStretch(1)
            lay.addWidget(self._prev_btn)
            lay.addWidget(self._month_label)
            lay.addWidget(self._next_btn)

        elif mode == HeaderMode.NAV_LEFT_TITLE_RIGHT:
            lay.addWidget(self._prev_btn)
            lay.addWidget(self._month_label)
            lay.addWidget(self._next_btn)
            lay.addStretch(1)
            lay.addWidget(self.title_label)

        elif mode == HeaderMode.NAV_ONLY_LEFT:
            lay.addWidget(self._prev_btn)
            lay.addWidget(self._month_label)
            lay.addWidget(self._next_btn)
            lay.addStretch(1)
            self.title_label.hide()

        elif mode == HeaderMode.NAV_ONLY_CENTER:
            lay.addStretch(1)
            lay.addWidget(self._prev_btn)
            lay.addWidget(self._month_label)
            lay.addWidget(self._next_btn)
            lay.addStretch(1)
            self.title_label.hide()

        elif mode == HeaderMode.NAV_ONLY_RIGHT:
            lay.addStretch(1)
            lay.addWidget(self._prev_btn)
            lay.addWidget(self._month_label)
            lay.addWidget(self._next_btn)
            self.title_label.hide()

        return lay

    def _build_kw_column(self) -> QWidget:
        """Baut die KW-Spalte als QWidget-Container auf (show/hide-fähig).

        Enthält oben das "KW"-Header-Label (22 px) und darunter 6
        WeekNumberLabel (43 px), passend zu den DayButton-Zeilen-Wrappern.
        Gibt einen QWidget zurück, damit set_show_week_numbers() ihn
        per setVisible() ein-/ausblenden kann.
        """
        widget = QWidget(self)
        widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        col = QVBoxLayout(widget)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(_ROW_SPACING)
        col.setAlignment(Qt.AlignmentFlag.AlignTop)

        kw_hdr = DayLetter("KW")
        kw_hdr.setObjectName("kw_header")
        kw_hdr.setFixedSize(28, 22)
        col.addWidget(kw_hdr)

        for _ in range(6):
            kw_lbl = WeekNumberLabel()
            kw_lbl.setFixedSize(28, 43)
            self._week_labels.append(kw_lbl)
            col.addWidget(kw_lbl)

        return widget

    def _build_grid_column(self) -> QVBoxLayout:
        """Baut den 7-Spalten-Grid als vertikalen Stack auf.

        Jede Zeile wird als QWidget mit setFixedHeight() gekapselt —
        damit kann der QVBoxLayout sie nicht vertikal strecken.
        Das ist zwingend erforderlich, damit kw_col und grid_col
        zeilengenau fluchten: kw_col enthält nur fixed-size QWidgets,
        grid_col muss dieselbe Garantie bieten.
        """
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(_ROW_SPACING)
        col.setAlignment(Qt.AlignmentFlag.AlignTop)

        col.addWidget(self._build_day_letters_row())
        for row in range(6):
            col.addWidget(self._build_week_row(row))

        return col

    def _build_day_letters_row(self) -> QWidget:
        """Wochentag-Kopfzeile (Mo–So) als fixed-height QWidget-Wrapper."""
        wrapper = QWidget()
        wrapper.setFixedHeight(22)
        wrapper.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        lay = QHBoxLayout(wrapper)
        lay.setContentsMargins(0, 0, 3, 0)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        for name in self._weekday_names:
            lbl = DayLetter(name)
            lbl.setFixedSize(38, 22)
            self._day_letter_labels.append(lbl)
            lay.addWidget(lbl)

        return wrapper

    def _build_week_row(self, row: int) -> QWidget:
        """Eine Kalenderzeile (7 DayButtons) als fixed-height QWidget-Wrapper.

        Wrapper ist 2 px höher als der Button (40 statt 38), damit die
        QSS-Selektions-Border (2 px) nicht am oberen/unteren Rand abgeschnitten
        wird — Qt clippt Kindwidget-Malerei an der Elternwidget-Grenze.
        """
        wrapper = QWidget()
        wrapper.setFixedHeight(43)          # 38px Button + 2,5px Puffer oben+unten
        wrapper.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        lay = QHBoxLayout(wrapper)
        lay.setContentsMargins(0, 0, 3, 0)  # 3px rechts damit Sonntags-Kreis nicht abgeschnitten wird
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        for col in range(7):
            btn = DayButton(row, col)
            btn.setFixedSize(38, 38)        # Kreis bleibt 38×38 — Qt zentriert in 43px
            btn.clicked.connect(self._make_day_handler(btn))
            self._day_buttons.append(btn)
            lay.addWidget(btn)

        return wrapper

    # ------------------------------------------------------------------ #
    # Tage befüllen                                                        #
    # ------------------------------------------------------------------ #

    def _populate_days(self) -> None:
        """Befüllt alle 42 DayButtons und aktualisiert die KW-Labels."""
        month = self._current_month
        days = month_cells(month)

        for row in range(6):
            visible = any(day is not None for day in days[row * 7:(row + 1) * 7])
            self._day_buttons[row * 7].parentWidget().setVisible(visible)
            self._week_labels[row].setVisible(visible)

        for day_val, btn in zip(days, self._day_buttons):
            btn.setEnabled(day_val is not None)
            if day_val is not None:
                btn.set_day(day_val, activity_for_day(self._activities, day_val, day_val))
                if (day_val.year, day_val.month) != (month.year, month.month):
                    btn.update_type("day_number_adjacent")
                if (
                    self._selected_date is not None
                    and day_val.date() == self._selected_date
                ):
                    btn.set_selected(True)
            else:
                btn.set_empty()

        # KW-Labels: erste belegte Zelle je Zeile bestimmt die KW
        if self._show_kw:
            for kw_lbl, kw_str in zip(self._week_labels, week_numbers_for_cells(days)):
                kw_lbl.setText(kw_str)
        self._kw_widget.layout().invalidate()
        self._kw_widget.layout().activate()
        self._grid_col.invalidate()
        self._grid_col.parent().invalidate()
        self.layout().invalidate()
        self.layout().activate()
        self.updateGeometry()

        # Jeder DayButton ruft unpolish/polish/update in update_type() und
        # set_selected() selbst auf — ein globales setStyleSheet() ist hier
        # nicht nötig und würde ein Full-Relayout auslösen.

    # ------------------------------------------------------------------ #
    # Navigation                                                           #
    # ------------------------------------------------------------------ #

    def _go_prev_month(self) -> None:
        if self._selection_mode != "day":
            self._pageSelection(-1)
            return
        first = datetime(self._current_month.year, self._current_month.month, 1)
        if first > datetime.min:
            self.set_month(first - timedelta(days=1))

    def _refreshToday(self) -> None:
        today = QDate.currentDate()
        text = self.tr("Heute") + ", " + self.locale().toString(today, QLocale.LongFormat)
        if self._today_button.text() != text:
            self._today_button.setText(text)
            self._viewChanged.emit()

    def _goToday(self) -> None:
        today = QDate.currentDate().toPython()
        self._refreshToday()
        self.set_selected_date(today)
        self.set_month(datetime(today.year, today.month, 1))
        for button in self.days_numbers:
            if button.day and button.day.date() == today:
                button.setFocus(Qt.FocusReason.OtherFocusReason)
                break

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._refreshToday()

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.LocaleChange and hasattr(self, "_today_button"):
            self._refreshToday()

    def _go_next_month(self) -> None:
        if self._selection_mode != "day":
            self._pageSelection(1)
            return
        year, month = self._current_month.year, self._current_month.month
        if (year, month) == (9999, 12):
            return
        if month == 12:
            self.set_month(datetime(year + 1, 1, 1))
        else:
            self.set_month(datetime(year, month + 1, 1))

    def _showSelection(self, mode: str) -> None:
        self._selection_mode = mode
        self._selection_year = self._current_month.year
        self._year_start = min(9988, ((self._current_month.year - 1) // 12) * 12 + 1)
        self._selection_panel.setMinimumHeight(self._day_view.sizeHint().height())
        self._day_view.hide()
        self._selection_panel.show()
        self._refreshSelection()
        index = self._current_month.month - 1 if mode == "month" else self._current_month.year - self._year_start
        self._choice_buttons[index].setFocus()

    def _refreshSelection(self) -> None:
        month_mode = self._selection_mode == "month"
        self._year_button.setText(str(self._selection_year) if month_mode else f"{self._year_start}–{self._year_start + 11}")
        for index, button in enumerate(self._choice_buttons):
            value = index + 1 if month_mode else self._year_start + index
            button.setText(self.locale().standaloneMonthName(value, QLocale.ShortFormat) if month_mode else str(value))
            button.setChecked(value == (self._current_month.month if month_mode else self._current_month.year))
        self._prev_btn.setEnabled(self._selection_year > 1 if month_mode else self._year_start > 1)
        self._next_btn.setEnabled(self._selection_year < 9999 if month_mode else self._year_start < 9988)
        self._selection_panel.layout().invalidate()
        self._selection_panel.layout().activate()
        self.layout().invalidate()
        self.layout().activate()
        self.updateGeometry()
        self._viewChanged.emit()

    def _pageSelection(self, step: int) -> None:
        if self._selection_mode == "month":
            self._selection_year = max(1, min(9999, self._selection_year + step))
        else:
            self._year_start = max(1, min(9988, self._year_start + 12 * step))
        self._refreshSelection()

    def _choosePeriod(self, index: int) -> None:
        month_mode = self._selection_mode == "month"
        year = self._selection_year if month_mode else self._year_start + index
        month = index + 1 if month_mode else self._current_month.month
        self.set_month(datetime(year, month, 1))
        (self._month_button if month_mode else self._year_button).setFocus()

    # ------------------------------------------------------------------ #
    # Signal-Handler                                                       #
    # ------------------------------------------------------------------ #

    def _make_day_handler(self, btn: DayButton):
        """Closure: emittiert datum_angeklickt mit dem Datum des Buttons."""
        def _handler(_checked: bool = False) -> None:
            if btn.day is not None:
                self.datum_angeklickt.emit(btn.day.date())
        return _handler
