"""Event handlers for the UV Project Creator.

This module defines all event handlers for UI interactions, including
project configuration, folder management, and build operations.
Handlers are attached to UI controls via the attach_handlers function.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Any

import flet as ft

from app.core.config_manager import ConfigManager
from app.core.models import BuildSummaryConfig, ProjectConfig
from app.core.project_builder import build_project
from app.core.state import AppState
from app.core.template_merger import merge_folder_lists, normalize_folder
from app.core.validator import (
    validate_path,
    validate_project_name,
    validate_folder_name,
)
from app.ui.components import Controls
from app.ui.dialogs import (
    create_git_cheat_sheet_dialog,
    create_help_dialog,
    create_add_item_dialog,
    create_add_packages_dialog,
    create_build_error_dialog,
    create_build_summary_dialog,
    create_framework_dialog,
)
from app.ui.theme_manager import get_theme_colors
from app.ui.ui_config import UIConfig
from app.utils.async_executor import AsyncExecutor
from app.core.constants import (
    DEFAULT_FOLDERS,
    DEFAULT_PYTHON_VERSION,
    FRAMEWORK_PACKAGE_MAP,
    GIT_CHEAT_SHEET_FILE,
    HELP_FILE,
    OTHER_PROJECT_CHECKBOX_LABEL,
    PROJECT_TYPE_PACKAGE_MAP,
    UI_PROJECT_CHECKBOX_LABEL,
)


def wrap_async(coro_func):
    """Wrap an async coroutine for Flet's sync callback system."""

    def wrapper(e):
        asyncio.create_task(coro_func(e))

    return wrapper


def _get_controls(page: ft.Page) -> Controls:
    """Retrieve the Controls instance from the page.

    Args:
        page: The Flet page containing the controls reference.

    Returns:
        The Controls instance stored on the page.
    """
    return page.controls_ref


class Handlers:
    """Event handlers for UI controls.

    Encapsulates all event handler methods and provides access to page,
    controls, and application state.
    """

    def __init__(self, page: ft.Page, controls: Controls, state: AppState) -> None:
        """Initialize handlers with required references.

        Args:
            page: The Flet page for UI updates.
            controls: The Controls instance containing UI references.
            state: The application state instance.
        """
        self.page = page
        self.controls = controls
        self.state = state
        self.config_manager = ConfigManager()

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
            btn.tooltip = "Build project (Ctrl+Enter)"
        else:
            btn.tooltip = "Enter a valid path and project name to enable"

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
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
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
            "success": (UIConfig.COLOR_SUCCESS, ft.Icons.CHECK_CIRCLE_OUTLINE),
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

    def _create_item_container(
        self, name: str, item_path: list[int | str], item_type: str, indent: int = 0
    ) -> ft.Container:
        """Create a clickable container for a folder or file.

        Args:
            name: Display name of the item.
            item_path: Navigation path to the item.
            item_type: Either "folder" or "file".
            indent: Indentation level (0 = root).

        Returns:
            Configured Container with click handler and selection highlighting.
        """
        is_selected = (
            self.state.selected_item_path == item_path
            and self.state.selected_item_type == item_type
        )

        if item_type == "folder":
            icon = ft.Icons.FOLDER
            icon_color = UIConfig.COLOR_FOLDER_ICON
            display_text = f"{name}/"
            text_color = None
        else:
            icon = ft.Icons.INSERT_DRIVE_FILE
            icon_color = UIConfig.COLOR_FILE_ICON
            display_text = name
            text_color = UIConfig.COLOR_FILE_TEXT

        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=13, color=icon_color),
                    ft.Text(
                        display_text,
                        size=UIConfig.TEXT_SIZE_SMALL,
                        font_family="monospace",
                        color=text_color,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                ],
                spacing=4,
                tight=True,
            ),
            data={"path": item_path, "type": item_type, "name": name},
            bgcolor=UIConfig.SELECTED_ITEM_BGCOLOR if is_selected else None,
            border=(
                ft.Border.all(
                    UIConfig.BORDER_WIDTH_DEFAULT, UIConfig.SELECTED_ITEM_BORDER_COLOR
                )
                if is_selected
                else None
            ),
            on_click=self._on_item_click,
            padding=ft.Padding(
                left=4 + indent * UIConfig.FOLDER_TREE_INDENT_PX,
                right=4,
                top=1,
                bottom=1,
            ),
            border_radius=2,
            margin=0,
        )

    def _process_folder_recursive(
        self,
        folder: dict[str, Any],
        base_path: list[int | str],
        indent: int,
        display_controls: list,
    ) -> None:
        """Recursively process a folder dict and add to display controls.

        Args:
            folder: Normalized folder dict with name, subfolders, files keys.
            base_path: Navigation path to this folder.
            indent: Current indentation level.
            display_controls: List to append created containers to.
        """
        name = folder.get("name", "")
        display_controls.append(
            self._create_item_container(name, base_path, "folder", indent)
        )

        for file_idx, file_name in enumerate(folder.get("files", [])):
            file_path = base_path + ["files", file_idx]
            display_controls.append(
                self._create_item_container(file_name, file_path, "file", indent + 1)
            )

        for subfolder_idx, subfolder in enumerate(folder.get("subfolders", [])):
            subfolder_path = base_path + ["subfolders", subfolder_idx]
            self._process_folder_recursive(
                subfolder, subfolder_path, indent + 1, display_controls
            )

    @staticmethod
    def _count_folders_and_files(folders: list[dict[str, Any]]) -> tuple[int, int]:
        """Recursively count folders and files in a normalized folder structure.

        Args:
            folders: List of normalized folder dicts.

        Returns:
            Tuple of (folder_count, file_count).
        """
        folder_count = 0
        file_count = 0

        for folder in folders:
            folder_count += 1
            file_count += len(folder.get("files", []) or [])
            subfolders = folder.get("subfolders", []) or []
            if subfolders:
                sub_f, sub_fi = Handlers._count_folders_and_files(subfolders)
                folder_count += sub_f
                file_count += sub_fi

        return folder_count, file_count

    def _update_folder_display(self) -> None:
        """Update the folder display container with current folder structure.

        Reads the current folder structure from state and creates clickable
        Container controls for each folder/file with selection highlighting.
        Also updates the subfolders label with folder/file counts.
        """
        folder_controls = []

        for idx, folder in enumerate(self.state.folders):
            self._process_folder_recursive(folder, [idx], 0, folder_controls)

        # Update the container
        self.controls.subfolders_container.content.controls = folder_controls

        # Update label with counts
        folder_count, file_count = self._count_folders_and_files(self.state.folders)
        self.controls.app_subfolders_label.value = (
            f"App Subfolders: {folder_count} folders, {file_count} files"
        )

        self.page.update()

    # --- Package Display ---

    def _create_package_item(self, pkg: str, idx: int) -> ft.Container:
        """Create a clickable package item container.

        Auto-derived packages (from framework/project type maps) show a muted
        'auto' badge on the right to distinguish them from manually added ones.
        """
        is_selected = self.state.selected_package_idx == idx
        is_auto = pkg in self.state.auto_packages

        row_controls: list[ft.Control] = [
            ft.Text(
                pkg,
                size=UIConfig.TEXT_SIZE_SMALL,
                font_family="monospace",
                expand=True,
            )
        ]
        if is_auto:
            row_controls.append(
                ft.Text("auto", size=10, color=ft.Colors.GREY_500, italic=True)
            )

        return ft.Container(
            content=ft.Row(row_controls, spacing=4),
            data={"idx": idx, "name": pkg},
            bgcolor=UIConfig.SELECTED_ITEM_BGCOLOR if is_selected else None,
            border=(
                ft.Border.all(
                    UIConfig.BORDER_WIDTH_DEFAULT, UIConfig.SELECTED_ITEM_BORDER_COLOR
                )
                if is_selected
                else None
            ),
            on_click=self._on_package_click,
            padding=UIConfig.FOLDER_ITEM_PADDING,
            border_radius=2,
            margin=0,
        )

    def _update_package_display(self) -> None:
        """Update the packages container with the current package list."""
        if self.state.packages:
            package_controls = [
                self._create_package_item(pkg, idx)
                for idx, pkg in enumerate(self.state.packages)
            ]
        else:
            package_controls = [
                ft.Container(
                    content=ft.Text(
                        "No packages",
                        size=UIConfig.TEXT_SIZE_SMALL,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                    padding=ft.Padding(left=4, top=4, right=0, bottom=0),
                )
            ]
        self.controls.packages_container.content.controls = package_controls
        count = len(self.state.packages)
        self.controls.packages_label.value = f"Packages: {count}"
        self.page.update()

    def _on_package_click(self, e: ft.ControlEvent) -> None:
        """Handle click on a package item to select it."""
        self.state.selected_package_idx = e.control.data["idx"]
        pkg_name = e.control.data["name"]
        self._set_status(f"Selected package: {pkg_name}", "info", update=False)
        self._update_package_display()

    def _collect_state_packages(self) -> list[str]:
        """Build the package list from current framework/project type selections."""
        packages: list[str] = []
        if self.state.ui_project_enabled and self.state.framework:
            fw_pkg = FRAMEWORK_PACKAGE_MAP.get(self.state.framework)
            if fw_pkg:
                packages.append(fw_pkg)
        if self.state.other_project_enabled and self.state.project_type:
            packages.extend(PROJECT_TYPE_PACKAGE_MAP.get(self.state.project_type, []))
        return packages

    def _on_item_click(self, e: ft.ControlEvent) -> None:
        """Handle click on folder/file item to select it."""
        self.state.selected_item_path = e.control.data["path"]
        self.state.selected_item_type = e.control.data["type"]
        item_name = e.control.data["name"]
        self._set_status(
            f"Selected {e.control.data['type']}: {item_name}", "info", update=False
        )
        self._update_folder_display()  # Re-render to show selection

    def _get_folder_hierarchy(self) -> list[dict]:
        """Build list of all folders with their paths for parent selection.

        Returns:
            List of dicts with "label" (display name) and "path" (navigation path).
            Example: [{"label": "core/", "path": [0]}, {"label": "core/ui/", "path": [0, "subfolders", 0]}]
        """
        hierarchy = []

        def process_folder(
            folder: dict[str, Any], base_path: list, parent_name: str = ""
        ) -> None:
            """Recursively process folders and build hierarchy."""
            name = folder.get("name", "")
            label = f"{parent_name}{name}/" if parent_name else f"{name}/"
            hierarchy.append({"label": label, "path": base_path})

            for subfolder_idx, subfolder in enumerate(folder.get("subfolders", [])):
                subfolder_path = base_path + ["subfolders", subfolder_idx]
                process_folder(subfolder, subfolder_path, label)

        for idx, folder in enumerate(self.state.folders):
            process_folder(folder, [idx])

        return hierarchy

    def _navigate_to_parent(
        self, path: list | None
    ) -> tuple[list | dict, int | str | None]:
        """Navigate to parent container by path.

        Args:
            path: Path to navigate (e.g., [0, "subfolders", 1])

        Returns:
            Tuple of (parent_container, index) where parent_container is the list/dict
            containing the item, and index is the position in that container.
        """
        if not path:
            return self.state.folders, None

        current = self.state.folders
        for segment in path[:-1]:
            if isinstance(segment, int):
                current = current[segment]
            elif segment == "subfolders":
                current = current.get("subfolders", [])
            elif segment == "files":
                current = current.get("files", [])

        return current, path[-1]

    def _validate_inputs(self) -> bool:
        """Validate all required inputs before building.

        Returns:
            True if all inputs are valid, False otherwise.
        """
        # Validate path
        path = Path(self.state.project_path)
        path_valid, path_error = validate_path(path)
        if not path_valid:
            self._set_warning(path_error, update=True)
            return False

        # Validate project name
        name_valid, name_error = validate_project_name(self.state.project_name)
        if not name_valid:
            self._set_warning(name_error, update=True)
            return False

        # Check if project already exists
        full_path = path / self.state.project_name
        if full_path.exists():
            self._set_warning(f"Project already exists at {full_path}", update=True)
            return False

        # Clear warning if all valid
        self._set_warning("", update=False)
        return True

    # --- Path & Name Handlers ---

    async def on_copy_path(self, _: ft.ControlEvent) -> None:
        """Copy the full project path (base + name) to the system clipboard."""
        full_path = str(Path(self.state.project_path) / self.state.project_name)
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
        except (FileNotFoundError, subprocess.CalledProcessError):
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
            # Validate the new path
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
            self._set_status("", "info", update=True)
        else:
            self._set_warning(error_msg, update=True)

    async def on_project_name_change(self, e: ft.ControlEvent) -> None:
        """Handle project name input changes.

        Validates the project name and updates state accordingly.
        """
        name = e.control.value if e.control.value else ""
        self.state.project_name = name

        if not name:
            self.state.name_valid = False
            self._set_validation_icon(self.controls.project_name_input, None)
            self._update_build_button_state()
            self._set_warning("Enter a project name.", update=True)
            return

        # Validate raw input to catch invalid characters (including spaces) immediately
        is_valid, error_msg = validate_project_name(name)
        self.state.name_valid = is_valid

        if is_valid:
            # Check if project already exists
            full_path = Path(self.state.project_path) / name
            if full_path.exists():
                self.state.name_valid = False
                self._set_validation_icon(self.controls.project_name_input, False)
                self._set_warning(
                    f"Project '{name}' already exists at this location.",
                    update=True,
                )
            else:
                self._set_validation_icon(self.controls.project_name_input, True)
                self._set_warning("", update=False)
                self._set_status(
                    f"Project will be created at: {full_path}", "info", update=True
                )
        else:
            self._set_validation_icon(self.controls.project_name_input, False)
            self._set_warning(error_msg, update=True)

        self._update_build_button_state()

    # --- Options Handlers ---

    async def on_python_version_change(self, e: ft.ControlEvent) -> None:
        """Handle Python version dropdown changes."""
        self.state.python_version = e.control.value or DEFAULT_PYTHON_VERSION
        self._set_status(
            f"Python version set to {self.state.python_version}",
            "info",
            update=True,
        )

    async def on_git_toggle(self, e: ft.ControlEvent) -> None:
        """Handle git initialization checkbox toggle."""
        self.state.git_enabled = e.control.value
        self._style_selected_checkbox(e.control)
        status = "enabled" if self.state.git_enabled else "disabled"
        self._set_status(f"Git initialization {status}.", "info", update=True)

    async def on_boilerplate_toggle(self, e: ft.ControlEvent) -> None:
        """Handle include starter files checkbox toggle."""
        self.state.include_starter_files = e.control.value
        self._style_selected_checkbox(e.control)
        status = "enabled" if self.state.include_starter_files else "disabled"
        self._set_status(f"Starter files {status}.", "info", update=True)

    async def on_ui_project_toggle(self, e: ft.ControlEvent) -> None:
        """Handle UI project checkbox toggle.

        Always opens the framework selection dialog. The dialog callbacks
        determine the final checked/unchecked state. Clicking an already-checked
        checkbox reopens the dialog to allow changing the selection.
        """
        e.control.value = True
        self.state.ui_project_enabled = True
        self._style_selected_checkbox(e.control)
        self._show_framework_dialog()
        self.page.update()

    def _show_framework_dialog(self) -> None:
        """Show the UI framework selection dialog."""

        def on_select(framework: str | None) -> None:
            """Handle framework selection."""
            if framework is None:
                # "None" selected — clear state, uncheck checkbox, reset label
                self.state.framework = None
                self.state.ui_project_enabled = False
                self.controls.ui_project_checkbox.value = False
                self.controls.ui_project_checkbox.label = UI_PROJECT_CHECKBOX_LABEL
                self._style_selected_checkbox(self.controls.ui_project_checkbox)
                self._reload_and_merge_templates()
                self._set_status("UI framework cleared.", "info", update=False)
            else:
                self.state.framework = framework
                self.controls.ui_project_checkbox.label = (
                    f"UI Framework: {framework}"
                )
                self._style_selected_checkbox(self.controls.ui_project_checkbox)
                self._reload_and_merge_templates()
                self._set_status(
                    f"Framework set to {framework}. Template loaded.",
                    "success",
                    update=False,
                )

            dialog.open = False
            self.page.update()

        def on_close(e) -> None:
            """Handle dialog close/cancel."""
            if not self.state.framework:
                self.state.ui_project_enabled = False
                self.controls.ui_project_checkbox.value = False
                self.controls.ui_project_checkbox.label = UI_PROJECT_CHECKBOX_LABEL
                self._style_selected_checkbox(self.controls.ui_project_checkbox)
                self._set_status("No framework selected.", "info", update=False)

            dialog.open = False
            self.page.update()

        dialog = create_framework_dialog(
            on_select_callback=on_select,
            on_close_callback=on_close,
            current_selection=self.state.framework,
            is_dark_mode=self.state.is_dark_mode,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    async def on_other_project_toggle(self, e: ft.ControlEvent) -> None:
        """Handle Other Project Type checkbox toggle.

        Always opens the project type selection dialog. The dialog callbacks
        determine the final checked/unchecked state. Clicking an already-checked
        checkbox reopens the dialog to allow changing the selection.
        """
        e.control.value = True
        self.state.other_project_enabled = True
        self._style_selected_checkbox(e.control)
        self._show_project_type_dialog()
        self.page.update()

    def _show_project_type_dialog(self) -> None:
        """Show the project type selection dialog."""
        from app.ui.dialogs import create_project_type_dialog

        def on_select(project_type: str | None) -> None:
            """Handle project type selection."""
            if project_type is None:
                # "None" selected — clear state, uncheck checkbox, reset label
                self.state.project_type = None
                self.state.other_project_enabled = False
                self.controls.other_projects_checkbox.value = False
                self.controls.other_projects_checkbox.label = (
                    OTHER_PROJECT_CHECKBOX_LABEL
                )
                self._style_selected_checkbox(self.controls.other_projects_checkbox)
                self._reload_and_merge_templates()
                self._set_status("Project type cleared.", "info", update=False)
            else:
                self.state.project_type = project_type
                self._reload_and_merge_templates()

                # Update checkbox label with selected type
                type_name = project_type.replace("_", " ").title()
                self.controls.other_projects_checkbox.label = f"Project: {type_name}"
                self._style_selected_checkbox(self.controls.other_projects_checkbox)
                self._set_status(
                    f"Project Type: {type_name}. Template loaded.",
                    "success",
                    update=False,
                )

            # Close dialog
            dialog.open = False
            self.page.update()

        def on_close(e) -> None:
            """Handle dialog close/cancel."""
            # If no project type selected, uncheck the checkbox
            if not self.state.project_type:
                self.state.other_project_enabled = False
                self.controls.other_projects_checkbox.value = False
                self.controls.other_projects_checkbox.label = (
                    OTHER_PROJECT_CHECKBOX_LABEL
                )
                self._style_selected_checkbox(self.controls.other_projects_checkbox)
                self._set_status("No project type selected.", "info", update=False)

            dialog.open = False
            self.page.update()

        # Create and show dialog
        dialog = create_project_type_dialog(
            on_select_callback=on_select,
            on_close_callback=on_close,
            current_selection=self.state.project_type,
            is_dark_mode=self.state.is_dark_mode,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _load_template_folders(self, template_name: str | None) -> list[dict]:
        """Load and normalize folder list from a template.

        Args:
            template_name: Template path (e.g. "flet", "project_types/django"),
                or None for default.

        Returns:
            List of normalized folder dicts.
        """
        settings = self.config_manager.load_config(template_name)
        raw_folders = settings.get("folders", DEFAULT_FOLDERS.copy())
        return [normalize_folder(f) for f in raw_folders]

    def _load_project_type_template(self, project_type: str | None) -> None:
        """Load folder template for the specified project type.

        Args:
            project_type: Project type name to load template for, or None for default.
        """
        template_name = f"project_types/{project_type}" if project_type else None
        self.state.folders = self._load_template_folders(template_name)
        self._update_folder_display()

    def _load_framework_template(self, framework: str | None) -> None:
        """Load folder template for the specified framework.

        Args:
            framework: Framework name to load template for, or None for default.
        """
        self.state.folders = self._load_template_folders(framework)
        self._update_folder_display()

    def _reload_and_merge_templates(self) -> None:
        """Reload templates based on current selections and merge if both are active.

        If both a UI framework and a project type are selected, their folder
        structures are merged. Otherwise the single active template is used.
        Falls back to the default template when neither is selected.
        """
        framework = (
            self.state.framework if self.state.ui_project_enabled else None
        )
        project_type = (
            self.state.project_type
            if self.state.other_project_enabled
            else None
        )

        if framework and project_type:
            fw_folders = self._load_template_folders(framework)
            pt_folders = self._load_template_folders(
                f"project_types/{project_type}"
            )
            self.state.folders = merge_folder_lists(fw_folders, pt_folders)

            pt_name = project_type.replace("_", " ").title()
            self._set_status(
                f"Merged templates: {framework} + {pt_name}", "info", update=False
            )
        elif framework:
            self.state.folders = self._load_template_folders(framework)
        elif project_type:
            self.state.folders = self._load_template_folders(
                f"project_types/{project_type}"
            )
        else:
            self.state.folders = self._load_template_folders(None)

        # Clear selections since structure changed
        self.state.selected_item_path = None
        self.state.selected_item_type = None
        self.state.selected_package_idx = None

        # Rebuild package list: keep user-added packages, replace auto ones
        new_auto = self._collect_state_packages()
        prev_auto = set(self.state.auto_packages)
        manual = [p for p in self.state.packages if p not in prev_auto]
        new_auto_set = set(new_auto)
        self.state.packages = new_auto + [p for p in manual if p not in new_auto_set]
        self.state.auto_packages = new_auto

        self._update_folder_display()
        self._update_package_display()

    # --- Folder Management Handlers ---

    async def on_add_folder(self, _: ft.ControlEvent) -> None:
        """Handle Add Folder button click.

        Opens dialog to add a folder or file at a selected location.
        """

        async def add_item(name: str, item_type: str, parent_path: list | None):
            """Add folder or file to state."""
            # Validate name
            valid, error = validate_folder_name(name)
            if not valid:
                # Show error in dialog's warning banner
                dialog.warning_text.value = error
                dialog.warning_text.visible = True
                self.page.update()
                return

            # Navigate to parent location
            if parent_path is None:
                # Add to root level
                parent_container = self.state.folders
            else:
                parent_container, idx = self._navigate_to_parent(parent_path)
                if isinstance(idx, int):
                    # Get the actual folder object
                    parent_folder = parent_container[idx]
                elif idx == "subfolders":
                    parent_folder = parent_container
                elif idx == "files":
                    # Show error in dialog's warning banner
                    dialog.warning_text.value = "Cannot add items inside a file."
                    dialog.warning_text.visible = True
                    self.page.update()
                    return
                else:
                    parent_folder = parent_container

                # Set parent_container to the folder's subfolders or files
                if item_type == "folder":
                    parent_container = parent_folder.setdefault("subfolders", [])
                else:  # file
                    parent_container = parent_folder.setdefault("files", [])

            # Add the new item
            if item_type == "folder":
                new_item = {"name": name, "subfolders": [], "files": []}
                if parent_path is None:
                    self.state.folders.append(new_item)
                else:
                    parent_container.append(new_item)
            else:  # file
                if parent_path is None:
                    # Show error in dialog's warning banner
                    dialog.warning_text.value = "Files must be added inside a folder."
                    dialog.warning_text.visible = True
                    self.page.update()
                    return
                parent_container.append(name)

            # Update display and close dialog
            self._update_folder_display()

            # Clear dialog warning and close
            dialog.warning_text.value = ""
            dialog.warning_text.visible = False
            dialog.open = False

            self._set_status(
                f"{item_type.title()} '{name}' added.", "success", update=True
            )

        def close_dialog(_):
            """Close the dialog."""
            dialog.open = False
            self.page.update()

        # Get list of parent folder options
        parent_folders = self._get_folder_hierarchy()

        # Create and show dialog
        dialog = create_add_item_dialog(
            lambda n, t, p: asyncio.create_task(add_item(n, t, p)),
            close_dialog,
            parent_folders,
            self.state.is_dark_mode,
        )

        # Clear any stale warnings from main window
        self._set_warning("", update=False)

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    async def on_remove_folder(self, _: ft.ControlEvent) -> None:
        """Handle Remove Folder button click.

        Removes the currently selected folder or file from state.
        """
        if not self.state.selected_item_path:
            self._set_status(
                "No item selected. Click an item to select it first.",
                "info",
                update=True,
            )
            return

        # Navigate to parent and remove item
        parent_container, idx = self._navigate_to_parent(self.state.selected_item_path)

        if parent_container is None or idx is None:
            self._set_warning("Cannot remove item: invalid selection.", update=True)
            return

        # Get item name before removal for status message
        item_type = self.state.selected_item_type
        if isinstance(idx, int) and idx < len(parent_container):
            item = parent_container[idx]
            item_name = item.get("name", "unnamed") if isinstance(item, dict) else item

            # Remove the item
            del parent_container[idx]

            # Clear selection
            self.state.selected_item_path = None
            self.state.selected_item_type = None

            # Update display
            self._update_folder_display()
            self._set_status(
                f"{item_type.title()} '{item_name}' removed.", "success", update=True
            )
        else:
            self._set_warning("Cannot remove item: index out of range.", update=True)

    async def on_auto_save_toggle(self, e: ft.ControlEvent) -> None:
        """Handle auto-save folder changes checkbox toggle."""
        self.state.auto_save_folders = e.control.value
        self._style_selected_checkbox(e.control)
        status = "enabled" if self.state.auto_save_folders else "disabled"
        self._set_status(f"Auto-save folder changes {status}.", "info", update=True)

    # --- Package Management Handlers ---

    async def on_add_package(self, _: ft.ControlEvent) -> None:
        """Handle Add Packages button click.

        Opens a dialog where the user can enter one or more package names
        (one per line or comma-separated). Deduplicates against the existing list.
        """
        existing = set(self.state.packages)

        def on_packages_entered(new_packages: list[str]) -> None:
            added = [p for p in new_packages if p not in existing]
            self.state.packages.extend(added)
            existing.update(added)
            dialog.open = False
            self._update_package_display()
            if added:
                self._set_status(
                    f"Added {len(added)} package(s): {', '.join(added)}",
                    "success",
                    update=True,
                )
            else:
                self._set_status(
                    "All entered packages are already in the list.",
                    "info",
                    update=True,
                )

        def on_close(_):
            dialog.open = False
            self.page.update()

        dialog = create_add_packages_dialog(
            on_add_callback=on_packages_entered,
            on_close_callback=on_close,
            is_dark_mode=self.state.is_dark_mode,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    async def on_clear_packages(self, _: ft.ControlEvent) -> None:
        """Handle Clear All packages button click.

        Removes all packages from the install list, including auto and manual.
        """
        if not self.state.packages:
            return
        self.state.packages = []
        self.state.auto_packages = []
        self.state.selected_package_idx = None
        self._update_package_display()
        self._set_status("All packages cleared.", "info", update=True)

    async def on_remove_package(self, _: ft.ControlEvent) -> None:
        """Handle Remove Package button click.

        Removes the currently selected package from the install list.
        """
        if self.state.selected_package_idx is None:
            self._set_warning("Select a package to remove.", update=True)
            return
        idx = self.state.selected_package_idx
        if 0 <= idx < len(self.state.packages):
            pkg = self.state.packages.pop(idx)
            self.state.selected_package_idx = None
            self._update_package_display()
            self._set_status(f"Package '{pkg}' removed.", "success", update=True)
        else:
            self._set_warning("Cannot remove package: index out of range.", update=True)

    # --- Main Actions ---

    @staticmethod
    def _open_in_file_manager(project_path: Path) -> None:
        """Open the project directory in the OS file manager."""
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(project_path)])
        elif sys.platform == "win32":
            subprocess.Popen(["explorer", str(project_path)])
        else:
            subprocess.Popen(["xdg-open", str(project_path)])

    def _open_in_vscode(self, project_path: Path) -> None:
        """Open the project directory in VS Code."""
        try:
            if sys.platform == "darwin":
                subprocess.Popen(
                    ["open", "-a", "Visual Studio Code", str(project_path)]
                )
            else:
                subprocess.Popen(["code", str(project_path)])
        except FileNotFoundError:
            self._show_snackbar("VS Code not found", is_error=True)

    async def _execute_build(
        self, open_folder: bool = False, open_vscode: bool = False
    ) -> None:
        """Execute the project build after confirmation.

        Creates project configuration and runs the build asynchronously.
        """
        # Show progress
        self.controls.progress_ring.visible = True
        self.controls.build_project_button.disabled = True
        self._set_status("Building project...", "info", update=True)

        # Create project configuration
        config = ProjectConfig(
            project_name=self.state.project_name,
            project_path=Path(self.state.project_path),
            python_version=self.state.python_version,
            git_enabled=self.state.git_enabled,
            ui_project_enabled=self.state.ui_project_enabled,
            framework=self.state.framework or "",
            other_project_enabled=self.state.other_project_enabled,
            project_type=self.state.project_type,
            include_starter_files=self.state.include_starter_files,
            folders=self.state.folders
            if self.state.folders
            else DEFAULT_FOLDERS.copy(),
            packages=list(self.state.packages),
        )

        # Build project asynchronously, forwarding step updates to the status text
        def _on_build_progress(msg: str) -> None:
            self._set_status(msg, "info", update=True)

        result = await AsyncExecutor.run(build_project, config, _on_build_progress)

        # Hide progress and update button state
        self.controls.progress_ring.visible = False
        self._update_build_button_state()

        if result.success:
            self._set_status(result.message, "success", update=False)
            self._show_snackbar(result.message, is_error=False)
            project_path = config.project_path / config.project_name
            if open_folder:
                self._open_in_file_manager(project_path)
            if open_vscode:
                self._open_in_vscode(project_path)
        else:
            self._set_status("Build failed. See error details.", "error", update=False)

            def close_error_dialog(_):
                error_dialog.open = False
                self.page.update()

            error_dialog = create_build_error_dialog(
                error_message=result.message,
                on_close_callback=close_error_dialog,
                is_dark_mode=self.state.is_dark_mode,
            )
            self.page.overlay.append(error_dialog)
            error_dialog.open = True

        self.page.update()

    async def on_build_project(self, _: ft.ControlEvent) -> None:
        """Handle Build Project button click.

        Validates inputs and shows a confirmation dialog before building.
        """
        # Validate all inputs
        if not self._validate_inputs():
            return

        # Count folders/files for the summary
        folder_count, file_count = self._count_folders_and_files(self.state.folders)

        async def on_confirm(_):
            open_folder = dialog.open_folder_checkbox.value
            open_vscode = dialog.open_vscode_checkbox.value
            dialog.open = False
            self.page.update()
            await self._execute_build(open_folder=open_folder, open_vscode=open_vscode)

        def on_cancel(_):
            dialog.open = False
            self.page.update()

        # Create build summary configuration
        build_config = BuildSummaryConfig(
            project_name=self.state.project_name,
            project_path=self.state.project_path,
            python_version=self.state.python_version,
            git_enabled=self.state.git_enabled,
            ui_project_enabled=self.state.ui_project_enabled,
            framework=self.state.framework
            if self.state.ui_project_enabled
            else None,
            other_project_enabled=self.state.other_project_enabled,
            project_type=self.state.project_type
            if self.state.other_project_enabled
            else None,
            starter_files=self.state.include_starter_files,
            folder_count=folder_count,
            file_count=file_count,
            packages=list(self.state.packages),
        )

        dialog = create_build_summary_dialog(
            config=build_config,
            on_build_callback=wrap_async(on_confirm),
            on_cancel_callback=on_cancel,
            is_dark_mode=self.state.is_dark_mode,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    async def on_reset(self, _: ft.ControlEvent) -> None:
        """Handle Reset button click.

        Resets all UI controls and state to initial values.
        """
        # Reset state (preserves dark mode)
        self.state.reset()

        # Reset UI controls
        self.controls.project_path_input.value = self.state.project_path
        self.controls.project_name_input.value = ""
        self.controls.python_version_dropdown.value = self.state.python_version
        self.controls.create_git_checkbox.value = True
        self.controls.include_starter_files_checkbox.value = True
        self.controls.ui_project_checkbox.value = False
        self.controls.ui_project_checkbox.label = UI_PROJECT_CHECKBOX_LABEL
        self.controls.other_projects_checkbox.value = False
        self.controls.other_projects_checkbox.label = OTHER_PROJECT_CHECKBOX_LABEL
        self.controls.auto_save_folder_changes.value = False

        # Reset checkbox label styles (include_starter_files stays green — it defaults to checked)
        for cb in (
            self.controls.create_git_checkbox,
            self.controls.ui_project_checkbox,
            self.controls.other_projects_checkbox,
            self.controls.auto_save_folder_changes,
        ):
            cb.label_style = None
        self._style_selected_checkbox(self.controls.include_starter_files_checkbox)
        self._style_selected_checkbox(self.controls.create_git_checkbox)
        self.controls.warning_banner.value = ""
        self.controls.progress_ring.visible = False

        # Reset validation icons (default path is valid, name is empty)
        self._set_validation_icon(self.controls.project_path_input, True)
        self._set_validation_icon(self.controls.project_name_input, None)
        self._update_build_button_state()

        # Reset folder/package displays to default template
        self._reload_and_merge_templates()

        self._set_status("All fields reset.", "info", update=True)
        await self.controls.project_path_input.focus()

    async def on_keyboard_event(self, e: ft.KeyboardEvent) -> None:
        """Handle keyboard shortcuts.

        Ctrl+Enter or Cmd+Enter triggers the build when inputs are valid.
        """
        if e.key == "Enter" and (e.ctrl or e.meta):
            # Only trigger if inputs are valid and button is not already disabled
            # (prevents double-trigger during an active build)
            if (
                self.state.path_valid
                and self.state.name_valid
                and not self.controls.build_project_button.disabled
            ):
                await self.on_build_project(e)

    async def on_exit(self, _: ft.ControlEvent) -> None:
        """Handle Exit button click."""
        await self.page.window.close()

    # --- UI Feature Handlers ---

    async def on_theme_toggle(self, _: ft.ControlEvent) -> None:
        """Handle theme toggle button click."""
        self.state.is_dark_mode = not self.state.is_dark_mode
        colors = get_theme_colors(self.state.is_dark_mode)

        if self.state.is_dark_mode:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.controls.theme_toggle_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.controls.theme_toggle_button.icon = ft.Icons.DARK_MODE

        # Update section colors
        for title_text in self.controls.section_titles:
            title_text.color = colors["section_title"]
        for container in self.controls.section_containers:
            container.border = ft.Border.all(1, colors["section_border"])

        self.page.bottom_appbar.bgcolor = colors["bottom_bar"]
        self.page.update()

    async def on_help_click(self, _: ft.ControlEvent) -> None:
        """Handle Help button click.

        Displays help information about the application.
        """
        # Load help text from file with fallback
        try:
            help_text = HELP_FILE.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError) as e:
            # Fallback help text if file cannot be read
            help_text = """# UV Project Creator Help

**Error**: Could not load help file.

This application helps you create new Python projects using UV.

For more information, visit: https://docs.astral.sh/uv/
"""
            # Log the error to status
            self._set_status(
                f"Warning: Help file not found ({e})", "error", update=False
            )

        def close_dialog(_):
            help_dialog.open = False
            self.page.update()

        help_dialog = create_help_dialog(
            help_text, close_dialog, self.page, self.state.is_dark_mode
        )

        self.page.overlay.append(help_dialog)
        help_dialog.open = True
        self.page.update()

    async def on_git_cheat_sheet_click(self, _: ft.ControlEvent) -> None:
        """Handle Git Cheat Sheet button click."""
        try:
            content = GIT_CHEAT_SHEET_FILE.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError) as e:
            content = "# Git Cheat Sheet\n\nError: Could not load cheat sheet file."
            self._set_status(
                f"Warning: Cheat sheet file not found ({e})", "error", update=False
            )

        def close_dialog(_):
            cheat_sheet_dialog.open = False
            self.page.update()

        cheat_sheet_dialog = create_git_cheat_sheet_dialog(
            content, close_dialog, self.page, self.state.is_dark_mode
        )

        self.page.overlay.append(cheat_sheet_dialog)
        cheat_sheet_dialog.open = True
        self.page.update()


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
