# Contributing to UV Forger

Thanks for your interest in contributing! UV Forger is a Flet desktop app for scaffolding Python projects with `uv`, and there are plenty of ways to help out — from reporting bugs to adding new project templates.

---

## Ways to Contribute

- **Bug reports** — Found something broken? Open an issue with steps to reproduce, your OS, and Python version.
- **Feature requests** — Have an idea? Open an issue and describe the use case.
- **New templates** — The easiest contribution. Add a new UI framework or project type — no core code changes needed in most cases.
- **New boilerplate** — Drop starter file content into `uv_forger/config/templates/boilerplate/` — also no code changes required.
- **Bug fixes and features** — Fork, branch, fix, test, PR. See below.
- **Docs** — Improvements to the [README](README.md), in-app Help text ([`uv_forger/assets/docs/HELP.md`](uv_forger/assets/docs/HELP.md)), or code comments are always welcome.

---

## Development Setup

You'll need Python 3.12+, `uv`, and Git.

```bash
git clone https://github.com/oktl/uv-forger.git
cd uv-forger
uv run uv-forger        # Run the app
uv run pytest          # Run the test suite (625 tests)
uv run ruff check uv_forger  # Lint
uv run ruff format uv_forger # Format
```

A pre-commit hook runs `ruff` automatically on commit, so you'll catch lint issues before pushing.

---

## Adding a New Framework or Project Type

This is the most common kind of contribution and is largely declarative:

1. **Add the name** to `UI_FRAMEWORKS` or `PROJECT_TYPE_PACKAGE_MAP` in `uv_forger/core/constants.py`
2. **Add the package mapping** to `FRAMEWORK_PACKAGE_MAP` (UI frameworks only)
3. **Add a display entry** to `UI_FRAMEWORK_CATEGORIES` or `PROJECT_TYPE_CATEGORIES` in `uv_forger/ui/dialog_data.py`
4. **Create a template JSON** in `uv_forger/config/templates/ui_frameworks/` or `uv_forger/config/templates/project_types/`
5. **Optionally add boilerplate** — drop starter files into `uv_forger/config/templates/boilerplate/ui_frameworks/<name>/` or `boilerplate/project_types/<name>/`. Uses `{{project_name}}` as a placeholder. No code changes needed.

The template JSON format:

```json
{
  "name": "src",
  "create_init": true,
  "root_level": false,
  "subfolders": [],
  "files": ["main.py", "config.py"]
}
```

Look at an existing template (e.g. `uv_forger/config/templates/ui_frameworks/flet.json`) for reference.

---

## Code Style

- **Linter/formatter:** Ruff — rules `E`, `F`, `I`, `W`, `UP`, `B`, `SIM`
- **Imports:** Absolute `uv_forger.*` paths only (e.g. `from uv_forger.core.state import AppState`)
- **Type hints:** Use `str | None` not `Optional[str]`; `collections.abc.Callable` not `typing.Callable`
- **Models:** Dataclasses for new data structures
- **Async:** Wrap coroutines with `wrap_async()` for Flet callbacks; use `AsyncExecutor.run()` for subprocess calls

---

## Testing

Run the full suite before opening a PR:

```bash
uv run pytest
```

Tests live in `tests/`, mirroring the `uv_forger/` structure. `pytest-asyncio` is configured in auto mode — async test functions just work.

**Please add tests** for any new functionality in `tests/core/`, `tests/handlers/`, or `tests/ui/`. Handler tests use `Handlers(MockPage(), MockControls(), AppState())` — no real Flet runtime needed.

Coverage is generated automatically. Aim to maintain or improve existing coverage.

---

## Submitting a Pull Request

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Run `uv run pytest` — all tests must pass
4. Run `uv run ruff check uv_forger` — no lint errors
5. Open a PR with a clear description of what changed and why

Small, focused PRs are much easier to review than large ones. If you're planning something significant, open an issue first so we can discuss the approach.

---

## Questions?

Open a [GitHub issue](https://github.com/oktl/uv-forger/issues) — happy to help get you oriented.
