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

    # Progress Ring
    PROGRESS_RING_SIZE = 18
    PROGRESS_RING_STROKE_WIDTH = 2

    # Icon Sizes
    ICON_SIZE_DEFAULT = 18

    # Border Radius
    BORDER_RADIUS_DEFAULT = 8

    # Border Widths
    BORDER_WIDTH_THIN = 1
    BORDER_WIDTH_DEFAULT = 2

    # Spacing
    SPACING_SMALL = 10
    SPACING_LARGE = 20
    SPACING_XLARGE = 80

    # Padding
    PADDING_SECTION = 15

    # Text Sizes
    TEXT_SIZE_SMALL = 12

    # Vertical Spacing (Container heights for spacing)
    VSPACE_SMALL = 10

    # Dialog Dimensions
    DIALOG_WIDTH = 700
    DIALOG_HEIGHT = 800
    DIALOG_CONTENT_PADDING = 20
    DIALOG_TITLE_SIZE = 20

    # Components Layout
    MAIN_TITLE_SIZE = 24
    SECTION_TITLE_SIZE = 16
    APPBAR_TITLE_SIZE = 18
    APPBAR_TOOLBAR_HEIGHT = 30
    SECTION_WIDTH = 700
    SPLIT_CONTAINER_WIDTH = (
        310  # fits two containers + 8px gap within SECTION_WIDTH border/padding
    )
    SUBFOLDERS_HEIGHT = 200
    BUTTON_WIDTH_BUILD = 300
    BUTTON_WIDTH_ACTION = 110  # Reset and Exit buttons

    # Folder Tree Display
    FOLDER_TREE_INDENT_UNIT = "  "
    FOLDER_TREE_BRANCH_PREFIX = "|- "
    FOLDER_ITEM_PADDING = ft.Padding(left=4, right=4, top=1, bottom=1)
    SELECTED_ITEM_BGCOLOR = ft.Colors.BLUE_800
    SELECTED_ITEM_BORDER_COLOR = ft.Colors.BLUE_400
