#!/usr/bin/env bash
# Download (or update) the K S Lo vocab-video asset repo: reusable Miss K library clips + lip-matched voice,
# character design images, brand logo, vocabulary DOCX, Unit 1 reference build.
# Private repo ksloenglish/kslo-vocab-video -> ~/kslo-vocab-video (override with KSLO_ASSETS=/path).
# Needs the GitHub integration / `gh` logged in as an account with access to ksloenglish.
set -e
D="${KSLO_ASSETS:-$HOME/kslo-vocab-video}"
REPO=ksloenglish/kslo-vocab-video
if [ -d "$D/.git" ]; then
  git -C "$D" pull --ff-only
else
  if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh repo clone "$REPO" "$D" -- --depth 1
  else
    git clone --depth 1 "https://github.com/$REPO.git" "$D"
  fi
fi
test -f "$D/library/library.json" || { echo "library/library.json missing in $D"; exit 1; }
echo "assets ready: $D"
python3 -c "import json; l=json.load(open('$D/library/library.json')); print('library v%s clips:' % l['version'], ', '.join(l['clips']))"
