# Post-Build Automation

UV Forger can run a shell command automatically after each successful build. This is useful for setup steps that should happen in every new project.

## Common examples

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit and tests
uv run pre-commit install && uv run pytest

# Open the project in a browser (for web frameworks)
open http://localhost:8000
```

## Configuration

Set up your post-build command in [Settings](settings.md):

- **Post-build Command** — The shell command to run
- **Enable post-build command** — Default on/off for the checkbox in the confirm dialog
- **Post-build Packages** — Comma-separated packages required by the command (e.g., `pre-commit`). These are automatically added to the project's package list when the post-build command is enabled.

## Per-build override

The **Confirm Build** dialog shows a checkbox and editable command field for the post-build command. You can:

- Toggle it on/off for this specific build
- Edit the command for a one-time change

The defaults come from Settings, but per-build changes don't affect your saved settings.

## How it works

1. Required packages (from `post_build_packages`) are merged into the build's package list
2. The build completes normally (folders, files, packages, git)
3. The post-build command runs via `subprocess.run(shell=True, timeout=30)` in the new project directory
4. A snackbar shows success or failure; output is logged via loguru
