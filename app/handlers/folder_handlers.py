"""Handlers for folder tree display and management."""

import asyncio
from typing import Any

import flet as ft

from app.core.validator import validate_folder_name
from app.ui.dialogs import create_add_item_dialog
from app.ui.ui_config import UIConfig


class FolderHandlersMixin:
    """Mixin for folder tree display, selection, add/remove operations.

    Expects HandlerBase helpers available via self.
    """

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
            if folder.get("create_init", True):
                file_count += 1  # __init__.py
            file_count += len(folder.get("files", []) or [])
            subfolders = folder.get("subfolders", []) or []
            if subfolders:
                sub_f, sub_fi = FolderHandlersMixin._count_folders_and_files(subfolders)
                folder_count += sub_f
                file_count += sub_fi

        return folder_count, file_count

    def _update_folder_display(self) -> None:
        """Update the folder display container with current folder structure."""
        folder_controls = []

        for idx, folder in enumerate(self.state.folders):
            self._process_folder_recursive(folder, [idx], 0, folder_controls)

        self.controls.subfolders_container.content.controls = folder_controls

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
        self._update_folder_display()

    def _get_folder_hierarchy(self) -> list[dict]:
        """Build list of all folders with their paths for parent selection.

        Returns:
            List of dicts with "label" (display name) and "path" (navigation path).
        """
        hierarchy = []

        def process_folder(
            folder: dict[str, Any], base_path: list, parent_name: str = ""
        ) -> None:
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
            Tuple of (parent_container, index).
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

    async def on_add_folder(self, e: ft.ControlEvent) -> None:
        """Handle Add Folder button click.

        Opens dialog to add a folder or file at a selected location.
        """

        async def add_item(name: str, item_type: str, parent_path: list | None):
            """Add folder or file to state."""
            valid, error = validate_folder_name(name)
            if not valid:
                dialog.warning_text.value = error
                dialog.warning_text.visible = True
                self.page.update()
                return

            if parent_path is None:
                parent_container = self.state.folders
            else:
                parent_container, idx = self._navigate_to_parent(parent_path)
                if isinstance(idx, int):
                    parent_folder = parent_container[idx]
                elif idx == "subfolders":
                    parent_folder = parent_container
                elif idx == "files":
                    dialog.warning_text.value = "Cannot add items inside a file."
                    dialog.warning_text.visible = True
                    self.page.update()
                    return
                else:
                    parent_folder = parent_container

                if item_type == "folder":
                    parent_container = parent_folder.setdefault("subfolders", [])
                else:
                    parent_container = parent_folder.setdefault("files", [])

            if item_type == "folder":
                new_item = {"name": name, "subfolders": [], "files": []}
                if parent_path is None:
                    self.state.folders.append(new_item)
                else:
                    parent_container.append(new_item)
            else:
                if parent_path is None:
                    dialog.warning_text.value = "Files must be added inside a folder."
                    dialog.warning_text.visible = True
                    self.page.update()
                    return
                parent_container.append(name)

            self._update_folder_display()

            dialog.warning_text.value = ""
            dialog.warning_text.visible = False
            dialog.open = False
            self.state.active_dialog = None

            self._set_status(
                f"{item_type.title()} '{name}' added.", "success", update=True
            )

        def close_dialog(_=None):
            dialog.open = False
            self.state.active_dialog = None
            self.page.update()

        parent_folders = self._get_folder_hierarchy()

        dialog = create_add_item_dialog(
            lambda n, t, p: asyncio.create_task(add_item(n, t, p)),
            close_dialog,
            parent_folders,
            self.state.is_dark_mode,
        )

        self._set_warning("", update=False)

        self.page.overlay.append(dialog)
        dialog.open = True
        self.state.active_dialog = close_dialog
        self.page.update()

    async def on_remove_folder(self, e: ft.ControlEvent) -> None:
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

        parent_container, idx = self._navigate_to_parent(self.state.selected_item_path)

        if parent_container is None or idx is None:
            self._set_warning("Cannot remove item: invalid selection.", update=True)
            return

        item_type = self.state.selected_item_type
        if isinstance(idx, int) and idx < len(parent_container):
            item = parent_container[idx]
            item_name = item.get("name", "unnamed") if isinstance(item, dict) else item

            del parent_container[idx]

            self.state.selected_item_path = None
            self.state.selected_item_type = None

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
