"""Handlers for build, reset, exit, and keyboard shortcuts."""

import subprocess
import sys
from pathlib import Path

import flet as ft

from app.core.async_executor import AsyncExecutor
from app.core.constants import (
    DEFAULT_FOLDERS,
    IDE_MACOS_APP_NAMES,
    SUPPORTED_IDES,
)
from app.core.models import BuildSummaryConfig, ProjectConfig
from app.handlers.handler_base import wrap_async
from app.handlers.project_builder import build_project
from app.ui.dialog_data import (
    OTHER_PROJECT_CHECKBOX_LABEL,
    UI_PROJECT_CHECKBOX_LABEL,
)
from app.ui.dialogs import (
    create_build_error_dialog,
    create_build_summary_dialog,
    create_confirm_dialog,
)


class BuildHandlersMixin:
    """Mixin for build execution, reset, exit, and keyboard shortcuts.

    Expects HandlerBase helpers and folder/template methods available via self.
    """

    @staticmethod
    def _open_in_file_manager(project_path: Path) -> None:
        """Open the project directory in the OS file manager.

        Args:
            project_path: Path to the project directory to open.
        """
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(project_path)])
        elif sys.platform == "win32":
            subprocess.Popen(["explorer", str(project_path)])
        else:
            subprocess.Popen(["xdg-open", str(project_path)])

    @staticmethod
    def _open_in_terminal(project_path: Path) -> None:
        """Open a terminal window at the project root.

        Args:
            project_path: Path to the project directory to open in a terminal.
        """
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Terminal", str(project_path)])
        elif sys.platform == "win32":
            subprocess.Popen(
                ["cmd"],
                cwd=str(project_path),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            for terminal, args in [
                ("gnome-terminal", [f"--working-directory={project_path}"]),
                ("konsole", ["--workdir", str(project_path)]),
                ("xfce4-terminal", ["--working-directory", str(project_path)]),
                ("xterm", []),
            ]:
                try:
                    subprocess.Popen([terminal] + args, cwd=str(project_path))
                    break
                except FileNotFoundError:
                    continue

    def _open_in_ide(self, project_path: Path) -> None:
        """Open the project directory in the user's preferred IDE.

        Uses the IDE configured in settings. Falls back to the CLI command
        from SUPPORTED_IDES, with macOS ``open -a`` handling for known apps.

        Args:
            project_path: Path to the project directory to open.
        """
        ide_name = self.state.settings.preferred_ide
        command = SUPPORTED_IDES.get(ide_name)

        # "Other / Custom" — use the custom path from settings
        if command is None:
            command = self.state.settings.custom_ide_path
            if not command:
                self._show_snackbar("No custom IDE path configured", is_error=True)
                return

        try:
            if sys.platform == "darwin" and ide_name in IDE_MACOS_APP_NAMES:
                subprocess.Popen(
                    ["open", "-a", IDE_MACOS_APP_NAMES[ide_name], str(project_path)]
                )
            else:
                subprocess.Popen([command, str(project_path)])
        except FileNotFoundError:
            self._show_snackbar(f"{ide_name} not found", is_error=True)

    async def _execute_build(
        self,
        open_folder: bool = False,
        open_ide: bool = False,
        open_terminal: bool = False,
    ) -> None:
        """Execute the project build after confirmation.

        Args:
            open_folder: Whether to open the project in the OS file manager after build.
            open_ide: Whether to open the project in the preferred IDE after build.
            open_terminal: Whether to open a terminal at the project root after build.
        """
        self.controls.progress_ring.visible = True
        self.controls.build_project_button.disabled = True
        self._set_status("Building project...", "info", update=True)

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
            github_root=Path(self.state.settings.default_github_root),
        )

        def _on_build_progress(msg: str) -> None:
            self._set_status(msg, "info", update=True)

        result = await AsyncExecutor.run(build_project, config, _on_build_progress)

        self.controls.progress_ring.visible = False
        self._update_build_button_state()

        if result.success:
            self._set_status(result.message, "success", update=False)
            self._show_snackbar(result.message, is_error=False)
            project_path = config.project_path / config.project_name
            if open_folder:
                self._open_in_file_manager(project_path)
            if open_ide:
                self._open_in_ide(project_path)
            if open_terminal:
                self._open_in_terminal(project_path)
        else:
            self._set_status("Build failed. See error details.", "error", update=False)

            def close_error_dialog(_=None):
                error_dialog.open = False
                self.state.active_dialog = None
                self.page.update()

            error_dialog = create_build_error_dialog(
                error_message=result.message,
                on_close_callback=close_error_dialog,
                is_dark_mode=self.state.is_dark_mode,
            )
            self.page.overlay.append(error_dialog)
            error_dialog.open = True
            self.state.active_dialog = close_error_dialog

        self.page.update()

    async def on_build_project(self, _: ft.ControlEvent) -> None:
        """Handle Build Project button click.

        Validates inputs and shows a confirmation dialog before building.
        """
        if not self._validate_inputs():
            return

        folder_count, file_count = self._count_folders_and_files(self.state.folders)

        async def on_confirm(_):
            open_folder = dialog.open_folder_checkbox.value
            open_ide = dialog.open_ide_checkbox.value
            open_terminal = dialog.open_terminal_checkbox.value
            dialog.open = False
            self.state.active_dialog = None
            self.page.update()
            await self._execute_build(
                open_folder=open_folder,
                open_ide=open_ide,
                open_terminal=open_terminal,
            )

        def on_cancel(_=None):
            dialog.open = False
            self.state.active_dialog = None
            self.page.update()

        build_config = BuildSummaryConfig(
            project_name=self.state.project_name,
            project_path=self.state.project_path,
            python_version=self.state.python_version,
            git_enabled=self.state.git_enabled,
            ui_project_enabled=self.state.ui_project_enabled,
            framework=self.state.framework if self.state.ui_project_enabled else None,
            other_project_enabled=self.state.other_project_enabled,
            project_type=self.state.project_type
            if self.state.other_project_enabled
            else None,
            starter_files=self.state.include_starter_files,
            folder_count=folder_count,
            file_count=file_count,
            packages=list(self.state.packages),
            folders=list(self.state.folders),
        )

        dialog = create_build_summary_dialog(
            config=build_config,
            on_build_callback=wrap_async(on_confirm),
            on_cancel_callback=on_cancel,
            is_dark_mode=self.state.is_dark_mode,
            ide_name=self.state.settings.preferred_ide,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.state.active_dialog = on_cancel
        self.page.update()

    async def _do_reset(self) -> None:
        """Perform the actual reset of all UI controls and state."""
        self.state.reset()

        self.controls.project_path_input.value = self.state.project_path
        self.controls.project_name_input.value = ""
        self.controls.python_version_dropdown.value = self.state.python_version
        self.controls.create_git_checkbox.value = self.state.git_enabled
        self.controls.include_starter_files_checkbox.value = True
        self.controls.ui_project_checkbox.value = False
        self.controls.ui_project_checkbox.label = UI_PROJECT_CHECKBOX_LABEL
        self.controls.other_projects_checkbox.value = False
        self.controls.other_projects_checkbox.label = OTHER_PROJECT_CHECKBOX_LABEL
        self.controls.auto_save_folder_changes.value = False

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
        self.controls.pypi_status_text.value = ""
        self.controls.check_pypi_button.disabled = True
        self.controls.path_preview_text.value = "\u00a0"
        self.controls.progress_ring.visible = False
        self.page.title = "UV Forge"

        self._set_validation_icon(self.controls.project_path_input, True)
        self._set_validation_icon(self.controls.project_name_input, None)
        self._update_build_button_state()

        self._reload_and_merge_templates()

        self._set_status("All fields reset.", "info", update=True)
        await self.controls.project_path_input.focus()

    async def on_reset(self, _: ft.ControlEvent) -> None:
        """Handle Reset button click — shows confirmation dialog first."""

        async def do_reset(_):
            dialog.open = False
            self.state.active_dialog = None
            self.page.update()
            await self._do_reset()

        def cancel(_=None):
            dialog.open = False
            self.state.active_dialog = None
            self.page.update()

        dialog = create_confirm_dialog(
            title="Reset All Settings?",
            message="This will clear all selections, packages, and folder changes.",
            confirm_label="Reset",
            on_confirm=wrap_async(do_reset),
            on_cancel=cancel,
            is_dark_mode=self.state.is_dark_mode,
            confirm_icon=ft.Icons.REFRESH,
        )
        self.state.active_dialog = cancel
        self.page.show_dialog(dialog)

    async def on_keyboard_event(self, e: ft.KeyboardEvent) -> None:
        """Handle keyboard shortcuts.

        Ctrl+Enter / Cmd+Enter — build project
        Ctrl+F / Cmd+F — add folder/file
        Ctrl+P / Cmd+P — add packages
        Ctrl+R / Cmd+R — reset
        Ctrl+/ / Cmd+/ — open help
        Escape — close dialog or exit (opens confirmation)
        """
        if e.key == "Enter" and (e.ctrl or e.meta):
            if (
                self.state.path_valid
                and self.state.name_valid
                and not self.controls.build_project_button.disabled
            ):
                await self.on_build_project(e)
        elif e.key == "F" and (e.ctrl or e.meta):
            await self.on_add_folder(e)
        elif e.key == "P" and (e.ctrl or e.meta):
            await self.on_add_package(e)
        elif e.key == "R" and (e.ctrl or e.meta):
            await self.on_reset(e)
        elif e.key == "/" and (e.ctrl or e.meta):
            await self.on_help_click(e)
        elif e.key == "Escape":
            if self.state.active_dialog:
                self.state.active_dialog()
            else:
                await self.on_exit(e)

    async def on_exit(self, _: ft.ControlEvent) -> None:
        """Handle Exit button click — shows confirmation dialog first."""

        async def do_exit(_):
            await self.page.window.close()

        def cancel(_=None):
            dialog.open = False
            self.state.active_dialog = None
            self.page.update()

        dialog = create_confirm_dialog(
            title="Exit Application?",
            message="Any unsaved configuration will be lost.",
            confirm_label="Exit",
            on_confirm=wrap_async(do_exit),
            on_cancel=cancel,
            is_dark_mode=self.state.is_dark_mode,
            confirm_icon=ft.Icons.EXIT_TO_APP,
        )
        self.state.active_dialog = cancel
        self.page.show_dialog(dialog)
