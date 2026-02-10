#!/usr/bin/env python3
"""Pytest tests for validator.py functions"""

import pytest
import tempfile
from pathlib import Path

from app.core.validator import validate_project_name, validate_folder_name, validate_path


@pytest.mark.parametrize("name,expected_valid,description", [
    ("my_project", True, "Valid name with underscore"),
    ("my-project", True, "Valid name with hyphen"),
    ("MyProject", True, "Valid name with capitals"),
    ("project123", True, "Valid name with numbers"),
    ("_private", True, "Valid name starting with underscore"),
    ("", False, "Empty name"),
    ("123project", False, "Starts with number"),
    ("-project", False, "Starts with hyphen"),
    ("my project", False, "Contains space"),
    ("my@project", False, "Contains special char"),
    ("class", False, "Python keyword"),
    ("for", False, "Python keyword"),
])
def test_validate_project_name(name, expected_valid, description):
    """Test project name validation"""
    is_valid, error_msg = validate_project_name(name)
    assert is_valid == expected_valid, f"{description}: {error_msg}"


@pytest.mark.parametrize("name,expected_valid,description", [
    ("my_folder", True, "Valid folder with underscore"),
    ("my-folder", True, "Valid folder with hyphen"),
    ("MyFolder", True, "Valid folder with capitals"),
    ("folder123", True, "Valid folder with numbers"),
    ("123folder", True, "Valid folder starting with number"),
    ("", False, "Empty name"),
    ("my folder", False, "Contains space"),
    ("my@folder", False, "Contains special char"),
])
def test_validate_folder_name(name, expected_valid, description):
    """Test folder name validation"""
    is_valid, error_msg = validate_folder_name(name)
    assert is_valid == expected_valid, f"{description}: {error_msg}"


def test_validate_path_new_folder():
    """Test validation of a new folder path that can be created"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "new_folder"
        is_valid, error_msg = validate_path(test_path)
        assert is_valid, f"Valid new path should pass: {error_msg}"


def test_validate_path_existing_directory():
    """Test validation of an existing directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir)
        is_valid, error_msg = validate_path(test_path)
        assert is_valid, f"Existing directory should be valid: {error_msg}"


def test_validate_path_file_not_directory():
    """Test that a file path (not directory) is rejected"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_file = Path(tmp.name)
        try:
            is_valid, error_msg = validate_path(tmp_file)
            assert not is_valid, "File path should be rejected"
            assert "not a" in error_msg.lower() and "directory" in error_msg.lower()
        finally:
            tmp_file.unlink()
