# Quick Git Guide

## Daily workflow

**See what changed:**
```bash
git status                    # See all changes (staged and unstaged)
git diff                      # Show unstaged changes (what you typed but haven't staged)
git diff --cached             # Show staged changes (what you added but haven't committed)
```

**Stage and commit:**
```bash
git add file.py               # Stage one file
git add .                     # Stage everything
git commit -m "message"       # Commit with message
```

**View history:**
```bash
git log                       # See recent commits
git log --oneline             # Shorter version
git log -p                    # Show what changed in each commit
```

## Before you push

**See what you're about to push:**
```bash
git log origin/main..HEAD     # Commits you made that main doesn't have
```

**Push your work:**
```bash
git push                      # Push current branch to remote
git push -u origin branch     # First push of a new branch
```

## Branching

```bash
git branch                    # List local branches
git branch new-feature        # Create a branch
git checkout new-feature      # Switch to a branch
git switch new-feature        # Same thing (newer syntax)
```

## When you mess up

**Unstage a file (keep changes):**
```bash
git restore --staged file.py  # Remove from staging, keep the edits
```

**Discard local changes (dangerous!):**
```bash
git restore file.py           # Revert file to last commit
git restore .                 # Revert all files to last commit
```

**Undo a commit (before push):**
```bash
git reset --soft HEAD~1       # Undo commit, keep changes staged
git reset HEAD~1              # Undo commit, keep changes unstaged
```

## Pulling updates

```bash
git pull                      # Fetch + merge remote changes into your branch
git fetch                     # Just download remote changes (don't merge yet)
```

## Key concepts

- **Staging** = telling git which changes to include in the next commit
- **Committed** = changes are saved in git history
- **Pushed** = changes sent to remote (GitHub, etc.)
- Use `git status` liberally—it always tells you what's next
