"""Theme management.

This module provides the ThemeManager singleton that caches theme colors
to improve performance and provide consistent theming across the app.
"""

import flet as ft


class ThemeManager:
    """Manages theme colors with caching for improved performance.

    Singleton pattern ensures only one instance exists and colors are
    cached rather than rebuilt on every access.
    """

    _instance = None
    _colors_cache: dict[str, dict[str, str]] = {}

    def __new__(cls):
        """Ensure only one instance of ThemeManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_colors(self, is_dark: bool) -> dict[str, str]:
        """Get theme colors for the specified mode.

        Colors are cached after first access for each theme mode.

        Args:
            is_dark: Whether dark mode is active

        Returns:
            Dictionary of color keys to Flet color values
        """
        cache_key = "dark" if is_dark else "light"

        if cache_key not in self._colors_cache:
            self._colors_cache[cache_key] = self._build_colors(is_dark)

        return self._colors_cache[cache_key]

    @staticmethod
    def _build_colors(is_dark: bool) -> dict[str, str]:
        """Build color dictionary for the specified theme mode.

        Args:
            is_dark: Whether dark mode is active

        Returns:
            Dictionary mapping color names to Flet color values
        """
        if is_dark:
            return {
                "section_title": ft.Colors.BLUE_GREY_300,
                "section_border": ft.Colors.BLUE_GREY_700,
                "status_default": ft.Colors.GREY_400,
                "main_title": ft.Colors.BLUE_300,
                "bottom_bar": ft.Colors.BLUE_GREY_900,
            }
        return {
            "section_title": ft.Colors.BLUE_GREY_700,
            "section_border": ft.Colors.BLUE_GREY_200,
            "status_default": ft.Colors.GREY_700,
            "main_title": ft.Colors.BLUE_800,
            "bottom_bar": ft.Colors.BLUE_GREY_100,
        }

    def clear_cache(self) -> None:
        """Clear the color cache.

        Useful if theme definitions need to be reloaded at runtime.
        """
        self._colors_cache.clear()


# Create singleton instance for convenience
theme_manager = ThemeManager()


def get_theme_colors(is_dark: bool) -> dict[str, str]:
    """Get theme colors using the ThemeManager.

    Backward-compatible wrapper around ThemeManager.get_colors().

    Args:
        is_dark: Whether dark mode is active

    Returns:
        Dictionary of color keys to Flet color values
    """
    return theme_manager.get_colors(is_dark)
