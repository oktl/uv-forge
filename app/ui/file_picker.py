"""macOS native folder picker with "New Folder" support.

Uses AppleScript's `choose folder` dialog via osascript, which includes
a "New Folder" button that Flet's built-in FilePicker lacks on macOS.
Falls back to Flet's FilePicker on non-macOS platforms.
"""

import asyncio
import platform
import subprocess

from loguru import logger

IS_MACOS = platform.system() == "Darwin"


def _select_folder_macos(prompt: str = "Select Folder") -> str | None:
    """Open native macOS folder picker dialog via AppleScript.

    Args:
        prompt: Prompt message to display in the dialog.

    Returns:
        POSIX path string of selected folder, or None if cancelled/error.
    """
    try:
        script = f'POSIX path of (choose folder with prompt "{prompt}")'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        return None

    except subprocess.TimeoutExpired:
        logger.warning("Folder selection timed out")
        return None
    except Exception as e:
        logger.error(f"Error opening folder picker: {e}")
        return None


async def select_folder(prompt: str = "Select Folder") -> str | None:
    """Open a folder picker dialog appropriate for the current platform.

    On macOS, uses AppleScript's `choose folder` which includes a "New Folder"
    button. On other platforms, falls back to Flet's built-in FilePicker.

    Args:
        prompt: Prompt message to display in the dialog.

    Returns:
        Path string of selected folder, or None if cancelled/error.
    """
    if IS_MACOS:
        return await asyncio.to_thread(_select_folder_macos, prompt)

    import flet as ft

    return await ft.FilePicker().get_directory_path(dialog_title=prompt)
