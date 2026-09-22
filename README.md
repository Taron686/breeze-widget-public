<img width="1619" height="971" alt="BreezeWidget — PySide6 UI Framework" src="https://raw.githubusercontent.com/Taron686/breeze-widget-public/main/docs/breezewidget.png" />

# BreezeWidget

> This repository is an entirely vibe-coded, work-in-progress project for
> PySide6. The API is not yet final, internal structures may change, and the
> repository is currently intended primarily for development, testing,
> experimentation, and migrations.

BreezeWidget is a clean-room, local PySide6 widget and theming layer with a
Breeze-inspired look. The project aims to provide Qt/PySide6 desktop apps with
consistent windows, theme management, icons, navigation, status components,
input controls, cards, views, and demo interfaces, without depending on an
external GPL widget library.

## Current Status

The package is pre-1.0 and is being actively restructured. Its public API is
documented in [the API contract](https://github.com/Taron686/breeze-widget-public/blob/main/docs/api-contract.md) and covered by tests; anything outside
that documented interface is considered internal. The repository already
contains working demos, tests, local icons, theme and stylesheet infrastructure,
and a growing collection of PySide6 components, but it is not yet a stable
framework release.

## What You Can Do

- Install BreezeWidget locally and use it in your own PySide6 prototypes.
- Install published releases directly from PyPI using `pip install`.
- Run the demo applications to explore the current UI components.
- Run the tests to verify the documented public API and core behavior.
- Build your own widgets or stylesheet fragments using the existing theme and
  icon infrastructure.
- Freely fork, adapt, and reuse the project.

## Install from PyPI

```powershell
python -m pip install breeze-widget
```

The PyPI package is named `breeze-widget`; the Python import is
`breezewidget`.

## Install for Development

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

## Run the Demos

```powershell
.\.venv\Scripts\python.exe .\examples\breeze_demo.py
.\.venv\Scripts\python.exe .\examples\widget_demo.py
```

## Run the Tests

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest
```

## Public API

The root imports from `breezewidget` and the curated subsystem modules
`breezewidget.window`, `breezewidget.theme`, `breezewidget.icons`, and
`breezewidget.navigation` form the public interface. Details, symbol names,
stable Qt dynamic properties, and internal areas are documented in the API
contract in [the API contract](https://github.com/Taron686/breeze-widget-public/blob/main/docs/api-contract.md).

Avoid direct imports from deeper implementation modules, as these may be moved
or renamed during refactoring.

## License

BreezeWidget is released under the MIT License. You may freely use, copy,
modify, and redistribute the project at no cost. See [`LICENSE`](https://github.com/Taron686/breeze-widget-public/blob/main/LICENSE)
for details.
