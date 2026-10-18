#!/usr/bin/env python3
"""Safely revise selected prepared item voices without rebuilding an approved soundtrack.

Before any selected-take/edit metadata change:
  VOCAB_PROJECT=/project python3 audio_revision.py snapshot --source /absolute/previous.mp4
After selected takes are prepared and project.json has a new output:
  VOCAB_PROJECT=/project python3 audio_revision.py finish --items 17 19

The source MP4 is never overwritten.  Finish invokes the current build_audio.py only to
make a proposed mix, then replaces selected word windows in the snapshotted original PCM.
"""
import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

SCRIPT_DIR = Path(__file__).resolve().parent
BASELINE_NAME = 'audio_revision_baseline.json'
ORIGINAL_MIX_NAME = 'audio_revision_original_final_mix.wav'
SR = 48000


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require_file(path, label=None):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f'missing {label or "file"}: {path}')
    return path


def hash_files(root, files, label):
    result = {}
    for path in sorted({Path(f) for f in files}):
        require_file(path, label)
        result[str(path.relative_to(root))] = sha(path)
    return result


def recursive_files(directory):
    directory = Path(directory)
    return [p for p in directory.rglob('*') if p.is_file()] if directory.is_dir() else []


def duration(path):
    info = json.loads(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(path)]))
    return float(info['format']['duration'])


def pcm_info(path):
    info = sf.info(path)
    if info.format != 'WAV' or info.subtype != 'PCM_16' or info.samplerate != SR:
        raise ValueError(f'{path} must be uncompressed 48 kHz PCM_16 WAV, got {info.format}/{info.subtype}/{info.samplerate}')
    if info.channels not in (1, 2) or info.frames <= 0:
        raise ValueError(f'{path} has invalid audio shape')
    return dict(format=info.format, subtype=info.subtype, samplerate=info.samplerate,
                channels=info.channels, frames=info.frames, duration=info.duration)


def source_mix_alignment(source, mix):
    """Decode the approved AAC once and prove this PCM mix is aligned with it, not merely same-length."""
    info = pcm_info(mix)
    with tempfile.TemporaryDirectory() as temp:
        decoded = Path(temp) / 'source_audio.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-map', '0:a:0',
                        '-ar', str(SR), '-ac', str(info['channels']), '-c:a', 'pcm_s16le', str(decoded)], check=True)
        reference, _ = sf.read(mix, dtype='float64', always_2d=True)
        candidate, _ = sf.read(decoded, dtype='float64', always_2d=True)
    # AAC priming can shift a decoded stream very slightly. Search only +/-80 ms at 1 kHz,
    # not arbitrary offsets that could disguise a stale PCM mix.
    reference, candidate = reference[::48].mean(1), candidate[::48].mean(1)
    best = (-1.0, 0)
    for offset in range(-80, 81):
        n = min(len(reference) - max(0, offset), len(candidate) - max(0, -offset))
        if n < 100:
            continue
        left = reference[max(0, offset):max(0, offset) + n]
        right = candidate[max(0, -offset):max(0, -offset) + n]
        corr = float(np.dot(left, right) / (np.linalg.norm(left) * np.linalg.norm(right) + 1e-15))
        if corr > best[0]:
            best = (corr, offset)
    if best[0] < .95:
        raise ValueError(f'original final_mix.wav does not match the approved source audio (correlation {best[0]:.3f})')
    return dict(decoded_audio_correlation=round(best[0], 6), decoded_audio_offset_seconds=round(best[1] / 1000, 4))


def baseline_path(root):
    return Path(root) / 'work' / BASELINE_NAME


def original_mix_path(root):
    return Path(root) / 'work' / ORIGINAL_MIX_NAME


def project_data(root):
    return json.loads(require_file(Path(root) / 'project.json', 'project.json').read_text())


def items_data(root):
    return json.loads(require_file(Path(root) / 'items.json', 'items.json').read_text())


def timeline_for(root):
    os.environ['VOCAB_PROJECT'] = str(root)
    sys.path.insert(0, str(SCRIPT_DIR))
    # This process imports timeline only once, after VOCAB_PROJECT has been set.
    import timeline
    return timeline.SEGMENTS, timeline.WORD_AT


def expected_item_audio(root, items):
    files = []
    for item in items:
        files.append(Path(root) / 'audio' / 'items' / f'{item["n"]:02d}_{item["slug"]}.wav')
    return files


def library_files(root):
    root = Path(root)
    files = recursive_files(root / 'clips') + recursive_files(root / 'audio' / 'aligned')
    files += [p for p in (root / 'audio').glob('*') if p.is_file() and p.name not in {'final_mix.wav', 'final_mix_raw.wav'}]
    files += [root / 'work' / name for name in ('clip_speech.json', 'library.json') if (root / 'work' / name).is_file()]
    return files


def segment_files(root, segments):
    return [Path(root) / 'work' / 'segs' / f"seg_{segment['idx']:03d}.mp4" for segment in segments]


def snapshot(root, source):
    root, source = Path(root).resolve(), require_file(source, 'approved source MP4').resolve()
    baseline, backup = baseline_path(root), original_mix_path(root)
    if baseline.exists() or backup.exists():
        raise ValueError('An audio-revision baseline/PCM backup already exists. Archive both explicitly before a NEW revision; never overwrite a stale baseline after edits.')
    segments, _ = timeline_for(root)
    items, project = items_data(root), project_data(root)
    item_voice = json.loads(require_file(root / 'work' / 'item_voice.json', 'prepared item_voice.json').read_text())
    original = require_file(root / 'audio' / 'final_mix.wav', 'original uncompressed audio/final_mix.wav')
    mix_info = pcm_info(original)  # Refuse a compressed or unknown alignment source.
    expected_total = segments[-1]['start'] + segments[-1]['dur']
    source_duration = duration(source)
    if abs(mix_info['duration'] - expected_total) > .04 or abs(source_duration - expected_total) > .08:
        raise ValueError('source MP4, original final_mix.wav, and current timeline do not align; do not guess a patch window')
    alignment = source_mix_alignment(source, original)
    all_images = recursive_files(root / 'illus')
    if not all_images:
        raise ValueError('no illustration files found for an approved-project snapshot')
    shutil.copy2(original, backup)
    data = dict(
        source=str(source), source_sha256=sha(source),
        project=project, project_sha256=sha(root / 'project.json'),
        items=items, items_sha256=sha(root / 'items.json'),
        timeline=copy.deepcopy(segments), renderer_sha256=sha(SCRIPT_DIR / 'render.py'),
        images=hash_files(root, all_images, 'illustration'),
        segments=hash_files(root, segment_files(root, segments), 'encoded segment'),
        prepared_audio=hash_files(root, expected_item_audio(root, items), 'prepared item audio'),
        library=hash_files(root, library_files(root), 'library/support file'),
        item_voice=item_voice,
        original_mix=dict(path=str(backup.relative_to(root)), sha256=sha(backup), **mix_info, **alignment),
    )
    baseline.parent.mkdir(parents=True, exist_ok=True)
    baseline.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(f'Audio-revision baseline saved before edits: {baseline}')


def verify_hash_map(root, expected, label, current_files=None):
    files = [Path(root) / key for key in expected] if current_files is None else current_files
    current = hash_files(root, files, label)
    if current != expected:
        changed = [key for key in sorted(set(current) | set(expected)) if current.get(key) != expected.get(key)]
        raise ValueError(f'changed {label}: {", ".join(changed[:4])}')


def _mapping(value, name):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f'project.json {name} must be an object')
    return {str(k): v for k, v in value.items()}


def verify_project_changes(before, after, selected, source, root):
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise ValueError('project.json must be an object')
    permitted = {'output', 'item_takes', 'item_gain_extra_db', 'item_trim'}
    sentinel = object()
    for key in set(before) | set(after):
        if key not in permitted and before.get(key, sentinel) != after.get(key, sentinel):
            raise ValueError(f'protected project metadata changed: {key}')
    output = after.get('output')
    if not isinstance(output, str) or not output.strip():
        raise ValueError('project.json output must be set to a new output filename before finish')
    if output == before.get('output') or (Path(root) / output).resolve() == Path(source).resolve():
        raise ValueError('set project.json output to a NEW version; never overwrite the approved source MP4')
    for key in ('item_takes', 'item_gain_extra_db', 'item_trim'):
        old, new = _mapping(before.get(key), key), _mapping(after.get(key), key)
        for item in set(old) | set(new):
            if old.get(item, sentinel) != new.get(item, sentinel) and int(item) not in selected:
                raise ValueError(f'protected {key} entry changed for unselected item {item}')


def verify_item_voice(before, after, selected, project, root, items):
    if not isinstance(before, dict) or not isinstance(after, dict) or set(before) != set(after):
        raise ValueError('work/item_voice.json keys changed')
    wanted = {str(item['n']) for item in items}
    if set(after) != wanted:
        raise ValueError('work/item_voice.json no longer describes exactly the current items')
    takes = _mapping(project.get('item_takes'), 'item_takes')
    for key in wanted:
        if int(key) not in selected and before[key] != after[key]:
            raise ValueError(f'protected item_voice metadata changed for item {key}')
        if not isinstance(after[key], dict) or 'dur' not in after[key] or 'take' not in after[key]:
            raise ValueError(f'item_voice entry {key} is incomplete')
        expected_take = takes.get(key, f'{int(key):02d}')
        if after[key]['take'] != expected_take:
            raise ValueError(f'item_voice {key} take does not match project item_takes')
    for item in items:
        n = item['n']
        if n not in selected:
            continue
        info = sf.info(require_file(Path(root) / 'audio' / 'items' / f'{n:02d}_{item["slug"]}.wav', 'selected prepared audio'))
        if info.samplerate != SR or info.channels != 1:
            raise ValueError(f'selected item {n} must be 48 kHz mono prepared WAV')
        if abs(float(after[str(n)]['dur']) - info.duration) > .006:
            raise ValueError(f'selected item {n} duration does not match prepared audio')


def item_windows(segments, word_at, old_voice, new_voice, selected, sr=SR):
    """Proven word windows: cue-.35 through cue+max(old/new duration)+.60."""
    windows = []
    segment_by_item = {s['item']: s for s in segments if s.get('kind') == 'item'}
    for n in selected:
        if n not in segment_by_item or str(n) not in old_voice or str(n) not in new_voice:
            raise ValueError(f'no timeline/prepared metadata for selected item {n}')
        segment = segment_by_item[n]
        cue = float(segment['start']) + float(word_at) - .06
        start = cue - .35
        end = cue + max(float(old_voice[str(n)]['dur']), float(new_voice[str(n)]['dur'])) + .60
        if start < float(segment['start']) - 1e-8 or end > float(segment['start']) + float(segment['dur']) + 1e-8:
            raise ValueError(f'item {n} patch window would escape its item segment')
        windows.append(dict(n=n, cue=cue, start=start, end=end, a=round(start * sr), b=round(end * sr),
                            u=round((cue - .75) * sr), v=round((cue - .55) * sr)))
    windows.sort(key=lambda w: w['a'])
    for left, right in zip(windows, windows[1:]):
        if right['a'] < left['b']:
            raise ValueError(f'word patch windows overlap: items {left["n"]} and {right["n"]}')
    return windows


def patch_pcm(original, proposed, windows, sr=SR):
    """Crossfade only guarded windows; rows outside them remain bit-identical in float/PCM form."""
    old, fresh = np.asarray(original, dtype=np.float64), np.asarray(proposed, dtype=np.float64)
    if old.ndim == 1:
        old, fresh = old[:, None], fresh[:, None]
    if old.shape != fresh.shape or old.ndim != 2:
        raise ValueError('original and proposed mixes must have identical sample/channel shapes')
    result, changed, report = old.copy(), np.zeros(len(old), dtype=bool), []
    fade = max(1, round(.012 * sr))
    last_end = 0
    for window in sorted(windows, key=lambda w: w['a']):
        a, b, u, v = (int(window[k]) for k in ('a', 'b', 'u', 'v'))
        if not (0 <= u < v <= a < b <= len(old)):
            raise ValueError(f'invalid word/backing window for item {window.get("n")}')
        if a < last_end or b - a <= 2 * fade:
            raise ValueError(f'overlapping or too-short patch window for item {window.get("n")}')
        backing_new, backing_old = fresh[u:v].reshape(-1), old[u:v].reshape(-1)
        gain = float(np.dot(backing_new, backing_old) / (np.dot(backing_new, backing_new) + 1e-15))
        if not .7 < gain < 1.4:
            raise ValueError(f'unsafe backing gain {gain:.4f} for item {window.get("n")}')
        patch = fresh[a:b] * gain
        if np.max(np.abs(patch)) >= .999:
            raise ValueError(f'local corrected word would clip for item {window.get("n")}')
        weight = np.ones(b - a)
        weight[:fade] = np.linspace(0, 1, fade)
        weight[-fade:] = np.linspace(1, 0, fade)
        result[a:b] = old[a:b] * (1 - weight[:, None]) + patch * weight[:, None]
        if np.max(np.abs(result[a:b])) >= .999:
            raise ValueError(f'crossfaded word would clip for item {window.get("n")}')
        changed[a:b] = True
        last_end = b
        report.append(dict(n=window.get('n'), start=window.get('start'), end=window.get('end'), local_gain=gain))
    if not np.array_equal(result[~changed], old[~changed]):
        raise AssertionError('PCM outside selected word windows changed')
    return result, changed, report


def selected_segment_indices(segments, old_voice, new_voice, selected):
    changed_duration = {n for n in selected if abs(float(old_voice[str(n)]['dur']) - float(new_voice[str(n)]['dur'])) > .0005}
    return [s['idx'] for s in segments if s.get('kind') == 'item' and s.get('item') in changed_duration]


def rerender_selected(root, indices):
    if not indices:
        return
    env = os.environ.copy()
    env['VOCAB_PROJECT'] = str(root)
    subprocess.run([sys.executable, str(SCRIPT_DIR / 'render.py'), 'segs', ','.join(map(str, indices))],
                   cwd=root, env=env, check=True)


def concat_and_mux(root, segments, output):
    root, output = Path(root), Path(output)
    concat = root / 'work' / 'audio_revision_concat.txt'
    concat.write_text(''.join(f"file '{root / 'work' / 'segs' / ('seg_%03d.mp4' % s['idx'])}'\n" for s in segments))
    video = root / 'work' / 'audio_revision_video_only.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat), '-c', 'copy', str(video)], check=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-i', str(root / 'audio' / 'final_mix.wav'),
                    '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR),
                    '-movflags', '+faststart', '-shortest', str(output)], check=True)


def finish(root, selected):
    root = Path(root).resolve()
    selected = [int(n) for n in selected]
    if not selected or len(set(selected)) != len(selected):
        raise ValueError('provide one or more distinct --items')
    baseline = json.loads(require_file(baseline_path(root), 'audio-revision baseline').read_text())
    source = require_file(baseline['source'], 'snapshotted approved source MP4').resolve()
    if sha(source) != baseline['source_sha256']:
        raise ValueError('approved source MP4 differs from the pre-edit baseline')
    backup = require_file(root / baseline['original_mix']['path'], 'snapshotted original PCM mix')
    baseline_mix_info = {k: baseline['original_mix'][k] for k in pcm_info(backup)}
    if sha(backup) != baseline['original_mix']['sha256'] or pcm_info(backup) != baseline_mix_info:
        raise ValueError('snapshotted original PCM mix changed or no longer matches its baseline')
    segments, word_at = timeline_for(root)
    items, project = items_data(root), project_data(root)
    numbers = {item['n'] for item in items}
    if not set(selected) <= numbers:
        raise ValueError('selected --items are not current project items')
    verify_project_changes(baseline['project'], project, set(selected), source, root)
    if items != baseline['items'] or sha(root / 'items.json') != baseline['items_sha256']:
        raise ValueError('approved vocabulary/content changed during audio-only revision')
    if segments != baseline['timeline']:
        raise ValueError('timeline/order/voice timing changed during audio-only revision')
    if sha(SCRIPT_DIR / 'render.py') != baseline['renderer_sha256']:
        raise ValueError('renderer changed during audio-only revision')
    verify_hash_map(root, baseline['images'], 'illustration', recursive_files(root / 'illus'))
    verify_hash_map(root, baseline['library'], 'library/support file', library_files(root))
    current_voice = json.loads(require_file(root / 'work' / 'item_voice.json', 'prepared item_voice.json').read_text())
    verify_item_voice(baseline['item_voice'], current_voice, set(selected), project, root, items)
    for name, digest in baseline['prepared_audio'].items():
        n = int(Path(name).name[:2])
        if n not in selected and sha(require_file(root / name, 'prepared item audio')) != digest:
            raise ValueError(f'protected prepared item audio changed: {name}')
    rerender = selected_segment_indices(segments, baseline['item_voice'], current_voice, set(selected))
    for segment in segments:
        name = str((root / 'work' / 'segs' / f"seg_{segment['idx']:03d}.mp4").relative_to(root))
        if segment['idx'] not in rerender and sha(require_file(root / name, 'encoded segment')) != baseline['segments'][name]:
            raise ValueError(f'protected encoded segment changed: {name}')
    rerender_selected(root, rerender)
    for segment in segments:
        name = str((root / 'work' / 'segs' / f"seg_{segment['idx']:03d}.mp4").relative_to(root))
        if segment['idx'] not in rerender and sha(root / name) != baseline['segments'][name]:
            raise ValueError(f'non-selected segment changed after rendering: {name}')
    env = os.environ.copy()
    env['VOCAB_PROJECT'] = str(root)
    subprocess.run([sys.executable, str(SCRIPT_DIR / 'build_audio.py')], cwd=root, env=env, check=True)
    pcm_info(root / 'audio' / 'final_mix.wav')
    original_i, old_sr = sf.read(backup, dtype='int16', always_2d=True)
    proposed_i, proposed_sr = sf.read(root / 'audio' / 'final_mix.wav', dtype='int16', always_2d=True)
    if old_sr != SR or proposed_sr != SR:
        raise ValueError('mix sample rate changed')
    windows = item_windows(segments, word_at, baseline['item_voice'], current_voice, selected, SR)
    mixed, changed, patch_report = patch_pcm(original_i.astype(np.float64) / 32768, proposed_i.astype(np.float64) / 32768, windows, SR)
    mixed_i = np.rint(np.clip(mixed, -1, 32767 / 32768) * 32768).astype(np.int16)
    if not np.array_equal(mixed_i[~changed], original_i[~changed]):
        raise AssertionError('PCM quantisation changed samples outside selected word windows')
    sf.write(root / 'audio' / 'final_mix.wav', mixed_i, SR, subtype='PCM_16')
    saved, saved_sr = sf.read(root / 'audio' / 'final_mix.wav', dtype='int16', always_2d=True)
    if saved_sr != SR or not np.array_equal(saved[~changed], original_i[~changed]):
        raise AssertionError('saved final mix changed PCM outside selected word windows')
    output = (root / project['output']).resolve()
    concat_and_mux(root, segments, output)
    expected_total = segments[-1]['start'] + segments[-1]['dur']
    if abs(duration(output) - expected_total) > .08:
        raise ValueError('new output duration does not match the protected timeline')
    if sha(source) != baseline['source_sha256']:
        raise ValueError('approved source MP4 was modified')
    subprocess.run([sys.executable, str(SCRIPT_DIR / 'youtube_text.py')], cwd=root, env=env, check=True)
    report = dict(source=str(source), output=str(output), selected_items=selected, rerendered_item_segments=rerender,
                  windows=patch_report, pcm_outside_word_windows_identical=True,
                  final_encoded_audio_identical=False,
                  encoded_audio_note='Audio was deliberately AAC re-encoded after selective PCM patching; do not compare it as byte-identical to the source.',
                  source_preserved=True, images_unchanged=True, content_unchanged=True, timeline_unchanged=True,
                  other_prepared_voices_unchanged=True, library_unchanged=True, untouched_segments_unchanged=True,
                  youtube_copy_regenerated=True)
    (root / 'work' / 'audio_revision_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['snapshot', 'finish'])
    parser.add_argument('--source', help='absolute approved MP4 path (required for snapshot)')
    parser.add_argument('--items', nargs='+', help='selected item numbers (required for finish)')
    args = parser.parse_args()
    root_text = os.environ.get('VOCAB_PROJECT')
    if not root_text:
        parser.error('Set VOCAB_PROJECT')
    try:
        if args.action == 'snapshot':
            if not args.source:
                raise ValueError('snapshot requires --source /absolute/previous.mp4')
            source = Path(args.source).expanduser()
            if not source.is_absolute():
                raise ValueError('snapshot --source must be an absolute path')
            snapshot(Path(root_text), source)
        else:
            if args.source:
                raise ValueError('finish reads the immutable snapshotted source; do not pass --source')
            if not args.items:
                raise ValueError('finish requires --items N [N ...]')
            finish(Path(root_text), args.items)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f'Audio revision FAILED: {error}', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
