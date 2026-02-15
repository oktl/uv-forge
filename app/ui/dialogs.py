"""Reusable dialog components.

This module provides standardized, theme-aware dialog components
that maintain consistent styling and behavior across the application.
"""

import ast
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
) -> list[ft.Control]:
    """Create standardized dialog action buttons.

    Args:
        primary_label: Label for primary action button
        primary_callback: Callback for primary action
        cancel_callback: Callback for cancel button
        primary_icon: Optional icon for primary button

    Returns:
        List of action buttons [FilledButton, TextButton]
    """
    primary = ft.FilledButton(primary_label, on_click=primary_callback)
    if primary_icon:
        primary.icon = primary_icon
    return [primary, ft.TextButton("Cancel", on_click=cancel_callback)]


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


def _create_none_option_container(is_dark_mode: bool) -> list[ft.Control]:
    """Create 'None (Clear Selection)' radio option with divider.

    Args:
        is_dark_mode: Whether dark mode is active

    Returns:
        List containing the none option container and divider
    """
    return [
        ft.Container(
            content=ft.Radio(
                value="_none_",
                label="None (Clear Selection)",
                label_style=ft.TextStyle(size=13, italic=True),
            ),
            padding=ft.Padding(left=12, top=4, bottom=4, right=0),
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
) -> ft.AlertDialog:
    """Create a theme-aware dialog with scrollable markdown content.

    Args:
        title: Dialog title text
        content: Markdown content to display
        on_close: Close button callback
        page: The Flet page instance (needed to launch URLs)
        is_dark_mode: Whether dark mode is active
        width: Dialog content width in pixels

    Returns:
        Configured AlertDialog
    """
    colors = get_theme_colors(is_dark_mode)

    async def handle_link_click(e):
        await page.launch_url(e.data)

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
    content: str, on_close, page: ft.Page, is_dark_mode: bool
) -> ft.AlertDialog:
    """Create theme-aware help dialog with scrollable content."""
    return _create_markdown_dialog(
        "Help & Documentation", content, on_close, page, is_dark_mode
    )


def create_git_cheat_sheet_dialog(
    content: str, on_close, page: ft.Page, is_dark_mode: bool
) -> ft.AlertDialog:
    """Create theme-aware dialog displaying the Git cheat sheet."""
    return _create_markdown_dialog(
        "Git Cheat Sheet", content, on_close, page, is_dark_mode, width=900
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
    try:
        filename = Path(file_path).name
    except ValueError, TypeError:
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


def create_project_type_dialog(
    on_select_callback,
    on_close_callback,
    current_selection: str | None,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create dialog for selecting project type with rich tooltips and styling.

    Args:
        on_select_callback: Callback function(project_type) when Select is clicked
        on_close_callback: Callback function when Cancel is clicked
        current_selection: Currently selected project type (or None)
        is_dark_mode: Whether dark mode is active

    Returns:
        Configured AlertDialog for project type selection
    """
    from app.core.constants import PROJECT_TYPE_CATEGORIES, PROJECT_TYPE_PACKAGE_MAP

    colors = get_theme_colors(is_dark_mode)

    # Build radio buttons organized by category
    dialog_controls = []

    # "None (Clear Selection)" option at top
    dialog_controls.extend(_create_none_option_container(is_dark_mode))

    # Iterate through categories from constants
    category_names = list(PROJECT_TYPE_CATEGORIES.keys())
    for category_name, category_data in PROJECT_TYPE_CATEGORIES.items():
        # Get color attribute from ft.Colors dynamically
        light_color = getattr(
            ft.Colors, category_data["light_color"], ft.Colors.GREY_50
        )
        dark_color = getattr(ft.Colors, category_data["dark_color"], ft.Colors.GREY_900)
        bg_color = light_color if not is_dark_mode else dark_color

        # Category header with icon and background
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

        # Radio buttons for this category with tooltips
        for label, value, description in category_data["items"]:
            packages = PROJECT_TYPE_PACKAGE_MAP.get(value, [])
            tooltip_text = create_tooltip(description, packages)

            radio_container = ft.Container(
                content=ft.Radio(
                    value=value,
                    label=label,
                    label_style=ft.TextStyle(size=13),
                ),
                padding=ft.Padding(left=32, top=2, bottom=2, right=0),
                tooltip=tooltip_text,
                border_radius=4,
                ink=True,
            )
            dialog_controls.append(radio_container)

        # Add divider after each category except the last
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

    # Create radio group with all controls
    selected = current_selection or "_none_"
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
        """Handle Select button click."""
        selected_value = radio_group.value
        if selected_value == "_none_":
            on_select_callback(None)
        else:
            on_select_callback(selected_value)

    dialog = ft.AlertDialog(
        modal=True,
        title=_create_dialog_title(
            "Select Project Type", colors, ft.Icons.FOLDER_SPECIAL
        ),
        content=ft.Container(
            content=radio_group,
            width=520,
            height=550,
            padding=12,
        ),
        actions=_create_dialog_actions(
            "Select", on_select_click, on_close_callback, ft.Icons.CHECK_CIRCLE_OUTLINE
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog


def create_framework_dialog(
    on_select_callback,
    on_close_callback,
    current_selection: str | None,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create dialog for selecting UI framework with rich tooltips.

    Args:
        on_select_callback: Callback function(framework) when Select is clicked.
            Receives None if "None (Clear Selection)" is chosen.
        on_close_callback: Callback function when Cancel is clicked.
        current_selection: Currently selected framework (or None).
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog for framework selection.
    """
    from app.core.constants import FRAMEWORK_PACKAGE_MAP, UI_FRAMEWORK_DETAILS

    colors = get_theme_colors(is_dark_mode)

    dialog_controls = []

    # "None (Clear Selection)" option at top
    dialog_controls.extend(_create_none_option_container(is_dark_mode))

    # Radio buttons for each framework
    for label, value, description in UI_FRAMEWORK_DETAILS:
        package = FRAMEWORK_PACKAGE_MAP.get(value)
        tooltip_text = create_tooltip(description, package)

        radio_container = ft.Container(
            content=ft.Radio(
                value=value,
                label=label,
                label_style=ft.TextStyle(size=13),
            ),
            padding=ft.Padding(left=12, top=2, bottom=2, right=0),
            tooltip=tooltip_text,
            border_radius=4,
            ink=True,
        )
        dialog_controls.append(radio_container)

    # Create radio group
    selected = current_selection or "_none_"
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
        """Handle Select button click."""
        selected_value = radio_group.value
        if selected_value == "_none_":
            on_select_callback(None)
        else:
            on_select_callback(selected_value)

    dialog = ft.AlertDialog(
        modal=True,
        title=_create_dialog_title("Select UI Framework", colors, ft.Icons.WIDGETS),
        content=ft.Container(
            content=radio_group,
            width=420,
            height=420,
            padding=12,
        ),
        actions=_create_dialog_actions(
            "Select", on_select_click, on_close_callback, ft.Icons.CHECK_CIRCLE_OUTLINE
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog


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
        color=ft.Colors.ORANGE_600,
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
            try:
                parent_path = ast.literal_eval(parent_value)
            except ValueError, SyntaxError:
                parent_path = None

        on_add_callback(name, item_type, parent_path)

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
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_600, size=24),
                ft.Text(
                    "Build Failed",
                    size=UIConfig.DIALOG_TITLE_SIZE,
                    color=ft.Colors.RED_600,
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
                        border_color=ft.Colors.RED_400,
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

    Args:
        on_add_callback: Callback function(packages: list[str]) called with parsed names.
        on_close_callback: Callback function when Cancel is clicked.
        is_dark_mode: Whether dark mode is active.

    Returns:
        Configured AlertDialog for adding packages.
    """
    colors = get_theme_colors(is_dark_mode)

    warning_text = ft.Text(
        value="",
        color=ft.Colors.ORANGE_600,
        size=13,
        visible=False,
        weight=ft.FontWeight.W_500,
    )

    packages_field = ft.TextField(
        label="Packages",
        hint_text="One package per line, or comma-separated\ne.g.\nrequests\nhttpx>=0.25\ndjango",
        multiline=True,
        min_lines=4,
        max_lines=8,
        width=400,
        autofocus=True,
    )

    def on_add_click(e):
        raw = packages_field.value or ""
        # Split on newlines and commas, strip whitespace, drop empty tokens
        tokens = [t.strip() for part in raw.splitlines() for t in part.split(",")]
        packages = [t for t in tokens if t]
        if not packages:
            warning_text.value = "Enter at least one package name."
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
                        "Enter package names to add to the install list.\nEnsure each package is spelled correctly — uv will fail at build time if a package cannot be found.",
                        size=13,
                        color=colors.get("section_title"),
                    ),
                    ft.Container(height=8),
                    packages_field,
                    warning_text,
                ],
                tight=True,
            ),
            width=450,
            padding=UIConfig.DIALOG_CONTENT_PADDING,
        ),
        actions=_create_dialog_actions(
            "Add", on_add_click, on_close_callback, ft.Icons.ADD
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog


def create_build_summary_dialog(
    config: "BuildSummaryConfig",
    on_build_callback,
    on_cancel_callback,
    is_dark_mode: bool,
) -> ft.AlertDialog:
    """Create a confirmation dialog showing project summary before build.

    Args:
        config: BuildSummaryConfig with all project configuration details
        on_build_callback: Callback when Build is clicked
        on_cancel_callback: Callback when Cancel is clicked
        is_dark_mode: Whether dark mode is active

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

    rows.append(
        _create_summary_row(
            "Structure:", f"{config.folder_count} folders, {config.file_count} files"
        )
    )

    if config.packages:
        n = len(config.packages)
        rows.append(
            ft.Row(
                [
                    ft.Text("Packages:", weight=ft.FontWeight.BOLD, size=13, width=130),
                    ft.Column(
                        [
                            ft.Text(
                                f"{n} package{'s' if n != 1 else ''}",
                                size=13,
                                color=colors.get("section_title"),
                            ),
                            *[ft.Text(f"  • {pkg}", size=12) for pkg in config.packages],
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
            ft.TextStyle(color=ft.Colors.GREEN) if e.control.value else None
        )
        e.page.update()

    green = ft.TextStyle(color=ft.Colors.GREEN)

    open_folder_checkbox = ft.Checkbox(
        label="Open project folder after build",
        value=True,
        label_style=green,
        on_change=on_checkbox_change,
    )

    open_vscode_checkbox = ft.Checkbox(
        label="Open in VS Code",
        value=True,
        label_style=green,
        on_change=on_checkbox_change,
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=_create_dialog_title("Confirm Build", colors, ft.Icons.BUILD_CIRCLE),
        content=ft.Container(
            content=ft.Column(
                rows
                + [
                    ft.Divider(height=16, thickness=1),
                    open_folder_checkbox,
                    open_vscode_checkbox,
                ],
                tight=True,
                spacing=8,
            ),
            width=420,
            padding=20,
        ),
        actions=_create_dialog_actions(
            "Build", on_build_callback, on_cancel_callback, ft.Icons.ROCKET_LAUNCH
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    dialog.open_folder_checkbox = open_folder_checkbox
    dialog.open_vscode_checkbox = open_vscode_checkbox
    return dialog
