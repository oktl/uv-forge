"""Project build orchestration

This module coordinates the complete project creation pipeline,
including validation, directory creation, UV operations, git setup,
and error handling with rollback.
"""

import shutil
import subprocess
from pathlib import Path

from app.core.boilerplate_resolver import BoilerplateResolver
from app.core.models import BuildResult, ProjectConfig
from app.core.validator import validate_project_name
from app.handlers.filesystem_handler import setup_app_structure
from app.handlers.git_handler import handle_git_init, finalize_git_setup
from app.handlers.uv_handler import (
    configure_pyproject,
    install_package,
    run_uv_init,
    setup_virtual_env,
)
from app.core.constants import (
    DEFAULT_GIT_HUB_ROOT,
    FRAMEWORK_PACKAGE_MAP,
    PROJECT_TYPE_PACKAGE_MAP,
)


def cleanup_on_error(
    project_path: Path, bare_repo_path: Path | None = None
) -> None:
    """Remove partially created project on build failure.

    Args:
        project_path: Path to the project directory to remove.
        bare_repo_path: Path to the bare hub repo to remove, if one was
            created during this build. Only passed when git was enabled.
    """
    if project_path.exists():
        shutil.rmtree(project_path)
    if bare_repo_path is not None and bare_repo_path.exists():
        shutil.rmtree(bare_repo_path)


def build_project(config: ProjectConfig) -> BuildResult:
    """Build a new UV project with all configured settings.

    Orchestrates the complete project creation pipeline:
    1. Validates project name
    2. Creates project directory
    3. Runs uv_init
    4. Handles git initialization
    5. Sets up app structure with folders
    6. Configures pyproject.toml
    7. Creates virtual environment
    8. Installs UI framework (if selected)
    9. Installs project type packages (if selected)

    Args:
        config: ProjectConfig containing all project settings.

    Returns:
        BuildResult indicating success or failure with message.
    """
    # Validate project name
    is_valid, error_msg = validate_project_name(config.project_name)
    if not is_valid:
        return BuildResult(success=False, message=error_msg)

    full_path = config.full_path
    bare_repo_path = (
        DEFAULT_GIT_HUB_ROOT / f"{full_path.name}.git" if config.git_enabled else None
    )

    # Ensure the base directory exists
    if not config.project_path.exists():
        try:
            config.project_path.mkdir(parents=True)
        except OSError as e:
            return BuildResult(
                success=False,
                message=f"Could not create base directory: {e}",
                error=e,
            )

    # Build the project
    try:
        full_path.mkdir(parents=True)

        # Execute the build steps
        run_uv_init(full_path, config.python_version)
        handle_git_init(full_path, config.git_enabled)
        if config.include_starter_files:
            resolver = BoilerplateResolver(
                project_name=config.project_name,
                framework=config.framework if config.ui_project_enabled else None,
                project_type=config.project_type,
            )
        else:
            resolver = None
        setup_app_structure(
            full_path,
            config.folders,
            resolver=resolver,
            skip_files=not config.include_starter_files,
        )
        configure_pyproject(
            full_path,
            config.project_name,
            framework=config.framework if config.ui_project_enabled else None,
            project_type=config.project_type,
        )
        setup_virtual_env(full_path, config.python_version)

        # Install UI framework if selected
        if config.ui_project_enabled:
            package_name = FRAMEWORK_PACKAGE_MAP.get(config.framework)
            if package_name:  # Skip if None (e.g., tkinter is built-in)
                install_package(full_path, package_name)

        # Install project type packages if selected
        if config.project_type:
            packages = PROJECT_TYPE_PACKAGE_MAP.get(config.project_type, [])
            for package in packages:
                install_package(full_path, package)

        # NEW: Finalize git after all files and packages are installed
        finalize_git_setup(full_path, config.git_enabled)

        return BuildResult(
            success=True, message=f"Project Created Successfully! Built at: {full_path}"
        )

    except subprocess.CalledProcessError as e:
        cleanup_on_error(full_path, bare_repo_path)
        error_detail = f"Command failed: {' '.join(e.cmd)}"
        if e.stderr:
            error_detail += f"\n\nError output:\n{e.stderr}"
        return BuildResult(success=False, message=error_detail, error=e)
    except OSError as e:
        cleanup_on_error(full_path, bare_repo_path)
        return BuildResult(
            success=False,
            message=f"Could not create project files: {e}",
            error=e,
        )
    except Exception as e:
        cleanup_on_error(full_path, bare_repo_path)
        return BuildResult(
            success=False,
            message=f"An unexpected error occurred: {e}",
        )
