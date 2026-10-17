#!/usr/bin/env python3
"""Contact sheet of a video between two times, each tile labelled with its timestamp.
Use it to check that gestures match the speech (e.g. the wave only on "See you next time"),
that clips start/end in the neutral pose, and to inspect pops reported by check_mk.py.

usage: python3 contact_sheet.py <video.mp4> <t0> <t1> <step> <out.jpg> [cols]
"""
import subprocess, sys, tempfile, os
from PIL import Image, ImageDraw

v, t0, t1, step, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 6
ts = []
t = t0
while t <= t1 + 1e-6:
    ts.append(round(t, 3)); t += step
tw, th = 384, 216
rows = (len(ts) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * th), (20, 20, 20))
d = tempfile.mkdtemp()
for i, t in enumerate(ts):
    f = os.path.join(d, f'{i}.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', v, '-frames:v', '1', f], check=True)
    im = Image.open(f).convert('RGB').resize((tw, th))
    ImageDraw.Draw(im).text((6, 6), f'{t:.2f}s', fill=(255, 60, 60))
    sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
sheet.save(out, quality=85)
print('saved', out, len(ts), 'frames')
