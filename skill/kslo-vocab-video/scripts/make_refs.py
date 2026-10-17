#!/usr/bin/env python3
"""Build Seedance audio references (lip-sync drivers) from the FINAL voice takes.

  words : audio/refs/word_NN.wav  - 5.0 s, the chosen take (project item_takes or items_raw/NN.wav) starting at 1.2 s
  lines : audio/refs/<name>.wav   - 0.5 s lead + audio/vo/<name>.wav, padded to a whole number of seconds (+~1 s tail)
          (greeting / conclusion; the transition clip is reused from the skill template)
Use the same whole-second length as the clip duration you request (Seedance 2.5: 4-30 s).

usage: python3 make_refs.py words [n ...] | lines [greeting conclusion]
"""
import math, os, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import p, proj, load_items

SR = 48000


def load(f):
    x, sr = sf.read(f); x = x if x.ndim == 1 else x.mean(1)
    return resample_poly(x, SR, sr) if sr != SR else x


def trim(x, rel=0.02):
    hop = SR // 100
    e = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, len(x) - hop, hop)])
    a = np.where(e > e.max() * rel)[0]
    return x[max(0, a[0] * hop - int(0.02 * SR)):min(len(x), (a[-1] + 1) * hop + int(0.06 * SR))]


if __name__ == '__main__':
    mode = sys.argv[1]
    os.makedirs(p('audio', 'refs'), exist_ok=True)
    if mode == 'words':
        takes = {int(k): v for k, v in (proj('item_takes') or {}).items()}
        items = load_items()
        sel = [int(a) for a in sys.argv[2:]] or [i['n'] for i in items]
        for n in sel:
            src = p('audio', 'items_raw', f'{takes.get(n, f"{n:02d}")}.wav')
            w = trim(load(src))
            out = np.zeros(int(5.0 * SR)); o = int(1.2 * SR)
            out[o:o + len(w)] = w[:len(out) - o]
            sf.write(p('audio', 'refs', f'word_{n:02d}.wav'), out, SR)
            print(f'word_{n:02d}.wav  speech {len(w) / SR:.2f} s from {os.path.basename(src)}')
    else:
        for nm in sys.argv[2:]:
            x = load(p('audio', 'vo', f'{nm}.wav'))
            L = math.ceil(len(x) / SR + 0.5 + 0.8)
            if L > 30:
                sys.exit(f'{nm}: {L} s is longer than the 30 s Seedance limit - shorten the script')
            out = np.zeros(int(max(4, L) * SR)); o = int(0.5 * SR)
            out[o:o + len(x)] = x
            sf.write(p('audio', 'refs', f'{nm}.wav'), out, SR)
            print(f'{nm}.wav  {L} s (request a {L} s clip)')
