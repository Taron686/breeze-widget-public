from __future__ import annotations

from .palette import BreezePalette


class StyleSheetBase:
    """Base class for stylesheet providers.

    Providers return one self-contained QSS fragment for a widget family.
    """

    def build(self, palette: BreezePalette) -> str:
        raise NotImplementedError
