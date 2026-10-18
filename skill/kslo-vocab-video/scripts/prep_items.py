#!/usr/bin/env python3
"""Prepare the final item voice clips (format v2: no per-item Miss K clips, so no lip fitting).
For each item: chosen take = project item_takes[n] (a file stem in audio/items_raw, e.g. "14_C" from extract_take.py)
or audio/items_raw/NN.wav -> trim silence (20 ms head / 60 ms tail) -> 48 kHz mono audio/items/NN_<slug>.wav.
Optional project.json item_trim overrides are per item, e.g. {"19": {"rel": .01, "head": .04, "tail": .18}}.
Writes work/item_voice.json {n: {"dur": s, "take": stem}} (renderer: badge speaking window; mixer: placement at WORD_AT).
usage: python3 prep_items.py [n ...]
"""
import json, os, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import p, proj, load_items
SR = 48000
DEFAULT_TRIM = dict(rel=.02, head=.02, tail=.06)  # Keep the established production default.


def load(f):
    x, sr = sf.read(f); x = x if x.ndim == 1 else x.mean(1)
    return resample_poly(x, SR, sr) if sr != SR else x


def trim_bounds(x, rel=.02, head=.02, tail=.06):
    """Return crop bounds and active end; retain the legacy default calculation exactly."""
    if not (0 < rel <= 1 and head >= 0 and tail >= 0):
        raise ValueError('trim settings require 0 < rel <= 1 and non-negative head/tail')
    hop = SR // 100
    starts = list(range(0, len(x) - hop, hop))
    if not starts and len(x):       # Short clips need one real analysis frame, not a guessed crop.
        starts = [0]
    e = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in starts])
    if not len(e) or not np.isfinite(e).all() or e.max() <= 0:
        raise ValueError('no audible activity in take')
    a = np.where(e > e.max() * rel)[0]
    if not len(a):
        raise ValueError('no audible activity at the configured relative threshold')
    start = max(0, starts[a[0]] - int(head * SR))
    active_end = min(len(x), starts[a[-1]] + hop)
    end = min(len(x), active_end + int(tail * SR))
    return start, end, active_end


def trim(x, rel=.02, head=.02, tail=.06, details=False):
    """Trim from detected speech; ``details`` exposes safe fade margins for tests/callers."""
    start, end, active_end = trim_bounds(x, rel, head, tail)
    y = x[start:end].copy()
    if details:
        return y, dict(start=start, end=end, active_end=active_end,
                       head_available=start and min(start, int(head * SR)),
                       tail_available=max(0, end - active_end))
    return y


def edge_fade(y, head_available, tail_available):
    """Use legacy 4/20 ms fades only in retained silence, never across a final stop."""
    y = y.copy()
    n1 = min(int(.004 * SR), len(y))
    n2 = min(int(.020 * SR), int(tail_available), len(y))
    if n1:
        y[:n1] *= np.arange(n1) / n1       # Same factors as the old default when margins exist.
    if n2:
        y[-n2:] *= (n2 - np.arange(n2)) / n2
    return y


def trim_settings(n):
    settings = DEFAULT_TRIM.copy()
    configured = proj('item_trim') or {}
    override = configured.get(str(n), configured.get(n))
    if override is None:
        return settings
    if not isinstance(override, dict) or set(override) - set(settings):
        raise ValueError(f'item_trim[{n!r}] must contain only rel, head and/or tail')
    settings.update({k: float(v) for k, v in override.items()})
    # Validate here so a malformed selected item cannot quietly retain stale prepared audio.
    trim_bounds(np.ones(SR), **settings)
    return settings


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
        settings = trim_settings(n)
        w, info = trim(load(src), details=True, **settings)
        w = edge_fade(w, info['head_available'], info['tail_available'])
        sf.write(p('audio', 'items', f'{n:02d}_{it["slug"]}.wav'), w, SR)
        out[n] = dict(dur=round(len(w) / SR, 3), take=stem)
        flag = '  <- long, check' if len(w) / SR > 3.6 else ''
        print(f'#{n:2d} {it["display"]:28s} {len(w) / SR:.2f} s  from {stem}.wav '
              f'(rel={settings["rel"]:.3g}, head={settings["head"]:.3g}, tail={settings["tail"]:.3g}){flag}')
    json.dump({str(k): v for k, v in sorted(out.items())}, open(f_out, 'w'), indent=1)
