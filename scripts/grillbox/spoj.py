#!/usr/bin/env python3
"""Grillbox: AI izmena (npr. dodata slanina) spojena sa pravom Wolt fotkom.

    python3 scripts/grillbox/spoj.py <wolt.jpg> <ai.png> <bez-pozadine.png> <x0,y0,x1,y1> <izlaz.png>

Sa AI slike se uzima samo ono što se zaista promenilo, i to samo unutar pravougaonika
x0,y0,x1,y1 (pikseli na 1600×900). Tanjir, pomfrit, pozadina i svetlo ostaju sa originala.
Providnost (alfa) se uzima sa iste fotke bez pozadine, jer se obris jela ne menja.
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

wolt, ai, cut, roi, out = sys.argv[1:6]
orig = Image.open(wolt).convert('RGB')
W, H = orig.size
edit = Image.open(ai).convert('RGB').resize((W, H), Image.LANCZOS)
a = np.asarray(orig).astype(np.float32)
b = np.asarray(edit).astype(np.float32)


# AI ponekad pomeri kadar za nekoliko piksela: nađi pomak sa najmanjom razlikom
def gray(x):
    return x.mean(2)[::4, ::4]


ga, gb = gray(a), gray(b)
best = (1e9, 0, 0)
for dy in range(-4, 5):
    for dx in range(-4, 5):
        d = np.abs(ga[8:-8, 8:-8] - np.roll(np.roll(gb, dy, 0), dx, 1)[8:-8, 8:-8]).mean()
        best = min(best, (d, dx, dy))
_, dx, dy = best
b = np.roll(np.roll(b, dy * 4, 0), dx * 4, 1)

# maska promene: razlika boja, zamućena, samo u zadatom pravougaoniku
diff = np.abs(a - b).max(2)
m = Image.fromarray(np.clip(diff * 3, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
m = np.asarray(m).astype(np.float32) / 255
x0, y0, x1, y1 = map(int, roi.split(','))
box = np.zeros_like(m)
box[y0:y1, x0:x1] = 1
box = np.asarray(Image.fromarray((box * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255
m = np.clip(m * 1.6, 0, 1) * box
# popuni rupe u maski i omekšaj ivicu
m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(5))).astype(np.float32) / 255
mix = a * (1 - m[..., None]) + b * m[..., None]

res = Image.fromarray(np.clip(mix, 0, 255).astype(np.uint8))
res.putalpha(Image.open(cut).getchannel('A'))
res.save(out)
print(out, 'pomak', dx * 4, dy * 4, 'promenjeno %.1f%%' % ((m > .5).mean() * 100))
