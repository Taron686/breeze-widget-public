<img width="400" alt="BreezeWidget — PySide6 UI Framework" src="https://raw.githubusercontent.com/Taron686/breeze-widget-public/main/docs/breezewidget-preview.png" />

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
`breezewidget.window`, `breezewidget.theme`, `breezewidget.icons`,
`breezewidget.navigation`, and `breezewidget.rich_text` form the public interface. Details, symbol names,
stable Qt dynamic properties, and internal areas are documented in the API
contract in [the API contract](https://github.com/Taron686/breeze-widget-public/blob/main/docs/api-contract.md).

Avoid direct imports from deeper implementation modules, as these may be moved
or renamed during refactoring.

## Rich-text table cells (opt-in)

```python
from PySide6.QtWidgets import QTableWidgetItem
from breezewidget import (
    TableWidget, RichTextTableItemDelegate, RichTextSegment, RICH_TEXT_ROLE,
)

table = TableWidget()
table.setRowCount(2)
table.setColumnCount(1)
table.setColumnWidth(0, 150)
delegate = RichTextTableItemDelegate(table)
table.setItemDelegate(delegate)
item = QTableWidgetItem("Mathe Sport")
item.setData(RICH_TEXT_ROLE, (
    RichTextSegment("Mathe", "#008000"), RichTextSegment(" Sport"),
))
table.setItem(0, 0, item)
table.setItem(1, 0, QTableWidgetItem("a" * 100))
table.setMinimumRowHeight(0, 72)
table.setMinimumRowHeight(1, 36)
table.setAutoRowHeightEnabled(True)
```

The delegate wraps long words with `QTextOption.WrapAtWordBoundaryOrAnywhere`;
pass `wrapMode=` to choose another mode. Display and editing share the same
document width, font and padding. Row sizing is separately opt-in and works
with other delegates too. Rows grow and shrink to their content/minimum after
model edits, column resizing, font/theme/DPI changes and row insertion/removal.
Horizontal spans use the full visible cell width, skip covered cell contents,
and reflow when `setSpan` or `clearSpans` changes the layout.
Disabling sizing leaves current row heights in place. Ordinary tables retain
their default delegate and height behavior.

Double-click to edit. Enter adds a paragraph; Tab/Shift+Tab commit and move;
Escape cancels. Select text and right-click → **Text color** to use a labeled
swatch or the Breeze custom color dialog. Color changes form one undo step,
including a selection spanning paragraphs. Menus and dialogs keep the active
editor and its selection alive. External rich-text paste into cells becomes
plain text. Standalone `RichTextEdit` provides the same menu with the usual
90-pixel minimum; table editors use a zero minimum.

The immutable segment tuple contains only text and optional RGB `#rrggbb`
foreground colors. `None` follows the item's foreground/theme. DisplayRole and
EditRole contain the exact concatenated text. Missing, malformed or mismatched
metadata displays as plain text. `richTextRole=` selects another user role;
the default is `Qt.UserRole + 1`. All four symbols are also available from the
stable `breezewidget.rich_text` module.

Use `editor.setSegments(...)`, `editor.segments()` and `editor.plainText()` to
round-trip data. Adjacent segments with equal color merge. A paragraph break
is `\n`, a soft break within a paragraph is U+2028, and an automatic line wrap
adds no text. Unlike Qt's `toPlainText()`, `plainText()` preserves soft breaks
and nonbreaking spaces. Empty paragraphs, emoji and color boundaries within
combining-character or emoji sequences also survive. This paragraph
representation leaves room for later block metadata without changing segments.
Paragraph separators retain their own color, including leading/trailing and
empty paragraphs.

Persist from `delegate.modelUpdated`, which fires **after** successful updates
to plain text and the full segment tuple:

```python
def save_cell(index):
    text = index.data()  # DisplayRole; EditRole has the same text
    segments = index.data(delegate.richTextRole())
    # Serialize/save both values in your application here.

delegate.modelUpdated.connect(save_cell)
```

The delegate calls `model.setItemData` with all three roles. Custom models must
support them; implement transactional validation there if rejection is possible.
A rejected update emits no `modelUpdated`. The emitted index follows the edited
item if the update sorts the model; no signal fires if the update removes the
item or resets the model. Raw `dataChanged`/`itemChanged`
notifications can expose intermediate roles in custom models, so use
`modelUpdated` for persistence. BreezeWidget does not serialize application data
or commit an active editor merely because a save button was pressed.

### Checklist paragraphs (opt-in)

```python
from breezewidget import RichTextBlock, RICH_TEXT_BLOCKS_ROLE

delegate.setChecklistsEnabled(True)
blocks = (
    RichTextBlock((RichTextSegment("Copy worksheets", "#008000"),), True),
    RichTextBlock((RichTextSegment("Lesson preparation"),)),  # ordinary paragraph
    RichTextBlock((RichTextSegment("Inform parents"),), False),
    RichTextBlock((RichTextSegment("Prepare the exam"),), False),
)
item = QTableWidgetItem("\n".join("".join(s.text for s in b.segments) for b in blocks))
item.setData(RICH_TEXT_BLOCKS_ROLE, blocks)
table.setItem(0, 0, item)
```

Click a task marker once to toggle it, including outside the editor. Ordinary
text clicks keep the view's normal selection/editing behavior. A cell's native
`CheckStateRole` checkbox remains independent. Long task paragraphs wrap with
one marker, and automatic row sizing includes list indentation.

In an enabled editor, right-click **Insert checkbox**, **Remove checkbox**, or
**Toggle completed**. The actions also work from the keyboard context menu.
Insert/remove apply to every selected paragraph; a selection ending exactly at
the next paragraph start excludes that paragraph. Existing task states and text
colors survive conversion. Enter at a task's end creates an open task; Enter
in an empty task ends the list. Insert, remove and toggle each support undo/redo.
Multiline plain-text paste/insertion also creates open tasks in one undo step.
At the paragraph start the original task state follows its existing text;
otherwise it stays with the first part, as when pressing Enter.
Standalone HTML clipboard content keeps its incoming text formatting and uses
the same task-state rule. Replacing a selection preserves its insertion format.
Surviving prefix/suffix paragraphs keep their own states; fully removed tasks
do not transfer completion to pasted text. If surviving text joins into one
paragraph, its prefix state takes precedence.

`RichTextBlock(segments, checked=None, *, separatorColor=None)` is frozen.
`segments` must be a tuple of `RichTextSegment` without paragraph separators;
U+2028 soft breaks remain valid. `checked` accepts only `True`, `False`, or
`None` (ordinary text). Blocks are joined with LF. The optional RGB
`separatorColor` preserves the color of the LF following that block, including
empty paragraphs; it is ignored for the final block. Text, emoji, NBSP, colors
and states round-trip through `editor.setBlocks(...)` / `editor.blocks()`.
Adjacent equal-color segments merge. Loading blocks clears undo history and
does not itself enable interaction.

Use `setChecklistsEnabled(True)` on a standalone `RichTextEdit` or the delegate;
`isChecklistsEnabled()` reports the switch, which defaults to False. Public
editor actions are `insertChecklist()`, `removeChecklist()`, and
`toggleChecklistItem()`. Both editor and delegate offer
`setChecklistMenuLabels(insert, remove, toggle)` for application translations,
for example `("Als Checkliste", "Checkbox entfernen", "Erledigt umschalten")`.
Defaults use Qt translation; delegate labels apply to newly created editors.
Read-only and disabled editors/items cannot change task state through actions.

The default block role is 258, or 259 when the existing custom color role is
258. Omitting `richTextBlocksRole` or passing None chooses this free default;
pass an explicit user role to choose another role distinct from `richTextRole=`
(default 257). Both have
matching accessors. With checklists enabled, valid blocks whose text matches
the model are authoritative over color metadata. Missing, invalid or stale
blocks fall back to the existing color/plain-text behavior without overwriting
plain text. Disabled delegates keep their previous color-only behavior.

Enabled commits and external toggles submit all four roles together via
`setItemData`: DisplayRole, EditRole, color segments, and blocks. Persist all
of them from `modelUpdated`. External toggles additionally emit
`checklistItemToggled(index, block_index, checked)` once after accepted updates;
editor toggles use the normal commit. Rejection emits neither success signal.
Persistent indexes follow synchronous sorting; reset/removal suppresses signals,
including a reset/removal in a `modelUpdated` subscriber before the toggle
signal. Custom models own transactional validation/rollback. BreezeWidget
does not add application persistence or Excel dependencies.

Default labels use Qt translation. Customize a standalone editor directly, or
customize delegate-created editors through the standard `createEditor` hook:

```python
class LocalizedDelegate(RichTextTableItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        editor.setColorPresets([("Grün", "#008000"), ("Rot", "#ff0000")])
        editor.setColorMenuLabels("Textfarbe", "Eigene Farbe …")
        return editor
```

The data-views gallery includes narrow columns, long words, six manual lines,
multiple colors and different row minimums.

## License

BreezeWidget is released under the MIT License. You may freely use, copy,
modify, and redistribute the project at no cost. See [`LICENSE`](https://github.com/Taron686/breeze-widget-public/blob/main/LICENSE)
for details.
