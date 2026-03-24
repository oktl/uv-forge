"""User settings management for UV Forger.

Handles loading and saving user preferences to a JSON file in the
platform-appropriate data directory. Settings that were previously
hardcoded constants (default paths, Python version, IDE preference)
are now user-configurable.
"""

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

import platformdirs

APP_NAME = "UV Forger"
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
        starter_files_default: Whether to include starter files by default.
        default_license: Default SPDX license identifier for new projects.
        default_author_name: Default author name for project metadata.
        default_author_email: Default author email for project metadata.
        open_folder_default: Whether to open project folder after build by default.
        open_terminal_default: Whether to open terminal at project root after build by default.
        post_build_command: Shell command to run after a successful build.
        post_build_command_enabled: Whether the post-build command runs by default.
        post_build_packages: Comma-separated packages required by the post-build command.
        git_remote_mode: Git remote strategy: "local", "github", or "none".
        github_username: GitHub username for repo creation when git_remote_mode is "github".
        github_repo_private: Whether GitHub repos are created as private by default.
        custom_templates_path: Custom directory for user-level project templates.
    """

    default_project_path: str = str(Path.home() / "Projects")
    default_github_root: str = str(Path.home() / "Projects" / "git-repos")
    default_python_version: str = "3.14"
    preferred_ide: str = "VS Code"
    custom_ide_path: str = ""
    git_enabled_default: bool = True
    starter_files_default: bool = True
    default_license: str = ""
    default_author_name: str = ""
    default_author_email: str = ""
    open_folder_default: bool = False
    open_terminal_default: bool = False
    post_build_command: str = ""
    post_build_command_enabled: bool = False
    post_build_packages: str = ""
    git_remote_mode: str = "local"
    github_username: str = ""
    github_repo_private: bool = True
    custom_templates_path: str = ""


def get_user_templates_dir(settings: AppSettings | None = None) -> Path:
    """Return the effective user templates directory.

    Uses custom_templates_path if set, otherwise SETTINGS_DIR / "templates".
    Does NOT create the directory — that happens only on save.

    Args:
        settings: Optional AppSettings to read custom_templates_path from.

    Returns:
        Path to the user templates directory.
    """
    if settings and settings.custom_templates_path:
        return Path(settings.custom_templates_path)
    return SETTINGS_DIR / "templates"


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
