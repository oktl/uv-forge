"""Tests for validate_folder_name function including file support.

Tests the enhanced validate_folder_name that now supports file names
with dots for extensions.
"""

import pytest
from app.core.validator import validate_folder_name


class TestValidateFolderName:
    """Tests for folder and file name validation."""

    @pytest.mark.parametrize(
        "name",
        [
            "simple",
            "with_underscore",
            "with-hyphen",
            "MixedCase123",
            "config.py",
            "requirements.txt",
            "data.json",
            "component.test.tsx",
            "archive.tar.gz",
            ".gitignore",
            ".env.local",
        ],
    )
    def test_valid_names(self, name):
        """Test that valid folder and file names pass validation."""
        is_valid, error = validate_folder_name(name)
        assert is_valid, f"Expected '{name}' to be valid, got error: {error}"
        assert error == ""

    @pytest.mark.parametrize(
        "name,expected_error_substring",
        [
            ("", "cannot be empty"),
            ("my folder", "can only contain"),
            ("folder@name", "can only contain"),
            ("folder#123", "can only contain"),
            ("folder/path", "can only contain"),
            ("folder\\path", "can only contain"),
            ("folder:name", "can only contain"),
            ("folder*", "can only contain"),
            ("folder?", "can only contain"),
            ("~", "can only contain"),  # ~ is invalid character, not reserved name
            (".", "reserved name"),
            ("..", "reserved name"),
        ],
    )
    def test_invalid_names(self, name, expected_error_substring):
        """Test that invalid names fail validation with appropriate errors."""
        is_valid, error = validate_folder_name(name)
        assert not is_valid, f"Expected '{name}' to be invalid"
        assert expected_error_substring.lower() in error.lower(), (
            f"Expected error to contain '{expected_error_substring}', got: {error}"
        )

    def test_allows_dots_for_files(self):
        """Test that dots are allowed (for file extensions)."""
        test_files = [
            "config.py",
            "test.spec.ts",
            "package.json",
            "index.html",
        ]

        for filename in test_files:
            is_valid, error = validate_folder_name(filename)
            assert is_valid, f"File '{filename}' should be valid"

    def test_rejects_only_dots(self):
        """Test that names consisting only of dots are rejected."""
        invalid_dots = [".", "..", "..."]

        for name in invalid_dots:
            is_valid, _ = validate_folder_name(name)
            # Only . and .. are explicitly reserved, but ... is just unusual
            if name in (".", ".."):
                assert not is_valid, f"'{name}' should be invalid (reserved)"

    def test_error_message_format(self):
        """Test that error messages are properly formatted."""
        # Empty name
        is_valid, error = validate_folder_name("")
        assert not is_valid
        assert error.startswith("Name cannot be empty")

        # Invalid characters
        is_valid, error = validate_folder_name("bad@name")
        assert not is_valid
        assert "can only contain" in error.lower()
        assert "letters" in error.lower()

        # Reserved name
        is_valid, error = validate_folder_name(".")
        assert not is_valid
        assert "reserved" in error.lower()
