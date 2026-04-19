#!/usr/bin/env bash
# rewrite-git-history.sh
# Safely rewrite Git history to update author and committer info.

# ===== CONFIGURATION =====
CORRECT_NAME="Thomas Harold"
CORRECT_EMAIL="tgh@tgharold.com"

# ===== SAFETY CHECK =====
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: This script must be run inside a Git repository."
    exit 1
fi

read -p "WARNING: This will rewrite history for ALL commits. Continue? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

# ===== REWRITE HISTORY =====
git filter-branch --env-filter "
if [ \"\$GIT_COMMITTER_EMAIL\" != \"$CORRECT_EMAIL\" ] || [ \"\$GIT_COMMITTER_NAME\" != \"$CORRECT_NAME\" ]; then
    export GIT_COMMITTER_NAME=\"$CORRECT_NAME\"
    export GIT_COMMITTER_EMAIL=\"$CORRECT_EMAIL\"
fi
if [ \"\$GIT_AUTHOR_EMAIL\" != \"$CORRECT_EMAIL\" ] || [ \"\$GIT_AUTHOR_NAME\" != \"$CORRECT_NAME\" ]; then
    export GIT_AUTHOR_NAME=\"$CORRECT_NAME\"
    export GIT_AUTHOR_EMAIL=\"$CORRECT_EMAIL\"
fi
" --tag-name-filter cat -- --branches --tags

# ===== CLEANUP =====
rm -rf "$(git rev-parse --git-dir)/refs/original/"
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✅ Git history rewritten with new name and email."
echo "⚠️ If this is a shared repo, you must force-push: git push --force --tags origin main"
