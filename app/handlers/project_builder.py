"""Project build orchestration

This module coordinates the complete project creation pipeline,
including validation, directory creation, UV operations, git setup,
and error handling with rollback.
"""

import shutil
from collections.abc import Callable
from pathlib import Path
from subprocess import CalledProcessError

from app.core.boilerplate_resolver import BoilerplateResolver
from app.core.constants import FRAMEWORK_PACKAGE_MAP, PROJECT_TYPE_PACKAGE_MAP
from app.core.models import BuildResult, ProjectConfig
from app.core.validator import validate_project_name
from app.handlers.filesystem_handler import setup_app_structure
from app.handlers.git_handler import (
    finalize_git_setup,
    get_bare_repo_path,
    handle_git_init,
)
from app.handlers.uv_handler import (
    configure_pyproject,
    install_packages,
    run_uv_init,
    setup_virtual_env,
)


def remove_partial_project(
    project_path: Path, bare_repo_path: Path | None = None
) -> None:
    """Remove partially created project directories on build failure.

    Args:
        project_path: Path to the project directory to remove.
        bare_repo_path: Path to the bare hub repo to remove, if one was
            created during this build. Only passed when git was enabled.
    """
    if project_path.exists():
        shutil.rmtree(project_path)
    if bare_repo_path is not None and bare_repo_path.exists():
        shutil.rmtree(bare_repo_path)


def _collect_packages_to_install(config: ProjectConfig) -> list[str]:
    """Gather all packages required by the project configuration.

    Checks both the UI framework (guarded by ui_project_enabled) and
    the project type (guarded by other_project_enabled) to build a
    single list suitable for a batch ``uv add`` invocation.

    Args:
        config: ProjectConfig containing framework and project type settings.

    Returns:
        List of package name strings to install (may be empty).
    """
    # If the user has an explicit package list, use it directly
    if config.packages:
        return list(config.packages)

    # Fallback: derive from framework and project type maps
    packages: list[str] = []

    if config.ui_project_enabled:
        framework_package = FRAMEWORK_PACKAGE_MAP.get(config.framework)
        if framework_package:  # None for built-ins like tkinter
            packages.append(framework_package)

    if config.other_project_enabled:
        packages.extend(PROJECT_TYPE_PACKAGE_MAP.get(config.project_type, []))

    return packages


def _create_project_scaffold(
    config: ProjectConfig,
    project_path: Path,
    on_progress: Callable[[str], None] | None = None,
) -> None:
    """Initialize project structure: UV init, git, folders, and pyproject.

    Runs the core scaffolding steps that produce the on-disk project layout
    before any dependency installation.

    Args:
        config: ProjectConfig containing all project settings.
        project_path: Absolute path to the project directory.
        on_progress: Optional callback invoked with a status string before each step.
    """

    def _p(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    _p("Initializing UV project...")
    run_uv_init(project_path, config.python_version)

    if config.git_enabled:
        _p("Setting up Git repository...")
    handle_git_init(project_path, config.git_enabled)

    resolver = (
        BoilerplateResolver(
            project_name=config.project_name,
            framework=config.effective_framework,
            project_type=config.project_type,
        )
        if config.include_starter_files
        else None
    )

    _p("Creating folder structure...")
    setup_app_structure(
        project_path,
        config.folders,
        resolver=resolver,
        skip_files=not config.include_starter_files,
    )
    configure_pyproject(
        project_path,
        config.project_name,
        framework=config.effective_framework,
        project_type=config.project_type,
    )


def _install_dependencies(
    config: ProjectConfig,
    project_path: Path,
    on_progress: Callable[[str], None] | None = None,
) -> None:
    """Create virtual environment and install all required packages.

    Args:
        config: ProjectConfig containing python version and package settings.
        project_path: Absolute path to the project directory.
        on_progress: Optional callback invoked with a status string before each step.
    """

    def _p(msg: str) -> None:
        if on_progress:
            on_progress(msg)

    _p("Creating virtual environment...")
    setup_virtual_env(project_path, config.python_version)

    packages = _collect_packages_to_install(config)
    if packages:
        n = len(packages)
        _p(f"Installing {n} package{'s' if n != 1 else ''}...")
    install_packages(project_path, packages)


def build_project(
    config: ProjectConfig,
    on_progress: Callable[[str], None] | None = None,
) -> BuildResult:
    """Build a new UV project with all configured settings.

    Orchestrates the complete project creation pipeline:
    1. Validates project name
    2. Creates project directory
    3. Scaffolds project (UV init, git phase 1, folders, pyproject.toml)
    4. Installs dependencies (venv, framework and project type packages)
    5. Finalizes git (stage, commit, push)

    Args:
        config: ProjectConfig containing all project settings.

    Returns:
        BuildResult indicating success or failure with message.
    """
    is_valid, error_msg = validate_project_name(config.project_name)
    if not is_valid:
        return BuildResult(success=False, message=error_msg)

    project_path = config.full_path
    bare_repo_path = get_bare_repo_path(project_path) if config.git_enabled else None

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

    try:
        project_path.mkdir(parents=True)
        _create_project_scaffold(config, project_path, on_progress)
        _install_dependencies(config, project_path, on_progress)

        # Finalize git after all files and packages are installed
        if config.git_enabled and on_progress:
            on_progress("Finalizing Git...")
        finalize_git_setup(project_path, config.git_enabled)

        return BuildResult(
            success=True,
            message=f"Project Created Successfully! Built at: {project_path}",
        )

    except CalledProcessError as e:
        remove_partial_project(project_path, bare_repo_path)
        error_detail = f"Command failed: {' '.join(e.cmd)}"
        if e.stderr:
            error_detail += f"\n\nError output:\n{e.stderr}"
        return BuildResult(success=False, message=error_detail, error=e)
    except OSError as e:
        remove_partial_project(project_path, bare_repo_path)
        return BuildResult(
            success=False,
            message=f"Could not create project files: {e}",
            error=e,
        )
    except Exception as e:
        remove_partial_project(project_path, bare_repo_path)
        return BuildResult(
            success=False,
            message=f"An unexpected error occurred: {e}",
            error=e,
        )
