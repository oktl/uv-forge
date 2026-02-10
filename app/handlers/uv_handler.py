"""UV package manager operations.

This module handles all interactions with the uv package manager,
including project initialization, virtual environment creation, and
package installation.
"""

import shutil
import subprocess
from pathlib import Path


def get_uv_path() -> str:
    """Get the full path to the uv executable.

    Returns:
        Full path to uv executable.

    Raises:
        FileNotFoundError: If uv cannot be found.
    """
    # Try to find uv in PATH
    uv_path = shutil.which("uv")

    # If not in PATH, check common installation locations
    if uv_path is None:
        import platform

        is_windows = platform.system() == "Windows"
        uv_name = "uv.exe" if is_windows else "uv"

        common_paths = [
            Path.home() / ".local" / "bin" / uv_name,
            Path.home() / ".cargo" / "bin" / uv_name,
        ]

        # Add Unix-specific paths
        if not is_windows:
            common_paths.append(Path("/usr/local/bin/uv"))

        for path in common_paths:
            if path.exists():
                uv_path = str(path)
                break

    if uv_path is None:
        raise FileNotFoundError(
            "Could not find 'uv' executable. Please ensure uv is installed."
        )

    return uv_path


def run_uv_init(project_path: Path, python_version: str) -> None:
    """Initialize a new UV project with specified Python version.

    Runs 'uv init --python <version> .' in the project directory.

    Args:
        project_path: Path to the project directory.
        python_version: Python version string (e.g., "3.14").

    Raises:
        subprocess.CalledProcessError: If uv init command fails.
    """
    uv_path = get_uv_path()
    subprocess.run(
        [uv_path, "init", "--python", python_version, "."],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=True,
    )


def setup_virtual_env(project_path: Path, python_version: str) -> None:
    """Create virtual environment and sync dependencies.

    Runs 'uv venv --python <version>' followed by 'uv sync' to create
    and populate the virtual environment.

    Args:
        project_path: Path to the project directory.
        python_version: Python version string (e.g., "3.14").

    Raises:
        subprocess.CalledProcessError: If uv commands fail.
    """
    uv_path = get_uv_path()
    subprocess.run(
        [uv_path, "venv", "--python", python_version],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        [uv_path, "sync"],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=True,
    )


def install_package(project_path: Path, package_name: str) -> None:
    """Install a package using uv add.

    Args:
        project_path: Path to the project directory.
        package_name: Name of the package to install.

    Raises:
        subprocess.CalledProcessError: If uv add command fails.
    """
    uv_path = get_uv_path()
    subprocess.run(
        [uv_path, "add", package_name],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=True,
    )


def _resolve_entry_point(
    framework: str | None = None,
    project_type: str | None = None,
) -> str | None:
    """Resolve the entry point for a project based on framework and project type.

    Priority: framework > project_type > default.
    Returns None when the project type/framework has its own runner
    (e.g., Django, FastAPI, Streamlit).

    Args:
        framework: UI framework name, or None.
        project_type: Project type name, or None.

    Returns:
        Entry point string like "app.main:main", or None if no scripts section needed.
    """
    from app.utils.constants import (
        DEFAULT_ENTRY_POINT,
        FRAMEWORK_ENTRY_POINT_MAP,
        PROJECT_TYPE_ENTRY_POINT_MAP,
    )

    if framework is not None:
        return FRAMEWORK_ENTRY_POINT_MAP.get(framework, DEFAULT_ENTRY_POINT)
    if project_type is not None:
        return PROJECT_TYPE_ENTRY_POINT_MAP.get(project_type, DEFAULT_ENTRY_POINT)
    return DEFAULT_ENTRY_POINT


def configure_pyproject(
    project_path: Path,
    project_name: str,
    framework: str | None = None,
    project_type: str | None = None,
) -> None:
    """Update pyproject.toml with package and entry point configuration.

    Appends hatch build configuration and, when appropriate, a project
    scripts entry point to the existing pyproject.toml file.

    Args:
        project_path: Path to the project directory.
        project_name: Name of the project for the entry point script.
        framework: UI framework name, or None.
        project_type: Project type name, or None.
    """
    entry_point = _resolve_entry_point(framework, project_type)

    config = '\n[tool.hatch.build.targets.wheel]\npackages = ["app"]\n'
    if entry_point is not None:
        config += f'\n[project.scripts]\n{project_name} = "{entry_point}"\n'

    with open(project_path / "pyproject.toml", "a") as f:
        f.write(config)
