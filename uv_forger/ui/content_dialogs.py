"""Content and documentation dialog components.

Reusable, theme-aware dialogs for displaying and editing text content:
markdown viewers (help, about, cheat sheets), file editors, and
formatted text previews. These dialogs have no dependencies on the
main dialogs module and can be reused independently.

Functions
---------
  create_dialog_text_field ........ Editable monospace text field
  create_help_dialog .............. Scrollable markdown help viewer
  create_app_cheat_sheet_dialog ... Wide markdown app cheat sheet viewer
  create_about_dialog ............. Scrollable markdown about viewer
"""

from __future__ import annotations

import collections.abc

import flet as ft

from uv_forger.ui.theme_manager import get_theme_colors
from uv_forger.ui.ui_config import UIConfig


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


def create_file_preview_dialog(
    filename: str,
    content: str,
    source_label: str,
    on_close,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create a read-only preview dialog showing file content.

    Args:
        filename: Name of the file (e.g., "main.py").
        content: Content to display.
        source_label: Label indicating content source (e.g., "From boilerplate").
        on_close: Close button callback.
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog with read-only content preview.
    """
    colors = get_theme_colors(is_dark_mode)

    return ft.AlertDialog(
        modal=True,
        title=ft.Text(
            f"Preview: {filename}",
            size=UIConfig.DIALOG_TITLE_SIZE,
            color=colors["main_title"],
        ),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        source_label,
                        size=11,
                        italic=True,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Container(
                        content=ft.Text(
                            content if content else "(empty file)",
                            font_family="monospace",
                            size=12,
                            selectable=True,
                            color=colors.get("text"),
                        ),
                        bgcolor=colors.get(
                            "input_bg",
                            ft.Colors.GREY_900 if is_dark_mode else ft.Colors.GREY_100,
                        ),
                        border_radius=4,
                        padding=12,
                        expand=True,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=8,
            ),
            width=700,
            height=450,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        ),
        actions=[ft.TextButton("Close", on_click=on_close)],
        actions_alignment=ft.MainAxisAlignment.END,
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
