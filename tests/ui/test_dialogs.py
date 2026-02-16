#!/usr/bin/env python3
"""Pytest tests for dialogs.py - Project type dialog creation"""

import flet as ft
import pytest

from app.ui.dialogs import create_project_type_dialog


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
