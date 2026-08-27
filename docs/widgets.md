---
last_reviewed: 2026-08-27
---

# AcroWidgets — Widget Framework

## Overview

AcroWidgets is a framework for building custom UIs out of reusable widget components. The system is built around two pieces:

- **`AcroWidgets`** (the manager) — discovers widgets in the scene, tracks selected components for inspection, and provides a single registry that the rest of the system queries.
- **`AcroWidgetContainer`** — the basic UI building block. Each container holds exactly one widget from the widget library at any time; containers can be nested, copied, dragged, and dropped.

The manager component lives at `/AcroWidgets` and is exposed as `op.AW`. It inherits from `CallbacksExt` and `AcroVersionExt`, so it carries the standard Component / Version pages.

> **Note:** `AcroWidgetContainer` is load-bearing infrastructure with subtle behaviors (undo handling, swap/replace conflict resolution, drag/drop semantics, deep nesting). Modifications should be small, isolated, and verified — see [Modifying AcroWidgetContainer](#modifying-widgetcontainer) below.

---

## AcroWidgetContainer — The Basic Block

A `AcroWidgetContainer` is the framework's analog to HTML's `<div>`. It can:

- exist anywhere in the scene hierarchy
- be nested arbitrarily deep
- contain exactly one widget (tagged `widget`) at a time
- be copied, cut, pasted, dragged, dropped, saved as `.tox`, and loaded from `.tox`

Each container holds a `SelectedWidget` storage entry — `{'folder': ..., 'widget': ...}` — that resolves to a master widget under one of the registered widget folders. When the selection changes, the container clones the master, destroys any prior widget, and registers an undo callback so the swap is reversible.

### AcroWidgetContainer API

| Method | Purpose |
|--------|---------|
| `UpdateSelectedWidget()` | Re-derive `SelectedWidget` by inspecting the current child widget's `clone` parameter. Called on init and on lifecycle hooks. |
| `SelectWidget(folder, widget)` | Replace the current widget with the named master. Wraps the change in `ui.undo.startBlock('select widget')`. |
| `Copy()` / `Cut()` / `Paste()` | Standard clipboard operations. Cut + paste = move; copy + paste = duplicate. Conflicts inside an occupied container raise a Replace/Swap/Cancel dialog. |
| `Delete()` | Replace the current widget with the empty widget. Registers an undo for both the selection change and the clipboard if the container was the cut source. |
| `Save()` / `Load()` | Save/load the container as a `.tox` file. `Load()` sets `externaltox` and disables `reloadtoxonstart` to prevent the container from clobbering the loaded widget on next session start. |
| `OpenWidgetContainerSettings()` | Open the container settings panel for this container. Marks the container `Selected = True`. |
| `OpenWidgetSettings()` | Open the widget settings panel for the contained widget. |
| `OpenRClickMenu()` | Open the PopMenu when the user right-clicks. Disabled unless `op.AW.par.Enableedit` is on. |
| `ReloadWidget()` | Destroy and recreate the contained widget from its master. Used to recover from corrupted or detached state. |
| `OnCreate()` / `OnStart()` | Lifecycle hooks. Both call `UpdateSelectedWidget()` and pulse `enablecloningpulse` on any `TDBasicWidget` children. |
| `OnDrag(args)` / `OnDrop(args)` | Drag/drop handlers. Drop with Ctrl held = copy; otherwise move. Rejects non-COMP drops, non-widget-container drops, and self-nesting drops. |

### Storage Keys

Each container's `data` comp stores:

| Key | Default | Purpose |
|-----|---------|---------|
| `SelectedWidget` | `{'folder': 'ui', 'widget': 'empty'}` | The master widget reference. |
| `Selected` | `False` | Whether this container is the active editing target. |
| `Drag` | `False` | Drag state flag. |
| `Drop` | `False` | Drop state flag. |

### Conflict Resolution

When pasting or dropping into an occupied container, `_transferWidget` decides what to do:

1. If the destination is empty, the source widget is copied in (and cleared from the source if `is_move`).
2. If the destination is occupied and the source is also occupied:
   - For paste (not move) into a container outside the source's tree: **Replace / Swap / Cancel**.
   - For move, or paste inside the source's own tree: **Replace / Cancel**.

Swap is intentionally disabled for moves to keep the operation deterministic.

---

## AcroWidgets Manager API

### Properties (via stored)

| Name | Type | Description |
|------|------|-------------|
| `Widgets` | `dict` | Widget registry, keyed by folder. Built by `UpdateWidgets`. |
| `Modifiers` | `dict` | Current modifier state — `{'ctrl': bool, 'alt': bool, 'shift': bool}`. |
| `Components` | `list[str]` | List of components found under `ComponentsPath`. Populated by `UpdateComponents`. |
| `ComponentsPath` | `str` | Path to the components folder being inspected. Driven by the `Components` parameter. |
| `SelectedComponent` | `dict` | Currently selected component for inspection — `{'index', 'name', 'path', 'parameters', 'classes', 'extPaths'}`. |
| `Copy` | `dict` | Clipboard for widget container copy/cut — `{'path': str, 'isCut': bool}`. |
| `SelectedWidgetContainer` | `str` | Path of the widget container with the active right-click menu. |

### Widget Discovery

| Method | Returns | Purpose |
|--------|---------|---------|
| `UpdateWidgets()` | `dict` | Re-scan the scene for widget folders (tag `widgetFolder`) and their widgets (tags `widget` or `TDBasicWidget`). Refreshes the `Widgets` storage and the widget settings menu. |
| `SearchWidgetsByTag(key, items)` | `list` | Filter a list of widget dicts to those whose name contains `key`. |

### Component Inspection

| Method | Returns | Purpose |
|--------|---------|---------|
| `UpdateComponentsPath()` | `None` | Re-resolve `ComponentsPath` from the `Components` parameter. |
| `UpdateComponents()` | `None` | Refresh `Components` by finding every operator under `ComponentsPath` tagged `component`. |
| `GetComponents()` | `list[str]` | Return the sorted, deduplicated list of component names. |
| `SelectComponent(index)` | `None` | Select a component by index, fire `onComponentSelect`, and call `UpdateComponent`. |
| `UpdateComponent()` | `None` | Refresh extension class info, public methods, attributes, and custom parameters for the selected component. |
| `OpenComponentsNetwork()` | `None` | Open a floating network editor for the components folder. |
| `OpenComponentNetwork()` | `None` | Open a floating network editor for the selected component. |
| `ImportComponent()` | `None` | Prompt the user for a `.tox`, then load it under `ComponentsPath` (unwired). |
| `ExportComponent()` | `None` | Prompt the user for a path, then save the selected component as a `.tox`. |

### Widget Container Creation

| Method | Returns | Purpose |
|--------|---------|---------|
| `CreateWC(path, x, y)` | `None` | Create a widget container at the given network position by copying the manager's `widgetContainer` template. |
| `CreateWCInCurrentPane()` | `None` | Create a widget container at the current network editor pane's cursor position. |

---

## Widget Discovery Tags

The manager finds widgets by walking the scene from the root looking for these tags:

| Tag | Applied to | Purpose |
|-----|-----------|---------|
| `widgetFolder` | A container component grouping widgets | Identifies a registered widget folder. |
| `widget` | An individual widget COMP | Identifies a widget that can be cloned into a container. |
| `TDBasicWidget` | An individual widget COMP using TD's stock widget kit | Same as `widget` but signals that `enablecloning` needs pulsing on lifecycle events. |
| `component` | Any user component under `ComponentsPath` | Identifies a component for the inspection UI. |

---

## Custom Callbacks

The manager dispatches the following callbacks via `CallbacksExt`. Implement them on the manager's external `Callbackdat`:

| Callback | Info Keys | Purpose |
|----------|-----------|---------|
| `onInit` | `ownerComp` | Fired during extension init. |
| `onComponentSelect` | `ownerComp`, `component` | Fired by `SelectComponent`. |

---

## Modifying AcroWidgetContainer

AcroWidgetContainer is exercised by drag/drop, copy/paste, undo, and arbitrarily deep nesting — the corner cases compound. When changing it:

1. **Don't replace `op.AW` with relative paths.** The reference must point to the central registry regardless of where the container lives in the scene tree.
2. **Don't bypass `op.TDResources.PopMenu`.** It is TD's shared right-click menu and is what the rest of the codebase expects.
3. **Make small, isolated changes.** Each change should be testable in isolation against:
   - paste into empty container
   - paste into occupied container (replace / swap / cancel)
   - cut + paste (move)
   - drag + drop (move and Ctrl-copy)
   - delete with active clipboard
   - undo on every operation above
   - all of the above with a deeply nested container
4. **Preserve undo wrapping.** Every clipboard or selection mutation goes through `ui.undo.startBlock` / `endBlock` and registers a callback. Skipping the undo wrap will leave the user with an unrecoverable state.
5. **Always ask before changing.** The container is small but heavily used; surprise behavior changes are expensive.

---

## Tag Discovery

The manager itself carries `tox_managed` and `version_tracking` tags via `AcroVersionExt` and is discoverable via `root.findChildren(tags=['version_tracking'])`.
