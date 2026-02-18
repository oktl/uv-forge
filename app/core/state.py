"""Application state management for UV Forge.

This module defines the AppState dataclass that holds all mutable application
state, including project configuration, UI state, and validation status.
"""

from collections.abc import Callable
from dataclasses import dataclass, field, fields
from typing import Any, Literal

from app.core.constants import DEFAULT_PROJECT_ROOT, DEFAULT_PYTHON_VERSION


@dataclass
class AppState:
    """Container for application state data.

    Attributes:
        project_path: Base directory where project will be created.
        project_name: Name of the project to create.
        python_version: Python version for the project.
        git_enabled: Whether to create a git repository.
        include_starter_files: Whether to populate files with starter content.
        ui_project_enabled: Whether this is a UI framework project.
        framework: Selected UI framework (if ui_project_enabled is True).
        other_project_enabled: Whether an other project type is selected.
        project_type: Selected project type (if other_project_enabled is True).
        folders: Current folder structure from template.
        auto_save_folders: Whether to auto-save folder changes to config.
        selected_item_path: Path to selected item for folder/file removal.
        selected_item_type: Whether selected item is a "folder" or "file".
        packages: List of packages to install (pre-populated from framework/project type, user-editable).
        auto_packages: Last set of packages derived from maps; used to distinguish user additions from auto ones.
        selected_package_idx: Index of selected package for removal, or None.
        is_dark_mode: Whether dark theme is active.
        path_valid: Whether the current path passes validation.
        name_valid: Whether the current project name passes validation.
    """

    # Path and project settings
    project_path: str = str(DEFAULT_PROJECT_ROOT)
    project_name: str = ""

    # Options
    python_version: str = DEFAULT_PYTHON_VERSION
    git_enabled: bool = True
    include_starter_files: bool = True
    ui_project_enabled: bool = False
    framework: str | None = None
    other_project_enabled: bool = False
    project_type: str | None = None

    # Folder management
    folders: list[str | dict[str, Any]] = field(default_factory=list)
    auto_save_folders: bool = False

    # Selection tracking for folder/file removal
    selected_item_path: list[int | str] | None = None
    selected_item_type: Literal["folder", "file"] | None = None

    # Package management
    packages: list[str] = field(default_factory=list)
    auto_packages: list[str] = field(
        default_factory=list
    )  # map-derived; used to detect manual additions
    selected_package_idx: int | None = None

    # UI state
    is_dark_mode: bool = True
    active_dialog: Callable[[], None] | None = None  # Currently open dismissible dialog

    # Validation state
    path_valid: bool = True  # Default path is valid
    name_valid: bool = False  # Empty name is invalid

    def reset(self) -> None:
        """Reset state to initial values.

        Preserves is_dark_mode since theme preference should persist.
        """
        preserved_dark_mode = self.is_dark_mode
        fresh = AppState()
        for attr in fields(self):
            setattr(self, attr.name, getattr(fresh, attr.name))
        self.is_dark_mode = preserved_dark_mode
