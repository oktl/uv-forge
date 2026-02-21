"""Project preset management for UV Forge.

Handles saving and loading named project presets to a JSON file in the
platform-appropriate data directory. Presets store a full project
configuration (framework, project type, packages, folders, etc.) that
can be applied to quickly set up a new project.
"""

import datetime
import json
from dataclasses import asdict, dataclass, field, fields
from typing import Any

from app.core.settings_manager import SETTINGS_DIR

PRESETS_FILE = SETTINGS_DIR / "presets.json"


@dataclass
class ProjectPreset:
    """A named project configuration preset.

    Attributes:
        name: User-given label for this preset.
        python_version: Python version to use.
        git_enabled: Whether to initialize git.
        include_starter_files: Whether to populate files with starter content.
        ui_project_enabled: Whether a UI framework is selected.
        framework: Selected UI framework name, or None.
        other_project_enabled: Whether a project type is selected.
        project_type: Selected project type name, or None.
        folders: Folder structure.
        packages: Packages to install.
        dev_packages: Packages marked as dev dependencies.
        author_name: Default author name for pyproject.toml.
        author_email: Default author email for pyproject.toml.
        description: Project description for pyproject.toml.
        license_type: SPDX license identifier.
        saved_at: ISO-format timestamp of when the preset was saved.
    """

    name: str
    python_version: str
    git_enabled: bool
    include_starter_files: bool
    ui_project_enabled: bool
    framework: str | None
    other_project_enabled: bool
    project_type: str | None
    folders: list[str | dict[str, Any]]
    packages: list[str]
    dev_packages: list[str] = field(default_factory=list)
    author_name: str = ""
    author_email: str = ""
    description: str = ""
    license_type: str = ""
    saved_at: str = ""


def load_presets() -> list[ProjectPreset]:
    """Load presets from disk.

    Returns:
        List of ProjectPreset, newest first. Empty list if file
        is missing or corrupted.
    """
    if not PRESETS_FILE.exists():
        return []

    try:
        data = json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError, OSError:
        return []

    if not isinstance(data, list):
        return []

    valid_keys = {f.name for f in fields(ProjectPreset)}
    presets = []
    for item in data:
        if not isinstance(item, dict):
            continue
        filtered = {k: v for k, v in item.items() if k in valid_keys}
        try:
            presets.append(ProjectPreset(**filtered))
        except TypeError:
            continue
    return presets


def save_presets(presets: list[ProjectPreset]) -> None:
    """Write presets to disk as JSON.

    Creates the settings directory if it doesn't exist.

    Args:
        presets: List of ProjectPreset to persist.
    """
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    PRESETS_FILE.write_text(
        json.dumps([asdict(p) for p in presets], indent=2) + "\n",
        encoding="utf-8",
    )


def add_preset(preset: ProjectPreset) -> None:
    """Add or update a preset, deduplicating by name.

    The new preset is prepended. If a preset with the same name already
    exists, it is replaced.

    Args:
        preset: The ProjectPreset to add.
    """
    presets = load_presets()
    presets = [p for p in presets if p.name != preset.name]
    presets.insert(0, preset)
    save_presets(presets)


def delete_preset(name: str) -> None:
    """Remove a preset by name.

    Args:
        name: The name of the preset to delete.
    """
    presets = load_presets()
    presets = [p for p in presets if p.name != name]
    save_presets(presets)


def make_preset(
    name: str,
    python_version: str,
    git_enabled: bool,
    include_starter_files: bool,
    ui_project_enabled: bool,
    framework: str | None,
    other_project_enabled: bool,
    project_type: str | None,
    folders: list,
    packages: list[str],
    dev_packages: list[str] | None = None,
    author_name: str = "",
    author_email: str = "",
    description: str = "",
    license_type: str = "",
) -> ProjectPreset:
    """Create a ProjectPreset with the current timestamp.

    Args:
        name: User-given label for this preset.
        python_version: Python version to use.
        git_enabled: Whether to initialize git.
        include_starter_files: Whether to populate files with starter content.
        ui_project_enabled: Whether a UI framework is selected.
        framework: Selected UI framework name, or None.
        other_project_enabled: Whether a project type is selected.
        project_type: Selected project type name, or None.
        folders: Folder structure.
        packages: Packages to install.
        dev_packages: Packages marked as dev dependencies.
        author_name: Default author name.
        author_email: Default author email.
        description: Project description.
        license_type: SPDX license identifier.

    Returns:
        A new ProjectPreset with saved_at set to now.
    """
    return ProjectPreset(
        name=name,
        python_version=python_version,
        git_enabled=git_enabled,
        include_starter_files=include_starter_files,
        ui_project_enabled=ui_project_enabled,
        framework=framework,
        other_project_enabled=other_project_enabled,
        project_type=project_type,
        folders=list(folders),
        packages=list(packages),
        dev_packages=list(dev_packages) if dev_packages else [],
        author_name=author_name,
        author_email=author_email,
        description=description,
        license_type=license_type,
        saved_at=datetime.datetime.now(datetime.UTC).isoformat(),
    )
