#!/usr/bin/env python3
"""Retime a Seedance Miss K clip so its lip movement follows the clean TTS voice exactly.
Seedance often speeds up, delays or mumbles parts of the reference line. Instead of stretching the voice, this maps every
speech stretch of the CLIP onto the matching phrase of the REFERENCE (piecewise-linear time warp of the video: slows or
speeds the lips a little, absorbs the difference in the pauses, where Miss K is just idling).
The output clip has the same length as the source and carries the reference audio, so the lip-aligned voice for that clip
is simply the reference file itself (audio/refs/<name>.wav, 0.5 s lead).
usage: python3 retime_clip.py SRC.mp4 REF.wav OUT.mp4 [--gap 0.25] [--anchors "ref:clip,ref:clip,..."]
Phrase counts must match; otherwise it prints both segmentations - pass a different --gap or explicit --anchors.
"""
import argparse, json, subprocess, sys
import numpy as np, soundfile as sf


def speech_segs(x, sr, gap=0.25, rel=0.05):
    h = sr // 100
    e = np.array([np.sqrt((x[i:i + h] ** 2).mean()) for i in range(0, len(x) - h, h)])
    on = e > e.max() * rel
    out, s, last = [], None, -99
    for i, v in enumerate(on):
        if v:
            if s is None or i - last > gap * 100:
                if s is not None and (last + 1 - s) >= 8:
                    out.append((s / 100, (last + 1) / 100))
                elif s is not None and out:
                    pass
                s = i
            last = i
    if s is not None:
        out.append((s / 100, (last + 1) / 100))
    return out


def merge_to(segs, n):
    """merge the shortest internal pauses until len(segs) == n"""
    segs = list(segs)
    while len(segs) > n:
        g = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
        i = int(np.argmin(g))
        segs[i:i + 2] = [(segs[i][0], segs[i + 1][1])]
    return segs


def load_audio(f):
    if f.endswith('.mp4'):
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                           capture_output=True, check=True)
        return np.frombuffer(r.stdout, np.float32).astype(np.float64), 16000
    x, sr = sf.read(f)
    return (x if x.ndim == 1 else x.mean(1)), sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('ref'); ap.add_argument('out')
    ap.add_argument('--gap', type=float, default=0.25); ap.add_argument('--anchors')
    a = ap.parse_args()
    info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                      'stream=width,height,r_frame_rate,nb_frames:format=duration', '-of', 'json', a.src],
                                     capture_output=True, text=True).stdout)
    st = info['streams'][0]; W, H = st['width'], st['height']
    num, den = map(int, st['r_frame_rate'].split('/')); fps = num / den
    dur = float(info['format']['duration'])
    if a.anchors:
        anc = [tuple(map(float, p.split(':'))) for p in a.anchors.split(',')]
    else:
        xr, srr = load_audio(a.ref); xc, src_sr = load_audio(a.src)
        R = speech_segs(xr, srr, a.gap); C = speech_segs(xc, src_sr, a.gap)
        print('ref ', ' '.join('%.2f-%.2f' % s for s in R))
        print('clip', ' '.join('%.2f-%.2f' % s for s in C))
        if len(R) != len(C):
            n = min(len(R), len(C))
            R, C = merge_to(R, n), merge_to(C, n)
            print(f'merged to {n} phrases (shortest pauses joined):')
            print('ref ', ' '.join('%.2f-%.2f' % s for s in R))
            print('clip', ' '.join('%.2f-%.2f' % s for s in C))
        anc = []
        for (r0, r1), (c0, c1) in zip(R, C):
            anc += [(r0, c0), (r1, c1)]
    anc = [(0.0, 0.0)] + anc + [(dur, dur)]
    ro = np.array([p[0] for p in anc]); co = np.array([p[1] for p in anc])
    assert np.all(np.diff(ro) > 0) and np.all(np.diff(co) > 0), 'anchors must increase'
    for i in range(len(anc) - 1):
        sp = (co[i + 1] - co[i]) / (ro[i + 1] - ro[i])
        kind = 'speech' if i % 2 == 1 else 'pause '
        flag = '  <- strong' if (kind == 'speech' and not 0.75 <= sp <= 1.33) else ''
        print(f'{kind} out {ro[i]:6.2f}-{ro[i + 1]:6.2f}  src {co[i]:6.2f}-{co[i + 1]:6.2f}  speed x{sp:.2f}{flag}')
    # decode all source frames, then emit frame by frame through the warp
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', a.src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    n_out = int(round(dur * fps))
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', f'{num}/{den}', '-i', '-', '-i', a.ref, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264',
                            '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                            '-shortest', a.out], stdin=subprocess.PIPE)
    for k in range(n_out):
        tc = float(np.interp(k / fps, ro, co))
        enc.stdin.write(fr[min(len(fr) - 1, int(round(tc * fps)))].tobytes())
    enc.stdin.close(); enc.wait()
    print('wrote', a.out, n_out, 'frames')


if __name__ == '__main__':
    main()
