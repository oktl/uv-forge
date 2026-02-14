"""Input validation functions

This module provides validation logic for project names, folder names,
and paths to ensure they meet filesystem and Python package requirements.
"""

import os
import re
import keyword
from pathlib import Path

ValidationResult = tuple[bool, str]

# Compiled regex patterns for name validation
_PROJECT_NAME_CHARS = re.compile(r"^[a-zA-Z0-9_-]+$")
_PROJECT_NAME_START = re.compile(r"^[a-zA-Z_]")
_FOLDER_NAME_CHARS = re.compile(r"^[a-zA-Z0-9_.-]+$")

_RESERVED_NAMES = frozenset({".", ".."})
_MAX_NAME_LENGTH = 255


def validate_project_name(name: str) -> ValidationResult:
    """Validate project name for filesystem and Python package compatibility.

    Checks that the name meets requirements for both filesystem paths and
    Python package names, including character restrictions and keyword conflicts.

    Args:
        name: The proposed project name to validate.

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty string.
    """
    if not name:
        return False, "Project name cannot be empty."

    if len(name) > _MAX_NAME_LENGTH:
        return False, f"Project name exceeds maximum length of {_MAX_NAME_LENGTH} characters."

    # Checked separately from the start-character rule below
    # so the UI can show the specific error as the user types
    if not _PROJECT_NAME_CHARS.match(name):
        return (
            False,
            "Project name can only contain letters, numbers, hyphens, and underscores.",
        )

    # Check if it starts with a letter or underscore (Python package requirement)
    if not _PROJECT_NAME_START.match(name):
        return False, "Project name must start with a letter or underscore."

    # Check for Python keywords
    if keyword.iskeyword(name):
        return False, f"'{name}' is a Python keyword and cannot be used."

    return True, ""


def validate_folder_name(name: str) -> ValidationResult:
    """Validate folder or file name for filesystem compatibility.

    Allows dots for file extensions (e.g., config.py, .gitignore) and
    names starting with numbers or dots. Does not enforce Python package
    start-character rules since folders/files may be non-Python assets.

    Args:
        name: The proposed folder or file name to validate.

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty string.
    """
    if not name:
        return False, "Name cannot be empty."

    if len(name) > _MAX_NAME_LENGTH:
        return False, f"Name exceeds maximum length of {_MAX_NAME_LENGTH} characters."

    # Check for invalid filesystem characters (allow dots for file extensions and dotfiles)
    if not _FOLDER_NAME_CHARS.match(name):
        return (
            False,
            "Name can only contain letters, numbers, hyphens, underscores, and periods.",
        )

    # Check for reserved names (must come before any start-character checks)
    if name in _RESERVED_NAMES:
        return False, f"'{name}' is a reserved name and cannot be used."

    return True, ""


def validate_path(path: Path) -> ValidationResult:
    """Validate that a path is accessible and writable.

    This is a read-only check — it does not create or modify any directories.
    Directory creation is handled by project_builder.build_project().

    Args:
        path: Path to validate.

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty string.
    """
    try:
        if not path.exists():
            # Check that the nearest existing ancestor is a writable directory
            parent = path
            while not parent.exists():
                parent = parent.parent
            if not parent.is_dir():
                return False, f"Path '{parent}' exists but is not a directory."
            if not os.access(parent, os.W_OK):
                return False, f"Parent directory '{parent}' is not writable."
            return True, ""

        # Path exists, check if it's a directory
        if not path.is_dir():
            return False, f"Path '{path}' exists but is not a directory."

        # Path exists and is a directory, check writability
        if not os.access(path, os.W_OK):
            return False, f"Directory '{path}' is not writable."

        return True, ""
    except OSError as e:
        return False, f"Cannot access path '{path}': {e}"
