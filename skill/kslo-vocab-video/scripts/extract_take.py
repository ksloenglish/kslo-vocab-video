#!/usr/bin/env python3
"""Cut the target word/phrase out of a carrier-sentence TTS take.

Carrier sentences give a natural FALLING tone on phrases that TTS otherwise reads with a rising, question-like tone:
  "The next phrase is: based on."     -> phrase = LAST group
  "Based on. That's the phrase."      -> phrase = FIRST group
The ASR transcript of the cut is printed: it must be exactly the item (no carrier words, nothing missing).
Groups are separated by pauses >= --gap seconds. Prints the actual detected groups so you can choose; writes <take>w.wav.
The ASR JSON written beside the take is the check record (terminal snippets are not parsed as a transcript).

usage: python3 extract_take.py audio/items_raw/21_C.wav --group last [--gap 0.18]
       then verify the printed ASR JSON with verify_transcription.py --expected <item>;
       run check_pitch.py on audio/items_raw/21_Cw.wav
"""
import argparse, json, os, subprocess
import numpy as np, soundfile as sf


def groups(x, sr, gap, rel=0.03):
    if not (gap >= 0 and 0 < rel <= 1):
        raise ValueError('gap must be non-negative and rel must be between 0 and 1')
    hop = sr // 100
    starts = list(range(0, len(x) - hop, hop)) or ([0] if len(x) else [])
    e = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in starts])
    if not len(e) or not np.isfinite(e).all() or e.max() <= 0:
        raise ValueError('no audible activity in take')
    act = e > e.max() * rel
    out, s, last = [], None, None
    for i, a in enumerate(act):
        if a:
            if s is None:
                s = i
            elif i - last > gap * 100:
                out.append((s, last + 1)); s = i
            last = i
    if s is not None:
        out.append((s, last + 1))
    out = [(starts[a] / sr, min(len(x), starts[b - 1] + hop) / sr) for a, b in out if b - a >= 5]
    if not out:
        raise ValueError('no speech group of at least 50 ms at the configured threshold')
    return out


def edge_fade(y, sr, head_available, tail_available):
    """Keep fades inside retained quiet guards; do not fade a final stop at a file edge."""
    y = y.copy()
    n1 = min(int(.006 * sr), len(y))
    n2 = min(int(.030 * sr), int(tail_available), len(y))
    if n1:
        y[:n1] *= np.linspace(0, 1, n1)
    if n2:
        y[-n2:] *= np.linspace(1, 0, n2)
    return y


def authoritative_asr_json(wav):
    """Run ASR once and return its newly written JSON; never inspect printed transcript lines."""
    folder = os.path.dirname(os.path.abspath(wav))
    stem = os.path.splitext(os.path.basename(wav))[0]
    before = set(os.path.join(folder, f) for f in os.listdir(folder)
                 if f.startswith(stem + '_transcription_') and f.endswith('.json'))
    subprocess.run(['manus-speech-to-text', wav], check=True)
    made = [os.path.join(folder, f) for f in os.listdir(folder)
            if f.startswith(stem + '_transcription_') and f.endswith('.json') and os.path.join(folder, f) not in before]
    if len(made) != 1:
        raise RuntimeError(f'ASR did not produce exactly one new authoritative JSON for {wav}')
    path = made[0]
    data = json.load(open(path))
    if not isinstance(data, dict) or not isinstance(data.get('segments'), list) or not isinstance(data.get('full_text'), str):
        raise RuntimeError(f'ASR JSON has no usable segments/full_text: {path}')
    return path, data


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('wav'); ap.add_argument('--group', default='last', help='first | last | <index> | a-b (merge range)')
    ap.add_argument('--gap', type=float, default=0.18)
    ap.add_argument('--head', type=float, default=0.03, help='quiet guard before the chosen group (default: 0.03)')
    ap.add_argument('--tail', type=float, default=0.08, help='quiet guard after the chosen group (default: 0.08)')
    ap.add_argument('--rel', type=float, default=0.03, help='relative speech threshold (default: 0.03)')
    a = ap.parse_args()
    if a.head < 0 or a.tail < 0:
        ap.error('--head and --tail must be non-negative')
    x, sr = sf.read(a.wav); x = x if x.ndim == 1 else x.mean(1)
    try:
        g = groups(x, sr, a.gap, a.rel)
    except ValueError as error:
        ap.error(str(error))
    for i, (s, e) in enumerate(g):
        print(f'group {i}: {s:.2f}-{e:.2f} ({e - s:.2f} s)')
    try:
        if a.group == 'first':
            raw_s, raw_e = g[0]
        elif a.group == 'last':
            raw_s, raw_e = g[-1]
        elif '-' in a.group:
            i, j = map(int, a.group.split('-')); raw_s, raw_e = g[i][0], g[j][1]
            if i > j:
                raise ValueError('merged group range must increase')
        else:
            raw_s, raw_e = g[int(a.group)]
    except (ValueError, IndexError) as error:
        ap.error(f'invalid --group {a.group!r}: {error}')
    s = max(0, raw_s - a.head); e = min(len(x) / sr, raw_e + a.tail)
    y = x[int(s * sr):int(e * sr)].copy()
    y = edge_fade(y, sr, (raw_s - s) * sr, (e - raw_e) * sr)
    out = os.path.splitext(a.wav)[0] + 'w.wav'
    sf.write(out, np.concatenate([np.zeros(int(0.05 * sr)), y, np.zeros(int(0.1 * sr))]), sr)
    print('wrote', out, f'({s:.2f}-{e:.2f}); source group {raw_s:.2f}-{raw_e:.2f}')
    path, data = authoritative_asr_json(out)
    print('ASR JSON:', path)
    print('ASR full_text:', data['full_text'])
