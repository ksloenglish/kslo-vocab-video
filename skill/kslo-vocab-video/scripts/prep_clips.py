#!/usr/bin/env python3
"""Chroma-key + framing stabilisation of every Miss K clip to the neutral reference pose (assets/missk_neutral.png).

Why: Seedance clips drift slightly in zoom/position; without this Miss K "jumps" between clips (user feedback V2).
Per clip: SIFT matches (frame -> neutral reference) on the neutral first/last 0.7 s, RANSAC similarity transform,
median of the best samples; linear drift between start and end. A common zoom `a` (>= 1) guarantees every clip
still covers the bottom frame edge. Output: clips/keyed/<name>.npy (N, 720, 960, 4) uint8 + meta.json + stab.json.

usage: python3 prep_clips.py [name ...]        (default: every library clip that exists: idle intro transition outro pop1..pop6)
       STAB_ONLY=1 python3 prep_clips.py ...    (only estimate + print framing; use to spot a badly framed clip)
Delete a name from clips/keyed/stab.json to force re-estimation after replacing a clip.
Disk: ~380 MB per 5 s clip, ~5 GB for the whole library (format v2: no per-item clips).
The library ships clips/keyed/stab.json (framing already estimated), so only keying runs per project.
"""
import json, os, sys, subprocess
import numpy as np, cv2
from PIL import Image
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import p, clip_path, load_items, word_clip_names
from keying import key, frames, W0, H0

OUT = p('clips', 'keyed')
os.makedirs(OUT, exist_ok=True)
BODY_CX = 632.0
X0, X1 = 160, 1120          # common crop (target coordinates)
_ref = None


def all_names():
    return ['idle', 'intro', 'transition', 'outro'] + [f'pop{i}' for i in range(1, 7)]


def ref_feats():
    global _ref
    if _ref is None:
        ref = np.array(Image.open(p('assets', 'missk_neutral.png')).convert('RGB').resize((W0, H0), Image.LANCZOS))
        rk = key(ref)
        sift = cv2.SIFT_create(3000)
        m = cv2.erode((rk[..., 3] > 128).astype(np.uint8) * 255, np.ones((7, 7), np.uint8))
        kr, dr = sift.detectAndCompute(cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY), m)
        _ref = (sift, kr, dr, cv2.BFMatcher())
    return _ref


def est(fr):
    sift, kr, dr, bf = ref_feats()
    k = key(fr)
    m = cv2.erode((k[..., 3] > 128).astype(np.uint8) * 255, np.ones((7, 7), np.uint8))
    kf, df = sift.detectAndCompute(cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY), m)
    if df is None or len(kf) < 10:
        return None
    ms = bf.knnMatch(df, dr, k=2)
    good = [q[0] for q in ms if len(q) == 2 and q[0].distance < 0.75 * q[1].distance]
    if len(good) < 12:
        return None
    src = np.float32([kf[g.queryIdx].pt for g in good]); dst = np.float32([kr[g.trainIdx].pt for g in good])
    M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=2.0)
    if M is None:
        return None
    s = float(np.hypot(M[0, 0], M[1, 0])); th = float(np.arctan2(M[1, 0], M[0, 0]))
    return s, th, float(M[0, 2]), float(M[1, 2]), int(inl.sum())


def _med(rows):
    a = np.array(rows)
    nmax = a[:, 5].max()
    sel = a[a[:, 5] >= 0.5 * nmax]
    return dict(s=float(np.median(sel[:, 1])), th=float(np.median(sel[:, 2])),
                tx=float(np.median(sel[:, 3])), ty=float(np.median(sel[:, 4])), n_sel=int(len(sel)))


def stab_job(name):
    frs = list(frames(clip_path(name)))
    n = len(frs)
    head, tail = [], []
    for i in range(0, 17, 2):
        r = est(frs[i]); head += [(i,) + r] if r else []
    for i in range(n - 17, n, 2):
        r = est(frs[i]); tail += [(i,) + r] if r else []
    p0, p1 = _med(head), _med(tail)
    return name, dict(n=n, start=p0, end=p1, d_tx=p1['tx'] - p0['tx'], d_ty=p1['ty'] - p0['ty'], d_s=p1['s'] - p0['s'])


def interp(q, k):
    u = 0.0 if q['n'] <= 1 else min(1.0, max(0.0, (k - 8) / max(1, q['n'] - 17)))
    a, b = q['start'], q['end']
    return {z: a[z] + (b[z] - a[z]) * u for z in ('s', 'th', 'tx', 'ty')}


def total_M(q, a):
    c, s_ = np.cos(q['th']) * q['s'], np.sin(q['th']) * q['s']
    Mc = np.array([[c, -s_, q['tx']], [s_, c, q['ty']], [0, 0, 1]])
    At = np.array([[a, 0, BODY_CX * (1 - a) - X0], [0, a, 0], [0, 0, 1]])
    return (At @ Mc)[:2]


def key_job(args):
    name, q, a = args
    pth = clip_path(name)
    n = int(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets',
                                     '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', pth]).strip())
    cw = X1 - X0
    mm = np.lib.format.open_memmap(os.path.join(OUT, f'{name}.npy'), mode='w+', dtype=np.uint8, shape=(n, H0, cw, 4))
    k = 0
    for fr in frames(pth):
        if k >= n:
            break
        M = total_M(interp(q, k), a)
        kk = key(fr).astype(np.float32)
        al = kk[..., 3:4] / 255.0
        pm = np.concatenate([kk[..., :3] * al, kk[..., 3:4]], -1)
        w = cv2.warpAffine(pm, M, (cw, H0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        aa = np.clip(w[..., 3:4], 0, 255)
        rgb = np.where(aa > 0.5, w[..., :3] / np.maximum(aa / 255.0, 1e-3), 0)
        mm[k] = np.concatenate([np.clip(rgb, 0, 255), aa], -1).astype(np.uint8)
        k += 1
    mm.flush()
    return name, k


if __name__ == '__main__':
    names = [n for n in all_names() if os.path.exists(clip_path(n))]
    if len(sys.argv) > 1:
        names = [n for n in names if n in sys.argv[1:]]
    stab_f = os.path.join(OUT, 'stab.json')
    stab = json.load(open(stab_f)) if os.path.exists(stab_f) else {}
    todo = [n for n in names if n not in stab]
    with Pool(6) as pool:
        for nm, q in pool.imap_unordered(stab_job, todo):
            stab[nm] = q
            print('stab', nm, 'scale %.3f -> %.3f  tx %.1f -> %.1f  ty %.1f -> %.1f' % (
                q['start']['s'], q['end']['s'], q['start']['tx'], q['end']['tx'], q['start']['ty'], q['end']['ty']), flush=True)
    json.dump(stab, open(stab_f, 'w'), indent=1)
    bottoms = {nm: min(z['s'] * H0 * np.cos(z['th']) + z['ty'] - abs(np.sin(z['th'])) * 300 for z in (q['start'], q['end']))
               for nm, q in stab.items()}
    a = max(1.0, H0 / (min(bottoms.values()) - 3))
    print('lowest bottom coverage', {k: round(v) for k, v in sorted(bottoms.items(), key=lambda kv: kv[1])[:6]}, 'zoom a=%.4f' % a)
    if a > 1.04:
        print('WARNING: common zoom > 4 %: one clip is badly framed (zoomed/shifted). Regenerate it rather than zooming all.')
    if os.environ.get('STAB_ONLY'):
        sys.exit(0)
    with Pool(6) as pool:
        res = pool.map(key_job, [(nm, stab[nm], a) for nm in names])
    meta_f = os.path.join(OUT, 'meta.json')
    meta = json.load(open(meta_f)) if os.path.exists(meta_f) else dict(frames={})
    meta.update(x0=X0, x1=X1, fps=24, zoom=a)
    for nm, k in res:
        meta['frames'][nm] = k
    json.dump(meta, open(meta_f, 'w'), indent=1)
    print('keyed', len(res), 'clips; zoom', round(a, 4))
