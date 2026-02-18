"""Handlers for project path and name input fields."""

import subprocess
import sys
from pathlib import Path

import flet as ft

from app.core.pypi_checker import check_pypi_availability, normalize_pypi_name
from app.core.validator import validate_path, validate_project_name
from app.ui.ui_config import UIConfig


class InputHandlersMixin:
    """Mixin for path and name input event handlers.

    Expects HandlerBase helpers available via self.
    """

    async def on_copy_path(self, _: ft.ControlEvent) -> None:
        """Copy the full project path (base + name) to the system clipboard."""
        full_path = str(Path(self.state.project_path) / self.state.project_name)
        _clipboard_errors = (FileNotFoundError, subprocess.CalledProcessError)
        try:
            if sys.platform == "darwin":
                subprocess.run(["pbcopy"], input=full_path.encode(), check=True)
            elif sys.platform == "win32":
                subprocess.run(["clip"], input=full_path.encode(), check=True)
            else:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=full_path.encode(),
                    check=True,
                )
            self._set_status(f"Copied: {full_path}", "info", update=True)
        except _clipboard_errors:
            self._set_status("Could not copy to clipboard.", "error", update=True)

    async def on_browse_click(self, _: ft.ControlEvent) -> None:
        """Handle the Browse button click.

        Opens a directory picker dialog and updates the project path.
        """
        result = await ft.FilePicker().get_directory_path(
            dialog_title="Select Project Location"
        )

        if result:
            self.state.project_path = result
            self.controls.project_path_input.value = result
            path_valid, path_error = validate_path(Path(result))
            self.state.path_valid = path_valid
            self._set_validation_icon(self.controls.project_path_input, path_valid)
            if path_valid:
                self._set_warning("", update=False)
                self._set_status(f"Path set to: {result}", "info")
            else:
                self._set_warning(path_error, update=True)
            self._update_build_button_state()
            self.page.update()

    async def on_path_change(self, e: ft.ControlEvent) -> None:
        """Handle project path input changes.

        Validates the path and updates state accordingly.
        """
        path_str = e.control.value.strip() if e.control.value else ""
        self.state.project_path = path_str

        if not path_str:
            self.state.path_valid = False
            self._set_validation_icon(self.controls.project_path_input, None)
            self._update_build_button_state()
            self._set_warning("Project path cannot be empty.", update=True)
            return

        path = Path(path_str)
        is_valid, error_msg = validate_path(path)
        self.state.path_valid = is_valid
        self._set_validation_icon(self.controls.project_path_input, is_valid)
        self._update_build_button_state()

        if is_valid:
            self._set_warning("", update=False)
            self._set_status("", "info", update=False)
        else:
            self._set_warning(error_msg, update=False)
        self._update_path_preview()
        self.page.update()

    async def on_project_name_change(self, e: ft.ControlEvent) -> None:
        """Handle project name input changes.

        Validates the project name and updates state accordingly.
        """
        name = e.control.value if e.control.value else ""
        self.state.project_name = name

        # Clear stale PyPI status on every keystroke
        self.controls.pypi_status_text.value = ""

        if not name:
            self.state.name_valid = False
            self._set_validation_icon(self.controls.project_name_input, None)
            self.controls.check_pypi_button.disabled = True
            self._update_build_button_state()
            self._set_warning("Enter a project name.", update=False)
            self._update_path_preview()
            self.page.title = "UV Forge"
            self.page.update()
            return

        is_valid, error_msg = validate_project_name(name)
        self.state.name_valid = is_valid

        if is_valid:
            full_path = Path(self.state.project_path) / name
            if full_path.exists():
                self.state.name_valid = False
                self._set_validation_icon(self.controls.project_name_input, False)
                self._set_warning(
                    f"Project '{name}' already exists at this location.",
                    update=False,
                )
            else:
                self._set_validation_icon(self.controls.project_name_input, True)
                self._set_warning("", update=False)
        else:
            self._set_validation_icon(self.controls.project_name_input, False)
            self._set_warning(error_msg, update=False)

        self.controls.check_pypi_button.disabled = not self.state.name_valid
        self._update_build_button_state()
        self._update_path_preview()
        self.page.title = f"UV Forge — {name}" if self.state.name_valid else "UV Forge"
        self.page.update()

    async def on_check_pypi(self, _: ft.ControlEvent) -> None:
        """Check PyPI availability for the current project name."""
        name = self.state.project_name
        if not name or not self.state.name_valid:
            return

        # Show checking state
        self.controls.pypi_status_text.value = "Checking PyPI..."
        self.controls.pypi_status_text.color = UIConfig.COLOR_INFO
        self.controls.check_pypi_button.disabled = True
        self.page.update()

        result = await check_pypi_availability(name)

        normalized = normalize_pypi_name(name)
        if result is True:
            self.controls.pypi_status_text.value = (
                f"✓ '{normalized}' is available on PyPI"
            )
            self.controls.pypi_status_text.color = UIConfig.COLOR_SUCCESS
        elif result is False:
            self.controls.pypi_status_text.value = f"✗ '{normalized}' is taken on PyPI"
            self.controls.pypi_status_text.color = UIConfig.COLOR_ERROR
        else:
            self.controls.pypi_status_text.value = "⚠ Could not check PyPI (offline?)"
            self.controls.pypi_status_text.color = UIConfig.COLOR_WARNING

        self.controls.check_pypi_button.disabled = False
        self.page.update()
