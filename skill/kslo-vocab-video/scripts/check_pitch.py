#!/usr/bin/env python3
"""Check the final pitch movement of word/phrase takes (Praat autocorrelation pitch via parselmouth).

User requirement: every word and phrase ends with a FALLING (statement) tone - never a rising, question-like tone.
Metric: rise = mean of the last 4 voiced frames minus the lowest point of the preceding frames, in semitones.
  rise > 3.0 st  -> RISE  (reject the take)
  1.5 - 3.0 st   -> mild  (listen; usually reject for phrases)
  < 1.5 st       -> OK (falling / level)
Also listen: the tool cannot hear creaky / unvoiced words (V3 'haggle'), swallowed short words (V4 'of'),
extra words, or emphatic endings ('with' heard as 'with one').

usage: python3 check_pitch.py file.wav [...]      (pip install praat-parselmouth)
"""
import sys
import numpy as np, parselmouth


def final_rise(f):
    snd = parselmouth.Sound(f)
    pt = snd.to_pitch_ac(time_step=0.02, pitch_floor=120, pitch_ceiling=700, very_accurate=True)
    f0 = pt.selected_array['frequency']; v = f0[f0 > 0]
    if len(v) < 6:
        return None, ''
    med = np.median(v); v = v[(v < med * 1.8) & (v > med / 1.8)]
    st = 12 * np.log2(v / med)
    end = st[-4:].mean(); trough = st[-12:-3].min() if len(st) >= 12 else st[:-3].min()
    return round(float(end - trough), 1), ' '.join(str(int(round(x / 10))) for x in v[-12:])


if __name__ == '__main__':
    for f in sys.argv[1:]:
        r, seq = final_rise(f)
        flag = '' if r is None else 'RISE' if r > 3.0 else 'mild' if r > 1.5 else 'OK'
        print('%-36s rise %5s st  %-4s | last f0 (x10 Hz): %s' % (f.split('/')[-1], r, flag, seq))
