"""Project build orchestration.

This module coordinates the complete project creation pipeline,
including validation, directory creation, UV operations, git setup,
and error handling with rollback.
"""

import shutil
import subprocess
from pathlib import Path

from core.models import ProjectConfig, BuildResult
from core.validator import validate_project_name
from handlers.uv_handler import (
    run_uv_init,
    setup_virtual_env,
    configure_pyproject,
    install_package,
)
from handlers.git_handler import handle_git_init
from handlers.filesystem_handler import setup_app_structure
from utils.constants import FRAMEWORK_PACKAGE_MAP


def cleanup_on_error(project_path: Path) -> None:
    """Remove partially created project directory on build failure.

    Args:
        project_path: Path to the project directory to remove.
    """
    if project_path.exists():
        shutil.rmtree(project_path)


def build_project(config: ProjectConfig) -> BuildResult:
    """Build a new UV project with all configured settings.

    Orchestrates the complete project creation pipeline:
    1. Validates project name
    2. Creates project directory
    3. Runs uv init
    4. Handles git initialization
    5. Sets up app structure with folders
    6. Configures pyproject.toml
    7. Creates virtual environment
    8. Installs UI framework (if selected)

    Args:
        config: ProjectConfig containing all project settings.

    Returns:
        BuildResult indicating success or failure with message.
    """
    # Validate project name
    is_valid, error_msg = validate_project_name(config.name)
    if not is_valid:
        return BuildResult(success=False, message=error_msg)

    full_path = config.full_path

    # Ensure the base directory exists
    if not config.path.exists():
        try:
            config.path.mkdir(parents=True)
        except OSError as e:
            return BuildResult(
                success=False,
                message=f"Could not create base directory: {e}",
                error=e,
            )

    # Check if project already exists
    if full_path.exists():
        return BuildResult(
            success=False,
            message=f"The folder '{config.name}' already exists in this location.",
        )

    # Build the project
    try:
        full_path.mkdir(parents=True)

        # Execute build steps
        run_uv_init(full_path, config.python_version)
        handle_git_init(full_path, config.git_enabled)
        setup_app_structure(full_path, config.folders)
        configure_pyproject(full_path, config.name)
        setup_virtual_env(full_path, config.python_version)

        # Install UI framework if selected
        if config.ui_project_enabled:
            package_name = FRAMEWORK_PACKAGE_MAP.get(config.framework)
            if package_name:  # Skip if None (e.g., tkinter built-in)
                install_package(full_path, package_name)

        return BuildResult(
            success=True,
            message=f"Project Created Successfully! Built at: {full_path}",
        )

    except subprocess.CalledProcessError as e:
        cleanup_on_error(full_path)
        error_detail = f"Command failed: {' '.join(e.cmd)}"
        if e.stderr:
            error_detail += f"\n\nError output:\n{e.stderr}"
        return BuildResult(success=False, message=error_detail, error=e)

    except OSError as e:
        cleanup_on_error(full_path)
        return BuildResult(
            success=False,
            message=f"Could not create project files: {e}",
            error=e,
        )

    except Exception as e:
        cleanup_on_error(full_path)
        return BuildResult(
            success=False,
            message=f"An unexpected error occurred: {e}",
            error=e,
        )
