# Troubleshooting

## "Project already exists at this location"

Choose a different project name or change the project path.

## "UV command not found"

UV is required but not installed. Install it from [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/).

## "Git command not found"

Git is optional — uncheck the Git Repository checkbox if you don't need it. Otherwise, install Git from [git-scm.com](https://git-scm.com/).

## Build fails mid-way

- Check your internet connection (needed for package installation)
- Ensure you have sufficient disk space
- The partial project directory is automatically cleaned up on failure

## Packages fail to install

- Verify the package name is correct (check PyPI)
- Some packages have platform-specific requirements (e.g., `torch` may need specific Python versions)
- Check the [log viewer](../guide/settings.md) for detailed error output

## Settings or presets not saving

UV Forger stores data in your platform's user data directory. Ensure you have write permissions to:

| Platform | Path                                      |
| -------- | ----------------------------------------- |
| macOS    | `~/Library/Application Support/UV Forger/` |
| Linux    | `~/.local/share/UV Forger/`                |
| Windows  | `%LOCALAPPDATA%/UV Forger/`                |

## App won't start

```bash
# Check Python version (3.12+ required)
python --version

# Try running directly
uv run python uv_forger/main.py

# Check for missing dependencies
uv sync
```

## Still stuck?

Open an issue on [GitHub](https://github.com/oktl/uv-forger/issues) with:

- Your OS and Python version
- Steps to reproduce the problem
- Any error messages from the log viewer
