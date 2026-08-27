---
last_reviewed: 2026-08-27
---

# Acro TD Widgets

Widget framework for building custom in-TD UIs from a reusable library of UI primitives.

## What it does

`AcroWidgets` (`/AcroWidgets`, shortcut `op.AW`, extension `ext.AcroWidgets`) provides:

- A **widget registry** that discovers widgets tagged `widget` under any `widgetFolder`-tagged container in the scene
- A **container primitive** (`AcroWidgetContainer`) — the framework's `<div>`. Holds exactly one widget, supports drag / drop / copy / cut / paste, undo-aware swap semantics, arbitrary nesting
- A **UI primitive library** — buttons, button arrays, pages with tabs, resizable matrix layouts, popup windows
- A **component browser** — inspect any TD component's extensions, methods, attributes, and parameters via `op.AW.SelectComponent(...)` plus the bundled selector / parameters / callbacks widgets

The widget settings UIs (`/AcroWidgets/widgetSettings`, `/AcroWidgets/widgetContainerSettings`) handle per-widget configuration; `op.AWWS` and `op.AWWCS` are their shortcuts respectively.

## Quick start

```python
# Refresh registry — picks up any new widget added to a widgetFolder
op.AW.UpdateWidgets()

# Drop a fresh widget container at the current network pane's location
op.AW.CreateWCInCurrentPane()

# Browse components — point the registry at a parent comp and select one
op.AW.UpdateComponentsPath()        # reads from the Components path parameter
op.AW.UpdateComponents()            # populate the list
op.AW.SelectComponent(0)            # first one
print(op.AW.SelectedComponent)      # {'name', 'path', 'parameters', 'classes', 'extPaths'}

# Open the components folder in a floating network editor
op.AW.OpenComponentsNetwork()
```

## Widget discovery

Widgets are discovered via TouchDesigner's tag system:

| Tag | What it marks |
|-----|---------------|
| `widgetFolder` | A container that holds a collection of widgets |
| `widget` | An individual widget. Can be cloned into an `AcroWidgetContainer`. |
| `TDBasicWidget` | TouchDesigner's stock basic-widget tag — also picked up |

`UpdateWidgets()` walks every `widgetFolder` under `/` and registers each tagged child as a candidate widget.

## Core classes (in `scripts/`)

| Class | Role |
|-------|------|
| `AcroWidgets` | Main extension — registry, component browser, clipboard state, selection bookkeeping |
| `AcroWidgetContainer` | The container primitive — load-bearing infrastructure for the whole UI system |
| `AcroUIButton` | Button widget (used by simple buttons, button arrays, tabs) |
| `AcroUIPages` | Pages widget with auto-generated tabs |
| `AcroUIMatrix` | Resizable grid of `AcroWidgetContainer`s with draggable splits |
| `AcroPopWin` | Floating popup window |
| `AcroDropList` | Dropdown menu list |
| `AcroComponentSelector` | Selector / picker for browsing components |
| `AcroComponentSelectorRelative` | Variant that uses a relative path expression |
| `AcroComponentCallbacks` | Callbacks viewer widget |
| `AcroComponentParameters` | Live parameters viewer widget |

## Initial-state protection

`AcroWidgets.EnsureValidSelections()` runs on init and via parexec on `op.AWWS.par.Widget` and `op.AWWCS.par.Widget`. It:

- Resets either Widget par to the sentinel `/AcroWidgets/widgets/ui/empty` if the saved value doesn't resolve to a real op
- Pads `SelectedComponent['extPaths']` to 4 empty strings so `extPaths[i]` lookups can't IndexError

This means downstream parameter expressions can always assume the Widget pars point at a valid op and that `extPaths` is at least 4 long, even at first load.

> **Caution:** `AcroWidgetContainer` is load-bearing for the whole UI system. The `op.AW` reference inside its code is intentional and must stay a global op shortcut — do not switch to relative paths. PopMenu uses TouchDesigner's built-in `op.TDResources.PopMenu`. Any change to `AcroWidgetContainer` should be small, isolated, and verified across nested-container, copy / paste / drag scenarios before merging.

## Where to go next

- **[Widgets Reference](widgets)** — Detailed coverage of `AcroWidgets` API, `AcroWidgetContainer` mechanics, every primitive class, widget discovery, and modification guidelines.

## Installation

```bash
git subtree add --prefix=modules/acro-td-widgets https://github.com/acronym-lol/acro-td-widgets.git main --squash
```

`setup.ps1` / `setup.sh` register `ACRO_TD_WIDGETS` pointing at the module on disk.
