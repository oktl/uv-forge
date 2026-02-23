"""User settings management for UV Forge.

Handles loading and saving user preferences to a JSON file in the
platform-appropriate data directory. Settings that were previously
hardcoded constants (default paths, Python version, IDE preference)
are now user-configurable.
"""

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

import platformdirs

APP_NAME = "UV Forge"
SETTINGS_DIR = Path(platformdirs.user_data_dir(APP_NAME))
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


@dataclass
class AppSettings:
    """User-configurable application settings.

    Attributes:
        default_project_path: Base directory for new projects.
        default_github_root: Base directory for bare git hub repos.
        default_python_version: Python version used for new projects.
        preferred_ide: Display name of the preferred IDE (key in SUPPORTED_IDES).
        custom_ide_path: Executable path when preferred_ide is "Other / Custom".
        git_enabled_default: Whether git init is enabled by default.
    """

    default_project_path: str = str(Path.home() / "Projects")
    default_github_root: str = str(Path.home() / "Projects" / "git-repos")
    default_python_version: str = "3.14"
    preferred_ide: str = "VS Code"
    custom_ide_path: str = ""
    git_enabled_default: bool = True
    default_author_name: str = ""
    default_author_email: str = ""
    post_build_command: str = ""
    post_build_command_enabled: bool = False
    post_build_packages: str = ""


def load_settings() -> AppSettings:
    """Load settings from disk, using defaults for any missing keys.

    If the settings file doesn't exist, returns an AppSettings with all
    defaults and writes it to disk for next time.

    Returns:
        AppSettings populated from the saved file or defaults.
    """
    if not SETTINGS_FILE.exists():
        settings = AppSettings()
        save_settings(settings)
        return settings

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return AppSettings()

    # Forward-compatible: only use keys that exist as fields
    valid_keys = {f.name for f in fields(AppSettings)}
    filtered = {k: v for k, v in data.items() if k in valid_keys}
    return AppSettings(**filtered)


def save_settings(settings: AppSettings) -> None:
    """Write settings to disk as JSON.

    Creates the settings directory if it doesn't exist.

    Args:
        settings: The AppSettings instance to persist.
    """
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        json.dumps(asdict(settings), indent=2) + "\n",
        encoding="utf-8",
    )
