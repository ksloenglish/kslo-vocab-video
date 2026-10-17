#!/usr/bin/env python3
"""Prepare the final item voice clips (format v2: no per-item Miss K clips, so no lip fitting).
For each item: chosen take = project item_takes[n] (a file stem in audio/items_raw, e.g. "14_C" from extract_take.py)
or audio/items_raw/NN.wav -> trim silence (20 ms head / 60 ms tail) -> 48 kHz mono audio/items/NN_<slug>.wav.
Writes work/item_voice.json {n: {"dur": s, "take": stem}} (renderer: badge speaking window; mixer: placement at WORD_AT).
usage: python3 prep_items.py [n ...]
"""
import json, os, sys
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
    takes = {int(k): v for k, v in (proj('item_takes') or {}).items()}
    items = load_items()
    sel = [int(a) for a in sys.argv[1:]] or [i['n'] for i in items]
    f_out = p('work', 'item_voice.json')
    out = {int(k): v for k, v in json.load(open(f_out)).items()} if os.path.exists(f_out) else {}
    os.makedirs(p('audio', 'items'), exist_ok=True)
    for it in items:
        n = it['n']
        if n not in sel:
            continue
        stem = takes.get(n, f'{n:02d}')
        src = p('audio', 'items_raw', f'{stem}.wav')
        if not os.path.exists(src):
            print(f'#{n} {it["display"]}: MISSING {src}'); continue
        w = trim(load(src))
        w = w * np.minimum(1, np.arange(len(w)) / (0.004 * SR)) * np.minimum(1, (len(w) - np.arange(len(w))) / (0.02 * SR))
        sf.write(p('audio', 'items', f'{n:02d}_{it["slug"]}.wav'), w, SR)
        out[n] = dict(dur=round(len(w) / SR, 3), take=stem)
        flag = '  <- long, check' if len(w) / SR > 3.6 else ''
        print(f'#{n:2d} {it["display"]:28s} {len(w) / SR:.2f} s  from {stem}.wav{flag}')
    json.dump({str(k): v for k, v in sorted(out.items())}, open(f_out, 'w'), indent=1)
