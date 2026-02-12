"""Test suite for boilerplate_resolver.py"""

import tempfile
from pathlib import Path

import pytest

from app.core.boilerplate_resolver import BoilerplateResolver, normalize_framework_name


class TestNormalizeFrameworkName:
    """Tests for normalize_framework_name function."""

    @pytest.mark.parametrize(
        "input_name, expected",
        [
            ("flet", "flet"),
            ("PyQt6", "pyqt6"),
            ("PySide6", "pyside6"),
            ("tkinter (built-in)", "tkinter"),
            ("customtkinter", "customtkinter"),
            ("kivy", "kivy"),
            ("pygame", "pygame"),
            ("nicegui", "nicegui"),
            ("streamlit", "streamlit"),
            ("gradio", "gradio"),
        ],
    )
    def test_normalize_names(self, input_name, expected):
        assert normalize_framework_name(input_name) == expected

    def test_spaces_replaced_with_underscores(self):
        assert normalize_framework_name("some framework") == "some_framework"


class TestBoilerplateResolverInit:
    """Tests for BoilerplateResolver constructor and search_dirs ordering."""

    def test_framework_only(self):
        resolver = BoilerplateResolver(
            "myproj", framework="flet", boilerplate_dir=Path("/bp")
        )
        assert resolver.search_dirs == [
            Path("/bp/ui_frameworks/flet"),
            Path("/bp/common"),
        ]

    def test_project_type_only(self):
        resolver = BoilerplateResolver(
            "myproj", project_type="django", boilerplate_dir=Path("/bp")
        )
        assert resolver.search_dirs == [
            Path("/bp/project_types/django"),
            Path("/bp/common"),
        ]

    def test_both_framework_and_project_type(self):
        resolver = BoilerplateResolver(
            "myproj",
            framework="PyQt6",
            project_type="fastapi",
            boilerplate_dir=Path("/bp"),
        )
        assert resolver.search_dirs == [
            Path("/bp/ui_frameworks/pyqt6"),
            Path("/bp/project_types/fastapi"),
            Path("/bp/common"),
        ]

    def test_neither_framework_nor_project_type(self):
        resolver = BoilerplateResolver("myproj", boilerplate_dir=Path("/bp"))
        assert resolver.search_dirs == [Path("/bp/common")]

    def test_framework_name_normalized_in_path(self):
        resolver = BoilerplateResolver(
            "myproj",
            framework="tkinter (built-in)",
            boilerplate_dir=Path("/bp"),
        )
        assert resolver.search_dirs[0] == Path("/bp/ui_frameworks/tkinter")


class TestBoilerplateResolverResolve:
    """Tests for BoilerplateResolver.resolve() fallback chain."""

    def _make_bp_dir(self, tmpdir: Path) -> Path:
        """Create a boilerplate directory structure for testing."""
        bp = tmpdir / "boilerplate"
        (bp / "common").mkdir(parents=True)
        (bp / "ui_frameworks" / "flet").mkdir(parents=True)
        (bp / "project_types" / "django").mkdir(parents=True)
        return bp

    def test_resolve_from_common(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = self._make_bp_dir(Path(tmpdir))
            (bp / "common" / "constants.py").write_text("APP = '{{project_name}}'")
            resolver = BoilerplateResolver("demo", boilerplate_dir=bp)
            result = resolver.resolve("constants.py")
            assert result == "APP = 'Demo'"

    def test_resolve_from_framework(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = self._make_bp_dir(Path(tmpdir))
            (bp / "ui_frameworks" / "flet" / "main.py").write_text("# flet main")
            (bp / "common" / "main.py").write_text("# common main")
            resolver = BoilerplateResolver("demo", framework="flet", boilerplate_dir=bp)
            result = resolver.resolve("main.py")
            assert result == "# flet main"

    def test_framework_falls_through_to_common(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = self._make_bp_dir(Path(tmpdir))
            (bp / "common" / "utils.py").write_text("# common utils")
            resolver = BoilerplateResolver("demo", framework="flet", boilerplate_dir=bp)
            result = resolver.resolve("utils.py")
            assert result == "# common utils"

    def test_project_type_before_common(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = self._make_bp_dir(Path(tmpdir))
            (bp / "project_types" / "django" / "settings.py").write_text("# django")
            (bp / "common" / "settings.py").write_text("# common")
            resolver = BoilerplateResolver(
                "demo", project_type="django", boilerplate_dir=bp
            )
            result = resolver.resolve("settings.py")
            assert result == "# django"

    def test_framework_before_project_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = self._make_bp_dir(Path(tmpdir))
            (bp / "ui_frameworks" / "flet" / "main.py").write_text("# flet")
            (bp / "project_types" / "django" / "main.py").write_text("# django")
            resolver = BoilerplateResolver(
                "demo",
                framework="flet",
                project_type="django",
                boilerplate_dir=bp,
            )
            result = resolver.resolve("main.py")
            assert result == "# flet"

    def test_resolve_returns_none_for_unknown_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = self._make_bp_dir(Path(tmpdir))
            resolver = BoilerplateResolver("demo", boilerplate_dir=bp)
            assert resolver.resolve("nonexistent.py") is None

    def test_resolve_with_missing_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = Path(tmpdir) / "empty_bp"
            bp.mkdir()
            (bp / "common").mkdir()
            resolver = BoilerplateResolver(
                "demo", framework="flet", boilerplate_dir=bp
            )
            # ui_frameworks/flet doesn't exist — should not error
            assert resolver.resolve("anything.py") is None


class TestBoilerplateResolverSubstitute:
    """Tests for placeholder substitution."""

    def test_project_name_substitution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = Path(tmpdir)
            (bp / "common").mkdir()
            (bp / "common" / "cfg.py").write_text('NAME = "{{project_name}}"')
            resolver = BoilerplateResolver("my_app", boilerplate_dir=bp)
            assert resolver.resolve("cfg.py") == 'NAME = "My App"'

    def test_no_placeholder_passthrough(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = Path(tmpdir)
            (bp / "common").mkdir()
            (bp / "common" / "plain.py").write_text("x = 1")
            resolver = BoilerplateResolver("proj", boilerplate_dir=bp)
            assert resolver.resolve("plain.py") == "x = 1"

    def test_multiple_placeholders(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp = Path(tmpdir)
            (bp / "common").mkdir()
            content = "a={{project_name}} b={{project_name}}"
            (bp / "common" / "multi.py").write_text(content)
            resolver = BoilerplateResolver("demo", boilerplate_dir=bp)
            assert resolver.resolve("multi.py") == "a=Demo b=Demo"
