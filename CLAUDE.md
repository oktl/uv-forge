# CLAUDE.md - UV Project Creator

**Version:** 0.2.3 | **Python:** 3.14+ | **UI:** Flet 0.80.5+ | **Package Manager:** UV

---

## What This Is

A Flet desktop app that creates Python projects using UV. It provides template-based folder structures, framework/package installation, git init, and Python version selection.

Key capabilities:
- 10 UI frameworks + 21 project types with automatic template merging when both selected
- JSON template system with fallback hierarchy (framework → default → hardcoded)
- Smart scaffolding: boilerplate resolver populates files with starter content instead of empty `.touch()`
- Async operations via thread pool (UV/git subprocess calls run off the UI thread)
- Error handling with rollback (cleanup_on_error removes partial projects)

---

## Running

```bash
uv run create_project        # Via entry point
python app/main.py            # Direct execution
uv run pytest                 # Run 387 tests (coverage automatic)
```

---

## Directory Structure

```plaintext
app/
├── main.py                   # Entry point: creates page, state, UI, attaches handlers
├── core/
│   ├── constants.py          # Single source of truth: versions, frameworks, package maps, paths, dialog data
│   ├── state.py              # AppState dataclass — single source of truth for all mutable state
│   ├── models.py             # FolderSpec, ProjectConfig, BuildResult, BuildSummaryConfig dataclasses
│   ├── validator.py          # validate_project_name(), validate_folder_name(), validate_path()
│   ├── project_builder.py    # build_project() orchestration — UV init, git, folders, packages
│   ├── config_manager.py     # ConfigManager: loads JSON templates, fallback chain
│   ├── boilerplate_resolver.py # BoilerplateResolver: populates files with starter content
│   ├── template_merger.py    # normalize_folder(), merge_folder_lists(), _merge_files()
│   └── state_validator.py    # EMPTY placeholder
├── handlers/
│   ├── event_handlers.py     # Handlers class + attach_handlers() — all UI event wiring
│   ├── filesystem_handler.py # setup_app_structure(), folder creation, cleanup_on_error()
│   ├── uv_handler.py         # run_uv_init(), install_package(), setup_virtual_env()
│   ├── git_handler.py        # handle_git_init(), finalize_git_setup() — two-phase git setup
├── ui/
│   ├── components.py         # Controls class + build_main_view(page, state)
│   ├── dialogs.py            # 8 dialog functions + 5 shared helpers; all theme-aware via is_dark_mode
│   ├── theme_manager.py      # get_theme_colors() singleton
│   └── ui_config.py          # UI constants (colors, sizes)
├── utils/
│   └── async_executor.py     # AsyncExecutor.run() — ThreadPoolExecutor wrapper
└── config/templates/
    ├── ui_frameworks/        # 11 templates: flet.json, pyqt6.json, default.json, etc.
    ├── project_types/        # 21 templates: django.json, fastapi.json, etc.
    └── boilerplate/          # Starter file content (smart scaffolding)
        ├── common/           # async_executor.py, constants.py
        └── ui_frameworks/    # flet/main.py, flet/state.py, flet/components.py

tests/
├── core/                     # 148 tests (state, models, validator, config_manager, template_merger, boilerplate_resolver)
├── handlers/                 # 93 tests (event_handlers, filesystem, git, uv)
├── ui/                       # 19 tests (dialogs)
└── utils/                    # 13 tests (async_executor)
```

---

## Critical Flet 0.80+ Patterns

These are non-obvious and will cause bugs if forgotten:

```python
# Dropdowns use on_select, NOT on_change
controls.python_version_dropdown.on_select = wrap_async(handler)

# on_change CANNOT be set as keyword arg in Dropdown constructor

# FilePicker is a service control — do NOT add to page.overlay or visual tree
result = await ft.FilePicker().get_directory_path(dialog_title="Select Location")

# Async handlers must be wrapped for Flet's sync callback system
def wrap_async(coro_func):
    def wrapper(e):
        asyncio.create_task(coro_func(e))
    return wrapper

# Buttons: on_click, Checkboxes: on_change, Dropdowns: on_select
```

---

## Template System

Templates are JSON files in `app/config/templates/` defining `FolderSpec` structures:

```json
{"name": "core", "create_init": true, "root_level": false,
 "subfolders": [...], "files": ["state.py", "models.py"]}
```

**Loading fallback chain** (see `config_manager.py`):
1. Framework-specific template (e.g., `ui_frameworks/flet.json`)
2. `ui_frameworks/default.json`
3. Hardcoded `DEFAULT_FOLDERS` from `constants.py`

**Template merging** (see `template_merger.py`):
When both UI framework + project type are selected, `_reload_and_merge_templates()` in `event_handlers.py` loads both and calls `merge_folder_lists()`:
- Folders matched by name → merged recursively (subfolders merged, files unioned, booleans OR'd)
- Unmatched folders → included from both (primary order first)

**Adding a new framework/project type:**
1. Add to `UI_FRAMEWORKS` or `PROJECT_TYPE_PACKAGE_MAP` in `constants.py`
2. Add package mapping to `FRAMEWORK_PACKAGE_MAP` if UI framework
3. Add entry to `UI_FRAMEWORK_DETAILS` or the appropriate category in `PROJECT_TYPE_CATEGORIES` in `constants.py`
4. Create template JSON in the appropriate templates subdirectory

**Boilerplate file scaffolding** (see `boilerplate_resolver.py`):
When files are created during project scaffolding, the `BoilerplateResolver` looks up starter content instead of creating empty files. Uses a fallback chain:
1. `boilerplate/ui_frameworks/{framework}/{filename}` (e.g., Flet-specific `main.py`)
2. `boilerplate/project_types/{project_type}/{filename}`
3. `boilerplate/common/{filename}` (universal utilities like `async_executor.py`)
4. `None` → falls back to empty `.touch()` (zero breakage risk)

Files use `{{project_name}}` placeholders, substituted at build time with a normalized title-case value (e.g. `my_app` → `My App`, `create-a-project` → `Create A Project`). Adding new boilerplate is just dropping a file into the right directory — no code changes needed.

---

## Key Architecture Decisions

- **All imports use absolute `app.*` paths** (e.g., `from app.core.state import AppState`)
- **Constants centralized in `app/core/constants.py`** — do not create duplicate constant files
- **AppState is the single mutable state object** — passed to UI builder and handlers, never duplicated
- **`page.controls_ref` and `page.state_ref`** store references for cross-module access
- **Async pattern**: sync handlers wrapped via `wrap_async()` / `AsyncExecutor.run()` to keep UI responsive
- **`_reload_and_merge_templates()`** is the single entry point for all template loading — framework change, project type change, reset, toggle off
- **`normalize_framework_name()`** in `boilerplate_resolver.py` is the shared function for framework name normalization — used by both `ConfigManager` and `BoilerplateResolver`
- **`normalize_project_name()`** in `boilerplate_resolver.py` converts project names to title case with spaces for `{{project_name}}` substitution (e.g. `my_app` → `My App`)
- **Two-phase git setup** (if git enabled):
  - Phase 1 (`handle_git_init`): Creates local repo + bare hub at `~/Projects/git-repos/<name>.git`, connects via remote origin
  - Phase 2 (`finalize_git_setup`): Called after all files created; stages, commits, and pushes to hub automatically

---

## Known Issues & Cleanup Needed

- `app/core/state_validator.py` — empty placeholder (file not yet created)

---

## Development Guidelines

- **Run `uv run pytest` before committing** — 387 tests, coverage automatic
- **Add tests** in `tests/core/`, `tests/handlers/`, or `tests/utils/` for new functionality
- **Use `wrap_async()` for new async handlers** wrapping coroutines for Flet callbacks
- **Use `uv add <package>`** for dependencies, never pip
- **Follow existing patterns**: dataclasses for models, try-except with cleanup, type hints

---

## Dependencies

**Runtime:** Python 3.14+, UV (external), Flet 0.80.5+, Git (optional)

**Dev:** pytest >=8.0, pytest-asyncio >=0.23, pytest-cov >=7.0

---

## Additional Docs

Detailed historical docs live in `app/assets/docs/`:
- `CODE_REVIEW_SUMMARY.md` — Feb 5 code review (34 bugs fixed)
- `PYTEST_MIGRATION.md` — test migration details
- `COVERAGE_GUIDE.md` — per-file coverage analysis
- `HELP.md` — user-facing help text shown in app
