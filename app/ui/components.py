"""UI components and layout construction for the Project Creator.

This module defines the Controls class for storing UI control references and
the build_main_view function for constructing the application's visual layout.
"""

from typing import TYPE_CHECKING

import flet as ft

from app.utils.constants import PYTHON_VERSIONS
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
        browse_button: Button to open directory picker.
        warning_banner: Text for displaying warnings.
        project_name_label: Label for project name input.
        project_name_input: TextField for entering project name.
        python_version_label: Label for Python version dropdown.
        python_version_dropdown: Dropdown for selecting Python version.
        create_git_checkbox: Checkbox for git initialization option.
        create_ui_project_checkbox: Checkbox for UI project option.
        other_projects_checkbox: Checkbox for Other Project types option.
        app_subfolders_label: Label for folder display.
        subfolders_container: Container showing folder structure.
        auto_save_folder_changes: Checkbox for auto-save option.
        add_folder_button: Button to add a folder.
        remove_folder_button: Button to remove a folder.
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
        self.browse_button: ft.Button
        self.warning_banner: ft.Text
        self.project_name_label: ft.Text
        self.project_name_input: ft.TextField
        self.python_version_label: ft.Text
        self.python_version_dropdown: ft.Dropdown
        self.create_git_checkbox: ft.Checkbox
        self.create_ui_project_checkbox: ft.Checkbox
        self.other_projects_checkbox: ft.Checkbox
        self.app_subfolders_label: ft.Text
        self.subfolders_container: ft.Container
        self.auto_save_folder_changes: ft.Checkbox
        self.add_folder_button: ft.Button
        self.remove_folder_button: ft.Button
        self.include_starter_files_checkbox: ft.Checkbox
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
        size=16,
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
            spacing=10,
        ),
        border=ft.Border.all(1, colors["section_border"]),
        border_radius=8,
        padding=15,
        width=700,
    )
    return container, title_text


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
    controls = Controls()

    # Define all the controls
    controls.theme_toggle_button = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if state.is_dark_mode else ft.Icons.DARK_MODE,
        icon_size=18,
        tooltip="Toggle dark/light mode",
    )

    controls.git_cheat_sheet_button = ft.IconButton(
        icon=ft.Icons.MENU_BOOK,
        icon_size=18,
        tooltip="Git Cheat Sheet",
    )

    controls.help_button = ft.IconButton(
        icon=ft.Icons.HELP_OUTLINE,
        icon_size=18,
        tooltip="Help & Documentation",
    )

    controls.project_path_label = ft.Text("Create Project In")
    controls.project_path_input = ft.TextField(
        value=state.project_path,
        hint_text="Project Root Directory",
        # bgcolor=ft.Colors.GREY_800,
        expand=True,
    )

    controls.browse_button = ft.Button("Browse...")

    controls.warning_banner = ft.Text(
        "",
        color=ft.Colors.ORANGE,
        weight=ft.FontWeight.BOLD,
        size=14,
    )

    controls.project_name_label = ft.Text("New Project Name")

    controls.project_name_input = ft.TextField(
        hint_text="Enter project name...",
        expand=True,
        # bgcolor=ft.Colors.GREY_800,
        border_color=ft.Colors.BLUE,
        border_width=1,
    )

    controls.python_version_label = ft.Text("Python Version")
    controls.python_version_dropdown = ft.Dropdown(
        value=state.selected_python_version,
        options=[ft.dropdown.Option(v) for v in PYTHON_VERSIONS],
        tooltip="Choose a version, default is 3.14",
        # bgcolor=ft.Colors.GREY_800,
        expand=True,
        border_color=ft.Colors.BLUE,
        width=300,
    )

    controls.create_git_checkbox = ft.Checkbox(
        label="Initialize Git Repository",
        value=state.initialize_git,
        tooltip="Choose if you want a git repository\nDefault is yes",
    )

    controls.include_starter_files_checkbox = ft.Checkbox(
        label="Include Starter Files",
        value=state.include_starter_files,
        label_style=ft.TextStyle(color=ft.Colors.GREEN)
        if state.include_starter_files
        else None,
        tooltip="Create template files with boilerplate starter content.\nDefault is no — only folders and __init__.py are created.",
    )

    controls.create_ui_project_checkbox = ft.Checkbox(
        label="Create UI Project",
        value=state.create_ui_project,
        tooltip="Choose if you're creating a UI.\nDefault is no.\nOpens a scrolling dialog to choose options.\nCan be combined with Other Project Type",
    )
    controls.other_projects_checkbox = ft.Checkbox(
        label="Create Other Project Type",
        tooltip="Create other project types\nlike Django, data science, web scraping, etc...\nOpens a scrolling dialog to choose options.\nCan be combined with UI Project",
    )

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
        height=200,
        width=700,
    )

    controls.auto_save_folder_changes = ft.Checkbox(
        label="Auto-save folder changes to config",
        value=state.auto_save_folders,
        tooltip="Select to save changes to the template.",
    )

    controls.add_folder_button = ft.Button(
        "Add Folder/File",
        tooltip="Add a folder or file to the template\nlist in the display.",
    )

    controls.remove_folder_button = ft.Button(
        "Remove Folder/File",
        tooltip="To remove folder or file from the displayed template\n click the folder or file in the display\nand then click this button.",
    )

    controls.status_text = ft.Text("")

    controls.build_project_button = ft.Button(
        content="Build Project",
        # icon=ft.Icons.
        tooltip="Enter a valid path and project name to enable.",
        bgcolor=ft.Colors.GREEN,
        color=ft.Colors.WHITE,
        width=300,
        disabled=True,
        opacity=0.5,
    )

    controls.reset_button = ft.Button(
        content="Reset",
        icon=ft.Icons.REFRESH,
        tooltip="Resets all controls and values\nto their original state.",
        bgcolor=ft.Colors.ORANGE,
        color=ft.Colors.WHITE,
        width=110,
    )

    controls.exit_button = ft.Button(
        content="Exit",
        icon=ft.Icons.EXIT_TO_APP,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        width=110,
    )

    controls.progress_ring = ft.ProgressRing(
        visible=False,
        width=UIConfig.PROGRESS_RING_SIZE,
        height=UIConfig.PROGRESS_RING_SIZE,
        stroke_width=UIConfig.PROGRESS_RING_STROKE_WIDTH,
    )

    controls.main_title = ft.Text(
        "UV Project Creator",
        size=24,
        weight=ft.FontWeight.BOLD,
        color=colors["main_title"],
    )

    controls.section_titles = []
    controls.section_containers = []

    # Put all the pieces together
    project_name_container, project_name_title = create_section_box(
        "Set Project Path and Name",
        [
            ft.Column(
                controls=[
                    controls.project_path_label,
                    ft.Row(
                        controls=[
                            controls.project_path_input,
                            controls.browse_button,
                        ],
                    ),
                    controls.warning_banner,
                    controls.project_name_label,
                    controls.project_name_input,
                ],
            ),
        ],
        state.is_dark_mode,
    )
    controls.section_containers.append(project_name_container)
    controls.section_titles.append(project_name_title)

    options_container, options_title = create_section_box(
        "Set Options",
        [
            ft.Column(
                controls=[
                    controls.python_version_label,
                    controls.python_version_dropdown,
                    controls.create_git_checkbox,
                    controls.create_ui_project_checkbox,
                    controls.other_projects_checkbox,
                    controls.include_starter_files_checkbox,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        state.is_dark_mode,
    )
    controls.section_containers.append(options_container)
    controls.section_titles.append(options_title)

    folders_container, folders_title = create_section_box(
        "Add or Remove Project Folders",
        [
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
                    controls.auto_save_folder_changes,
                ],
            ),
        ],
        state.is_dark_mode,
    )
    controls.section_containers.append(folders_container)
    controls.section_titles.append(folders_title)

    # Put it all together
    layout = ft.Column(
        controls=[
            # controls.main_title,
            ft.Container(height=10),  # Spacer
            project_name_container,  # Set Project Path and Name
            options_container,  # Set Options
            folders_container,  # Add or Remove Folders
            ft.Container(
                content=ft.Row(
                    controls=[controls.progress_ring, controls.status_text],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                )
            ),
            ft.Row(
                controls=[controls.build_project_button],
                alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Divider(height=20),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.appbar = ft.AppBar(
        title=ft.Text(
            "Create New Project with UV",
            size=18,
            color=colors["main_title"],
        ),
        bgcolor=ft.Colors.TRANSPARENT,
        actions=[
            controls.git_cheat_sheet_button,
            controls.help_button,
            controls.theme_toggle_button,
        ],
        toolbar_height=30,
    )

    page.bottom_appbar = ft.BottomAppBar(
        bgcolor=colors["bottom_bar"],
        content=ft.Row(
            controls=[
                controls.reset_button,
                controls.exit_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=80,
        ),
    )

    page.controls_ref = controls
    page.state_ref = state

    return layout
