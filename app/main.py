"""Application entry point for the UV Project Creator.

This module initializes the Flet application, configures the main page,
and wires together the application state, UI components, and event handlers.
"""

import sys
from pathlib import Path

# Add project root to path when running as script
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

import flet as ft
from loguru import logger

from app.config.logging_config import setup_logging
from app.core.state import AppState
from app.handlers.event_handlers import attach_handlers
from app.ui.components import build_main_view


async def main(page: ft.Page) -> None:
    """Initialize and configure the main application page.

    Sets up window dimensions, theme, padding, and initializes the application
    state and UI components. Attaches event handlers and centers the window.

    Args:
        page: The Flet page object representing the application window.
    """
    try:
        # Set up logging first thing.
        setup_logging()
        logger.info("Starting Create Project application")

        # Configure page-level settings including window size, colors, and title.
        page.title = "UV Project Creator"
        page.window.width = 750
        page.window.height = 1330
        page.padding = 30

        state = AppState()
        page.theme_mode = (
            ft.ThemeMode.DARK if state.is_dark_mode else ft.ThemeMode.LIGHT
        )
        controls = build_main_view(page, state)
        page.add(controls)

        attach_handlers(page, state)

        await page.window.center()

    except Exception as e:
        logger.error(f"Application error: {e}")
        logger.exception("Full traceback:")
        raise


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
