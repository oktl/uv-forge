"""{{project_name}} — Flet application entry point."""

import flet as ft


def main(page: ft.Page):
    page.title = "{{project_name}}"
    page.add(ft.Text("Hello from {{project_name}}!"))


def run():
    """Entry point for pyproject.toml [project.scripts]."""
    ft.run(main)


if __name__ == "__main__":
    run()
