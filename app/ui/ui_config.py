"""UI configuration constants.

This module centralizes all UI styling constants including dimensions,
colors, spacing, and provider configurations to ensure consistency
across the application.
"""

import flet as ft


class UIConfig:
    """Centralized UI styling and sizing constants.

    All magic numbers for UI dimensions, spacing, colors, and styling
    are defined here for easy modification and consistency.
    """

    # Button Dimensions
    BUTTON_WIDTH_SMALL = 120  # Brief, Balanced, Detailed buttons
    BUTTON_WIDTH_LARGE = 180  # Save button
    BUTTON_HEIGHT_DEFAULT = None  # Use Flet default

    # Progress Ring
    PROGRESS_RING_SIZE = 18
    PROGRESS_RING_STROKE_WIDTH = 2

    # Icon Sizes
    ICON_SIZE_SMALL = 14
    ICON_SIZE_DEFAULT = 18
    ICON_SIZE_LARGE = 24

    # Border Radius
    BORDER_RADIUS_DEFAULT = 8
    BORDER_RADIUS_BUTTON = 8

    # Border Widths
    BORDER_WIDTH_THIN = 1
    BORDER_WIDTH_DEFAULT = 2
    BORDER_WIDTH_SELECTED = 3

    # Container/Section Dimensions
    CONTAINER_WIDTH_MAIN = 550
    CONTAINER_WIDTH_TEXTAREA = 500

    # Spacing
    SPACING_SMALL = 10
    SPACING_MEDIUM = 15
    SPACING_LARGE = 20
    SPACING_XLARGE = 80

    # Padding
    PADDING_DEFAULT = 10
    PADDING_SECTION = 15

    # Text Sizes
    TEXT_SIZE_SMALL = 12
    TEXT_SIZE_DEFAULT = 14
    TEXT_SIZE_LARGE = 16

    # Vertical Spacing (Container heights for spacing)
    VSPACE_SMALL = 10
    VSPACE_MEDIUM = 15
    VSPACE_LARGE = 20

    # Toolbar
    TOOLBAR_HEIGHT = 40

    # Dialog Dimensions
    DIALOG_WIDTH = 700
    DIALOG_HEIGHT = 800
    DIALOG_CONTENT_PADDING = 20
    DIALOG_TITLE_SIZE = 20

    # Provider Colors (used for button borders and highlights)
    PROVIDER_CLAUDE_COLOR = ft.Colors.ORANGE_800
    PROVIDER_GEMINI_COLOR = ft.Colors.PURPLE_600
    PROVIDER_CHATGPT_COLOR = ft.Colors.BLUE_600

    # Selection Colors
    SELECTION_COLOR_ACTIVE = ft.Colors.BLUE_600
    SELECTION_COLOR_INACTIVE = ft.Colors.GREY_600

    @classmethod
    def create_button_style(
        cls,
        bgcolor: str = ft.Colors.GREY_600,
        color: str = ft.Colors.WHITE,
    ) -> ft.ButtonStyle:
        """Create a standard button style.

        Args:
            bgcolor: Background color
            color: Text color

        Returns:
            ButtonStyle instance
        """
        return ft.ButtonStyle(
            bgcolor=bgcolor,
            color=color,
        )

    @classmethod
    def get_border_for_selection(
        cls,
        is_selected: bool,
        provider_color: str = ft.Colors.GREY_600,
    ) -> ft.Border:
        """Get border styling for selection state.

        Args:
            is_selected: Whether the item is selected
            provider_color: Color to use when selected

        Returns:
            Border with appropriate width and color
        """
        width = cls.BORDER_WIDTH_SELECTED if is_selected else cls.BORDER_WIDTH_DEFAULT
        color = provider_color if is_selected else ft.Colors.GREY_600
        return ft.border.all(width, color)


# Create a singleton-like instance for convenience (though it's all class methods)
ui_config = UIConfig()
