"""Application entry point for UV Forge.

This module initializes the Flet application, configures the main page,
and wires together the application state, UI components, and event handlers.
"""

import os
import sys
from pathlib import Path

# Add project root to path when running as script
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

import flet as ft
from loguru import logger

from uv_forge.core.logging_config import setup_logging
from uv_forge.core.settings_manager import load_settings
from uv_forge.core.state import AppState
from uv_forge.handlers.ui_handler import attach_handlers
from uv_forge.ui.components import build_main_view


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
        logger.info("Starting UV Forge application")

        # Configure page-level settings including window size, colors, and title.
        page.title = "UV Forge"
        page.window.width = 1520
        page.window.height = 980
        page.padding = 30

        settings = load_settings()
        state = AppState(settings=settings)
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


def run() -> None:
    """Entry point for the uv-forge console script."""
    # Ensure the venv bin dir is on PATH so tools like ruff are discoverable
    # even when running directly via .venv/bin/python (not via `uv run`).
    venv_bin = str(Path(sys.executable).parent)
    if venv_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = venv_bin + os.pathsep + os.environ.get("PATH", "")

    assets_dir = Path(__file__).parent / "assets"
    ft.run(main, assets_dir=str(assets_dir))


if __name__ == "__main__":
    run()
