"""Phase 7c — Translator."""
from __future__ import annotations

import pytest

from breezewidget import Translator


def test_initial_state(qapp):
    tr = Translator()
    assert tr.currentLocale() == ""
    assert tr.searchPaths() == []
    assert tr.availableLocales() == []


def test_add_search_path_dedup(qapp, tmp_path):
    tr = Translator()
    tr.addSearchPath(tmp_path)
    tr.addSearchPath(tmp_path)
    assert tr.searchPaths() == [tmp_path]


def test_constructor_search_paths(qapp, tmp_path):
    tr = Translator(search_paths=[tmp_path])
    assert tr.searchPaths() == [tmp_path]


def test_prefix_setter_getter(qapp):
    tr = Translator(prefix="breeze_")
    assert tr.prefix() == "breeze_"
    tr.setPrefix("app_")
    assert tr.prefix() == "app_"


def test_available_locales_discovers_qm_files(qapp, tmp_path):
    (tmp_path / "de.qm").touch()
    (tmp_path / "fr_FR.qm").touch()
    (tmp_path / "ignored.txt").touch()
    tr = Translator(search_paths=[tmp_path])
    locales = sorted(tr.availableLocales())
    assert locales == ["de", "fr_FR"]


def test_available_locales_with_prefix(qapp, tmp_path):
    (tmp_path / "breeze_de.qm").touch()
    (tmp_path / "breeze_en.qm").touch()
    (tmp_path / "other_es.qm").touch()
    tr = Translator(search_paths=[tmp_path], prefix="breeze_")
    locales = sorted(tr.availableLocales())
    assert locales == ["de", "en"]


def test_available_locales_skips_missing_dir(qapp, tmp_path):
    tr = Translator(search_paths=[tmp_path / "missing"])
    assert tr.availableLocales() == []


def test_set_locale_missing_returns_false(qapp, tmp_path):
    tr = Translator(search_paths=[tmp_path])
    seen = []
    tr.languageChanged.connect(seen.append)
    assert tr.setLocale("de") is False
    assert tr.currentLocale() == ""
    assert seen == [""]


def test_set_locale_invalid_qm_returns_false(qapp, tmp_path):
    # An empty file is not a valid .qm — load fails; state must reset.
    (tmp_path / "de.qm").write_text("not a real qm", encoding="utf-8")
    tr = Translator(search_paths=[tmp_path])
    assert tr.setLocale("de") is False
    assert tr.currentLocale() == ""


def test_set_locale_falls_back_to_base_language(qapp, tmp_path, monkeypatch):
    # de.qm exists, de_DE.qm does not — fallback should look at "de".
    (tmp_path / "de.qm").touch()
    tr = Translator(search_paths=[tmp_path])

    seen_paths: list[str] = []
    real_load = tr._translator.load

    def spy_load(self, path):  # type: ignore[no-untyped-def]
        seen_paths.append(path)
        return False

    monkeypatch.setattr("PySide6.QtCore.QTranslator.load", spy_load)
    tr.setLocale("de_DE")
    # _find_qm tried de_DE first (missing), then de (found).
    assert any(p.endswith("de.qm") for p in seen_paths)


def test_use_system_locale_calls_set_locale(qapp, tmp_path, monkeypatch):
    tr = Translator(search_paths=[tmp_path])
    captured = []
    monkeypatch.setattr(tr, "setLocale", lambda loc: captured.append(loc) or False)
    tr.useSystemLocale()
    assert len(captured) == 1
    assert isinstance(captured[0], str)


def test_clear_emits_signal_and_resets(qapp):
    tr = Translator()
    seen = []
    tr.languageChanged.connect(seen.append)
    tr.clear()
    assert tr.currentLocale() == ""
    assert seen == [""]


def test_set_locale_empty_string_returns_false(qapp):
    tr = Translator()
    assert tr.setLocale("") is False
