"""Renderer for K S Lo English vocabulary revision videos (project text comes from project.json).
Usage:
  python3 render.py test t1 t2 ...      -> work/test/frame_<t>.png  (global times, seconds)
  python3 render.py segs i,j,...        -> render listed segments to work/segs/seg_XXX.mp4
  python3 render.py all [workers]        -> render every segment in parallel
"""
import os, sys, json, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from timeline import *
from config import CJK_FONT, CJK_INDEX

W, H = 1920, 1080
R = ROOT
NAVY_TOP = (17, 40, 86)
NAVY_BOT = (6, 15, 38)
NAVY_TXT = (12, 28, 62)
GOLD = (255, 200, 66)
CORAL = (255, 112, 104)
SKY = (110, 205, 255)
WHITE = (255, 255, 255)
DIM = (184, 200, 228)
LUT = [[v * k // 255 for v in range(256)] for k in range(256)]

# ------------------------------------------------------------------ helpers
_fc = {}
FONT_FILES = {'bebas': 'BebasNeue-Regular.ttf', 'reg': 'Poppins-Regular.ttf', 'med': 'Poppins-Medium.ttf',
              'semi': 'Poppins-SemiBold.ttf', 'bold': 'Poppins-Bold.ttf', 'xb': 'Poppins-ExtraBold.ttf',
              'ital': 'Poppins-Italic.ttf'}


def font(key, size):
    k = (key, size)
    if k not in _fc:
        if key == 'cjk':
            _fc[k] = ImageFont.truetype(CJK_FONT, size, index=CJK_INDEX)
        else:
            _fc[k] = ImageFont.truetype(f'{R}/assets/fonts/{FONT_FILES[key]}', size)
    return _fc[k]


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / (t1 - t0))


def eo(x):
    return 1 - (1 - x) ** 3


def eio(x):
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eback(x, s=1.70158):
    x = x - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def inout(t, a0, a1, b0, b1):
    """opacity that fades in over [a0,a1] and out over [b0,b1]"""
    return eo(prog(t, a0, a1)) * (1 - prog(t, b0, b1))


def paste(dst, src, x, y, op=1.0):
    if src is None or op <= 0.004:
        return
    x = int(round(x)); y = int(round(y))
    sw, sh = src.size; dw, dh = dst.size
    x0, y0, x1, y1 = max(0, x), max(0, y), min(dw, x + sw), min(dh, y + sh)
    if x1 <= x0 or y1 <= y0:
        return
    s = src if (x0 == x and y0 == y and x1 == x + sw and y1 == y + sh) else src.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    if op < 0.996:
        s = s.copy()
        s.putalpha(s.getchannel('A').point(LUT[int(op * 255)]))
    dst.alpha_composite(s, dest=(x0, y0))


def scaled(im, s, resample=Image.BILINEAR):
    if abs(s - 1) < 0.002:
        return im
    w, h = im.size
    return im.resize((max(1, int(w * s)), max(1, int(h * s))), resample)


def paste_scaled(dst, src, cx, cy, s, op=1.0):
    im = scaled(src, s)
    paste(dst, im, cx - im.size[0] / 2, cy - im.size[1] / 2, op)


SENT_W = 1700                 # sentence width in the full-width question panel
CLUE_BLANK = '_____'          # every blank in the clue sentence has the same length (user rule P8)


def blank_words(text):
    """'formulate strategies to' -> 'f_____ s_____ t_____'; one-letter words ('a') stay as they are."""
    return ' '.join(w if len(w) == 1 else w[0] + CLUE_BLANK for w in text.split())


def clue_sentence(sent, highlights):
    """Blank the item in the sample sentence (as it appears there, e.g. 'Having access to'), keep first letters.
    Returns (clue text, list of blanked spans to highlight)."""
    out, spans = sent, []
    for hl in highlights:
        i = out.find(hl)
        if i < 0:
            i = out.lower().find(hl.lower())
        if i < 0:
            continue
        j = i + len(hl)
        while j < len(out) and out[j].isalpha():      # blank the whole word ('features' -> 'f_____')
            j += 1
        b = blank_words(out[i:j])
        out = out[:i] + b + out[j:]
        spans.append(b)
    return out, spans


class Txt:
    """Text sprite; (x, top) refers to the font's ascent top; pad offset handled."""
    PAD = 6

    def __init__(self, txt, f, fill=WHITE, tracking=0, alpha=255):
        asc, desc = f.getmetrics()
        if tracking:
            w = sum(f.getlength(c) for c in txt) + tracking * (len(txt) - 1)
        else:
            w = f.getlength(txt)
        self.w = int(math.ceil(w)); self.asc = asc; self.desc = desc
        P = self.PAD
        im = Image.new('RGBA', (self.w + 2 * P, asc + desc + 2 * P), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        col = tuple(fill[:3]) + (alpha,)
        if tracking:
            x = P
            for c in txt:
                d.text((x, P + asc), c, font=f, fill=col, anchor='ls')
                x += f.getlength(c) + tracking
        else:
            d.text((P, P + asc), txt, font=f, fill=col, anchor='ls')
        self.im = im
        bb = im.getbbox() or (0, 0, 1, 1)
        self.ink_top = bb[1] - P; self.ink_bot = bb[3] - P
        self.h = asc + desc

    def draw(self, dst, x, top, op=1.0):
        paste(dst, self.im, x - self.PAD, top - self.PAD, op)

    def draw_center(self, dst, cx, top, op=1.0):
        self.draw(dst, cx - self.w / 2, top, op)

    def draw_right(self, dst, rx, top, op=1.0):
        self.draw(dst, rx - self.w, top, op)


def rounded(size, radius, fill, outline=None, width=0):
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=fill, outline=outline, width=width)
    return im


def shadow_sprite(size, radius, blur, alpha):
    pad = blur * 3
    im = Image.new('RGBA', (size[0] + 2 * pad, size[1] + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((pad, pad, pad + size[0], pad + size[1]), radius, fill=(0, 0, 0, alpha))
    return im.filter(ImageFilter.GaussianBlur(blur)), pad


def radial(rad, color, amax, power=2.0):
    yy, xx = np.mgrid[-rad:rad, -rad:rad]
    d = np.sqrt(xx ** 2 + yy ** 2) / rad
    a = np.clip(1 - d, 0, 1) ** power * amax
    arr = np.zeros((2 * rad, 2 * rad, 4), np.uint8)
    arr[..., :3] = color
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def star_sprite(r, color=(255, 244, 200)):
    s = r * 4
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    pts = []
    for k in range(8):
        ang = math.pi / 4 * k - math.pi / 2
        rr = r * 1.9 if k % 2 == 0 else r * 0.42
        pts.append((c + rr * math.cos(ang), c + rr * math.sin(ang)))
    d.polygon(pts, fill=color + (255,))
    glow = radial(s // 2, color, 110, 2.5)
    out = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(im)
    return out


# ------------------------------------------------------------------ static assets
class Assets:
    def __init__(self):
        # background
        y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
        t = np.clip(0.62 * y + 0.38 * x, 0, 1)[..., None]
        img = np.array(NAVY_TOP)[None, None] * (1 - t) + np.array(NAVY_BOT)[None, None] * t
        yy, xx = np.mgrid[0:H, 0:W]
        stripes = (((xx + yy) // 46) % 2).astype(np.float32) * 3.2
        img += stripes[..., None]
        # dot grid in top-right & bottom-left corners
        dots = ((xx % 34 < 3) & (yy % 34 < 3)).astype(np.float32)
        cornerA = np.clip(1 - np.sqrt(((xx - W) / 700.0) ** 2 + (yy / 420.0) ** 2), 0, 1)
        cornerB = np.clip(1 - np.sqrt((xx / 520.0) ** 2 + ((yy - H) / 360.0) ** 2), 0, 1)
        img += (dots * (cornerA + cornerB) * 38)[..., None]
        r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        img *= (1 - 0.32 * np.clip(r - 0.45, 0, 1))[..., None]
        self.bg = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
        self.blobs = [  # sprite, cx, cy, ax, ay, w, phase
            (radial(360, SKY, 30), 330, 260, 70, 45, 0.07, 0.0),
            (radial(300, CORAL, 20), 1560, 880, 80, 50, 0.05, 1.3),
            (radial(440, (90, 120, 255), 28), 1100, 120, 90, 35, 0.04, 2.1),
            (radial(240, GOLD, 14), 230, 930, 50, 40, 0.06, 0.7),
        ]
        # logo
        logo = Image.open(f'{R}/assets/logo_white.png').convert('RGBA')
        self.logo = logo
        self.logo_big = logo.resize((int(logo.width * 230 / logo.height), 230), Image.LANCZOS)
        self.logo_small = logo.resize((int(logo.width * 54 / logo.height), 54), Image.LANCZOS)
        self.logo_lock = logo.resize((int(logo.width * LOCK_LOGO_H / logo.height), LOCK_LOGO_H), Image.LANCZOS)
        self.logo_blur = [self.logo_big.filter(ImageFilter.GaussianBlur(b)) if b else self.logo_big for b in (0, 2, 4, 7, 10)]
        la = np.array(self.logo_big)[..., 3].astype(np.float32) / 255
        self.logo_alpha = la
        g = np.array(self.logo_big.filter(ImageFilter.GaussianBlur(18)))[..., 3]
        glow = np.zeros(g.shape + (4,), np.uint8); glow[..., :3] = SKY; glow[..., 3] = (g * 0.7).astype(np.uint8)
        self.logo_glow = Image.fromarray(glow, 'RGBA')
        # header
        self.header_title = Txt(proj('header_title'), font('semi', 25), WHITE, alpha=235)
        # card frame
        self.card_w, self.card_h = 1100, 619
        self.card_xy = (70, 112)
        self.card_shadow, self.card_shadow_pad = shadow_sprite((self.card_w, self.card_h), 26, 22, 150)
        m = Image.new('L', (self.card_w, self.card_h), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, self.card_w - 1, self.card_h - 1), 26, fill=255)
        self.card_mask = m
        self.card_border = rounded((self.card_w, self.card_h), 26, None, (255, 255, 255, 210), 4)
        # question panel
        self.qp_xy = (70, 752); self.qp_size = (1780, 300)
        self.qpanel = rounded(self.qp_size, 24, (255, 255, 255, 15), (255, 255, 255, 46), 2)
        # right panel
        self.rp_xy = (1210, 112); self.rp_size = (660, 292)
        self.rp_shadow, self.rp_shadow_pad = shadow_sprite(self.rp_size, 22, 18, 130)
        self._leader_static()
        # miss K decorations
        self.mk_back = radial(360, SKY, 92, 1.6)
        self.mk_back2 = radial(260, (255, 255, 255), 40, 2.0)
        self.star = star_sprite(7)
        self.star_small = star_sprite(4)
        # miss k sources
        self.mk_meta = json.load(open(f'{R}/clips/keyed/meta.json')) if os.path.exists(f'{R}/clips/keyed/meta.json') else None
        self._mk = {}
        self.items = {it['n']: it for it in ITEMS}
        self._item_cache = {}

    # ---------------- film leader
    def _leader_static(self):
        w, h = self.rp_size
        base = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(base)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=(10, 12, 18, 255))
        for col_x in (10, w - 10 - 20):
            for yy in range(14, h - 20, 30):
                d.rounded_rectangle((col_x, yy, col_x + 20, yy + 15), 4, fill=(54, 60, 76, 255))
        ix0, iy0, ix1, iy1 = 44, 12, w - 44, h - 12
        self.inner = (ix0, iy0, ix1, iy1)
        # inner frame gradient (warm grey leader)
        iw, ih = ix1 - ix0, iy1 - iy0
        yy, xx = np.mgrid[0:ih, 0:iw]
        rr = np.sqrt(((xx - iw / 2) / (iw / 2)) ** 2 + ((yy - ih / 2) / (ih / 2)) ** 2)
        v = np.clip(1 - 0.45 * rr, 0, 1)
        arr = np.zeros((ih, iw, 4), np.uint8)
        arr[..., 0] = (52 + 46 * v); arr[..., 1] = (62 + 52 * v); arr[..., 2] = (86 + 64 * v); arr[..., 3] = 255
        inner = Image.fromarray(arr, 'RGBA')
        m = Image.new('L', (iw, ih), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, iw - 1, ih - 1), 10, fill=255)
        inner.putalpha(m)
        base.alpha_composite(inner, dest=(ix0, iy0))
        self.leader_base = base
        ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        cx, cy = w // 2, h // 2
        self.ld_c = (cx, cy)
        d.line((ix0 + 6, cy, ix1 - 6, cy), fill=(255, 255, 255, 120), width=2)
        d.line((cx, iy0 + 6, cx, iy1 - 6), fill=(255, 255, 255, 120), width=2)
        for rad, wd, a in ((118, 5, 235), (100, 3, 200)):
            d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=(255, 255, 255, a), width=wd)
        self.leader_over = ov
        rng = np.random.default_rng(7)
        self.grain = []
        for k in range(8):
            g = rng.integers(0, 255, (h, w)).astype(np.uint8)
            a = (rng.random((h, w)) * 34).astype(np.uint8)
            arr = np.zeros((h, w, 4), np.uint8); arr[..., 0] = g; arr[..., 1] = g; arr[..., 2] = g; arr[..., 3] = a
            gi = Image.fromarray(arr, 'RGBA')
            mi = Image.new('L', (w, h), 0); ImageDraw.Draw(mi).rectangle(self.inner, fill=255)
            gi.putalpha(Image.fromarray(np.minimum(np.array(mi), arr[..., 3])))
            self.grain.append(gi)
        self.num = {n: Txt(str(n), font('bebas', 210), WHITE) for n in (1, 2, 3)}
        self.flash = rounded(self.rp_size, 22, (255, 255, 255, 255))

    def leader(self, t_cd, fidx):
        """t_cd: seconds since countdown start (can be <0 before start)."""
        w, h = self.rp_size
        im = self.leader_base.copy()
        cx, cy = self.ld_c
        if t_cd >= 0:
            frac = t_cd % 1.0
            sweep = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(sweep)
            R0 = 300
            d.pieslice((cx - R0, cy - R0, cx + R0, cy + R0), -90, -90 + 360 * frac, fill=(255, 255, 255, 46))
            m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rectangle(self.inner, fill=255)
            sweep.putalpha(Image.fromarray(np.minimum(np.array(sweep)[..., 3], np.array(m))))
            im.alpha_composite(sweep)
        im.alpha_composite(self.leader_over)
        n = 3 if t_cd < 1 else 2 if t_cd < 2 else 1
        local = t_cd - (3 - n) if t_cd >= 0 else 0
        s = 1.0 + 0.22 * (1 - eo(prog(local, 0, 0.18))) if t_cd >= 0 else 1.0
        tx = self.num[n]
        top_ink = (tx.ink_top + tx.ink_bot) / 2
        img = scaled(tx.im, s)
        ox = cx - img.size[0] / 2
        oy = cy - (Txt.PAD + top_ink) * s
        paste(im, img, ox, oy)
        im.alpha_composite(self.grain[fidx % 8])
        rng = np.random.default_rng(fidx)
        if rng.random() < 0.35:
            d = ImageDraw.Draw(im)
            x = int(rng.integers(self.inner[0] + 10, self.inner[2] - 10))
            d.line((x, self.inner[1], x + int(rng.integers(-6, 6)), self.inner[3]), fill=(255, 255, 255, int(rng.integers(30, 80))), width=1)
        fl = rng.random() * 26
        if fl > 3:
            ov = Image.new('RGBA', (w, h), (0, 0, 0, int(fl)))
            m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rectangle(self.inner, fill=int(fl))
            ov.putalpha(m)
            im.alpha_composite(ov)
        return im

    # ---------------- background
    def background(self, t):
        fr = self.bg.copy()
        for spr, cx, cy, ax, ay, w, ph in self.blobs:
            x = cx + ax * math.sin(w * t * 2 * math.pi * 0.25 + ph) - spr.size[0] / 2
            y = cy + ay * math.cos(w * t * 2 * math.pi * 0.2 + ph) - spr.size[1] / 2
            paste(fr, spr, x, y)
        return fr

    # ---------------- per-item sprites
    def item(self, n):
        if n in self._item_cache:
            return self._item_cache[n]
        it = self.items[n]
        c = {}
        src = Image.open(f'{R}/illus/{n:02d}_{it["slug"]}.png').convert('RGB')
        big = src.resize((int(self.card_w * 1.08), int(self.card_h * 1.08)), Image.LANCZOS)
        c['img_big'] = big
        c['label'] = Txt(it['question'], font('semi', 36), GOLD)
        # fit blanks/answer
        size = 92
        while True:
            fb = font('bold', size)
            bw = self._blank_width(it['display'], fb)
            aw = fb.getlength(it['display'])
            if max(bw, aw) <= 1270 or size <= 50:
                break
            size -= 2
        c['size'] = size
        c['blanks'] = self._blank_img(it['display'], font('bold', size))
        c['answer'] = Txt(it['display'], font('bold', size), WHITE)
        c['sentence'] = self._rich(it['sentence'], it['highlight'], 30, SENT_W)
        cs, chl = clue_sentence(it['sentence'], it['highlight'])
        c['clue'] = self._rich(cs, chl, 30, SENT_W, clue=True)
        c['card'] = self._meaning(it)
        self._item_cache[n] = c
        return c

    def _blank_layout(self, display, f):
        """[(kind, x, payload)], total width.  'e_____' style: first letter, then one bar per missing letter."""
        size = f.size
        U, G, LG, WG = 0.40 * size, 0.17 * size, 0.14 * size, 0.42 * size
        out, x = [], 0.0
        for wi, word in enumerate(display.split()):
            if wi:
                x += WG
            out.append(('t', x, word[0])); x += f.getlength(word[0])
            for k in range(len(word) - 1):
                x += LG if k == 0 else G
                out.append(('u', x, U)); x += U
        return out, x

    def _blank_width(self, display, f):
        return self._blank_layout(display, f)[1]

    def _blank_img(self, display, f):
        size = f.size
        asc, desc = f.getmetrics()
        P = Txt.PAD
        lay, tw = self._blank_layout(display, f)
        w = int(tw) + 2 * P + 4
        im = Image.new('RGBA', (w, asc + desc + 2 * P), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        base = P + asc
        th = max(5, int(size * 0.065))
        for kind, x, pay in lay:
            if kind == 't':
                d.text((P + x, base), pay, font=f, fill=WHITE + (255,), anchor='ls')
            else:
                d.rounded_rectangle((P + x, base - th + 2, P + x + pay, base + 2), th // 2, fill=(255, 255, 255, 235))
        o = Txt.__new__(Txt)
        o.im = im; o.w = w - 2 * P; o.asc = asc; o.desc = desc; o.h = asc + desc
        bb = im.getbbox(); o.ink_top = bb[1] - P; o.ink_bot = bb[3] - P
        return o

    def _rich(self, sent, highlights, size, maxw, clue=False):
        """Sentence with highlighted spans. clue=True: spans contain CLUE_BLANK markers, drawn as first letter +
        one solid gold bar of fixed width (all blanks the same length), without the highlight pill."""
        bw = round(size * 2.4)

        def seg_w(f, s):
            return f.getlength(s.replace(CLUE_BLANK, '')) + s.count(CLUE_BLANK) * bw
        mask = [False] * len(sent)
        for hl in highlights:
            i = sent.find(hl)
            if i < 0:
                i = sent.lower().find(hl.lower())
            if i >= 0:
                for j in range(i, i + len(hl)):
                    mask[j] = True
        words, cur = [], []
        for idx, ch in enumerate(sent):
            if ch == ' ':
                if cur:
                    words.append(cur); cur = []
                continue
            if cur and cur[-1][1] == mask[idx]:
                cur[-1] = (cur[-1][0] + ch, mask[idx])
            else:
                cur.append((ch, mask[idx]))
        if cur:
            words.append(cur)
        fn, fh = font('reg', size), font('semi', size)
        sp = fn.getlength(' ')
        lines, lw = [[]], 0
        for wd in words:
            ww = sum(seg_w(fh if hl else fn, s) for s, hl in wd)
            if lines[-1] and lw + sp + ww > maxw:
                lines.append([]); lw = 0
            if lines[-1]:
                lw += sp
            lines[-1].append((wd, lw)); lw += ww
        asc, desc = fn.getmetrics(); lh = int(size * 1.45)
        im = Image.new('RGBA', (maxw + 20, lh * len(lines) + 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for li, line in enumerate(lines):
            y = 6 + li * lh + asc
            for wd, x in line:
                xx = 6 + x
                for s, hl in wd:
                    f = fh if hl else fn
                    col = (GOLD + (255,)) if hl else (236, 241, 250, 255)
                    if hl and not clue:
                        d.rounded_rectangle((xx - 3, y - asc * 0.78, xx + f.getlength(s) + 3, y + desc * 0.55), 6, fill=(255, 200, 66, 46))
                    for k, part in enumerate(s.split(CLUE_BLANK)):
                        if k:
                            th = max(3, round(size * 0.1))
                            d.rounded_rectangle((xx + 3, y + 2, xx + bw - 3, y + 2 + th), th // 2, fill=col)
                            xx += bw
                        if part:
                            d.text((xx, y), part, font=f, fill=col, anchor='ls')
                            xx += f.getlength(part)
        return im

    def _meaning(self, it):
        w, h = self.rp_size
        im = rounded((w, h), 22, (255, 255, 255, 22), (255, 255, 255, 70), 2)
        d = ImageDraw.Draw(im)
        # pos pill
        fp = font('semi', 24)
        pt = it['pos_short'].rstrip('.')
        pw = int(fp.getlength(pt)) + 30
        # headword first, then the POS pill
        hs = 30
        while font('semi', hs).getlength(it['headword']) > w - 28 - pw - 16 - 26 and hs > 20:
            hs -= 1
        fh = font('semi', hs)
        d.text((28, 47), it['headword'], font=fh, fill=WHITE + (255,), anchor='lm')
        px = 28 + int(fh.getlength(it['headword'])) + 16
        d.rounded_rectangle((px, 26, px + pw, 66), 20, fill=CORAL + (255,))
        d.text((px + pw / 2, 47), pt, font=fp, fill=WHITE + (255,), anchor='mm')
        # chinese
        zs = 56
        while font('cjk', zs).getlength(it['zh']) > w - 56 and zs > 30:
            zs -= 2
        d.text((28, 86), it['zh'], font=font('cjk', zs), fill=GOLD + (255,), anchor='lt')
        # definition
        fd = font('reg', 26)
        words = it['definition'].split(' ')
        lines, cur = [], ''
        for wd in words:
            test = (cur + ' ' + wd).strip()
            if fd.getlength(test) > w - 56 and cur:
                lines.append(cur); cur = wd
            else:
                cur = test
        if cur:
            lines.append(cur)
        y = 172
        for ln in lines[:3]:
            d.text((28, y), ln, font=fd, fill=(214, 224, 242, 255), anchor='lt')
            y += 36
        return im

    # ---------------- Miss K sources
    def mk_src(self, name):
        if name not in self._mk:
            self._mk[name] = np.load(f'{R}/clips/keyed/{name}.npy', mmap_mode='r')
        return self._mk[name]

    def mk_frame(self, name, tc):
        arr = self.mk_src(name)
        idx = int(round(tc * 24))
        idx = max(0, min(len(arr) - 1, idx))
        return np.asarray(arr[idx])

    def mk_idle_at(self, tau):
        arr = self.mk_src('idle')
        n = len(arr) - 1
        idx = int(round(max(0.0, tau) * 24)) % n
        return np.asarray(arr[idx])

    def mk_global(self, g):
        """Miss K frame at global time g: scheduled clip, or idle ping-pong that is neutral at both gap ends."""
        X = 0.08
        prev = None
        for c in MK_SCHED:
            if c['start'] <= g < c['start'] + c['dur']:
                tc = g - c['start']
                fr = self.mk_frame(c['name'], tc)
                if tc < X:
                    return blend(self.mk_idle_at(0.0), fr, tc / X)
                return fr
            if c['start'] + c['dur'] <= g:
                prev = c
        nxt = next((c for c in MK_SCHED if c['start'] > g), None)
        if prev is None:
            tau = 0.0 if nxt is None else 0.0
            if nxt is not None:
                L = nxt['start']
                tau = (L / math.pi) * math.sin(math.pi * min(1.0, g / L))
        else:
            e0 = prev['start'] + prev['dur']
            u = g - e0
            if nxt is None:
                tau = u
            else:
                L = nxt['start'] - e0
                tau = (L / math.pi) * math.sin(math.pi * u / L)
        fr = self.mk_idle_at(tau)
        if prev is not None and g - (prev['start'] + prev['dur']) < X:
            last = self.mk_frame(prev['name'], prev['dur'])
            return blend(last, fr, (g - prev['start'] - prev['dur']) / X)
        return fr


A = None
LOCK_LOGO_H = 120

# ------------------------------------------------------------------ Miss K placement
MK_CORNER = dict(s=0.9, cx=1668)
MK_LARGE = dict(s=1.36, cx=1450)


def mk_place(mode_mix):
    """mode_mix: 0 = corner, 1 = large"""
    k = mode_mix
    s = MK_CORNER['s'] + (MK_LARGE['s'] - MK_CORNER['s']) * k
    cx = MK_CORNER['cx'] + (MK_LARGE['cx'] - MK_CORNER['cx']) * k
    return s, cx


def draw_missk(fr, arr, s, cx, t, op=1.0, dx=0.0):
    meta = A.mk_meta
    body_cx = 632 - meta['x0']
    im = Image.fromarray(arr, 'RGBA')
    hh = int(720 * s); ww = int(arr.shape[1] * s)
    im = im.resize((ww, hh), Image.BILINEAR if s < 1.05 else Image.LANCZOS)
    x = cx - body_cx * s + dx
    y = H - hh
    # backlight
    bcx = cx + dx; bcy = y + 250 * s
    paste_scaled(fr, A.mk_back, bcx, bcy, s * 1.05, op * 0.95)
    paste_scaled(fr, A.mk_back2, bcx, y + 200 * s, s, op)
    # rotating dashed ring
    rr = int(235 * s)
    ring = Image.new('RGBA', (2 * rr + 12, 2 * rr + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    rot = (t * 14) % 360
    for k in range(10):
        a0 = rot + k * 36
        d.arc((6, 6, 6 + 2 * rr, 6 + 2 * rr), a0, a0 + 22, fill=GOLD + (170,), width=max(2, int(3 * s)))
    d.ellipse((18, 18, 2 * rr - 6, 2 * rr - 6), outline=(255, 255, 255, 60), width=max(1, int(2 * s)))
    paste(fr, ring, bcx - rr - 6, y + 215 * s - rr - 6, op)
    # soft outer glow from alpha
    a = np.array(im)[..., 3]
    small = cv2.resize(a, (ww // 4, hh // 4), interpolation=cv2.INTER_AREA)
    small = cv2.dilate(small, np.ones((3, 3), np.uint8))
    small = cv2.GaussianBlur(small, (0, 0), 3)
    gl = cv2.resize(small, (ww, hh), interpolation=cv2.INTER_LINEAR)
    glow = np.zeros((hh, ww, 4), np.uint8); glow[..., :3] = (225, 240, 255); glow[..., 3] = (gl * 0.42).astype(np.uint8)
    paste(fr, Image.fromarray(glow, 'RGBA'), x, y, op)
    paste(fr, im, x, y, op)
    # sparkles
    for k, (ox, oy, ph, big) in enumerate(((-205, 70, 0.0, 1), (190, 120, 1.7, 0), (225, -10, 3.1, 1), (-240, 300, 4.4, 0), (170, 330, 2.4, 0))):
        tw = 0.5 + 0.5 * math.sin(t * 2.4 + ph)
        spr = A.star if big else A.star_small
        paste_scaled(fr, spr, bcx + ox * s, y + (oy + 30) * s, s * (0.6 + 0.5 * tw), op * (0.25 + 0.75 * tw))


def blend(a, b, w):
    if w <= 0:
        return a
    if w >= 1:
        return b
    return (a.astype(np.float32) * (1 - w) + b.astype(np.float32) * w).astype(np.uint8)


# ------------------------------------------------------------------ shared UI parts
def draw_header(fr, op, n_done, section, t_item=None, show_counter=True):
    if op <= 0:
        return
    lx, ly = 56, 26
    paste(fr, A.logo_small, lx, ly, op)
    dx = lx + A.logo_small.size[0] + 22
    d_img = Image.new('RGBA', (2, 44), (255, 255, 255, 90))
    paste(fr, d_img, dx, 31, op)
    A.header_title.draw(fr, dx + 22, 53 - A.header_title.asc * 0.62, op)
    # progress bar (top)
    if n_done is not None:
        frac = n_done / N_TOTAL
        if t_item is not None:
            frac = (n_done - 1 + eio(prog(t_item, 0.1, 0.7))) / N_TOTAL
        bar = Image.new('RGBA', (W, 6), (255, 255, 255, 34))
        paste(fr, bar, 0, 0, op)
        if frac > 0:
            fill = Image.new('RGBA', (max(1, int(W * frac)), 6), GOLD + (255,))
            paste(fr, fill, 0, 0, op)
    if show_counter and n_done:
        ct = Txt(f'{n_done:02d} / {N_TOTAL}', font('bebas', 50), WHITE)
        ct.draw_right(fr, 1866, 52 - ct.asc * 0.62, op)
        rx = 1866 - ct.w - 22
    else:
        rx = 1866
    if section:
        fs = font('semi', 19)
        tw = int(fs.getlength(section)) + 4 * len(section)
        chip = rounded((tw + 34, 36), 18, (255, 200, 66, 255))
        d = ImageDraw.Draw(chip)
        x = 17
        for ch in section:
            d.text((x, 18), ch, font=fs, fill=NAVY_TXT + (255,), anchor='lm'); x += fs.getlength(ch) + 4
        paste(fr, chip, rx - chip.size[0], 34, op)


TITLE = {}


def title_sprites():
    if TITLE:
        return TITLE
    TITLE['kick'] = Txt(proj('kicker'), font('bold', 30), NAVY_TXT, tracking=3)
    TITLE['l1'] = Txt(proj('title_lines')[0], font('bebas', 150), WHITE, tracking=2)
    TITLE['l2'] = Txt(proj('title_lines')[1], font('bebas', 150), GOLD, tracking=2)
    TITLE['sub'] = Txt(proj('subtitle'), font('reg', 32), DIM)
    TITLE['lt_name'] = Txt('Miss K', font('bold', 44), WHITE)
    TITLE['lt_role'] = Txt('Your Virtual English Tutor', font('reg', 27), DIM)
    TITLE['presents'] = Txt('PRESENTS', font('med', 22), DIM, tracking=12)
    return TITLE


LOCK_LOGO_CY = 222
LOCK_TOP = 346          # pill top
X_LEFT = 120            # left edge of the title column (as in version 1)


def lock_m(t):
    """0 = centred lockup, 1 = left-aligned column (Miss K on screen)."""
    return eio(prog(t, OPEN_MK_IN - 0.2, OPEN_MK_IN + 0.7))


def _lx(w, m, off=0):
    xc = 960 - w / 2
    return xc + (X_LEFT + off - xc) * m


def logo_cx(m):
    lw = A.logo_lock.size[0]
    return 960 + (X_LEFT + lw / 2 - 960) * m


def draw_title(fr, t, op_all=1.0, t0=3.4, m=1.0):
    T = title_sprites()
    y0 = LOCK_TOP
    p = eo(prog(t, t0, t0 + 0.5))
    a = p * op_all
    kw = T['kick'].w + 40
    pill = rounded((kw, 52), 26, GOLD + (255,))
    dy = 18 * (1 - p)
    px = _lx(kw, m)
    paste(fr, pill, px, y0 + dy, a)
    T['kick'].draw(fr, px + 20, y0 + 26 - T['kick'].asc * 0.62 + dy, a)
    for key, ts, top in (('l1', t0 + 0.15, y0 + 66), ('l2', t0 + 0.3, y0 + 204)):
        p = eo(prog(t, ts, ts + 0.6))
        T[key].draw(fr, _lx(T[key].w, m), top + 34 * (1 - p), p * op_all)
    p = eo(prog(t, t0 + 0.6, t0 + 1.1))
    if p > 0:
        bw = max(2, int(230 * p))
        bx = (960 - bw / 2) + (X_LEFT + 4 - (960 - bw / 2)) * m
        paste(fr, rounded((bw, 9), 4, CORAL + (255,)), bx, y0 + 368, op_all)
    p = eo(prog(t, t0 + 0.8, t0 + 1.3))
    T['sub'].draw(fr, _lx(T['sub'].w, m, 2), y0 + 398 + 14 * (1 - p), p * op_all)


def draw_lower_third(fr, t, t0, t1):
    """Miss K name tag, placed beside her (overlapping her sleeve slightly)."""
    T = title_sprites()
    a = inout(t, t0, t0 + 0.5, t1 - 0.5, t1)
    if a <= 0:
        return
    wbox = max(T['lt_name'].w, T['lt_role'].w) + 60
    dx = 40 * (1 - eo(prog(t, t0, t0 + 0.5)))
    x0, y0 = MK_LARGE['cx'] - LT_RIGHT_INSET - wbox + dx, LT_Y
    box = rounded((wbox, 118), 18, (8, 20, 46, 215), (255, 255, 255, 60), 2)
    paste(fr, box, x0, y0, a)
    paste(fr, rounded((8, 82), 4, GOLD + (255,)), x0 + 18, y0 + 18, a)
    T['lt_name'].draw(fr, x0 + 42, y0 + 14, a)
    T['lt_role'].draw(fr, x0 + 42, y0 + 70, a)


LT_RIGHT_INSET = 200    # tag's right edge sits this far left of Miss K's centre
LT_Y = 830


def draw_part_text(fr, t, part, a_in, a_out):
    key = f'part{part}'
    if key not in TITLE:
        kind, its = PARTS[part - 1]
        TITLE[key] = (Txt(f'PART {part}', font('semi', 30), GOLD, tracking=10),
                      Txt(kind.upper(), font('bebas', 200), WHITE, tracking=4),
                      Txt(f'{len(its)} {kind if len(its) > 1 else kind[:-1]} to revise', font('reg', 34), DIM))
    k, big, sub = TITLE[key]
    cx = 960 if part == 1 else 440
    p = eo(prog(t, a_in, a_in + 0.55)); o = 1 - prog(t, a_out, a_out + 0.4)
    k.draw_center(fr, cx, 350 + 20 * (1 - p), p * o)
    big.draw_center(fr, cx, 396 + 30 * (1 - p), p * o)
    p2 = eo(prog(t, a_in + 0.2, a_in + 0.75))
    sub.draw_center(fr, cx, 636 + 16 * (1 - p2), p2 * o)
    p3 = eo(prog(t, a_in + 0.3, a_in + 0.8))
    if p3 > 0:
        lw = int(300 * p3)
        paste(fr, rounded((max(2, lw), 6), 3, CORAL + (255,)), cx - lw / 2, 610, o)


def draw_logo(fr, t, t0, cx=960, cy=455, sc=1.0, shine_t=None, op=1.0):
    """Transparent logo (no glow / no fill behind the knocked-out letters)."""
    p = eo(prog(t, t0, t0 + 0.9))
    if p <= 0:
        return
    bl = int(round((1 - p) * 4))
    src = A.logo_blur[min(4, bl)]
    s = (1.08 - 0.08 * p) * sc
    shining = False
    if shine_t is not None:
        sp = prog(t, shine_t, shine_t + 0.9)
        if 0 < sp < 1:
            shining = True
            arr = np.array(src).copy()
            h, w = arr.shape[:2]
            yy, xx = np.mgrid[0:h, 0:w]
            u = (xx / w + (yy / h) * 0.45) / 1.45
            pos = -0.2 + 1.4 * sp
            band = np.exp(-((u - pos) / 0.07) ** 2)
            col = np.array([255, 214, 120], np.float32)
            rgb = arr[..., :3].astype(np.float32)
            rgb = rgb * (1 - band[..., None] * 0.85) + col * band[..., None] * 0.85
            arr[..., :3] = rgb.astype(np.uint8)
            src = Image.fromarray(arr, 'RGBA')
    lock_s = A.logo_lock.size[1] / A.logo_big.size[1]
    if not shining and bl == 0 and abs(s - lock_s) < 1e-3:
        paste_scaled(fr, A.logo_lock, cx, cy, 1.0, p * op)
    else:
        paste_scaled(fr, src, cx, cy, s, p * op)


def draw_logo_center(fr, t, t0, cy=455, with_glow=False, shine_t=None):
    draw_logo(fr, t, t0, 960, cy, 1.0, shine_t)


def ripple(fr, t, t0, cy=455):
    for k in range(2):
        p = prog(t, t0 + k * 0.35, t0 + k * 0.35 + 1.8)
        if 0 < p < 1:
            r = int(130 + 420 * eo(p))
            im = Image.new('RGBA', (2 * r + 6, 2 * r + 6), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse((3, 3, 3 + 2 * r, 3 + 2 * r), outline=(255, 255, 255, int(110 * (1 - p))), width=2)
            paste(fr, im, 960 - r - 3, cy - r - 3)


def confetti(fr, t, t0, dur=5.0, n=70):
    p = t - t0
    if p < 0 or p > dur + 2:
        return
    rng = np.random.default_rng(11)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cols = [GOLD, CORAL, SKY, (255, 255, 255), (150, 230, 160)]
    for i in range(n):
        x0 = rng.uniform(80, 1100); vy = rng.uniform(160, 330); delay = rng.uniform(0, 1.6)
        sw = rng.uniform(20, 60); ph = rng.uniform(0, 6.28); sz = rng.uniform(7, 14); col = cols[i % len(cols)]
        tt = p - delay
        if tt < 0:
            continue
        y = -30 + vy * tt
        if y > H + 20:
            continue
        x = x0 + sw * math.sin(tt * 2.2 + ph)
        ang = tt * 4 + ph
        c, s_ = math.cos(ang), math.sin(ang)
        w2, h2 = sz, sz * 0.45 * abs(math.cos(tt * 5 + ph)) + 2
        pts = [(x + c * dx - s_ * dy, y + s_ * dx + c * dy) for dx, dy in ((-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2))]
        fade_a = int(255 * (1 - prog(p, dur, dur + 1.5)))
        d.polygon(pts, fill=col + (fade_a,))
    fr.alpha_composite(layer)


# ------------------------------------------------------------------ segments
def render_opening(seg, t, g, fidx):
    fr = A.background(g)
    if t < 4.0:
        ripple(fr, t, 0.6)
    m = lock_m(t)
    pm = eio(prog(t, 3.0, 3.7))                      # logo rises into the title lockup (no corner shrink)
    lock_s = A.logo_lock.size[1] / A.logo_big.size[1]
    cy = 455 + (LOCK_LOGO_CY - 455) * pm
    sc = 1.0 + (lock_s - 1.0) * pm
    draw_logo(fr, t, 0.5, logo_cx(m), cy, sc, shine_t=1.35)
    T = title_sprites()
    lp = eo(prog(t, 1.5, 2.1)) * (1 - prog(t, 2.85, 3.2))
    if lp > 0:
        lw = int(380 * eo(prog(t, 1.5, 2.1)))
        paste(fr, rounded((max(2, lw), 3), 1, GOLD + (255,)), 960 - lw / 2, 606, lp)
        T['presents'].draw_center(fr, 960, 628, eo(prog(t, 1.8, 2.4)) * (1 - prog(t, 2.85, 3.2)))
    if t >= 3.55:
        draw_title(fr, t, t0=3.6, m=m)
    if t >= OPEN_MK_IN:
        p = eo(prog(t, OPEN_MK_IN, OPEN_MK_IN + 0.7))
        s, cx = mk_place(1.0)
        draw_missk(fr, A.mk_global(g), s, cx, g, op=p, dx=160 * (1 - p))
        draw_lower_third(fr, t, OPEN_MK_IN + 0.8, OPEN_MK_IN + 9.0)
    if t < 0.5:
        paste(fr, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0, 0, 1 - prog(t, 0, 0.5))
    return fr


def render_part(seg, t, g, fidx):
    fr = A.background(g)
    o = 1 - prog(t, 0.0, 0.35)
    if o > 0:
        draw_title(fr, 99, op_all=o, m=1.0)
        paste_scaled(fr, A.logo_lock, logo_cx(1.0), LOCK_LOGO_CY, 1.0, o)
    hop = eo(prog(t, 0.4, 0.9))
    if hop > 0:
        paste(fr, A.logo_small, 56, 26, hop)
        draw_header_rest(fr, hop, 0, None)
    draw_part_text(fr, t, 1, 0.45, 1.95)
    k = eio(prog(t, 0.0, 0.7))
    if k < 1:
        s, cx = mk_place(1.0)
        draw_missk(fr, A.mk_global(g), s, cx, g, op=1 - k, dx=520 * k)
    return fr


def draw_header_rest(fr, op, n_done, section, t_item=None):
    """header without re-drawing the logo"""
    dx = 56 + A.logo_small.size[0] + 22
    paste(fr, Image.new('RGBA', (2, 44), (255, 255, 255, 90)), dx, 31, op)
    A.header_title.draw(fr, dx + 22, 53 - A.header_title.asc * 0.62, op)
    bar = Image.new('RGBA', (W, 6), (255, 255, 255, 34))
    paste(fr, bar, 0, 0, op)
    if n_done:
        frac = n_done / N_TOTAL
        if t_item is not None:
            frac = (n_done - 1 + eio(prog(t_item, 0.1, 0.7))) / N_TOTAL
        paste(fr, Image.new('RGBA', (max(1, int(W * frac)), 6), GOLD + (255,)), 0, 0, op)
    rx = 1866
    if n_done:
        ct = Txt(f'{n_done:02d} / {N_TOTAL}', font('bebas', 50), WHITE)
        ct.draw_right(fr, 1866, 52 - ct.asc * 0.62, op)
        rx = 1866 - ct.w - 22
    if section:
        fs = font('semi', 19)
        tw = int(sum(fs.getlength(c) for c in section)) + 4 * (len(section) - 1)
        chip = rounded((tw + 34, 36), 18, GOLD + (255,))
        d = ImageDraw.Draw(chip)
        x = 17
        for ch in section:
            d.text((x, 18), ch, font=fs, fill=NAVY_TXT + (255,), anchor='lm'); x += fs.getlength(ch) + 4
        paste(fr, chip, rx - chip.size[0], 34, op)


def mk_item_frame(n, t, g):
    return A.mk_global(g)


def render_item(seg, t, g, fidx):
    n = seg['item']
    it = A.items[n]
    c = A.item(n)
    fr = A.background(g)
    section = 'ITEM'
    paste(fr, A.logo_small, 56, 26, 1.0)
    draw_header_rest(fr, 1.0, n, section, t_item=t)
    ex = 1 - eo(prog(t, EXIT_AT, ITEM_DUR))
    # image card
    pin = eo(prog(t, 0.0, 0.5))
    op = pin * ex
    if op > 0:
        cw, ch = A.card_w, A.card_h
        kb = 1.0 + 0.06 * prog(t, 0, ITEM_DUR)          # ken burns zoom
        big = c['img_big']
        bw, bh = big.size
        vw, vh = bw / 1.08 * (1.08 / kb), bh / 1.08 * (1.08 / kb)
        cxk, cyk = bw / 2, bh / 2
        crop = big.crop((int(cxk - vw / 2), int(cyk - vh / 2), int(cxk + vw / 2), int(cyk + vh / 2))).resize((cw, ch), Image.BILINEAR)
        card = crop.convert('RGBA'); card.putalpha(A.card_mask)
        card.alpha_composite(A.card_border)
        s = 0.94 + 0.06 * pin + 0.02 * (1 - ex)
        x0, y0 = A.card_xy
        ccx, ccy = x0 + cw / 2, y0 + ch / 2
        sh = A.card_shadow
        paste_scaled(fr, sh, ccx, ccy + 14, s, op)
        paste_scaled(fr, card, ccx, ccy, s, op)
    # question panel
    qx, qy = A.qp_xy
    qop = eo(prog(t, 0.15, 0.6)) * ex
    paste(fr, A.qpanel, qx, qy, qop)
    lab = c['label']
    lab_op = qop * (1 - 0.45 * prog(t, CD_END, CD_END + 0.3))
    # small question badge
    badge = rounded((40, 40), 20, GOLD + (255,))
    ImageDraw.Draw(badge).text((20, 21), '?', font=font('bold', 28), fill=NAVY_TXT + (255,), anchor='mm')
    paste(fr, badge, qx + 32, qy + 22 + 10 * (1 - qop), lab_op)
    lab.draw(fr, qx + 84, qy + 18 + 10 * (1 - qop), lab_op)
    size = c['size']
    base_top = qy + 60
    bl = c['blanks']
    bp_in = eo(prog(t, 0.3, 0.75))
    bp_out = prog(t, CD_END, CD_END + 0.2)
    if bp_out < 1:
        bl.draw(fr, qx + 34, base_top + 16 * (1 - bp_in) - 18 * bp_out, bp_in * (1 - bp_out) * ex)
    if t >= CD_END:
        ans = c['answer']
        p = prog(t, CD_END + 0.02, CD_END + 0.4)
        s = 0.82 + 0.18 * eback(p) if p < 1 else 1.0
        a_op = clamp(p * 2.5) * ex
        img = scaled(ans.im, s)
        # anchor left / vertical centre of the ascent box
        ay = base_top + ans.asc * 0.5
        paste(fr, img, qx + 34 - Txt.PAD * s, ay - (Txt.PAD + ans.asc * 0.5) * s, a_op)
        up = eo(prog(t, CD_END + 0.15, CD_END + 0.55))
        if up > 0:
            uw = int(ans.w * up)
            paste(fr, rounded((max(2, uw), 7), 3, GOLD + (255,)), qx + 34, base_top + ans.asc + 10, ex)
        sp = eo(prog(t, INFO_AT, INFO_AT + 0.45))
        paste(fr, c['sentence'], qx + 28, qy + 190 + 12 * (1 - sp), sp * ex)
    # clue: the sample sentence with the item blanked (first letters given), during the thinking time
    cl_in = eo(prog(t, 0.45, 0.9))
    cl_out = prog(t, CD_END, CD_END + 0.25)
    if cl_out < 1:
        paste(fr, c['clue'], qx + 28, qy + 190 + 12 * (1 - cl_in), cl_in * (1 - cl_out) * ex)
    # right panel: countdown -> meaning card
    rx, ry = A.rp_xy
    if t < CD_END + 0.05:
        lop = eo(prog(t, 0.1, 0.45)) * ex
        paste(fr, A.rp_shadow, rx - A.rp_shadow_pad, ry - A.rp_shadow_pad + 10, lop)
        paste(fr, A.leader(t - CD_START, fidx), rx, ry + 12 * (1 - lop), lop)
    else:
        mp = eo(prog(t, CD_END + 0.1, CD_END + 0.45))
        paste(fr, A.rp_shadow, rx - A.rp_shadow_pad, ry - A.rp_shadow_pad + 10, mp * ex * 0.7)
        paste(fr, c['card'], rx, ry + 12 * (1 - mp), mp * ex)
    fl = 1 - prog(t, CD_END, CD_END + 0.3)
    if t >= CD_END and fl > 0:
        paste(fr, A.flash, rx, ry, 0.85 * fl)
    # Miss K badge (voice-call style): rings + voice bars while her answer plays
    vd = ITEM_VOICE.get(n, {}).get('dur', 1.0)
    sp = clamp((t - WORD_AT + 0.05) / 0.15) * (1 - clamp((t - WORD_AT - vd - 0.1) / 0.25))
    draw_badge(fr, g, BADGE_CX, BADGE_CY, sp, op=ex)
    return fr


def render_transition(seg, t, g, fidx):
    fr = A.background(g)
    paste(fr, A.logo_small, 56, 26, 1.0)
    draw_header_rest(fr, 1.0, N_PART1, 'ITEM')
    draw_part_text(fr, t, 2, 0.7, TRANS_DUR - 1.0)
    k = eo(prog(t, 0.0, TRANS_GROW)) * (1 - eio(prog(t, TRANS_GROW + TRANS_CLIP, TRANS_GROW + TRANS_CLIP + 0.8)))
    if k > 0:
        s, cx = mk_place(1.0)
        draw_missk(fr, A.mk_global(g), s, cx, g, op=k, dx=520 * (1 - k))
    return fr


CONC = {}


def render_conclusion(seg, t, g, fidx):
    fr = A.background(g)
    hop = 1 - prog(t, 0.0, 0.6)
    paste(fr, A.logo_small, 56, 26, 1.0)
    if hop > 0:
        draw_header_rest(fr, hop, N_TOTAL, 'ITEM')
    if not CONC:
        CONC['wd'] = Txt('WELL DONE!', font('bebas', 180), GOLD, tracking=3)
        CONC['l1'] = Txt(proj('conclusion_l1').format(total=N_TOTAL), font('semi', 38), WHITE)
        CONC['l2'] = Txt(proj('conclusion_l2'), font('semi', 38), WHITE)
        CONC['chips'] = [(Txt(f'{len(its)} {k if len(its) > 1 else k[:-1]}', font('semi', 26), NAVY_TXT), col)
                         for (k, its), col in zip(PARTS, (GOLD, SKY))]
        CONC['l3'] = Txt('Keep using them in your speaking and writing!', font('reg', 30), DIM)
    out = 1 - prog(t, CONC_DUR - 1.3, CONC_DUR - 0.6)
    x0 = 120
    p = eo(prog(t, 1.0, 1.6)); CONC['wd'].draw(fr, x0, 250 + 40 * (1 - p), p * out)
    p = eo(prog(t, 1.5, 2.1)); CONC['l1'].draw(fr, x0 + 4, 470 + 16 * (1 - p), p * out); CONC['l2'].draw(fr, x0 + 4, 524 + 16 * (1 - p), p * out)
    p = eo(prog(t, 2.2, 2.7))
    if p > 0:
        x = x0 + 4
        for tx, col in CONC['chips']:
            chip = rounded((tx.w + 40, 50), 25, col + (255,))
            paste(fr, chip, x, 612 + 14 * (1 - p), p * out)
            tx.draw(fr, x + 20, 612 + 25 - tx.asc * 0.62 + 14 * (1 - p), p * out)
            x += tx.w + 60
    p = eo(prog(t, 3.0, 3.6)); CONC['l3'].draw(fr, x0 + 4, 702 + 14 * (1 - p), p * out)
    confetti(fr, t, 1.0, dur=5.0)
    k = eo(prog(t, 0.0, TRANS_GROW))
    s, cx = mk_place(1.0)
    arr = A.mk_global(g)
    mop = k * (1 - prog(t, CONC_DUR - 1.0, CONC_DUR - 0.2))
    draw_missk(fr, arr, s, cx, g, op=mop, dx=520 * (1 - k))
    if t > CONC_DUR - 1.2:   # fade the small header logo away
        pass
    return fr


OUT = {}


OUT_DY = int(os.environ.get('OUT_DY', '68'))


def render_outro(seg, t, g, fidx):
    fr = A.background(g)
    hop = 1 - prog(t, 0.0, 0.5)
    paste(fr, A.logo_small, 56, 26, hop)
    if not OUT:
        OUT['l1'] = Txt('Thanks for revising with Miss K!', font('semi', 36), WHITE)
        OUT['l2'] = Txt(proj('header_title'), font('reg', 26), DIM)
    ripple(fr, t, 0.3, cy=420 + OUT_DY)
    draw_logo_center(fr, t, 0.3, cy=420 + OUT_DY, shine_t=1.1)
    lp = eo(prog(t, 1.2, 1.8))
    if lp > 0:
        lw = int(380 * lp)
        paste(fr, rounded((max(2, lw), 3), 1, GOLD + (255,)), 960 - lw / 2, 566 + OUT_DY, 1)
    OUT['l1'].draw_center(fr, 960, 596 + OUT_DY + 14 * (1 - eo(prog(t, 1.5, 2.1))), eo(prog(t, 1.5, 2.1)))
    fo = eio(prog(t, OUTRO_DUR - 3.0, OUTRO_DUR - 1.0))   # v5: 2 s eased fade, then hold black
    if fo > 0:
        paste(fr, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0, 0, fo)
    return fr



# ------------------------------------------------------------------ format v2: badge + pop-up
BD = 172                      # badge diameter
BADGE_CX, BADGE_CY = 1540, 548
QP_W = 1780                   # question panel spans the width (no corner Miss K)
_BADGE = {}


def badge_sprite():
    if 'im' not in _BADGE:
        from keying import key
        src = np.array(Image.open(f'{R}/assets/missk_neutral.png').convert('RGB'))
        hh, ww = src.shape[:2]
        sc = hh / 1440.0                                   # crop defined on the 2560x1440 keyframe
        crop = src[int(60 * sc):int(700 * sc), int(930 * sc):int(1570 * sc)]
        im = Image.fromarray(key(crop), 'RGBA').resize((BD, BD), Image.LANCZOS)
        base = Image.new('RGBA', (BD, BD), (28, 62, 128, 255))
        base.alpha_composite(radial(BD // 2, SKY, 150, 1.4).resize((BD, BD)))
        base.alpha_composite(im)
        m = Image.new('L', (BD, BD), 0); ImageDraw.Draw(m).ellipse((0, 0, BD - 1, BD - 1), fill=255)
        disc = Image.new('RGBA', (BD, BD), (0, 0, 0, 0)); disc.paste(base, (0, 0), m)
        ring = Image.new('RGBA', (BD + 16, BD + 16), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((3, 3, BD + 12, BD + 12), outline=GOLD + (255,), width=5)
        ring.alpha_composite(disc, (8, 8))
        _BADGE['im'] = ring
        _BADGE['name'] = Txt('Miss K', font('bold', 34), WHITE)
        _BADGE['cap'] = Txt('Say it out loud!', font('med', 24), DIM)
    return _BADGE


def draw_badge(fr, t, cx, cy, speak=0.0, op=1.0):
    B = badge_sprite()
    if op <= 0:
        return
    if speak > 0:
        for k in range(3):
            ph = ((t * 1.25) + k / 3) % 1.0
            r = BD / 2 + 8 + 44 * ph
            ring = Image.new('RGBA', (int(2 * r) + 8, int(2 * r) + 8), (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse((4, 4, 4 + 2 * r, 4 + 2 * r), outline=GOLD + (int(200 * (1 - ph)),), width=4)
            paste(fr, ring, cx - r - 4, cy - r - 4, speak * op)
        paste_scaled(fr, A.mk_back2, cx, cy, 0.55, 0.6 * speak * op)
    paste(fr, B['im'], cx - B['im'].size[0] / 2, cy - B['im'].size[1] / 2, op)
    B['name'].draw_center(fr, cx, cy + BD / 2 + 20, op)
    ty = cy + BD / 2 + 70
    if speak > 0:
        n = 9; bw = 9; gap = 7; x0 = cx - (n * bw + (n - 1) * gap) / 2
        for k in range(n):
            h = 8 + 34 * abs(math.sin(t * 9 + k * 1.3)) * (0.5 + 0.5 * math.sin(t * 4.1 + k))
            paste(fr, rounded((bw, int(h)), 4, GOLD + (255,)), x0 + k * (bw + gap), ty + 20 - h / 2, speak * op)
    if speak < 1:
        B['cap'].draw_center(fr, cx, ty, (1 - speak) * op)


POP = {}


def render_popup(seg, t, g, fidx):
    fr = A.background(g)
    paste(fr, A.logo_small, 56, 26, 1.0)
    n_done = seg['n_done']
    draw_header_rest(fr, 1.0, n_done, 'ITEM')
    D = seg['dur']
    k = eo(prog(t, 0.0, 0.45)) * (1 - eio(prog(t, D - 0.55, D - 0.05)))
    key_ = seg['pop']
    if key_ not in POP:
        line = POP_LINES[key_]
        if '! ' in line:
            a_, b_ = line.split('! ', 1); a_ += '!'
        elif '. ' in line:
            a_, b_ = line.split('. ', 1); a_ += '.'
        else:
            a_, b_ = line, ''
        POP[key_] = (Txt(a_.upper(), font('bebas', 128), NAVY_TXT), Txt(b_, font('bold', 50), CORAL) if b_ else None)
    if 'bub' not in POP:
        bw, bh = 1000, 300
        POP['bub'] = rounded((bw, bh), 40, (255, 255, 255, 236))
        tail = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(tail).polygon([(0, 0), (80, 30), (0, 70)], fill=(255, 255, 255, 236))
        POP['tail'] = tail
        POP['sh'] = shadow_sprite((bw, bh), 40, 26, 120)
    t1, t2 = POP[key_]
    bw, bh = POP['bub'].size
    bx, by = 150, 330
    bp = eback(clamp(prog(t, 0.25, 0.75))) if t < 0.75 else 1.0
    bop = clamp(prog(t, 0.25, 0.5)) * (1 - prog(t, D - 0.6, D - 0.2))
    if bop > 0:
        sc = 0.85 + 0.15 * bp
        layer = Image.new('RGBA', (bw + 120, bh + 80), (0, 0, 0, 0))
        shs, shp = POP['sh']
        layer.alpha_composite(shs, (max(0, 40 - shp), max(0, 40 - shp + 12)))
        layer.alpha_composite(POP['bub'], (40, 40))
        layer.alpha_composite(POP['tail'], (40 + bw - 6, 40 + 150))
        dl = Txt.PAD
        t1.draw(layer, 40 + bw / 2 - t1.w / 2, 40 + (40 if t2 else 86), 1.0)
        if t2:
            t2.draw(layer, 40 + bw / 2 - t2.w / 2, 40 + 190, 1.0)
        paste_scaled(fr, layer, bx - 40 + (bw + 120) / 2, by - 40 + (bh + 80) / 2, sc, bop)
        pr = Txt(f'{n_done} of {N_TOTAL} done', font('semi', 30), DIM)
        pr.draw_center(fr, bx + bw / 2, by + bh + 50, bop)
        sw = max(8, min(30, int((bw - 40) / N_TOTAL) - 6)); gp = 6
        tot = N_TOTAL * sw + (N_TOTAL - 1) * gp; x0 = bx + bw / 2 - tot / 2
        lit = n_done - 1 + clamp(prog(t, 0.6, 1.0))
        for j in range(N_TOTAL):
            col = GOLD + (255,) if j < lit else (255, 255, 255, 50)
            paste(fr, rounded((sw, 10), 5, col), x0 + j * (sw + gp), by + bh + 106, bop)
    if k > 0:
        s_, cx = mk_place(1.0)
        draw_missk(fr, A.mk_global(g), s_, cx, g, op=k, dx=520 * (1 - k))
    return fr

RENDER = dict(popup=render_popup, opening=render_opening, part=render_part, item=render_item, transition=render_transition,
              conclusion=render_conclusion, outro=render_outro)


def frame_at(g):
    for s in SEGMENTS:
        if s['start'] <= g < s['start'] + s['dur'] or s is SEGMENTS[-1]:
            t = g - s['start']
            f = int(round(g * FPS))
            return RENDER[s['kind']](s, t, g, f)


def render_segment(i):
    global A
    if A is None:
        A = Assets()
    s = SEGMENTS[i]
    os.makedirs(f'{R}/work/segs', exist_ok=True)
    out = f'{R}/work/segs/seg_{i:03d}.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-g', '60', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(s['nf']):
        f = s['f0'] + k
        g = f / FPS
        t = g - s['start']
        fr = RENDER[s['kind']](s, t, g, f)
        p.stdin.write(fr.convert('RGB').tobytes())
    p.stdin.close(); p.wait()
    return i


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'test':
        A = Assets()
        os.makedirs(f'{R}/work/test', exist_ok=True)
        for a in sys.argv[2:]:
            g = float(a)
            frame_at(g).convert('RGB').save(f'{R}/work/test/frame_{g:07.2f}.png')
            print('saved', g)
    elif mode == 'segs':
        for i in sys.argv[2].split(','):
            render_segment(int(i)); print('seg', i)
    elif mode in ('all', 'pool'):
        from multiprocessing import Pool
        nw = int(sys.argv[2]) if len(sys.argv) > 2 else 6
        if mode == 'pool':
            sel = [int(v) for v in sys.argv[3].split(',')]
        else:
            sel = list(range(len(SEGMENTS)))
        order = sorted(sel, key=lambda i: -SEGMENTS[i]['nf'])
        with Pool(nw) as pool:
            for i in pool.imap_unordered(render_segment, order):
                print('done seg', i, flush=True)
