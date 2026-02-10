"""Test suite for project_builder.py"""

import tempfile
from pathlib import Path

from app.core.project_builder import cleanup_on_error


class TestCleanupOnError:
    """Tests for the cleanup_on_error rollback function"""

    def test_removes_project_directory(self):
        """Test that the project directory is removed on cleanup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "myproject"
            project_path.mkdir()
            assert project_path.exists()

            cleanup_on_error(project_path)

            assert not project_path.exists()

    def test_removes_bare_repo_when_provided(self):
        """Test that the bare hub repo is removed alongside the project dir"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "myproject"
            project_path.mkdir()
            bare_repo = Path(tmpdir) / "myproject.git"
            bare_repo.mkdir()

            cleanup_on_error(project_path, bare_repo)

            assert not project_path.exists()
            assert not bare_repo.exists()

    def test_bare_repo_none_does_not_raise(self):
        """Test that passing None for bare_repo_path is safe (git disabled)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "myproject"
            project_path.mkdir()

            cleanup_on_error(project_path, None)

            assert not project_path.exists()

    def test_handles_nonexistent_project_path(self):
        """Test that cleanup is safe when the project dir was never created"""
        nonexistent = Path("/tmp/nonexistent_create_project_test_xyz")
        cleanup_on_error(nonexistent)  # Should not raise

    def test_handles_nonexistent_bare_repo(self):
        """Test that cleanup is safe when bare repo was never created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "myproject"
            project_path.mkdir()
            nonexistent_bare = Path(tmpdir) / "nonexistent.git"

            cleanup_on_error(project_path, nonexistent_bare)  # Should not raise

            assert not project_path.exists()

    def test_removes_nested_project_contents(self):
        """Test that cleanup recursively removes nested files and directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "myproject"
            nested = project_path / "app" / "core"
            nested.mkdir(parents=True)
            (nested / "state.py").write_text("# state")

            cleanup_on_error(project_path)

            assert not project_path.exists()
