"""Handlers for theme toggle, help dialog, git cheat sheet, and about dialog."""

import asyncio

import flet as ft

from app.core.constants import ABOUT_FILE, GIT_CHEAT_SHEET_FILE, HELP_FILE
from app.ui.dialogs import (
    create_about_dialog,
    create_git_cheat_sheet_dialog,
    create_help_dialog,
)
from app.ui.theme_manager import get_theme_colors


class FeatureHandlersMixin:
    """Mixin for UI feature handlers: theme, help, git cheat sheet.

    Expects HandlerBase helpers available via self.
    """

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

        for title_text in self.controls.section_titles:
            title_text.color = colors["section_title"]
        for container in self.controls.section_containers:
            container.border = ft.Border.all(1, colors["section_border"])

        self.page.bottom_appbar.bgcolor = colors["bottom_bar"]
        self.page.update()

    async def on_help_click(self, _: ft.ControlEvent) -> None:
        """Handle Help button click."""
        try:
            help_text = HELP_FILE.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError) as e:
            help_text = """# UV Project Creator Help

**Error**: Could not load help file.

This application helps you create new Python projects using UV.

For more information, visit: https://docs.astral.sh/uv/
"""
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

    async def on_about_click(self, _: ft.ControlEvent) -> None:
        """Handle About button click.

        Internal links (app://help, app://git-cheat-sheet) close the About
        dialog and open the corresponding dialog directly.
        """
        try:
            content = ABOUT_FILE.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError) as e:
            content = "# UV Project Creator\n\nError: Could not load about file."
            self._set_status(
                f"Warning: About file not found ({e})", "error", update=False
            )

        def close_dialog(_=None):
            about_dialog.open = False
            self.page.update()

        def handle_internal_link(path: str) -> None:
            close_dialog()
            if path == "help":
                asyncio.create_task(self.on_help_click(None))
            elif path == "git-cheat-sheet":
                asyncio.create_task(self.on_git_cheat_sheet_click(None))

        about_dialog = create_about_dialog(
            content,
            close_dialog,
            self.page,
            self.state.is_dark_mode,
            on_internal_link=handle_internal_link,
        )

        self.page.overlay.append(about_dialog)
        about_dialog.open = True
        self.page.update()
