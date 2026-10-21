#!/usr/bin/env python3
"""Nemi Studio intro film: an edit in the grammar of the reference reel (r8).

Eye opens -> pupil dilates -> dive into the pupil -> space -> history in a decelerating
flash montage -> hero -> whip -> industries burst -> hero -> spin -> macro burst -> hero ->
night city -> eye closes / opens -> white flash -> wordmark.

    python3 tools/intro_film.py <clips-dir> <images-dir> <out.mp4> [--format web|reel] [--lang de|en] [--preview N]

clips-dir:  Mixkit clips named <id>.mp4      images-dir: history stills 01.jpg..13.jpg
"""
import argparse
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, 'fonts')

ap = argparse.ArgumentParser()
ap.add_argument('clips')
ap.add_argument('images')
ap.add_argument('out')
ap.add_argument('--format', default='web')
ap.add_argument('--lang', default='de')
ap.add_argument('--preview', type=int, default=0, help='only render every Nth frame as JPGs into out dir')
ap.add_argument('--width', type=int, default=1920)
ap.add_argument('--music', default='')
ap.add_argument('--music-at', type=float, default=20.31, help='track time that plays at film time 0')
args = ap.parse_args()

REEL = args.format == 'reel'
W = 1080 * args.width // 1920 if REEL else args.width
H = round(W * 16 / 9) if REEL else round(W * 9 / 16)
S = W / (1080 if REEL else 1920)  # scale factor for pixel sizes designed at 1920 (web) / 1080 (reel)

# ---------------------------------------------------------------- copy
T = {
    'de': {
        'eye': '40.000 v. Chr. — heute',
        'h1': ['Menschen wollen', '*gesehen* werden.'],
        'h2': ['Jedes Geschäft', 'hat eine *Geschichte*.'],
        'h3': ['Die meisten Websites', '*schweigen*.'],
        'end1': 'Wir geben ihnen eine Stimme.',
        'url': 'NEMISTUDIO.AT',
    },
    'en': {
        'eye': '40,000 BC — today',
        'h1': ['People want', 'to be *seen*.'],
        'h2': ['Every business', 'has a *story*.'],
        'h3': ['Most websites', 'stay *silent*.'],
        'end1': 'We give them a voice.',
        'url': 'NEMISTUDIO.AT',
    },
}[args.lang]

# ---------------------------------------------------------------- shots
# src: 'v:<id>' video, 'i:<nn>' still, 'black'
# t: source start (s), n: frames, sp: playback speed (negative = reverse), z0/z1: zoom, c: focus point (0..1)
def sh(src, t=0.0, n=2, sp=1.0, z0=1.0, z1=None, c=(0.5, 0.5), dx=0.0, **kw):
    d = dict(src=src, t=t, n=n, sp=sp, z0=z0, z1=z0 * 1.04 if z1 is None else z1, c=c, dx=dx)
    d.update(kw)
    return d

PUPIL = (0.44, 0.59)
shots = []
mark = {}

def add(*ss):
    for s in ss:
        shots.append(s)

def here():
    return sum(s['n'] for s in shots)

# 1) the eye opens, settles, pupil widens, dive
mark['open'] = here()
add(sh('v:48017', 0.75, 30, 0.8, 1.0, 1.10, PUPIL, fadein=10))
add(sh('v:48017', 1.55, 22, 1.0, 1.10, 1.22, PUPIL))
mark['dilate'] = here()
add(sh('v:48017', 3.4, 18, -2.6, 1.22, 2.6, PUPIL, ease='in'))      # reverse = pupil widens
mark['dive'] = here()
add(sh('v:48017', 1.6, 9, 0.0, 2.6, 26.0, PUPIL, ease='expo', radial=0.35))
add(sh('black', n=5))
# 2) space: inside the eye there is a world
mark['space'] = here()
add(sh('v:29351', 1.0, 34, 1.0, 0.78, 1.55, (0.48, 0.5), fadein=8, ease='in'))
add(sh('v:45032', 4.0, 12, 1.2, 1.25, 2.6, (0.5, 0.5), ease='expo', radial=0.25, flash_out=6))

# 3) history burst: decelerating flash cuts
mark['burst1'] = here()
B1 = [
    ('i:02', 0, (0.5, 0.5)), ('v:45676', 2, (0.5, 0.55)), ('i:03', 0, (0.5, 0.5)), ('v:52312', 3, (0.5, 0.5)),
    ('i:01', 0, (0.5, 0.42)), ('i:05', 0, (0.5, 0.5)), ('v:47380', 2, (0.5, 0.5)), ('v:3461', 3, (0.55, 0.5)),
    ('v:9755', 0.5, (0.45, 0.35)), ('v:1759', 2, (0.5, 0.5)), ('v:50695', 2, (0.5, 0.5)), ('v:21612', 1, (0.5, 0.5)),
    ('v:3819', 2, (0.5, 0.5)), ('i:07', 0, (0.5, 0.5)), ('i:08', 0, (0.5, 0.5)), ('v:21617', 1, (0.5, 0.5)),
    ('v:21626', 6, (0.5, 0.55)), ('i:09', 0, (0.5, 0.5)), ('v:21333', 2, (0.5, 0.5)), ('v:43374', 4, (0.5, 0.5)),
    ('v:4421', 6.5, (0.5, 0.5)), ('v:4143', 2, (0.5, 0.5)), ('v:46291', 3, (0.5, 0.5)), ('v:1140', 2, (0.5, 0.5)),
    ('v:1728', 4, (0.5, 0.5)),
]
LEN1 = [2] * 15 + [3, 3, 3, 4, 4, 5, 6, 7, 8, 11]  # 84 frames: the hero lands on the beat
YEARS = ['−40.000', '−32.000', '−17.000', '−12.000', '−8.000', '−3.200', '−1.400', '−1.000', '−480', '−100',
         '800', '1200', '1450', '1455', '1492', '1569', '1650', '1910', '1920', '1925', '1937', '1955', '1962', '1971', '1991']
for k, ((src, t, c), n) in enumerate(zip(B1, LEN1)):
    add(sh(src, t, n, 1.0, 1.06, 1.12, c, year=YEARS[k]))
mark['hero1'] = here()
add(sh('v:46635', 2.0, 84, 0.6, 1.05, 1.16, (0.62, 0.42), letterbox=True, text='h1', eyebrow='eye', year='2026'))
mark['whip1'] = here()
# 4) industries burst
B2 = [
    ('v:41858', 3.0), ('v:4982', 2.0), ('v:47555', 6.0), ('v:43222', 3.0), ('v:33328', 2.0), ('v:39500', 4.0),
    ('v:52088', 6.0), ('v:23222', 22.0), ('v:22240', 4.0), ('v:242', 3.0), ('v:4915', 2.0), ('v:4196', 6.0),
    ('v:5015', 6.0), ('v:41858', 8.5), ('v:39500', 10.0), ('v:33328', 5.0),
]
LEN2 = [2] * 9 + [3, 3, 4, 5, 6, 7, 11]
for (src, t), n in zip(B2, LEN2):
    add(sh(src, t, n, 1.0, 1.05, 1.1))
mark['hero2'] = here()
add(sh('v:47555', 4.7, 53, 0.45, 1.04, 1.14, (0.5, 0.45), letterbox=True, text='h2'))
mark['spin'] = here()
# 5) macro burst
B3 = [('v:41858', 10.5, (0.5, 0.5)), ('v:105', 3, (0.5, 0.5)), ('v:52304', 2, (0.5, 0.5)), ('v:3653', 3, (0.4, 0.5)),
      ('v:45674', 4, (0.5, 0.6)), ('v:39500', 13, (0.6, 0.6)), ('v:1140', 6, (0.5, 0.5)), ('v:3463', 3, (0.5, 0.5)),
      ('v:4982', 6, (0.5, 0.5)), ('v:28893', 3, (0.4, 0.5))]
LEN3 = [2] * 6 + [3, 3, 5, 8]
for (src, t, c), n in zip(B3, LEN3):
    add(sh(src, t, n, 1.0, 1.15, 1.25, c))
mark['hero3'] = here()
add(sh('v:43222', 1.5, 38, 0.6, 1.05, 1.13, (0.55, 0.42)))
add(sh('v:22240', 2.2, 20, 1.0, 1.0, 1.06, (0.5, 0.5)))
add(sh('v:52088', 4.0, 14, 0.6, 1.05, 1.1))
add(sh('v:33328', 1.0, 12, 1.0, 1.05, 1.1, (0.55, 0.4)))
mark['night'] = here()
add(sh('v:49845', 12.0, 57, 1.0, 1.02, 1.12, (0.5, 0.5), letterbox=True, text='h3'))
# 6) the eye closes ... and opens: white flash
mark['blink'] = here()
add(sh('v:4257', 3.85, 18, 0.8, 1.12, 1.24, (0.5, 0.55)))
add(sh('black', n=6))
mark['reopen'] = here()
add(sh('v:48017', 0.8, 18, 1.3, 1.25, 1.45, PUPIL, flash_out=8))
mark['end'] = here()
add(sh('end', n=75))
TOTAL = here()

# transitions at cut frames: kind, half-width (frames)
TRANS = [
    ('whip', mark['whip1'], 4),
    ('spin', mark['spin'], 5),
    ('whip', mark['hero3'], 3),
    ('xfade', mark['night'], 3),
]

# ---------------------------------------------------------------- media
_cache = {}      # shot index -> {source frame index: image}
_meta = {}
_img = {}

def video_meta(vid):
    if vid not in _meta:
        cap = cv2.VideoCapture(os.path.join(args.clips, vid + '.mp4'))
        _meta[vid] = (cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    return _meta[vid]

def source_index(shot, i):
    fps, count = video_meta(shot['src'][2:])
    t = shot['t'] + i * shot['sp'] / FPS
    return max(0.0, min(count - 1.0, t * fps))

def shot_frames(idx):
    """decode only the source frames this shot needs (kept for the last few shots)"""
    if idx in _cache:
        return _cache[idx]
    shot = shots[idx]
    vid = shot['src'][2:]
    xs = [source_index(shot, i) for i in range(shot['n'])]
    need = sorted({int(math.floor(x)) for x in xs} | {min(int(math.floor(x)) + 1, video_meta(vid)[1] - 1) for x in xs})
    cap = cv2.VideoCapture(os.path.join(args.clips, vid + '.mp4'))
    cap.set(cv2.CAP_PROP_POS_FRAMES, need[0])
    got = {}
    k = need[0]
    while k <= need[-1]:
        ok, f = cap.read()
        if not ok:
            break
        if k in need:
            got[k] = f
        k += 1
    # pad missing (end of file)
    last = max(got) if got else None
    for n in need:
        if n not in got and last is not None:
            got[n] = got[last]
    _cache[idx] = got
    for old in [k for k in _cache if k < idx - 2]:
        del _cache[old]
    return got

def load_image(nn):
    if nn not in _img:
        _img[nn] = cv2.imread(os.path.join(args.images, nn + '.jpg'))
    return _img[nn]

def src_frame(shot, i, idx):
    """source frame for local frame i (with frame blending for slow motion)"""
    s = shot['src']
    if s.startswith('i:'):
        return load_image(s[2:])
    got = shot_frames(idx)
    x = source_index(shot, i)
    a = int(math.floor(x))
    b = min(a + 1, max(got))
    w = x - a
    fa = got.get(a, got[min(got, key=lambda q: abs(q - a))])
    if w < 0.05 or a == b or b not in got:
        return fa
    return cv2.addWeighted(fa, 1 - w, got[b], w, 0)

def ease(kind, u):
    if kind == 'in':
        return u * u
    if kind == 'expo':
        return (math.pow(2, 8 * u) - 1) / 255
    return u * u * (3 - 2 * u) if kind == 'smooth' else u

def place(img, zoom, c, dx=0.0):
    """cover-fit img into WxH, zoomed around focus c (0..1 of the source)"""
    h, w = img.shape[:2]
    s = max(W / w, H / h) * zoom
    cx, cy = c[0] * w, c[1] * h
    # keep the focus point on screen center as we zoom in, but never show outside the image
    tx = W / 2 - cx * s + dx * W
    ty = H / 2 - cy * s
    tx = min(0, max(W - w * s, tx))
    ty = min(0, max(H - h * s, ty))
    M = np.float32([[s, 0, tx], [0, s, ty]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def radial_blur(img, amount, center=(0.5, 0.5), steps=8):
    acc = np.zeros_like(img, dtype=np.float32)
    cx, cy = center[0] * W, center[1] * H
    for k in range(steps):
        s = 1 + amount * k / steps
        M = np.float32([[s, 0, cx - cx * s], [0, s, cy - cy * s]])
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return (acc / steps).astype(np.uint8)

def spin_blur(img, angle, steps=7):
    acc = np.zeros_like(img, dtype=np.float32)
    for k in range(steps):
        a = angle * (k / steps - 0.5)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), a, 1.15)
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return (acc / steps).astype(np.uint8)

def motion_blur(img, length):
    L = max(1, int(length))
    return cv2.blur(img, (L, 1)) if L > 1 else img

# ---------------------------------------------------------------- look
def make_lut():
    x = np.arange(256) / 255.0
    curve = x + 0.18 * (x - 0.5) * (1 - np.abs(2 * x - 1))  # gentle S
    curve = np.clip(curve, 0, 1)
    # teal shadows, warm highlights (BGR)
    b = np.clip(curve + 0.05 * (1 - x) ** 2 - 0.03 * x ** 2, 0, 1)
    g = np.clip(curve + 0.015 * (1 - x) ** 2, 0, 1)
    r = np.clip(curve - 0.02 * (1 - x) ** 2 + 0.04 * x ** 2, 0, 1)
    return [(c * 255).astype(np.uint8) for c in (b, g, r)]
LUT = make_lut()
YY, XX = np.mgrid[0:H, 0:W]
VIGNETTE = (1 - 0.42 * (((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2) ** 1.2).clip(0.35, 1).astype(np.float32)[..., None]
rng = np.random.default_rng(7)

def grade(img):
    img = cv2.merge([cv2.LUT(ch, l) for ch, l in zip(cv2.split(img), LUT)])
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.14, 0, 255)
    img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return img

def finish(img):
    f = img.astype(np.float32) * VIGNETTE
    f += rng.normal(0, 5.0, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)[:H, :W]
    return np.clip(f, 0, 255).astype(np.uint8)

def sharpen(img):
    blur = cv2.GaussianBlur(img, (0, 0), 1.2 * S)
    return cv2.addWeighted(img, 1.35, blur, -0.35, 0)

# ---------------------------------------------------------------- type
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + '.ttf'), int(size))

def text_layer(lines, size, eyebrow=None, align='left'):
    """RGBA layer with a two-line serif headline; *word* in italic"""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fr, fi = font('serif', size), font('serif-italic', size)
    lh = size * 1.0
    x0 = int((70 if REEL else 110) * S)
    y = H - int((330 if REEL else 150) * S) - lh * len(lines)
    # soft dark scrim behind the words
    sc = Image.new('L', (W, H), 0)
    sd = ImageDraw.Draw(sc)
    sd.rectangle([0, int(y - size * 0.9), int(W * (1 if REEL else 0.62)), H], fill=150)
    sc = sc.filter(ImageFilter.GaussianBlur(int(120 * S)))
    layer.putalpha(sc)
    layer = Image.composite(layer, Image.new('RGBA', (W, H), (0, 0, 0, 0)), sc)
    d = ImageDraw.Draw(layer)
    if eyebrow:
        d.text((x0, y - int(56 * S)), eyebrow.upper(), font=font('mono', 22 * S), fill=(239, 234, 226, 210))
    for line in lines:
        x = x0
        for k, part in enumerate(line.replace('*', '\0*').split('\0')):
            if not part:
                continue
            it = part.startswith('*')
            txt = part.strip('*')
            f = fi if it else fr
            d.text((x, y), txt, font=f, fill=(239, 234, 226, 255))
            x += d.textlength(txt, font=f)
        y += lh
    return layer

def over(img, layer, alpha=1.0, blur=0.0, rise=0.0):
    if alpha <= 0:
        return img
    if blur > 0.3:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(layer, dtype=np.float32)
    if rise:
        M = np.float32([[1, 0, 0], [0, 1, rise]])
        a = cv2.warpAffine(a, M, (W, H))
    rgb = a[..., 2::-1]  # RGBA -> BGR
    al = a[..., 3:4] / 255.0 * alpha
    out = img.astype(np.float32) * (1 - al) + rgb * al
    # soft shadow for legibility
    return np.clip(out, 0, 255).astype(np.uint8)

TEXT = {k: text_layer(T[k], (112 if REEL else 128) * S, eyebrow=T['eye'] if k == 'h1' else None) for k in ('h1', 'h2', 'h3')}
YEAR_FONT = font('mono', 22 * S)

def year_layer(year):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = int((70 if REEL else 110) * S)
    y = int((150 if REEL else 86) * S)
    d.text((x + int(26 * S), y), year, font=font('mono', 40 * S), fill=(239, 234, 226, 240))
    d.ellipse([x, y + int(16 * S), x + int(14 * S), y + int(30 * S)], fill=(255, 90, 36, 255))
    return layer

def end_frame(k, n):
    """wordmark on ink after the white flash"""
    u = k / max(1, n - 1)
    img = np.full((H, W, 3), (12, 11, 11), np.uint8)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    size = int((260 if REEL else 300) * S)
    f = font('sans', size)
    word = 'nemi'
    tw = d.textlength(word, font=f)
    x = (W - tw) / 2
    y = H / 2 - size * 0.62
    d.text((x, y), word, font=f, fill=(239, 234, 226, 255))
    # the dot of the i in signal orange
    bbox = d.textbbox((x, y), 'nem', font=f)
    iw = d.textlength('i', font=f)
    d.ellipse([bbox[2] + iw * 0.18, y + size * 0.1, bbox[2] + iw * 0.18 + size * 0.12, y + size * 0.22], fill=(255, 90, 36, 255))
    f2 = font('serif-italic', (64 if REEL else 72) * S)
    t2 = T['end1']
    d.text(((W - d.textlength(t2, font=f2)) / 2, H / 2 + size * 0.45), t2, font=f2, fill=(239, 234, 226, 230))
    f3 = font('mono', 24 * S)
    d.text(((W - d.textlength(T['url'], font=f3)) / 2, H / 2 + size * 0.45 + 120 * S), T['url'], font=f3, fill=(239, 234, 226, 170))
    a1 = min(1, u / 0.25)
    blur = (1 - a1) * 18
    return over(img, layer, a1, blur)

# ---------------------------------------------------------------- render
def shot_at(frame):
    acc = 0
    for idx, s in enumerate(shots):
        if frame < acc + s['n']:
            return idx, frame - acc
        acc += s['n']
    return len(shots) - 1, shots[-1]['n'] - 1

def render_shot_frame(idx, i):
    s = shots[idx]
    n = s['n']
    u = i / max(1, n - 1)
    if s['src'] == 'black':
        return np.zeros((H, W, 3), np.uint8)
    if s['src'] == 'end':
        return end_frame(i, n)
    z = s['z0'] + (s['z1'] - s['z0']) * ease(s.get('ease', 'lin'), u)
    img = place(src_frame(s, i, idx), z, s['c'], s.get('dx', 0))
    img = sharpen(img)
    img = grade(img)
    if s.get('radial'):
        img = radial_blur(img, s['radial'] * u, s['c'] if False else (0.5, 0.5))
    if s.get('fadein') and i < s['fadein']:
        img = (img.astype(np.float32) * (i / s['fadein'])).astype(np.uint8)
    if s.get('flash_out') and i >= n - s['flash_out']:
        k = (i - (n - s['flash_out'])) / s['flash_out']
        bloom = cv2.GaussianBlur(img, (0, 0), 30 * S)
        img = cv2.addWeighted(img, 1, bloom, 0.8 * k, 0)
        img = (img.astype(np.float32) * (1 - k) + 255 * k).clip(0, 255).astype(np.uint8)
    return img

def letterbox_amount(frame):
    """0..1 how far the 2.39:1 bars are in"""
    best = 0.0
    acc = 0
    for s in shots:
        if s.get('letterbox'):
            a, b = acc, acc + s['n']
            if a - 6 <= frame <= b:
                best = max(best, min(1, (frame - (a - 6)) / 8), 0)
                if frame > b - 4:
                    best = min(best, max(0, (b - frame) / 4))
        acc += s['n']
    return best

def text_state(frame):
    acc = 0
    for s in shots:
        if s.get('text'):
            a, b = acc, acc + s['n']
            if a <= frame < b:
                k = frame - a
                ain = min(1, max(0, (k - 8) / 14))
                aout = min(1, max(0, (b - 5 - frame) / 5))
                return s['text'], min(ain, aout), (1 - ain) * 14 * S, (1 - ain) * 16 * S
        acc += s['n']
    return None, 0, 0, 0

def year_at(frame):
    acc = 0
    for s in shots:
        if acc <= frame < acc + s['n'] and s.get('year'):
            return s['year']
        acc += s['n']
    return None

def frame_image(f):
    idx, i = shot_at(f)
    img = render_shot_frame(idx, i)
    # transitions around cuts
    for kind, at, hw in TRANS:
        d = f - at
        if -hw <= d < hw:
            p = 1 - abs(d + 0.5) / hw  # 0 at edges, 1 at the cut
            if kind == 'whip':
                shift = int((d + 0.5) / hw * W * 0.18)
                M = np.float32([[1, 0, -shift], [0, 1, 0]])
                img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
                img = motion_blur(img, 260 * S * p)
            elif kind == 'spin':
                ang = (d + 0.5) / hw * 35
                M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, 1.12)
                img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
                img = spin_blur(img, 40 * p)
            elif kind == 'xfade' and d < 0:
                j = shot_at(at)
                other = render_shot_frame(*j)
                img = cv2.addWeighted(img, 1 - (d + hw) / (2 * hw), other, (d + hw) / (2 * hw), 0)
    # type and HUD
    key, a, blur, rise = text_state(f)
    yr = year_at(f)
    if f < mark['end']:
        img = finish(img)
    if yr:
        img = over(img, year_layer(yr), 0.95)
    if key:
        img = over(img, TEXT[key], a, blur, rise)
    lb = 0 if REEL else letterbox_amount(f)
    if lb > 0:
        bar = int((H - W / 2.39) / 2 * lb)
        img[:bar] = 0
        img[H - bar:] = 0
    return img

def main():
    print('frames', TOTAL, 'seconds', round(TOTAL / FPS, 2), 'marks', mark, file=sys.stderr)
    if args.preview:
        os.makedirs(args.out, exist_ok=True)
        for f in range(0, TOTAL, args.preview):
            cv2.imwrite(os.path.join(args.out, f'p_{f:04d}.jpg'), cv2.resize(frame_image(f), (360, 640) if REEL else (640, 360)), [cv2.IMWRITE_JPEG_QUALITY, 80])
        return
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
    if args.music:
        dur = TOTAL / FPS
        cmd += ['-ss', str(args.music_at), '-t', f'{dur:.3f}', '-i', args.music,
                '-af', f'afade=t=in:d=0.6,afade=t=out:st={dur - 1.8:.3f}:d=1.8', '-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', args.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(TOTAL):
        p.stdin.write(frame_image(f).tobytes())
        if f % 60 == 0:
            print('frame', f, file=sys.stderr)
    p.stdin.close()
    p.wait()

main()
