# Acro TD Widgets

[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://acronym-lol.github.io/acro-td-widgets/)

Widget management system for TouchDesigner — discovers widgets in the scene, inspects component extensions/parameters, and provides building blocks for custom UIs (buttons, lists, matrices, paged containers, popups).

**Documentation:** https://acronym-lol.github.io/acro-td-widgets/

## Components

- **`AcroWidgets`** (`scripts/AcroWidgets.py`) — main extension; discovers `widget` / `widgetFolder` tagged components and tracks selected component metadata.
- **`AcroWidgetContainer`** — container that hosts a single widget.
- **`AcroUIButton`, `AcroUIMatrix`, `AcroUIPages`** — reusable UI primitives.
- **`AcroDropList`, `AcroPopWin`** — dropdown menus and floating popup windows.
- **`AcroComponent*`** — selectors, parameter inspectors, and callbacks for the component browser.

## Installation

```bash
git subtree add --prefix=modules/acro-td-widgets https://github.com/acronym-lol/acro-td-widgets.git main --squash
```

## Contributing

Issues are welcome here. Pull requests go to [acro-td-core](https://github.com/acronym-lol/acro-td-core) against its `dev` branch; see [CONTRIBUTING.md](CONTRIBUTING.md).
