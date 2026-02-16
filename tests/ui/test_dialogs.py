#!/usr/bin/env python3
"""Pytest tests for dialogs.py - Project type dialog and about dialog creation"""

from unittest.mock import AsyncMock, Mock

import flet as ft
import pytest

from app.core.models import BuildSummaryConfig
from app.ui.dialogs import (
    _build_project_tree_lines,
    create_about_dialog,
    create_project_type_dialog,
)


def test_create_project_type_dialog_basic():
    """Test basic dialog creation"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection=None,
        is_dark_mode=True,
    )

    assert isinstance(dialog, ft.AlertDialog)
    assert dialog.modal == True
    assert dialog.title is not None
    assert dialog.content is not None
    assert dialog.actions is not None
    assert len(dialog.actions) == 2  # Select and Cancel buttons


def test_create_project_type_dialog_with_selection():
    """Test dialog creation with current selection"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection="django",
        is_dark_mode=True,
    )

    # Find the RadioGroup in the dialog content
    radio_group = dialog.content.content
    assert isinstance(radio_group, ft.RadioGroup)
    assert radio_group.value == "django"


def test_create_project_type_dialog_default_selection():
    """Test dialog defaults to '_none_' when no selection"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection=None,
        is_dark_mode=True,
    )

    radio_group = dialog.content.content
    assert radio_group.value == "_none_"


def test_create_project_type_dialog_dark_mode():
    """Test dialog creation in dark mode"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection=None,
        is_dark_mode=True,
    )

    assert isinstance(dialog, ft.AlertDialog)
    # Dialog should be created without errors in dark mode


def test_create_project_type_dialog_light_mode():
    """Test dialog creation in light mode"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection=None,
        is_dark_mode=False,
    )

    assert isinstance(dialog, ft.AlertDialog)
    # Dialog should be created without errors in light mode


def test_create_project_type_dialog_has_categories():
    """Test dialog contains expected project type categories"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection=None,
        is_dark_mode=True,
    )

    # Get the radio group content (Column with all controls)
    radio_group = dialog.content.content
    column = radio_group.content

    # Extract all text values from the column
    text_values = []
    for control in column.controls:
        if isinstance(control, ft.Container):
            if isinstance(control.content, ft.Text):
                text_values.append(control.content.value)
            elif isinstance(control.content, ft.Row):
                # Enhanced categories have Row with icon + text
                for item in control.content.controls:
                    if isinstance(item, ft.Text):
                        text_values.append(item.value)
            elif isinstance(control.content, ft.Radio):
                text_values.append(control.content.label)

    # Check that expected categories appear
    text_str = " ".join(text_values)
    assert "Web Frameworks" in text_str
    assert "Data Science" in text_str or "Data Science & ML" in text_str
    assert "CLI Tools" in text_str


def test_create_project_type_dialog_has_project_types():
    """Test dialog contains specific project types"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection=None,
        is_dark_mode=True,
    )

    radio_group = dialog.content.content
    column = radio_group.content

    # Extract all radio button values
    radio_values = []
    for control in column.controls:
        if isinstance(control, ft.Container) and isinstance(control.content, ft.Radio):
                radio_values.append(control.content.value)

    # Check for expected project types
    assert "django" in radio_values
    assert "fastapi" in radio_values
    assert "flask" in radio_values
    assert "data_analysis" in radio_values
    assert "cli_typer" in radio_values
    assert "scraping" in radio_values


@pytest.mark.parametrize("project_type", [
    "django",
    "fastapi",
    "flask",
    "bottle",
    "data_analysis",
    "ml_sklearn",
    "cli_click",
    "cli_typer",
    "scraping",
])
def test_create_project_type_dialog_various_selections(project_type):
    """Test dialog can be created with various project type selections"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection=project_type,
        is_dark_mode=True,
    )

    radio_group = dialog.content.content
    assert radio_group.value == project_type


def test_create_project_type_dialog_callbacks_not_none():
    """Test that callbacks are required (not None)"""
    # This test verifies the dialog can be created with valid callbacks
    select_called = []
    close_called = []

    def on_select(pt):
        select_called.append(pt)

    def on_close(e):
        close_called.append(True)

    dialog = create_project_type_dialog(
        on_select_callback=on_select,
        on_close_callback=on_close,
        current_selection=None,
        is_dark_mode=True,
    )

    assert dialog is not None
    # Note: We can't easily test callback execution without a full Flet page


def test_create_project_type_dialog_content_structure():
    """Test dialog content has correct structure"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection=None,
        is_dark_mode=True,
    )

    # Dialog should have a Container as content
    assert isinstance(dialog.content, ft.Container)

    # Container should hold a RadioGroup
    assert isinstance(dialog.content.content, ft.RadioGroup)

    # RadioGroup should have a Column as content
    radio_group = dialog.content.content
    assert isinstance(radio_group.content, ft.Column)

    # Column should have controls (categories and radios)
    column = radio_group.content
    assert len(column.controls) > 0


def test_create_project_type_dialog_actions():
    """Test dialog has correct action buttons"""
    dialog = create_project_type_dialog(
        on_select_callback=lambda x: None,
        on_close_callback=lambda x: None,
        current_selection=None,
        is_dark_mode=True,
    )

    assert len(dialog.actions) == 2

    # Check button types - Select is FilledButton, Cancel is OutlinedButton
    assert isinstance(dialog.actions[0], ft.FilledButton)  # Select button
    assert isinstance(dialog.actions[1], ft.OutlinedButton)  # Cancel button


# ========== About Dialog Tests ==========


def test_create_about_dialog_basic():
    """Test about dialog creates a valid AlertDialog."""
    page = Mock()
    page.launch_url = AsyncMock()

    dialog = create_about_dialog(
        content="# About\nTest content",
        on_close=lambda _: None,
        page=page,
        is_dark_mode=True,
    )

    assert isinstance(dialog, ft.AlertDialog)
    assert dialog.modal is True
    assert dialog.actions is not None
    assert len(dialog.actions) == 1  # Close button only


def test_create_about_dialog_light_mode():
    """Test about dialog works in light mode."""
    page = Mock()
    page.launch_url = AsyncMock()

    dialog = create_about_dialog(
        content="# About",
        on_close=lambda _: None,
        page=page,
        is_dark_mode=False,
    )

    assert isinstance(dialog, ft.AlertDialog)


def test_create_about_dialog_with_internal_link_callback():
    """Test about dialog accepts on_internal_link parameter."""
    page = Mock()
    page.launch_url = AsyncMock()
    captured = []

    dialog = create_about_dialog(
        content="# About\n[Help](app://help)",
        on_close=lambda _: None,
        page=page,
        is_dark_mode=True,
        on_internal_link=lambda path: captured.append(path),
    )

    assert isinstance(dialog, ft.AlertDialog)


def test_create_about_dialog_has_markdown_content():
    """Test about dialog wraps content in a Markdown widget."""
    page = Mock()
    page.launch_url = AsyncMock()

    dialog = create_about_dialog(
        content="# UV Project Creator\nVersion 0.1.0",
        on_close=lambda _: None,
        page=page,
        is_dark_mode=True,
    )

    # Content is Container > Column > [Markdown]
    column = dialog.content.content
    assert isinstance(column, ft.Column)
    assert len(column.controls) == 1
    assert isinstance(column.controls[0], ft.Markdown)


# ========== Project Tree Preview Tests ==========


def _make_config(**overrides) -> BuildSummaryConfig:
    """Create a BuildSummaryConfig with sensible defaults."""
    defaults = dict(
        project_name="my_project",
        project_path="/tmp",
        python_version="3.14",
        git_enabled=True,
        ui_project_enabled=False,
        framework=None,
        other_project_enabled=False,
        project_type=None,
        starter_files=True,
        folder_count=2,
        file_count=5,
        packages=[],
        folders=[
            {
                "name": "core",
                "create_init": True,
                "subfolders": [],
                "files": ["state.py", "models.py"],
            },
            {
                "name": "ui",
                "create_init": True,
                "subfolders": [],
                "files": ["components.py"],
            },
        ],
    )
    defaults.update(overrides)
    return BuildSummaryConfig(**defaults)


def test_tree_root_line():
    """Tree starts with project_name/."""
    config = _make_config()
    lines = _build_project_tree_lines(config)
    assert lines[0] == "my_project/"


def test_tree_includes_root_files_with_git():
    """Tree includes .gitignore when git is enabled."""
    config = _make_config(git_enabled=True)
    lines = _build_project_tree_lines(config)
    text = "\n".join(lines)
    assert ".gitignore" in text
    assert ".python-version" in text
    assert "README.md" in text
    assert "pyproject.toml" in text


def test_tree_excludes_gitignore_without_git():
    """Tree excludes .gitignore when git is disabled."""
    config = _make_config(git_enabled=False)
    lines = _build_project_tree_lines(config)
    text = "\n".join(lines)
    assert ".gitignore" not in text
    assert "pyproject.toml" in text


def test_tree_includes_app_dir():
    """Tree includes app/ with __init__.py and main.py."""
    config = _make_config()
    lines = _build_project_tree_lines(config)
    text = "\n".join(lines)
    assert "app/" in text
    assert "__init__.py" in text
    assert "main.py" in text


def test_tree_includes_template_folders():
    """Tree includes template folders inside app/."""
    config = _make_config()
    lines = _build_project_tree_lines(config)
    text = "\n".join(lines)
    assert "core/" in text
    assert "state.py" in text
    assert "models.py" in text
    assert "ui/" in text
    assert "components.py" in text


def test_tree_create_init_true_shows_init_py():
    """Folders with create_init=True show __init__.py."""
    config = _make_config(
        folders=[{"name": "core", "create_init": True, "subfolders": [], "files": []}]
    )
    lines = _build_project_tree_lines(config)
    # Find __init__.py under core/
    core_idx = next(i for i, l in enumerate(lines) if "core/" in l)
    assert "__init__.py" in lines[core_idx + 1]


def test_tree_create_init_false_no_init_py():
    """Folders with create_init=False don't show __init__.py."""
    config = _make_config(
        folders=[
            {
                "name": "assets",
                "create_init": False,
                "subfolders": [],
                "files": ["logo.png"],
            }
        ]
    )
    lines = _build_project_tree_lines(config)
    # Find the line after assets/
    assets_idx = next(i for i, l in enumerate(lines) if "assets/" in l)
    assert "logo.png" in lines[assets_idx + 1]
    # No __init__.py between assets/ and logo.png
    assert "__init__" not in lines[assets_idx + 1]


def test_tree_create_init_false_inherited_by_string_subfolders():
    """String subfolders inherit create_init=False from parent — no __init__.py."""
    from app.core.template_merger import normalize_folder

    raw_folder = {
        "name": "assets",
        "create_init": False,
        "subfolders": ["icons", "images"],
        "files": [],
    }
    config = _make_config(folders=[normalize_folder(raw_folder)])
    lines = _build_project_tree_lines(config)
    text = "\n".join(lines)
    # icons/ and images/ should appear but not contain __init__.py
    assert "icons/" in text
    assert "images/" in text
    # Count __init__.py occurrences — only app/ should have one
    init_count = text.count("__init__.py")
    assert init_count == 1  # Only app/__init__.py


def test_tree_root_level_folders():
    """Root-level folders appear at project root, not inside app/."""
    config = _make_config(
        folders=[
            {
                "name": "tests",
                "root_level": True,
                "create_init": True,
                "subfolders": [],
                "files": [],
            },
            {
                "name": "core",
                "create_init": True,
                "subfolders": [],
                "files": [],
            },
        ]
    )
    lines = _build_project_tree_lines(config)
    text = "\n".join(lines)
    # tests/ should be at root level (same indent as app/)
    # Find the app/ line and tests/ line — they should have the same prefix depth
    app_line = next(l for l in lines if "app/" in l)
    tests_line = next(l for l in lines if "tests/" in l)
    app_prefix = len(app_line) - len(app_line.lstrip("│├└── "))
    tests_prefix = len(tests_line) - len(tests_line.lstrip("│├└── "))
    assert app_prefix == tests_prefix


def test_tree_nested_subfolders():
    """Tree handles nested subfolders correctly."""
    config = _make_config(
        folders=[
            {
                "name": "core",
                "create_init": True,
                "subfolders": [
                    {
                        "name": "utils",
                        "create_init": True,
                        "subfolders": [],
                        "files": ["helpers.py"],
                    }
                ],
                "files": ["state.py"],
            }
        ]
    )
    lines = _build_project_tree_lines(config)
    text = "\n".join(lines)
    assert "core/" in text
    assert "utils/" in text
    assert "helpers.py" in text
    assert "state.py" in text


def test_tree_empty_folders():
    """Tree works with no template folders."""
    config = _make_config(folders=[])
    lines = _build_project_tree_lines(config)
    text = "\n".join(lines)
    assert "my_project/" in text
    assert "app/" in text
    assert "main.py" in text


def test_tree_box_drawing_characters():
    """Tree uses Unicode box-drawing characters."""
    config = _make_config()
    lines = _build_project_tree_lines(config)
    all_text = "\n".join(lines)
    assert "├── " in all_text or "└── " in all_text
