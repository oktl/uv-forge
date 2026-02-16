"""Test suite for git_handler.py"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.handlers.git_handler import finalize_git_setup, handle_git_init


@pytest.fixture
def check_git_available():
    """Check if git is available for testing"""
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("Git is not available - tests require git to be installed")


class TestHandleGitInit:
    """Tests for handle_git_init function"""

    def test_initialize_git_repository(self, check_git_available):
        """Test initialize git repository when use_git=True"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            handle_git_init(project_path, use_git=True)

            git_dir = project_path / ".git"
            assert git_dir.exists()
            assert git_dir.is_dir()

    def test_dont_reinitialize_existing_repo(self, check_git_available):
        """Test don't reinitialize if .git already exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Initialize git first
            subprocess.run(
                ["git", "init"],
                cwd=project_path,
                capture_output=True,
                check=True
            )

            # Create a test file in .git to verify it's not overwritten
            test_file = project_path / ".git" / "test_marker.txt"
            test_file.write_text("existing")

            # Call handle_git_init
            handle_git_init(project_path, use_git=True)

            # Check that our marker file still exists
            assert test_file.exists()
            assert test_file.read_text() == "existing"

    def test_remove_git_repository(self, check_git_available):
        """Test remove .git directory when use_git=False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Initialize git first
            subprocess.run(
                ["git", "init"],
                cwd=project_path,
                capture_output=True,
                check=True
            )

            # Verify .git exists
            git_dir = project_path / ".git"
            assert git_dir.exists()

            # Remove git
            handle_git_init(project_path, use_git=False)

            # Check that .git was removed
            assert not git_dir.exists()

    def test_handle_removing_nonexistent_git(self, check_git_available):
        """Test handle removing non-existent .git"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Call with use_git=False when no .git exists
            # Should complete without error
            handle_git_init(project_path, use_git=False)

    def test_git_commands_work_correctly(self, check_git_available):
        """Test verify git commands work correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            handle_git_init(project_path, use_git=True)

            # Check for typical git files/dirs
            git_dir = project_path / ".git"
            config_file = git_dir / "config"
            head_file = git_dir / "HEAD"

            assert git_dir.exists()
            assert config_file.exists()
            assert head_file.exists()

    def test_function_signature(self, check_git_available):
        """Test function signature and error handling"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            # This should work normally - verifies signature is correct
            handle_git_init(project_path, use_git=True)

    def test_initial_branch_is_main(self, check_git_available):
        """Test that git init sets the initial branch to main, not master"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "testproject"
            project_path.mkdir()
            hub_dir = Path(tmpdir) / "hubs"

            with patch("app.handlers.git_handler.DEFAULT_GIT_HUB_ROOT", hub_dir):
                handle_git_init(project_path, use_git=True)

            head_content = (project_path / ".git" / "HEAD").read_text()
            assert "refs/heads/main" in head_content


class TestFinalizeGitSetup:
    """Tests for finalize_git_setup function"""

    def _setup_repo(self, project_path: Path, bare_path: Path) -> None:
        """Create a project repo with a bare remote and local identity configured."""
        bare_path.mkdir(parents=True)
        subprocess.run(
            ["git", "init", "--bare"], cwd=bare_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "init", "--initial-branch=main"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "remote", "add", "origin", str(bare_path)],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "--local", "user.email", "test@test.com"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "--local", "user.name", "Test User"],
            cwd=project_path,
            check=True,
            capture_output=True,
        )

    def test_noop_when_git_disabled(self):
        """finalize_git_setup returns immediately when use_git is False"""
        finalize_git_setup(Path("/nonexistent"), use_git=False)

    def test_creates_initial_commit_and_pushes(self, check_git_available):
        """Test that an initial commit is created and pushed to origin"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "myproject"
            project_path.mkdir()
            bare_path = Path(tmpdir) / "myproject.git"
            self._setup_repo(project_path, bare_path)
            (project_path / "README.md").write_text("# Hello")

            finalize_git_setup(project_path, use_git=True)

            log = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=project_path,
                capture_output=True,
                text=True,
            )
            assert "Initial commit" in log.stdout

    def test_skips_commit_when_nothing_to_stage(self, check_git_available):
        """Test that no commit is made when the project directory is empty"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "myproject"
            project_path.mkdir()
            bare_path = Path(tmpdir) / "myproject.git"
            self._setup_repo(project_path, bare_path)
            # No files added — nothing to commit

            finalize_git_setup(project_path, use_git=True)

            log = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=project_path,
                capture_output=True,
                text=True,
            )
            assert log.stdout.strip() == ""

    def test_raises_clear_error_when_identity_not_configured(
        self, check_git_available
    ):
        """Test that a RuntimeError with helpful message is raised when git
        user.email is not set, instead of an opaque CalledProcessError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "myproject"
            project_path.mkdir()
            bare_path = Path(tmpdir) / "myproject.git"
            self._setup_repo(project_path, bare_path)
            # Override email to empty string to simulate unconfigured identity
            subprocess.run(
                ["git", "config", "--local", "user.email", ""],
                cwd=project_path,
                check=True,
                capture_output=True,
            )
            (project_path / "README.md").write_text("# Hello")

            with pytest.raises(RuntimeError, match="Git identity not configured"):
                finalize_git_setup(project_path, use_git=True)
