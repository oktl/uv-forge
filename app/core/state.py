"""Application state management for the UV Project Creator.

This module defines the AppState dataclass that holds all mutable application
state, including project configuration, UI state, and validation status.
"""

from dataclasses import dataclass, field
from typing import Optional

from app.utils.constants import DEFAULT_PROJECT_ROOT, DEFAULT_PYTHON_VERSION


@dataclass
class AppState:
    """Container for application state data.

    Attributes:
        project_path: Base directory where project will be created.
        project_name: Name of the project to create.
        selected_python_version: Python version for the project.
        initialize_git: Whether to create a git repository.
        create_ui_project: Whether this is a UI framework project.
        selected_framework: Selected UI framework (if create_ui_project is True).
        folders: Current folder structure from template.
        auto_save_folders: Whether to auto-save folder changes to config.
        is_dark_mode: Whether dark theme is active.
        path_valid: Whether the current path passes validation.
        name_valid: Whether the current project name passes validation.
    """

    # Path and project settings
    project_path: str = DEFAULT_PROJECT_ROOT
    project_name: str = ""

    # Options
    selected_python_version: str = DEFAULT_PYTHON_VERSION
    initialize_git: bool = True
    include_starter_files: bool = True
    create_ui_project: bool = False
    selected_framework: Optional[str] = None
    create_other_project: bool = False
    selected_project_type: Optional[str] = None

    # Folder management
    folders: list = field(default_factory=list)
    auto_save_folders: bool = False

    # Selection tracking for folder/file removal
    selected_item_path: Optional[list] = (
        None  # Path to selected item, e.g., [0, "subfolders", 1]
    )
    selected_item_type: Optional[str] = None  # "folder" or "file"

    # UI state
    is_dark_mode: bool = True

    # Validation state
    path_valid: bool = True  # Default path is valid
    name_valid: bool = False  # Empty name is invalid

    def reset(self) -> None:
        """Reset state to initial values.

        Preserves is_dark_mode since theme preference should persist.
        """
        self.project_path = DEFAULT_PROJECT_ROOT
        self.project_name = ""
        self.selected_python_version = DEFAULT_PYTHON_VERSION
        self.initialize_git = True
        self.include_starter_files = True
        self.create_ui_project = False
        self.selected_framework = None
        self.create_other_project = False
        self.selected_project_type = None
        self.folders = []
        self.auto_save_folders = False
        self.selected_item_path = None
        self.selected_item_type = None
        self.path_valid = True
        self.name_valid = False
