#!/usr/bin/env python3
"""Cut the target word/phrase out of a carrier-sentence TTS take.

Carrier sentences give a natural FALLING tone on phrases that TTS otherwise reads with a rising, question-like tone:
  "The next phrase is: based on."     -> phrase = LAST group
  "Based on. That's the phrase."      -> phrase = FIRST group
The ASR transcript of the cut is printed: it must be exactly the item (no carrier words, nothing missing).
Groups are separated by pauses >= --gap seconds. Prints the groups so you can choose; writes <take>w.wav.

usage: python3 extract_take.py audio/items_raw/21_C.wav --group last [--gap 0.18]
       then verify:  manus-speech-to-text audio/items_raw/21_Cw.wav ; python3 check_pitch.py audio/items_raw/21_Cw.wav
"""
import argparse
import numpy as np, soundfile as sf


def groups(x, sr, gap, rel=0.03):
    hop = sr // 100
    e = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, len(x) - hop, hop)])
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
    return [(a / 100, b / 100) for a, b in out if b - a >= 5]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('wav'); ap.add_argument('--group', default='last', help='first | last | <index> | a-b (merge range)')
    ap.add_argument('--gap', type=float, default=0.18)
    a = ap.parse_args()
    x, sr = sf.read(a.wav); x = x if x.ndim == 1 else x.mean(1)
    g = groups(x, sr, a.gap)
    for i, (s, e) in enumerate(g):
        print(f'group {i}: {s:.2f}-{e:.2f} ({e - s:.2f} s)')
    if a.group == 'first':
        s, e = g[0]
    elif a.group == 'last':
        s, e = g[-1]
    elif '-' in a.group:
        i, j = map(int, a.group.split('-')); s, e = g[i][0], g[j][1]
    else:
        s, e = g[int(a.group)]
    s = max(0, s - 0.03); e = min(len(x) / sr, e + 0.08)
    y = x[int(s * sr):int(e * sr)].copy()
    n1, n2 = int(0.006 * sr), int(0.03 * sr)
    y[:n1] *= np.linspace(0, 1, n1); y[-n2:] *= np.linspace(1, 0, n2)
    out = a.wav[:-4] + 'w.wav'
    sf.write(out, np.concatenate([np.zeros(int(0.05 * sr)), y, np.zeros(int(0.1 * sr))]), sr)
    print('wrote', out, f'({s:.2f}-{e:.2f})')
    import subprocess
    tx = subprocess.run(['manus-speech-to-text', out], capture_output=True, text=True).stdout
    heard = sorted({ln for ln in tx.splitlines() if ln.startswith('[')})
    print('ASR heard:', ' | '.join(heard) or '(nothing) - check the group')
