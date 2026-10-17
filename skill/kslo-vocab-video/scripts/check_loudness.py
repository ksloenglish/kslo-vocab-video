#!/usr/bin/env python3
"""Report perceived loudness of every final item voice (max short-term loudness over 400 ms, after the mixer's
active-speech normalisation). Items more than ~1 dB below the median sound quieter (V4: 'unique').
The mixer already matches them; add a small extra in project.json "item_gain_extra_db" if one still sounds soft.

usage: python3 check_loudness.py
"""
import os, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import p, load_items

SR = 48000
met = pyln.Meter(SR, block_size=0.2)
rows = []
for it in load_items():
    f = p('audio', 'items', f'{it["n"]:02d}_{it["slug"]}.wav')
    if not os.path.exists(f):
        continue
    x, sr = sf.read(f); x = x if x.ndim == 1 else x.mean(1)
    x = resample_poly(x, SR, sr) if sr != SR else x
    m = np.abs(x); act = x[m > m.max() * 0.05]; x = x * (10 ** (-19 / 20) / (np.sqrt((act ** 2).mean()) + 1e-9))
    w = int(0.4 * SR)
    xs = np.concatenate([x, np.zeros(int(0.3 * SR))]) if len(x) <= w else x
    st = max(met.integrated_loudness(xs[i:i + w]) for i in range(0, max(1, len(xs) - w), int(0.05 * SR)))
    rows.append((it['n'], it['display'], st, 20 * np.log10(np.abs(x).max())))
med = np.median([r[2] for r in rows])
for n, d, st, pk in rows:
    print(f'{n:2d} {d:28s} max-ST {st:6.1f} LUFS  ({st - med:+.1f} vs median)  peak {pk:5.1f} dBFS' + ('   <- soft' if st - med < -1 else ''))
