#!/usr/bin/env python3
"""Pytest tests for state.py - AppState dataclass"""

import pytest
from app.core.state import AppState
from app.utils.constants import DEFAULT_PROJECT_ROOT, DEFAULT_PYTHON_VERSION


def test_appstate_initialization():
    """Test AppState initializes with correct defaults"""
    state = AppState()

    assert state.project_path == DEFAULT_PROJECT_ROOT
    assert state.project_name == ""
    assert state.selected_python_version == DEFAULT_PYTHON_VERSION
    assert state.initialize_git == True
    assert state.create_ui_project == False
    assert state.selected_framework is None
    assert state.create_other_project == False
    assert state.selected_project_type is None
    assert state.folders == []
    assert state.auto_save_folders == False
    assert state.is_dark_mode == True
    assert state.path_valid == True
    assert state.name_valid == False  # Empty name is invalid


def test_appstate_custom_initialization():
    """Test AppState with custom values"""
    state = AppState(
        project_path="/custom/path",
        project_name="my_project",
        selected_python_version="3.12",
        initialize_git=True,
        create_ui_project=True,
        selected_framework="flet",
        create_other_project=True,
        selected_project_type="django",
        folders=["core", "ui", "utils"],
        auto_save_folders=True,
        is_dark_mode=False,
        path_valid=False,
        name_valid=True,
    )

    assert state.project_path == "/custom/path"
    assert state.project_name == "my_project"
    assert state.selected_python_version == "3.12"
    assert state.initialize_git == True
    assert state.create_ui_project == True
    assert state.selected_framework == "flet"
    assert state.create_other_project == True
    assert state.selected_project_type == "django"
    assert state.folders == ["core", "ui", "utils"]
    assert state.auto_save_folders == True
    assert state.is_dark_mode == False
    assert state.path_valid == False
    assert state.name_valid == True


def test_appstate_reset():
    """Test AppState.reset() method resets all fields except is_dark_mode"""
    # Create state with custom values
    state = AppState(
        project_path="/custom/path",
        project_name="my_project",
        selected_python_version="3.12",
        initialize_git=True,
        create_ui_project=True,
        selected_framework="flet",
        create_other_project=True,
        selected_project_type="django",
        folders=["core", "ui", "utils"],
        auto_save_folders=True,
        is_dark_mode=False,  # Set to False to test it's preserved
        path_valid=False,
        name_valid=True,
    )

    # Reset state
    state.reset()

    # Test reset values (all should be back to defaults except is_dark_mode)
    assert state.project_path == DEFAULT_PROJECT_ROOT
    assert state.project_name == ""
    assert state.selected_python_version == DEFAULT_PYTHON_VERSION
    assert state.initialize_git == True
    assert state.create_ui_project == False
    assert state.selected_framework is None
    assert state.create_other_project == False
    assert state.selected_project_type is None
    assert state.folders == []
    assert state.auto_save_folders == False
    assert state.is_dark_mode == False  # PRESERVED (was False, still False)
    assert state.path_valid == True
    assert state.name_valid == False


def test_appstate_reset_preserves_dark_mode_true():
    """Test that reset() preserves is_dark_mode=True"""
    state = AppState(is_dark_mode=True, project_name="test")
    state.reset()
    assert state.is_dark_mode == True


def test_appstate_reset_preserves_dark_mode_false():
    """Test that reset() preserves is_dark_mode=False"""
    state = AppState(is_dark_mode=False, project_name="test")
    state.reset()
    assert state.is_dark_mode == False


@pytest.mark.parametrize("field,value", [
    ("project_path", "/new/path"),
    ("project_name", "new_name"),
    ("selected_python_version", "3.11"),
    ("initialize_git", True),
    ("create_ui_project", True),
    ("selected_framework", "pyqt6"),
    ("create_other_project", True),
    ("selected_project_type", "fastapi"),
    ("auto_save_folders", True),
    ("is_dark_mode", False),
    ("path_valid", False),
    ("name_valid", True),
])
def test_appstate_field_mutability(field, value):
    """Test that AppState fields are mutable"""
    state = AppState()
    setattr(state, field, value)
    assert getattr(state, field) == value


def test_appstate_folders_mutability():
    """Test that folders list is mutable"""
    state = AppState()
    state.folders = ["new", "folders"]
    assert state.folders == ["new", "folders"]


def test_appstate_folders_independence():
    """Test that folders list is independent across instances"""
    state1 = AppState()
    state2 = AppState()

    # Modify folders in state1
    state1.folders.append("test_folder")

    # Verify state2 folders is not affected
    assert "test_folder" not in state2.folders
    # Verify state1 has the folder
    assert "test_folder" in state1.folders


# ========== Project Type Tests ==========


def test_appstate_project_type_defaults():
    """Test project type fields initialize with correct defaults"""
    state = AppState()
    assert state.create_other_project == False
    assert state.selected_project_type is None


def test_appstate_create_other_project_mutability():
    """Test create_other_project field is mutable"""
    state = AppState()
    assert state.create_other_project == False

    state.create_other_project = True
    assert state.create_other_project == True

    state.create_other_project = False
    assert state.create_other_project == False


def test_appstate_selected_project_type_mutability():
    """Test selected_project_type field is mutable"""
    state = AppState()
    assert state.selected_project_type is None

    state.selected_project_type = "django"
    assert state.selected_project_type == "django"

    state.selected_project_type = "fastapi"
    assert state.selected_project_type == "fastapi"

    state.selected_project_type = None
    assert state.selected_project_type is None


@pytest.mark.parametrize("project_type", [
    "django",
    "fastapi",
    "flask",
    "data_analysis",
    "cli_typer",
    "scraping",
    "ml_sklearn",
    "api_graphql",
])
def test_appstate_various_project_types(project_type):
    """Test AppState can store various project type values"""
    state = AppState(selected_project_type=project_type)
    assert state.selected_project_type == project_type


def test_appstate_mutual_exclusion_concept():
    """Test that both checkboxes can be tracked independently in state"""
    # Note: Mutual exclusion is enforced in event handlers, not state
    state = AppState()

    # Can set UI project
    state.create_ui_project = True
    state.selected_framework = "flet"
    assert state.create_ui_project == True
    assert state.selected_framework == "flet"

    # State allows both to be set (handlers enforce mutual exclusion)
    state.create_other_project = True
    state.selected_project_type = "django"
    assert state.create_other_project == True
    assert state.selected_project_type == "django"


def test_appstate_reset_clears_project_type():
    """Test reset() clears project type fields"""
    state = AppState(
        create_other_project=True,
        selected_project_type="fastapi"
    )

    assert state.create_other_project == True
    assert state.selected_project_type == "fastapi"

    state.reset()

    assert state.create_other_project == False
    assert state.selected_project_type is None
