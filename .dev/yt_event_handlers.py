"""Event handlers for the YouTube Transcript Downloader.

This module defines all event handlers for UI interactions, including
transcript fetching, saving, summarization, and application control.
Handlers are attached to UI controls via the attach_handlers function.
"""

import asyncio
from pathlib import Path

import flet as ft
from core.state import AppState
from core.state_validator import StateValidator
from core.ui_state_sync import UIStateSync
from handlers.button_state_manager import ButtonStateManager
from handlers.handler_factory import async_handler
from services.format_transcript import format_transcript
from services.get_transcript import extract_video_id, get_transcript, get_video_title
from services.summarize import summarize_transcript
from ui.components import Controls
from ui.dialogs import (
    create_edit_file_dialog,
    create_help_dialog,
    create_preview_formatted_dialog,
)
from ui.theme_manager import get_theme_colors
from ui.ui_config import UIConfig
from utils.async_executor import AsyncExecutor
from utils.file_content_builder import FileContentBuilder


def _get_controls(page: ft.Page) -> Controls:
    """Retrieve the Controls instance from the page.

    Args:
        page: The Flet page containing the controls reference.

    Returns:
        The Controls instance stored on the page.
    """
    return page.controls_ref


async def _reset_ui(page: ft.Page, controls: Controls, state: AppState) -> None:
    """Reset all UI controls and application state to initial values.

    Clears input fields, resets status messages, disables action buttons,
    and resets the application state.

    Args:
        page: The Flet page to update.
        controls: The Controls instance containing UI references.
        state: The AppState instance to reset.
    """
    state.reset()
    colors = get_theme_colors(state.is_dark_mode)

    controls.url_field.value = ""
    await controls.url_field.focus()
    controls.status_text.value = ""
    controls.progress_ring.visible = False

    controls.status_text.color = colors["status_default"]

    # Reset all buttons to initial disabled state
    button_manager = ButtonStateManager(controls, state)
    button_manager.reset_all_buttons_to_initial_state()

    controls.summary_text.value = ""

    page.update()


def _build_file_content(
    transcript: str,
    formatted: str | None,
    summary: str | None,
    should_format: bool,
    video_title: str | None = None,
    video_id: str | None = None,
) -> str:
    """Build the file content based on format preference and available data.

    Uses FileContentBuilder for consistent formatting logic.
    """
    builder = FileContentBuilder(video_title, video_id)
    return builder.build(
        transcript=transcript,
        formatted_transcript=formatted,
        summary=summary,
        as_markdown=should_format,
    )


def _build_content_description(
    summary: str | None, should_format: bool
) -> tuple[str, str]:
    """Build content description for dialog title and status message.

    Uses FileContentBuilder for consistent description generation.

    Returns:
        Tuple of (dialog_title, status_description)
    """
    builder = FileContentBuilder()
    return builder.get_description(has_summary=bool(summary), as_markdown=should_format)


class Handlers:
    """Event handlers for UI controls.

    Encapsulates all event handler methods and provides access to page,
    controls, and application state.
    """

    def __init__(self, page: ft.Page, controls: Controls, state: AppState) -> None:
        """Initialize handlers with required references.

        Args:
            page: The Flet page for UI updates.
            controls: The Controls instance containing UI references.
            state: The application state instance.
        """
        self.page = page
        self.controls = controls
        self.state = state
        self.button_manager = ButtonStateManager(controls, state)
        self.state_sync = UIStateSync(controls, state)

    def _set_status(
        self, message: str, status_type: str = "info", update: bool = False
    ) -> None:
        """Update status text message and color.

        Args:
            message: Status message to display.
            status_type: One of "info", "success", or "error".
            update: Whether to call page.update() after setting.
        """
        colors = {
            "info": ft.Colors.BLUE_600,
            "success": ft.Colors.GREEN_600,
            "error": ft.Colors.RED_600,
        }
        self.controls.status_text.value = message
        self.controls.status_text.color = colors.get(status_type, ft.Colors.BLUE_600)
        if update:
            self.page.update()

    async def on_get_transcript(self, _: ft.ControlEvent) -> None:
        """Handle the Get Transcript button click.

        Validates the URL, extracts the video ID, fetches the transcript,
        and updates the UI with results or error messages.
        """
        url = (
            self.controls.url_field.value.strip()
            if self.controls.url_field.value
            else ""
        )
        if not url:
            self._set_status("Please enter a YouTube URL.", "error", update=True)
            return

        video_id = extract_video_id(url)
        if not video_id:
            self._set_status(
                "Invalid YouTube URL. Please check and try again.", "error", update=True
            )
            return

        self._set_status("Fetching transcript...", "info", update=True)

        transcript, message = get_transcript(video_id)

        if transcript:
            # Set transcript and clear dependent fields
            video_title = get_video_title(video_id)
            self.state_sync.set_transcript(transcript, video_id, video_title)

            self._set_status(message, "success")

            # Enable all transcript action buttons
            self.button_manager.enable_all_transcript_actions()

            self._update_word_count_buttons()  # Ensure correct visual state
        else:
            self._set_status(message, "error")

            # Disable all transcript action buttons
            self.button_manager.disable_all_transcript_actions()
            self.controls.reset_button.disabled = False

        self.page.update()

    async def _run_formatting(self) -> tuple[str | None, str | None]:
        """Run transcript formatting and update UI.

        Returns:
            A tuple containing the formatted text and an error message.
            If formatting is successful, the error message will be None.
        """
        provider = self.state.format_provider
        self.state_sync.set_progress_visible(True)
        self._set_status(
            f"Formatting transcript via {provider.title()}...", "info", update=True
        )

        formatted, message = await AsyncExecutor.run(
            format_transcript, self.state.transcript_text, provider
        )

        self.state_sync.set_progress_visible(False)

        if formatted:
            self.state_sync.set_formatted_text(formatted)
            return formatted, None

        self._set_status(message, "error", update=True)
        return None, message

    async def _format_if_needed(self) -> bool:
        """Format transcript via AI if provider selected and not already formatted.

        Returns:
            True if ready to proceed with save, False if formatting failed.
        """
        if self.state.format_provider is None or self.state.formatted_text:
            return True

        formatted, error = await self._run_formatting()

        if error:
            return False

        self._set_status(
            "Transcript formatted! Opening save dialog...", "success", update=True
        )
        return True

    def _write_file(self, save_path: str, content: str, status_desc: str) -> None:
        """Write content to file and update status message.

        Args:
            save_path: Path to write the file to.
            content: Content to write.
            status_desc: Description of content for status message.
        """
        try:
            Path(save_path).write_text(content, encoding="utf-8")
            self._set_status(f"Saved {status_desc} to: {save_path}", "success")
        except Exception as ex:
            self._set_status(f"Error saving file: {ex}", "error")
        self.page.update()

    async def on_save_click(self, _: ft.ControlEvent) -> None:
        """Handle the Save Transcript button click.

        Optionally formats the transcript using AI, then opens a file save
        dialog and writes the transcript (and summary if available) to file.
        """
        if not StateValidator.has_transcript(self.state):
            return

        if not await self._format_if_needed():
            return

        should_format = self.state.format_provider is not None
        file_extension = "md" if should_format else "txt"
        default_filename = f"transcript_{self.state.video_id}.{file_extension}"
        dialog_title, status_desc = _build_content_description(
            self.state.summary_text, should_format
        )

        save_path = await self.controls.file_picker.save_file(
            dialog_title=dialog_title,
            file_name=default_filename,
            allowed_extensions=[file_extension],
        )

        if save_path:
            content = _build_file_content(
                self.state.transcript_text,
                self.state.formatted_text,
                self.state.summary_text,
                should_format,
                video_title=self.state.video_title,
                video_id=self.state.video_id,
            )
            self._write_file(save_path, content, status_desc)

    def _update_word_count_buttons(self) -> None:
        """Update visual state of word count buttons based on selection."""
        self.button_manager.update_word_count_button(self.state.selected_word_count)

    def _update_provider_buttons(
        self,
        button_prefix: str,
        selected_provider: str | None,
    ) -> None:
        """Update visual state of provider buttons based on selection.

        Generic method that works for both format and summarize provider buttons.
        Updates border color and width to indicate selection state.

        Args:
            button_prefix: The button name prefix ("format" or "summarize")
            selected_provider: The currently selected provider name, or None
        """
        for provider_name, config in UIConfig.PROVIDER_CONFIG.items():
            # Get the button dynamically (e.g., "format_claude_button")
            button_attr = f"{button_prefix}_{provider_name}_button"
            button = getattr(self.controls, button_attr)

            # Update border using UIConfig helper
            is_selected = provider_name == selected_provider
            button.border = UIConfig.get_border_for_selection(
                is_selected, config["color"]
            )

    def _update_format_provider_buttons(self) -> None:
        """Update visual state of format provider buttons based on selection."""
        self._update_provider_buttons("format", self.state.format_provider)

    def _update_summarize_provider_buttons(self) -> None:
        """Update visual state of summarize provider buttons based on selection."""
        self._update_provider_buttons("summarize", self.state.summarize_provider)

    async def on_format_provider_select(self, provider: str) -> None:
        """Handle format provider button click - toggle selection.

        Args:
            provider: The AI provider to use ("claude" or "gemini").
        """
        # Check if disabled (no transcript loaded)
        if not StateValidator.has_transcript(self.state):
            return

        # Toggle logic: if already selected, deselect; otherwise select
        if self.state.format_provider == provider:
            self.state_sync.set_format_provider(None, clear_formatted=True)
            self._set_status("Format disabled. Transcript will save as plain text.")
        else:
            self.state_sync.set_format_provider(provider, clear_formatted=True)
            self._set_status(
                f"Format with {provider.title()} selected. Click Save to format and save."
            )
        self._update_format_provider_buttons()
        self.button_manager._update_preview_button_state()
        self.page.update()

    async def on_select_word_count(self, word_count: int) -> None:
        """Handle word count button click - selects the word count without summarizing.

        Args:
            word_count: Target word count (100, 300, or 500).
        """
        self.state_sync.set_word_count(word_count)
        self._update_word_count_buttons()
        self._set_status(
            f"Word count set to ~{word_count} words. Click a provider button to summarize.",
            "info",
            update=True,
        )

    async def on_summarize(self, provider: str) -> None:
        """Handle a summarize button click (Claude or Gemini).

        Generates an AI summary of the transcript using the selected provider
        and the previously selected word count.

        Args:
            provider: The AI provider to use ("claude" or "gemini").
        """
        if not StateValidator.can_summarize(self.state):
            return

        self.state_sync.set_summarize_provider(provider)
        self._update_summarize_provider_buttons()

        word_count = self.state.selected_word_count
        self.state_sync.set_progress_visible(True)
        self._set_status(
            f"Generating {word_count}-word summary via {provider.title()}...",
            "info",
            update=True,
        )

        summary, message = await AsyncExecutor.run(
            summarize_transcript,
            self.state.transcript_text,
            word_count,
            provider,
        )

        self.state_sync.set_progress_visible(False)
        if summary:
            self.state_sync.set_summary(summary, visible=True)
            self._set_status(message, "success")
        else:
            self.state_sync.clear_summary()
            self._set_status(message, "error")

        self.page.update()

    async def on_reset(self, _: ft.ControlEvent) -> None:
        """Handle the Reset button click."""
        await _reset_ui(self.page, self.controls, self.state)

    async def on_exit(self, _: ft.ControlEvent) -> None:
        """Handle the Exit button click."""
        await self.page.window.close()

    async def on_copy_summary(self, _: ft.ControlEvent) -> None:
        """Handle copying the summary to clipboard."""
        if self.state.summary_text:
            await self.page.set_clipboard(self.state.summary_text)
            self._set_status("Summary copied to clipboard.", "success", update=True)

    async def on_paste_url(self, _: ft.ControlEvent) -> None:
        """Handle pasting a URL from clipboard."""
        value = await self.page.get_clipboard()
        if value:
            self.controls.url_field.value = value
            self._set_status("URL pasted from clipboard.", "info", update=True)

    async def on_theme_toggle(self, _: ft.ControlEvent) -> None:
        """Handle theme toggle button click."""
        self.state_sync.toggle_theme()
        colors = get_theme_colors(self.state.is_dark_mode)

        if self.state.is_dark_mode:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.controls.theme_toggle.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.controls.theme_toggle.icon = ft.Icons.DARK_MODE

        self.controls.main_title.color = colors["main_title"]
        self.page.bottom_appbar.bgcolor = colors["bottom_bar"]

        for title_text in self.controls.section_titles:
            title_text.color = colors["section_title"]
        for container in self.controls.section_containers:
            container.border = ft.border.all(1, colors["section_border"])

        self.page.update()

    def _show_dialog(self, dialog: ft.AlertDialog) -> None:
        """Add a dialog to the page overlay, open it, and update the page.

        Args:
            dialog: The Alert Dialog to show
        """
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    async def on_help_click(self, _: ft.ControlEvent) -> None:
        """Handle the Help button click.

        Loads help content from HELP.md and displays in a dialog.
        """
        # Load help content from file
        help_path = Path(__file__).parent.parent.parent / "HELP.md"
        try:
            help_content = help_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            help_content = (
                "# Help File Not Found\n\n"
                "The help documentation file (HELP.md) could not be found. "
                "Please ensure the file exists in the project root directory."
            )
        except Exception as e:
            help_content = f"# Error Loading Help\n\nAn error occurred: {e}"

        # Create close handler as a closure that will capture dialog
        def close_help_dialog(_):
            help_dialog.open = False
            self.page.update()

        # Create and show dialog
        help_dialog = create_help_dialog(help_content, close_help_dialog)
        self._show_dialog(help_dialog)

    async def on_view_edit_file(self, _: ft.ControlEvent) -> None:
        """Handle the View/Edit File button click.

        Opens a file picker to select a markdown or text file, displays it
        in an editable dialog, and allows saving changes back to the file.
        """
        # Open file picker to select a file
        files = await self.controls.file_picker.pick_files(
            dialog_title="Select transcript file to view/edit",
            allowed_extensions=["md", "txt"],
            allow_multiple=False,
        )

        # Check if user selected a file (returns list[FilePickerFile])
        if not files or len(files) == 0:
            return

        selected_file = files[0].path

        # Read the file content
        try:
            content = Path(selected_file).read_text(encoding="utf-8")
        except Exception as e:
            self._set_status(f"Error reading file: {e}", "error", update=True)
            return

        # Create save handler for the dialog
        def save_edited_file(edited_content: str, file_path: str):
            try:
                Path(file_path).write_text(edited_content, encoding="utf-8")
                edit_dialog.open = False
                self._set_status(
                    f"File saved successfully: {Path(file_path).name}", "success"
                )
            except Exception as ex:
                self._set_status(f"Error saving file: {ex}", "error")
            self.page.update()

        # Create close handler
        def close_edit_dialog(_):
            edit_dialog.open = False
            self.page.update()

        # Create and show edit dialog
        edit_dialog = create_edit_file_dialog(
            content,
            selected_file,
            save_edited_file,
            close_edit_dialog,
        )
        self._show_dialog(edit_dialog)

    async def on_preview_formatted(self, _: ft.ControlEvent) -> None:
        """Handle the Preview Formatted button click.

        Formats the transcript using the selected AI provider and displays
        it in an editable preview dialog. User can review/edit before saving.
        """
        # Validate prerequisites
        if not StateValidator.has_transcript(self.state):
            self._set_status("No transcript loaded.", "error", update=True)
            return

        if not self.state.format_provider:
            self._set_status(
                "Please select a format provider first.", "error", update=True
            )
            return

        # Use cached text or format if needed
        if self.state.formatted_text:
            formatted_content = self.state.formatted_text
        else:
            formatted_content, error = await self._run_formatting()
            if error:
                return  # Status already set by _run_formatting

        provider = self.state.format_provider

        # Create save handler for the dialog
        def save_to_file_from_preview(edited_content: str):
            # Update cached formatted text with any edits
            self.state_sync.set_formatted_text(edited_content)
            preview_dialog.open = False
            self.page.update()
            # Trigger the normal save flow asynchronously
            asyncio.create_task(self.on_save_click(None))

        # Create close handler
        def close_preview_dialog(_):
            # If user edited the text, update the cached version
            if text_field.value != formatted_content:
                self.state_sync.set_formatted_text(text_field.value)
            preview_dialog.open = False
            self.page.update()

        # Create and show preview dialog
        preview_dialog = create_preview_formatted_dialog(
            formatted_content,
            provider,
            save_to_file_from_preview,
            close_preview_dialog,
        )

        # Store text_field reference for close handler
        text_field = preview_dialog.content.content.controls[0]
        self._show_dialog(preview_dialog)


def attach_handlers(page: ft.Page, state: AppState) -> None:
    """Attach event handlers to button UI controls.

    Args:
        page: The Flet page containing the UI controls.
        state: The application state instance for handlers to access.
    """
    controls = _get_controls(page)
    handlers = Handlers(page, controls, state)

    # --- Main Action Buttons ---
    controls.get_transcript_button.on_click = handlers.on_get_transcript
    controls.save_button.on_click = handlers.on_save_click
    controls.preview_formatted_button.on_click = handlers.on_preview_formatted
    controls.view_edit_button.on_click = handlers.on_view_edit_file

    # --- Word Count Buttons ---
    word_counts = {"brief": 100, "balanced": 300, "detailed": 500}
    for name, count in word_counts.items():
        button = getattr(controls, f"summarize_{name}_button")
        button.on_click = async_handler(handlers.on_select_word_count, count)

    # --- Provider Buttons (Format & Summarize) ---
    for provider in UIConfig.PROVIDER_CONFIG:
        # Summarize by provider
        summarize_button = getattr(controls, f"summarize_{provider}_button")
        summarize_button.on_click = async_handler(handlers.on_summarize, provider)

        # Select format provider
        format_button = getattr(controls, f"format_{provider}_button")
        format_button.on_click = async_handler(
            handlers.on_format_provider_select, provider
        )

    # --- App Bar Buttons ---
    controls.reset_button.on_click = handlers.on_reset
    controls.exit_button.on_click = handlers.on_exit
    controls.help_button.on_click = handlers.on_help_click
    controls.theme_toggle.on_click = handlers.on_theme_toggle
