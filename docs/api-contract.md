# BreezeWidget — Public API Contract

This document defines the public API of the `breezewidget` package. Anything
listed here is part of the contract and may not be renamed, removed, or
silently change behavior without a major-version bump. Anything **not** listed
is internal and may move at any time.

> Status: pre-1.0. Property names and symbol identifiers are already considered
> stable; signatures may still gain optional parameters. Internal layout may change during refactoring.

---

## 1. Public symbols (`from breezewidget import …`)

The 140 names below are re-exported from `breezewidget/__init__.py` and are
guaranteed to be importable from the package root. Importing the same name
from a deeper module path is only part of the contract for the curated
subsystem modules listed in section 1a.

### Core infrastructure
`BreezeRouter`, `ExceptionHandler`, `Translator`,
`PropertyAnimation`, `BackgroundColorAnimation`, `DropShadowAnimation`,
`BreezeConfig`, `ConfigItem`, `RangeConfigItem`, `OptionsConfigItem`, `ColorConfigItem`,
`ConfigValidator`, `RangeValidator`, `OptionsValidator`, `BoolValidator`,
`FolderValidator`, `FolderListValidator`,
`ConfigSerializer`, `ColorSerializer`, `EnumSerializer`

### Theme & palette
`Theme`, `ThemeManager`, `OSThemeListener`, `BreezePalette`,
`StyleSheetBase`, `StyleSheetManager`,
`setTheme`, `setThemeColor`, `applyTheme`, `getPalette`, `isDarkTheme`,
`setCustomStyleSheet`

### Icons
`BreezeIcon`, `IconRegistry`, `icon_from`

### Buttons
`PushButton`, `PrimaryPushButton`, `TransparentPushButton`,
`ToolButton`, `PrimaryToolButton`, `TransparentToolButton`, `ToggleButton`,
`HyperlinkButton`, `DropDownPushButton`, `SplitPushButton`,
`PillPushButton`, `BreezeThemeSwitch`, `IconWidget`

### Text inputs
`LineEdit`, `SearchLineEdit`, `PasswordLineEdit`,
`TextEdit`, `PlainTextEdit`,
`RichTextEdit`, `RichTextSegment`, `RICH_TEXT_ROLE`, `RichTextTableItemDelegate`,
`RichTextBlock`, `RICH_TEXT_BLOCKS_ROLE`,
`ComboBox`, `EditableComboBox`,
`SpinBox`, `DoubleSpinBox`,
`DateEdit`, `TimeEdit`, `DateTimeEdit`,
`Slider`, `ClickableSlider`

### Pickers, views, layout, menu & media
`ExpandLayout`, `FlowLayout`,
`RoundMenu`, `CheckableMenu`, `CommandBar`,
`CalendarPicker`, `FastCalendarPicker`, `DatePicker`, `TimePicker`,
`PipsPager`, `SmoothScrollArea`,
`ListView`, `TableView`, `TableWidget`, `TableItemDelegate`, `TreeView`,
`FlipView`, `CycleListWidget`, `Avatar`,
`MediaPlayer`, `PlayBar`, `VideoWidget`

### Status & progress
`ProgressBar`, `IndeterminateProgressBar`,
`InfoBar`, `InfoBarPosition`,
`InfoBadge`, `DotInfoBadge`, `IconInfoBadge`,
`ProgressRing`, `IndeterminateProgressRing`,
`StateToolTip`,
`MessageBox`

### Flyout
`Flyout`, `FlyoutPlacement`, `FlyoutAnimationType`, `TeachingTip`

### Choice
`CheckBox`, `RadioButton`, `SwitchButton`

### Cards & labels
`CardWidget`, `SimpleCardWidget`, `ElevatedCardWidget`,
`HeaderCardWidget`, `SettingCard`, `SettingCardGroup`,
`SwitchSettingCard`, `ComboBoxSettingCard`, `RangeSettingCard`,
`PushSettingCard`, `HyperlinkCard`, `ExpandSettingCard`,
`OptionsSettingCard`, `CustomColorSettingCard`,
`BodyLabel`, `CaptionLabel`, `StrongBodyLabel`,
`SubtitleLabel`, `TitleLabel`

### Navigation & window
`NavigationInterface`, `NavigationItemPosition`,
`Pivot`, `PivotItem`, `SegmentedWidget`,
`BreadcrumbBar`, `BreadcrumbItem`, `TabBar`, `TabItem`,
`BreezeWindow`, `BreezeTitleBar`,
`MSBreezeWindow`, `SplitBreezeWindow`

---

## 1a. Public subsystem modules

The following subsystem modules are also stable import paths. Their `__all__`
lists are part of the public contract:

- `breezewidget.window`: `BreezeWindow`, `BreezeTitleBar`, `MSBreezeWindow`,
  `SplitBreezeWindow`, `BreezeSplashScreen`, `MaterialEffect`,
  `apply_material`
- `breezewidget.theme`: `Theme`, `ThemeManager`, `BreezePalette`,
  `setTheme`, `setThemeColor`, `applyTheme`, `getPalette`, `isDarkTheme`,
  `StyleSheetBase`, `StyleSheetManager`, `build_stylesheet`,
  `setCustomStyleSheet`, `OSThemeListener`
- `breezewidget.icons`: `BreezeIcon`, `icon_from`, `IconRegistry`
- `breezewidget.rich_text`: `RichTextSegment`, `RICH_TEXT_ROLE`,
  `RichTextEdit`, `RichTextTableItemDelegate`, `RichTextBlock`, `RICH_TEXT_BLOCKS_ROLE`
- `breezewidget.navigation`: `NavigationInterface`, `NavigationItemPosition`,
  `Pivot`, `PivotItem`, `SegmentedWidget`, `BreadcrumbBar`,
  `BreadcrumbItem`, `TabBar`, `TabItem`

All other subpackages and direct implementation modules remain internal unless
listed here.

---

## 2. Stable Qt dynamic properties

Custom widgets can opt into the Breeze stylesheet by setting these properties.
The names live in `breezewidget.constants`; downstream code should import
them from there rather than typing the strings.

| Constant | Property name | Allowed values | Set by |
|---|---|---|---|
| `PROP_ROLE` | `breezeRole` | `ROLE_PRIMARY` (`"primary"`), `ROLE_TRANSPARENT` (`"transparent"`) | `PrimaryPushButton`, `PrimaryToolButton`, `TransparentPushButton`, `TransparentToolButton` |
| `PROP_LABEL` | `breezeLabel` | `LABEL_CAPTION` (`"caption"`), `LABEL_BODY_STRONG` (`"bodyStrong"`), `LABEL_SUBTITLE` (`"subtitle"`), `LABEL_TITLE` (`"title"`) | `CaptionLabel`, `StrongBodyLabel`, `SubtitleLabel`, `TitleLabel` |
| `PROP_CARD` | `breezeCard` | `CARD_DEFAULT` (`"true"`), `CARD_ELEVATED` (`"elevated"`) | `CardWidget`, `ElevatedCardWidget` |
| `PROP_INFO_BAR` | `breezeInfoBar` | `True` | `InfoBar` |
| `PROP_THEME_PILL` | `breezeThemePill` | `True` | `BreezeThemeSwitch` |
| `PROP_PILL` | `breezePill` | `"true"` | `PillPushButton` |
| `PROP_SWITCH` | `breezeSwitch` | `True` | `SwitchButton` *(painted widget; no QSS selector required)* |
| `PROP_NAVIGATION` | `breezeNavigation` | `True` | `NavigationInterface` |
| `PROP_NAVIGATION_COMPACT` | `breezeNavigationCompact` | `bool` | `NavigationInterface` (compact state) |
| `PROP_NAVIGATION_ITEM` | `breezeNavigationItem` | `True` | items added via `NavigationInterface.addItem` |
| `PROP_NAVIGATION_ITEM_COMPACT` | `breezeNavigationItemCompact` | `bool` | nav items in compact mode |
| `PROP_NAVIGATION_INDICATOR` | `breezeNavigationIndicator` | `True` | selection indicator frame |
| `PROP_TITLE_BAR` | `breezeTitleBar` | `True` | `BreezeTitleBar` |
| `PROP_TITLE_LABEL` | `breezeTitleLabel` | `True` | title text label |
| `PROP_TITLE_ICON` | `breezeTitleIcon` | `True` | window icon label |
| `PROP_TITLE_BUTTON` | `breezeTitleButton` | `True` | every titlebar button |
| `PROP_TITLE_BUTTON_ROLE` | `breezeTitleButtonRole` | `TITLE_BUTTON_ROLE_BACK` / `_ACTION` / `_CLOSE` / `_MINIMIZE` / `_MAXIMIZE` / `_RESTORE` | titlebar buttons |
| `PROP_BADGE` | `breezeBadge` | `BADGE_DEFAULT` / `_INFO` / `_SUCCESS` / `_ATTENTION` / `_WARNING` / `_DANGER` | `InfoBadge`, `DotInfoBadge`, `IconInfoBadge` |
| `PROP_STATE_TOOLTIP` | `breezeStateToolTip` | `True` | `StateToolTip` |
| `PROP_FLYOUT` | `breezeFlyout` | `True` | `Flyout` |
| `PROP_TEACHING_TIP` | `breezeTeachingTip` | `True` | `TeachingTip` |
| `PROP_PIVOT` | `breezePivot` | `"true"` | `Pivot` |
| `PROP_PIVOT_ITEM` | `breezePivotItem` | `"true"` | `PivotItem` |
| `PROP_SEGMENTED` | `breezeSegmented` | `"true"` | `SegmentedWidget` |
| `PROP_SEGMENTED_ITEM` | `breezeSegmentedItem` | `"true"` | items added via `SegmentedWidget.addItem` |
| `PROP_BREADCRUMB` | `breezeBreadcrumb` | `"true"` | `BreadcrumbBar` |
| `PROP_BREADCRUMB_ITEM` | `breezeBreadcrumbItem` | `"true"` | `BreadcrumbItem` |
| `PROP_TAB_BAR` | `breezeTabBar` | `"true"` | `TabBar` |
| `PROP_TAB_ITEM` | `breezeTabItem` | `"true"` | `TabItem` |

The constants module also exposes the allowed string values
(`ROLE_PRIMARY`, `LABEL_CAPTION`, …). Use those instead of literals so a
rename of a value in a future release is a single-place change.

---

## 3. Stable behaviors

- `setTheme(value, target=None)` accepts a `Theme` enum or its string value
  (`"light"`, `"dark"`, `"auto"`). It mutates the active theme and rebuilds
  the stylesheet on `target` (defaults to the running `QApplication`).
- `setThemeColor(value, target=None)` accepts any `QColor`-compatible input.
- `setCustomStyleSheet(widget, light_qss, dark_qss=None)` applies the
  stylesheet matching the resolved theme and refreshes it when the theme or
  accent color changes.
- `ThemeManager.instance()` returns the singleton theme manager. Its
  `themeChanged(Theme)` and `themeColorChanged(QColor)` signals fire when the
  stored theme or accent color changes. The root helper functions delegate to
  this manager.
- `StyleSheetManager.register(widget_type, provider)` adds or replaces a
  `StyleSheetBase` provider. `StyleSheetManager.unregister(widget_type)`
  removes it. Stylesheet builds include all registered provider fragments.
- `getPalette()` returns a `BreezePalette` whose fields are documented as
  `#rrggbb` strings.
- `isDarkTheme()` returns `True` when the resolved theme is dark, including
  the `Theme.AUTO` case.
- `BreezeIcon(value).icon(color=None)` and `icon_from(value, color=None)`
  return a non-null `QIcon` for every member of `BreezeIcon`. `icon_from`
  passes existing `QIcon` instances through unchanged and falls back to an
  empty icon for unknown strings. Built-in `BreezeIcon` members are backed by
  local Tabler outline SVG assets.
- `IconRegistry.get(value, color=None, size=32, stroke_width=None, **attributes)`
  returns cached icons keyed by icon name/path, color, size, stroke width, and
  SVG attributes. For SVG icons, `color` is written into `stroke` for outline
  icons and `fill` for filled icons; additional keyword arguments are written
  as SVG attributes with underscores converted to hyphens. `register_painter(name)`
  and `register_svg(name, path)` add rendering backends.
- `NavigationInterface`:
  - `addItem(routeKey, icon, text, onClick=None, selectable=True, position=NavigationItemPosition.TOP, tooltip=None)` returns the created button.
  - `setCompact(compact, animated=False)` switches between compact and
    expanded layout; `isCompact()` reports the current state.
  - `currentItemChanged(str)` fires when a route is activated.
- `BreezeWindow`:
  - `addSubInterface(interface, icon, text, position=…, routeKey=None)` adds
    a page and registers a navigation entry.
  - `switchTo(interface)` accepts either a `routeKey` or the widget reference.
  - `setNavigationCompact(compact, animated=False)` and
    `toggleNavigation(animated=True)` control the side-nav.
  - `enableNavigationMenuButton(visible=True)` wires the back-button slot to
    toggle the navigation.
- `InfoBar`:
  - Class methods `info`, `success`, `warning`, `error` create and show a
    notification. `duration=0` disables auto-close.
  - `InfoBarPosition` has six members: `TOP`, `TOP_RIGHT`, `TOP_LEFT`,
    `BOTTOM`, `BOTTOM_RIGHT`, `BOTTOM_LEFT`.
- `InfoBadge`, `DotInfoBadge`, and `IconInfoBadge` expose the variants
  `default`, `info`, `success`, `attention`, `warning`, and `danger`.
- `ProgressRing` supports determinate progress through `setRange`/`setValue`;
  `IndeterminateProgressRing` animates while visible.
- `StateToolTip.setState(True)` switches the tooltip from running to done and
  emits `closed` when dismissed.
- `Flyout` hosts arbitrary content anchored to a target widget. `TeachingTip`
  is a preset flyout with title, body text, close button, and optional action
  buttons.
- `Pivot`, `SegmentedWidget`, `BreadcrumbBar`, and `TabBar` expose `currentChanged`
  route/key signals for lightweight navigation surfaces.
- `ClickableSlider` sets its value from left-click/drag position.
- `TableWidget` is a Breeze-styled `QTableWidget` wrapper for item-based
  tables. It supports `setBorderVisible(bool)` and `setBorderRadius(int)`.
  `TableItemDelegate` is the matching default delegate hook.
- `TableWidget.setAutoRowHeightEnabled(enabled)` opts into coalesced content
  sizing; `isAutoRowHeightEnabled()` defaults to `False`. Sizing uses the
  maximum delegate size hint across visible columns and reacts to model,
  column width, delegate, font, style, theme and DPI changes.
  Horizontal spans use their visible rendered width and ignore covered cells;
  `setSpan` and `clearSpans` schedule coalesced sizing when enabled.
  `setMinimumRowHeight(row, height)` sets a nonnegative pixel floor for an
  existing row (invalid row raises `IndexError`). Floors follow row insertion
  and removal; model reset clears them. Disabling retains current heights.
- `RichTextSegment(text: str, color: str | None = None)` is immutable.
  `color` is an explicit RGB `#rrggbb` (case normalized) or `None` for the
  item's/theme's default foreground. Invalid text/color raises
  `TypeError`/`ValueError`. Concatenated segment text is exactly the plain
  DisplayRole/EditRole text. Paragraph boundaries are `\n`; U+2028 is a
  soft break inside a paragraph. Automatic wrapping adds no characters.
  NBSP, emoji, spaces and empty paragraphs are preserved. Segment boundaries
  do not identify paragraphs; a future block model can split at `\n`.
- `RICH_TEXT_ROLE` is `int(Qt.UserRole) + 1` (257), transporting
  `tuple[RichTextSegment, ...]`. Missing, invalid or mismatched metadata
  falls back to plain text. Segment loading also accepts a list. Adjacent
  equal-color segments are merged on extraction and empty segments omitted.
- `RichTextEdit(parent=None, *, cellMode=False)` adds the color submenu while
  retaining standard edit actions. `setSegments(segments)` replaces content
  and clears undo history; `segments()` returns normalized color segments;
  `plainText()` preserves soft breaks/NBSP (unlike Qt's `toPlainText()`).
  `applyTextColor(color)` colors only the selection in one undo step.
  `setColorPresets([(label, color), ...])` replaces the eight labeled swatches;
  `setColorMenuLabels(title, customColor)` overrides submenu/dialog labels.
  Defaults use Qt translation. `isFormattingPopupOpen()` remains true through
  nested menus and the ColorDialog transition. Cancel preserves text/colors.
  Cell mode has minimum height 0 and plain-text external paste; standalone
  RichTextEdit/TextEdit keep the 90-pixel minimum.
- `RichTextTableItemDelegate(parent=None, *, richTextRole=RICH_TEXT_ROLE,
  wrapMode=QTextOption.WrapAtWordBoundaryOrAnywhere)` is opt-in, with
  `richTextRole()`/`wrapMode()` accessors. It shares document metrics with its
  RichTextEdit editor, keeps Qt decoration/check hit geometry and Breeze
  selection styling. Enter inserts a paragraph, Tab/Shift+Tab commit and move,
  Escape cancels. A formatting popup never ends the editing session.
  `modelUpdated(QModelIndex)` fires after a successful `model.setItemData`
  update of DisplayRole, EditRole and the configured segment role. It is the
  public persistence observation point: raw model `dataChanged`/item change
  notifications may occur while a custom model updates individual roles.
  A rejected update does not emit `modelUpdated`; custom models are
  responsible for transactional validation/rollback in `setItemData`.
  The emitted index follows the edited item through synchronous sorting;
  updates that remove the item or reset the model do not emit it.
- `RichTextBlock(segments: tuple[RichTextSegment, ...], checked: bool | None = None,
  *, separatorColor: str | None = None)` is immutable. Only actual bool or None
  are accepted; None is ordinary text. Segments contain one paragraph (no LF,
  CR or U+2029); U+2028 remains a soft break. `separatorColor` is the normalized
  RGB color of the following LF and is ignored on the last block.
- `RICH_TEXT_BLOCKS_ROLE` is 258. It transports a tuple of RichTextBlock; loading
  also accepts a list. With checklists enabled, valid blocks matching the plain
  model text are authoritative over color segments. Missing, invalid or stale
  blocks fall back to existing plain/color-role data without replacing text.
- `RichTextEdit.setChecklistsEnabled(enabled)` / `isChecklistsEnabled()` control
  checklist actions and mouse/Enter behavior; default False. `setBlocks(blocks)`
  replaces content and clears undo history independently of activation;
  `blocks()` extracts normalized paragraphs, states and separator colors.
  `insertChecklist()` / `removeChecklist()` affect selected paragraphs (exclude
  a selection ending at the next paragraph start); existing task states survive
  insertion. `toggleChecklistItem()` toggles the current task. Each action is
  one undo step and respects read-only/disabled state. Enter at a task end adds
  an open task; at its start the existing task's state follows its text; in an
  empty task Enter converts it to ordinary text. Soft breaks remain in one task.
  Multiline plain-text paste/insertion follows the same rule: the existing task
  state follows its text at the paragraph start, otherwise remains on the first
  part; new task paragraphs start open, with the whole insertion in one undo step.
  Standalone rich clipboard insertion preserves incoming HTML formatting while
  following the same task-state rule. Selection replacement preserves the native
  insertion foreground and character format.
  Surviving prefix/suffix paragraphs keep their own task states when a selection
  is replaced; fully removed tasks do not transfer completion to pasted text.
  If surviving text joins into one paragraph, its prefix state takes precedence.
  `setChecklistMenuLabels(insert, remove, toggle)` overrides Qt-translated labels.
- `RichTextTableItemDelegate` additionally accepts `richTextBlocksRole=None`, with
  a matching accessor. Omitted/None chooses 258, or 259 when the existing
  `richTextRole` is 258. Explicitly configured roles must be distinct user roles.
  `setChecklistsEnabled(enabled)` / `isChecklistsEnabled()` default to False.
  `setChecklistMenuLabels(insert, remove, toggle)` configures new cell editors.
  Enabled commits submit DisplayRole, EditRole, color segments and blocks in one
  `setItemData`. Native markers can be clicked without opening an editor on
  enabled editable items. `checklistItemToggled(index, block_index, checked)`
  fires once after an accepted external toggle, following `modelUpdated`.
  Both respect synchronous sorting/reset/removal; a reset/removal by a
  modelUpdated subscriber suppresses the follow-on toggle signal. Local editor
  toggles persist through regular commit and do not emit checklistItemToggled.
  Native cell CheckStateRole indicators remain independent. Disabling the
  delegate restores color-only behavior and leaves stored block metadata alone.
- `PrimaryToolButton` sets `breezeRole="primary"`. `IconWidget` displays a
  `BreezeIcon`, registered icon string, path, or `QIcon`.
- `FastCalendarPicker(parent=None, date=None)` is a parent-first wrapper
  around `CalendarPicker` for qfluent-compatible migrations.
- `DropDownPushButton` owns a `QMenu`; `SplitPushButton` exposes a main
  `clicked()` signal plus a separate menu button; `PillPushButton` sets
  `breezePill="true"`.
- `DoubleSpinBox`, `DateEdit`, `TimeEdit`, and `DateTimeEdit` are Breeze-sized
  wrappers around the matching Qt input widgets. Date widgets enable calendar
  popups.
- `HeaderCardWidget` exposes `titleLabel`, `headerLayout`, and `viewLayout`.
- `SettingCard` exposes `titleLabel`, `captionLabel`, `iconLabel`, and
  `actionLayout`; specialized setting cards expose their embedded controls
  (`switchButton`, `comboBox`, `slider`, `button`, `segmentedWidget`) and emit
  matching change/action signals.
- `SettingCardGroup.addSettingCard(card)` appends a settings row and returns it.
- `BreezeConfig` is a `QObject` container for `ConfigItem` instances declared
  as class attributes. `load(path=None)` reads JSON (`{group: {key: value}}`)
  into the items; `save(path=None)` writes them. Both accept an explicit path
  or fall back to the path passed to `__init__`. `valueChanged(group, key, value)`
  re-emits each item's individual `valueChanged` signal. Validators
  (`RangeValidator`, `OptionsValidator`, `BoolValidator`, `FolderValidator`,
  `FolderListValidator`) silently correct invalid values; serializers
  (`ColorSerializer`, `EnumSerializer`) handle non-JSON-native types.
- `ExceptionHandler` installs as `sys.excepthook` (`install()` / `uninstall()`).
  Sinks are independent and best-effort: optional `log_file` (append-mode
  with timestamp), optional `show_dialog` (uses Breeze `Dialog`), optional
  `callback`. `exceptionRaised(type, exc, tb)` Qt signal fires for every
  caught exception. `KeyboardInterrupt` is forwarded to the previous hook.
  `chain_previous=True` re-invokes the prior `sys.excepthook` after the
  sinks run.
- `Translator` wraps `QTranslator` for Qt i18n. `addSearchPath(path)` adds
  a directory to scan for `<prefix><locale>.qm` files. `setLocale(name)`
  loads and installs the matching `.qm` (with base-language fallback so
  `de_DE` falls back to `de`); returns `True` on success. `useSystemLocale()`
  reads `QLocale.system().name()`. `clear()` removes the translator and
  reverts to the source language. `languageChanged(locale)` fires after
  every locale change (including failure, where the locale is `""`).
  `availableLocales()` lists discovered locale names.
- `OSThemeListener` polls the OS dark/light setting (Win: `winreg` key
  `Personalize\AppsUseLightTheme`; macOS: `defaults read -g
  AppleInterfaceStyle`; Linux: `GTK_THEME` env-var hint). `start()` /
  `stop()` control polling at `setInterval(ms)` cadence (min 100 ms).
  `osThemeChanged(bool)` fires when the OS state flips (and once on
  start). `isOSDark()` returns the current detected value without
  starting the timer.
- `PropertyAnimation` is a `QPropertyAnimation` subclass with Breeze
  defaults (180 ms, `OutCubic`) and chainable setters: `from_(value)`,
  `to(value)`, `withDuration(ms)`, `withEasing(curve)`. Property name
  may be passed as `bytes` or `str`.
- `BackgroundColorAnimation(target_widget, initial)` animates a widget's
  background color via a `backgroundColor` Q_PROPERTY; on every tick it
  rewrites the widget's stylesheet. `animateTo(color)` runs the
  transition from the current color.
- `DropShadowAnimation(target_widget, color, offset, initial_blur)`
  attaches a `QGraphicsDropShadowEffect` and animates its blur radius
  via `animateBlur(target_blur)`. `detach()` restores the previous
  graphics effect.

---

## 4. What is *not* public API

Treating any of the following as API is undefined behavior; they may be
removed, renamed, or change semantics in any release:

- Anything whose name starts with `_` (single or double underscore).
- The exact text content and structure of the stylesheet returned by
  `breezewidget.theme.build_stylesheet`.
- Internal state on `ThemeManager`, `StyleSheetManager`, and `IconRegistry`
  such as caches, provider lists, and stored colors.
- Helper classes such as `_BreezeWidgetMixin`.
- Internal dynamic properties prefixed with `_breeze` (e.g.
  `_breezeIconSource`, `_breezeCaptionRole`).
- The `_routes` dictionary on `BreezeWindow`.
- Imports from non-curated submodules (`from breezewidget.widgets import …`,
  `from breezewidget.dialogs import …`) and direct implementation modules
  (`from breezewidget.window._navigation import …`). Non-curated sub-module
  layout will change during the framework refactor.
- The fact that `MSBreezeWindow` and `SplitBreezeWindow` are currently
  thin aliases — they will gain distinct behavior in a later phase.

---

## 5. Versioning policy

- Patch (`0.2.x`): bug fixes, internal refactors, no API change.
- Minor (`0.x.0`): additive API changes (new symbols, new optional
  parameters, new property values).
- Major (`x.0.0`): breaking changes to anything in section 1, 2, or 3.

The `tests/` suite is the executable form of this contract — every public
symbol, property name, and stable behavior listed here has at least one test.
