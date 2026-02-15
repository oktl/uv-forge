"""UI components and layout construction for the Project Creator.

This module defines the Controls class for storing UI control references and
the build_main_view function for constructing the application's visual layout.
"""

from typing import TYPE_CHECKING

import flet as ft

from app.core.constants import PYTHON_VERSIONS
from app.ui.theme_manager import get_theme_colors
from app.ui.ui_config import UIConfig

if TYPE_CHECKING:
    from app.core.state import AppState


class Controls:
    """Container for reference to controls.

    Stores references to interactive UI elements for access by event handlers.

    Attributes:
        project_path_label: Label for project path input.
        project_path_input: TextField for entering project path.
        copy_path_button: IconButton to copy the full project path to clipboard.
        browse_button: Button to open directory picker.
        warning_banner: Text for displaying warnings.
        project_name_label: Label for project name input.
        project_name_input: TextField for entering project name.
        python_version_label: Label for Python version dropdown.
        python_version_dropdown: Dropdown for selecting Python version.
        create_git_checkbox: Checkbox for git initialization option.
        ui_project_checkbox: Checkbox for UI project option.
        other_projects_checkbox: Checkbox for Other Project types option.
        app_subfolders_label: Label for folder display.
        subfolders_container: Container showing folder structure.
        auto_save_folder_changes: Checkbox for auto-save option.
        add_folder_button: Button to add a folder.
        remove_folder_button: Button to remove a folder.
        packages_label: Label for packages display.
        packages_container: Container showing packages list.
        add_package_button: Button to open the add-packages dialog.
        remove_package_button: Button to remove the selected package.
        clear_packages_button: Button to remove all packages from the list.
        path_preview_text: Small greyed text showing the resolved project path as the user types.
        include_starter_files_checkbox: Checkbox to include starter files in template.
        status_text: Text for displaying status messages.
        build_project_button: Button to build the project.
        reset_button: Button to reset all fields.
        exit_button: Button to exit the application.
        progress_ring: Progress indicator for async operations.
        help_button: Button to show help dialog.
        git_cheat_sheet_button: Button to show Git cheat sheet dialog.
        theme_toggle_button: Button to toggle theme.
        main_title: Main title text.
        section_titles: List of section title texts.
        section_containers: List of section containers.
    """

    def __init__(self) -> None:
        self.project_path_label: ft.Text
        self.project_path_input: ft.TextField
        self.copy_path_button: ft.IconButton
        self.browse_button: ft.Button
        self.warning_banner: ft.Text
        self.project_name_label: ft.Text
        self.project_name_input: ft.TextField
        self.python_version_label: ft.Text
        self.python_version_dropdown: ft.Dropdown
        self.create_git_checkbox: ft.Checkbox
        self.ui_project_checkbox: ft.Checkbox
        self.other_projects_checkbox: ft.Checkbox
        self.app_subfolders_label: ft.Text
        self.subfolders_container: ft.Container
        self.auto_save_folder_changes: ft.Checkbox
        self.add_folder_button: ft.Button
        self.remove_folder_button: ft.Button
        self.packages_label: ft.Text
        self.packages_container: ft.Container
        self.add_package_button: ft.Button
        self.remove_package_button: ft.Button
        self.clear_packages_button: ft.Button
        self.include_starter_files_checkbox: ft.Checkbox
        self.path_preview_text: ft.Text
        self.status_icon: ft.Icon
        self.status_text: ft.Text
        self.build_project_button: ft.Button
        self.reset_button: ft.Button
        self.exit_button: ft.Button
        self.progress_ring: ft.ProgressRing
        self.help_button: ft.IconButton
        self.git_cheat_sheet_button: ft.IconButton
        self.theme_toggle_button: ft.IconButton
        self.main_title: ft.Text
        self.section_titles: list[ft.Text]
        self.section_containers: list[ft.Container]


def create_section_box(
    title: str, content: list[ft.Control], is_dark: bool = False
) -> tuple[ft.Container, ft.Text]:
    """Create a bordered section with a title and content.

    Returns:
        Tuple of (container, title_text) for theme update access.
    """
    colors = get_theme_colors(is_dark)
    title_text = ft.Text(
        title,
        size=UIConfig.SECTION_TITLE_SIZE,
        weight=ft.FontWeight.W_600,
        color=colors["section_title"],
    )
    container = ft.Container(
        content=ft.Column(
            controls=[
                title_text,
                *content,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=UIConfig.SPACING_SMALL,
        ),
        border=ft.Border.all(UIConfig.BORDER_WIDTH_THIN, colors["section_border"]),
        border_radius=UIConfig.BORDER_RADIUS_DEFAULT,
        padding=UIConfig.PADDING_SECTION,
        width=UIConfig.SECTION_WIDTH,
    )
    return container, title_text


def create_controls(state: "AppState", colors: dict) -> Controls:
    """Create all UI controls for the application.

    Args:
        state: The application state instance.
        colors: Theme colors dictionary.

    Returns:
        Controls instance with all UI elements initialized.
    """
    controls = Controls()

    # Icon buttons
    controls.theme_toggle_button = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if state.is_dark_mode else ft.Icons.DARK_MODE,
        icon_size=UIConfig.ICON_SIZE_DEFAULT,
        tooltip="Toggle dark/light mode",
    )

    controls.git_cheat_sheet_button = ft.IconButton(
        icon=ft.Icons.MENU_BOOK,
        icon_size=UIConfig.ICON_SIZE_DEFAULT,
        tooltip="Git Cheat Sheet",
    )

    controls.help_button = ft.IconButton(
        icon=ft.Icons.HELP_OUTLINE,
        icon_size=UIConfig.ICON_SIZE_DEFAULT,
        tooltip="Help & Documentation",
    )

    # Project path controls
    controls.project_path_label = ft.Text("Create Project In")
    controls.project_path_input = ft.TextField(
        value=state.project_path,
        hint_text="Project Root Directory",
        expand=True,
        autofocus=True,
    )

    controls.copy_path_button = ft.IconButton(
        icon=ft.Icons.CONTENT_COPY,
        icon_size=UIConfig.ICON_SIZE_DEFAULT,
        tooltip="Copy full project path to clipboard",
        disabled=True,
        opacity=0.4,
    )

    controls.browse_button = ft.Button("Browse...")

    controls.warning_banner = ft.Text(
        "",
        color=UIConfig.COLOR_WARNING,
        weight=ft.FontWeight.BOLD,
        size=14,
    )

    # Project name controls
    controls.project_name_label = ft.Text("New Project Name")

    controls.project_name_input = ft.TextField(
        hint_text="Enter project name...",
        expand=True,
        border_color=UIConfig.COLOR_INFO,
        border_width=1,
    )

    controls.path_preview_text = ft.Text(
        "",
        size=12,
        color=ft.Colors.GREY_500,
        italic=True,
    )

    # Python version controls
    controls.python_version_label = ft.Text("Python Version")
    controls.python_version_dropdown = ft.Dropdown(
        value=state.python_version,
        options=[ft.dropdown.Option(v) for v in PYTHON_VERSIONS],
        tooltip="Choose a version, default is 3.14",
        expand=True,
        border_color=UIConfig.COLOR_INFO,
    )

    # Checkbox controls
    controls.create_git_checkbox = ft.Checkbox(
        label="Initialize Git Repository",
        value=state.git_enabled,
        tooltip="Choose if you want a git repository\nDefault is yes",
    )

    controls.include_starter_files_checkbox = ft.Checkbox(
        label="Include Starter Files",
        value=state.include_starter_files,
        label_style=ft.TextStyle(color=UIConfig.COLOR_CHECKBOX_ACTIVE)
        if state.include_starter_files
        else None,
        tooltip="Create template files with boilerplate starter content.\nDefault is no – only folders and __init__.py are created.",
    )

    controls.ui_project_checkbox = ft.Checkbox(
        label="Create UI Project",
        value=state.ui_project_enabled,
        tooltip="Choose if you're creating a UI.\nDefault is no.\nOpens a scrolling dialog to choose options.\nCan be combined with Other Project Type",
    )
    controls.other_projects_checkbox = ft.Checkbox(
        label="Create Other Project Type",
        tooltip="Create other project types\nlike Django, data science, web scraping, etc...\nOpens a scrolling dialog to choose options.\nCan be combined with UI Project",
    )

    # Folder management controls
    controls.app_subfolders_label = ft.Text("App Subfolders:")
    controls.subfolders_container = ft.Container(
        content=ft.Column(
            controls=[],  # Populated dynamically from template data
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        border=ft.Border.all(1, ft.Colors.GREY_700),
        border_radius=4,
        padding=10,
        height=UIConfig.SUBFOLDERS_HEIGHT,
        width=UIConfig.SPLIT_CONTAINER_WIDTH,
    )

    controls.auto_save_folder_changes = ft.Checkbox(
        label="Auto-save folder changes to config",
        value=state.auto_save_folders,
        tooltip="Select to save changes to the template.",
    )

    _split_btn_style = ft.ButtonStyle(
        text_style=ft.TextStyle(size=UIConfig.TEXT_SIZE_SMALL)
    )

    controls.add_folder_button = ft.Button(
        "Add Folder/File",
        tooltip="Add a folder or file to the template\nlist in the display.",
        style=_split_btn_style,
    )

    controls.remove_folder_button = ft.Button(
        "Remove Folder/File",
        tooltip="To remove folder or file from the displayed template\n click the folder or file in the display\nand then click this button.",
        style=_split_btn_style,
    )

    # Package management controls
    controls.packages_label = ft.Text("Packages: 0")

    controls.packages_container = ft.Container(
        content=ft.Column(
            controls=[],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        border=ft.Border.all(1, ft.Colors.GREY_700),
        border_radius=4,
        padding=10,
        height=UIConfig.SUBFOLDERS_HEIGHT,
        width=UIConfig.SPLIT_CONTAINER_WIDTH,
    )

    controls.add_package_button = ft.Button(
        "Add Packages...",
        tooltip="Open dialog to add one or more packages to the install list.",
        style=_split_btn_style,
    )

    controls.remove_package_button = ft.Button(
        "Remove Package",
        tooltip="Click a package in the list to select it,\nthen click Remove to delete it.",
        style=_split_btn_style,
    )

    controls.clear_packages_button = ft.Button(
        "Clear Packages",
        tooltip="Remove all packages from the install list.",
        style=_split_btn_style,
    )

    # Status and action controls
    controls.status_icon = ft.Icon(ft.Icons.INFO_OUTLINE, size=16, visible=False)
    controls.status_text = ft.Text("")

    controls.build_project_button = ft.Button(
        content="Build Project",
        tooltip="Enter a valid path and project name to enable.",
        bgcolor=UIConfig.COLOR_BTN_BUILD,
        color=ft.Colors.WHITE,
        width=UIConfig.BUTTON_WIDTH_BUILD,
        disabled=True,
        opacity=0.5,
    )

    controls.reset_button = ft.Button(
        content="Reset",
        icon=ft.Icons.REFRESH,
        tooltip="Resets all controls and values\nto their original state.",
        bgcolor=UIConfig.COLOR_BTN_RESET,
        color=ft.Colors.WHITE,
        width=UIConfig.BUTTON_WIDTH_ACTION,
    )

    controls.exit_button = ft.Button(
        content="Exit",
        icon=ft.Icons.EXIT_TO_APP,
        bgcolor=UIConfig.COLOR_BTN_EXIT,
        color=ft.Colors.WHITE,
        width=UIConfig.BUTTON_WIDTH_ACTION,
    )

    controls.progress_ring = ft.ProgressRing(
        visible=False,
        width=UIConfig.PROGRESS_RING_SIZE,
        height=UIConfig.PROGRESS_RING_SIZE,
        stroke_width=UIConfig.PROGRESS_RING_STROKE_WIDTH,
    )

    # Title and container lists
    controls.main_title = ft.Text(
        "UV Project Creator",
        size=UIConfig.MAIN_TITLE_SIZE,
        weight=ft.FontWeight.BOLD,
        color=colors["main_title"],
    )

    controls.section_titles = []
    controls.section_containers = []

    return controls


def create_sections(controls: Controls, state: "AppState") -> None:
    """Create section containers and organize controls into sections.

    Args:
        controls: Controls instance containing all UI elements.
        state: The application state instance.
    """
    # Project path and name section
    project_name_container, project_name_title = create_section_box(
        "Set Project Path and Name",
        [
            ft.Column(
                controls=[
                    controls.project_path_label,
                    ft.Row(
                        controls=[
                            controls.project_path_input,
                            controls.copy_path_button,
                            controls.browse_button,
                        ],
                    ),
                    controls.warning_banner,
                    controls.project_name_label,
                    controls.project_name_input,
                    controls.path_preview_text,
                ],
            ),
        ],
        state.is_dark_mode,
    )
    controls.section_containers.append(project_name_container)
    controls.section_titles.append(project_name_title)

    # Options section
    options_container, options_title = create_section_box(
        "Set Options",
        [
            ft.Column(
                controls=[
                    controls.python_version_label,
                    controls.python_version_dropdown,
                    controls.create_git_checkbox,
                    controls.ui_project_checkbox,
                    controls.other_projects_checkbox,
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.MERGE_TYPE,
                                size=12,
                                color=ft.Colors.GREY_500,
                            ),
                            ft.Text(
                                "Select both to merge templates",
                                size=11,
                                italic=True,
                                color=ft.Colors.GREY_500,
                            ),
                            ft.Icon(
                                ft.Icons.INFO_OUTLINE,
                                size=12,
                                color=UIConfig.COLOR_INFO,
                                tooltip=(
                                    "When both a UI Framework and a Project Type are selected, "
                                    "their folder structures are merged automatically.\n"
                                    "Matching folders are combined, unique folders from each are "
                                    "included, and file lists are unioned."
                                ),
                            ),
                        ],
                        spacing=4,
                    ),
                    controls.include_starter_files_checkbox,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        state.is_dark_mode,
    )
    controls.section_containers.append(options_container)
    controls.section_titles.append(options_title)

    # Folders + Packages section (side by side)
    folders_container, folders_title = create_section_box(
        "Project Structure",
        [
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            controls.app_subfolders_label,
                            controls.subfolders_container,
                            ft.Row(
                                controls=[
                                    controls.add_folder_button,
                                    controls.remove_folder_button,
                                ],
                            ),
                            ft.Row(
                                controls=[
                                    controls.auto_save_folder_changes,
                                    ft.Icon(
                                        ft.Icons.INFO_OUTLINE,
                                        size=14,
                                        color=UIConfig.COLOR_INFO,
                                        tooltip=(
                                            "When enabled, any folder structure changes "
                                            "(add, remove) are automatically saved to the "
                                            "project template config.\n"
                                            "Your customisations persist for future projects "
                                            "of the same framework or type."
                                        ),
                                    ),
                                ],
                                spacing=4,
                            ),
                        ],
                        spacing=UIConfig.SPACING_SMALL,
                    ),
                    ft.Container(
                        content=ft.VerticalDivider(
                            width=UIConfig.BORDER_WIDTH_DEFAULT,
                            color=ft.Colors.GREY_700,
                        ),
                        height=320,
                    ),
                    ft.Column(
                        controls=[
                            controls.packages_label,
                            controls.packages_container,
                            ft.Row(
                                controls=[
                                    controls.add_package_button,
                                    controls.remove_package_button,
                                ],
                            ),
                            controls.clear_packages_button,
                        ],
                        spacing=UIConfig.SPACING_SMALL,
                    ),
                ],
                spacing=UIConfig.SPACING_LARGE,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        state.is_dark_mode,
    )
    controls.section_containers.append(folders_container)
    controls.section_titles.append(folders_title)


def create_app_bars(page: ft.Page, controls: Controls, colors: dict) -> None:
    """Create and configure the app bar and bottom app bar.

    Args:
        page: The Flet page to attach app bars to.
        controls: Controls instance containing UI elements.
        colors: Theme colors dictionary.
    """
    page.appbar = ft.AppBar(
        title=ft.Text(
            "Create New Project with UV",
            size=UIConfig.APPBAR_TITLE_SIZE,
            color=colors["main_title"],
        ),
        bgcolor=ft.Colors.TRANSPARENT,
        actions=[
            controls.git_cheat_sheet_button,
            controls.help_button,
            controls.theme_toggle_button,
        ],
        toolbar_height=UIConfig.APPBAR_TOOLBAR_HEIGHT,
    )

    page.bottom_appbar = ft.BottomAppBar(
        bgcolor=colors["bottom_bar"],
        content=ft.Row(
            controls=[
                controls.reset_button,
                controls.exit_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=UIConfig.SPACING_XLARGE,
        ),
    )


def create_layout(controls: Controls) -> ft.Column:
    """Create the main layout column with all sections.

    Args:
        controls: Controls instance containing UI elements.

    Returns:
        The root Column control containing the complete UI layout.
    """
    return ft.Column(
        controls=[
            ft.Container(height=UIConfig.VSPACE_SMALL),  # Spacer
            controls.section_containers[0],  # Set Project Path and Name
            controls.section_containers[1],  # Set Options
            controls.section_containers[2],  # Add or Remove Folders
            ft.Container(
                content=ft.Row(
                    controls=[controls.progress_ring, controls.status_icon, controls.status_text],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                )
            ),
            ft.Row(
                controls=[controls.build_project_button],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Divider(height=UIConfig.SPACING_LARGE),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


def build_main_view(page: ft.Page, state: "AppState") -> ft.Control:
    """Build and return the main application UI layout.

    Creates all UI controls, arranges them in a column layout, and stores
    references on the page object for cross-module access.

    Args:
        page: The Flet page to attach controls and state references to.
        state: The application state instance to store on the page.

    Returns:
        The root Column control containing the complete UI layout.
    """
    colors = get_theme_colors(state.is_dark_mode)

    # Create all controls
    controls = create_controls(state, colors)

    # Organize controls into sections
    create_sections(controls, state)

    # Create app bars
    create_app_bars(page, controls, colors)

    # Create main layout
    layout = create_layout(controls)

    # Store references on page
    page.controls_ref = controls
    page.state_ref = state

    return layout
