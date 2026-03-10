# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-10

### Added

- Initial release of UV Forge
- Flet desktop GUI for scaffolding Python projects with UV
- 10 UI framework templates (Flet, PyQt6, PySide6, tkinter, customtkinter, Kivy, Pygame, NiceGUI, Streamlit, Gradio)
- 21 project type templates (Django, FastAPI, Flask, data science, ML, CLI tools, APIs, web scraping, and more)
- JSON-based template system with fallback hierarchy and intelligent merging
- Smart scaffolding with boilerplate file content and `{{project_name}}` placeholder substitution
- PyPI name availability checker with PEP 503 normalization
- Two-phase git integration (local repo + bare hub, auto commit and push)
- Dev dependency support (`uv add --dev`) with amber badge in UI
- Project metadata dialog (author, email, description, SPDX license)
- Post-build automation with configurable shell commands
- Rollback system for cleanup on build failure
- Named project presets with 4 built-in starters
- Recent projects history (last 5 builds)
- Persistent settings (project path, GitHub root, Python version, IDE, git defaults)
- Colour-coded log viewer with clickable source locations
- Dark and light theme toggle

[0.1.0]: https://github.com/oktl/uv-forge/releases/tag/v0.1.0
