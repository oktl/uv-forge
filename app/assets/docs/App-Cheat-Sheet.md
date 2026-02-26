# UV Forge Cheat Sheet

## Keyboard Shortcuts

| Shortcut | Action                  |
| -------- | ----------------------- |
| `⌘Enter` | Build project           |
| `⌘F`     | Add folder or file      |
| `⌘P`     | Add packages            |
| `⌘R`     | Reset all fields        |
| `⌘/`     | Open Help               |
| `Esc`    | Close dialog / Exit app |

On Windows/Linux, replace ⌘ with Ctrl.

---

## Quick Build Checklist

1. Enter a **project name** (valid Python package name)
2. Set **project path** (default from Settings)
3. Pick **Python version** (default: 3.14)
4. Optionally enable **Git**, **UI framework**, **project type**
5. `⌘Enter` → review confirm dialog → **Build**

---

## Build Pipeline

| Step | What happens                                       |
| ---- | -------------------------------------------------- |
| 1    | Create project directory                           |
| 2    | `uv init` — scaffolds pyproject.toml               |
| 3    | Git Phase 1 — local repo + bare hub + origin       |
| 4    | Create folder structure from templates             |
| 5    | Populate files with boilerplate starter content    |
| 6    | Configure pyproject.toml (metadata, authors, etc.) |
| 7    | `uv venv` — create virtual environment             |
| 8    | `uv add` — install packages (+ `--dev` for dev)    |
| 9    | Git Phase 2 — stage, commit, push to hub           |
| 10   | Run post-build command (if enabled)                |

---

## Template Merging (Framework + Project Type)

| Scenario          | Result                                                            |
| ----------------- | ----------------------------------------------------------------- |
| Framework only    | Framework template (fallback → default → hardcoded)               |
| Project type only | Project type template loaded                                      |
| Both selected     | Merged — matching folders combined, unique folders kept from both |
| Neither           | Default template structure                                        |

**Merge rules:** folders matched by name → subfolders merged recursively, files unioned, booleans OR'd.

---

## Smart Scaffolding (Boilerplate)

Files get starter content instead of being empty. Fallback chain:

1. `boilerplate/ui_frameworks/{framework}/{file}` — framework-specific
2. `boilerplate/project_types/{type}/{file}` — project-type-specific
3. `boilerplate/common/{file}` — shared utilities
4. Empty file — if no boilerplate found

`{{project_name}}` in templates → replaced with title case (e.g., `my_app` → `My App`).

---

## PyPI Name Check

Click the globe icon next to the project name field:

| Colour | Meaning                         |
| ------ | ------------------------------- |
| Green  | Name available on PyPI          |
| Red    | Name taken (PEP 503 normalized) |
| Orange | Could not reach PyPI            |

Names are normalized: `my_app` = `my-app` = `my.app`.

---

## Packages

| Action          | How                                                     |
| --------------- | ------------------------------------------------------- |
| Add packages    | `⌘P` → type name → Enter                                |
| Mark as dev     | Select package → "Toggle Dev" (or checkbox when adding) |
| Clear all       | "Clear Packages" button (confirms first)                |
| PyPI validation | Each package checked live in the Add dialog             |

Dev packages install with `uv add --dev` → `[dependency-groups]` in pyproject.toml. Shown with an amber "dev" badge.

---

## Settings Quick Reference

| Setting              | What it does                                 |
| -------------------- | -------------------------------------------- |
| Default Project Path | Where new projects are created               |
| GitHub Root          | Location for bare hub repositories           |
| Python Version       | Default version for new projects             |
| Preferred IDE        | IDE for "Open in IDE" post-build action      |
| Git Default          | Whether Git checkbox is pre-checked          |
| Author Name/Email    | Default project metadata                     |
| Post-build Command   | Shell command run after successful builds    |
| Post-build Packages  | Packages auto-installed when command enabled |

Settings stored in `~/Library/Application Support/UV Forge/settings.json` (macOS), `%LOCALAPPDATA%\UV Forge\settings.json` (Windows), or `~/.local/share/UV Forge/settings.json` (Linux).

---

## Presets vs Recent Projects

| Feature   | Presets                    | Recent Projects        |
| --------- | -------------------------- | ---------------------- |
| Purpose   | Reusable project templates | History of past builds |
| Limit     | Unlimited (user presets)   | Last 5 builds          |
| Built-ins | 4 starter presets included | None                   |
| Saves     | Config only (no name/path) | Full build snapshot    |
| On apply  | Keeps current name & path  | Restores everything    |
| Storage   | `presets.json`             | `recent_projects.json` |

**Built-in presets:** Flet Desktop App, FastAPI Backend, Data Science Starter, CLI Tool (Typer). Shown with a teal "Built-in" badge; cannot be deleted.

---

## Post-Build Command

Configure in Settings → runs after every successful build.

- Command runs in the new project directory with `shell=True`
- 30-second timeout
- Required packages (comma-separated) auto-installed during build
- Override per-build in the confirm dialog

Example: `uv run pre-commit install && uv run pytest`

---

## Git Two-Phase Setup

| Phase | When            | What                                         |
| ----- | --------------- | -------------------------------------------- |
| 1     | During build    | `git init` + bare hub + `remote add origin`  |
| 2     | After all files | `git add .` + commit + `push -u origin HEAD` |

Hub path configurable in Settings → GitHub Root.

---

## See Also

- [Help & Documentation](app://help) — Full usage guide
- [Git Cheat Sheet](app://git-cheat-sheet) — Git command reference
- [About UV Forge](app://about) — App info and tech stack
