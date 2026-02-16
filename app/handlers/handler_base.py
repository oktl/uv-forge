"""Shared UI helper methods used across all handler mixins."""

from pathlib import Path

import flet as ft

from app.core.validator import validate_path, validate_project_name
from app.ui.ui_config import UIConfig


class HandlerBase:
    """Mixin providing shared helper methods for UI handlers.

    Expects self.page, self.controls, and self.state to be set
    by the composing Handlers class.
    """

    @staticmethod
    def _style_selected_checkbox(checkbox: ft.Checkbox) -> None:
        """Set checkbox label green when checked, default when unchecked."""
        checkbox.label_style = (
            ft.TextStyle(color=UIConfig.COLOR_CHECKBOX_ACTIVE) if checkbox.value else None
        )

    @staticmethod
    def _set_validation_icon(field: ft.TextField, is_valid: bool | None) -> None:
        """Set a validation icon on a text field.

        Args:
            field: The TextField to set the icon on.
            is_valid: True for green check, False for red X, None to clear.
        """
        if is_valid is None:
            field.suffix = None
        elif is_valid:
            field.suffix = ft.Icon(ft.Icons.CHECK_CIRCLE, color=UIConfig.COLOR_VALIDATION_OK)
        else:
            field.suffix = ft.Icon(ft.Icons.CANCEL, color=UIConfig.COLOR_VALIDATION_ERROR)

    def _update_build_button_state(self) -> None:
        """Enable/disable build button and copy-path button based on validation state."""
        is_ready = self.state.path_valid and self.state.name_valid
        btn = self.controls.build_project_button
        btn.disabled = not is_ready
        btn.opacity = 1.0 if is_ready else 0.5
        if is_ready:
            btn.tooltip = "Build project\n\n⌘Enter / Ctrl+Enter"
        else:
            reasons = []
            if not self.state.path_valid:
                path_val = self.controls.project_path_input.value or ""
                reasons.append(
                    "Project path is required"
                    if not path_val
                    else "Project path is invalid or does not exist"
                )
            if not self.state.name_valid:
                name_val = self.controls.project_name_input.value or ""
                reasons.append(
                    "Project name is required"
                    if not name_val
                    else "Project name is invalid — no spaces or special characters"
                )
            reasons.append("\n⌘Enter / Ctrl+Enter")
            btn.tooltip = "\n".join(reasons)

        copy_btn = self.controls.copy_path_button
        copy_btn.disabled = not is_ready
        copy_btn.opacity = 1.0 if is_ready else 0.4
        if is_ready:
            full_path = str(Path(self.state.project_path) / self.state.project_name)
            copy_btn.tooltip = f"Copy to clipboard:\n{full_path}"
        else:
            copy_btn.tooltip = "Copy full project path to clipboard"

    def _show_snackbar(self, message: str, is_error: bool = False) -> None:
        """Show an auto-dismissing snackbar notification.

        Args:
            message: Message to display.
            is_error: True for red background, False for green.
        """
        icon = ft.Icons.ERROR if is_error else ft.Icons.CHECK_CIRCLE
        snackbar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(icon, color=ft.Colors.WHITE, size=18),
                    ft.Text(message, color=ft.Colors.WHITE),
                ],
                spacing=8,
            ),
            bgcolor=UIConfig.COLOR_ERROR if is_error else UIConfig.COLOR_SUCCESS,
        )
        self.page.show_dialog(snackbar)

    def _set_warning(self, message: str, update: bool = False) -> None:
        """Update warning text message and color.

        Args:
            message: Warning message to display.
            update: Whether to call page.update() after setting.
        """
        self.controls.warning_banner.value = message
        if update:
            self.page.update()

    def _set_status(
        self, message: str, status_type: str = "info", update: bool = False
    ) -> None:
        """Update status text message, color, and icon.

        Args:
            message: Status message to display.
            status_type: One of "info", "success", or "error".
            update: Whether to call page.update() after setting.
        """
        type_styles = {
            "info":    (UIConfig.COLOR_INFO,    ft.Icons.INFO_OUTLINE),
            "success": (UIConfig.COLOR_SUCCESS, ft.Icons.CHECK_CIRCLE),
            "error":   (UIConfig.COLOR_ERROR,   ft.Icons.ERROR_OUTLINE),
        }
        color, icon = type_styles.get(status_type, type_styles["info"])
        self.controls.status_text.value = message
        self.controls.status_text.color = color
        self.controls.status_icon.name = icon
        self.controls.status_icon.color = color
        self.controls.status_icon.visible = bool(message)
        if update:
            self.page.update()

    def _update_path_preview(self) -> None:
        """Update the resolved path preview below the project name field."""
        path = self.controls.project_path_input.value or ""
        name = self.controls.project_name_input.value or ""
        if path and name and self.state.path_valid and self.state.name_valid:
            self.controls.path_preview_text.value = f"→ {Path(path) / name}"
        else:
            self.controls.path_preview_text.value = "\u00a0"

    def _validate_inputs(self) -> bool:
        """Validate all required inputs before building.

        Returns:
            True if all inputs are valid, False otherwise.
        """
        path = Path(self.state.project_path)
        path_valid, path_error = validate_path(path)
        if not path_valid:
            self._set_warning(path_error, update=True)
            return False

        name_valid, name_error = validate_project_name(self.state.project_name)
        if not name_valid:
            self._set_warning(name_error, update=True)
            return False

        full_path = path / self.state.project_name
        if full_path.exists():
            self._set_warning(f"Project already exists at {full_path}", update=True)
            return False

        self._set_warning("", update=False)
        return True
