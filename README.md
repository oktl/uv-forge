# 🛠️ UV Forge

[![PyPI version](https://img.shields.io/pypi/v/uv-forger)](https://pypi.org/project/uv-forger/)
[![Python 3.12+](https://img.shields.io/pypi/pyversions/uv-forger)](https://pypi.org/project/uv-forger/)
[![License: MIT](https://img.shields.io/github/license/oktl/uv-forge)](https://github.com/oktl/uv-forge/blob/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/oktl/uv-forge/ci.yml?label=CI)](https://github.com/oktl/uv-forge/actions)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Built with Flet](https://img.shields.io/badge/built%20with-Flet-0553B1?logo=flet)](https://flet.dev)

UV Forge is a high-performance [Flet](https://flet.dev) desktop application designed to "forge" new Python projects using the [uv](https://docs.astral.sh/uv/) package manager. It bridges the gap between powerful command-line tooling and a visual, intuitive workflow, allowing developers to scaffold production-ready environments in seconds.  

Pick a UI framework or project type, (or both), configure your options, and UV Forge generates a fully wired project: folder structure, boilerplate files, package installation, virtual environment, git repo, and pyproject.toml, and optionally does an initial commit  — all in one click.

---

![UV Forge main window](https://raw.githubusercontent.com/oktl/uv-forge/main/uv_forge/assets/images/main-window.png)

## ✨ Key Features

- **uv-Powered Core** - Leverages the lightning-fast uv executable for virtual environment management and dependency resolution.
- **Intelligent Scaffolding** - Dynamically generates project structures based on your selections, from basic scripts to complex Flet UIs or Web Scraping suites. Key files (e.g. `main.py`, `state.py`, `components.py`) are populated with starter boilerplate instead of created empty, with `{{project_name}}` placeholders auto-substituted.
- **Template Portability** - Uses a flexible, dictionary-based folder/file/package template system in config/templates/ that allows for easy addition or removal of frameworks.
- **Template Merging** — Select both a UI framework and project type; their folder structures are intelligently merged.
- **Template Previewing** - Templates can be previewed and modified in the app - add or remove folders and files, same with dependency packages. The file/folder list and the packages list update automatically. Dependency packages can be marked dev and placed in the dev list in pyproject.toml. When adding a file, use the Browse button to import an existing file from disk in one step.
- **10 UI Frameworks** — Flet, PyQt6, PySide6, tkinter, customtkinter, Kivy, Pygame, NiceGUI, Streamlit, Gradio.
- **21 Project Types** — Django, FastAPI, Flask, data science, ML (PyTorch/TensorFlow/scikit-learn), CLI tools (Click/Typer/Rich), REST/GraphQL/gRPC APIs, web scraping, browser automation, async apps, and more.
- **PyPI Guardrails** — Verify your package name is available on PyPI before building (PEP 503 normalization, async). Real-time validation checks project names against PyPI to prevent naming conflicts before you even start coding.
- **Git Integration** — Two-phase setup with three remote modes: local bare hub (default), GitHub via `gh`, or local-only with no remote
- **Dev Dependencies** — Mark packages as dev dependencies; they're installed with `uv add --dev` and shown with an amber badge
- **Project Metadata** — Configure author, email, description, and license (SPDX); written directly into `pyproject.toml`
- **Post-Build Automation** — Optionally run a configurable shell command after each successful build (e.g. `uv run pre-commit install`)
- **Safety First** - Includes a robust rollback system that cleans up partially created directories if a build fails, keeping your workspace pristine.
- **Presets** — Save full project configurations as named presets for one-click reuse. Ships with 4 built-in starter presets (Flet Desktop App, FastAPI Backend, Data Science Starter, CLI Tool) for instant project setup
- **Recent Projects** — Restore any of your last 5 builds with a single click
- **Settings** — Configurable defaults for project path, GitHub root, Python version, preferred IDE, and git behaviour
- **Log Viewer** — Colour-coded log display with clickable source locations that open directly in your IDE
- **Theme** — Toggle between dark and light mode
- **Error Handling** — Automatic cleanup and rollback on build failure
- **Async Operations** — UV and git commands run off the UI thread; the app stays responsive throughout

---

## Requirements

- **Python 3.12+**
- **UV** — [install UV](https://docs.astral.sh/uv/getting-started/installation/)
- **Git** (optional, for repository initialization)
- **GitHub CLI (`gh`)** (optional, for GitHub remote mode) — [install gh](https://cli.github.com/)

---

## Installation

```bash
# Run directly without installing
uvx uv-forger

# Or install into a project / global environment
uv tool install uv-forger
uv-forger
```

---

## Running from Source

```bash
git clone https://github.com/oktl/uv-forge.git
cd uv-forge
uv run uv-forger       # Via entry point
python uv_forge/main.py     # Direct execution
```

---

## Usage

### Quick Start

1. Enter a **project name** (valid Python package name)
2. Set the **project path** (where the folder will be created)
3. Choose a **Python version** (3.10–3.14)
4. Optionally enable **Git**, select a **UI framework**, and/or select a **project type**
5. Review the auto-generated **folder structure** and **package list**
6. Click **Build Project**

A confirmation dialog summarises your settings and lets you choose post-build actions (open folder, open in IDE, open terminal, run post-build command). Click Confirm to build.

### Keyboard Shortcuts

| Shortcut                | Action                 |
| ----------------------- | ---------------------- |
| `⌘Enter` / `Ctrl+Enter` | Build project          |
| `⌘F` / `Ctrl+F`         | Add Folder/File dialog |
| `⌘P` / `Ctrl+P`         | Add Packages dialog    |
| `⌘R` / `Ctrl+R`         | Reset all fields       |
| `⌘/` / `Ctrl+/`         | Open Help              |
| `Esc`                   | Close dialog / Exit    |

### Overflow Menu (⋮)

All secondary actions live in the app bar overflow menu:

- **Recent Projects** — Restore a previous build's full configuration
- **Presets** — Save, apply, and delete named configurations
- **Settings** — Configure defaults and post-build behaviour
- **Help** — Usage guide and keyboard shortcuts
- **View Logs** — Colour-coded log viewer with clickable source locations
- **About** — App info and tech stack

---

## Documentation

Full documentation is available at **[oktl.github.io/uv-forge](https://oktl.github.io/uv-forge/)** — including a user guide, template system reference, and troubleshooting.

---

## Template System

Templates are JSON files in `uv_forge/config/templates/` defining folder structures:

```plaintext
uv_forge/config/templates/
├── ui_frameworks/     # flet.json, pyqt6.json, default.json, etc.
├── project_types/     # django.json, fastapi.json, etc.
└── boilerplate/       # Starter file content
    ├── common/        # async_executor.py, constants.py, ...
    └── ui_frameworks/ # flet/main.py, flet/state.py, ...
```

**Loading fallback chain:**

1. Framework-specific template (e.g. `ui_frameworks/flet.json`)
2. `ui_frameworks/default.json`
3. Hardcoded `DEFAULT_FOLDERS` in `constants.py`

**Boilerplate fallback chain** (per file):

1. `boilerplate/ui_frameworks/{framework}/{filename}`
2. `boilerplate/project_types/{project_type}/{filename}`
3. `boilerplate/common/{filename}`
4. Empty file (zero breakage risk)

**Template merging** — when both a UI framework and project type are selected, folders matched by name are merged recursively (files unioned, booleans OR'd); unmatched folders from both templates are included.

### Adding a New Framework or Project Type

1. Add to `UI_FRAMEWORKS` or `PROJECT_TYPE_PACKAGE_MAP` in `uv_forge/core/constants.py`
2. Add package mapping to `FRAMEWORK_PACKAGE_MAP` (for UI frameworks)
3. Add display entry to `UI_FRAMEWORK_CATEGORIES` or `PROJECT_TYPE_CATEGORIES` in `uv_forge/ui/dialog_data.py`
4. Create a template JSON in the appropriate subdirectory
5. (Optional) Drop boilerplate files into `uv_forge/config/templates/boilerplate/` — no code changes needed

---

## Git Integration

When **Git Repository** is checked, UV Forge uses a two-phase setup. The behaviour varies by **Git Remote Mode** (configurable in Settings, overridable per-build in the Confirm dialog):

### Local Bare Repo (default)

- **Phase 1:** Initializes a local repo, creates a bare hub at your GitHub Root (default: `~/Projects/git-repos/<name>.git`), and connects it as `origin`
- **Phase 2:** Stages all files, commits, and pushes to hub with upstream tracking

### GitHub

- **Phase 1:** Initializes a local repo only
- **Phase 2:** Stages all files, commits, then runs `gh repo create` to create a GitHub repository and pushes. Supports username/org prefix and private/public visibility. Requires the [GitHub CLI (`gh`)](https://cli.github.com/) to be installed and authenticated.

### None (local only)

- **Phase 1:** Initializes a local repo only
- **Phase 2:** Stages all files and commits — no remote, no push

---

## Settings & Persistence

Settings are stored in the platform-appropriate user data directory (e.g. `~/Library/Application Support/UV Forge/` on macOS):

| File                   | Contents                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------- |
| `settings.json`        | Default path, GitHub root, Python version, IDE, git default, git remote mode, GitHub username, private repos, author, post-build command |
| `recent_projects.json` | Last 5 successful builds (name, path, config, timestamp)                                |
| `presets.json`         | Named project configuration presets (no limit)                                          |

Log files rotate daily and are stored in the `logs/` subdirectory alongside settings.

---

## Development

```bash
uv run pytest              # Run 619+ tests (coverage automatic)
uv run ruff check uv_forge      # Lint (runs automatically on commit)
uv run ruff format uv_forge     # Auto-format
```

**Running tests:** Uses `pytest-asyncio` in auto mode. All tests are in `tests/` mirroring the `uv_forge/` structure.

**Linting:** Ruff enforces `E`, `F`, `I`, `W`, `UP`, `B`, `SIM` rules. A pre-commit hook lints and format-checks `uv_forge/` automatically.

**Key patterns:**

- All imports use absolute `uv_forge.*` paths
- `AppState` is the single mutable state object — never duplicated
- Async handlers wrapped via `wrap_async()` to keep Flet's sync callback system happy
- `Dropdown.on_select` (not `on_change`) — Flet 0.80+ requirement

---

## Tech Stack

| Component                                            | Version  |
| ---------------------------------------------------- | -------- |
| Python                                               | 3.12+    |
| [Flet](https://flet.dev)                             | 0.80.5+  |
| [uv](https://docs.astral.sh/uv/)                     | external |
| [httpx](https://www.python-httpx.org/)               | 0.28+    |
| [loguru](https://loguru.readthedocs.io/)             | 0.7+     |
| [platformdirs](https://platformdirs.readthedocs.io/) | 4.0+     |

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting bugs, adding templates, and submitting pull requests.

---

## License

[MIT License](LICENSE)
