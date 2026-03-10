"""Smoke tests for {{project_name}}."""


def test_app_imports():
    """Verify the app package is importable."""
    import app  # noqa: F401


def test_app_name(app_name):
    """Verify the project name fixture works."""
    assert app_name == "{{project_name}}"
