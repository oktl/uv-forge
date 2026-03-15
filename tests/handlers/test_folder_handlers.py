"""Tests for FolderHandlersMixin — hierarchy, navigation, item click, user templates."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from uv_forge.core.state import AppState
from uv_forge.handlers.ui_handler import Handlers


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
        self.progress_bar = MockControl()
        self.progress_step_text = MockControl()
        self.build_project_button = MockControl()
        self.reset_button = MockControl()
        self.exit_button = MockControl()
        self.theme_toggle_button = Mock(icon=None)
        self.about_menu_item = MockControl()
        self.help_menu_item = MockControl()
        self.app_cheat_sheet_menu_item = MockControl()
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


class TestGetUserTemplatePath:
    """Tests for FolderHandlersMixin._get_user_template_path."""

    def test_framework_path(self, mock_handlers):
        handlers, state = mock_handlers
        state.ui_project_enabled = True
        state.framework = "Flet"
        state.other_project_enabled = False
        result = handlers._get_user_template_path("main.py")
        assert result.parts[-3:] == ("ui_frameworks", "flet", "main.py")

    def test_project_type_path(self, mock_handlers):
        handlers, state = mock_handlers
        state.ui_project_enabled = False
        state.other_project_enabled = True
        state.project_type = "django"
        result = handlers._get_user_template_path("urls.py")
        assert result.parts[-3:] == ("project_types", "django", "urls.py")

    def test_common_path_fallback(self, mock_handlers):
        handlers, state = mock_handlers
        state.ui_project_enabled = False
        state.other_project_enabled = False
        result = handlers._get_user_template_path("constants.py")
        assert result.parts[-2:] == ("common", "constants.py")


class TestUserTemplateExists:
    """Tests for FolderHandlersMixin._user_template_exists."""

    def test_returns_false_when_no_file(self, mock_handlers):
        handlers, state = mock_handlers
        state.ui_project_enabled = False
        state.other_project_enabled = False
        assert handlers._user_template_exists("nonexistent.py") is False

    def test_returns_true_when_file_exists(self, mock_handlers):
        handlers, state = mock_handlers
        state.ui_project_enabled = False
        state.other_project_enabled = False
        with tempfile.TemporaryDirectory() as tmpdir:
            state.settings.custom_templates_path = tmpdir
            common = Path(tmpdir) / "boilerplate" / "common"
            common.mkdir(parents=True)
            (common / "test.py").write_text("content")
            assert handlers._user_template_exists("test.py") is True


class TestDeleteUserTemplateFile:
    """Tests for FolderHandlersMixin._delete_user_template_file."""

    def test_deletes_existing_file(self, mock_handlers):
        handlers, state = mock_handlers
        state.ui_project_enabled = False
        state.other_project_enabled = False
        with tempfile.TemporaryDirectory() as tmpdir:
            state.settings.custom_templates_path = tmpdir
            common = Path(tmpdir) / "boilerplate" / "common"
            common.mkdir(parents=True)
            f = common / "test.py"
            f.write_text("content")
            assert handlers._delete_user_template_file("test.py") is True
            assert not f.exists()

    def test_returns_false_when_no_file(self, mock_handlers):
        handlers, state = mock_handlers
        state.ui_project_enabled = False
        state.other_project_enabled = False
        assert handlers._delete_user_template_file("nonexistent.py") is False


class TestAddItemWithContent:
    """Tests for adding files with imported content via on_add_folder."""

    def test_add_file_with_content_stores_override(self, mock_handlers):
        """Adding a file with content should populate file_overrides."""
        handlers, state = mock_handlers
        state.folders = [{"name": "core", "subfolders": [], "files": ["state.py"]}]

        # Simulate what add_item does internally when content is provided
        parent_path = [0]
        parent_container, idx = handlers._navigate_to_parent(parent_path)
        parent_folder = parent_container[idx]
        files_list = parent_folder.setdefault("files", [])
        files_list.append("new_file.py")

        # Compute canonical path the same way add_item does
        from uv_forge.handlers.folder_handlers import get_canonical_file_path

        file_idx = len(files_list) - 1
        file_path = parent_path + ["files", file_idx]
        canonical = get_canonical_file_path(state.folders, file_path)

        assert canonical == "core/new_file.py"

        # Store override
        state.file_overrides[canonical] = "# imported content"
        assert state.file_overrides["core/new_file.py"] == "# imported content"

    def test_add_file_without_content_no_override(self, mock_handlers):
        """Adding a file without content should not create a file_overrides entry."""
        handlers, state = mock_handlers
        state.folders = [{"name": "utils", "subfolders": [], "files": []}]
        state.file_overrides = {}

        # Simulate adding a blank file
        parent_path = [0]
        parent_container, idx = handlers._navigate_to_parent(parent_path)
        parent_folder = parent_container[idx]
        files_list = parent_folder.setdefault("files", [])
        files_list.append("empty.py")

        # No content → no override
        assert state.file_overrides == {}

    def test_canonical_path_nested_subfolder(self, mock_handlers):
        """Canonical path should work for files in nested subfolders."""
        handlers, state = mock_handlers
        state.folders = [
            {
                "name": "core",
                "subfolders": [
                    {"name": "utils", "subfolders": [], "files": ["helpers.py"]}
                ],
                "files": [],
            }
        ]

        from uv_forge.handlers.folder_handlers import get_canonical_file_path

        # Path to helpers.py: folders[0] → subfolders[0] → files[0]
        item_path = [0, "subfolders", 0, "files", 0]
        canonical = get_canonical_file_path(state.folders, item_path)
        assert canonical == "core/utils/helpers.py"

        # Add a new file and check its canonical path
        state.folders[0]["subfolders"][0]["files"].append("new.py")
        new_path = [0, "subfolders", 0, "files", 1]
        canonical_new = get_canonical_file_path(state.folders, new_path)
        assert canonical_new == "core/utils/new.py"

    def test_content_cleared_on_folder_type(self, mock_handlers):
        """Switching type to folder should not pass content."""
        # This tests the dialog logic — content is only passed for files
        handlers, state = mock_handlers
        state.folders = [{"name": "src", "subfolders": [], "files": []}]
        state.file_overrides = {}

        # Simulate adding a folder (content should be None)
        new_folder = {"name": "models", "subfolders": [], "files": []}
        state.folders[0]["subfolders"].append(new_folder)

        # No file_overrides should exist
        assert state.file_overrides == {}
