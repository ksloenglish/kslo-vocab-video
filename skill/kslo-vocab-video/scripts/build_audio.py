#!/usr/bin/env python3
"""Mix the soundtrack -> audio/final_mix.wav (48 kHz stereo, loudnorm -16 LUFS).
Voice: aligned greeting / transition / conclusion at their clip starts; item voices at item start + WORD_AT - 0.06,
loudness-matched (max short-term loudness, 400 ms) so no item sounds quieter (user feedback V4: 'unique').
Extra per-item gain: project.json "item_gain_extra_db" {"12": 1.0}.
SFX: logo sting, whooshes, 3-2-1 countdown beeps + film-projector loop, reveal chime, finale sparkle.
Music: bgm_a (opening..words) and bgm_b (phrases..ending), ducked under the voice; music ends 1 s before the end
(silent during the final black hold).
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from scipy.ndimage import uniform_filter1d
import pyloudnorm as pyln
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import *

SR = 48000
N = int((TOTAL + 0.5) * SR)


def load(path, mono=False):
    if not path.lower().endswith(('.wav', '.flac')):          # mp3 / opus / m4a ... decoded by ffmpeg
        tmp = '/tmp/_dec.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ar', str(SR), '-ac', '2', tmp], check=True)
        x, sr = sf.read(tmp)
    else:
        x, sr = sf.read(path)
        if sr != SR:
            x = resample_poly(x, SR, sr, axis=0)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    if mono:
        x = x.mean(1, keepdims=True).repeat(2, 1)
    return x.astype(np.float64)


def active_norm(x, db):
    m = np.abs(x).max(1)
    act = x[m > m.max() * 0.05]
    return x * (10 ** (db / 20) / (np.sqrt((act ** 2).mean()) + 1e-9))


def rms_norm(x, db):
    return x * (10 ** (db / 20) / (np.sqrt((x ** 2).mean()) + 1e-9))


def place(bus, x, t, gain=1.0, fade_in=0.0, fade_out=0.0, length=None):
    o = int(round(t * SR))
    if length is not None:
        x = x[:int(length * SR)]
    x = x.copy()
    if fade_in > 0:
        n = min(len(x), int(fade_in * SR)); x[:n] *= np.linspace(0, 1, n)[:, None]
    if fade_out > 0:
        n = min(len(x), int(fade_out * SR)); x[-n:] *= np.linspace(1, 0, n)[:, None]
    if o < 0:
        x = x[-o:]; o = 0
    e = min(len(bus), o + len(x))
    bus[o:e] += x[:e - o] * gain


def beep(freq=1000, dur=0.11):
    t = np.arange(int(dur * SR)) / SR
    env = np.minimum(1, t / 0.004) * np.exp(-t / 0.05)
    y = (np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * 2 * freq * t)) * env
    return np.stack([y, y], 1)


vo = np.zeros((N, 2)); music = np.zeros((N, 2)); sfx = np.zeros((N, 2))
seg = seg_by_key()
VO_DB = -14.0

# ---------------- voice
place(vo, active_norm(load(p('audio', 'aligned', 'intro.wav')), VO_DB - 6), seg['opening']['start'] + OPEN_MK_IN)
if 'transition' in seg:
    place(vo, active_norm(load(p('audio', 'aligned', 'transition.wav')), VO_DB - 6), seg['transition']['start'] + TRANS_GROW)
place(vo, active_norm(load(p('audio', 'aligned', 'outro.wav')), VO_DB - 6), seg['conclusion']['start'] + TRANS_GROW)
POPS = [s_ for s_ in SEGMENTS if s_['kind'] == 'popup']
for s_ in POPS:     # library voice is aligned to the clip's lips; the clip starts at the segment start
    place(vo, active_norm(load(p('audio', 'aligned', f"{s_['pop']}.wav")), VO_DB - 6), s_['start'])

_MET = pyln.Meter(SR, block_size=0.2)
ITEM_ST = -18.2
ITEM_EXTRA = {int(k): float(v) for k, v in (proj('item_gain_extra_db') or {}).items()}


def st_max(x):
    m = x.mean(1) if x.ndim > 1 else x
    w = int(0.4 * SR)
    if len(m) <= w:
        return _MET.integrated_loudness(np.concatenate([m, np.zeros(int(0.3 * SR))]))
    return max(_MET.integrated_loudness(m[i:i + w]) for i in range(0, len(m) - w, int(0.05 * SR)))


gains = {}
for it in ITEMS:
    s = seg[f'item{it["n"]}']
    w = active_norm(load(p('audio', 'items', f'{it["n"]:02d}_{it["slug"]}.wav')), VO_DB - 5)
    gdb = float(np.clip(ITEM_ST - st_max(w), -3, 3)) + ITEM_EXTRA.get(it['n'], 0.0)
    gains[it['n']] = round(gdb, 2)
    place(vo, w * 10 ** (gdb / 20), s['start'] + WORD_AT - 0.06)
print('item loudness gains dB:', gains)

# ---------------- sfx
A = lambda f: p('audio', f)
sting = rms_norm(load(A('sfx_logo_sting.mp3')), -24)
whoosh = rms_norm(load(A('sfx_whoosh.mp3')), -27)
reveal = rms_norm(load(A('sfx_reveal.mp3')), -25)
proj_loop = rms_norm(load(A('sfx_projector.mp3')), -33)
finale = rms_norm(load(A('sfx_finale.mp3')), -25)
bp = beep(1000) * 0.22
o = seg['opening']['start']
place(sfx, sting, o + 0.45, fade_out=0.6)
place(sfx, whoosh, o + 2.95, gain=0.7)
place(sfx, whoosh, o + OPEN_MK_IN - 0.05, gain=0.6)
place(sfx, whoosh, seg['part']['start'] + 0.05, gain=0.8)
for s_ in POPS:
    place(sfx, whoosh, s_['start'], gain=0.6)
    place(sfx, whoosh, s_['start'] + s_['dur'] - 0.55, gain=0.45)
for it in ITEMS:
    s = seg[f'item{it["n"]}']['start']
    place(sfx, whoosh, s, gain=0.55)
    place(sfx, proj_loop, s + CD_START - 0.05, fade_in=0.08, fade_out=0.12, length=CD_END - CD_START + 0.05)
    for k in range(3):
        place(sfx, bp, s + CD_START + k)
    place(sfx, reveal, s + CD_END)
t0 = seg['transition']['start'] if 'transition' in seg else seg['conclusion']['start']
if 'transition' in seg:
    place(sfx, whoosh, t0, gain=0.8)
    place(sfx, whoosh, t0 + TRANS_GROW + TRANS_CLIP, gain=0.6)
c0 = seg['conclusion']['start']
place(sfx, whoosh, c0, gain=0.7)
place(sfx, finale, c0 + 1.0, fade_out=0.5)
place(sfx, sting, seg['outro']['start'] + 0.25, fade_out=1.0)

# ---------------- music (ducked under the voice)
def music_file(stem):
    for ext in ('.opus', '.mp3', '.m4a', '.ogg', '.wav', '.flac'):
        if os.path.exists(A(stem + ext)):
            return A(stem + ext)
    raise FileNotFoundError(f'audio/{stem}.* not found (copied from templates/audio by init_project.py)')
ma = rms_norm(load(music_file('bgm_a')), -20)
mb = rms_norm(load(music_file('bgm_b')), -20)
place(music, ma, 0.0, fade_in=1.5, fade_out=2.0, length=t0 + 0.6)
place(music, mb, t0 - 0.6, fade_in=1.2, fade_out=2.6, length=TOTAL - 1.0 - (t0 - 0.6))
env = uniform_filter1d(np.abs(vo).max(1), int(0.05 * SR))
env = uniform_filter1d((env > 0.01).astype(np.float64), int(0.35 * SR))
music *= (0.55 * (1.0 - 0.55 * np.clip(env * 1.3, 0, 1)))[:, None]

for nm, b in (('vo', vo), ('sfx', sfx), ('music', music)):
    print(nm, 'peak %.2f' % np.abs(b).max(), 'rms %.1f dB' % (20 * np.log10(np.sqrt((b ** 2).mean()) + 1e-9)))
mix = (vo + sfx + music)[:int(TOTAL * SR)]
pk = np.abs(mix).max()
if pk > 0.95:
    mix *= 0.95 / pk
sf.write(p('audio', 'final_mix_raw.wav'), mix.astype(np.float32), SR)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p('audio', 'final_mix_raw.wav'), '-af',
                'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', str(SR), p('audio', 'final_mix.wav')], check=True)
print('done', round(TOTAL, 2), 's')
