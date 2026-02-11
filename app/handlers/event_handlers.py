"""Event handlers for the UV Project Creator.

This module defines all event handlers for UI interactions, including
project configuration, folder management, and build operations.
Handlers are attached to UI controls via the attach_handlers function.
"""

import asyncio
from pathlib import Path

import flet as ft

from app.core.config_manager import ConfigManager
from app.core.models import BuildSummaryConfig, ProjectConfig
from app.core.project_builder import build_project
from app.core.state import AppState
from app.core.template_merger import merge_folder_lists
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
    create_build_summary_dialog,
    create_framework_dialog,
)
from app.ui.theme_manager import get_theme_colors
from app.utils.async_executor import AsyncExecutor
from app.core.constants import DEFAULT_FOLDERS, DEFAULT_PYTHON_VERSION, GIT_CHEAT_SHEET_FILE, HELP_FILE


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
    def _style_checkbox(checkbox: ft.Checkbox) -> None:
        """Set checkbox label green when checked, default when unchecked."""
        checkbox.label_style = (
            ft.TextStyle(color=ft.Colors.GREEN) if checkbox.value else None
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
            field.suffix = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
        else:
            field.suffix = ft.Icon(ft.Icons.CANCEL, color=ft.Colors.RED)

    def _update_build_button_state(self) -> None:
        """Enable/disable build button based on validation state."""
        is_ready = self.state.path_valid and self.state.name_valid
        btn = self.controls.build_project_button
        btn.disabled = not is_ready
        btn.opacity = 1.0 if is_ready else 0.5
        if is_ready:
            btn.tooltip = "Build project (Ctrl+Enter)"
        else:
            btn.tooltip = "Enter a valid path and project name to enable"

    def _show_snackbar(self, message: str, is_error: bool = False) -> None:
        """Show an auto-dismissing snackbar notification.

        Args:
            message: Message to display.
            is_error: True for red background, False for green.
        """
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
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
        """Update status text message and color.

        Args:
            message: Status message to display.
            status_type: One of "info", "success", or "error".
            update: Whether to call page.update() after setting.
        """
        colors = {
            "info": ft.Colors.BLUE_600,
            "success": ft.Colors.GREEN_600,
            "error": ft.Colors.RED_600,
        }
        self.controls.status_text.value = message
        self.controls.status_text.color = colors.get(status_type, ft.Colors.BLUE_600)
        if update:
            self.page.update()

    def _create_item_container(
        self, name: str, path: list, item_type: str, indent: int = 0
    ) -> ft.Container:
        """Create a clickable container for a folder or file.

        Args:
            name: Display name of the item.
            path: Navigation path to the item.
            item_type: Either "folder" or "file".
            indent: Indentation level (0 = root).

        Returns:
            Configured Container with click handler and selection highlighting.
        """
        prefix = "  " * indent + ("|- " if indent > 0 else "")
        is_selected = (
            self.state.selected_item_path == path
            and self.state.selected_item_type == item_type
        )

        # Format display text and color based on type
        if item_type == "folder":
            display_text = f"{prefix}{name}/"
            text_color = None  # Use default color
        else:  # file
            display_text = f"{prefix}{name}"
            text_color = ft.Colors.GREY_400

        return ft.Container(
            content=ft.Text(
                display_text,
                size=12,
                font_family="monospace",
                color=text_color,
            ),
            data={"path": path, "type": item_type, "name": name},
            bgcolor=ft.Colors.BLUE_800 if is_selected else None,
            border=ft.Border.all(2, ft.Colors.BLUE_400) if is_selected else None,
            on_click=self._on_item_click,
            padding=ft.Padding(left=4, right=4, top=1, bottom=1),
            border_radius=2,
            margin=0,
        )

    def _process_folder_recursive(
        self, folder, base_path: list, indent: int, controls_list: list
    ) -> None:
        """Recursively process a folder item and add to controls list.

        Args:
            folder: Folder item (string, dict, or FolderSpec).
            base_path: Navigation path to this folder.
            indent: Current indentation level.
            controls_list: List to append created containers to.
        """
        if isinstance(folder, str):
            controls_list.append(
                self._create_item_container(folder, base_path, "folder", indent)
            )
        elif isinstance(folder, dict):
            name = folder.get("name", "")
            controls_list.append(
                self._create_item_container(name, base_path, "folder", indent)
            )

            # Display files in this folder
            files = folder.get("files", [])
            if files:
                for file_idx, file_name in enumerate(files):
                    file_path = base_path + ["files", file_idx]
                    controls_list.append(
                        self._create_item_container(
                            file_name, file_path, "file", indent + 1
                        )
                    )

            # Display subfolders recursively
            subfolders = folder.get("subfolders", [])
            for subfolder_idx, subfolder in enumerate(subfolders):
                subfolder_path = base_path + ["subfolders", subfolder_idx]
                self._process_folder_recursive(
                    subfolder, subfolder_path, indent + 1, controls_list
                )
        else:
            # FolderSpec object
            controls_list.append(
                self._create_item_container(folder.name, base_path, "folder", indent)
            )

            # Display files in this folder
            if folder.files:
                for file_idx, file_name in enumerate(folder.files):
                    file_path = base_path + ["files", file_idx]
                    controls_list.append(
                        self._create_item_container(
                            file_name, file_path, "file", indent + 1
                        )
                    )

            # Display subfolders recursively
            if folder.subfolders:
                for subfolder_idx, subfolder in enumerate(folder.subfolders):
                    subfolder_path = base_path + ["subfolders", subfolder_idx]
                    self._process_folder_recursive(
                        subfolder, subfolder_path, indent + 1, controls_list
                    )

    @staticmethod
    def _count_folders_and_files(folders: list) -> tuple[int, int]:
        """Recursively count folders and files in a folder structure.

        Args:
            folders: List of folder items (str, dict, or FolderSpec).

        Returns:
            Tuple of (folder_count, file_count).
        """
        folder_count = 0
        file_count = 0

        for folder in folders:
            if isinstance(folder, str):
                folder_count += 1
            elif isinstance(folder, dict):
                folder_count += 1
                file_count += len(folder.get("files", []) or [])
                subfolders = folder.get("subfolders", []) or []
                if subfolders:
                    sub_f, sub_fi = Handlers._count_folders_and_files(subfolders)
                    folder_count += sub_f
                    file_count += sub_fi
            else:
                # FolderSpec object
                folder_count += 1
                if folder.files:
                    file_count += len(folder.files)
                if folder.subfolders:
                    sub_f, sub_fi = Handlers._count_folders_and_files(folder.subfolders)
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

        def process_folder(folder, base_path: list, parent_name: str = "") -> None:
            """Recursively process folders and build hierarchy."""
            if isinstance(folder, str):
                label = f"{parent_name}{folder}/" if parent_name else f"{folder}/"
                hierarchy.append({"label": label, "path": base_path})
            elif isinstance(folder, dict):
                name = folder.get("name", "")
                label = f"{parent_name}{name}/" if parent_name else f"{name}/"
                hierarchy.append({"label": label, "path": base_path})

                # Process subfolders
                subfolders = folder.get("subfolders", [])
                for subfolder_idx, subfolder in enumerate(subfolders):
                    subfolder_path = base_path + ["subfolders", subfolder_idx]
                    process_folder(subfolder, subfolder_path, label)
            else:
                # FolderSpec object
                label = (
                    f"{parent_name}{folder.name}/" if parent_name else f"{folder.name}/"
                )
                hierarchy.append({"label": label, "path": base_path})

                # Process subfolders
                if folder.subfolders:
                    for subfolder_idx, subfolder in enumerate(folder.subfolders):
                        subfolder_path = base_path + ["subfolders", subfolder_idx]
                        process_folder(subfolder, subfolder_path, label)

        for idx, folder in enumerate(self.state.folders):
            process_folder(folder, [idx])

        return hierarchy

    def _navigate_to_parent(self, path: list | None):
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
                if isinstance(current, dict):
                    current = current.get("subfolders", [])
                else:
                    current = (
                        current.subfolders if hasattr(current, "subfolders") else []
                    )
            elif segment == "files":
                if isinstance(current, dict):
                    current = current.get("files", [])
                else:
                    current = current.files if hasattr(current, "files") else []

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
        self.state.selected_python_version = e.control.value or DEFAULT_PYTHON_VERSION
        self._set_status(
            f"Python version set to {self.state.selected_python_version}",
            "info",
            update=True,
        )

    async def on_git_toggle(self, e: ft.ControlEvent) -> None:
        """Handle git initialization checkbox toggle."""
        self.state.initialize_git = e.control.value
        self._style_checkbox(e.control)
        status = "enabled" if self.state.initialize_git else "disabled"
        self._set_status(f"Git initialization {status}.", "info", update=True)

    async def on_boilerplate_toggle(self, e: ft.ControlEvent) -> None:
        """Handle include starter files checkbox toggle."""
        self.state.include_starter_files = e.control.value
        self._style_checkbox(e.control)
        status = "enabled" if self.state.include_starter_files else "disabled"
        self._set_status(f"Starter files {status}.", "info", update=True)

    async def on_ui_project_toggle(self, e: ft.ControlEvent) -> None:
        """Handle UI project checkbox toggle.

        Always opens the framework selection dialog. The dialog callbacks
        determine the final checked/unchecked state. Clicking an already-checked
        checkbox reopens the dialog to allow changing the selection.
        """
        e.control.value = True
        self.state.create_ui_project = True
        self._style_checkbox(e.control)
        self._show_framework_dialog()
        self.page.update()

    def _show_framework_dialog(self) -> None:
        """Show the UI framework selection dialog."""

        def on_select(framework: str | None) -> None:
            """Handle framework selection."""
            if framework is None:
                # "None" selected — clear state, uncheck checkbox, reset label
                self.state.selected_framework = None
                self.state.create_ui_project = False
                self.controls.create_ui_project_checkbox.value = False
                self.controls.create_ui_project_checkbox.label = "Create UI Project"
                self._style_checkbox(self.controls.create_ui_project_checkbox)
                self._reload_and_merge_templates()
                self._set_status("UI framework cleared.", "info", update=False)
            else:
                self.state.selected_framework = framework
                self.controls.create_ui_project_checkbox.label = (
                    f"UI Framework: {framework}"
                )
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
            if not self.state.selected_framework:
                self.state.create_ui_project = False
                self.controls.create_ui_project_checkbox.value = False
                self.controls.create_ui_project_checkbox.label = "Create UI Project"
                self._style_checkbox(self.controls.create_ui_project_checkbox)
                self._set_status("No framework selected.", "info", update=False)

            dialog.open = False
            self.page.update()

        dialog = create_framework_dialog(
            on_select_callback=on_select,
            on_close_callback=on_close,
            current_selection=self.state.selected_framework,
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
        self.state.create_other_project = True
        self._style_checkbox(e.control)
        self._show_project_type_dialog()
        self.page.update()

    def _show_project_type_dialog(self) -> None:
        """Show the project type selection dialog."""
        from app.ui.dialogs import create_project_type_dialog

        def on_select(project_type: str | None) -> None:
            """Handle project type selection."""
            if project_type is None:
                # "None" selected — clear state, uncheck checkbox, reset label
                self.state.selected_project_type = None
                self.state.create_other_project = False
                self.controls.other_projects_checkbox.value = False
                self.controls.other_projects_checkbox.label = (
                    "Create Other Project Type"
                )
                self._style_checkbox(self.controls.other_projects_checkbox)
                self._reload_and_merge_templates()
                self._set_status("Project type cleared.", "info", update=False)
            else:
                self.state.selected_project_type = project_type
                self._reload_and_merge_templates()

                # Update checkbox label with selected type
                type_name = project_type.replace("_", " ").title()
                self.controls.other_projects_checkbox.label = f"Project: {type_name}"
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
            if not self.state.selected_project_type:
                self.state.create_other_project = False
                self.controls.other_projects_checkbox.value = False
                self.controls.other_projects_checkbox.label = (
                    "Create Other Project Type"
                )
                self._style_checkbox(self.controls.other_projects_checkbox)
                self._set_status("No project type selected.", "info", update=False)

            dialog.open = False
            self.page.update()

        # Create and show dialog
        dialog = create_project_type_dialog(
            on_select_callback=on_select,
            on_close_callback=on_close,
            current_selection=self.state.selected_project_type,
            is_dark_mode=self.state.is_dark_mode,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _load_project_type_template(self, project_type: str | None) -> None:
        """Load folder template for the specified project type.

        Args:
            project_type: Project type name to load template for, or None for default.
        """
        # Try to load from project_types subfolder first
        if project_type:
            template_name = f"project_types/{project_type}"
        else:
            template_name = None

        settings = self.config_manager.load_config(template_name)
        self.state.folders = settings.get("folders", DEFAULT_FOLDERS.copy())
        self._update_folder_display()

    def _load_framework_template(self, framework: str | None) -> None:
        """Load folder template for the specified framework.

        Args:
            framework: Framework name to load template for, or None for default.
        """
        settings = self.config_manager.load_config(framework)
        self.state.folders = settings.get("folders", DEFAULT_FOLDERS.copy())
        self._update_folder_display()

    def _reload_and_merge_templates(self) -> None:
        """Reload templates based on current selections and merge if both are active.

        If both a UI framework and a project type are selected, their folder
        structures are merged. Otherwise the single active template is used.
        Falls back to the default template when neither is selected.
        """
        framework = (
            self.state.selected_framework if self.state.create_ui_project else None
        )
        project_type = (
            self.state.selected_project_type
            if self.state.create_other_project
            else None
        )

        if framework and project_type:
            fw_settings = self.config_manager.load_config(framework)
            fw_folders = fw_settings.get("folders", DEFAULT_FOLDERS.copy())

            pt_settings = self.config_manager.load_config(
                f"project_types/{project_type}"
            )
            pt_folders = pt_settings.get("folders", DEFAULT_FOLDERS.copy())

            self.state.folders = merge_folder_lists(fw_folders, pt_folders)

            fw_name = framework
            pt_name = project_type.replace("_", " ").title()
            self._set_status(
                f"Merged templates: {fw_name} + {pt_name}", "info", update=False
            )
        elif framework:
            settings = self.config_manager.load_config(framework)
            self.state.folders = settings.get("folders", DEFAULT_FOLDERS.copy())
        elif project_type:
            settings = self.config_manager.load_config(f"project_types/{project_type}")
            self.state.folders = settings.get("folders", DEFAULT_FOLDERS.copy())
        else:
            settings = self.config_manager.load_config(None)
            self.state.folders = settings.get("folders", DEFAULT_FOLDERS.copy())

        # Clear selection since folder structure changed
        self.state.selected_item_path = None
        self.state.selected_item_type = None

        self._update_folder_display()

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

                # Ensure parent is a dict (convert if needed)
                if isinstance(parent_folder, str):
                    # Convert string folder to dict
                    parent_folder = {
                        "name": parent_folder,
                        "subfolders": [],
                        "files": [],
                    }
                    parent_container[idx] = parent_folder
                elif not isinstance(parent_folder, dict):
                    # FolderSpec - convert to dict
                    parent_folder = {
                        "name": parent_folder.name,
                        "subfolders": list(parent_folder.subfolders)
                        if parent_folder.subfolders
                        else [],
                        "files": list(parent_folder.files)
                        if parent_folder.files
                        else [],
                    }
                    parent_container[idx] = parent_folder

                # Set parent_container to the folder's subfolders or files
                if item_type == "folder":
                    if "subfolders" not in parent_folder:
                        parent_folder["subfolders"] = []
                    parent_container = parent_folder["subfolders"]
                else:  # file
                    if "files" not in parent_folder:
                        parent_folder["files"] = []
                    parent_container = parent_folder["files"]

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
            if isinstance(item, str):
                item_name = item
            elif isinstance(item, dict):
                item_name = item.get("name", "unnamed")
            else:
                item_name = item.name if hasattr(item, "name") else "unnamed"

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
        self._style_checkbox(e.control)
        status = "enabled" if self.state.auto_save_folders else "disabled"
        self._set_status(f"Auto-save folder changes {status}.", "info", update=True)

    # --- Main Actions ---

    async def _execute_build(self) -> None:
        """Execute the project build after confirmation.

        Creates project configuration and runs the build asynchronously.
        """
        # Show progress
        self.controls.progress_ring.visible = True
        self.controls.build_project_button.disabled = True
        self._set_status("Building project...", "info", update=True)

        # Create project configuration
        config = ProjectConfig(
            name=self.state.project_name,
            path=Path(self.state.project_path),
            python_version=self.state.selected_python_version,
            git_enabled=self.state.initialize_git,
            ui_project_enabled=self.state.create_ui_project,
            framework=self.state.selected_framework or "",
            project_type=self.state.selected_project_type,
            include_starter_files=self.state.include_starter_files,
            folders=self.state.folders
            if self.state.folders
            else DEFAULT_FOLDERS.copy(),
        )

        # Build project asynchronously
        result = await AsyncExecutor.run(build_project, config)

        # Hide progress and update button state
        self.controls.progress_ring.visible = False
        self._update_build_button_state()

        if result.success:
            self._set_status(result.message, "success", update=False)
            self._show_snackbar(result.message, is_error=False)
        else:
            self._set_status(result.message, "error", update=False)
            self._show_snackbar(result.message, is_error=True)

        self.page.update()

    async def on_build_project(self, _: ft.ControlEvent) -> None:
        """Handle Build Project button click.

        Validates inputs and shows a confirmation dialog before building.
        """
        # Validate all inputs
        if not self._validate_inputs():
            return

        # Count folders/files for the summary
        fc, fic = self._count_folders_and_files(self.state.folders)

        async def on_confirm(_):
            dialog.open = False
            self.page.update()
            await self._execute_build()

        def on_cancel(_):
            dialog.open = False
            self.page.update()

        # Create build summary configuration
        build_config = BuildSummaryConfig(
            project_name=self.state.project_name,
            project_path=self.state.project_path,
            python_version=self.state.selected_python_version,
            git_enabled=self.state.initialize_git,
            framework=self.state.selected_framework
            if self.state.create_ui_project
            else None,
            project_type=self.state.selected_project_type
            if self.state.create_other_project
            else None,
            starter_files=self.state.include_starter_files,
            folder_count=fc,
            file_count=fic,
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
        self.controls.python_version_dropdown.value = self.state.selected_python_version
        self.controls.create_git_checkbox.value = False
        self.controls.include_starter_files_checkbox.value = True
        self.controls.create_ui_project_checkbox.value = False
        self.controls.create_ui_project_checkbox.label = "Create UI Project"
        self.controls.other_projects_checkbox.value = False
        self.controls.other_projects_checkbox.label = "Create Other Project Type"
        self.controls.auto_save_folder_changes.value = False

        # Reset checkbox label styles (include_starter_files stays green — it defaults to checked)
        for cb in (
            self.controls.create_git_checkbox,
            self.controls.create_ui_project_checkbox,
            self.controls.other_projects_checkbox,
            self.controls.auto_save_folder_changes,
        ):
            cb.label_style = None
        self.controls.include_starter_files_checkbox.label_style = ft.TextStyle(
            color=ft.Colors.GREEN
        )
        self.controls.warning_banner.value = ""
        self.controls.progress_ring.visible = False

        # Reset validation icons (default path is valid, name is empty)
        self._set_validation_icon(self.controls.project_path_input, True)
        self._set_validation_icon(self.controls.project_name_input, None)
        self._update_build_button_state()

        # Reset folder display to default template
        self._reload_and_merge_templates()

        self._set_status("All fields reset.", "info", update=True)

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

    # Load default folder template on startup
    handlers._load_framework_template(None)

    # Set initial UI state (path icon if default path exists, button disabled)
    if state.path_valid:
        Handlers._set_validation_icon(controls.project_path_input, True)
    handlers._update_build_button_state()

    # Apply green styling to any checkboxes that start in a checked state
    for checkbox in (
        controls.create_git_checkbox,
        controls.include_starter_files_checkbox,
    ):
        Handlers._style_checkbox(checkbox)

    # --- Path & Name Handlers ---
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
    controls.create_ui_project_checkbox.on_change = wrap_async(
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

    # --- Main Action Handlers ---
    controls.build_project_button.on_click = wrap_async(handlers.on_build_project)
    controls.reset_button.on_click = wrap_async(handlers.on_reset)
    controls.exit_button.on_click = wrap_async(handlers.on_exit)

    # --- UI Feature Handlers ---
    controls.git_cheat_sheet_button.on_click = wrap_async(handlers.on_git_cheat_sheet_click)
    controls.help_button.on_click = wrap_async(handlers.on_help_click)
    controls.theme_toggle_button.on_click = wrap_async(handlers.on_theme_toggle)

    # --- Keyboard Shortcuts ---
    page.on_keyboard_event = wrap_async(handlers.on_keyboard_event)

    # Update page to register all handlers
    page.update()
