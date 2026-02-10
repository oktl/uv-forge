import flet as ft


# TODO - place different controls in window to see what they look like.
# Main function to initialize Flet app
def main(page: ft.Page):
    # default theme mode
    page.theme_mode = ft.ThemeMode.LIGHT

    # define Light mode theme
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.GREEN_100,
    )

    # define Dark mode theme
    page.dark_theme = ft.Theme(
        color_scheme_seed=ft.Colors.ORANGE_100,
    )

    def toggle_theme(e):
        # Toggle theme between light and dark
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        page.update()

    # Controls
    theme_button = ft.ElevatedButton("Toggle Theme", on_click=toggle_theme)
    input = ft.TextField("Something to read")

    # Layout and add components to page
    page.add(
        ft.Text("Hi, From Flet!", size=30),
        theme_button,
        input,
    )


ft.run(main)
