#!/usr/bin/env bash
# Render every segment, concatenate, mux the final mix -> project.json "output".
# usage: VOCAB_PROJECT=/path/to/project bash finalize.sh [workers]     (~10-15 min for a 5-min video with 6 workers)
#        Re-render only some segments:  python3 render.py pool 6 33,34   then run this script with SKIP_RENDER=1
#        Image-only revision: snapshot BEFORE edits with image_revision.py, render affected item segments,
#        then SOURCE_MP4=/path/old.mp4 SKIP_RENDER=1 bash finalize.sh (copies/verifies exact old encoded audio).
set -e
S="$(cd "$(dirname "$0")" && pwd)"
: "${VOCAB_PROJECT:?set VOCAB_PROJECT}"
cd "$VOCAB_PROJECT"
W=${1:-6}
python3 "$S/check_popup_layout.py"
OUT=$(python3 -c "import json;print(json.load(open('project.json'))['output'])")
if [ -n "${SOURCE_MP4:-}" ]; then
  if [ "${SKIP_RENDER:-}" != "1" ]; then
    echo "Image-only mode requires SKIP_RENDER=1; re-render only affected item segments first." >&2
    exit 1
  fi
  python3 "$S/image_revision.py" finish --source "$SOURCE_MP4"
  python3 "$S/youtube_text.py"
  exit 0
fi
python3 "$S/check_illustrations.py"
# The normal build cannot start rendering (or mux a final video) until every
# current source PNG has both a gallery and an explicit hash-matched approval.
python3 "$S/review_images.py" --check
NSEG=$(python3 -c "import sys;sys.path.insert(0,'$S');from timeline import SEGMENTS;print(len(SEGMENTS))")
if [ -z "$SKIP_RENDER" ]; then
  rm -rf work/segs && mkdir -p work/segs
  python3 "$S/render.py" all "$W"
fi
python3 "$S/build_audio.py"
mkdir -p "$(dirname "$OUT")"
: > work/concat.txt
for i in $(seq 0 $((NSEG-1))); do printf "file '%s/work/segs/seg_%03d.mp4'\n" "$PWD" "$i" >> work/concat.txt; done
ffmpeg -v error -y -f concat -safe 0 -i work/concat.txt -c copy work/video_only.mp4
ffmpeg -v error -y -i work/video_only.mp4 -i audio/final_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
  -ar 48000 -movflags +faststart -shortest "$OUT"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact "$OUT"
python3 "$S/youtube_text.py"
echo "wrote $VOCAB_PROJECT/$OUT"
