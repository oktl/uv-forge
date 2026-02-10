"""Data models for the project setup application.

This module defines the core data structures used throughout the application,
including project configuration, folder specifications, and build results.
"""

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
    subfolders: Optional[list[Any]] = None  # Can contain str or FolderSpec
    files: Optional[list[str]] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FolderSpec":
        """Create a FolderSpec from a dictionary.

        Args:
            data: Dictionary with folder specification data.

        Returns:
            FolderSpec instance.
        """
        subfolders = data.get("subfolders")
        if subfolders:
            # Recursively convert subfolders
            subfolders = [
                cls.from_dict(sf) if isinstance(sf, dict) else sf for sf in subfolders
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

        Returns:
            Dictionary representation of the folder specification.
        """
        result = {"name": self.name}
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

    Attributes:
        name: Project name.
        path: Base path where project will be created.
        python_version: Python version to use (e.g., "3.14").
        git_enabled: Whether to initialize a git repository.
        ui_project_enabled: Whether this is a UI project.
        framework: UI framework to install (if ui_project_enabled is True).
        project_type: Project type (e.g., "django", "fastapi") if other_project_enabled is True.
        folders: List of folder specifications (can be str or dict/FolderSpec).
    """

    name: str
    path: Path
    python_version: str
    git_enabled: bool
    ui_project_enabled: bool
    framework: str
    project_type: Optional[str] = None
    include_starter_files: bool = True
    folders: list[str | dict[str, Any] | FolderSpec] = field(default_factory=list)

    @property
    def full_path(self) -> Path:
        """Get the full project path (base path + project name).

        Returns:
            Full path to the project directory.
        """
        return self.path / self.name


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

    Attributes:
        project_name: Name of the project.
        project_path: Base path where project will be created.
        python_version: Selected Python version.
        git_enabled: Whether git initialization is enabled.
        framework: Selected UI framework (or None).
        project_type: Selected project type (or None).
        starter_files: Whether starter files are included.
        folder_count: Number of folders to be created.
        file_count: Number of files to be created.
    """

    project_name: str
    project_path: str
    python_version: str
    git_enabled: bool
    framework: Optional[str]
    project_type: Optional[str]
    starter_files: bool
    folder_count: int
    file_count: int
