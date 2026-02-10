"""UI components for {{project_name}}."""

import flet as ft


def build_main_view(page: ft.Page) -> ft.Column:
    """Build and return the main view layout.

    Args:
        page: The Flet page instance.

    Returns:
        A Column containing the main UI elements.
    """
    return ft.Column(
        controls=[
            ft.Text("{{project_name}}", size=24, weight=ft.FontWeight.BOLD),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
