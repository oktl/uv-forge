"""Content and documentation dialog components.

Reusable, theme-aware dialogs for displaying and editing text content:
markdown viewers (help, about, cheat sheets), file editors, and
formatted text previews. These dialogs have no dependencies on the
main dialogs module and can be reused independently.

Functions
---------
  create_dialog_text_field ........ Editable monospace text field
  create_help_dialog .............. Scrollable markdown help viewer
  create_git_cheat_sheet_dialog ... Wide markdown cheat sheet viewer
  create_app_cheat_sheet_dialog ... Wide markdown app cheat sheet viewer
  create_about_dialog ............. Scrollable markdown about viewer
  create_edit_file_dialog ......... File content editor with save
  create_preview_formatted_dialog . Formatted text preview with save
"""

from __future__ import annotations

import collections.abc
from pathlib import Path

import flet as ft

from app.ui.theme_manager import get_theme_colors
from app.ui.ui_config import UIConfig


def create_dialog_text_field(content: str, is_dark_mode: bool) -> ft.TextField:
    """Return an editable, preformatted text field.

    Args:
        content: Text content for the field
        is_dark_mode: Whether dark mode is active

    Returns:
        Configured TextField with theme-aware styling
    """
    colors = get_theme_colors(is_dark_mode)
    return ft.TextField(
        value=content,
        multiline=True,
        min_lines=20,
        max_lines=40,
        border_color=colors["section_border"],
        text_style=ft.TextStyle(
            font_family="monospace",
            size=13,
        ),
        expand=True,
    )


def _create_markdown_dialog(
    title: str,
    content: str,
    on_close,
    page: ft.Page,
    is_dark_mode: bool,
    width: int = UIConfig.DIALOG_WIDTH,
    on_internal_link: collections.abc.Callable[[str], None] | None = None,
) -> ft.AlertDialog:
    """Create a theme-aware dialog with scrollable markdown content.

    Args:
        title: Dialog title text
        content: Markdown content to display
        on_close: Close button callback
        page: The Flet page instance (needed to launch URLs)
        is_dark_mode: Whether dark mode is active
        width: Dialog content width in pixels
        on_internal_link: Optional callback for app:// links

    Returns:
        Configured AlertDialog
    """
    colors = get_theme_colors(is_dark_mode)

    async def handle_link_click(e):
        url = e.data
        if url.startswith("app://") and on_internal_link is not None:
            on_internal_link(url[len("app://") :])
        else:
            await page.launch_url(url)

    return ft.AlertDialog(
        modal=True,
        title=ft.Text(
            title,
            size=UIConfig.DIALOG_TITLE_SIZE,
            color=colors["main_title"],
        ),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Markdown(
                        content,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        on_tap_link=handle_link_click,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            width=width,
            height=UIConfig.DIALOG_HEIGHT,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        ),
        actions=[ft.TextButton("Close", on_click=on_close)],
        actions_alignment=ft.MainAxisAlignment.END,
    )


def create_help_dialog(
    content: str,
    on_close,
    page: ft.Page,
    is_dark_mode: bool,
    on_internal_link: collections.abc.Callable[[str], None] | None = None,
) -> ft.AlertDialog:
    """Create theme-aware help dialog with scrollable content.

    Args:
        content: Markdown help text to display.
        on_close: Close button callback.
        page: The Flet page instance (needed to launch URLs).
        is_dark_mode: Whether dark mode is active.
        on_internal_link: Optional callback for app:// links.

    Returns:
        Configured AlertDialog with scrollable markdown content.
    """
    return _create_markdown_dialog(
        "Help & Documentation",
        content,
        on_close,
        page,
        is_dark_mode,
        on_internal_link=on_internal_link,
    )


def create_git_cheat_sheet_dialog(
    content: str,
    on_close,
    page: ft.Page,
    is_dark_mode: bool,
    on_internal_link: collections.abc.Callable[[str], None] | None = None,
) -> ft.AlertDialog:
    """Create theme-aware dialog displaying the Git cheat sheet.

    Args:
        content: Markdown cheat sheet text to display.
        on_close: Close button callback.
        page: The Flet page instance (needed to launch URLs).
        is_dark_mode: Whether dark mode is active.
        on_internal_link: Optional callback for app:// links.

    Returns:
        Configured AlertDialog with scrollable markdown content.
    """
    return _create_markdown_dialog(
        "Git Cheat Sheet",
        content,
        on_close,
        page,
        is_dark_mode,
        width=900,
        on_internal_link=on_internal_link,
    )


def create_app_cheat_sheet_dialog(
    content: str,
    on_close,
    page: ft.Page,
    is_dark_mode: bool,
    on_internal_link: collections.abc.Callable[[str], None] | None = None,
) -> ft.AlertDialog:
    """Create theme-aware dialog displaying the App cheat sheet.

    Args:
        content: Markdown cheat sheet text to display.
        on_close: Close button callback.
        page: The Flet page instance (needed to launch URLs).
        is_dark_mode: Whether dark mode is active.
        on_internal_link: Optional callback for app:// links.

    Returns:
        Configured AlertDialog with scrollable markdown content.
    """
    return _create_markdown_dialog(
        "App Cheat Sheet",
        content,
        on_close,
        page,
        is_dark_mode,
        width=900,
        on_internal_link=on_internal_link,
    )


def create_about_dialog(
    content: str,
    on_close,
    page: ft.Page,
    is_dark_mode: bool,
    on_internal_link: collections.abc.Callable[[str], None] | None = None,
) -> ft.AlertDialog:
    """Create theme-aware About dialog with optional internal link navigation.

    Args:
        content: Markdown about text to display.
        on_close: Close button callback.
        page: The Flet page instance (needed to launch URLs).
        is_dark_mode: Whether dark mode is active.
        on_internal_link: Optional callback for app:// links.

    Returns:
        Configured AlertDialog with scrollable markdown content.
    """
    return _create_markdown_dialog(
        "About",
        content,
        on_close,
        page,
        is_dark_mode,
        on_internal_link=on_internal_link,
    )


def create_edit_file_dialog(
    content: str, file_path: str, on_save, on_close, is_dark_mode: bool
) -> ft.AlertDialog:
    """Create theme-aware file editing dialog with save functionality.

    Args:
        content: File content to edit
        file_path: Path to the file being edited
        on_save: Save button callback (receives edited text and file_path)
        on_close: Close button callback
        is_dark_mode: Whether dark mode is active

    Returns:
        Configured AlertDialog with editable text field
    """
    colors = get_theme_colors(is_dark_mode)

    # Extract filename from path for display - add safety check
    _path_errors = (ValueError, TypeError)
    try:
        filename = Path(file_path).name
    except _path_errors:
        filename = str(file_path)

    # Create editable text field
    text_field = create_dialog_text_field(content, is_dark_mode)

    def on_save_click(e):
        """Handle save button click."""
        on_save(text_field.value, file_path)

    return ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"Edit File: {filename}",
            size=UIConfig.DIALOG_TITLE_SIZE,
            color=colors["main_title"],
        ),
        content=ft.Container(
            content=ft.Row(
                controls=[text_field],
                expand=True,
            ),
            width=UIConfig.DIALOG_WIDTH,
            height=UIConfig.DIALOG_HEIGHT,
        ),
        actions=[
            ft.TextButton("Save", on_click=on_save_click),
            ft.TextButton("Cancel", on_click=on_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


def create_preview_formatted_dialog(
    content: str,
    provider_name: str,
    on_save_to_file,
    on_close,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create theme-aware preview dialog for formatted transcript.

    Args:
        content: Formatted transcript text to preview
        provider_name: Name of AI provider used for formatting
        on_save_to_file: Save to File button callback (receives edited text)
        on_close: Close button callback
        is_dark_mode: Whether dark mode is active

    Returns:
        Configured AlertDialog with editable preview
    """
    colors = get_theme_colors(is_dark_mode)
    text_field = create_dialog_text_field(content, is_dark_mode)

    def on_save_click(e):
        """Handle save button click."""
        on_save_to_file(text_field.value)

    return ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"Preview Formatted Transcript ({provider_name.title()})",
            size=UIConfig.DIALOG_TITLE_SIZE,
            color=colors["main_title"],
        ),
        content=ft.Container(
            content=ft.Row(
                controls=[text_field],
                expand=True,
            ),
            width=UIConfig.DIALOG_WIDTH,
            height=UIConfig.DIALOG_HEIGHT,
        ),
        actions=[
            ft.TextButton("Save to File", on_click=on_save_click),
            ft.TextButton("Close", on_click=on_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
