"""Configuration manager for folder preferences.

This module handles loading folder structure configurations from templates.
Templates are organized in subdirectories:
- app/config/templates/ui_frameworks/ - UI framework templates (Flet, PyQt6, etc.)
- app/config/templates/project_types/ - Project type templates (Django, FastAPI, etc.)
"""

import json
from pathlib import Path
from typing import Any, Optional

from app.core.boilerplate_resolver import normalize_framework_name
from app.utils.constants import (
    TEMPLATES_DIR,
    UI_TEMPLATES_DIR,
    PROJECT_TYPE_TEMPLATES_DIR,
    DEFAULT_FOLDERS,
)


class ConfigManager:
    """Manages loading folder configuration from templates.

    Loads folder structure templates from organized subdirectories:
    - UI frameworks: app/config/templates/ui_frameworks/ (e.g., flet.json, pyqt6.json)
    - Project types: app/config/templates/project_types/ (e.g., django.json, fastapi.json)

    Attributes:
        config_source: Path to the active template file being used.
        settings: Current configuration dictionary with 'folders' key.
        loaded_framework: Name of framework whose config is currently loaded.
    """

    def __init__(self):
        """Initialize ConfigManager and load default settings."""
        self.config_source: Path = UI_TEMPLATES_DIR / "default.json"
        self.loaded_framework: Optional[str] = None
        self.settings: dict[str, Any] = self.load_config()

    def _normalize_framework_name(self, framework: str) -> str:
        """Convert framework display name to template filename.

        Args:
            framework: Framework display name (e.g., "PyQt6", "tkinter (built-in)").

        Returns:
            Normalized framework name for template filename (e.g., "pyqt6", "tkinter").
        """
        return normalize_framework_name(framework)

    def _load_template(self, template_path: Path) -> Optional[dict[str, Any]]:
        """Load and parse a template file.

        Args:
            template_path: Path to the JSON template file.

        Returns:
            Dictionary containing configuration with 'folders' key, or None if
            the file doesn't exist or cannot be parsed.
        """
        if not template_path.exists():
            return None
        try:
            with open(template_path, "r") as f:
                data = json.load(f)
                return {"folders": data.get("folders", DEFAULT_FOLDERS.copy())}
        except json.JSONDecodeError, OSError:
            return None

    def load_config(self, framework: Optional[str] = None) -> dict[str, Any]:
        """Load folder configuration from template files.

        Precedence:
        1. Framework-specific template (if framework specified)
            - Handles both UI frameworks (ui_frameworks/) and project types (project_types/)
        2. Default template (ui_frameworks/default.json)
        3. Hard-coded DEFAULT_FOLDERS constant

        Args:
            framework: Optional framework name to load framework-specific template.
                    Can be a simple name like "flet" or a path like "project_types/django".

        Returns:
            Dictionary containing 'folders' key with folder structure configuration.
        """
        defaults = {"folders": DEFAULT_FOLDERS.copy()}

        # Try framework-specific template
        if framework:
            # Check if it's already a path (e.g., "project_types/django")
            if "/" in framework:
                template_path = TEMPLATES_DIR / f"{framework}.json"
            else:
                # UI framework - look in ui_frameworks directory
                normalized = self._normalize_framework_name(framework)
                template_path = UI_TEMPLATES_DIR / f"{normalized}.json"

            settings = self._load_template(template_path)
            if settings:
                self.config_source = template_path
                self.loaded_framework = framework
                self.settings = settings
                return settings

        # Fall back to default template
        default_template = UI_TEMPLATES_DIR / "default.json"
        settings = self._load_template(default_template)
        if settings:
            self.config_source = default_template
            self.loaded_framework = framework
            self.settings = settings
            return settings

        # Final fallback to hard-coded defaults
        self.config_source = default_template  # For display purposes
        self.loaded_framework = framework
        self.settings = defaults
        return defaults

    def save_config(self, settings: Optional[dict[str, Any]] = None) -> None:
        """Save folder structure to the active template.

        Writes the current settings to the template file being used.

        Args:
            settings: Optional settings dictionary to save. If None, uses self.settings
        """
        if settings is None:
            settings = self.settings

        with open(self.config_source, "w") as f:
            json.dump({"folders": settings["folders"]}, f, indent=2)

    def get_config_display_name(self) -> str:
        """Get a user-friendly name for the active config source.

        Returns:
            String like "default", "flet", "pyqt6", etc.
        """
        # Get template filename without extension
        template_name = self.config_source.stem

        # If it's a framework template, show framework name
        if self.loaded_framework and template_name != "default":
            return f"{template_name} template"

        return f"{template_name} template"
