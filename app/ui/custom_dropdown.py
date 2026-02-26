"""Custom overlay dropdown menu component.

Adapted from https://github.com/example/flet-dropdown experiment.
Uses page.overlay for the menu popup with animated open/close.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import flet as ft

BUTTON_HEIGHT = 40
DEFAULT_BORDER_DARKMODE = ft.Border.all(width=1, color="white,0.1")
DEFAULT_BORDER_LIGHTMODE = ft.Border.all(width=0.5, color=ft.Colors.GREY_500)
DEFAULT_TEXTCOLOR_DARKMODE = ft.Colors.WHITE60
DEFAULT_TEXTCOLOR_LIGHTMODE = ft.Colors.BLACK87
DEFAULT_TEXTSTYLE_DARKMODE = ft.TextStyle(size=15, color=DEFAULT_TEXTCOLOR_DARKMODE)
DEFAULT_TEXTSTYLE_LIGHTMODE = ft.TextStyle(size=15, color=DEFAULT_TEXTCOLOR_LIGHTMODE)
DEFAULT_BG = "white,0.01"
DEFAULT_RADIUS = 10
DEFAULT_BLUR = 10
DEFAULT_ANIMATION_OPACITY = 300
DEFAULT_ANIMATION_SPEED = 300


class _OverlayMenu(ft.Container):
    """Animated overlay menu that appears below the dropdown button."""

    def __init__(
        self,
        left: float = 0,
        top: float = 0,
        width: float = 200,
        on_select: Callable[[str], None] | None = None,
        options: list[str] | None = None,
        max_visible: int = 3,
        row_height: float = BUTTON_HEIGHT,
    ):
        super().__init__()
        self._left = left
        self._top = top
        self._width = width
        self.options = options or []
        self.max_visible = max_visible
        self.on_select = on_select
        self.height_button = row_height
        self.on_click = self.remove_menu
        self.text_color = DEFAULT_TEXTCOLOR_DARKMODE
        self.border = DEFAULT_BORDER_DARKMODE
        self.menu: ft.Container = self._create_menu()
        self.animate_opacity = DEFAULT_ANIMATION_OPACITY
        self.animate = DEFAULT_ANIMATION_SPEED

    def _build_button(self, text: str) -> ft.Container:
        def on_hover(e):
            color = "white,0.05"
            if self.page:
                if self.page.theme_mode == ft.ThemeMode.LIGHT:
                    color = "grey,0.15"
                else:
                    color = "white,0.05"
            e.control.bgcolor = color if e.control.bgcolor != color else "white,0.00"
            e.control.update()

        return ft.Container(
            content=ft.Text(text, size=16, color=self.text_color),
            on_click=lambda e: (self.on_select(text), self.remove_menu(e)),
            height=self.height_button - 8,
            on_hover=on_hover,
            padding=ft.padding.only(left=5, right=5),
            bgcolor="white,0.00",
            alignment=ft.Alignment.CENTER,
        )

    def _build_menu_content(self) -> ft.Column:
        return ft.Column(
            [self._build_button(option) for option in self.options],
            scroll=ft.ScrollMode.AUTO if self.max_visible < len(self.options) else None,
            spacing=0,
        )

    def _create_menu(self) -> ft.Container:
        self.menu = ft.Container(
            height=0,
            width=self._width,
            left=self._left,
            top=self._top,
            border_radius=DEFAULT_RADIUS,
            blur=10,
            bgcolor=DEFAULT_BG,
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

    async def _async_remove_menu(self, e):
        self.menu.height = 0
        self.menu.opacity = 0
        self.menu.update()
        await asyncio.sleep(0.01)
        self.page.overlay.remove(self)
        self.page.update()

    def remove_menu(self, e):
        self.page.run_task(self._async_remove_menu, e)

    async def _on_mount(self):
        self.page.update()
        self._create_menu()
        self.page.overlay.append(self.menu)
        self.page.update()
        await asyncio.sleep(0.02)
        count = len(self.options)
        self.menu.height = ((self.height_button - 8) * min(count, self.max_visible)) + 2
        self.menu.opacity = 1
        self.menu.update()

    def before_update(self):
        super().before_update()
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.text_color = DEFAULT_TEXTCOLOR_LIGHTMODE
            self.menu.border = DEFAULT_BORDER_LIGHTMODE
        else:
            self.text_color = DEFAULT_TEXTCOLOR_DARKMODE
            self.menu.border = DEFAULT_BORDER_DARKMODE

    def did_mount(self):
        self.page.run_task(self._on_mount)
        return super().did_mount()


class CustomDropdown(ft.Container):
    """Custom dropdown menu using an overlay for option selection.

    Exposes a ``value`` property for compatibility with code that
    reads/writes ``controls.python_version_dropdown.value``.
    """

    def __init__(
        self,
        height: float = BUTTON_HEIGHT,
        width: float = 70,
        text_style: ft.TextStyle = DEFAULT_TEXTSTYLE_DARKMODE,
        default_value: str = "None",
        options: list[str] | None = None,
        on_select: Callable[[str], None] | None = None,
        max_visible: int = 3,
        tooltip: str | None = None,
        selected_color: str | None = None,
    ):
        super().__init__()
        self._on_select_callback = on_select
        self.menu_text_style = text_style
        self.max_visible = max_visible
        self.options = options or []
        self.default_value = default_value
        self.height = height
        self.width = width
        self.tooltip = tooltip
        self.selected_color = selected_color or ft.Colors.GREEN
        self.text_display = ft.Text(
            value=self.default_value,
            style=ft.TextStyle(size=15, color=self.selected_color),
        )
        self._chevron = ft.Icon(
            ft.Icons.ARROW_DROP_DOWN,
            color=self.selected_color,
            size=20,
        )
        self.showing_container = ft.Container(
            ft.Row(
                [self.text_display, self._chevron],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=2,
            ),
            blur=DEFAULT_BLUR,
            on_hover=self._on_hover,
            alignment=ft.Alignment.CENTER,
            border_radius=DEFAULT_RADIUS,
        )
        self.content = self._build_content()

    # --- Public value property ---

    @property
    def value(self) -> str:
        return self.text_display.value

    @value.setter
    def value(self, new_value: str):
        self.text_display.value = new_value
        if self.page:
            self.text_display.update()

    # --- Public on_select property ---

    @property
    def on_select(self) -> Callable[[str], None] | None:
        return self._on_select_callback

    @on_select.setter
    def on_select(self, callback: Callable[[str], None] | None):
        self._on_select_callback = callback

    # --- Internal ---

    def _on_hover(self, e):
        color = "white,0.03"
        if self.page:
            if self.page.theme_mode == ft.ThemeMode.LIGHT:
                color = "grey,0.1"
            else:
                color = "white,0.03"
        e.control.bgcolor = color if e.control.bgcolor != color else DEFAULT_BG
        e.control.update()

    def before_update(self):
        super().before_update()
        if self.page:
            if self.page.theme_mode == ft.ThemeMode.LIGHT:
                self.showing_container.border = DEFAULT_BORDER_LIGHTMODE
            else:
                self.showing_container.border = DEFAULT_BORDER_DARKMODE
            self.text_display.style = ft.TextStyle(size=15, color=self.selected_color)
            self._chevron.color = self.selected_color

    def _handle_select(self, value: str):
        if self._on_select_callback:
            self._on_select_callback(value)
        self.text_display.value = value
        if self.page:
            self.text_display.update()

    def _on_tap_up(self, e: ft.TapEvent):
        top_left_x = e.global_position.x - e.local_position.x
        top_left_y = e.global_position.y - e.local_position.y + self.height + 5
        self.page.overlay.append(
            _OverlayMenu(
                left=top_left_x,
                top=top_left_y,
                width=self.width,
                on_select=self._handle_select,
                options=self.options,
                max_visible=self.max_visible,
                row_height=self.height,
            )
        )
        self.page.update()

    def _build_content(self) -> ft.GestureDetector:
        self.showing_container.border = DEFAULT_BORDER_DARKMODE
        return ft.GestureDetector(
            content=self.showing_container,
            on_tap_up=self._on_tap_up,
            mouse_cursor=ft.MouseCursor.CLICK,
        )
