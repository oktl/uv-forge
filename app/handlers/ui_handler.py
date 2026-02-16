"""Event handlers for the UV Project Creator.

This module composes handler mixins into a single Handlers class and
provides the attach_handlers() function that wires all UI controls.
"""

import asyncio

import flet as ft

from app.core.state import AppState
from app.core.template_loader import TemplateLoader
from app.ui.components import Controls

from app.handlers.handler_base import HandlerBase
from app.handlers.input_handlers import InputHandlersMixin
from app.handlers.option_handlers import OptionHandlersMixin
from app.handlers.folder_handlers import FolderHandlersMixin
from app.handlers.package_handlers import PackageHandlersMixin
from app.handlers.build_handlers import BuildHandlersMixin
from app.handlers.feature_handlers import FeatureHandlersMixin


def wrap_async(coro_func):
    """Wrap an async coroutine for Flet's sync callback system."""

    def wrapper(e):
        asyncio.create_task(coro_func(e))

    return wrapper


def _get_controls(page: ft.Page) -> Controls:
    """Retrieve the Controls instance from the page."""
    return page.controls_ref


class Handlers(
    HandlerBase,
    InputHandlersMixin,
    OptionHandlersMixin,
    FolderHandlersMixin,
    PackageHandlersMixin,
    BuildHandlersMixin,
    FeatureHandlersMixin,
):
    """Event handlers for UI controls.

    Composes all handler mixins and provides shared state access.
    """

    def __init__(self, page: ft.Page, controls: Controls, state: AppState) -> None:
        self.page = page
        self.controls = controls
        self.state = state
        self.template_loader = TemplateLoader()


def attach_handlers(page: ft.Page, state: AppState) -> None:
    """Attach event handlers to UI controls.

    Args:
        page: The Flet page containing the UI controls.
        state: The application state instance for handlers to access.
    """
    controls = _get_controls(page)
    handlers = Handlers(page, controls, state)

    # Load default folder template and package list on startup
    handlers._load_framework_template(None)
    handlers._update_package_display()

    # Set initial UI state (path icon if default path exists, button disabled)
    if state.path_valid:
        handlers._set_validation_icon(controls.project_path_input, True)
    handlers._update_build_button_state()

    # Apply green styling to any checkboxes that start in a checked state
    for checkbox in (
        controls.create_git_checkbox,
        controls.include_starter_files_checkbox,
    ):
        handlers._style_selected_checkbox(checkbox)

    # --- Path & Name Handlers ---
    controls.copy_path_button.on_click = wrap_async(handlers.on_copy_path)
    controls.browse_button.on_click = wrap_async(handlers.on_browse_click)
    controls.project_path_input.on_change = wrap_async(handlers.on_path_change)
    controls.project_name_input.on_change = wrap_async(handlers.on_project_name_change)

    # --- Options Handlers ---
    controls.python_version_dropdown.on_select = wrap_async(
        handlers.on_python_version_change
    )
    controls.create_git_checkbox.on_change = wrap_async(handlers.on_git_toggle)
    controls.include_starter_files_checkbox.on_change = wrap_async(
        handlers.on_boilerplate_toggle
    )
    controls.ui_project_checkbox.on_change = wrap_async(
        handlers.on_ui_project_toggle
    )
    controls.other_projects_checkbox.on_change = wrap_async(
        handlers.on_other_project_toggle
    )

    # --- Folder Management Handlers ---
    controls.add_folder_button.on_click = wrap_async(handlers.on_add_folder)
    controls.remove_folder_button.on_click = wrap_async(handlers.on_remove_folder)
    controls.auto_save_folder_changes.on_change = wrap_async(
        handlers.on_auto_save_toggle
    )

    # --- Package Management Handlers ---
    controls.add_package_button.on_click = wrap_async(handlers.on_add_package)
    controls.remove_package_button.on_click = wrap_async(handlers.on_remove_package)
    controls.clear_packages_button.on_click = wrap_async(handlers.on_clear_packages)

    # --- Main Action Handlers ---
    controls.build_project_button.on_click = wrap_async(handlers.on_build_project)
    controls.reset_button.on_click = wrap_async(handlers.on_reset)
    controls.exit_button.on_click = wrap_async(handlers.on_exit)

    # --- UI Feature Handlers ---
    controls.git_cheat_sheet_button.on_click = wrap_async(
        handlers.on_git_cheat_sheet_click
    )
    controls.help_button.on_click = wrap_async(handlers.on_help_click)
    controls.theme_toggle_button.on_click = wrap_async(handlers.on_theme_toggle)

    # --- Keyboard Shortcuts ---
    page.on_keyboard_event = wrap_async(handlers.on_keyboard_event)

    # Update page to register all handlers
    page.update()
