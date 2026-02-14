"""Git repository operations.

This module implements a two-phase git setup for newly created projects:

Phase 1 — handle_git_init():
    Called immediately after uv init. Creates a local git repository in the
    project directory and a corresponding bare repository (the "hub") at
    ~/Projects/git-repos/<project_name>.git, then connects them with a remote
    named 'origin'. Both inits are idempotent — safe to call on existing repos.

Phase 2 — finalize_git_setup():
    Called after all project files and packages have been installed. Stages
    everything, creates the initial commit, and pushes to the local hub so the
    project is immediately git-ready without requiring a manual first push.

If the user opts out of git, handle_git_init() removes any pre-existing .git
directory (e.g. one created by uv init) and finalize_git_setup() is a no-op.
"""

import shutil
import subprocess
from pathlib import Path

from loguru import logger

from app.core.constants import DEFAULT_GIT_HUB_ROOT


def get_bare_repo_path(project_path: Path) -> Path:
    """Derive the bare hub repository path for a project.

    Args:
        project_path: Absolute path to the project directory.

    Returns:
        Path to the corresponding bare repo at ~/Projects/git-repos/<name>.git.
    """
    return DEFAULT_GIT_HUB_ROOT / f"{project_path.name}.git"


def _run_git(
    cmd: list[str], cwd: Path, *, check: bool = True
) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def handle_git_init(project_path: Path, use_git: bool) -> None:
    """Phase 1: Create local and bare repositories and connect them.

    If use_git is True:
        - Initializes a local git repo in project_path (skipped if .git already
            exists, e.g. created by uv init).
        - Creates a bare repository at ~/Projects/git-repos/<name>.git, which
            acts as the local hub (skipped if it already exists).
        - Adds the bare repo as the 'origin' remote; if origin already exists,
            updates its URL instead.

    If use_git is False:
        - Removes the .git directory if present and returns immediately.

    Args:
        project_path: Absolute path to the project directory.
        use_git: Whether to set up git for this project.

    Raises:
        subprocess.CalledProcessError: If any git command fails.
    """
    if not use_git:
        git_dir = project_path / ".git"
        if git_dir.exists():
            logger.info("Removing .git directory (git disabled): {}", project_path)
            shutil.rmtree(git_dir)
        return

    logger.info("Initializing git repositories for: {}", project_path.name)

    # Initialize local repo (idempotent)
    git_dir = project_path / ".git"
    if not git_dir.exists():
        result = _run_git(["git", "init", "--initial-branch=main"], cwd=project_path)
        logger.debug("git init: {}", result.stdout.strip())
    else:
        logger.debug("Local .git already exists, skipping git init")

    # Initialize bare hub repo
    bare_repo_path = get_bare_repo_path(project_path)
    logger.debug("Bare repo path: {}", bare_repo_path)
    bare_repo_path.mkdir(parents=True, exist_ok=True)
    if not (bare_repo_path / "HEAD").exists():
        result = _run_git(["git", "init", "--bare"], cwd=bare_repo_path)
        logger.debug("git init --bare: {}", result.stdout.strip())
    else:
        logger.debug("Bare repo already exists, skipping bare init")

    # Add remote origin (update URL if it already exists)
    try:
        _run_git(
            ["git", "remote", "add", "origin", str(bare_repo_path)], cwd=project_path
        )
        logger.debug("Added remote origin: {}", bare_repo_path)
    except subprocess.CalledProcessError:
        logger.debug("Remote origin exists, updating URL to: {}", bare_repo_path)
        _run_git(
            ["git", "remote", "set-url", "origin", str(bare_repo_path)],
            cwd=project_path,
        )

    logger.info("Git initialized successfully for: {}", project_path.name)


def finalize_git_setup(project_path: Path, use_git: bool) -> None:
    """Phase 2: Stage, commit, and push all project files to the hub.

    Called after the full project structure has been written to disk and all
    packages have been installed. Stages every file in project_path, creates
    an initial commit, and pushes to origin with upstream tracking set (-u),
    so the project is immediately ready to use in an IDE without a manual push.

    Skipped entirely if use_git is False or if there are no files to commit
    (edge case where the project directory is empty).

    Args:
        project_path: Absolute path to the project directory.
        use_git: Whether git was enabled for this project.

    Raises:
        subprocess.CalledProcessError: If git add, commit, or push fails.
    """
    if not use_git:
        return

    logger.info("Finalizing git setup for: {}", project_path.name)

    # Stage all files created during the build process
    _run_git(["git", "add", "."], cwd=project_path)

    # Only commit if there are staged changes (prevents errors on empty projects)
    status = _run_git(["git", "status", "--porcelain"], cwd=project_path, check=False)
    if status.stdout:
        # Verify git identity is configured before attempting to commit
        identity = _run_git(
            ["git", "config", "user.email"], cwd=project_path, check=False
        )
        if not identity.stdout.strip():
            raise RuntimeError(
                "Git identity not configured — commit would fail.\n"
                "Run these commands to fix it:\n"
                '  git config --global user.name "Your Name"\n'
                '  git config --global user.email "you@example.com"'
            )

        result = _run_git(
            ["git", "commit", "-m", "Initial commit: Full project structure"],
            cwd=project_path,
        )
        logger.debug("git commit: {}", result.stdout.strip())

        result = _run_git(["git", "push", "-u", "origin", "HEAD"], cwd=project_path)
        logger.debug("git push: {}", result.stdout.strip())
        logger.info("Initial commit pushed to hub for: {}", project_path.name)
    else:
        logger.warning("No files to commit for: {}", project_path.name)
