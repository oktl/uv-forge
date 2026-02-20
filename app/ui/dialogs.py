"""Reusable dialog components.

This module provides standardized, theme-aware dialog components
that maintain consistent styling and behavior across the application.
"""

import ast
import collections.abc
from pathlib import Path
from typing import TYPE_CHECKING

import flet as ft

from app.ui.theme_manager import get_theme_colors
from app.ui.ui_config import UIConfig

if TYPE_CHECKING:
    from app.core.models import BuildSummaryConfig


# ============================================================================
# Module-Level Helper Functions
# ============================================================================


def create_tooltip(description: str, packages: list[str] | str | None) -> str:
    """Create rich tooltip text with description and package info.

    Args:
        description: Main description text
        packages: Package name(s) - can be list, single string, or None

    Returns:
        Formatted tooltip string with description and package information
    """
    tooltip_lines = [description, ""]
    if isinstance(packages, list) and packages:
        tooltip_lines.append("📦 Packages:")
        for pkg in packages:
            tooltip_lines.append(f"  • {pkg}")
    elif isinstance(packages, str):
        tooltip_lines.append(f"📦 Package: {packages}")
    else:
        tooltip_lines.append("📦 No additional packages")
    return "\n".join(tooltip_lines)


def _create_dialog_title(
    text: str, colors: dict, icon: str | None = None, icon_size: int = 24
) -> ft.Control:
    """Create standardized dialog title with optional icon.

    Args:
        text: Title text
        colors: Theme colors dictionary
        icon: Optional icon name (Flet Icons constant)
        icon_size: Size of the icon in pixels

    Returns:
        Row with icon and text, or just Text if no icon
    """
    if icon:
        return ft.Row(
            [
                ft.Icon(icon, size=icon_size, color=colors["main_title"]),
                ft.Text(
                    text, size=UIConfig.DIALOG_TITLE_SIZE, color=colors["main_title"]
                ),
            ],
            spacing=8,
        )
    return ft.Text(text, size=UIConfig.DIALOG_TITLE_SIZE, color=colors["main_title"])


def _create_dialog_actions(
    primary_label: str,
    primary_callback,
    cancel_callback,
    primary_icon: str | None = None,
    is_dark_mode: bool = True,
    primary_autofocus: bool = True,
) -> list[ft.Control]:
    """Create standardized dialog action buttons.

    Both buttons show an obvious focused state (brighter shade + white border)
    matching the style used in confirmation dialogs.

    Args:
        primary_label: Label for primary action button
        primary_callback: Callback for primary action
        cancel_callback: Callback for cancel button
        primary_icon: Optional icon for primary button
        is_dark_mode: Whether dark mode is active
        primary_autofocus: Whether to autofocus the primary button (default True)

    Returns:
        List of action buttons [FilledButton, OutlinedButton]
    """
    primary = ft.FilledButton(
        primary_label,
        on_click=primary_callback,
        autofocus=primary_autofocus,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.BLUE_600,
                ft.ControlState.FOCUSED: ft.Colors.BLUE_400,
                ft.ControlState.HOVERED: ft.Colors.BLUE_500,
                ft.ControlState.PRESSED: ft.Colors.BLUE_700,
            },
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(0, ft.Colors.TRANSPARENT),
                ft.ControlState.FOCUSED: ft.BorderSide(2, ft.Colors.WHITE),
                ft.ControlState.HOVERED: ft.BorderSide(0, ft.Colors.TRANSPARENT),
            },
        ),
    )
    if primary_icon:
        primary.icon = primary_icon

    cancel_bg_focused = ft.Colors.GREY_700 if is_dark_mode else ft.Colors.GREY_300
    cancel = ft.OutlinedButton(
        "Cancel",
        on_click=cancel_callback,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                ft.ControlState.FOCUSED: cancel_bg_focused,
                ft.ControlState.HOVERED: cancel_bg_focused,
            },
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(1, ft.Colors.GREY_500),
                ft.ControlState.FOCUSED: ft.BorderSide(2, ft.Colors.WHITE),
                ft.ControlState.HOVERED: ft.BorderSide(1, ft.Colors.GREY_400),
            },
        ),
    )
    return [primary, cancel]


def _create_summary_row(label: str, value: str) -> ft.Row:
    """Create a row for build summary dialog.

    Args:
        label: Row label (e.g., "Project Name:")
        value: Row value

    Returns:
        Formatted Row with label and value
    """
    return ft.Row(
        [
            ft.Text(label, weight=ft.FontWeight.BOLD, size=13, width=130),
            ft.Text(value, size=13),
        ],
        spacing=8,
    )


def _build_project_tree_lines(config: BuildSummaryConfig) -> list[str]:
    """Build a Unicode box-drawing tree of the full project structure.

    Includes root-level files created by UV init (pyproject.toml, README.md, etc.),
    the app/ directory with __init__.py and main.py, and all template folders/files.

    Args:
        config: BuildSummaryConfig with project name, git_enabled, and folders.

    Returns:
        List of strings, one per tree line.
    """
    lines: list[str] = [f"{config.project_name}/"]

    # Separate root-level and app-level template folders
    root_folders = []
    app_folders = []
    for folder in config.folders:
        if isinstance(folder, dict) and folder.get("root_level", False):
            root_folders.append(folder)
        else:
            app_folders.append(folder)

    # Root-level files created by UV init
    root_files = [".python-version", "README.md", "pyproject.toml"]
    if config.git_enabled:
        root_files.insert(0, ".gitignore")

    # All root-level entries: files first, then app/, then root template folders
    root_entries: list[dict | str] = []
    root_entries.extend(root_files)
    root_entries.append("__app__")  # Sentinel for app/ directory
    root_entries.extend(root_folders)

    def _add_entries(
        entries: list[dict | str], prefix: str, parent_create_init: bool = True
    ) -> None:
        """Recursively add tree entries with box-drawing prefixes."""
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")

            if isinstance(entry, str):
                if entry == "__app__":
                    _add_app_dir(prefix, connector, child_prefix)
                else:
                    lines.append(f"{prefix}{connector}{entry}")
            elif isinstance(entry, dict):
                _add_folder(entry, prefix, connector, child_prefix)

    def _add_subfolder(
        name: str,
        parent_create_init: bool,
        prefix: str,
        connector: str,
        child_prefix: str,
    ) -> None:
        """Add a string subfolder (inherits parent's create_init)."""
        lines.append(f"{prefix}{connector}{name}/")
        if parent_create_init:
            lines.append(f"{child_prefix}└── __init__.py")

    def _add_folder(
        folder: dict, prefix: str, connector: str, child_prefix: str
    ) -> None:
        """Add a template folder and its contents to the tree."""
        name = folder.get("name", "")
        lines.append(f"{prefix}{connector}{name}/")

        create_init = folder.get("create_init", True)

        # Collect all children: __init__.py, files, then subfolders
        file_children: list[str] = []
        if create_init:
            file_children.append("__init__.py")
        file_children.extend(folder.get("files", []) or [])

        subfolders = folder.get("subfolders", []) or []
        total = len(file_children) + len(subfolders)
        idx = 0

        for file in file_children:
            idx += 1
            is_last = idx == total
            conn = "└── " if is_last else "├── "
            lines.append(f"{child_prefix}{conn}{file}")

        for sf in subfolders:
            idx += 1
            is_last = idx == total
            conn = "└── " if is_last else "├── "
            sf_child_prefix = child_prefix + ("    " if is_last else "│   ")
            if isinstance(sf, str):
                _add_subfolder(sf, create_init, child_prefix, conn, sf_child_prefix)
            elif isinstance(sf, dict):
                _add_folder(sf, child_prefix, conn, sf_child_prefix)

    def _add_app_dir(prefix: str, connector: str, child_prefix: str) -> None:
        """Add the app/ directory with __init__.py, main.py, and template folders."""
        lines.append(f"{prefix}{connector}app/")

        app_children: list[dict | str] = ["__init__.py", "main.py"]
        app_children.extend(app_folders)
        _add_entries(app_children, child_prefix)

    _add_entries(root_entries, "")
    return lines


def _build_project_tree_controls(config: BuildSummaryConfig) -> list[ft.Control]:
    """Build a list of Flet Row controls for the project tree with icons.

    Same structure as _build_project_tree_lines() but returns styled Flet
    controls with folder/file icons matching the Subfolders container.

    Args:
        config: BuildSummaryConfig with project name, git_enabled, and folders.

    Returns:
        List of Flet Row controls for display in the tree preview.
    """
    controls: list[ft.Control] = []

    def _tree_row(prefix: str, connector: str, name: str, is_folder: bool) -> ft.Row:
        icon = ft.Icons.FOLDER if is_folder else ft.Icons.INSERT_DRIVE_FILE
        icon_color = (
            UIConfig.COLOR_FOLDER_ICON if is_folder else UIConfig.COLOR_FILE_ICON
        )
        text_color = None if is_folder else UIConfig.COLOR_FILE_TEXT
        display = f"{name}/" if is_folder else name

        return ft.Row(
            [
                ft.Text(
                    f"{prefix}{connector}",
                    size=11,
                    font_family="monospace",
                    no_wrap=True,
                    color=ft.Colors.GREY_600,
                ),
                ft.Icon(icon, size=12, color=icon_color),
                ft.Text(
                    display,
                    size=11,
                    font_family="monospace",
                    no_wrap=True,
                    color=text_color,
                ),
            ],
            spacing=2,
            tight=True,
        )

    # Root line
    controls.append(
        ft.Row(
            [
                ft.Icon(ft.Icons.FOLDER, size=12, color=UIConfig.COLOR_FOLDER_ICON),
                ft.Text(
                    f"{config.project_name}/",
                    size=11,
                    font_family="monospace",
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=2,
            tight=True,
        )
    )

    # Separate root-level and app-level template folders
    root_folders = []
    app_folders = []
    for folder in config.folders:
        if isinstance(folder, dict) and folder.get("root_level", False):
            root_folders.append(folder)
        else:
            app_folders.append(folder)

    # Root-level files
    root_files = [".python-version", "README.md", "pyproject.toml"]
    if config.git_enabled:
        root_files.insert(0, ".gitignore")

    root_entries: list[dict | str] = []
    root_entries.extend(root_files)
    root_entries.append("__app__")
    root_entries.extend(root_folders)

    def _add_entries(entries: list[dict | str], prefix: str) -> None:
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")

            if isinstance(entry, str):
                if entry == "__app__":
                    _add_app_dir(prefix, connector, child_prefix)
                else:
                    controls.append(_tree_row(prefix, connector, entry, False))
            elif isinstance(entry, dict):
                _add_folder(entry, prefix, connector, child_prefix)

    def _add_subfolder(
        name: str,
        parent_create_init: bool,
        prefix: str,
        connector: str,
        child_prefix: str,
    ) -> None:
        controls.append(_tree_row(prefix, connector, name, True))
        if parent_create_init:
            controls.append(_tree_row(child_prefix, "└── ", "__init__.py", False))

    def _add_folder(
        folder: dict, prefix: str, connector: str, child_prefix: str
    ) -> None:
        name = folder.get("name", "")
        controls.append(_tree_row(prefix, connector, name, True))

        create_init = folder.get("create_init", True)
        file_children: list[str] = []
        if create_init:
            file_children.append("__init__.py")
        file_children.extend(folder.get("files", []) or [])

        subfolders = folder.get("subfolders", []) or []
        total = len(file_children) + len(subfolders)
        idx = 0

        for file in file_children:
            idx += 1
            is_last = idx == total
            conn = "└── " if is_last else "├── "
            controls.append(_tree_row(child_prefix, conn, file, False))

        for sf in subfolders:
            idx += 1
            is_last = idx == total
            conn = "└── " if is_last else "├── "
            sf_child_prefix = child_prefix + ("    " if is_last else "│   ")
            if isinstance(sf, str):
                _add_subfolder(sf, create_init, child_prefix, conn, sf_child_prefix)
            elif isinstance(sf, dict):
                _add_folder(sf, child_prefix, conn, sf_child_prefix)

    def _add_app_dir(prefix: str, connector: str, child_prefix: str) -> None:
        controls.append(_tree_row(prefix, connector, "app", True))
        app_children: list[dict | str] = ["__init__.py", "main.py"]
        app_children.extend(app_folders)
        _add_entries(app_children, child_prefix)

    _add_entries(root_entries, "")
    return controls


def _autofocus_selected_radio(controls: list[ft.Control], selected_value: str) -> None:
    """Set autofocus on the Radio whose value matches selected_value.

    Walks a flat list of Container controls, finds the Radio inside each,
    and sets autofocus=True on the one matching selected_value.
    """
    for control in controls:
        if not isinstance(control, ft.Container) or control.content is None:
            continue
        # Radio is either directly in the container or inside a Row
        radio = None
        if isinstance(control.content, ft.Radio):
            radio = control.content
        elif isinstance(control.content, ft.Row):
            for child in control.content.controls:
                if isinstance(child, ft.Radio):
                    radio = child
                    break
        if radio and radio.value == selected_value:
            radio.autofocus = True
            return


def _create_none_option_container(is_dark_mode: bool) -> list[ft.Control]:
    """Create 'None (Clear Selection)' radio option with divider.

    Styled distinctly from regular options (tinted bg + cancel icon) to
    signal that this is a clearing action rather than a normal selection.

    Args:
        is_dark_mode: Whether dark mode is active

    Returns:
        List containing the none option container and divider
    """
    bg_color = ft.Colors.GREY_700 if is_dark_mode else ft.Colors.GREY_200

    return [
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CANCEL, size=14, color=UIConfig.COLOR_ERROR),
                    ft.Radio(
                        value="_none_",
                        label="None (Clear Selection)",
                        label_style=ft.TextStyle(size=13, italic=True),
                    ),
                ],
                spacing=4,
            ),
            padding=ft.Padding(left=8, top=4, bottom=4, right=0),
            bgcolor=bg_color,
            tooltip="Clear selection and uncheck the checkbox",
            border_radius=4,
            ink=True,
        ),
        ft.Divider(
            height=1,
            thickness=1,
            color=ft.Colors.GREY_300 if not is_dark_mode else ft.Colors.GREY_700,
        ),
    ]


# ============================================================================
# Public Dialog Functions
# ============================================================================


def create_confirm_dialog(
    title: str,
    message: str,
    confirm_label: str,
    on_confirm,
    on_cancel,
    is_dark_mode: bool,
    confirm_icon: str | None = None,
) -> ft.AlertDialog:
    """Create a simple confirmation dialog with confirm and cancel actions.

    The confirm button receives autofocus so pressing Enter immediately triggers
    it. Both buttons show an obvious focused state when tabbing between them.

    Args:
        title: Dialog title text
        message: Body message to display
        confirm_label: Label for the confirm button
        on_confirm: Callback when confirm is clicked
        on_cancel: Callback when cancel is clicked
        is_dark_mode: Whether dark mode is active
        confirm_icon: Optional icon for the confirm button

    Returns:
        Configured AlertDialog
    """
    colors = get_theme_colors(is_dark_mode)

    # Confirm button — autofocused so Enter triggers it immediately.
    # Focused state uses a BRIGHTER shade (not darker) so it stands out
    # against the dark dialog background, plus a white border ring.
    confirm_btn = ft.FilledButton(
        confirm_label,
        on_click=on_confirm,
        autofocus=True,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.BLUE_600,
                ft.ControlState.FOCUSED: ft.Colors.BLUE_400,
                ft.ControlState.HOVERED: ft.Colors.BLUE_500,
                ft.ControlState.PRESSED: ft.Colors.BLUE_700,
            },
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(0, ft.Colors.TRANSPARENT),
                ft.ControlState.FOCUSED: ft.BorderSide(2, ft.Colors.WHITE),
                ft.ControlState.HOVERED: ft.BorderSide(0, ft.Colors.TRANSPARENT),
            },
        ),
    )
    if confirm_icon:
        confirm_btn.icon = confirm_icon

    # Cancel button — outlined at rest, fills with grey + white border when focused.
    cancel_bg_focused = ft.Colors.GREY_700 if is_dark_mode else ft.Colors.GREY_300
    cancel_btn = ft.OutlinedButton(
        "Cancel",
        on_click=on_cancel,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                ft.ControlState.FOCUSED: cancel_bg_focused,
                ft.ControlState.HOVERED: cancel_bg_focused,
            },
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(1, ft.Colors.GREY_500),
                ft.ControlState.FOCUSED: ft.BorderSide(2, ft.Colors.WHITE),
                ft.ControlState.HOVERED: ft.BorderSide(1, ft.Colors.GREY_400),
            },
        ),
    )

    return ft.AlertDialog(
        modal=True,
        title=_create_dialog_title(
            title, colors, icon=ft.Icons.WARNING_AMBER_ROUNDED, icon_size=20
        ),
        content=ft.Container(
            content=ft.Text(message, size=14, color=colors.get("section_title")),
            width=360,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        ),
        actions=[confirm_btn, cancel_btn],
        actions_alignment=ft.MainAxisAlignment.END,
    )


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


def _create_categorized_radio_dialog(
    title: str,
    icon: str,
    categories: dict,
    package_map: dict,
    on_select_callback,
    on_close_callback,
    current_selection: str | None,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create a categorized radio-button selection dialog.

    Shared implementation for project type and UI framework dialogs.

    Args:
        title: Dialog title text (e.g., "Select Project Type")
        icon: Flet Icons constant for the title
        categories: Category dict (e.g., PROJECT_TYPE_CATEGORIES)
        package_map: Package mapping dict for tooltip generation
        on_select_callback: Callback function(selected_value) when Select is clicked.
            Receives None if "None (Clear Selection)" is chosen.
        on_close_callback: Callback function when Cancel is clicked
        current_selection: Currently selected value (or None)
        is_dark_mode: Whether dark mode is active

    Returns:
        Configured AlertDialog for selection
    """
    colors = get_theme_colors(is_dark_mode)

    dialog_controls = []
    dialog_controls.extend(_create_none_option_container(is_dark_mode))

    category_names = list(categories.keys())
    for category_name, category_data in categories.items():
        light_color = getattr(
            ft.Colors, category_data["light_color"], ft.Colors.GREY_50
        )
        dark_color = getattr(ft.Colors, category_data["dark_color"], ft.Colors.GREY_900)
        bg_color = light_color if not is_dark_mode else dark_color

        dialog_controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text(category_data["icon"], size=16),
                        ft.Text(
                            category_name,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=colors["section_title"],
                        ),
                    ],
                    spacing=8,
                ),
                bgcolor=bg_color,
                padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                border_radius=6,
                margin=ft.Margin(top=8, bottom=4, left=0, right=0),
            )
        )

        selected_bgcolor = ft.Colors.BLUE_900 if is_dark_mode else ft.Colors.BLUE_50
        for label, value, description in category_data["items"]:
            packages = package_map.get(value) or []
            tooltip_text = create_tooltip(description, packages)

            dialog_controls.append(
                ft.Container(
                    content=ft.Radio(
                        value=value,
                        label=label,
                        label_style=ft.TextStyle(size=13),
                    ),
                    padding=ft.Padding(left=32, top=2, bottom=2, right=0),
                    tooltip=tooltip_text,
                    border_radius=4,
                    ink=True,
                    bgcolor=selected_bgcolor if value == current_selection else None,
                )
            )

        if category_name != category_names[-1]:
            dialog_controls.append(
                ft.Divider(
                    height=1,
                    thickness=1,
                    color=ft.Colors.GREY_300
                    if not is_dark_mode
                    else ft.Colors.GREY_700,
                )
            )

    selected = current_selection or "_none_"
    _autofocus_selected_radio(dialog_controls, selected)

    radio_column = ft.Column(
        controls=dialog_controls,
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
    )

    radio_group = ft.RadioGroup(
        content=radio_column,
        value=selected,
    )

    def on_select_click(e):
        selected_value = radio_group.value
        on_select_callback(None if selected_value == "_none_" else selected_value)

    return ft.AlertDialog(
        modal=True,
        title=_create_dialog_title(title, colors, icon),
        content=ft.Container(
            content=radio_group,
            width=520,
            height=550,
            padding=12,
        ),
        actions=_create_dialog_actions(
            "Select",
            on_select_click,
            on_close_callback,
            ft.Icons.CHECK_CIRCLE_OUTLINE,
            is_dark_mode,
            primary_autofocus=False,
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )


def create_project_type_dialog(
    on_select_callback,
    on_close_callback,
    current_selection: str | None,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create dialog for selecting project type with rich tooltips and styling.

    Args:
        on_select_callback: Callback receiving the selected project type string, or None if cleared.
        on_close_callback: Callback when Cancel is clicked.
        current_selection: Currently selected project type, or None.
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog with categorized radio selection.
    """
    from app.core.constants import PROJECT_TYPE_PACKAGE_MAP
    from app.ui.dialog_data import PROJECT_TYPE_CATEGORIES

    return _create_categorized_radio_dialog(
        title="Select Project Type",
        icon=ft.Icons.FOLDER_SPECIAL,
        categories=PROJECT_TYPE_CATEGORIES,
        package_map=PROJECT_TYPE_PACKAGE_MAP,
        on_select_callback=on_select_callback,
        on_close_callback=on_close_callback,
        current_selection=current_selection,
        is_dark_mode=is_dark_mode,
    )


def create_framework_dialog(
    on_select_callback,
    on_close_callback,
    current_selection: str | None,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create dialog for selecting UI framework with rich tooltips.

    Args:
        on_select_callback: Callback receiving the selected framework string, or None if cleared.
        on_close_callback: Callback when Cancel is clicked.
        current_selection: Currently selected framework, or None.
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog with categorized radio selection.
    """
    from app.core.constants import FRAMEWORK_PACKAGE_MAP
    from app.ui.dialog_data import UI_FRAMEWORK_CATEGORIES

    return _create_categorized_radio_dialog(
        title="Select UI Framework",
        icon=ft.Icons.WIDGETS,
        categories=UI_FRAMEWORK_CATEGORIES,
        package_map=FRAMEWORK_PACKAGE_MAP,
        on_select_callback=on_select_callback,
        on_close_callback=on_close_callback,
        current_selection=current_selection,
        is_dark_mode=is_dark_mode,
    )


def create_add_item_dialog(
    on_add_callback,
    on_close_callback,
    parent_folders: list[dict],
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create dialog for adding a folder or file.

    Args:
        on_add_callback: Callback function(name, item_type, parent_path) when Add is clicked
        on_close_callback: Callback function when Cancel is clicked
        parent_folders: List of parent folder options [{"label": "core/", "path": [0]}, ...]
        is_dark_mode: Whether dark mode is active

    Returns:
        Configured AlertDialog for adding items
    """
    from app.core.validator import validate_folder_name

    colors = get_theme_colors(is_dark_mode)

    # Warning banner for validation errors (defined first so it can be referenced)
    warning_text = ft.Text(
        value="",
        color=UIConfig.COLOR_WARNING,
        size=13,
        visible=False,
        weight=ft.FontWeight.W_500,
    )

    def on_name_change(e):
        """Validate name input in real-time."""
        name = e.control.value if e.control.value else ""

        if not name:
            # Empty input - hide warning
            warning_text.value = ""
            warning_text.visible = False
        else:
            # Validate the name
            is_valid, error_msg = validate_folder_name(name)
            if is_valid:
                # Valid input - clear warning
                warning_text.value = ""
                warning_text.visible = False
            else:
                # Invalid input - show warning
                warning_text.value = error_msg
                warning_text.visible = True

        e.page.update()

    # Input fields
    name_field = ft.TextField(
        label="Name",
        hint_text="Enter folder or file name",
        width=400,
        autofocus=True,
        on_change=on_name_change,
    )

    # Type selection
    type_radio = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="folder", label="Folder"),
                ft.Radio(value="file", label="File"),
            ]
        ),
        value="folder",
    )

    # Parent folder dropdown
    parent_options = [ft.dropdown.Option(key="root", text="Root")]
    for folder in parent_folders:
        parent_options.append(
            ft.dropdown.Option(key=str(folder["path"]), text=folder["label"])
        )

    parent_dropdown = ft.Dropdown(
        label="Parent Location",
        hint_text="Select parent folder",
        options=parent_options,
        value="root",
        width=400,
        dense=True,
        text_size=13,
        menu_height=300,
    )

    def on_add_click(e):
        """Handle Add button click with validation."""
        name = name_field.value

        # Validate name before proceeding
        if not name:
            warning_text.value = "Name cannot be empty"
            warning_text.visible = True
            e.page.update()
            return

        is_valid, error_msg = validate_folder_name(name)
        if not is_valid:
            warning_text.value = error_msg
            warning_text.visible = True
            e.page.update()
            return

        # Name is valid, proceed with adding
        item_type = type_radio.value
        parent_value = parent_dropdown.value

        # Parse parent path
        if parent_value == "root":
            parent_path = None
        else:
            _parse_errors = (ValueError, SyntaxError)
            try:
                parent_path = ast.literal_eval(parent_value)
            except _parse_errors:
                parent_path = None

        on_add_callback(name, item_type, parent_path)

    name_field.on_submit = on_add_click

    dialog = ft.AlertDialog(
        modal=True,
        title=_create_dialog_title(
            "Add File or Folder", colors, icon=ft.Icons.ADD_CIRCLE_OUTLINE
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    name_field,
                    warning_text,
                    ft.Container(height=10),
                    ft.Text("Type:", size=14),
                    type_radio,
                    ft.Container(height=10),
                    parent_dropdown,
                ],
                tight=True,
            ),
            width=450,
            padding=20,
        ),
        actions=[
            ft.TextButton("Add", on_click=on_add_click),
            ft.TextButton("Cancel", on_click=on_close_callback),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Store warning text reference on dialog for callback access
    dialog.warning_text = warning_text

    return dialog


def create_build_error_dialog(
    error_message: str,
    on_close_callback,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create a dialog displaying a build failure with its full error output.

    Args:
        error_message: Full error detail string from the failed build.
        on_close_callback: Callback when the Close button is clicked.
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog showing the build error.
    """
    colors = get_theme_colors(is_dark_mode)

    return ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=UIConfig.COLOR_ERROR, size=24),
                ft.Text(
                    "Build Failed",
                    size=UIConfig.DIALOG_TITLE_SIZE,
                    color=UIConfig.COLOR_ERROR,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=8,
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "The build did not complete. Full error details:",
                        size=13,
                        color=colors.get("section_title"),
                    ),
                    ft.Container(height=8),
                    ft.TextField(
                        value=error_message,
                        read_only=True,
                        multiline=True,
                        min_lines=6,
                        max_lines=12,
                        text_style=ft.TextStyle(size=12, font_family="monospace"),
                        border_color=UIConfig.COLOR_ERROR,
                        width=500,
                    ),
                ],
                tight=True,
            ),
            width=540,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        ),
        actions=[ft.TextButton("Close", on_click=on_close_callback)],
        actions_alignment=ft.MainAxisAlignment.END,
    )


def create_add_packages_dialog(
    on_add_callback,
    on_close_callback,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create dialog for adding one or more packages to the install list.

    Includes an opt-in "Verify on PyPI" button that checks each package
    against the PyPI registry asynchronously. Results are informational
    only — the Add button works regardless of check results.

    Args:
        on_add_callback: Callback function(packages: list[str]) called with parsed names.
        on_close_callback: Callback function when Cancel is clicked.
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog for adding packages.
    """
    import asyncio

    from app.core.pypi_checker import (
        check_pypi_availability,
        extract_package_name,
        validate_package_format,
    )

    colors = get_theme_colors(is_dark_mode)

    warning_text = ft.Text(
        value="",
        color=UIConfig.COLOR_WARNING,
        size=13,
        visible=False,
        weight=ft.FontWeight.W_500,
    )

    packages_field = ft.TextField(
        label="Packages",
        hint_text="One package per line, or comma-separated\ne.g.\nrequests\nhttpx>=0.25\ndjango[postgres]\npytest==8.0",
        multiline=True,
        min_lines=4,
        max_lines=8,
        width=400,
        autofocus=True,
    )

    # Results area for PyPI verification — hidden until first verify click
    results_column = ft.Column(
        scroll=ft.ScrollMode.AUTO, height=120, visible=False, spacing=4
    )

    def _parse_packages() -> list[str]:
        """Parse package specs from the text field."""
        raw = packages_field.value or ""
        tokens = [
            token.strip() for part in raw.splitlines() for token in part.split(",")
        ]
        return [token for token in tokens if token]

    def _make_result_row(icon: str, icon_color: str, pkg: str, message: str) -> ft.Row:
        return ft.Row(
            [
                ft.Icon(icon, color=icon_color, size=16),
                ft.Text(pkg, size=12, weight=ft.FontWeight.W_500),
                ft.Text(f"— {message}", size=12, color=ft.Colors.GREY_500),
            ],
            spacing=6,
            tight=True,
        )

    def _make_checking_row(pkg: str) -> ft.Row:
        return ft.Row(
            [
                ft.ProgressRing(width=14, height=14, stroke_width=2),
                ft.Text(pkg, size=12, weight=ft.FontWeight.W_500),
                ft.Text("— Checking...", size=12, color=ft.Colors.GREY_500),
            ],
            spacing=6,
            tight=True,
        )

    async def _verify_packages(e):
        """Check each package against PyPI."""
        packages = _parse_packages()
        if not packages:
            warning_text.value = "Enter at least one package name to verify."
            warning_text.visible = True
            e.page.update()
            return

        warning_text.visible = False
        results_column.controls.clear()
        results_column.visible = True

        # First pass: client-side format validation + show checking spinners
        valid_packages: list[tuple[int, str]] = []  # (index, spec)
        for pkg in packages:
            fmt_error = validate_package_format(pkg)
            if fmt_error:
                results_column.controls.append(
                    _make_result_row(
                        ft.Icons.CANCEL, UIConfig.COLOR_ERROR, pkg, fmt_error
                    )
                )
            else:
                idx = len(results_column.controls)
                results_column.controls.append(_make_checking_row(pkg))
                valid_packages.append((idx, pkg))

        e.page.update()

        # Second pass: async PyPI lookups
        for idx, pkg in valid_packages:
            bare_name = extract_package_name(pkg)
            result = await check_pypi_availability(bare_name)

            if result is False:
                # Package exists on PyPI — that's good for an install
                row = _make_result_row(
                    ft.Icons.CHECK_CIRCLE,
                    UIConfig.COLOR_SUCCESS,
                    pkg,
                    "Found on PyPI",
                )
            elif result is True:
                # Package NOT on PyPI — warn user
                row = _make_result_row(
                    ft.Icons.ERROR_OUTLINE,
                    UIConfig.COLOR_WARNING,
                    pkg,
                    "Not found on PyPI",
                )
            else:
                # Network error
                row = _make_result_row(
                    ft.Icons.WIFI_OFF,
                    UIConfig.COLOR_WARNING,
                    pkg,
                    "Could not check",
                )

            results_column.controls[idx] = row
            e.page.update()

    def _wrap_verify(e):
        asyncio.create_task(_verify_packages(e))

    verify_button = ft.Button(
        "Verify on PyPI",
        icon=ft.Icons.TRAVEL_EXPLORE,
        on_click=_wrap_verify,
    )

    def on_add_click(e):
        packages = _parse_packages()
        if not packages:
            warning_text.value = "Enter at least one package name."
            warning_text.visible = True
            e.page.update()
            return

        # Client-side format validation before adding
        errors = []
        for pkg in packages:
            fmt_error = validate_package_format(pkg)
            if fmt_error:
                errors.append(fmt_error)

        if errors:
            warning_text.value = "\n".join(errors)
            warning_text.visible = True
            e.page.update()
            return

        warning_text.visible = False
        on_add_callback(packages)

    dialog = ft.AlertDialog(
        modal=True,
        title=_create_dialog_title(
            "Add Packages", colors, icon=ft.Icons.ADD_CIRCLE_OUTLINE
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Enter package names to add to the install list.\n"
                        "Version specifiers (>=, ==, <) and extras "
                        "([postgres], [dev]) are supported.",
                        size=13,
                        color=colors.get("section_title"),
                    ),
                    ft.Container(height=8),
                    packages_field,
                    ft.Row([verify_button], spacing=8),
                    warning_text,
                    results_column,
                ],
                tight=True,
                spacing=8,
            ),
            width=450,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        ),
        actions=_create_dialog_actions(
            "Add",
            on_add_click,
            on_close_callback,
            ft.Icons.ADD,
            is_dark_mode,
            primary_autofocus=False,
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Expose for testing
    dialog.verify_button = verify_button
    dialog.results_column = results_column

    return dialog


def create_build_summary_dialog(
    config: BuildSummaryConfig,
    on_build_callback,
    on_cancel_callback,
    is_dark_mode: bool,
    ide_name: str = "VS Code",
) -> ft.AlertDialog:
    """Create a confirmation dialog showing project summary before build.

    Args:
        config: BuildSummaryConfig with all project configuration details
        on_build_callback: Callback when Build is clicked
        on_cancel_callback: Callback when Cancel is clicked
        is_dark_mode: Whether dark mode is active
        ide_name: Display name of the preferred IDE for the open-in checkbox.

    Returns:
        Configured AlertDialog with project summary
    """
    colors = get_theme_colors(is_dark_mode)

    rows = [
        _create_summary_row("Project Name:", config.project_name),
        _create_summary_row("Location:", config.project_path),
        _create_summary_row("Python Version:", config.python_version),
        _create_summary_row("Git Init:", "Yes" if config.git_enabled else "No"),
        _create_summary_row("Starter Files:", "Yes" if config.starter_files else "No"),
    ]

    if config.framework:
        rows.append(_create_summary_row("UI Framework:", config.framework))
    if config.project_type:
        type_name = config.project_type.replace("_", " ").title()
        rows.append(_create_summary_row("Project Type:", type_name))

    if config.author_name or config.author_email:
        author_display = config.author_name
        if config.author_email:
            author_display += (
                f" <{config.author_email}>" if author_display else config.author_email
            )
        rows.append(_create_summary_row("Author:", author_display))
    if config.description:
        rows.append(_create_summary_row("Description:", config.description))
    if config.license_type:
        rows.append(_create_summary_row("License:", config.license_type))

    # Collapsible project tree preview
    tree_controls = _build_project_tree_controls(config)
    tree_container = ft.Container(
        content=ft.Column(
            tree_controls,
            scroll=ft.ScrollMode.AUTO,
            spacing=1,
            tight=True,
        ),
        width=460,
        height=200,
        padding=ft.Padding(left=8, top=4, right=4, bottom=4),
    )

    structure_label = f"{config.folder_count} folders, {config.file_count} files"
    tree_tile = ft.ExpansionTile(
        title=ft.Text("Structure", weight=ft.FontWeight.BOLD, size=13),
        subtitle=ft.Text(structure_label, size=12),
        controls=[tree_container],
        expanded=False,
        tile_padding=ft.Padding(left=0, top=0, right=0, bottom=0),
        controls_padding=ft.Padding(left=0, top=0, right=0, bottom=0),
    )
    rows.append(tree_tile)

    if config.packages:
        count = len(config.packages)
        rows.append(
            ft.Row(
                [
                    ft.Text("Packages:", weight=ft.FontWeight.BOLD, size=13, width=130),
                    ft.Column(
                        [
                            ft.Text(
                                f"{count} package{'s' if count != 1 else ''}",
                                size=13,
                                color=colors.get("section_title"),
                            ),
                            *[
                                ft.Text(f"  • {pkg}", size=12)
                                for pkg in config.packages
                            ],
                        ],
                        spacing=2,
                        tight=True,
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )
    else:
        rows.append(_create_summary_row("Packages:", "None"))

    def on_checkbox_change(e):
        e.control.label_style = (
            ft.TextStyle(color=UIConfig.COLOR_CHECKBOX_ACTIVE)
            if e.control.value
            else None
        )
        e.page.update()

    green = ft.TextStyle(color=UIConfig.COLOR_CHECKBOX_ACTIVE)

    open_folder_checkbox = ft.Checkbox(
        label="Open project folder after build",
        value=False,
        on_change=on_checkbox_change,
    )

    open_vscode_checkbox = ft.Checkbox(
        label=f"Open in {ide_name}",
        value=True,
        label_style=green,
        on_change=on_checkbox_change,
    )

    open_folder_row = ft.Row(
        [
            ft.Icon(ft.Icons.FOLDER_OPEN, size=16, color=UIConfig.COLOR_FOLDER_ICON),
            open_folder_checkbox,
        ],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    open_vscode_row = ft.Row(
        [
            ft.Icon(ft.Icons.CODE, size=16, color=UIConfig.COLOR_INFO),
            open_vscode_checkbox,
        ],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    open_terminal_checkbox = ft.Checkbox(
        label="Open terminal at project root",
        value=False,
        on_change=on_checkbox_change,
    )

    open_terminal_row = ft.Row(
        [
            ft.Icon(ft.Icons.TERMINAL, size=16, color=ft.Colors.GREY_400),
            open_terminal_checkbox,
        ],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    post_build_command_field = ft.TextField(
        value=config.post_build_command,
        hint_text="e.g. uv run pre-commit install",
        width=390,
        text_size=13,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        disabled=not config.post_build_command_enabled,
    )

    post_build_enabled = config.post_build_command_enabled
    post_build_checkbox = ft.Checkbox(
        label="Run post-build command",
        value=post_build_enabled,
        label_style=green if post_build_enabled else None,
        on_change=on_checkbox_change,
    )

    def on_post_build_toggle(e):
        post_build_command_field.disabled = not e.control.value
        e.control.label_style = (
            ft.TextStyle(color=UIConfig.COLOR_CHECKBOX_ACTIVE)
            if e.control.value
            else None
        )
        e.page.update()

    post_build_checkbox.on_change = on_post_build_toggle

    post_build_row = ft.Row(
        [
            ft.Icon(ft.Icons.PLAY_ARROW, size=16, color=ft.Colors.GREY_400),
            post_build_checkbox,
        ],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    post_build_command_row = ft.Row(
        [
            ft.Container(width=22),
            ft.Text("Run:", size=12, color=colors.get("section_title")),
            post_build_command_field,
        ],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=_create_dialog_title("Confirm Build", colors, ft.Icons.BUILD_CIRCLE),
        content=ft.Container(
            content=ft.Column(
                rows
                + [
                    ft.Divider(height=16, thickness=1),
                    ft.Text(
                        "After Build",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=colors["section_title"],
                    ),
                    open_folder_row,
                    open_vscode_row,
                    open_terminal_row,
                    post_build_row,
                    post_build_command_row,
                ],
                tight=True,
                spacing=8,
            ),
            width=500,
            padding=20,
        ),
        actions=_create_dialog_actions(
            "Build",
            on_build_callback,
            on_cancel_callback,
            ft.Icons.ROCKET_LAUNCH,
            is_dark_mode,
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    dialog.open_folder_checkbox = open_folder_checkbox
    dialog.open_ide_checkbox = open_vscode_checkbox
    # Keep legacy alias for backward compatibility in tests
    dialog.open_vscode_checkbox = open_vscode_checkbox
    dialog.open_terminal_checkbox = open_terminal_checkbox
    dialog.post_build_checkbox = post_build_checkbox
    dialog.post_build_command_field = post_build_command_field
    return dialog


def _parse_log_location(location: str) -> tuple[str, int] | None:
    """Extract module path and line number from a log location segment.

    Args:
        location: Location string like ``app.core.state:load:42``.

    Returns:
        Tuple of (dotted module path, line number) or None if unparseable.
    """
    parts = location.strip().split(":")
    if len(parts) >= 3:
        try:
            return parts[0], int(parts[-1])
        except ValueError:
            return None
    return None


def _parse_log_line(
    line: str,
    is_dark_mode: bool,
    on_location_click: collections.abc.Callable[[str, int], None] | None = None,
) -> ft.Row:
    """Parse a single log line into a colored Flet Row.

    Expected format: ``{time} | {level} | {name}:{function}:{line} - {message}``

    Args:
        line: Raw log line string.
        is_dark_mode: Whether dark mode is active.
        on_location_click: Optional callback ``(module_path, line_number)`` invoked
            when the location segment is clicked.

    Returns:
        A Row with coloured Text segments for each part of the log line.
    """
    level_colors = {
        "DEBUG": ft.Colors.GREY_600,
        "INFO": ft.Colors.GREY_400 if is_dark_mode else ft.Colors.GREY_700,
        "SUCCESS": ft.Colors.GREEN_400,
        "WARNING": ft.Colors.AMBER_400,
        "ERROR": ft.Colors.RED_400,
        "CRITICAL": ft.Colors.RED_300,
    }

    text_kwargs = {"font_family": "monospace", "size": 11, "no_wrap": True}

    parts = line.split(" | ", 2)
    if len(parts) != 3:
        return ft.Row(
            [ft.Text(line, color=ft.Colors.GREY_600, **text_kwargs)],
            spacing=0,
            tight=True,
        )

    timestamp, level_raw, rest = parts
    level = level_raw.strip()
    color = level_colors.get(level, ft.Colors.GREY_600)
    weight = ft.FontWeight.BOLD if level == "CRITICAL" else None

    loc_msg = rest.split(" - ", 1)
    location = loc_msg[0] if len(loc_msg) == 2 else rest
    message = loc_msg[1] if len(loc_msg) == 2 else ""

    # Build the location control — clickable if a callback is provided
    loc_parsed = _parse_log_location(location) if on_location_click else None
    if loc_parsed and on_location_click:
        module_path, line_no = loc_parsed

        loc_text = ft.Text(location, color=ft.Colors.CYAN_400, **text_kwargs)

        def _on_hover(e, txt=loc_text):
            txt.text_decorations = (
                ft.TextDecoration.UNDERLINE
                if e.data == "true"
                else ft.TextDecoration.NONE
            )
            txt.update()

        def _on_click(_e, mp=module_path, ln=line_no):
            on_location_click(mp, ln)

        location_control = ft.GestureDetector(
            content=loc_text,
            on_hover=_on_hover,
            on_tap=_on_click,
            mouse_cursor=ft.MouseCursor.CLICK,
        )
    else:
        location_control = ft.Text(location, color=ft.Colors.CYAN_400, **text_kwargs)

    controls = [
        ft.Text(timestamp, color=ft.Colors.GREY_600, **text_kwargs),
        ft.Text(" | ", color=ft.Colors.GREY_700, **text_kwargs),
        ft.Text(level_raw, color=color, weight=weight, **text_kwargs),
        ft.Text(" | ", color=ft.Colors.GREY_700, **text_kwargs),
        location_control,
    ]
    if message:
        controls.append(ft.Text(" - ", color=ft.Colors.GREY_700, **text_kwargs))
        controls.append(ft.Text(message, color=color, weight=weight, **text_kwargs))

    return ft.Row(controls, spacing=0, tight=True)


def create_log_viewer_dialog(
    log_content: str,
    on_close_callback,
    is_dark_mode: bool,
    on_location_click: collections.abc.Callable[[str, int], None] | None = None,
) -> ft.AlertDialog:
    """Create a dialog displaying application log content with coloured lines.

    Args:
        log_content: Raw log file text.
        on_close_callback: Callback when the Close button is clicked.
        is_dark_mode: Whether dark mode is active.
        on_location_click: Optional callback ``(module_path, line_number)`` invoked
            when a clickable location segment is tapped.  When provided, location
            segments are rendered as hover-underline links.

    Returns:
        Configured AlertDialog with parsed, coloured log rows.
    """
    colors = get_theme_colors(is_dark_mode)

    parsed_rows = [
        _parse_log_line(line, is_dark_mode, on_location_click=on_location_click)
        for line in log_content.splitlines()
        if line.strip()
    ]

    if not parsed_rows:
        parsed_rows = [ft.Text("(empty log)", italic=True, color=ft.Colors.GREY_500)]

    log_text_ref = log_content

    def on_copy_click(e):
        import subprocess
        import sys

        try:
            if sys.platform == "darwin":
                subprocess.run(["pbcopy"], input=log_text_ref.encode(), check=True)
            elif sys.platform == "win32":
                subprocess.run(["clip"], input=log_text_ref.encode(), check=True)
            else:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=log_text_ref.encode(),
                    check=True,
                )
            copy_btn.text = "Copied!"
        except FileNotFoundError, subprocess.CalledProcessError:
            copy_btn.text = "Copy failed"
        e.page.update()

    copy_btn = ft.TextButton("Copy to Clipboard", on_click=on_copy_click)

    return ft.AlertDialog(
        modal=True,
        title=_create_dialog_title("Log Viewer", colors, icon=ft.Icons.ARTICLE),
        content=ft.Container(
            content=ft.Column(
                controls=parsed_rows,
                scroll=ft.ScrollMode.AUTO,
                auto_scroll=True,
            ),
            width=UIConfig.DIALOG_WIDTH,
            height=UIConfig.DIALOG_HEIGHT - 100,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        ),
        actions=[copy_btn, ft.TextButton("Close", on_click=on_close_callback)],
        actions_alignment=ft.MainAxisAlignment.END,
    )


def create_metadata_dialog(
    state,
    on_save_callback: collections.abc.Callable,
    on_close_callback: collections.abc.Callable,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create a dialog for editing project metadata fields.

    Args:
        state: Current AppState instance to populate fields from.
        on_save_callback: Callback receiving (author_name, author_email, description, license_type).
        on_close_callback: Callback when Cancel is clicked.
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog for editing metadata.
    """
    from app.core.constants import LICENSE_TYPES

    colors = get_theme_colors(is_dark_mode)
    label_style = ft.TextStyle(size=13, color=colors["section_title"])

    field_width = 410

    author_name_field = ft.TextField(
        label="Author Name",
        value=state.author_name,
        width=field_width,
        label_style=label_style,
        autofocus=True,
    )

    author_email_field = ft.TextField(
        label="Author Email",
        value=state.author_email,
        width=field_width,
        label_style=label_style,
    )

    description_field = ft.TextField(
        label="Description",
        value=state.description,
        width=field_width,
        multiline=True,
        min_lines=2,
        max_lines=3,
        label_style=label_style,
    )

    license_options = [ft.dropdown.Option(key="", text="(None)")] + [
        ft.dropdown.Option(lt) for lt in LICENSE_TYPES
    ]
    license_dropdown = ft.Dropdown(
        label="License",
        value=state.license_type,
        options=license_options,
        width=field_width,
        label_style=label_style,
    )

    def on_save_click(_):
        on_save_callback(
            author_name_field.value or "",
            author_email_field.value or "",
            description_field.value or "",
            license_dropdown.value or "",
        )

    return ft.AlertDialog(
        modal=True,
        title=_create_dialog_title(
            "Project Metadata", colors, icon=ft.Icons.DESCRIPTION
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Set metadata fields for pyproject.toml.",
                        size=13,
                        color=colors.get("section_title"),
                    ),
                    ft.Container(height=8),
                    author_name_field,
                    author_email_field,
                    ft.Divider(height=16, color=colors.get("section_border")),
                    description_field,
                    license_dropdown,
                ],
                tight=True,
                spacing=10,
            ),
            width=450,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        ),
        actions=_create_dialog_actions(
            "Save",
            on_save_click,
            on_close_callback,
            ft.Icons.SAVE,
            is_dark_mode,
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )


def create_settings_dialog(
    settings,
    on_save_callback: collections.abc.Callable,
    on_close_callback: collections.abc.Callable,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create a dialog for editing user preferences.

    Args:
        settings: Current AppSettings instance to populate fields from.
        on_save_callback: Callback receiving the updated AppSettings on save.
        on_close_callback: Callback when Cancel is clicked or dialog dismissed.
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog for editing settings.
    """
    from app.core.constants import PYTHON_VERSIONS, SUPPORTED_IDES

    colors = get_theme_colors(is_dark_mode)

    label_style = ft.TextStyle(size=13, color=colors["section_title"])
    field_width = 460

    # --- Default project path ---
    project_path_field = ft.TextField(
        label="Default Project Path",
        value=settings.default_project_path,
        expand=True,
        label_style=label_style,
    )

    async def browse_project_path(_):
        from app.ui.file_picker import select_folder

        result = await select_folder("Select Default Project Path")
        if result:
            project_path_field.value = result
            project_path_field.update()

    project_path_row = ft.Row(
        [
            project_path_field,
            ft.IconButton(
                icon=ft.Icons.FOLDER_OPEN,
                icon_size=UIConfig.ICON_SIZE_DEFAULT,
                tooltip="Browse",
                on_click=browse_project_path,
            ),
        ],
        spacing=4,
    )

    # --- Default GitHub root ---
    github_root_field = ft.TextField(
        label="Default GitHub Root",
        value=settings.default_github_root,
        expand=True,
        label_style=label_style,
    )

    async def browse_github_root(_):
        from app.ui.file_picker import select_folder

        result = await select_folder("Select Default GitHub Root")
        if result:
            github_root_field.value = result
            github_root_field.update()

    github_root_row = ft.Row(
        [
            github_root_field,
            ft.IconButton(
                icon=ft.Icons.FOLDER_OPEN,
                icon_size=UIConfig.ICON_SIZE_DEFAULT,
                tooltip="Browse",
                on_click=browse_github_root,
            ),
        ],
        spacing=4,
    )

    # --- Default Python version ---
    python_version_dropdown = ft.Dropdown(
        label="Default Python Version",
        value=settings.default_python_version,
        options=[ft.dropdown.Option(v) for v in PYTHON_VERSIONS],
        width=field_width,
        label_style=label_style,
    )

    # --- Preferred IDE ---
    ide_names = list(SUPPORTED_IDES.keys())
    ide_dropdown = ft.Dropdown(
        label="Preferred IDE",
        value=settings.preferred_ide
        if settings.preferred_ide in ide_names
        else ide_names[0],
        options=[ft.dropdown.Option(name) for name in ide_names],
        width=field_width,
        label_style=label_style,
    )

    custom_ide_field = ft.TextField(
        label="Custom IDE Executable Path",
        value=settings.custom_ide_path,
        visible=settings.preferred_ide == "Other / Custom",
        width=field_width,
        label_style=label_style,
        hint_text="/usr/local/bin/my-editor",
    )

    def on_ide_change(e):
        custom_ide_field.visible = ide_dropdown.value == "Other / Custom"
        custom_ide_field.update()

    ide_dropdown.on_change = on_ide_change

    # --- Git init default ---
    git_checkbox = ft.Checkbox(
        label="Enable Git init by default",
        value=settings.git_enabled_default,
    )

    # --- Author defaults ---
    author_name_field = ft.TextField(
        label="Default Author Name",
        value=settings.default_author_name,
        width=field_width,
        label_style=label_style,
    )

    author_email_field = ft.TextField(
        label="Default Author Email",
        value=settings.default_author_email,
        width=field_width,
        label_style=label_style,
    )

    # --- Post-build command ---
    post_build_enabled_checkbox = ft.Checkbox(
        label="Enable post-build command",
        value=settings.post_build_command_enabled,
    )

    post_build_command_field = ft.TextField(
        label="Post-build Command",
        value=settings.post_build_command,
        hint_text="uv run pre-commit install && uv run pytest",
        width=field_width,
        label_style=label_style,
    )

    post_build_packages_field = ft.TextField(
        label="Required Packages",
        value=settings.post_build_packages,
        hint_text="pre-commit, ruff",
        width=field_width,
        label_style=label_style,
    )

    # --- Save handler ---
    def on_save_click(_):
        from app.core.settings_manager import AppSettings

        updated = AppSettings(
            default_project_path=project_path_field.value
            or settings.default_project_path,
            default_github_root=github_root_field.value or settings.default_github_root,
            default_python_version=python_version_dropdown.value
            or settings.default_python_version,
            preferred_ide=ide_dropdown.value or settings.preferred_ide,
            custom_ide_path=custom_ide_field.value or "",
            git_enabled_default=git_checkbox.value,
            default_author_name=author_name_field.value or "",
            default_author_email=author_email_field.value or "",
            post_build_command=post_build_command_field.value or "",
            post_build_command_enabled=post_build_enabled_checkbox.value,
            post_build_packages=post_build_packages_field.value or "",
        )
        on_save_callback(updated)

    dialog = ft.AlertDialog(
        modal=True,
        title=_create_dialog_title("Settings", colors, icon=ft.Icons.SETTINGS),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Configure default values for new projects.",
                        size=13,
                        color=colors.get("section_title"),
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        "Paths",
                        weight=ft.FontWeight.W_600,
                        size=14,
                        color=colors["main_title"],
                    ),
                    project_path_row,
                    github_root_row,
                    ft.Divider(height=16, color=colors.get("section_border")),
                    ft.Text(
                        "Defaults",
                        weight=ft.FontWeight.W_600,
                        size=14,
                        color=colors["main_title"],
                    ),
                    ft.Row([python_version_dropdown], spacing=16),
                    git_checkbox,
                    ft.Divider(height=16, color=colors.get("section_border")),
                    ft.Text(
                        "Author",
                        weight=ft.FontWeight.W_600,
                        size=14,
                        color=colors["main_title"],
                    ),
                    author_name_field,
                    author_email_field,
                    ft.Divider(height=16, color=colors.get("section_border")),
                    ft.Text(
                        "IDE",
                        weight=ft.FontWeight.W_600,
                        size=14,
                        color=colors["main_title"],
                    ),
                    ide_dropdown,
                    custom_ide_field,
                    ft.Divider(height=16, color=colors.get("section_border")),
                    ft.Text(
                        "Automation",
                        weight=ft.FontWeight.W_600,
                        size=14,
                        color=colors["main_title"],
                    ),
                    post_build_enabled_checkbox,
                    post_build_command_field,
                    post_build_packages_field,
                ],
                tight=True,
                spacing=10,
            ),
            width=500,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        ),
        actions=_create_dialog_actions(
            "Save",
            on_save_click,
            on_close_callback,
            ft.Icons.SAVE,
            is_dark_mode,
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog


def create_history_dialog(
    entries: list,
    on_restore_callback: collections.abc.Callable,
    on_close_callback: collections.abc.Callable,
    on_clear_callback: collections.abc.Callable,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create a dialog showing recent project history.

    Args:
        entries: List of ProjectHistoryEntry objects, newest first.
        on_restore_callback: Callback receiving the selected entry on restore.
        on_close_callback: Callback when Cancel is clicked or dialog dismissed.
        on_clear_callback: Callback to clear all history entries.
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog for browsing and restoring recent projects.
    """
    colors = get_theme_colors(is_dark_mode)
    selected_index: dict[str, int | None] = {"value": None}

    row_containers: list[ft.Container] = []

    def _highlight(idx: int) -> None:
        for i, container in enumerate(row_containers):
            if i == idx:
                container.bgcolor = (
                    ft.Colors.BLUE_900 if is_dark_mode else ft.Colors.BLUE_100
                )
                container.border = ft.Border.all(1, ft.Colors.BLUE_400)
            else:
                container.bgcolor = None
                container.border = ft.Border.all(
                    1, ft.Colors.GREY_700 if is_dark_mode else ft.Colors.GREY_300
                )

    def _on_row_click(idx: int):
        def handler(_):
            selected_index["value"] = idx
            _highlight(idx)
            restore_btn.disabled = False
            for c in row_containers:
                c.update()
            restore_btn.update()

        return handler

    def _on_restore(_):
        idx = selected_index["value"]
        if idx is not None and idx < len(entries):
            on_restore_callback(entries[idx])

    restore_btn = ft.FilledButton(
        "Restore",
        icon=ft.Icons.RESTORE,
        disabled=True,
        on_click=_on_restore,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.BLUE_600,
                ft.ControlState.FOCUSED: ft.Colors.BLUE_400,
                ft.ControlState.HOVERED: ft.Colors.BLUE_500,
                ft.ControlState.PRESSED: ft.Colors.BLUE_700,
                ft.ControlState.DISABLED: ft.Colors.GREY_700,
            },
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(0, ft.Colors.TRANSPARENT),
                ft.ControlState.FOCUSED: ft.BorderSide(2, ft.Colors.WHITE),
            },
        ),
    )

    if not entries:
        content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.HISTORY,
                        size=48,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Text(
                        "No recent projects",
                        size=16,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Projects will appear here after a successful build.",
                        size=13,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            width=500,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        )
    else:
        for i, entry in enumerate(entries):
            # Build badge text
            badges = []
            if entry.ui_project_enabled and entry.framework:
                badges.append(entry.framework)
            if entry.other_project_enabled and entry.project_type:
                badges.append(entry.project_type)

            badge_row = []
            for badge_text in badges:
                badge_row.append(
                    ft.Container(
                        content=ft.Text(badge_text, size=11, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE_700,
                        border_radius=4,
                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                    )
                )
            if entry.packages:
                badge_row.append(
                    ft.Text(
                        f"{len(entry.packages)} pkg{'s' if len(entry.packages) != 1 else ''}",
                        size=11,
                        color=ft.Colors.GREY_500,
                        italic=True,
                    )
                )

            # Parse built_at for display
            try:
                dt = __import__("datetime").datetime.fromisoformat(entry.built_at)
                time_str = dt.strftime("%b %d, %H:%M")
            except ValueError, AttributeError:
                time_str = entry.built_at[:16] if entry.built_at else ""

            row = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    entry.project_name,
                                    weight=ft.FontWeight.W_600,
                                    size=14,
                                    color=colors["main_title"],
                                    expand=True,
                                ),
                                ft.Text(
                                    time_str,
                                    size=11,
                                    color=ft.Colors.GREY_500,
                                ),
                            ],
                        ),
                        ft.Text(
                            entry.project_path,
                            size=12,
                            color=ft.Colors.GREY_500,
                        ),
                        ft.Row(badge_row, spacing=6) if badge_row else ft.Container(),
                    ],
                    spacing=2,
                    tight=True,
                ),
                border=ft.Border.all(
                    1, ft.Colors.GREY_700 if is_dark_mode else ft.Colors.GREY_300
                ),
                border_radius=6,
                padding=10,
                on_click=_on_row_click(i),
                ink=True,
            )
            row_containers.append(row)

        content = ft.Container(
            content=ft.Column(
                row_containers,
                spacing=6,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=500,
            height=min(len(entries) * 90, 400),
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        )

    cancel_bg_focused = ft.Colors.GREY_700 if is_dark_mode else ft.Colors.GREY_300
    cancel_btn = ft.OutlinedButton(
        "Cancel",
        on_click=on_close_callback,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                ft.ControlState.FOCUSED: cancel_bg_focused,
                ft.ControlState.HOVERED: cancel_bg_focused,
            },
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(1, ft.Colors.GREY_500),
                ft.ControlState.FOCUSED: ft.BorderSide(2, ft.Colors.WHITE),
            },
        ),
    )

    actions = [restore_btn, cancel_btn] if entries else [cancel_btn]
    if entries:
        clear_btn = ft.TextButton(
            "Clear History",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=on_clear_callback,
            style=ft.ButtonStyle(color=ft.Colors.RED_400),
        )
        actions.insert(0, clear_btn)

    dialog = ft.AlertDialog(
        modal=True,
        title=_create_dialog_title("Recent Projects", colors, icon=ft.Icons.HISTORY),
        content=content,
        actions=actions,
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog
