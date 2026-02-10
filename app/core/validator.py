"""Input validation functions

This module provides validation logic for project names, folder names,
and paths to ensure they meet filesystem and Python package requirements.
"""

import re
import keyword
from pathlib import Path


def validate_project_name(name: str) -> tuple[bool, str]:
    """Validate project name for filesystem and Python package compatibility.

    Checks that the name meet requirements for both filesystem paths and
    Python package names, including character restrictions and keyword conflicts.

    Args:
        name: The proposed project name to validate.

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty string.
    """
    if not name:
        return False, "Project name cannot be empty."

    # Check for invalid filesystem characters
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        return (
            False,
            "Project name can only contain letters, numbers, hyphens, and underscores.",
        )

    # Check if it starts with a letter or underscore (Python package requirement)
    if not re.match(r"^[a-zA-Z_]", name):
        return False, "Project name must start with a letter or underscore."

    # Check for Python keywords
    if keyword.iskeyword(name):
        return False, f"'{name}' is a Python keyword and cannot be used."

    return True, ""


def validate_folder_name(name: str) -> tuple[bool, str]:
    """Validate folder or file name for filesystem compatibility.

    Allows dots for file extensions (e.g., config.py, requirements.txt).
    Requires starting with a letter or underscore for Python package compatibility.

    Args:
        name: The proposed folder or file name to validate.

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty string.
    """
    if not name:
        return False, "Name cannot be empty."

    # Check for invalid filesystem characters (allow dots for file extensions)
    if not re.match(r"^[a-zA-Z0-9_.-]+$", name):
        return (
            False,
            "Name can only contain letters, numbers, hyphens, underscores, and periods.",
        )

    # Check if it starts with a letter or underscore (Python package requirement)
    if not re.match(r"^[a-zA-Z_]", name):
        return False, "Name must start with a letter or underscore."

    # Check for reserved names
    if name in (".", "..", "~"):
        return False, f"'{name}' is a reserved name and cannot be used."

    return True, ""


def validate_path(path: Path) -> tuple[bool, str]:
    """Validate that a path is accessible and writeable.

    Args:
        path: Path to validate.

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty string.
    """
    try:
        # Check if path exists or can be created
        if not path.exists():
            # Try to create it temporarily to check permissions
            path.mkdir(parents=True, exist_ok=True)
            # If we created it for testing, we can leave it
            return True, ""

        # Path exists, check if it's a directory
        if not path.is_dir():
            return False, f"Path '{path}' exists but is not a directory."

        return True, ""
    except (OSError, PermissionError) as e:
        return False, f"Cannot access path '{path}': {e}"
