# Basic commands

## Saving changes (the core loop)

| What             | Terminal                              | IDE                                             |
| ---------------- | ------------------------------------- | ----------------------------------------------- |
| See what changed | `git status`                          | Source Control tab — files listed automatically |
| Stage a file     | `git add app/handlers/git_handler.py` | Click **+** next to the file                    |
| Stage everything | `git add .`                           | Click **+** next to "Changes" heading           |
| Commit           | `git commit -m "your message"`        | Type message in the box, click ✓                |
| Push to hub      | `git push`                            | Click **Sync** / the cloud icon                 |

---

## Reviewing history

| Command             | Description                                     |
| ------------------- | ----------------------------------------------- |
| `git log --oneline` | Compact list of commits                         |
| `git diff`          | Shows what changed since last commit (unstaged) |
| `git diff --staged` | Shows what's staged and ready to commit         |
| `git show abc1234`  | Displays exactly what a specific commit changed |

The IDE shows this in the **Timeline** panel (bottom of the Explorer sidebar) and you can click any file to see a diff.

---

## Undoing things

| Command                         | Description                               |
| ------------------------------- | ----------------------------------------- |
| `git restore app/core/state.py` | Discard unsaved changes to one file       |
| `git restore .`                 | Discard **all** unsaved changes (careful) |
| `git restore --staged state.py` | Unstage a file while keeping the changes  |

In the IDE: right-click a changed file → **Discard Changes**, or click **−** to unstage.

---

## Branching (when you want to try something without risk)

| Command                       | Description                              |
| ----------------------------- | ---------------------------------------- |
| `git switch -c my-experiment` | Create and switch to a new branch        |
| `git switch main`             | Switch back to `main`                    |
| `git merge my-experiment`     | Merge your experiment branch into `main` |
| `git branch -d my-experiment` | Delete the branch after merging          |

---

## The golden rule

**Commit often, with clear messages.** Small commits like `"Fix orphaned bare repo cleanup on build error"` are far more useful than one giant `"A bunch of changes"` at the end of the day. For a personal project, committing after each meaningful change (feature, fix, or refactor) is the right rhythm.

For more information, visit the official Git documentation at [Git Docs](https://git-scm.com/doc)

---

## See Also

- [Help & Documentation](app://help) — Usage guide and keyboard shortcuts
- [About UV Forge](app://about) — App info, tech stack, and features
