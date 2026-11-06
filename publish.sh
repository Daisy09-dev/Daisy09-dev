bash publish.s#!/usr/bin/env bash
# One-command publish: replaces the contents of github.com/Daisy09-dev/Daisy09-dev
# with this folder and pushes. Run it from inside this folder (Git Bash on Windows works).
# Git will ask you to sign in the first time (browser or Personal Access Token).
set -euo pipefail

OWNER="Daisy09-dev"
REPO="Daisy09-dev"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"

echo "Cloning $OWNER/$REPO ..."
git clone "https://github.com/$OWNER/$REPO.git" "$WORK/repo"
cd "$WORK/repo"

# remove old files (keeps .git), then copy the new profile in
git rm -rq --ignore-unmatch . || true
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -a "$HERE"/. .
rm -f publish.sh

git add -A
if git diff --cached --quiet; then
  echo "Nothing to change. Profile is already up to date."
  exit 0
fi
git commit -m "Blue terminal profile with auto-updating card and snake"
git push origin HEAD
echo
echo "Published. Now open https://github.com/$OWNER/$REPO/actions and run both workflows once."
