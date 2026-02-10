"""UI State Synchronization for the UV Project Creator.

This module provides the UIStateSync class that ensures application state
and UI controls stay synchronized, preventing bugs from inconsistent updates.
"""

from typing import Optional

from app.ui.components import Controls
from app.core.state import AppState


class UIStateSync:
    """Synchronizes AppState with UI controls to prevent inconsistencies.

    Provides methods to update both state and UI together atomically,
    ensuring they never get out of sync.
    """

    def __init__(self, controls: Controls, state: AppState):
        """Initialize the UI state synchronizer.

        Args:
            controls: Reference to all UI controls
            state: Application state instance
        """
        self.controls = controls
        self.state = state

    def set_transcript(
        self,
        transcript: str,
        video_id: str,
        video_title: Optional[str] = None,
    ) -> None:
        """Set transcript data in state and clear dependent fields.

        When a new transcript is loaded, this clears any previous summary
        and formatted text since they're no longer valid.

        Args:
            transcript: The raw transcript text
            video_id: The YouTube video ID
            video_title: The video title (optional)
        """
        self.state.transcript_text = transcript
        self.state.video_id = video_id
        self.state.video_title = video_title

        # Clear dependent data that's no longer valid
        self.state.summary_text = None
        self.state.formatted_text = None

        # Clear summary UI (keep visible)
        self.controls.summary_text.value = ""

    def set_summary(self, summary: str, visible: bool = True) -> None:
        """Set summary text in both state and UI.

        Args:
            summary: The summary text to display
            visible: Whether to show the summary text field (default: True, kept for compatibility)
        """
        self.state.summary_text = summary
        self.controls.summary_text.value = summary
        # Keep summary text always visible

    def clear_summary(self) -> None:
        """Clear summary text from both state and UI (keep visible)."""
        self.state.summary_text = None
        self.controls.summary_text.value = ""
        # Keep summary text always visible

    def set_formatted_text(self, formatted_text: Optional[str]) -> None:
        """Set formatted transcript text in state.

        Args:
            formatted_text: The AI-formatted transcript, or None to clear
        """
        self.state.formatted_text = formatted_text

    def set_video_title(self, title: Optional[str]) -> None:
        """Update video title in state.

        Args:
            title: The video title, or None if unavailable
        """
        self.state.video_title = title

    def set_word_count(self, word_count: int) -> None:
        """Update selected word count in state.

        Args:
            word_count: The selected word count (100, 300, or 500)
        """
        self.state.selected_word_count = word_count

    def set_summarize_provider(self, provider: Optional[str]) -> None:
        """Update the last used summarize provider.

        Args:
            provider: Provider name ("claude", "gemini", "chatgpt") or None
        """
        self.state.summarize_provider = provider

    def set_format_provider(
        self,
        provider: Optional[str],
        clear_formatted: bool = False,
    ) -> None:
        """Update format provider selection.

        Args:
            provider: Provider name ("claude", "gemini", "chatgpt") or None
            clear_formatted: Whether to clear cached formatted text (default: False)
        """
        self.state.format_provider = provider
        if clear_formatted:
            self.state.formatted_text = None

    def toggle_theme(self) -> None:
        """Toggle between dark and light theme mode."""
        self.state.is_dark_mode = not self.state.is_dark_mode

    def set_url_field(self, value: str) -> None:
        """Update URL field UI control.

        Args:
            value: The URL value to set
        """
        self.controls.url_field.value = value

    def set_status(self, message: str) -> None:
        """Update status text UI control.

        Args:
            message: The status message to display
        """
        self.controls.status_text.value = message

    def set_progress_visible(self, visible: bool) -> None:
        """Show or hide the progress ring.

        Args:
            visible: Whether to show the progress indicator
        """
        self.controls.progress_ring.visible = visible
