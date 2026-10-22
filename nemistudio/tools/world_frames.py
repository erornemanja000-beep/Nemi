#!/usr/bin/env python3
"""Cuts the chapter clips of the four sense worlds into WebP frame sequences for the scroll films.

    python3 tools/world_frames.py <clips-dir> public/w src/worlds.json

Every chapter becomes N frames over its chosen seconds of footage: desktop 1280x720 (cover) and a
portrait 720x1280 crop around the subject for phones. worlds.json tells the site how many frames
each chapter has.
"""
import json
import os
import sys

import cv2

SRC, OUT, MANIFEST = sys.argv[1], sys.argv[2], sys.argv[3]
N = 40            # frames per chapter
D = (1280, 720)   # desktop
M = (720, 1280)   # phone

# world: [(clip, start s, end s, focus x for the portrait crop)]
WORLDS = {
    'cafe': [
        ('808', 1.0, 5.0, 0.45),
        ('coverr-hand-holding-coffee-beans-3024', 0.4, 4.6, 0.42),
        ('coverr-espresso-making-4455', 2.0, 7.0, 0.36),
        ('41858', 1.5, 5.7, 0.55),
        ('46333', 4.0, 9.0, 0.6),
        ('29330', 1.0, 3.6, 0.5),
    ],
    'law': [
        ('coverr-contemplative-woman-in-city', 2.0, 7.0, 0.42),
        ('23115', 2.5, 6.0, 0.35),
        ('16106', 0.5, 5.0, 0.42),
        ('46755', 0.6, 4.6, 0.47),
        ('17049', 4.6, 8.4, 0.5),
        ('23112', 1.0, 5.0, 0.5),
    ],
    'gym': [
        ('4596', 1.0, 6.0, 0.5),
        ('45874', 0.5, 5.0, 0.45),
        ('40966', 6.5, 10.0, 0.6),
        ('52097', 2.8, 4.6, 0.55),
        ('52084', 1.0, 6.0, 0.5),
        ('coverr-contemplative-woman-with-windswept-hair', 9.0, 14.0, 0.62),
    ],
    'hotel': [
        ('coverr-woman-posing-by-the-window-6038', 4.2, 9.0, 0.5),
        ('5009', 0.5, 5.5, 0.5),
        ('5030', 1.0, 6.0, 0.55),
        ('coverr-woman-relaxing-in-a-pool-4201', 1.0, 4.5, 0.48),
        ('44500', 1.0, 6.0, 0.45),
        ('1704', 1.0, 6.0, 0.5),
    ],
}

def cover(img, size, fx=0.5, fy=0.5):
    h, w = img.shape[:2]
    tw, th = size
    s = max(tw / w, th / h)
    nw, nh = round(w * s), round(h * s)
    r = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    x = int(min(max(0, fx * nw - tw / 2), nw - tw))
    y = int(min(max(0, fy * nh - th / 2), nh - th))
    return r[y:y + th, x:x + tw]

manifest = {}
for world, chapters in WORLDS.items():
    manifest[world] = []
    for ci, (clip, t0, t1, fx) in enumerate(chapters):
        cap = cv2.VideoCapture(os.path.join(SRC, clip + '.mp4'))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        a, b = int(t0 * fps), int(t1 * fps)
        want = [round(a + (b - a) * k / (N - 1)) for k in range(N)]
        frames = {}
        cap.set(cv2.CAP_PROP_POS_FRAMES, a)
        i = a
        while i <= b:
            ok, f = cap.read()
            if not ok:
                break
            if i in want:
                frames[i] = f
            i += 1
        for kind, size, q in (('d', D, 70), ('m', M, 66)):
            d = os.path.join(OUT, world, str(ci + 1), kind)
            os.makedirs(d, exist_ok=True)
            for k, idx in enumerate(want):
                f = frames[idx] if idx in frames else frames[max(frames)]
                img = cover(f, size, fx if kind == 'm' else 0.5)
                cv2.imwrite(os.path.join(d, f'{k + 1:02d}.webp'), img, [cv2.IMWRITE_WEBP_QUALITY, q])
        manifest[world].append({'n': N, 'src': clip})
        print(world, ci + 1, clip, len(frames))
json.dump(manifest, open(MANIFEST, 'w'), indent=1)
