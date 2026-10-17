"""Chroma-key helpers for Miss K's green-screen (#00FF00) Seedance clips (1280x720)."""
import subprocess
import numpy as np, cv2

W0, H0 = 1280, 720
LO, HI = 45.0, 150.0


def frames(path, step=1):
    """Decode a 1280x720 clip (Seedance 720p 16:9) to RGB frames."""
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         stdout=subprocess.PIPE, bufsize=10 ** 8)
    i = 0
    while True:
        buf = p.stdout.read(W0 * H0 * 3)
        if len(buf) < W0 * H0 * 3:
            break
        if i % step == 0:
            yield np.frombuffer(buf, np.uint8).reshape(H0, W0, 3)
        i += 1
    p.wait()


def key(fr):
    """RGB uint8 -> RGBA uint8 with green spill suppression and a slight alpha choke."""
    f = fr.astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    mx = np.maximum(r, b)
    d = g - mx
    a = np.clip((HI - d) / (HI - LO), 0, 1)
    a = np.clip((a - 0.12) / 0.88, 0, 1)
    a = cv2.GaussianBlur(a, (3, 3), 0.7)
    a[a < 0.03] = 0
    g2 = np.minimum(g, mx)
    h, w = fr.shape[:2]
    out = np.empty((h, w, 4), np.uint8)
    out[..., 0] = fr[..., 0]
    out[..., 1] = g2.astype(np.uint8)
    out[..., 2] = fr[..., 2]
    out[..., 3] = (a * 255).astype(np.uint8)
    return out


def bg_check(path, t=0.5):
    """Mean RGB of the top-left 40x40 corner at t seconds. Green screen OK when G > 200 and R, B < 80
    (Unit 1 clips ~ [25, 239, 26]); a black or other background (~[17, 18, 21]) breaks keying -> regenerate."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', path, '-frames:v', '1', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw[:W0 * H0 * 3], np.uint8).reshape(H0, W0, 3)
    m = fr[:40, :40].reshape(-1, 3).mean(0).round(1).tolist()
    return m, ('OK' if m[1] > 200 and m[0] < 80 and m[2] < 80 else 'NOT GREEN')
