#!/usr/bin/env python3
"""Nemi Studio intro film v3: a story told in traces, cut in the grammar of the reference reel (r8).

The eye opens -> the pupil widens -> dive -> fire ("Seit es Menschen gibt,") -> the drop: footprints
("hinterlassen wir Spuren.") -> a hand on a cave wall -> a sign in stone -> a name on paper -> a voice
on the radio -> a face on a screen -> a burst through every era ("Immer mit demselben Wunsch:") ->
"Gesehen zu werden." -> today ("Heute ist deine Spur deine Website.") -> night city ("Die meisten
Websites schweigen.") -> the eye closes -> "Hinterlass eine, die bleibt." -> nemi.

Each line of the story has its own type animation (blur, slam, mask, chisel, typewriter, radio wave,
glitch, tracking, dissolve) and lands on the beat of the music.

    python3 tools/intro_film.py <clips-dir> <images-dir> <out.mp4> [--format web|reel] [--lang de|en]
                                [--preview N] [--width 1920] [--music path] [--music-at 20.0]

clips-dir:  Mixkit clips named <id>.mp4 (1080p where available)
images-dir: stills named hands, cave, hiero, statue, greek, papyrus, type, ship, street, radio, tv, fire (.jpg)
"""
import argparse
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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
ap.add_argument('--frames', default='', help='preview only these frames, comma separated')
ap.add_argument('--width', type=int, default=1920)
ap.add_argument('--music', default='')
ap.add_argument('--music-at', type=float, default=20.0, help='track time that plays at film time 0')
ap.add_argument('--crf', type=int, default=18)
ap.add_argument('--sr', default='', help='folder with AI-upscaled versions of some clips (used first)')
args = ap.parse_args()

REEL = args.format == 'reel'
W = 1080 * args.width // 1920 if REEL else args.width
H = round(W * 16 / 9) if REEL else round(W * 9 / 16)
S = W / (1080 if REEL else 1920)  # pixel sizes are designed at 1920 (web) / 1080 (reel)
BEAT = 60 / 130 * FPS             # 13.85 frames

# ---------------------------------------------------------------- the story
# '|' groups words that land together (slam / flash); '*word*' is italic; '/' breaks the line
T = {
    'de': {
        'l1': 'Seit es Menschen gibt,',
        'l2': 'hinterlassen|wir|*Spuren*.',
        'l3': 'Eine Hand an der Höhlenwand.',
        'l4': 'Ein Zeichen in Stein.',
        'l5': 'Ein Name auf Papier.',
        'l6': 'Eine Stimme im Radio.',
        'l7': 'Ein Gesicht auf dem Bildschirm.',
        'l8': 'Immer|mit|demselben|Wunsch:',
        'l9': 'Gesehen zu *werden*.',
        'l10': 'Heute ist deine Spur/deine *Website*.',
        'l11': 'Die meisten Websites *schweigen*.',
        'l12': 'Hinterlass eine, die *bleibt*.',
        'url': 'NEMISTUDIO.AT',
    },
    'en': {
        'l1': 'Ever since there have been people,',
        'l2': 'we have|left|*traces*.',
        'l3': 'A hand on a cave wall.',
        'l4': 'A sign in stone.',
        'l5': 'A name on paper.',
        'l6': 'A voice on the radio.',
        'l7': 'A face on a screen.',
        'l8': 'Always|with the|same|wish:',
        'l9': 'To be *seen*.',
        'l10': 'Today your trace/is your *website*.',
        'l11': 'Most websites stay *silent*.',
        'l12': 'Leave one that *lasts*.',
        'url': 'NEMISTUDIO.AT',
    },
}[args.lang]

# ---------------------------------------------------------------- shots
# src: 'v:<id>' video, 'i:<name>' still, 'black', 'end'
# t: source start (s), n: frames, sp: playback speed (negative = reverse), z0/z1: zoom, c: focus (0..1),
# rc: focus for the 9:16 crop when the subject sits off-centre
def sh(src, t=0.0, n=2, sp=1.0, z0=1.0, z1=None, c=(0.5, 0.5), **kw):
    d = dict(src=src, t=t, n=n, sp=sp, z0=z0, z1=z0 * 1.05 if z1 is None else z1, c=c)
    d.update(kw)
    return d

PUPIL = (0.44, 0.59)
shots = []
mark = {}
cues = []      # text cues: dict(key, a, b, fx, pos, size, ...)
years = []     # (a, b, label)

def add(*ss):
    for s in ss:
        shots.append(s)

def here():
    return sum(s['n'] for s in shots)

def flashes(items):
    """2-3 frame flash cuts: (src, t, n)"""
    for src, t, n in items:
        add(sh(src, t, n, 1.0, 1.08, 1.14))

# A) the eye opens, no pause: the pupil widens at once and we dive in
mark['eye'] = here()
add(sh('v:48017', 0.95, 10, 1.0, 1.0, 1.06, PUPIL, fadein=4, era=1.0))
add(sh('v:48017', 3.4, 12, -2.6, 1.06, 1.9, PUPIL, ease='in', era=1.0))
add(sh('v:48017', 1.6, 10, 0.0, 1.9, 22.0, PUPIL, ease='expo', radial=0.35, era=1.0, burn=True))
add(sh('black', n=2))
# B) fire: since there have been people
mark['fire'] = here()
add(sh('v:52312', 2.0, 52, 0.6, 1.1, 1.22, (0.5, 0.5), fadein=10))
add(sh('v:3463', 1.0, 26, 0.7, 1.0, 1.08))
add(sh('v:45676', 3.0, 26, 0.8, 1.1, 1.2))
cues.append(dict(key='l1', a=mark['fire'] + 10, b=here() - 2, fx='blur', pos='c'))
# C) the drop: footprints in the sand
mark['drop'] = here()
add(sh('v:1013', 1.0, 50, 0.8, 1.05, 1.16, (0.5, 0.62), flash_in=4))
cues.append(dict(key='l2', a=mark['drop'], b=here() - 1, fx='slam', pos='c'))
# D) a hand on a cave wall
mark['hand'] = here()
flashes([('i:cave', 0, 3), ('v:52312', 6, 2), ('i:hands', 0, 2), ('i:cave', 0, 2)])
add(sh('i:hands', 0, 47, 1.0, 1.04, 1.16, (0.55, 0.5), rc=(0.68, 0.55)))
cues.append(dict(key='l3', a=mark['hand'] + 8, b=here() - 2, fx='mask', pos='bl'))
years.append((mark['hand'], here(), '−40.000'))
# E) a sign in stone
mark['stone'] = here()
flashes([('i:greek', 0, 2), ('i:papyrus', 0, 2), ('i:statue', 0, 2), ('i:cave', 0, 2)])
add(sh('i:hiero', 0, 48, 1.0, 1.05, 1.2, (0.5, 0.45)))
cues.append(dict(key='l4', a=mark['stone'] + 8, b=here() - 2, fx='chisel', pos='bl'))
years.append((mark['stone'], here(), '−3.200'))
# F) a name on paper
mark['paper'] = here()
flashes([('i:type', 0, 2), ('v:49557', 3, 2), ('i:papyrus', 0, 2), ('v:50700', 4, 2)])
add(sh('v:50705', 1.0, 51, 0.9, 1.04, 1.12, (0.5, 0.5)))
cues.append(dict(key='l5', a=mark['paper'] + 8, b=here() - 2, fx='type', pos='bl'))
years.append((mark['paper'], here(), '1450'))
# G) a voice on the radio (second phrase of the music)
mark['radio'] = here()
flashes([('i:radio', 0, 2), ('v:43370', 4, 2), ('v:48533', 3, 2)])
add(sh('v:31957', 2.0, 50, 0.8, 1.05, 1.14, (0.5, 0.5)))
cues.append(dict(key='l6', a=mark['radio'] + 6, b=here() - 2, fx='wave', pos='bl'))
years.append((mark['radio'], here(), '1925'))
# H) a face on a screen
mark['screen'] = here()
flashes([('v:4143', 2, 2), ('i:tv', 0, 2), ('v:46291', 3, 2), ('i:street', 0, 2)])
add(sh('v:47911', 2.0, 47, 0.8, 1.04, 1.14, (0.45, 0.5), rc=(0.2, 0.5)))
cues.append(dict(key='l7', a=mark['screen'] + 8, b=here() - 2, fx='glitch', pos='bl'))
years.append((mark['screen'], here(), '1955'))
# I) every era at once: always with the same wish
mark['burst'] = here()
B = [('i:fire', 0), ('i:hands', 0), ('v:1013', 2), ('i:cave', 0), ('i:hiero', 0), ('i:statue', 0), ('i:greek', 0),
     ('i:papyrus', 0), ('v:50700', 2), ('i:type', 0), ('v:49557', 5), ('i:ship', 0), ('v:18288', 2), ('i:street', 0),
     ('v:43370', 6), ('i:radio', 0), ('v:31957', 4), ('v:48533', 5), ('i:tv', 0), ('v:4143', 4), ('v:46291', 1),
     ('v:47911', 4), ('v:33490', 2), ('v:52285', 2), ('v:3463', 3), ('v:50705', 3), ('i:hands', 0), ('v:45676', 6),
     ('i:hiero', 0), ('v:41858', 3), ('v:242', 2), ('v:4915', 3), ('v:52088', 5), ('v:23222', 22), ('v:4196', 4),
     ('v:43222', 3), ('v:47555', 6), ('v:4982', 2), ('v:39500', 4), ('v:33328', 2), ('v:5015', 4), ('v:22240', 3),
     ('v:46635', 4)]
LENS = [2] * 36 + [3, 3, 4, 4, 5, 6, 14]
YEARS = ['−40.000', '−32.000', '−17.000', '−12.000', '−3.200', '−480', '−400', '−100', '800', '1200', '1450', '1492',
         '1569', '1650', '1700', '1810', '1876', '1902', '1920', '1925', '1937', '1955', '1962', '1971', '1979', '1984',
         '1991', '1995', '1998', '2001', '2004', '2007', '2010', '2012', '2014', '2016', '2018', '2020', '2022', '2024',
         '2025', '2026', '2026']
acc = here()
for (src, t), n, y in zip(B, LENS, YEARS):
    add(sh(src, t, n, 1.0, 1.08, 1.14))
    years.append((acc, acc + n, y))
    acc += n
cues.append(dict(key='l8', a=mark['burst'] + 2, b=here() - 1, fx='flash', pos='c'))
# J) to be seen (third phrase)
mark['seen'] = here()
add(sh('v:46635', 2.0, 99, 0.55, 1.05, 1.16, (0.62, 0.42), letterbox=True))
cues.append(dict(key='l9', a=mark['seen'] + 6, b=here() - 3, fx='track', pos='bl', size=1.2))
# K) today: industries, then hands on a laptop
mark['today'] = here()
B2 = [('v:41858', 3.0), ('v:4982', 2.0), ('v:47555', 6.0), ('v:43222', 3.0), ('v:33328', 2.0), ('v:39500', 4.0),
      ('v:52088', 6.0), ('v:23222', 22.0), ('v:22240', 4.0), ('v:4196', 6.0), ('v:5015', 6.0), ('v:41858', 8.5),
      ('v:4915', 2.0), ('v:52088', 2.0), ('v:39500', 10.0), ('v:4196', 2.0), ('v:43222', 8.0)]
LEN2 = [2] * 14 + [3, 4, 5]
for (src, t), n in zip(B2, LEN2):
    add(sh(src, t, n, 1.0, 1.05, 1.1))
mark['web'] = here()
add(sh('v:242', 3.0, 82, 0.7, 1.04, 1.12, (0.5, 0.5)))
cues.append(dict(key='l10', a=mark['web'] + 4, b=here() - 3, fx='mask', pos='bl', accent=True))
# L) most websites stay silent (fourth phrase)
mark['night'] = here()
add(sh('v:49845', 12.0, 60, 1.0, 1.02, 1.12, (0.5, 0.5), letterbox=True))
cues.append(dict(key='l11', a=mark['night'] + 4, b=here() - 1, fx='dissolve', pos='bl'))
# M) the eye closes
mark['blink'] = here()
add(sh('v:4257', 3.85, 18, 0.8, 1.12, 1.24, (0.5, 0.55)))
add(sh('black', n=4))
# N) leave one that lasts -> nemi
mark['end'] = here()
add(sh('end', n=106))
TOTAL = here()

# how old the picture looks: 0 = oldest film, 1 = today. The look ages back after the dive into the
# pupil and grows up again era by era until "Gesehen zu werden".
ERA = [('fire', 0.6), ('drop', 0.5), ('hand', 0.18), ('stone', 0.22), ('paper', 0.3), ('radio', 0.45),
       ('screen', 0.65), ('burst', None), ('seen', 1.0), ('today', 1.0), ('web', 1.0), ('night', 1.0), ('blink', 1.0)]
def assign_eras():
    order = sorted(ERA, key=lambda e: mark[e[0]])
    acc = 0
    for s in shots:
        if 'era' not in s:
            cur = None
            for name, val in order:
                if acc >= mark[name]:
                    cur = (name, val)
            if cur and cur[1] is None:  # the burst: ramp from the 1950s to today
                u = (acc - mark['burst']) / (mark['seen'] - mark['burst'])
                s['era'] = 0.55 + 0.45 * u ** 1.4
            else:
                s['era'] = cur[1] if cur else 1.0
        acc += s['n']
assign_eras()

TRANS = [
    ('whip', mark['today'], 4),
    ('xfade', mark['night'], 3),
]
DROPS = [mark['drop'], mark['radio'], mark['seen'], mark['night']]  # light bump on the big beats

# ---------------------------------------------------------------- media
_cache = {}
_meta = {}
_img = {}

def clip_path(vid):
    if args.sr and os.path.exists(os.path.join(args.sr, vid + '.mp4')):
        return os.path.join(args.sr, vid + '.mp4')
    return os.path.join(args.clips, vid + '.mp4')

def video_meta(vid):
    if vid not in _meta:
        cap = cv2.VideoCapture(clip_path(vid))
        _meta[vid] = (cap.get(cv2.CAP_PROP_FPS) or 25, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    return _meta[vid]

def source_index(shot, i):
    fps, count = video_meta(shot['src'][2:])
    t = shot['t'] + i * shot['sp'] / FPS
    return max(0.0, min(count - 1.0, t * fps))

def shot_frames(idx):
    if idx in _cache:
        return _cache[idx]
    shot = shots[idx]
    vid = shot['src'][2:]
    xs = [source_index(shot, i) for i in range(shot['n'])]
    count = video_meta(vid)[1]
    need = sorted({int(math.floor(x)) for x in xs} | {min(int(math.floor(x)) + 1, count - 1) for x in xs})
    cap = cv2.VideoCapture(clip_path(vid))
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
    last = max(got) if got else None
    for n in need:
        if n not in got and last is not None:
            got[n] = got[last]
    _cache[idx] = got
    for old in [k for k in _cache if k < idx - 3]:
        del _cache[old]
    return got

def load_image(name):
    if name not in _img:
        _img[name] = cv2.imread(os.path.join(args.images, name + '.jpg'))
    return _img[name]

def src_frame(shot, i, idx):
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

def place(img, zoom, c):
    h, w = img.shape[:2]
    s = max(W / w, H / h) * zoom
    tx = W / 2 - c[0] * w * s
    ty = H / 2 - c[1] * h * s
    tx = min(0, max(W - w * s, tx))
    ty = min(0, max(H - h * s, ty))
    M = np.float32([[s, 0, tx], [0, s, ty]])
    # Lanczos when enlarging keeps 720p sources crisper
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4 if s > 1 else cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)

def radial_blur(img, amount, steps=8):
    acc = np.zeros_like(img, dtype=np.float32)
    cx, cy = W / 2, H / 2
    for k in range(steps):
        s = 1 + amount * k / steps
        M = np.float32([[s, 0, cx - cx * s], [0, s, cy - cy * s]])
        acc += cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return (acc / steps).astype(np.uint8)

def motion_blur(img, length):
    L = max(1, int(length))
    return cv2.blur(img, (L, 1)) if L > 1 else img

# ---------------------------------------------------------------- look (retro, but sharp)
def make_lut():
    x = np.arange(256) / 255.0
    curve = np.clip(x + 0.16 * (x - 0.5) * (1 - np.abs(2 * x - 1)), 0, 1)
    b = np.clip(curve + 0.05 * (1 - x) ** 2 - 0.03 * x ** 2, 0, 1)
    g = np.clip(curve + 0.015 * (1 - x) ** 2, 0, 1)
    r = np.clip(curve - 0.02 * (1 - x) ** 2 + 0.04 * x ** 2, 0, 1)
    return [(c * 255).astype(np.uint8) for c in (b, g, r)]
LUT = make_lut()
YY, XX = np.mgrid[0:H, 0:W]
VIGNETTE = (1 - 0.36 * (((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2) ** 1.25).clip(0.4, 1).astype(np.float32)[..., None]
rng = np.random.default_rng(7)

def grade(img):
    img = cv2.merge([cv2.LUT(ch, l) for ch, l in zip(cv2.split(img), LUT)])
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.12, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def sharpen(img):
    # two-band unsharp mask: fine detail + local contrast
    b1 = cv2.GaussianBlur(img, (0, 0), 0.9 * S)
    img = cv2.addWeighted(img, 1.7, b1, -0.7, 0)
    b2 = cv2.GaussianBlur(img, (0, 0), 6 * S)
    return cv2.addWeighted(img, 1.18, b2, -0.18, 0)

SEPIA = np.array([0.72, 0.93, 1.12], np.float32)  # BGR tint of old print stock (keeps brightness)

def vintage(img, era, f):
    """old film by degree: sepia/faded colour, lifted blacks, flicker, weave, scratches, dust"""
    v = 1.0 - era
    if v <= 0.02:
        return img
    r = np.random.default_rng(f * 7919 + 13)
    x = img.astype(np.float32)
    lum = x @ np.array([0.114, 0.587, 0.299], np.float32)
    sep = lum[..., None] * SEPIA
    k = min(1.0, v * 0.95)
    x = x * (1 - k) + sep * k
    # faded print: lifted blacks, softer whites
    x = x * (1 - 0.07 * v) + 12 * v
    # flicker
    x *= 1 + (r.random() - 0.5) * 0.09 * v
    # gate weave
    dx, dy = r.normal(0, 1.6 * v * S), r.normal(0, 1.2 * v * S)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    x = cv2.warpAffine(x, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    # scratches: thin vertical lines that live a few frames
    for _ in range(r.poisson(1.6 * v)):
        sx = int(r.uniform(0.05, 0.95) * W)
        y0, y1 = int(r.uniform(0, 0.4) * H), int(r.uniform(0.6, 1.0) * H)
        val = 255 if r.random() < 0.6 else 20
        cv2.line(x, (sx, y0), (sx + int(r.normal(0, 3)), y1), (val, val, val), max(1, int(1.2 * S)))
    # dust
    for _ in range(r.poisson(6 * v)):
        cx, cy = int(r.uniform(0, W)), int(r.uniform(0, H))
        rad = max(1, int(r.uniform(1, 4) * S))
        val = 15 if r.random() < 0.7 else 240
        cv2.circle(x, (cx, cy), rad, (val, val, val), -1)
    return np.clip(x, 0, 255).astype(np.uint8)

def halation(img, amount=0.22):
    """red glow around highlights, like light bouncing in film emulsion"""
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA).astype(np.float32)
    hi = np.clip(small.max(axis=2) - 185, 0, 70) / 70
    glow = cv2.GaussianBlur(hi, (0, 0), 6)
    glow = cv2.resize(glow, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    tint = np.array([20, 70, 255], np.float32)
    return np.clip(img.astype(np.float32) + glow * tint * amount, 0, 255).astype(np.uint8)

def burn(img, k):
    """warm film burn that blows out from the centre (the dive into the past)"""
    g = np.exp(-(((XX - W * 0.5) / (W * 0.35)) ** 2 + ((YY - H * 0.55) / (H * 0.4)) ** 2)).astype(np.float32)[..., None]
    col = np.array([60, 150, 255], np.float32)
    return np.clip(img.astype(np.float32) + g * col * k * 1.6 + 255 * max(0, k - 0.6) * 1.5, 0, 255).astype(np.uint8)

def finish(img, era=1.0):
    v = 1.0 - era
    f = img.astype(np.float32) * (VIGNETTE ** (1 + 0.35 * v))
    g = 2.4 + 2.4 * v
    c = 2 if v < 0.5 else 3  # older stock has coarser grain
    f += rng.normal(0, g, (H // c + 1, W // c + 1, 1)).repeat(c, 0).repeat(c, 1)[:H, :W]
    return np.clip(f, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- kinetic type
BONE = np.array([226, 234, 239], np.float32)    # BGR
SIGNAL = np.array([36, 90, 255], np.float32)
_fonts = {}

def font(name, size):
    k = (name, int(size))
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(os.path.join(FONTS, name + '.ttf'), int(size))
    return _fonts[k]

class Glyph:
    __slots__ = ('ch', 'x', 'y', 'w', 'patch', 'ox', 'oy', 'word', 'line', 'idx', 'accent', 'cache')

def glyph_patch(ch, f):
    """white glyph on transparent, with padding; returns (alpha float32, ox, oy) relative to the pen position"""
    pad = int(f.size * 0.35)
    l, t, r, b = f.getbbox(ch)
    w, h = max(1, r - l) + 2 * pad, max(1, b - t) + 2 * pad
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).text((pad - l, pad - t), ch, font=f, fill=255)
    return np.asarray(im, np.float32) / 255.0, l - pad, t - pad

def wrap(text, base, pos):
    """split on '/' and break any line that is wider than the frame at word (or '|') boundaries"""
    limit = (W * 0.88 if pos == 'c' else W - 2 * (70 if REEL else 110) * S) * 0.97
    f = font('serif', base)
    out = []
    for line in text.split('/'):
        tokens = [t for t in __import__('re').split(r'([ |])', line) if t != '']
        cur = ''
        for tok in tokens:
            trial = cur + tok
            if cur.strip() and tok.strip(' |') and f.getlength(trial.replace('*', '').replace('|', ' ')) * 1.04 > limit:
                out.append(cur.rstrip(' '))
                cur = tok.lstrip(' ')
            else:
                cur = trial
        out.append(cur)
    return [l for l in out if l.strip(' |')]

def layout(cue):
    """glyphs with pen positions for a cue; lines split on '/', italic on *...*, word groups on '|'"""
    text = T[cue['key']]
    base = (118 if REEL else 136) * S * cue.get('size', 1.0)
    if cue['pos'] == 'c':
        base *= 1.12
    lines = wrap(text, base, cue['pos'])
    glyphs = []
    word = 0
    lh = base * 1.02
    total_h = lh * len(lines)
    # measure widths
    widths = []
    for line in lines:
        x = 0.0
        for part in line.replace('*', '\0*').split('\0'):
            it = part.startswith('*')
            txt = part.strip('*').replace('|', ' ')
            x += font('serif-italic' if it else 'serif', base).getlength(txt)
        widths.append(x)
    maxw = max(widths)
    # y0 is the top of the first line ('la' anchor: pen at the ascender)
    if cue['pos'] == 'c':
        y0 = H / 2 - total_h / 2 - base * 0.08
    else:
        y0 = H - (330 if REEL else 150) * S - total_h
    x_left = (70 if REEL else 110) * S
    idx = 0
    for li, line in enumerate(lines):
        x = (W - widths[li]) / 2 if cue['pos'] == 'c' else x_left
        y = y0 + li * lh
        for part in line.replace('*', '\0*').split('\0'):
            if not part:
                continue
            it = part.startswith('*')
            f = font('serif-italic' if it else 'serif', base)
            txt = part.strip('*')
            for ch in txt:
                if ch == '|':
                    word += 1
                    ch = ' '
                elif ch == ' ' and cue['fx'] not in ('slam', 'flash'):
                    word += 1
                g = Glyph()
                g.ch, g.x, g.y, g.word, g.line, g.idx = ch, x, y, word, li, idx
                g.accent = it and cue.get('accent', False)
                adv = f.getlength(ch)
                g.w = adv
                if ch.strip():
                    g.patch, g.ox, g.oy = glyph_patch(ch, f)
                else:
                    g.patch = None
                g.cache = {}
                glyphs.append(g)
                x += adv
                idx += 1
        word += 1
    cue['glyphs'] = glyphs
    cue['nwords'] = word
    cue['bbox'] = (min(g.x for g in glyphs), y0 + base * 0.2, max(g.x + g.w for g in glyphs), y0 + total_h)
    cue['base'] = base
    # soft scrim behind the words
    m = np.zeros((H, W), np.float32)
    x0, y0b, x1, y1 = cue['bbox']
    padx, pady = base * 1.2, base * 0.9
    cv2.rectangle(m, (int(x0 - padx), int(y0b - pady)), (int(x1 + padx), int(y1 + pady)), 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), base * 0.9)
    cue['scrim'] = m[..., None]

for c in cues:
    layout(c)

def smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)

def out_expo(u):
    u = min(1.0, max(0.0, u))
    return 1 - math.pow(2, -10 * u) if u < 1 else 1.0

def glyph_state(cue, g, t, n):
    """alpha, dx, dy, scale, blur, flash for glyph g at local frame t of n"""
    fx = cue['fx']
    a, dx, dy, sc, bl, fl = 1.0, 0.0, 0.0, 1.0, 0.0, 0.0
    base = cue['base']
    if fx == 'blur':
        u = smooth((t - g.idx * 1.1) / 12)
        a, bl, dy = u, (1 - u) * 14 * S, (1 - u) * base * 0.18
    elif fx == 'slam':
        k = t - g.word * BEAT
        u = out_expo(k / 6)
        a = 1.0 if k >= 0 else 0.0
        sc = 1 + (1 - u) * 0.55
        bl = (1 - u) * 10 * S
    elif fx == 'flash':
        k = t - g.word * BEAT
        a = 1.0 if k >= 0 else 0.0
        sc = 1 + (1 - out_expo(k / 4)) * 0.3
        fl = max(0.0, 1 - k / 5) if k >= 0 else 0.0
    elif fx == 'mask':
        u = out_expo((t - g.line * 5 - g.word * 0.6) / 16)
        a = 1.0 if u > 0.001 else 0.0
        dy = (1 - u) * base * 1.05
    elif fx == 'chisel':
        k = t - g.idx * 1.4
        a = 1.0 if k >= 0 else 0.0
        u = out_expo(k / 5)
        sc = 1 + (1 - u) * 0.35
        fl = max(0.0, 1 - k / 6) if k >= 0 else 0.0
        if 0 <= k < 4:
            r = np.random.default_rng(g.idx * 31 + int(k))
            dx, dy = r.normal(0, 3 * S), r.normal(0, 3 * S)
    elif fx == 'type':
        a = 1.0 if t >= g.idx * 1.25 else 0.0
    elif fx == 'wave':
        u = smooth((t - g.idx * 0.7) / 8)
        a = u
        dy = math.sin(t * 0.55 + g.idx * 0.75) * base * 0.16 * math.exp(-max(0, t - g.idx * 0.7) / 18)
    elif fx == 'glitch':
        u = smooth((t - g.idx * 0.5) / 6)
        a = u * (0.35 if (t < 16 and (t * 7 + g.idx) % 5 == 0) else 1.0)
        if t < 14:
            r = np.random.default_rng(int(t) * 97 + g.line)
            dx = r.normal(0, 14 * S) * (1 - t / 14)
    elif fx == 'track':
        u = out_expo(t / 34)
        a = smooth(t / 10)
        # letters drift together from wide tracking
        dx = (1 - u) * (g.idx - len(cue['glyphs']) / 2) * base * 0.14
        bl = (1 - u) * 12 * S
    elif fx == 'dissolve':
        u = smooth((t - g.idx * 0.9) / 10)
        a, bl, dy = u, (1 - u) * 10 * S, (1 - u) * base * 0.15
        # the last word falls silent before the cut
        last = cue['nwords'] - 1
        if g.word >= last - 0 and n - t < 22:
            r = np.random.default_rng(g.idx)
            k = smooth((22 - (n - t) - r.uniform(0, 8)) / 10)
            a *= 1 - k
            bl += k * 16 * S
            dy -= k * base * 0.25
    # exit for everything: up and out of focus in the last frames
    if fx != 'dissolve' and n - t < 6:
        k = smooth((6 - (n - t)) / 6)
        a *= 1 - k
        bl += k * 10 * S
        dy -= k * base * 0.2
    return a, dx, dy, sc, bl, fl

def draw_glyph(img, g, a, dx, dy, sc, bl, fl, color, shift=None):
    if g.patch is None or a <= 0.01:
        return
    key = (round(sc, 2), int(bl))
    p = g.cache.get(key)
    if p is None:
        p = g.patch
        if abs(sc - 1) > 0.005:
            p = cv2.resize(p, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
        if bl >= 1:
            pad = int(bl * 2)
            p = cv2.copyMakeBorder(p, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
            p = cv2.GaussianBlur(p, (0, 0), bl)
        g.cache[key] = p
    ph, pw = p.shape
    # scale around the glyph centre
    cx = g.x + g.ox + g.patch.shape[1] / 2 + dx
    cy = g.y + g.oy + g.patch.shape[0] / 2 + dy
    x0 = int(round(cx - pw / 2))
    y0 = int(round(cy - ph / 2))
    x1, y1 = x0 + pw, y0 + ph
    if x1 <= 0 or y1 <= 0 or x0 >= W or y0 >= H:
        return
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x0c, y0c = max(0, x0), max(0, y0)
    x1c, y1c = min(W, x1), min(H, y1)
    al = p[sy0:sy0 + (y1c - y0c), sx0:sx0 + (x1c - x0c)][..., None] * a
    col = color * (1 - fl) + 255 * fl
    reg = img[y0c:y1c, x0c:x1c].astype(np.float32)
    if shift is None:
        img[y0c:y1c, x0c:x1c] = (reg * (1 - al) + col * al).astype(np.uint8)
    else:  # one colour channel only (chromatic split)
        ch = shift
        reg[..., ch] = reg[..., ch] * (1 - al[..., 0]) + col[ch] * al[..., 0]
        img[y0c:y1c, x0c:x1c] = reg.astype(np.uint8)

def render_cue(img, cue, f):
    t = f - cue['a']
    n = cue['b'] - cue['a']
    if t < 0 or t > n:
        return img
    # scrim
    fade = smooth(t / 8) * (1 - smooth((t - (n - 6)) / 6))
    img = (img.astype(np.float32) * (1 - 0.5 * cue['scrim'] * fade)).astype(np.uint8)
    states = [(g, glyph_state(cue, g, t, n)) for g in cue['glyphs']]
    for g, (a, dx, dy, sc, bl, fl) in states:
        color = SIGNAL if g.accent else BONE
        if cue['fx'] == 'glitch' and t < 18:
            k = (1 - t / 18) * 10 * S
            draw_glyph(img, g, a * 0.9, dx - k, dy, sc, bl, fl, color, shift=2)
            draw_glyph(img, g, a * 0.9, dx + k, dy, sc, bl, fl, color, shift=0)
        draw_glyph(img, g, a, dx, dy, sc, bl, fl, color)
    if cue['fx'] == 'type':
        vis = [g for g, s in states if s[0] > 0.5]
        if vis and (t // 8) % 2 == 0 and n - t > 6:
            last = vis[-1]
            x = int(last.x + last.w + 6 * S)
            b = cue['base']
            cv2.rectangle(img, (x, int(last.y + b * 0.28)), (x + max(2, int(4 * S)), int(last.y + b * 1.02)), (226, 234, 239), -1)
    return img

def year_layer(img, label):
    x = int((70 if REEL else 110) * S)
    y = int((150 if REEL else 86) * S)
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    d.text((x + int(28 * S), y), label, font=font('mono', 38 * S), fill=(239, 234, 226))
    d.ellipse([x, y + int(15 * S), x + int(14 * S), y + int(29 * S)], fill=(255, 90, 36))
    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)

# ---------------------------------------------------------------- end card
END_LINE = dict(key='l12', a=0, b=0, fx='blur', pos='c')
layout(END_LINE)

def end_frame(k, n):
    img = np.full((H, W, 3), (11, 11, 12), np.uint8)
    # phase 1: the last line of the story
    if k < 52:
        END_LINE['a'], END_LINE['b'] = 0, 52
        return render_cue(img, END_LINE, k)
    # phase 2: the wordmark
    u = (k - 52) / (n - 52)
    a1 = smooth(u / 0.35)
    pil = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(pil)
    size = int((260 if REEL else 300) * S)
    f = font('sans', size)
    word = 'nemi'
    tw = d.textlength(word, font=f)
    x = (W - tw) / 2
    y = H / 2 - size * 0.62
    d.text((x, y), word, font=f, fill=(239, 234, 226, 255))
    bbox = d.textbbox((x, y), 'nem', font=f)
    iw = d.textlength('i', font=f)
    dot = min(1, max(0, (u - 0.2) / 0.15))
    if dot > 0:
        r = size * 0.06 * (1 + 0.6 * (1 - dot))
        cx, cy = bbox[2] + iw * 0.18 + size * 0.06, y + size * 0.16
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 90, 36, int(255 * dot)))
    f3 = font('mono', 24 * S)
    d.text(((W - d.textlength(T['url'], font=f3)) / 2, H / 2 + size * 0.5), T['url'], font=f3, fill=(239, 234, 226, int(170 * smooth((u - 0.3) / 0.3))))
    a = np.asarray(pil, np.float32)
    blur = (1 - a1) * 16 * S
    if blur > 0.5:
        a = cv2.GaussianBlur(a, (0, 0), blur)
    al = a[..., 3:4] / 255.0 * a1
    out = img.astype(np.float32) * (1 - al) + a[..., 2::-1] * al
    return np.clip(out, 0, 255).astype(np.uint8)

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
        img = np.zeros((H, W, 3), np.uint8)
        if idx > 0 and shots[idx - 1].get('burn'):
            img = burn(img, 1.0 - i / max(1, n))
        return img
    if s['src'] == 'end':
        return end_frame(i, n)
    z = s['z0'] + (s['z1'] - s['z0']) * ease(s.get('ease', 'lin'), u)
    img = place(src_frame(s, i, idx), z, s.get('rc', s['c']) if REEL else s['c'])
    img = sharpen(img)
    img = grade(img)
    img = halation(img)
    img = vintage(img, s.get('era', 1.0), FRAME[0])
    if s.get('burn') and u > 0.55:
        img = burn(img, (u - 0.55) / 0.45)
    if s.get('radial'):
        img = radial_blur(img, s['radial'] * u)
    if s.get('fadein') and i < s['fadein']:
        img = (img.astype(np.float32) * (i / s['fadein'])).astype(np.uint8)
    if s.get('flash_in') and i < s['flash_in']:
        k = 1 - i / s['flash_in']
        img = (img.astype(np.float32) * (1 - k) + 255 * k).clip(0, 255).astype(np.uint8)
    return img

def letterbox_amount(frame):
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

FRAME = [0]

def frame_image(f):
    FRAME[0] = f
    idx, i = shot_at(f)
    img = render_shot_frame(idx, i)
    for kind, at, hw in TRANS:
        d = f - at
        if -hw <= d < hw:
            p = 1 - abs(d + 0.5) / hw
            if kind == 'whip':
                shift = int((d + 0.5) / hw * W * 0.18)
                M = np.float32([[1, 0, -shift], [0, 1, 0]])
                img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
                img = motion_blur(img, 260 * S * p)
            elif kind == 'xfade' and d < 0:
                other = render_shot_frame(*shot_at(at))
                img = cv2.addWeighted(img, 1 - (d + hw) / (2 * hw), other, (d + hw) / (2 * hw), 0)
    # exposure bump on the big beats
    for at in DROPS:
        if 0 <= f - at < 5:
            k = 1 - (f - at) / 5
            img = cv2.addWeighted(img, 1, cv2.GaussianBlur(img, (0, 0), 24 * S), 0.35 * k, 0)
    if f < mark['end']:
        img = finish(img, shots[idx].get('era', 1.0))
    for a, b, label in years:
        if a <= f < b:
            img = year_layer(img, label)
            break
    for cue in cues:
        img = render_cue(img, cue, f)
    lb = 0 if REEL else letterbox_amount(f)
    if lb > 0:
        bar = int((H - W / 2.39) / 2 * lb)
        img[:bar] = 0
        img[H - bar:] = 0
    return img

def main():
    print('frames', TOTAL, 'seconds', round(TOTAL / FPS, 2), 'marks', mark, file=sys.stderr)
    if args.preview or args.frames:
        os.makedirs(args.out, exist_ok=True)
        todo = [int(x) for x in args.frames.split(',')] if args.frames else range(0, TOTAL, args.preview)
        for f in todo:
            im = frame_image(f)
            cv2.imwrite(os.path.join(args.out, f'p_{f:04d}.jpg'), cv2.resize(im, (540, 960) if REEL else (960, 540), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 84])
        return
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
    if args.music:
        dur = TOTAL / FPS
        cmd += ['-ss', str(args.music_at), '-t', f'{dur:.3f}', '-i', args.music,
                '-af', f'afade=t=in:d=0.4,afade=t=out:st={dur - 2.2:.3f}:d=2.2', '-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', str(args.crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', args.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(TOTAL):
        p.stdin.write(frame_image(f).tobytes())
        if f % 60 == 0:
            print('frame', f, file=sys.stderr)
    p.stdin.close()
    p.wait()

main()
