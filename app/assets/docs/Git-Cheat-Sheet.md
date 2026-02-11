# Git Cheat Sheet

## Saving changes (the core loop)

| What | Terminal | IDE |
| --- | --- | --- |
| See what changed | `git status` | Source Control tab — files listed automatically |
| Stage a file | `git add app/handlers/git_handler.py` | Click **+** next to the file |
| Stage everything | `git add .` | Click **+** next to "Changes" heading |
| Commit | `git commit -m "your message"` | Type message in the box, click ✓ |
| Push to hub | `git push` | Click **Sync** / the cloud icon |

---

## Reviewing history

```bash
git log --oneline          # compact list of commits
git diff                   # what changed since last commit (unstaged)
git diff --staged          # what's staged and ready to commit
git show abc1234           # see exactly what one commit changed
```

The IDE shows this in the **Timeline** panel (bottom of the Explorer sidebar) and you can click any file to see a diff.

---

## Undoing things

```bash
git restore app/core/state.py      # discard unsaved changes to one file
git restore .                      # discard ALL unsaved changes (careful)
git restore --staged state.py      # unstage a file (keep the changes)
```

In the IDE: right-click a changed file → **Discard Changes**, or click **−** to unstage.

---

## Branching (when you want to try something without risk)

```bash
git switch -c my-experiment        # create + switch to new branch
git switch main                    # go back to main
git merge my-experiment            # merge your experiment into main
git branch -d my-experiment        # delete the branch after merging
```

---

## The golden rule

**Commit often, with clear messages.** Small commits like `"Fix orphaned bare repo cleanup on build error"` are far more useful than one giant `"A bunch of changes"` at the end of the day. For a personal project, committing after each meaningful change (feature, fix, or refactor) is the right rhythm.
