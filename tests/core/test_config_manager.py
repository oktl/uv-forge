"""Test suite for ConfigManager class"""

import json
import tempfile
from pathlib import Path
import pytest

from app.core.config_manager import ConfigManager


class TestConfigManagerInit:
    """Tests for ConfigManager initialization"""

    def test_init_creates_valid_manager(self):
        """Test ConfigManager initialization"""
        manager = ConfigManager()

        # Check if settings is a dict (not a method object)
        assert isinstance(manager.settings, dict)

        # Check if settings has 'folders' key
        assert "folders" in manager.settings

        # Check if config_source is a Path
        assert isinstance(manager.config_source, Path)


class TestLoadTemplate:
    """Tests for template loading"""

    def test_returns_none_for_nonexistent_file(self):
        """Test returns None for non-existent file"""
        manager = ConfigManager()
        result = manager._load_template(Path("/nonexistent/path.json"))
        assert result is None

    def test_loads_valid_json_template(self):
        """Test loads valid JSON file"""
        manager = ConfigManager()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"folders": ["src", "tests"]}, f)
            temp_path = Path(f.name)

        try:
            result = manager._load_template(temp_path)
            assert result is not None
            assert isinstance(result, dict)
            assert "folders" in result
        finally:
            temp_path.unlink()

    def test_returns_none_for_invalid_json(self):
        """Test returns None for invalid JSON file"""
        manager = ConfigManager()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)

        try:
            result = manager._load_template(temp_path)
            assert result is None
        finally:
            temp_path.unlink()


class TestUpdateConfigState:
    """Tests for config state updates"""

    def test_update_config_state_sets_attributes(self):
        """Test _update_config_state updates all config attributes"""
        manager = ConfigManager()
        test_path = Path("/test/path.json")
        test_template = "flet"
        test_settings = {"folders": ["src", "tests"]}

        manager._update_config_state(test_path, test_template, test_settings)

        assert manager.config_source == test_path
        assert manager.loaded_template == test_template
        assert manager.settings == test_settings

    def test_update_config_state_with_none_template(self):
        """Test _update_config_state with None loaded_template"""
        manager = ConfigManager()
        test_path = Path("/test/default.json")
        test_settings = {"folders": []}

        manager._update_config_state(test_path, None, test_settings)

        assert manager.loaded_template is None


class TestLoadConfig:
    """Tests for config loading"""

    def test_load_config_without_template(self):
        """Test load without template (should use default)"""
        manager = ConfigManager()
        config = manager.load_config()

        assert isinstance(config, dict)
        assert "folders" in config

    def test_load_config_with_nonexistent_template(self):
        """Test load with non-existent template (should fall back to default)"""
        manager = ConfigManager()
        config = manager.load_config("nonexistent_framework")

        assert isinstance(config, dict)
        assert "folders" in config


class TestGetConfigDisplayName:
    """Tests for config display name generation"""

    def test_returns_valid_display_name(self):
        """Test returns valid display name"""
        manager = ConfigManager()
        display_name = manager.get_config_display_name()

        assert isinstance(display_name, str)
        assert len(display_name) > 0
        assert display_name.endswith(" template")

    def test_display_name_includes_template_suffix(self):
        """Test display name always includes ' template' suffix"""
        manager = ConfigManager()
        manager.load_config()
        display_name = manager.get_config_display_name()

        assert " template" in display_name
        assert display_name.endswith(" template")
