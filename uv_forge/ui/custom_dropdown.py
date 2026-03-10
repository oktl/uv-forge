"""Custom dropdown menu component built with Flet page overlays.

Provides a themed, animated dropdown menu using page overlays. Supports
both light and dark themes with configurable options, max visible items,
and selection callbacks.

Based on Wanna-Pizza/Flet-Custom-Controls
(https://github.com/Wanna-Pizza/Flet-Custom-Controls)
with theme support contributed by Moluntic. Modified and refactored
for Flet 0.80+ with property-based public API for app integration.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import flet as ft

BUTTON_HEIGHT = 40
BUTTON_PADDING = 8
DEFAULT_BORDER_DARKMODE = ft.Border.all(width=1, color="white,0.1")
DEFAULT_BORDER_LIGHTMODE = ft.Border.all(width=0.5, color=ft.Colors.GREY_500)
DEFAULT_TEXTCOLOR_DARKMODE = ft.Colors.WHITE
DEFAULT_TEXTCOLOR_LIGHTMODE = ft.Colors.BLACK_87
DEFAULT_BG = "white,0.01"
MENU_BG_DARKMODE = "#1e1e1e"
MENU_BG_LIGHTMODE = "#f5f5f5"
DEFAULT_BG_TRANSPARENT = "white,0.00"
DEFAULT_RADIUS = 10
DEFAULT_BLUR = 10
DEFAULT_ANIMATION_OPACITY = 300
DEFAULT_ANIMATION_SPEED = 300
HOVER_COLOR_DARKMODE = "white,0.05"
HOVER_COLOR_LIGHTMODE = "grey,0.15"
HOVER_COLOR_DROPDOWN_DARKMODE = "white,0.03"
HOVER_COLOR_DROPDOWN_LIGHTMODE = "grey,0.1"


class _OverlayMenu(ft.Container):
    """Animated overlay menu that displays selectable options.

    Renders as a positioned overlay on the page with animated open/close
    transitions. Each option is a hoverable button that triggers a callback
    on selection. Scrolls automatically when options exceed max_visible.
    """

    def __init__(
        self,
        left: float = 0,
        top: float = 0,
        width: float = 200,
        on_select: Callable[[str], None] | None = None,
        options: list[str] | None = None,
        max_visible: int = 3,
    ):
        super().__init__()
        self._left = left
        self._top = top
        self._width = width
        self.options = options or []
        self.max_visible = max_visible
        self.on_select = on_select
        self.on_click = self.remove_menu
        self.text_color = DEFAULT_TEXTCOLOR_DARKMODE
        self.menu: ft.Container | None = None
        self._last_theme = None

    def _build_button(self, text: str) -> ft.Container:
        """Build a single hoverable, clickable option button."""

        def on_hover(e):
            color = HOVER_COLOR_DARKMODE
            if self.page and self.page.theme_mode == ft.ThemeMode.LIGHT:
                color = HOVER_COLOR_LIGHTMODE
            e.control.bgcolor = (
                color if e.control.bgcolor != color else DEFAULT_BG_TRANSPARENT
            )
            e.control.update()

        def on_click(e):
            if self.on_select:
                self.on_select(text)
            self.remove_menu(e)

        return ft.Container(
            content=ft.Text(text, size=14, color=self.text_color),
            on_click=on_click,
            height=BUTTON_HEIGHT - BUTTON_PADDING,
            on_hover=on_hover,
            padding=ft.Padding.only(left=5, right=5),
            bgcolor=DEFAULT_BG_TRANSPARENT,
            alignment=ft.Alignment.CENTER,
        )

    def _build_menu_content(self) -> ft.Column:
        """Build the scrollable column of option buttons."""
        return ft.Column(
            [self._build_button(option) for option in self.options],
            scroll=ft.ScrollMode.AUTO if self.max_visible < len(self.options) else None,
            spacing=0,
        )

    def _create_menu(self) -> ft.Container:
        """Create the animated menu container with blur and border styling."""
        self.menu = ft.Container(
            height=0,
            width=self._width,
            left=self._left,
            top=self._top,
            border_radius=DEFAULT_RADIUS,
            bgcolor=MENU_BG_DARKMODE,
            opacity=0,
            animate_opacity=ft.Animation(
                duration=DEFAULT_ANIMATION_OPACITY,
                curve=ft.AnimationCurve.LINEAR_TO_EASE_OUT,
            ),
            animate=ft.Animation(
                duration=DEFAULT_ANIMATION_SPEED,
                curve=ft.AnimationCurve.LINEAR_TO_EASE_OUT,
            ),
            border=DEFAULT_BORDER_DARKMODE,
            content=self._build_menu_content(),
        )
        return self.menu

    async def _async_remove_menu(self, _e):
        """Animate the menu closed and remove it from the page overlay."""
        self.menu.height = 0
        self.menu.opacity = 0
        self.menu.update()
        await asyncio.sleep(0.01)
        self.page.overlay.remove(self)
        self.page.update()

    def remove_menu(self, e):
        """Schedule the async menu removal as a background task."""
        self.page.run_task(self._async_remove_menu, e)

    async def on_mount(self):
        """Add the menu to the page overlay and animate it open."""
        self._create_menu()
        self.page.overlay.append(self.menu)
        self.page.update()
        await asyncio.sleep(0.02)
        count = len(self.options)
        self.menu.height = (
            (BUTTON_HEIGHT - BUTTON_PADDING) * min(count, self.max_visible)
        ) + 2
        self.menu.opacity = 1
        self.menu.update()

    def before_update(self):
        """Update text and border colors to match the current theme."""
        super().before_update()
        theme = self.page.theme_mode if self.page else None
        if theme == self._last_theme:
            return
        self._last_theme = theme
        if theme == ft.ThemeMode.LIGHT:
            self.text_color = DEFAULT_TEXTCOLOR_LIGHTMODE
            if self.menu:
                self.menu.border = DEFAULT_BORDER_LIGHTMODE
                self.menu.bgcolor = MENU_BG_LIGHTMODE
        else:
            self.text_color = DEFAULT_TEXTCOLOR_DARKMODE
            if self.menu:
                self.menu.border = DEFAULT_BORDER_DARKMODE
                self.menu.bgcolor = MENU_BG_DARKMODE

    def did_mount(self):
        """Trigger the async mount animation when added to the page."""
        self.page.run_task(self.on_mount)
        return super().did_mount()


class CustomDropdown(ft.Container):
    """Themed dropdown menu that opens an overlay menu on tap.

    Displays the currently selected value with a dropdown arrow icon.
    Tapping opens an animated overlay menu positioned below the control.
    Adapts styling to the page's light or dark theme.

    Exposes ``.value``, ``.options``, and ``.on_select`` properties for
    compatibility with the rest of the app.
    """

    def __init__(
        self,
        height: float = BUTTON_HEIGHT,
        width: float = 70,
        default_value: str = "None",
        options: list[str] | None = None,
        on_select: Callable[[str], None] | None = None,
        max_visible: int = 3,
        tooltip: str | None = None,
        selected_color: str | None = None,
    ):
        super().__init__(height=height, width=width)

        self._on_select_callback = on_select
        self.max_visible = max_visible
        self._options = options or []
        self.default_value = default_value
        self._active_menu: _OverlayMenu | None = None
        self._last_theme = None
        self.tooltip = tooltip
        self.selected_color = selected_color or ft.Colors.GREEN

        self.text_display = ft.Text(
            value=self.default_value,
            style=ft.TextStyle(size=14, color=self.selected_color),
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.arrow_icon = ft.Icon(
            ft.Icons.ARROW_DROP_DOWN, color=self.selected_color, size=20
        )

        self.showing_container = ft.Container(
            blur=DEFAULT_BLUR,
            on_hover=self._on_hover,
            alignment=ft.Alignment.CENTER,
            border_radius=DEFAULT_RADIUS,
            border=DEFAULT_BORDER_DARKMODE,
            padding=ft.Padding.only(left=10, right=5),
            content=ft.Row(
                controls=[
                    self.text_display,
                    self.arrow_icon,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self.content = ft.GestureDetector(
            content=self.showing_container,
            on_tap_up=self._on_tap_up,
            mouse_cursor=ft.MouseCursor.CLICK,
        )

    # --- Public value property ---

    @property
    def value(self) -> str:
        return self.text_display.value

    @value.setter
    def value(self, new_value: str):
        self.text_display.value = new_value
        if self.page:
            self.text_display.update()

    # --- Public options property ---

    @property
    def options(self) -> list[str]:
        return self._options

    @options.setter
    def options(self, new_options: list[str]):
        self._options = new_options

    # --- Public on_select property ---

    @property
    def on_select(self) -> Callable[[str], None] | None:
        return self._on_select_callback

    @on_select.setter
    def on_select(self, callback: Callable[[str], None] | None):
        self._on_select_callback = callback

    # --- Internal ---

    def _on_hover(self, e):
        """Toggle background highlight on hover."""
        color = HOVER_COLOR_DROPDOWN_DARKMODE
        if self.page and self.page.theme_mode == ft.ThemeMode.LIGHT:
            color = HOVER_COLOR_DROPDOWN_LIGHTMODE
        e.control.bgcolor = color if e.control.bgcolor != color else DEFAULT_BG
        e.control.update()

    def _handle_select(self, selected_value: str):
        """Handle option selection: update display and invoke callback."""
        self._active_menu = None
        if self._on_select_callback:
            self._on_select_callback(selected_value)
        self.text_display.value = selected_value
        if self.page:
            self.text_display.update()

    def before_update(self):
        """Update arrow icon, text style, and border colors based on theme."""
        super().before_update()
        if not self.page:
            return
        theme = self.page.theme_mode
        if theme == self._last_theme:
            return
        self._last_theme = theme
        if theme == ft.ThemeMode.LIGHT:
            self.showing_container.border = DEFAULT_BORDER_LIGHTMODE
        else:
            self.showing_container.border = DEFAULT_BORDER_DARKMODE
            self.text_display.style = ft.TextStyle(size=14, color=self.selected_color)
            self.arrow_icon.color = self.selected_color

    def _on_tap_up(self, e: ft.TapEvent):
        """Open the overlay menu positioned below this dropdown."""
        if self._active_menu:
            self._active_menu.remove_menu(e)
        # Overlay is positioned below the AppBar, so subtract its height
        # from window-relative global coordinates.
        appbar_h = self.page.appbar.toolbar_height if self.page.appbar else 0
        top_left_x = e.global_position.x - e.local_position.x
        top_left_y = (
            e.global_position.y - e.local_position.y + self.height + 2 - appbar_h
        )
        menu = _OverlayMenu(
            left=top_left_x,
            top=top_left_y,
            width=self.width,
            on_select=self._handle_select,
            options=self._options,
            max_visible=self.max_visible,
        )
        self._active_menu = menu
        self.page.overlay.append(menu)
        self.page.update()
