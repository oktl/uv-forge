#!/usr/bin/env python3
"""Pytest tests for models.py"""

import pytest
from pathlib import Path

from app.core.models import FolderSpec, ProjectConfig, BuildResult


# FolderSpec Tests

def test_folder_spec_basic_creation():
    """Test basic FolderSpec creation with defaults"""
    folder = FolderSpec(name="test_folder")
    assert folder.name == "test_folder"
    assert folder.create_init == True
    assert folder.root_level == False


def test_folder_spec_all_parameters():
    """Test FolderSpec with all parameters"""
    folder = FolderSpec(
        name="custom",
        create_init=False,
        root_level=True,
        subfolders=["sub1", "sub2"],
        files=["file1.py", "file2.py"]
    )
    assert folder.name == "custom"
    assert folder.create_init == False
    assert folder.root_level == True
    assert len(folder.subfolders) == 2
    assert len(folder.files) == 2


def test_folder_spec_from_dict():
    """Test FolderSpec._from_dict()"""
    data = {
        "name": "models",
        "create_init": True,
        "root_level": False,
        "files": ["__init__.py", "user.py"]
    }
    folder = FolderSpec._from_dict(data)
    assert folder.name == "models"
    assert folder.create_init == True
    assert len(folder.files) == 2


def test_folder_spec_from_dict_nested_subfolders():
    """Test FolderSpec._from_dict() with nested subfolders"""
    data = {
        "name": "app",
        "create_init": True,
        "subfolders": [
            {"name": "core", "create_init": True},
            {"name": "utils", "create_init": False}
        ]
    }
    folder = FolderSpec._from_dict(data)
    assert folder.name == "app"
    assert len(folder.subfolders) == 2
    assert isinstance(folder.subfolders[0], FolderSpec)
    assert folder.subfolders[0].name == "core"
    assert folder.subfolders[1].name == "utils"
    assert folder.subfolders[1].create_init == False


def test_folder_spec_to_dict():
    """Test FolderSpec.to_dict()"""
    folder = FolderSpec(
        name="handlers",
        create_init=False,
        root_level=True,
        files=["git_handler.py"]
    )
    result = folder.to_dict()
    assert isinstance(result, dict)
    assert result["name"] == "handlers"
    assert result["create_init"] == False
    assert result["root_level"] == True
    assert len(result["files"]) == 1


def test_folder_spec_to_dict_nested():
    """Test FolderSpec.to_dict() with nested subfolders"""
    nested = FolderSpec(name="nested", create_init=True)
    folder = FolderSpec(name="parent", subfolders=[nested, "simple_string"])
    result = folder.to_dict()
    assert isinstance(result["subfolders"], list)
    assert isinstance(result["subfolders"][0], dict)
    assert result["subfolders"][0]["name"] == "nested"
    assert result["subfolders"][1] == "simple_string"


# ProjectConfig Tests

def test_project_config_basic_creation():
    """Test basic ProjectConfig creation"""
    config = ProjectConfig(
        project_name="my_project",
        project_path=Path("/tmp"),
        python_version="3.14",
        git_enabled=True,
        ui_project_enabled=False,
        framework="",
    )
    assert config.project_name == "my_project"
    assert config.project_path == Path("/tmp")
    assert config.python_version == "3.14"
    assert config.git_enabled == True


def test_project_config_full_path():
    """Test ProjectConfig.full_path property"""
    config = ProjectConfig(
        project_name="test_app",
        project_path=Path("/home/user/projects"),
        python_version="3.14",
        git_enabled=True,
        ui_project_enabled=True,
        framework="flet",
    )
    full_path = config.full_path
    expected = Path("/home/user/projects/test_app")
    assert full_path == expected


def test_project_config_mixed_folder_types():
    """Test ProjectConfig with mixed folder types"""
    folder_spec = FolderSpec(name="models")
    config = ProjectConfig(
        project_name="test",
        project_path=Path("/tmp"),
        python_version="3.14",
        git_enabled=False,
        ui_project_enabled=False,
        framework="",
        folders=["simple", {"name": "dict_folder"}, folder_spec]
    )
    assert len(config.folders) == 3
    assert isinstance(config.folders[0], str)
    assert isinstance(config.folders[1], dict)
    assert isinstance(config.folders[2], FolderSpec)


# BuildResult Tests

def test_build_result_success():
    """Test BuildResult success"""
    result = BuildResult(success=True, message="Project created successfully")
    assert result.success == True
    assert result.message
    assert result.error is None


def test_build_result_failure_with_exception():
    """Test BuildResult failure with exception"""
    test_exception = ValueError("Test error")
    result = BuildResult(
        success=False,
        message="Build failed",
        error=test_exception
    )
    assert result.success == False
    assert result.message == "Build failed"
    assert isinstance(result.error, ValueError)


def test_build_result_failure_without_exception():
    """Test BuildResult failure without exception"""
    result = BuildResult(success=False, message="Validation failed")
    assert result.success == False
    assert result.error is None
