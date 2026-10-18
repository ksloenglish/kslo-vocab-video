#!/usr/bin/env python3
"""Snapshot an approved build before image edits; finish without rebuilding its audio.

VOCAB_PROJECT=/project python3 image_revision.py snapshot --source /project/output/old.mp4
# Replace/review artwork, set project.json output to a NEW version, render affected item segments.
VOCAB_PROJECT=/project SOURCE_MP4=/project/output/old.mp4 SKIP_RENDER=1 bash finalize.sh
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys

IMAGE_FIELDS = {'image_prompt', 'creature_family', 'creature_signature',
                'creature_role', 'human_creature_interaction', 'creature_scale_plan',
                'style_reference_files', 'image_prompt_previous'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def audio_sha(path):
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path),
                                    '-map', '0:a:0', '-c', 'copy', '-f', 'adts', '-'])
    return hashlib.sha256(data).hexdigest()


def content(items):
    return [{k: v for k, v in item.items() if k not in IMAGE_FIELDS} for item in items]


def timing(segments):
    return [{k: v for k, v in segment.items()} for segment in segments]


def baseline_path(root):
    return root / 'work/image_revision_baseline.json'


def snapshot(root, source, segments):
    items = json.loads((root / 'items.json').read_text())
    data = dict(source=str(source), source_sha256=sha(source), audio_sha256=audio_sha(source),
                items=content(items), timeline=timing(segments), audio_files={}, non_item_segments={},
                image_files={})
    for item in items:
        file = root / 'audio/items' / f"{item['n']:02d}_{item['slug']}.wav"
        data['audio_files'][str(file.relative_to(root))] = sha(file)
        image = root / 'illus' / f"{item['n']:02d}_{item['slug']}.png"
        if not image.is_file() or image.stat().st_size == 0:
            raise ValueError(f'Missing illustration at snapshot: {image}')
        data['image_files'][str(image.relative_to(root))] = sha(image)
    for segment in segments:
        if segment['kind'] != 'item':
            file = root / 'work/segs' / f"seg_{segment['idx']:03d}.mp4"
            data['non_item_segments'][str(file.relative_to(root))] = sha(file)
    target = baseline_path(root)
    if target.exists():
        raise ValueError('An image-revision baseline already exists. Archive it explicitly before starting a NEW revision; never overwrite it after edits.')
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print('Image-only baseline saved before edits:', target)


def validate(root, source, segments, data):
    if str(source) != data['source'] or sha(source) != data['source_sha256']:
        raise ValueError('Approved source MP4 differs from the pre-edit baseline')
    items = json.loads((root / 'items.json').read_text())
    if content(items) != data['items']:
        raise ValueError('Approved vocabulary/content fields changed during an image-only revision')
    if timing(segments) != data['timeline']:
        raise ValueError('Timeline/order/voice timing changed during an image-only revision')
    for group in ['audio_files', 'non_item_segments']:
        for name, digest in data[group].items():
            if sha(root / name) != digest:
                raise ValueError(f'Unrequested {group} change: {name}')


def changed_image_numbers(root, data):
    """Return only source PNG IDs whose bytes differ from the pre-edit snapshot."""
    hashes = data.get('image_files')
    if not isinstance(hashes, dict):
        raise ValueError('Image-revision baseline has no image hashes; take a new snapshot before editing images')
    changed = []
    for item in json.loads((root / 'items.json').read_text()):
        image = root / 'illus' / f"{item['n']:02d}_{item['slug']}.png"
        name = str(image.relative_to(root))
        if not image.is_file() or image.stat().st_size == 0 or hashes.get(name) != sha(image):
            changed.append(int(item['n']))
    return changed


def finish(root, source, segments):
    from check_illustrations import check
    from review_images import check as check_image_approval
    check(root)
    data = json.loads(baseline_path(root).read_text())
    validate(root, source, segments, data)
    changed_images = changed_image_numbers(root, data)
    # A source-MP4 revision inherits its untouched legacy images; only source
    # PNG bytes changed after the snapshot need a new gallery + explicit approval.
    check_image_approval(root, changed_images)
    project = json.loads((root / 'project.json').read_text())
    out = (root / project['output']).resolve()
    if out == source:
        raise ValueError('Use a NEW output version; do not overwrite the approved source video')
    concat = root / 'work/image_revision_concat.txt'
    for segment in segments:
        file = root / 'work/segs' / f"seg_{segment['idx']:03d}.mp4"
        if not file.exists():
            raise ValueError(f'Missing encoded segment: {file}')
    concat.write_text(''.join(f"file '{root}/work/segs/seg_{segment['idx']:03d}.mp4'\n" for segment in segments))
    video = root / 'work/image_revision_video_only.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat), '-c', 'copy', str(video)], check=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-i', str(source),
                    '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', str(out)], check=True)
    if audio_sha(out) != data['audio_sha256']:
        raise ValueError('Final encoded audio is not identical to the approved source')
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-of', 'json', str(out)]))
    expected = segments[-1]['start'] + segments[-1]['dur']
    if abs(float(probe['format']['duration']) - expected) > .04:
        raise ValueError('Final duration does not match the unchanged timeline')
    report = dict(output=str(out), wording_unchanged=True, timeline_unchanged=True,
                  non_item_segments_unchanged=True, item_audio_files_unchanged=True,
                  final_encoded_audio_identical=True, audio_sha256=data['audio_sha256'],
                  changed_image_numbers=changed_images)
    (root / 'work/image_revision_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Image-only revision complete; exact approved audio copied and verified:', out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['snapshot', 'finish'])
    parser.add_argument('--source', required=True)
    args = parser.parse_args()
    if not os.environ.get('VOCAB_PROJECT'):
        parser.error('Set VOCAB_PROJECT')
    root = Path(os.environ['VOCAB_PROJECT']).resolve()
    source = Path(args.source).resolve()
    from timeline import SEGMENTS
    try:
        globals()[args.action](root, source, SEGMENTS)
    except (ValueError, OSError, KeyError) as error:
        print('Image-only revision FAILED:', error, file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
