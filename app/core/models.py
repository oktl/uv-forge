"""Data models for the project setup application.

This module defines the core data structures used throughout the application,
including project configuration, folder specifications, and build results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class FolderSpec:
    """Specification for a folder in the project structure.

    Attributes:
        name: The folder name.
        create_init: Whether to create __init__.py in this folder (default: True).
        root_level: Whether this folder should be created at project root vs app/ (default: False).
        subfolders: List of nested folder specifications (default: None).
        files: List of file names to create in this folder (default: None).
    """

    name: str
    create_init: bool = True
    root_level: bool = False
    subfolders: Optional[list[str | FolderSpec]] = None
    files: Optional[list[str]] = None

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> "FolderSpec":
        """Create a FolderSpec from a dictionary (internal use only).

        This method is provided for potential future use or testing scenarios where
        folder specs need to be reconstructed from raw dictionaries. It is not
        currently used in the application's runtime code path, which works directly
        with mixed dict/string folder structures.

        Args:
            data: Dictionary with folder specification data.

        Returns:
            FolderSpec instance.

        Raises:
            ValueError: If 'name' field is missing from data.
        """
        if "name" not in data:
            raise ValueError("FolderSpec requires 'name' field in dictionary")

        subfolders = data.get("subfolders")
        if subfolders:
            # Recursively convert subfolders
            subfolders = [
                cls._from_dict(sf) if isinstance(sf, dict) else sf for sf in subfolders
            ]

        return cls(
            name=data.get("name", ""),
            create_init=data.get("create_init", True),
            root_level=data.get("root_level", False),
            subfolders=subfolders,
            files=data.get("files"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert FolderSpec to a dictionary.

        Only includes fields with non-default values to minimize JSON output:
        - create_init (default True): only included if False
        - root_level (default False): only included if True
        - subfolders, files: only included if present

        Returns:
            Dictionary representation of the folder specification.
        """
        result = {"name": self.name}
        # Only include non-default values to minimize JSON
        if not self.create_init:
            result["create_init"] = False
        if self.root_level:
            result["root_level"] = True
        if self.subfolders:
            result["subfolders"] = [
                sf.to_dict() if isinstance(sf, FolderSpec) else sf
                for sf in self.subfolders
            ]
        if self.files:
            result["files"] = self.files
        return result


@dataclass
class ProjectConfig:
    """Configuration for a project to be created.

    This dataclass holds all configuration needed to orchestrate project creation,
    including validation, directory setup, package installation, and git initialization.

    Attributes:
        project_name: Project name (must be non-empty and pass normalize_project_name validation).
        project_path: Base path where project will be created (must be an existing directory).
        python_version: Python version to use (e.g., "3.14").
        git_enabled: Whether to initialize a git repository (default: True).
        ui_project_enabled: Whether this is a UI project (default: False).
        framework: UI framework to install (e.g., "flet", "pyqt6"). Empty string if
            ui_project_enabled is False. If ui_project_enabled is True, framework
            should be non-empty and valid (default: "").
        other_project_enabled: Whether an other project type is selected (default: False).
        project_type: Project type (e.g., "django", "fastapi") for package/template
            installation. None if other_project_enabled is False. If other_project_enabled
            is True, project_type should be non-None and valid (default: None).
        include_starter_files: Whether to populate created files with starter content
            instead of creating empty files (default: True).
        folders: List of folder specifications defining the project structure. Can mix
            strings (folder names) and FolderSpec objects. Falls back to DEFAULT_FOLDERS
            if empty (default: []).
        packages: Explicit list of packages to install. When non-empty, overrides the
            packages derived from framework/project type maps (default: []).
    """

    project_name: str
    project_path: Path
    python_version: str
    git_enabled: bool = True
    ui_project_enabled: bool = False
    framework: str = ""
    other_project_enabled: bool = False
    project_type: Optional[str] = None
    include_starter_files: bool = True
    folders: list[str | dict[str, Any] | FolderSpec] = field(default_factory=list)
    packages: list[str] = field(default_factory=list)

    @property
    def full_path(self) -> Path:
        """Get the full project path (base path + project name).

        Returns:
            Full path to the project directory.
        """
        return self.project_path / self.project_name

    @property
    def effective_framework(self) -> str | None:
        """Resolve the active UI framework, or None if UI is disabled.

        Returns:
            Framework name when ui_project_enabled is True, otherwise None.
        """
        return self.framework if self.ui_project_enabled else None

    @property
    def effective_project_type(self) -> str | None:
        """Resolve the active project type, or None if other project is disabled.

        Returns:
            Project type when other_project_enabled is True, otherwise None.
        """
        return self.project_type if self.other_project_enabled else None


@dataclass
class BuildResult:
    """Result of a project build operation.

    Attributes:
        success: Whether the build succeeded.
        message: Status or error message.
        error: Optional exception that occurred during build.
    """

    success: bool
    message: str
    error: Optional[Exception] = None


@dataclass
class BuildSummaryConfig:
    """Configuration for build summary dialog display.

    Used to pass project configuration data to the build summary dialog for user
    review before project creation. The dialog displays this information and
    provides options to proceed with the build or cancel.

    Attributes:
        project_name: Name of the project.
        project_path: Base path where project will be created.
        python_version: Selected Python version (e.g., "3.14").
        git_enabled: Whether git repository initialization is enabled.
        ui_project_enabled: Whether a UI project was selected. If True, framework
            will be non-None; if False, framework will be None.
        framework: Selected UI framework name (e.g., "Flet"), or None if
            ui_project_enabled is False.
        other_project_enabled: Whether an other project type was selected. If True,
            project_type will be non-None; if False, project_type will be None.
        project_type: Selected project type (e.g., "django", "fastapi"), or None if
            other_project_enabled is False.
        starter_files: Whether starter files will be included in the project.
        folder_count: Number of folders to be created in the project.
        file_count: Number of files to be created in the project.

    Note:
        ui_project_enabled and other_project_enabled are independent—both can be
        False, and in practice, at most one should typically be True (but the dialog
        handles all cases).
    """

    project_name: str
    project_path: str
    python_version: str
    git_enabled: bool
    ui_project_enabled: bool
    framework: Optional[str]
    other_project_enabled: bool
    project_type: Optional[str]
    starter_files: bool
    folder_count: int
    file_count: int
