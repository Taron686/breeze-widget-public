"""i18n adapter — :class:`Translator` wraps :class:`QTranslator` for Qt i18n.

Loads ``.qm`` files for one or more locales, installs them on the running
``QCoreApplication``, and emits ``languageChanged(locale)`` whenever the
active language changes.

The class only manages compiled Qt translation files (``.qm``). Generate
them with ``lrelease`` from your ``.ts`` source files.

Typical usage::

    from breezewidget import Translator

    tr = Translator(search_paths=[Path("translations")])
    tr.useSystemLocale()             # or tr.setLocale("de_DE")
    tr.languageChanged.connect(window.retranslateUi)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QLocale, QObject, QTranslator, Signal
from PySide6.QtCore import QCoreApplication


class Translator(QObject):
    """Manage application translations.

    Translation files are looked up by locale name (``de_DE``, ``de``, …)
    in each path of ``search_paths``. The first ``.qm`` file matching the
    pattern ``<prefix><locale>.qm`` is loaded. ``prefix`` defaults to
    ``""``; pass e.g. ``"breeze_"`` to look for ``breeze_de.qm``.

    Falls back to base locale (``de`` from ``de_DE``) when the specific
    file is missing.
    """

    languageChanged = Signal(str)

    def __init__(
        self,
        search_paths: Iterable[Path | str] | None = None,
        prefix: str = "",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._search_paths: list[Path] = [Path(p) for p in (search_paths or [])]
        self._prefix = prefix
        self._translator = QTranslator()
        self._installed = False
        self._current_locale: str = ""

    # -- search-path management --------------------------------------------

    def addSearchPath(self, path: Path | str) -> None:
        p = Path(path)
        if p not in self._search_paths:
            self._search_paths.append(p)

    def searchPaths(self) -> list[Path]:
        return list(self._search_paths)

    def setPrefix(self, prefix: str) -> None:
        self._prefix = prefix

    def prefix(self) -> str:
        return self._prefix

    # -- locale switching --------------------------------------------------

    def availableLocales(self) -> list[str]:
        """Return locale names with a matching ``.qm`` file in the search paths."""
        found: list[str] = []
        for path in self._search_paths:
            if not path.is_dir():
                continue
            for entry in path.glob(f"{self._prefix}*.qm"):
                stem = entry.stem
                if self._prefix and stem.startswith(self._prefix):
                    locale = stem[len(self._prefix):]
                else:
                    locale = stem
                if locale and locale not in found:
                    found.append(locale)
        return found

    def currentLocale(self) -> str:
        return self._current_locale

    def setLocale(self, locale: str) -> bool:
        """Load and install translations for *locale*.

        Returns ``True`` when a translation file was loaded successfully,
        ``False`` when no matching ``.qm`` file exists. In the failure
        case any previously installed translator is removed and the
        application falls back to the source language.
        """
        candidate = self._find_qm(locale)
        if candidate is None and "_" in locale:
            candidate = self._find_qm(locale.split("_", 1)[0])

        self._uninstall()

        if candidate is None:
            self._current_locale = ""
            self.languageChanged.emit("")
            return False

        new_translator = QTranslator()
        if not new_translator.load(str(candidate)):
            self._current_locale = ""
            self.languageChanged.emit("")
            return False

        self._translator = new_translator
        app = QCoreApplication.instance()
        if app is not None:
            app.installTranslator(self._translator)
            self._installed = True
        self._current_locale = locale
        self.languageChanged.emit(locale)
        return True

    def useSystemLocale(self) -> bool:
        """Detect the OS locale via :class:`QLocale.system` and load it."""
        return self.setLocale(QLocale.system().name())

    def clear(self) -> None:
        """Remove the active translator and revert to the source language."""
        self._uninstall()
        self._current_locale = ""
        self.languageChanged.emit("")

    # -- internals ---------------------------------------------------------

    def _find_qm(self, locale: str) -> Path | None:
        if not locale:
            return None
        filename = f"{self._prefix}{locale}.qm"
        for path in self._search_paths:
            candidate = path / filename
            if candidate.is_file():
                return candidate
        return None

    def _uninstall(self) -> None:
        if self._installed:
            app = QCoreApplication.instance()
            if app is not None:
                app.removeTranslator(self._translator)
            self._installed = False


__all__ = ["Translator"]
