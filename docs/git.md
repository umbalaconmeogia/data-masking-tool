# Git Guide

How this project was first published to GitHub, and the common commands for daily work.

Repository: https://github.com/umbalaconmeogia/data-masking-tool

## 1. Initial setup (already done)

These steps were used to publish this folder (which had no git yet) to an existing empty GitHub repository.

### Step 1: Initialize the repository

Create a new git repository with `main` as the default branch:

```bash
cd /home/thanh_tt/dev/open-source/data-masking-tool
git init -b main
```

### Step 2: Configure your git identity

Commits require a name and email. Set them for this repository only:

```bash
git config user.name "umbalaconmeogia"
git config user.email "umbalaconmeogia@gmail.com"
```

Or set them machine-wide (for all repositories) with `--global`:

```bash
git config --global user.name "umbalaconmeogia"
git config --global user.email "umbalaconmeogia@gmail.com"
```

### Step 3: Stage and commit all files

```bash
git add .
git status          # review what will be committed
git commit -m "Initial commit"
```

Files listed in [.gitignore](../.gitignore) (`.env`, `masking-rule.csv`, backups, Python caches, virtualenvs) are automatically excluded.

### Step 4: Connect to the GitHub repository

Add the GitHub repository as the `origin` remote, using SSH:

```bash
git remote add origin git@github.com:umbalaconmeogia/data-masking-tool.git
```

Verify SSH authentication to GitHub works:

```bash
ssh -T git@github.com
# Expected: "Hi umbalaconmeogia! You've successfully authenticated..."
```

### Step 5: Push to GitHub

Push the `main` branch and set it to track the remote branch:

```bash
git push -u origin main
```

The `-u` flag links the local `main` to `origin/main`, so future pushes and pulls only need `git push` / `git pull`.

## 2. Daily workflow

After the initial setup, publishing changes is just:

```bash
git status                      # see what changed
git add .                       # stage all changes (or: git add <file>)
git commit -m "Describe change" # commit
git push                        # publish to GitHub
```

To get the latest changes from GitHub (e.g. edits made on another machine or on the web):

```bash
git pull
```

## 3. Useful commands

| Command | Purpose |
|---|---|
| `git status` | Show modified / staged / untracked files |
| `git diff` | Show unstaged changes |
| `git diff --staged` | Show staged changes |
| `git log --oneline` | Compact commit history |
| `git restore <file>` | Discard unstaged changes to a file |
| `git restore --staged <file>` | Unstage a file (keep the changes) |
| `git remote -v` | Show configured remotes |

## 4. Working with branches

Create a branch for a feature or fix, then merge it back:

```bash
git switch -c feature/my-feature   # create and switch to a new branch
# ... edit, add, commit as usual ...
git push -u origin feature/my-feature  # publish the branch

git switch main                    # go back to main
git merge feature/my-feature       # merge the branch into main
git push
```

## 5. Notes

- **SSH configuration**: authentication uses the key configured in `~/.ssh/config` under the `github.com` host entry, so no password or token is needed for push/pull.
- **`.claude/settings.local.json`** is local Claude Code configuration and is intentionally left untracked.
- **Never commit secrets**: real database credentials belong in `.env` (ignored). Only `.env.example` and the docker test env files (test credentials only) are tracked.
