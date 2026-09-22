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

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
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
QLabel#month_label {{
    color: {text};
    font-size: 16px;
    font-weight: bold;
    background: transparent;
    min-width: 110px;
}}
QPushButton#toggle_button {{
    border-radius: 15px;
    color: {text};
    font-size: 14px;
    font-weight: bold;
    background: transparent;
    border: none;
}}
QPushButton#toggle_button:hover   {{ background: {hover}; }}
QPushButton#toggle_button:pressed {{ background: {pressed}; }}

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

DayButton#day_number_event     {{ background: transparent; color: {text}; }}
DayButton#day_number_event:hover   {{ background: {hover}; }}
DayButton#day_number_event:pressed {{ background: {pressed}; }}

DayButton#day_number_today     {{ background: {today}; color: {today_text}; }}
DayButton#day_number_today:hover   {{ background: {today_hover}; }}
DayButton#day_number_today:pressed {{ background: {today_pressed}; color: {today_text}; }}

DayButton#day_number_today_event {{
    background: {today}; color: {today_text};
    border: none;
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
    return _QSS_TEMPLATE.format(
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
        self._month_label.setText(month.strftime("%b %Y").upper())
        self._populate_days()

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

        root.addLayout(self._build_header())

        divider = QFrame(self)
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(divider)

        # Body: [kw_widget][gap_kw][line_widget][gap_line][grid_col]
        # Alle Elemente werden immer gebaut; show/hide via _update_kw_visibility().
        # So können KW und Linie zur Laufzeit per set_show_week_numbers/line() umgeschaltet
        # werden ohne das Layout neu aufzubauen.
        body = QHBoxLayout()
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
        body.addLayout(grid_col)
        body.setAlignment(grid_col, Qt.AlignmentFlag.AlignTop)
        body.addStretch(1)

        root.addLayout(body)
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

        self._month_label = QLabel()
        self._month_label.setObjectName("month_label")
        self._month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._month_label.setMinimumWidth(110)

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

        for day_val, btn in zip(days, self._day_buttons):
            if day_val is not None:
                btn.set_day(day_val, activity_for_day(self._activities, month, day_val))
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

        # Jeder DayButton ruft unpolish/polish/update in update_type() und
        # set_selected() selbst auf — ein globales setStyleSheet() ist hier
        # nicht nötig und würde ein Full-Relayout auslösen.

    # ------------------------------------------------------------------ #
    # Navigation                                                           #
    # ------------------------------------------------------------------ #

    def _go_prev_month(self) -> None:
        first = datetime(self._current_month.year, self._current_month.month, 1)
        self.set_month(first - timedelta(days=1))

    def _go_next_month(self) -> None:
        year, month = self._current_month.year, self._current_month.month
        if month == 12:
            self.set_month(datetime(year + 1, 1, 1))
        else:
            self.set_month(datetime(year, month + 1, 1))

    # ------------------------------------------------------------------ #
    # Signal-Handler                                                       #
    # ------------------------------------------------------------------ #

    def _make_day_handler(self, btn: DayButton):
        """Closure: emittiert datum_angeklickt mit dem Datum des Buttons."""
        def _handler(_checked: bool = False) -> None:
            if btn.day is not None:
                self.datum_angeklickt.emit(btn.day.date())
        return _handler
