"""Filesystem operations for project structure creation.

This module handles creating directories, __init__.py files, and processing
nested folder structures from configuration specifications.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.core.boilerplate_resolver import BoilerplateResolver


def create_folders(
    parent_dir: Path,
    folders: list[str | dict[str, Any]],
    parent_create_init: bool = True,
    resolver: "BoilerplateResolver | None" = None,
    skip_files: bool = False,
) -> None:
    """Recursively create directory structure from configuration.

    Processes folder specifications and creates the corresponding filesystem
    structure. Supports both simple string entries and complex nested objects
    with configuration options.

    Args:
        parent_dir: Parent directory where folders should be created.
        folders: List of folder specifications (strings or dict objects).
        parent_create_init: Whether parent's create_init setting was True (default: True).
        resolver: Optional BoilerplateResolver for populating files with starter content.
        skip_files: When True, skip creating template files (only dirs + __init__.py).

    Folder specification formats:
        - String: "core" -> creates core/ with __init__.py
        - Object: {
            "name": "assets",
            "create_init": false,
            "root_level": false,
            "subfolders": [...],
            "files": ["event_handlers.py", ...]
        }
    """
    for folder_spec in folders:
        if isinstance(folder_spec, str):
            # Simple string folder
            target = parent_dir / folder_spec
            target.mkdir(parents=True, exist_ok=True)
            if parent_create_init:
                (target / "__init__.py").touch()
        elif isinstance(folder_spec, dict):
            # Structured folder with possible subfolders and files
            folder_name = folder_spec.get("name", "")
            create_init = folder_spec.get("create_init", True)
            subfolders = folder_spec.get("subfolders", [])
            files = folder_spec.get("files", [])

            if not folder_name:
                continue

            target = parent_dir / folder_name
            target.mkdir(parents=True, exist_ok=True)
            if create_init:
                (target / "__init__.py").touch()

            # Create specified files in this folder
            if files and not skip_files:
                for file_name in files:
                    file_path = target / file_name
                    content = resolver.resolve(file_name) if resolver else None
                    if content is not None:
                        file_path.write_text(content, encoding="utf-8")
                    else:
                        file_path.touch()

            # Recursively create subfolders
            if subfolders:
                create_folders(target, subfolders, create_init, resolver, skip_files)


def setup_app_structure(
    project_path: Path,
    folders: list[str | dict[str, Any]],
    resolver: "BoilerplateResolver | None" = None,
    skip_files: bool = False,
) -> None:
    """Create app directory and configured folder structure.

    Creates the app/ directory with __init__.py, then processes the folder
    configuration to create root-level folders (at project root) and
    app-level folders (inside app/). Moves hello.py to app/main.py if present.

    Args:
        project_path: Path to the project directory.
        folders: List of folder specifications from configuration.
        resolver: Optional BoilerplateResolver for populating files with starter content.
        skip_files: When True, skip creating template files (only dirs + __init__.py).
    """
    app_dir = project_path / "app"
    app_dir.mkdir(exist_ok=True)
    (app_dir / "__init__.py").touch()

    # Separate folders into root-level and app-level
    root_folders = []
    app_folders = []

    for folder_spec in folders:
        if isinstance(folder_spec, dict) and folder_spec.get("root_level", False):
            root_folders.append(folder_spec)
        else:
            app_folders.append(folder_spec)

    # Create root-level folders at project root
    if root_folders:
        create_folders(project_path, root_folders, resolver=resolver, skip_files=skip_files)

    # Create app-level folders inside app/
    if app_folders:
        create_folders(app_dir, app_folders, resolver=resolver, skip_files=skip_files)

    # Move main.py to app/main.py if it exists (uv init creates main.py)
    main_py = project_path / "main.py"
    app_main = app_dir / "main.py"
    if main_py.exists():
        main_py.rename(app_main)

    # Replace UV's default main.py and README.md with boilerplate if available
    if resolver and not skip_files:
        content = resolver.resolve("main.py")
        if content is not None:
            app_main.write_text(content, encoding="utf-8")

        readme_content = resolver.resolve("README.md")
        if readme_content is not None:
            (project_path / "README.md").write_text(readme_content, encoding="utf-8")
