"""Tests for FolderHandlersMixin — _get_folder_hierarchy, _navigate_to_parent, _on_item_click."""

from unittest.mock import Mock

import pytest

from app.core.state import AppState
from app.handlers.ui_handler import Handlers


class MockControl:
    def __init__(self, value=None):
        self.value = value
        self.visible = True
        self.disabled = False
        self.color = None
        self.data = {}

    async def focus(self):
        pass


class MockText:
    def __init__(self, value=""):
        self.value = value
        self.color = None


class MockContainer:
    def __init__(self):
        self.content = Mock()
        self.content.controls = []
        self.border = None


class MockPage:
    def __init__(self):
        self.updated = False
        self.overlay = []
        self.appbar = None
        self.bottom_appbar = Mock()
        self.bottom_appbar.bgcolor = None
        self.theme_mode = None
        self.window = Mock()
        self.opened_controls = []

    def update(self):
        self.updated = True

    def show_dialog(self, control):
        self.opened_controls.append(control)


class MockControls:
    def __init__(self):
        self.warning_banner = MockText()
        self.path_preview_text = MockControl()
        self.status_icon = MockControl()
        self.status_text = MockText()
        self.copy_path_button = MockControl()
        self.project_path_input = MockControl(value="/test/path")
        self.project_name_input = MockControl(value="")
        self.python_version_dropdown = MockControl(value="3.14")
        self.create_git_checkbox = MockControl(value=False)
        self.include_starter_files_checkbox = MockControl(value=False)
        self.ui_project_checkbox = MockControl(value=False)
        self.other_projects_checkbox = MockControl(value=False)
        self.auto_save_folder_changes = MockControl(value=False)
        self.app_subfolders_label = MockText()
        self.subfolders_container = MockContainer()
        self.packages_label = MockText()
        self.packages_container = MockContainer()
        self.add_package_button = MockControl()
        self.remove_package_button = MockControl()
        self.clear_packages_button = MockControl()
        self.progress_ring = MockControl()
        self.build_project_button = MockControl()
        self.reset_button = MockControl()
        self.exit_button = MockControl()
        self.theme_toggle_button = Mock(icon=None)
        self.about_menu_item = MockControl()
        self.help_menu_item = MockControl()
        self.git_cheat_sheet_menu_item = MockControl()
        self.settings_menu_item = MockControl()
        self.history_menu_item = MockControl()
        self.log_viewer_menu_item = MockControl()
        self.overflow_menu = MockControl()
        self.check_pypi_button = MockControl()
        self.pypi_status_text = MockText()
        self.metadata_button = MockControl()
        self.metadata_summary = MockText()
        self.section_titles = []
        self.section_containers = []


@pytest.fixture
def mock_handlers():
    page = MockPage()
    controls = MockControls()
    state = AppState()
    handlers = Handlers(page, controls, state)
    return handlers, state


class TestGetFolderHierarchy:
    """Tests for FolderHandlersMixin._get_folder_hierarchy."""

    def test_empty_folders_returns_empty_list(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = []
        result = handlers._get_folder_hierarchy()
        assert result == []

    def test_single_root_folder(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [{"name": "core", "subfolders": [], "files": []}]
        result = handlers._get_folder_hierarchy()
        assert len(result) == 1
        assert result[0]["label"] == "core/"
        assert result[0]["path"] == [0]

    def test_multiple_root_folders(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [
            {"name": "core", "subfolders": [], "files": []},
            {"name": "ui", "subfolders": [], "files": []},
            {"name": "utils", "subfolders": [], "files": []},
        ]
        result = handlers._get_folder_hierarchy()
        labels = [r["label"] for r in result]
        assert "core/" in labels
        assert "ui/" in labels
        assert "utils/" in labels
        assert len(result) == 3

    def test_nested_subfolders_included(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [
            {
                "name": "app",
                "subfolders": [
                    {"name": "core", "subfolders": [], "files": []},
                    {"name": "ui", "subfolders": [], "files": []},
                ],
                "files": [],
            }
        ]
        result = handlers._get_folder_hierarchy()
        # Should have: app/, app/core/, app/ui/
        assert len(result) == 3
        labels = [r["label"] for r in result]
        assert "app/" in labels
        assert "app/core/" in labels
        assert "app/ui/" in labels

    def test_nested_paths_are_correct(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [
            {
                "name": "app",
                "subfolders": [
                    {"name": "core", "subfolders": [], "files": []}
                ],
                "files": [],
            }
        ]
        result = handlers._get_folder_hierarchy()
        app_entry = next(r for r in result if r["label"] == "app/")
        core_entry = next(r for r in result if r["label"] == "app/core/")
        assert app_entry["path"] == [0]
        assert core_entry["path"] == [0, "subfolders", 0]

    def test_deeply_nested_hierarchy(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [
            {
                "name": "a",
                "subfolders": [
                    {
                        "name": "b",
                        "subfolders": [
                            {"name": "c", "subfolders": [], "files": []}
                        ],
                        "files": [],
                    }
                ],
                "files": [],
            }
        ]
        result = handlers._get_folder_hierarchy()
        labels = [r["label"] for r in result]
        assert "a/" in labels
        assert "a/b/" in labels
        assert "a/b/c/" in labels


class TestNavigateToParent:
    """Tests for FolderHandlersMixin._navigate_to_parent."""

    def test_none_path_returns_root_and_none(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [{"name": "core", "subfolders": [], "files": []}]
        container, idx = handlers._navigate_to_parent(None)
        assert container is state.folders
        assert idx is None

    def test_empty_path_returns_root_and_none(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [{"name": "core", "subfolders": [], "files": []}]
        container, idx = handlers._navigate_to_parent([])
        assert container is state.folders
        assert idx is None

    def test_root_level_path(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [
            {"name": "a", "subfolders": [], "files": []},
            {"name": "b", "subfolders": [], "files": []},
        ]
        container, idx = handlers._navigate_to_parent([1])
        assert container is state.folders
        assert idx == 1

    def test_subfolder_path(self, mock_handlers):
        handlers, state = mock_handlers
        sub = {"name": "child", "subfolders": [], "files": []}
        parent = {"name": "parent", "subfolders": [sub], "files": []}
        state.folders = [parent]
        container, idx = handlers._navigate_to_parent([0, "subfolders", 0])
        assert container == [sub]
        assert idx == 0

    def test_file_path(self, mock_handlers):
        handlers, state = mock_handlers
        folder = {"name": "src", "subfolders": [], "files": ["main.py", "utils.py"]}
        state.folders = [folder]
        container, idx = handlers._navigate_to_parent([0, "files", 1])
        assert container == ["main.py", "utils.py"]
        assert idx == 1


class TestOnItemClick:
    """Tests for FolderHandlersMixin._on_item_click."""

    def test_sets_selected_item_path_and_type(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [{"name": "core", "subfolders": [], "files": []}]

        event = Mock()
        event.control.data = {"path": [0], "type": "folder", "name": "core"}

        handlers._on_item_click(event)

        assert state.selected_item_path == [0]
        assert state.selected_item_type == "folder"

    def test_sets_status_message(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [{"name": "core", "subfolders": [], "files": []}]

        event = Mock()
        event.control.data = {"path": [0], "type": "folder", "name": "core"}

        handlers._on_item_click(event)

        assert "folder" in handlers.controls.status_text.value.lower()
        assert "core" in handlers.controls.status_text.value

    def test_file_item_click(self, mock_handlers):
        handlers, state = mock_handlers
        state.folders = [{"name": "core", "subfolders": [], "files": ["state.py"]}]

        event = Mock()
        event.control.data = {
            "path": [0, "files", 0],
            "type": "file",
            "name": "state.py",
        }

        handlers._on_item_click(event)

        assert state.selected_item_path == [0, "files", 0]
        assert state.selected_item_type == "file"
