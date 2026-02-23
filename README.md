# 🛠️ UV Forge

> UV Forge is a high-performance [Flet](https://flet.dev) desktop application designed to "forge" new Python projects using the [uv](https://docs.astral.sh/uv/) package manager. It bridges the gap between powerful command-line tooling and a visual, intuitive workflow, allowing developers to scaffold production-ready environments in seconds.  

Pick a UI framework or project type, (or both), configure your options, and UV Forge generates a fully wired project: folder structure, boilerplate files, package installation, virtual environment, git repo, and pyproject.toml, and optionally does an initial commit  — all in one click.

---

![](app/assets/images/looksliethis.png)

## ✨ Key Features

- **uv-Powered Core** - Leverages the lightning-fast uv executable for virtual environment management and dependency resolution.
- **Intelligent Scaffolding** - Dynamically generates project structures based on your selections, from basic scripts to complex Flet UIs or Web Scraping suites. Key files (e.g. `main.py`, `state.py`, `components.py`) are populated with starter boilerplate instead of created empty, with `{{project_name}}` placeholders auto-substituted.
- **Template Portability** - Uses a flexible, dictionary-based folder/file/package template system in config/templates/ that allows for easy addition or removal of frameworks.
- **Template Merging** — Select both a UI framework and project type; their folder structures are intelligently merged.
- **Template Previewing** - Templates can be previewed and modified in the app - add or remove folders and files, same with dependency packages. The file/folder list and the pacakages list update automatically. Dependency packages can be marked dev and placed in the dev list in pyrproject.toml.
- **10 UI Frameworks** — Flet, PyQt6, PySide6, tkinter, customtkinter, Kivy, Pygame, NiceGUI, Streamlit, Gradio.
- **21 Project Types** — Django, FastAPI, Flask, data science, ML (PyTorch/TensorFlow/scikit-learn), CLI tools (Click/Typer/Rich), REST/GraphQL/gRPC APIs, web scraping, browser automation, async apps, and more.
- **PyPI Guardrails** — Verify your package name is available on PyPI before building (PEP 503 normalization, async). Real-time validation checks project names against PyPI to prevent naming conflicts before you even start coding.
- **Git Integration** — Two-phase setup: creates a local repo + bare hub repository, then stages, commits, and pushes automatically after build
- **Dev Dependencies** — Mark packages as dev dependencies; they're installed with `uv add --dev` and shown with an amber badge
- **Project Metadata** — Configure author, email, description, and license (SPDX); written directly into `pyproject.toml`
- **Post-Build Automation** — Optionally run a configurable shell command after each successful build (e.g. `uv run pre-commit install`)
- **Safety First** - Includes a robust rollback system that cleans up partially created directories if a build fails, keeping your workspace pristine.
- **Presets** — Save full project configurations as named presets for one-click reuse
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

---

## Installation

```bash
# Run directly without installing
uvx uv-forge

# Or install into a project / global environment
uv tool install uv-forge
uv-forge
```

---

## Running from Source

```bash
git clone <repo-url>
cd uv-forge
uv run uv-forge        # Via entry point
python app/main.py     # Direct execution
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
- **Git Cheat Sheet** — Quick reference for common Git commands
- **View Logs** — Colour-coded log viewer with clickable source locations
- **About** — App info and tech stack

---

## Template System

Templates are JSON files in `app/config/templates/` defining folder structures:

```plaintext
app/config/templates/
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

1. Add to `UI_FRAMEWORKS` or `PROJECT_TYPE_PACKAGE_MAP` in `app/core/constants.py`
2. Add package mapping to `FRAMEWORK_PACKAGE_MAP` (for UI frameworks)
3. Add display entry to `UI_FRAMEWORK_CATEGORIES` or `PROJECT_TYPE_CATEGORIES` in `app/ui/dialog_data.py`
4. Create a template JSON in the appropriate subdirectory
5. (Optional) Drop boilerplate files into `app/config/templates/boilerplate/` — no code changes needed

---

## Git Integration

When **Git Repository** is checked, UV Forge uses a two-phase setup:

**Phase 1 (during project creation):**

- Initializes a local git repo in the project directory
- Creates a bare hub repo at your configured GitHub Root (default: `~/Projects/git-repos/<name>.git`)
- Connects the local repo to the hub as `origin`

**Phase 2 (after all files are created):**

- Stages all files (`git add .`)
- Creates an initial commit
- Pushes to hub with upstream tracking (`git push -u origin HEAD`)

Your project is git-ready immediately — no manual first push needed.

---

## Settings & Persistence

Settings are stored in the platform-appropriate user data directory (e.g. `~/Library/Application Support/UV Forge/` on macOS):

| File                   | Contents                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------- |
| `settings.json`        | Default path, GitHub root, Python version, IDE, git default, author, post-build command |
| `recent_projects.json` | Last 5 successful builds (name, path, config, timestamp)                                |
| `presets.json`         | Named project configuration presets (no limit)                                          |

Log files rotate daily and are stored in the `logs/` directory inside the project root.

---

## Development

```bash
uv run pytest              # Run 619+ tests (coverage automatic)
uv run ruff check app      # Lint (runs automatically on commit)
uv run ruff format app     # Auto-format
```

**Running tests:** Uses `pytest-asyncio` in auto mode. All tests are in `tests/` mirroring the `app/` structure.

**Linting:** Ruff enforces `E`, `F`, `I`, `W`, `UP`, `B`, `SIM` rules. A pre-commit hook lints and format-checks `app/` automatically.

**Key patterns:**

- All imports use absolute `app.*` paths
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

## License

[PolyForm Noncommercial 1.0.0](LICENSE) — free for personal, educational, and noncommercial use. Commercial use is not permitted.
