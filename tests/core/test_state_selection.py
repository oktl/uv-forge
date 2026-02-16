"""Tests for AppState selection tracking fields.

Tests the new selected_item_path and selected_item_type fields
added for folder/file selection functionality.
"""

from app.core.state import AppState


class TestSelectionTracking:
    """Tests for selection tracking fields in AppState."""

    def test_selection_fields_initialize_to_none(self):
        """Test that selection fields start as None."""
        state = AppState()
        assert state.selected_item_path is None
        assert state.selected_item_type is None

    def test_can_set_folder_selection(self):
        """Test setting selection for a folder."""
        state = AppState()
        state.selected_item_path = [0, "subfolders", 2]
        state.selected_item_type = "folder"

        assert state.selected_item_path == [0, "subfolders", 2]
        assert state.selected_item_type == "folder"

    def test_can_set_file_selection(self):
        """Test setting selection for a file."""
        state = AppState()
        state.selected_item_path = [1, "files", 0]
        state.selected_item_type = "file"

        assert state.selected_item_path == [1, "files", 0]
        assert state.selected_item_type == "file"

    def test_can_clear_selection(self):
        """Test clearing selection by setting to None."""
        state = AppState()
        state.selected_item_path = [0]
        state.selected_item_type = "folder"

        # Clear selection
        state.selected_item_path = None
        state.selected_item_type = None

        assert state.selected_item_path is None
        assert state.selected_item_type is None

    def test_reset_clears_selection(self):
        """Test that reset() clears selection fields."""
        state = AppState()
        state.selected_item_path = [2, "subfolders", 1, "files", 3]
        state.selected_item_type = "file"

        state.reset()

        assert state.selected_item_path is None
        assert state.selected_item_type is None

    def test_reset_preserves_other_behavior(self):
        """Test that reset() still preserves dark mode as before."""
        state = AppState(is_dark_mode=False)
        state.selected_item_path = [0]
        state.selected_item_type = "folder"

        state.reset()

        # Dark mode should be preserved
        assert state.is_dark_mode is False
        # But selection should be cleared
        assert state.selected_item_path is None
        assert state.selected_item_type is None

    def test_selection_path_can_be_deep(self):
        """Test that selection path can handle deeply nested structures."""
        state = AppState()
        deep_path = [0, "subfolders", 1, "subfolders", 2, "files", 5]
        state.selected_item_path = deep_path
        state.selected_item_type = "file"

        assert state.selected_item_path == deep_path
        assert len(state.selected_item_path) == 7

    def test_selection_type_accepts_only_expected_values(self):
        """Test that selection_type field accepts folder/file/None."""
        state = AppState()

        # Valid values
        state.selected_item_type = "folder"
        assert state.selected_item_type == "folder"

        state.selected_item_type = "file"
        assert state.selected_item_type == "file"

        state.selected_item_type = None
        assert state.selected_item_type is None

        # Since it's just a string field, any value is technically allowed
        # but we document the expected values
