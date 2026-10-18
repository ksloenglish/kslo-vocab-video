#!/usr/bin/env bash
# Fetch public ksloenglish/kslo-vocab-video: reusable library, character/brand,
# vocabulary DOCX and Unit 1 reference. Public reading needs no owner-specific access.
set -euo pipefail
D="${KSLO_ASSETS:-$HOME/kslo-vocab-video}"
REPO=ksloenglish/kslo-vocab-video
if [ -d "$D/.git" ]; then
  git -C "$D" pull --ff-only
elif [ -f "$D/library/library.json" ]; then
  echo "Using supplied asset snapshot (no .git): $D"
  echo "This snapshot is not automatically updated; use a clean directory for a fresh clone."
else
  if [ -e "$D" ] && [ ! -d "$D" ]; then
    echo "Asset target is not a directory: $D" >&2
    exit 1
  fi
  if [ -d "$D" ] && [ -n "$(ls -A "$D")" ]; then
    echo "Refusing to overwrite non-empty non-asset directory: $D" >&2
    exit 1
  fi
  if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh repo clone "$REPO" "$D" -- --depth 1
  else
    GIT_TERMINAL_PROMPT=0 git clone --depth 1 "https://github.com/$REPO.git" "$D"
  fi
fi
test -f "$D/library/library.json" || { echo "library/library.json missing in $D" >&2; exit 1; }
echo "assets ready: $D"
KSLO_ASSETS="$D" python3 - <<'PY'
import json
import os
from pathlib import Path
library = json.loads((Path(os.environ['KSLO_ASSETS']) / 'library/library.json').read_text())
if not library.get('clips'):
    raise SystemExit('library/library.json has no clips')
print('library v%s clips:' % library.get('version', '?'), ', '.join(library['clips']))
PY
