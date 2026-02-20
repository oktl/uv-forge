# UV Forge

**Version 0.1.0**

A desktop application for creating Python projects with UV — the fast Python package manager. Provides template-based folder structures, framework/package installation, git initialization, and Python version selection.

---

## Tech Stack

- **Python** 3.14+
- **Flet** 0.80.5+ (UI framework)
- **UV** (package & project manager)
- **httpx** (async HTTP for PyPI checks)
- **platformdirs** (cross-platform settings storage)
- **Git** (optional, for repository initialization)

---

## Key Features

- **10 UI Frameworks** — Flet, PyQt6, PySide6, tkinter, customtkinter, Kivy, Pygame, NiceGUI, Streamlit, Gradio
- **21 Project Types** — Django, FastAPI, Flask, data science, web scraping, CLI tools, and more
- **Template Merging** — Select both a UI framework and project type to automatically merge their folder structures
- **Smart Scaffolding** — Starter files populated with boilerplate content instead of empty files
- **PyPI Name Checker** — Verify package name availability before building
- **User Settings** — Configurable defaults for project path, Python version, IDE preference, and git; persisted to disk
- **Git Integration** — Two-phase setup with local repo and bare hub (path configurable via Settings)
- **Async Operations** — UV and git commands run off the UI thread for a responsive experience
- **Recent Projects** — Restore settings from your last 5 builds with one click
- **Log Viewer** — Colour-coded log display with clickable source locations that open in your IDE
- **Theme Support** — Toggle between dark and light mode
- **Error Handling** — Rollback and cleanup on build failure

---

## More Information

- [Help & Documentation](app://help) — Usage guide and keyboard shortcuts
- [Git Cheat Sheet](app://git-cheat-sheet) — Quick reference for common Git commands

---

## Credits

Built with [Flet](https://flet.dev) and [UV](https://docs.astral.sh/uv/).

Created by Tim with assistance from Claude Code.
