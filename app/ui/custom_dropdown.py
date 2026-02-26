"""Custom dropdown menu component.

Uses Flet's PopupMenuButton for reliable menu positioning, wrapped in a
styled button that matches the app's design language.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

DEFAULT_BORDER_DARKMODE = ft.Border.all(width=1, color="white,0.1")
DEFAULT_BORDER_LIGHTMODE = ft.Border.all(width=0.5, color=ft.Colors.GREY_500)
DEFAULT_RADIUS = 10


class CustomDropdown(ft.Container):
    """Styled dropdown using PopupMenuButton for the menu.

    Exposes a ``value`` property for compatibility with code that
    reads/writes ``controls.python_version_dropdown.value``.
    """

    def __init__(
        self,
        height: float = 40,
        width: float = 70,
        default_value: str = "None",
        options: list[str] | None = None,
        on_select: Callable[[str], None] | None = None,
        max_visible: int = 3,
        tooltip: str | None = None,
        selected_color: str | None = None,
    ):
        super().__init__()
        self._on_select_callback = on_select
        self.max_visible = max_visible
        self._options = options or []
        self.default_value = default_value
        self.height = height
        self.width = width
        self.tooltip = tooltip
        self.selected_color = selected_color or ft.Colors.GREEN
        self.text_display = ft.Text(
            value=self.default_value,
            style=ft.TextStyle(size=14, color=self.selected_color),
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
            alignment=ft.Alignment.CENTER,
            border_radius=DEFAULT_RADIUS,
            border=DEFAULT_BORDER_DARKMODE,
        )
        self._popup = self._build_popup()
        self.content = self._popup

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
        self._popup.items = self._build_menu_items()

    # --- Public on_select property ---

    @property
    def on_select(self) -> Callable[[str], None] | None:
        return self._on_select_callback

    @on_select.setter
    def on_select(self, callback: Callable[[str], None] | None):
        self._on_select_callback = callback

    # --- Internal ---

    def _build_menu_items(self) -> list[ft.PopupMenuItem]:
        return [
            ft.PopupMenuItem(
                content=ft.Text(opt, size=14),
                on_click=lambda e, v=opt: self._handle_select(v),
            )
            for opt in self._options
        ]

    def _build_popup(self) -> ft.PopupMenuButton:
        return ft.PopupMenuButton(
            content=self.showing_container,
            items=self._build_menu_items(),
        )

    def before_update(self):
        super().before_update()
        if self.page:
            if self.page.theme_mode == ft.ThemeMode.LIGHT:
                self.showing_container.border = DEFAULT_BORDER_LIGHTMODE
            else:
                self.showing_container.border = DEFAULT_BORDER_DARKMODE
            self.text_display.style = ft.TextStyle(size=14, color=self.selected_color)
            self._chevron.color = self.selected_color

    def _handle_select(self, value: str):
        if self._on_select_callback:
            self._on_select_callback(value)
        self.text_display.value = value
        if self.page:
            self.text_display.update()
