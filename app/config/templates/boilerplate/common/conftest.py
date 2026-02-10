"""Shared test fixtures for {{project_name}}."""

import pytest


@pytest.fixture
def app_name():
    """Return the application name."""
    return "{{project_name}}"
