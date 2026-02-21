"""Tests for app.core.preset_manager."""

import json

import pytest

from app.core.preset_manager import (
    PRESETS_FILE,
    ProjectPreset,
    add_preset,
    delete_preset,
    load_presets,
    make_preset,
    save_presets,
)


def _make_preset(name: str = "My Stack", **kwargs):
    """Create a test preset with sensible defaults."""
    defaults = {
        "name": name,
        "python_version": "3.14",
        "git_enabled": True,
        "include_starter_files": True,
        "ui_project_enabled": False,
        "framework": None,
        "other_project_enabled": False,
        "project_type": None,
        "folders": ["core", "utils"],
        "packages": ["httpx"],
        "saved_at": "2026-02-19T10:00:00+00:00",
    }
    defaults.update(kwargs)
    return ProjectPreset(**defaults)


@pytest.fixture(autouse=True)
def _use_tmp_presets(tmp_path, monkeypatch):
    """Redirect PRESETS_FILE to a temp directory for every test."""
    tmp_file = tmp_path / "presets.json"
    monkeypatch.setattr("app.core.preset_manager.PRESETS_FILE", tmp_file)
    monkeypatch.setattr("app.core.preset_manager.SETTINGS_DIR", tmp_path)


def test_load_empty():
    """Returns empty list when no file exists."""
    assert load_presets() == []


def test_save_and_load_roundtrip():
    """Presets survive a save/load cycle."""
    preset = _make_preset()
    save_presets([preset])
    loaded = load_presets()
    assert len(loaded) == 1
    assert loaded[0].name == "My Stack"
    assert loaded[0].packages == ["httpx"]


def test_add_preset_prepends():
    """New preset is added at the front."""
    add_preset(_make_preset(name="First"))
    add_preset(_make_preset(name="Second"))
    presets = load_presets()
    assert len(presets) == 2
    assert presets[0].name == "Second"
    assert presets[1].name == "First"


def test_deduplication_by_name():
    """Same name replaces old preset at top."""
    add_preset(_make_preset(name="dup", packages=["old-pkg"]))
    add_preset(_make_preset(name="other"))
    add_preset(_make_preset(name="dup", packages=["new-pkg"]))

    presets = load_presets()
    assert len(presets) == 2
    assert presets[0].name == "dup"
    assert presets[0].packages == ["new-pkg"]


def test_delete_preset():
    """Delete removes preset by name."""
    add_preset(_make_preset(name="keep"))
    add_preset(_make_preset(name="remove"))
    delete_preset("remove")

    presets = load_presets()
    assert len(presets) == 1
    assert presets[0].name == "keep"


def test_delete_nonexistent():
    """Delete of nonexistent name is a no-op."""
    add_preset(_make_preset(name="only"))
    delete_preset("ghost")
    assert len(load_presets()) == 1


def test_no_cap_on_count():
    """Unlike history, presets have no entry limit."""
    for i in range(25):
        add_preset(_make_preset(name=f"preset-{i}"))
    assert len(load_presets()) == 25


def test_corrupt_file_returns_empty(tmp_path, monkeypatch):
    """Corrupt JSON returns empty list."""
    tmp_file = tmp_path / "presets.json"
    monkeypatch.setattr("app.core.preset_manager.PRESETS_FILE", tmp_file)
    tmp_file.write_text("not json at all", encoding="utf-8")
    assert load_presets() == []


def test_non_list_json_returns_empty(tmp_path, monkeypatch):
    """JSON that is not a list returns empty list."""
    tmp_file = tmp_path / "presets.json"
    monkeypatch.setattr("app.core.preset_manager.PRESETS_FILE", tmp_file)
    tmp_file.write_text('{"name": "oops"}', encoding="utf-8")
    assert load_presets() == []


def test_unknown_keys_ignored(tmp_path, monkeypatch):
    """Future keys in JSON are silently dropped."""
    tmp_file = tmp_path / "presets.json"
    monkeypatch.setattr("app.core.preset_manager.PRESETS_FILE", tmp_file)
    data = [
        {
            "name": "test",
            "python_version": "3.14",
            "git_enabled": True,
            "include_starter_files": False,
            "ui_project_enabled": False,
            "framework": None,
            "other_project_enabled": False,
            "project_type": None,
            "folders": [],
            "packages": [],
            "future_field": "ignored",
        }
    ]
    tmp_file.write_text(json.dumps(data), encoding="utf-8")
    presets = load_presets()
    assert len(presets) == 1
    assert presets[0].name == "test"
    assert not hasattr(presets[0], "future_field")


def test_invalid_entry_skipped(tmp_path, monkeypatch):
    """Entries missing required fields are skipped."""
    tmp_file = tmp_path / "presets.json"
    monkeypatch.setattr("app.core.preset_manager.PRESETS_FILE", tmp_file)
    data = [{"name": "incomplete"}, "not a dict"]
    tmp_file.write_text(json.dumps(data), encoding="utf-8")
    assert load_presets() == []


def test_make_preset_sets_timestamp():
    """make_preset fills saved_at with an ISO timestamp."""
    preset = make_preset(
        name="ts-test",
        python_version="3.14",
        git_enabled=True,
        include_starter_files=True,
        ui_project_enabled=False,
        framework=None,
        other_project_enabled=False,
        project_type=None,
        folders=["core"],
        packages=["flask"],
    )
    assert preset.saved_at
    assert "T" in preset.saved_at


def test_dev_packages_preserved():
    """Dev packages roundtrip through save/load."""
    preset = _make_preset(dev_packages=["pytest", "ruff"])
    save_presets([preset])
    loaded = load_presets()
    assert loaded[0].dev_packages == ["pytest", "ruff"]


def test_metadata_fields_preserved():
    """Author, email, description, license roundtrip."""
    preset = _make_preset(
        author_name="Alice",
        author_email="alice@example.com",
        description="My project",
        license_type="MIT",
    )
    save_presets([preset])
    loaded = load_presets()
    assert loaded[0].author_name == "Alice"
    assert loaded[0].author_email == "alice@example.com"
    assert loaded[0].description == "My project"
    assert loaded[0].license_type == "MIT"


def test_framework_and_project_type():
    """Framework and project type are stored correctly."""
    preset = _make_preset(
        ui_project_enabled=True,
        framework="Flet",
        other_project_enabled=True,
        project_type="FastAPI",
    )
    save_presets([preset])
    loaded = load_presets()
    assert loaded[0].framework == "Flet"
    assert loaded[0].project_type == "FastAPI"
    assert loaded[0].ui_project_enabled is True
    assert loaded[0].other_project_enabled is True
