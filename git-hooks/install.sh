#!/bin/bash
# git-hooks/install.sh — Install this repo's git hooks into .git/hooks.
#
# Usage:
#   git-hooks/install.sh              # install all hooks in this directory
#   git-hooks/install.sh --uninstall  # remove hooks this script installed
#
# Every regular file in git-hooks/ (other than this installer) is copied to
# .git/hooks/<name> and made executable. Re-run after pulling a change to a
# hook file.
#
# Bypass any installed hook for a single push with `git push --no-verify`.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# `git rev-parse --git-path hooks` resolves to the correct hooks directory
# whether this is a normal checkout (.git/hooks) or a linked worktree
# (.git/worktrees/<name>/hooks, since hooks are shared across worktrees but
# resolved per-worktree by git itself) or core.hooksPath is customized.
HOOKS_DIR="$(git rev-parse --git-path hooks)"

mkdir -p "$HOOKS_DIR"

if [ "${1:-}" = "--uninstall" ]; then
  for hook in "$SCRIPT_DIR"/*; do
    name="$(basename "$hook")"
    [ "$name" = "install.sh" ] && continue
    [ -f "$hook" ] || continue
    target="$HOOKS_DIR/$name"
    if [ -f "$target" ] && cmp -s "$hook" "$target"; then
      rm -f "$target"
      echo "Removed $target"
    fi
  done
  exit 0
fi

for hook in "$SCRIPT_DIR"/*; do
  name="$(basename "$hook")"
  [ "$name" = "install.sh" ] && continue
  [ -f "$hook" ] || continue
  target="$HOOKS_DIR/$name"
  cp "$hook" "$target"
  chmod +x "$target"
  echo "Installed $target"
done

echo "Done. Bypass any hook for one push with: git push --no-verify"
