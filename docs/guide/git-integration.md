# Git Integration

When **Git Repository** is checked, UV Forge sets up a complete git workflow using a two-phase approach. Your project is commit-ready immediately after build — no manual first push needed.

## Two-phase setup

### Phase 1: Repository creation

During the build, before any project files are written:

- A local git repo is initialized in the project directory (`git init`)
- A **bare hub repository** is created at your configured GitHub Root path (default: `~/Projects/git-repos/<project_name>.git`)
- The local repo is connected to the hub as the `origin` remote

### Phase 2: Initial commit

After all files, folders, and packages are set up:

- All generated files are staged (`git add .`)
- An initial commit is created
- The commit is pushed to the hub with upstream tracking (`git push -u origin HEAD`)

## Configuring the hub path

The hub repository location is configurable in [Settings](settings.md):

- **GitHub Root** — Base directory for hub repos (default: `~/Projects/git-repos`)
- The bare repo is created at `<github_root>/<project_name>.git`

!!! info "What's a bare hub?"
    A bare repository is a git repo without a working tree — it only contains the `.git` internals. It acts as a central repository (like a local GitHub) that you can push to and pull from. This is useful for keeping a clean backup of your projects on the same machine or a network drive.

## Git default setting

In Settings, you can configure whether the Git checkbox is checked by default for new projects. This saves a click if you always (or never) want git initialization.
