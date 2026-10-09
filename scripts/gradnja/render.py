#!/usr/bin/env python3
"""Renderuje video "Gradnja DON'S-a" od pet fotografija lokala.

Lokal se sklapa deo po deo: zazidan prozor se raspadne u cigle, padaju
okviri i stakla, pa vrata i vitrina, unutrasnjost se puni i na kraju
padaju slova DON'S. Scenario (sta, gde i kada) je u scenario.py.

Upotreba:
  python3 render.py assets/lokal video/gradnja.mp4
  python3 render.py assets/lokal preview.png --preview 1.0 2.5 6.0
"""
import argparse
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import align  # noqa: E402
import scenario as S  # noqa: E402

K = 1.6875                      # raw piksel -> izlazni piksel (640 -> 1080)
OW, OH = 1920, 1080
MARGIN = 160                    # rezerva oko platna (izlazni px)
CW = int(round(480 * K)) + 2 * MARGIN
CH = int(round(640 * K)) + 2 * MARGIN
X0_R = 15 + 1.40625 * 395       # kadriranje faza 2-5 (kao lokal_faza_N.png)
X0_1 = 15 + 1.40625 * 384       # kadriranje faze 1 (kao video_c_end_frame.png)
TOP_BAND = 92                   # gornji redovi (oluk/prozori) koriste drugu kolonu za razvlacenje
SHUTTER = 0.5

GOLD = (255, 214, 140)
PINK = (255, 186, 206)
WHITE = (255, 250, 242)
DUST = (248, 238, 228)


# ---------------------------------------------------------------- pomocne

def cx(x):
    return MARGIN + K * x


def cy(y):
    return MARGIN + K * y


def crect(r):
    x0, y0, x1, y1 = r
    return (int(round(cx(x0))), int(round(cy(y0))), int(round(cx(x1))), int(round(cy(y1))))


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def smoothstep(e0, e1, x):
    t = clamp((x - e0) / (e1 - e0))
    return t * t * (3 - 2 * t)


def ease_out_back(t, s=1.70158):
    t = t - 1
    return t * t * ((s + 1) * t + s) + 1


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def to_premul(arr_rgba):
    a = arr_rgba[..., 3:4] / 255.0
    return np.concatenate([arr_rgba[..., :3] * a, a], -1).astype(np.float32)


def pil_from_premul(p):
    a = p[..., 3:4]
    rgb = np.where(a > 1e-4, p[..., :3] / np.maximum(a, 1e-4), 0)
    out = np.concatenate([rgb, a * 255], -1)
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), 'RGBA')


def premul_from_pil(im):
    return to_premul(np.asarray(im.convert('RGBA')).astype(np.float32))


def over(D, spr, x, y, clip=None):
    """Premultiplied 'over' kompozicija sprajta na platno D (u mestu)."""
    h, w = spr.shape[:2]
    x0, y0 = int(math.floor(x)), int(math.floor(y))
    X0, Y0 = max(x0, 0), max(y0, 0)
    X1, Y1 = min(x0 + w, D.shape[1]), min(y0 + h, D.shape[0])
    if X1 <= X0 or Y1 <= Y0:
        return
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    if clip is not None:
        m = np.zeros((Y1 - Y0, X1 - X0), np.float32)
        for (a0, b0, a1, b1) in clip:
            ix0, iy0, ix1, iy1 = max(a0, X0), max(b0, Y0), min(a1, X1), min(b1, Y1)
            if ix1 > ix0 and iy1 > iy0:
                m[iy0 - Y0:iy1 - Y0, ix0 - X0:ix1 - X0] = 1
        s = s * m[..., None]
    dst = D[Y0:Y1, X0:X1]
    dst *= (1 - s[..., 3:4])
    dst += s


def smooth1d(a, k):
    if k <= 1:
        return a
    pad = k // 2
    ap = np.pad(a, ((pad, pad), (0, 0)), mode='edge')
    ker = np.ones(2 * pad + 1) / (2 * pad + 1)
    return np.stack([np.convolve(ap[:, c], ker, mode='valid') for c in range(a.shape[1])], 1)


def coons_fill(img, r, rng, band=4, smooth=15, noise=1.6):
    """Popuni pravougaonik glatkim prelazom izmedju boja na njegovim ivicama."""
    x0, y0, x1, y1 = r
    h, w = y1 - y0, x1 - x0
    T = smooth1d(img[y0 - band:y0, x0:x1].mean(0), smooth)
    B = smooth1d(img[y1:y1 + band, x0:x1].mean(0), smooth)
    L = smooth1d(img[y0:y1, x0 - band:x0].mean(1), smooth)
    R = smooth1d(img[y0:y1, x1:x1 + band].mean(1), smooth)
    TL, TR = (T[0] + L[0]) / 2, (T[-1] + R[0]) / 2
    BL, BR = (B[0] + L[-1]) / 2, (B[-1] + R[-1]) / 2
    u = ((np.arange(w) + 0.5) / w)[None, :, None]
    v = ((np.arange(h) + 0.5) / h)[:, None, None]
    P = ((1 - v) * T[None] + v * B[None] + (1 - u) * L[:, None] + u * R[:, None]
         - ((1 - u) * (1 - v) * TL + u * (1 - v) * TR + (1 - u) * v * BL + u * v * BR))
    return P + rng.normal(0, noise, P.shape)


# ---------------------------------------------------------------- sprajtovi efekata

_cache = {}


def star_sprite(r, color):
    key = ('star', r, color)
    if key in _cache:
        return _cache[key]
    n = int(r * 6) | 1
    c = n // 2
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - c
    d = np.hypot(xx, yy)
    core = np.exp(-(d / (0.55 * r)) ** 2)
    glow = 0.45 * np.exp(-(d / (1.6 * r)) ** 2)
    rays = (np.exp(-(np.abs(yy) / (0.18 * r)) ** 2) * np.exp(-(np.abs(xx) / (2.6 * r)) ** 2)
            + np.exp(-(np.abs(xx) / (0.18 * r)) ** 2) * np.exp(-(np.abs(yy) / (2.6 * r)) ** 2))
    a = np.clip(core + glow + 0.8 * rays, 0, 1)
    col = np.array(color, np.float32)
    rgb = col[None, None] * (0.55 + 0.45 * core[..., None]) + 255 * 0.45 * core[..., None]
    spr = np.concatenate([np.clip(rgb, 0, 255) * a[..., None], a[..., None]], -1).astype(np.float32)
    _cache[key] = spr
    return spr


def soft_sprite(r, color, kind='soft'):
    r = max(1, int(round(r)))
    key = (kind, r, color)
    if key in _cache:
        return _cache[key]
    n = r * 4 + 1
    c = n // 2
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - c
    d = np.hypot(xx, yy) / r
    a = np.exp(-d * d * 1.6) if kind == 'soft' else np.exp(-d * d * 0.9)
    col = np.array(color, np.float32)
    spr = np.concatenate([col[None, None] * a[..., None], a[..., None]], -1).astype(np.float32)
    _cache[key] = spr
    return spr


def draw_centered(D, spr, x, y, alpha=1.0, clip=None):
    if alpha <= 0.003:
        return
    h, w = spr.shape[:2]
    over(D, spr * alpha if alpha < 0.999 else spr, x - w / 2, y - h / 2, clip)


# ---------------------------------------------------------------- pokreti elemenata

E_REST = 0.22


def drop_curve(tau, e=E_REST):
    tl = 1 / (1 + 2 * e + 2 * e * e)
    if tau < tl:
        return -(1 - (tau / tl) ** 2), tl
    t2 = tau - tl
    b1 = 2 * e * tl
    if t2 < b1:
        s = t2 / b1
        return -(e * e) * 4 * s * (1 - s), tl
    t3 = t2 - b1
    b2 = 2 * e * e * tl
    s = min(t3 / b2, 1.0)
    return -(e ** 4) * 4 * s * (1 - s), tl


def first_cross(fn):
    """Prvi tau u kom ease kriva dostigne 1 (trenutak 'udarca')."""
    for i in range(1, 400):
        if fn(i / 400) >= 1:
            return i / 400
    return 0.6


IMPACT_BACK = {s: first_cross(lambda t, s=s: ease_out_back(t, s)) for s in (1.6, 1.8, 2.2)}


class Elem:
    pass


def motion(e, tau):
    """Vraca stanje elementa u trenutku tau (0..1)."""
    st = dict(dx=0.0, dy=0.0, sx=1.0, sy=1.0, ax=0.5, ay=1.0, rot=0.0, alpha=1.0, flash=0.0, wipe=1.0)
    a = e.anim
    if a == 'drop':
        ee = 0.15 if e.heavy else E_REST
        y, tl = drop_curve(tau, ee)
        st['dy'] = y * e.dist
        st['alpha'] = clamp(tau / 0.10)
        if tau >= tl:
            dt = (tau - tl) * e.d
            st['flash'] = 0.22 * math.exp(-dt / 0.08)
            if e.squash:
                q = math.exp(-dt / 0.06)
                st['sy'] = 1 - (0.12 if e.heavy else 0.09) * q
                st['sx'] = 1 + (0.05 if e.heavy else 0.04) * q
    elif a == 'rise':
        k = ease_out_back(tau, 1.8)
        st['dy'] = (1 - k) * e.dist
        st['alpha'] = clamp(tau / 0.12)
        ti = IMPACT_BACK[1.8]
        if tau >= ti:
            st['flash'] = 0.18 * math.exp(-(tau - ti) * e.d / 0.08)
    elif a == 'slide_l':
        k = ease_out_back(tau, 1.6)
        st['dx'] = (1 - k) * e.dist
        ti = IMPACT_BACK[1.6]
        if tau >= ti:
            st['flash'] = 0.18 * math.exp(-(tau - ti) * e.d / 0.08)
    elif a == 'swing':
        st['sx'] = max(0.03, ease_out_back(tau, 2.2))
        st['ax'], st['ay'] = 0.0, 0.5
        st['alpha'] = clamp(tau / 0.08)
    elif a == 'pop':
        s = max(0.02, ease_out_back(tau, 2.6))
        st['sx'] = st['sy'] = s
        st['ax'], st['ay'] = 0.5, 0.5
        st['alpha'] = clamp(tau / 0.15)
    elif a == 'light':
        st['alpha'] = 1.0 if tau < 0.06 or tau > 0.15 else 0.15
    elif a == 'flicker':
        pattern = [(0.0, 1), (0.08, 0.1), (0.20, 1), (0.28, 0.15), (0.40, 1)]
        v = 1
        for (t0, val) in pattern:
            if tau >= t0:
                v = val
        st['alpha'] = v
    elif a == 'wipe_up':
        st['wipe'] = smoothstep(0, 1, tau)
    elif a == 'vanish':
        k = tau * tau
        st['sy'] = max(0.02, 1 - k)
        st['sx'] = max(0.02, 1 - 0.5 * k)
        st['ax'], st['ay'] = 0.5, 0.5
        st['alpha'] = 1 - smoothstep(0.45, 1.0, tau)
        st['flash'] = 0.6 * smoothstep(0.0, 0.5, tau)
    return st


def impact_tau(e):
    a = e.anim
    if a == 'drop':
        return drop_curve(0.0, 0.15 if e.heavy else E_REST)[1]
    if a == 'rise':
        return IMPACT_BACK[1.8]
    if a == 'slide_l':
        return IMPACT_BACK[1.6]
    if a == 'swing':
        return 0.55
    if a == 'pop':
        return 0.35
    return None


# ---------------------------------------------------------------- priprema scene

class Scene:
    def __init__(self, base, seed=7):
        self.rng = np.random.default_rng(seed)
        random.seed(seed)
        self.P = {n: self.make_plate(base, n) for n in range(1, 6)}
        self.E = {}
        self.tr = {}
        self.impacts = []        # (globalno t, amplituda tresenja)
        self.particles = []
        for key, spec in S.TRANSITIONS.items():
            self.tr[key] = self.prepare(key, spec)
        self.make_ambient()
        self.grain = [self.rng.normal(0, 2.0, (OH, OW, 1)).astype(np.float32) for _ in range(6)]
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        r2 = ((xx - OW / 2) / (OW / 2)) ** 2 + ((yy - OH / 2) / (OH / 2)) ** 2
        self.vig_mask = np.clip(r2 - 0.25, 0, None)[..., None].astype(np.float32)

    def make_plate(self, base, n):
        sx, sy, tx, ty = align.ALIGN[n]
        pad = 160
        raw = align.padded(align.load_raw(base, n), pad)
        a = 1 / (K * sx)
        e = 1 / (K * sy)
        c = (-MARGIN / K - align.CX - tx) / sx + align.CX + pad
        f = (-MARGIN / K - align.CY - ty) / sy + align.CY + pad
        im = raw.transform((CW, CH), Image.AFFINE, (a, 0, c, 0, e, f), resample=Image.BICUBIC)
        return np.asarray(im).astype(np.float32)

    # -- elementi
    def make_elem(self, spec, pix, mask, tstart, interior_tops):
        e = Elem()
        e.name = spec['name']
        e.rect = spec['rect']
        e.c = crect(spec['rect'])
        e.anim = spec['anim']
        e.t = spec['t']
        e.d = spec['d']
        e.kind = spec.get('kind', 'facade')
        e.heavy = spec.get('heavy', False)
        e.clip = [crect(c) for c in spec['clip']] if spec.get('clip') else None
        x0, y0, x1, y1 = spec['rect']
        e.squash = e.anim == 'drop' and (y1 - y0) > 20 and (x1 - x0) > 30
        # rastojanje pada/izlaska (raw px)
        if e.anim == 'drop':
            if e.clip:
                tops = [c[1] for c in spec['clip'] if c[0] < x1 and c[2] > x0]
                e.dist = y1 - min(tops)
            else:
                e.dist = 150
        elif e.anim == 'rise':
            if e.clip:
                bots = [c[3] for c in spec['clip'] if c[0] < x1 and c[2] > x0]
                e.dist = max(bots) - y0
            else:
                e.dist = 110
        elif e.anim == 'slide_l':
            if e.clip:
                rights = [c[2] for c in spec['clip'] if c[1] < y1 and c[3] > y0]
                e.dist = max(rights) - x0
            else:
                e.dist = 70
        else:
            e.dist = 0
        if spec.get('bg') == 'src':
            # meke ivice da se element stopi sa praznom prostorijom iza njega
            h, w = mask.shape
            f = 6.0
            ry = np.minimum(np.arange(h) + 0.5, h - np.arange(h) - 0.5) / f
            rx = np.minimum(np.arange(w) + 0.5, w - np.arange(w) - 0.5) / f
            mask = mask * np.clip(np.minimum(ry[:, None], rx[None, :]), 0, 1)
        rgba = np.concatenate([pix, mask[..., None] * 255], -1)
        e.pil = Image.fromarray(np.clip(rgba + 0.5, 0, 255).astype(np.uint8), 'RGBA')
        e.premul = to_premul(rgba)
        e.mask = mask
        e.start = tstart
        return e

    def cut_elements(self, plate, specs, tstart, bgplate=None):
        """Iseca elemente od kasnijeg ka ranijem; ispod svakog ostaje 'prazno'.

        Prazno je glatka popuna iz okoline, ili (za velike elemente sa bg='src')
        odgovarajuci deo pozadinske ploce, npr. prazne prostorije.
        """
        img = plate.copy()
        out = {}
        for spec in sorted(specs, key=lambda s: s['t'], reverse=True):
            r = crect(spec['rect'])
            x0, y0, x1, y1 = r
            mask = np.ones((y1 - y0, x1 - x0), np.float32)
            for hr in spec.get('holes', []):
                hx0, hy0, hx1, hy1 = crect(hr)
                ix0, iy0, ix1, iy1 = max(hx0, x0), max(hy0, y0), min(hx1, x1), min(hy1, y1)
                if ix1 > ix0 and iy1 > iy0:
                    mask[iy0 - y0:iy1 - y0, ix0 - x0:ix1 - x0] = 0
            pix = img[y0:y1, x0:x1].copy()
            if spec.get('bg') == 'src' and bgplate is not None:
                fill = bgplate[y0:y1, x0:x1]
            else:
                fill = coons_fill(img, r, self.rng)
            img[y0:y1, x0:x1] = fill * mask[..., None] + pix * (1 - mask[..., None])
            out[spec['name']] = self.make_elem(spec, pix, mask, tstart, None)
        elems = [out[s['name']] for s in sorted(specs, key=lambda s: s['t'])]
        return img, elems

    def make_bricks(self, plate, spec, tstart):
        x0, y0, x1, y1 = spec['rect']
        cols, rows = spec['cols'], spec['rows']
        bw, bh = (x1 - x0) / cols, (y1 - y0) / rows
        ccx, ccy = (x0 + x1) / 2, (y0 + y1) / 2
        bricks = []
        dmax = math.hypot((x1 - x0) / 2, (y1 - y0) / 2)
        for r in range(rows):
            off = 0.5 * bw if r % 2 else 0.0
            xs = [x0]
            xx = x0 + (bw - off if off else bw)
            while xx < x1 - 1:
                xs.append(xx)
                xx += bw
            xs.append(x1)
            for i in range(len(xs) - 1):
                rr = (xs[i], y0 + r * bh, xs[i + 1], y0 + (r + 1) * bh)
                c = crect(rr)
                if c[2] - c[0] < 4 or c[3] - c[1] < 4:
                    continue
                pix = plate[c[1]:c[3], c[0]:c[2]].copy()
                b = Elem()
                b.c = c
                h, w = pix.shape[:2]
                plain = np.concatenate([pix, np.full((h, w, 1), 255, np.float32)], -1)
                bev = plain.copy()
                t = 3
                bev[:t, :, :3] = np.minimum(255, bev[:t, :, :3] * 1.10 + 22)
                bev[:, :t, :3] = np.minimum(255, bev[:, :t, :3] * 1.08 + 16)
                bev[-t:, :, :3] *= 0.70
                bev[:, -t:, :3] *= 0.76
                bev[:1, :, :3] *= 0.80
                bev[:, :1, :3] *= 0.82
                b.plain = to_premul(plain)
                b.bevel = to_premul(bev)
                b.pil = Image.fromarray(np.clip(bev + 0.5, 0, 255).astype(np.uint8), 'RGBA')
                mx, my = (rr[0] + rr[2]) / 2, (rr[1] + rr[3]) / 2
                d = math.hypot(mx - ccx, my - ccy) / dmax
                if spec['order'] == 'center':
                    order = d
                    dirx, diry = (mx - ccx), (my - ccy)
                    n = math.hypot(dirx, diry) or 1
                    sp = random.uniform(60, 170)
                    b.v = (dirx / n * sp, random.uniform(-230, -60) + diry / n * 40)
                else:
                    order = r / max(1, rows - 1)
                    b.v = (random.uniform(-80, 80), random.uniform(-150, 0))
                b.tdet = spec['t0'] + spec['spread'] * order + random.uniform(0, 0.07)
                s0, s1 = spec['seams']
                b.tseam = s0 + (s1 - s0) * order
                b.w = random.uniform(-260, 260)
                b.center = (mx, my)
                bricks.append(b)
                # prasina pri odvajanju
                for _ in range(2):
                    self.particles.append(dict(kind='dust', t0=tstart + b.tdet + 0.04, life=random.uniform(0.45, 0.7),
                                               x=cx(mx + random.uniform(-bw / 3, bw / 3)), y=cy(my + random.uniform(-bh / 3, bh / 3)),
                                               vx=random.uniform(-30, 30) * K, vy=random.uniform(-20, 30) * K, g=0,
                                               r0=4 * K, r1=13 * K, a0=0.22, color=DUST))
        return bricks

    def prepare(self, key, spec):
        T = dict(spec)
        T['key'] = key
        src, dst = self.P[spec['src']], self.P[spec['dst']]
        start = spec['start']
        if key == 'D':
            sg = spec['sign']
            r = crect(sg['rect'])
            x0, y0, x1, y1 = r
            # zid bez natpisa = isti deo zida iz faze 4, izjednacen po boji sa fazom 5
            ring = np.zeros(dst.shape[:2], bool)
            ring[y0 - 10:y1 + 10, x0 - 10:x1 + 10] = True
            ring[y0:y1, x0:x1] = False
            gain = dst[ring].mean(0) / np.maximum(src[ring].mean(0), 1)
            E = dst.copy()
            h, w = y1 - y0, x1 - x0
            f = 14.0
            ry = np.minimum(np.arange(h) + 0.5, h - np.arange(h) - 0.5) / f
            rx = np.minimum(np.arange(w) + 0.5, w - np.arange(w) - 0.5) / f
            fm = np.clip(np.minimum(ry[:, None], rx[None, :]), 0, 1)[..., None]
            E[y0:y1, x0:x1] = np.clip(src[y0:y1, x0:x1] * gain, 0, 255) * fm + dst[y0:y1, x0:x1] * (1 - fm)
            lum = dst[y0:y1, x0:x1].mean(-1)
            dark = Image.fromarray(((lum < 140) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(15))
            dark = np.asarray(dark.filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255
            # slova su tamna (~85), senka srednja (~170), zid svetao (~210)
            alpha = np.clip((198 - lum) / 70, 0, 1) * dark
            letters = []
            for i, (ch, a0, a1) in enumerate(sg['spans']):
                m = np.zeros_like(alpha)
                c0, c1 = int(round(cx(a0))) - x0, int(round(cx(a1))) - x0
                m[:, c0:c1] = alpha[:, c0:c1]
                ys, xs = np.nonzero(m > 0.02)
                by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
                pix = dst[y0 + by0:y0 + by1, x0 + bx0:x0 + bx1]
                rgba = np.concatenate([pix, m[by0:by1, bx0:bx1, None] * 255], -1)
                L = Elem()
                L.name = ch
                L.c = (x0 + bx0, y0 + by0, x0 + bx1, y0 + by1)
                L.anim = 'drop'
                L.t = sg['t0'] + i * sg['step']
                L.d = sg['d']
                L.heavy = False
                L.squash = True
                L.kind = 'letter'
                L.clip = None
                L.spin = ch == "'"
                L.dist = (L.c[3] - MARGIN) / K + 30
                L.pil = Image.fromarray(np.clip(rgba + 0.5, 0, 255).astype(np.uint8), 'RGBA')
                L.premul = to_premul(rgba)
                L.start = start
                letters.append(L)
            T['letters'] = letters
            T['letter_mask'] = (r, alpha)
            T['E'] = E
            T['elems'] = letters
        else:
            srcp = src
            if 'remove' in spec:
                srcp = src.copy()
                T['removed'] = []
                for rs in spec['remove']:
                    r = crect(rs['rect'])
                    pix = src[r[1]:r[3], r[0]:r[2]].copy()
                    mask = np.ones(pix.shape[:2], np.float32)
                    T['removed'].append(self.make_elem(rs, pix, mask, start, None))
                    srcp[r[1]:r[3], r[0]:r[2]] = coons_fill(src, r, self.rng)
            T['srcp'] = srcp
            bg = None
            if 'grade' in spec:
                bg = self.empty_room(srcp, dst, spec)
            E, elems = self.cut_elements(dst, spec['elements'], start, bg)
            if bg is not None:
                E = bg
            T['E'] = E
            T['elems'] = elems
            for e in T.get('removed', []):
                x0, y0, x1, y1 = e.c
                for _ in range(18):
                    self.particles.append(dict(kind='star', t0=start + e.t + random.uniform(0.1, 0.35), life=random.uniform(0.4, 0.7),
                                               x=random.uniform(x0, x1), y=random.uniform(y0, y1),
                                               vx=random.uniform(-50, 50) * K, vy=random.uniform(-70, 10) * K, g=30 * K,
                                               r=random.uniform(2.0, 3.4), color=random.choice([GOLD, PINK, WHITE])))
            if 'bricks' in spec:
                T['brick_list'] = self.make_bricks(src, spec['bricks'], start)
        # udarci: tresenje + cestice
        for e in T['elems']:
            ti = impact_tau(e)
            if ti is None:
                continue
            tg = start + e.t + ti * e.d
            amp = 6.0 if e.heavy else 3.2 if e.kind == 'letter' else 2.4 if e.anim in ('drop', 'rise') else 1.4
            if e.anim == 'pop':
                amp = 0.0
            if amp:
                self.impacts.append((tg, amp))
            self.spawn_impact(e, tg)
        for e in T['elems']:
            if e.anim in ('light', 'flicker', 'wipe_up'):
                self.spawn_soft(e, start)
        self.E[spec['dst']] = E
        return T

    def empty_room(self, srcp, dst, spec):
        """Faza 4 sa unutrasnjoscu iz faze 3 (prazna prostorija) prefarbanom u boje faze 4."""
        xs, ys = [], []
        for r in spec['grade']:
            x0, y0, x1, y1 = crect(r)
            xs.append(srcp[y0:y1, x0:x1].reshape(-1, 3).mean(0))
            ys.append(dst[y0:y1, x0:x1].reshape(-1, 3).mean(0))
        (xa, xb), (ya, yb) = xs, ys
        g = np.clip((yb - ya) / np.where(np.abs(xb - xa) < 1, 1, xb - xa), 0.5, 1.6)
        o = ya - g * xa
        graded = np.clip(srcp * g + o, 0, 255)
        out = dst.copy()
        f = 4.0
        for r in spec['interior']:
            x0, y0, x1, y1 = crect(r)
            h, w = y1 - y0, x1 - x0
            ry = np.minimum(np.arange(h) + 0.5, h - np.arange(h) - 0.5) / f
            rx = np.minimum(np.arange(w) + 0.5, w - np.arange(w) - 0.5) / f
            m = np.clip(np.minimum(ry[:, None], rx[None, :]), 0, 1)[..., None]
            out[y0:y1, x0:x1] = graded[y0:y1, x0:x1] * m + dst[y0:y1, x0:x1] * (1 - m)
        return out

    def spawn_impact(self, e, tg):
        x0, y0, x1, y1 = e.c
        w = x1 - x0
        if e.kind == 'facade':
            n = 12 if w > 60 * K else 7
            yb = y1 if e.anim == 'drop' else y0
            for _ in range(n):
                x = random.uniform(x0, x1)
                self.particles.append(dict(kind='dust', t0=tg, life=random.uniform(0.45, 0.75), x=x, y=yb + random.uniform(-3, 3),
                                           vx=random.uniform(-60, 60) * K, vy=random.uniform(-45, -10) * K, g=0,
                                           r0=3 * K, r1=random.uniform(10, 16) * K, a0=0.30, color=DUST))
            for _ in range(4):
                self.particles.append(dict(kind='star', t0=tg, life=random.uniform(0.4, 0.7), x=random.uniform(x0, x1), y=yb,
                                           vx=random.uniform(-70, 70) * K, vy=random.uniform(-120, -30) * K, g=120 * K,
                                           r=random.uniform(2.2, 3.6), color=random.choice([GOLD, PINK, WHITE])))
        else:
            n = 16 if e.heavy else 10
            if e.anim == 'pop':
                cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
                for _ in range(n):
                    ang = random.uniform(0, 2 * math.pi)
                    sp = random.uniform(50, 140) * K
                    self.particles.append(dict(kind='star', t0=tg, life=random.uniform(0.45, 0.8), x=cxm, y=cym,
                                               vx=math.cos(ang) * sp, vy=math.sin(ang) * sp, g=60 * K,
                                               r=random.uniform(2.2, 3.8), color=random.choice([GOLD, PINK, WHITE])))
            else:
                yb = y1 if e.anim == 'drop' else (y0 + y1) / 2
                for _ in range(n):
                    self.particles.append(dict(kind='star', t0=tg, life=random.uniform(0.45, 0.8), x=random.uniform(x0, x1), y=yb,
                                               vx=random.uniform(-90, 90) * K, vy=random.uniform(-150, -40) * K, g=140 * K,
                                               r=random.uniform(2.2, 3.8), color=random.choice([GOLD, PINK, WHITE])))
                if e.kind == 'letter':
                    for _ in range(6):
                        self.particles.append(dict(kind='dust', t0=tg, life=random.uniform(0.4, 0.6), x=random.uniform(x0, x1), y=y1,
                                                   vx=random.uniform(-50, 50) * K, vy=random.uniform(-30, -5) * K, g=0,
                                                   r0=3 * K, r1=12 * K, a0=0.22, color=DUST))

    def spawn_soft(self, e, start):
        x0, y0, x1, y1 = e.c
        tg = start + e.t
        if e.anim == 'wipe_up':
            for i in range(14):
                tt = tg + e.d * i / 14
                yl = y1 - (y1 - y0) * smoothstep(0, 1, i / 14)
                self.particles.append(dict(kind='star', t0=tt, life=0.5, x=random.uniform(x0, x1), y=yl,
                                           vx=random.uniform(-30, 30) * K, vy=random.uniform(-60, -20) * K, g=0,
                                           r=random.uniform(2.0, 3.2), color=random.choice([GOLD, PINK, WHITE])))
        else:
            for _ in range(5):
                self.particles.append(dict(kind='star', t0=tg + 0.05, life=random.uniform(0.4, 0.6), x=(x0 + x1) / 2, y=(y0 + y1) / 2,
                                           vx=random.uniform(-60, 60) * K, vy=random.uniform(-60, 40) * K, g=40 * K,
                                           r=random.uniform(2.0, 3.0), color=random.choice([GOLD, WHITE])))

    def make_ambient(self):
        self.ambient = []
        for _ in range(55):
            self.ambient.append(dict(x=cx(random.uniform(10, 470)), y=cy(random.uniform(100, 620)),
                                     f=random.uniform(0.35, 0.9), ph=random.uniform(0, 1),
                                     r=random.uniform(1.6, 2.8), vy=-random.uniform(4, 10) * K,
                                     color=random.choice([GOLD, GOLD, PINK, WHITE])))

    # ------------------------------------------------------------ vremenska linija

    def locate(self, t):
        if t < S.A_START:
            return 'rest', 1, None, 0.0
        for key in 'ABCD':
            tr = self.tr[key]
            if tr['start'] <= t < tr['start'] + tr['dur']:
                return 'tr', key, tr, t - tr['start']
            nxt = {'A': 'B', 'B': 'C', 'C': 'D', 'D': None}[key]
            end = tr['start'] + tr['dur']
            nstart = self.tr[nxt]['start'] if nxt else S.FINAL_START
            if end <= t < nstart:
                return 'rest', tr['dst'], None, 0.0
        return 'final', 5, None, t - S.FINAL_START

    def geometry(self, t):
        """(gx, gy, gtx, gty) i X0: faza 1 u svom kadru, pa prelaz na kadar faze 4."""
        a1 = align.ALIGN[1]
        if t < S.A_START:
            p = 0.0
        else:
            f0, f1 = self.tr['A']['fade']
            p = smoothstep(S.A_START + f0, S.A_START + f1, t)
        g = tuple(a1[i] * (1 - p) + (1.0 if i < 2 else 0.0) * p for i in range(4))
        X0 = X0_1 * (1 - p) + X0_R * p
        return g, X0

    def side_layers(self, t):
        """Ploce od kojih se razvlace ivice kadra: [(tezina, ploca, pravilo)]."""
        mode, key, tr, lt = self.locate(t)
        if mode != 'tr':
            return [(1.0, self.P[key], 'plain' if key == 1 else 'crop')]
        p = smoothstep(tr['fade'][0], tr['fade'][1], lt)
        if key in ('A', 'B') and lt < tr['bricks']['t0']:
            p = 0.0
        src = tr.get('srcp', self.P[tr['src']])
        rule_src = 'plain' if key == 'A' else 'crop'
        return [(1 - p, src, rule_src), (p, tr['E'], 'crop')]

    def shake(self, t):
        sx = sy = 0.0
        for (ti, amp) in self.impacts:
            dt = t - ti
            if 0 <= dt < 0.45:
                k = amp * math.exp(-dt / 0.085)
                sx += k * math.sin(2 * math.pi * 17 * dt)
                sy += k * math.cos(2 * math.pi * 21 * dt) * 0.8
        for key in 'AB':
            tr = self.tr[key]
            bs = tr['bricks']
            lt = t - tr['start']
            if bs['t0'] - 0.05 <= lt <= bs['t0'] + bs['spread'] + 0.25:
                env = math.sin(math.pi * clamp((lt - bs['t0'] + 0.05) / (bs['spread'] + 0.3)))
                sx += 1.1 * env * math.sin(t * 91.0)
                sy += 1.1 * env * math.sin(t * 73.0 + 1.0)
        return sx, sy

    # ------------------------------------------------------------ staticki sloj

    def static_layer(self, t):
        mode, key, tr, lt = self.locate(t)
        if mode != 'tr':
            return self.P[key]
        dst = tr['dst']
        E = tr['E']
        if key in ('A', 'B'):
            bs = tr['bricks']
            if lt < bs['t0']:
                base = tr['srcp'].copy()
            else:
                p = smoothstep(tr['fade'][0], tr['fade'][1], lt)
                base = tr['srcp'] * (1 - p) + E * p
                x0, y0, x1, y1 = crect(bs['rect'])
                base[y0:y1, x0:x1] = E[y0:y1, x0:x1]
        elif key == 'C':
            p = smoothstep(tr['fade'][0], tr['fade'][1], lt)
            base = tr['srcp'] * (1 - p) + E * p
            w = smoothstep(tr['wipe'][0], tr['wipe'][1], lt)
            ytop, ybot = cy(219), cy(602)
            ylev = ybot - w * (ybot - ytop + 60 * K)
            for r in tr['interior']:
                x0, y0, x1, y1 = crect(r)
                yy = np.arange(y0, y1, dtype=np.float32)
                m = np.clip((yy - ylev) / (30 * K) + 0.5, 0, 1)[:, None, None]
                base[y0:y1, x0:x1] = tr['srcp'][y0:y1, x0:x1] * (1 - m) + E[y0:y1, x0:x1] * m
        else:
            p = smoothstep(tr['fade'][0], tr['fade'][1], lt)
            base = self.P[tr['src']] * (1 - p) + E * p
        for e in tr['elems']:
            if lt >= e.t + e.d:
                x0, y0 = e.c[0], e.c[1]
                sl = base[y0:y0 + e.premul.shape[0], x0:x0 + e.premul.shape[1]]
                sl *= (1 - e.premul[..., 3:4])
                sl += e.premul[..., :3]
        if tr.get('settle'):
            s = smoothstep(tr['settle'][0], tr['settle'][1], lt)
            if s > 0:
                base = base * (1 - s) + self.P[dst] * s
        return base

    # ------------------------------------------------------------ dinamicki sloj

    def draw_elem(self, D, e, lt):
        tau = (lt - e.t) / e.d
        if tau < 0 or tau >= 1:
            return
        st = motion(e, tau)
        if st['alpha'] <= 0.003:
            return
        x0, y0, x1, y1 = e.c
        w, h = x1 - x0, y1 - y0
        spr_pil = e.pil
        if getattr(e, 'spin', False):
            tl = drop_curve(0, E_REST)[1]
            st['rot'] = 540 * (1 - min(1.0, tau / tl))
        need_pil = abs(st['sx'] - 1) > 1e-3 or abs(st['sy'] - 1) > 1e-3 or abs(st['rot']) > 0.05
        if need_pil:
            nw, nh = max(1, int(round(w * st['sx']))), max(1, int(round(h * st['sy'])))
            im = spr_pil if (nw, nh) == (w, h) else spr_pil.resize((nw, nh), Image.BICUBIC)
            if abs(st['rot']) > 0.05:
                im = im.rotate(st['rot'], resample=Image.BICUBIC, expand=True)
            spr = premul_from_pil(im)
        else:
            nw, nh = w, h
            spr = e.premul
        if st['flash'] > 0.002:
            spr = spr.copy()
            spr[..., :3] += (255 * spr[..., 3:4] - spr[..., :3]) * st['flash']
        if st['alpha'] < 0.999:
            spr = spr * st['alpha']
        if st['wipe'] < 0.999:
            hh = spr.shape[0]
            yy = np.arange(hh, dtype=np.float32)
            m = np.clip((yy - (1 - st['wipe']) * hh) / 4.0, 0, 1)[:, None, None]
            spr = spr * m

        def pos(tt):
            s2 = motion(e, clamp(tt))
            ox = x0 + st['ax'] * w - st['ax'] * nw + s2['dx'] * K
            oy = y0 + st['ay'] * h - st['ay'] * nh + s2['dy'] * K
            if abs(st['rot']) > 0.05:
                ox += (nw - spr.shape[1]) / 2
                oy += (nh - spr.shape[0]) / 2
            return ox, oy

        px, py = pos(tau)
        dt_tau = SHUTTER / S.FPS / e.d
        qx, qy = pos(tau - dt_tau)
        dist = math.hypot(px - qx, py - qy)
        n = int(clamp(math.ceil(dist / 5), 1, 8))
        if n == 1:
            over(D, spr, px, py, e.clip)
            return
        pts = [pos(tau - dt_tau * j / (n - 1)) for j in range(n)]
        bx0 = int(math.floor(min(p[0] for p in pts)))
        by0 = int(math.floor(min(p[1] for p in pts)))
        bx1 = int(math.ceil(max(p[0] for p in pts))) + spr.shape[1] + 1
        by1 = int(math.ceil(max(p[1] for p in pts))) + spr.shape[0] + 1
        acc = np.zeros((by1 - by0, bx1 - bx0, 4), np.float32)
        for (ax_, ay_) in pts:
            ix, iy = int(math.floor(ax_)) - bx0, int(math.floor(ay_)) - by0
            acc[iy:iy + spr.shape[0], ix:ix + spr.shape[1]] += spr
        acc /= n
        over(D, acc, bx0, by0, e.clip)

    def draw_bricks(self, D, tr, lt):
        g = 2200 * K
        for b in tr['brick_list']:
            x0, y0, x1, y1 = b.c
            if lt < b.tdet:
                over(D, b.plain, x0, y0)
                bs = smoothstep(b.tseam, b.tseam + 0.08, lt)
                if bs > 0:
                    over(D, b.bevel * bs, x0, y0)
                continue
            tau = lt - b.tdet
            if tau > 1.4:
                continue
            if tau < 0.06:
                s = 1 + 0.06 * tau / 0.06
                im = b.pil.resize((max(1, int((x1 - x0) * s)), max(1, int((y1 - y0) * s))), Image.BICUBIC)
                spr = premul_from_pil(im)
                over(D, spr, (x0 + x1) / 2 - spr.shape[1] / 2, (y0 + y1) / 2 - spr.shape[0] / 2)
                continue
            tt = tau - 0.06
            mx = cx(b.center[0]) + b.v[0] * K * tt
            my = cy(b.center[1]) + b.v[1] * K * tt + 0.5 * g * tt * tt
            if my > CH + 80:
                continue
            im = b.pil.resize((max(1, int((x1 - x0) * 1.06)), max(1, int((y1 - y0) * 1.06))), Image.BICUBIC)
            im = im.rotate(b.w * tt, resample=Image.BICUBIC, expand=True)
            spr = premul_from_pil(im)
            a = 1 - smoothstep(1.0, 1.35, tau)
            over(D, spr * a if a < 1 else spr, mx - spr.shape[1] / 2, my - spr.shape[0] / 2)

    def draw_glint(self, D, rect, lt, t0, d, peak=0.34):
        tau = (lt - t0) / d
        if not 0 <= tau <= 1:
            return
        x0, y0, x1, y1 = crect(rect)
        w, h = x1 - x0, y1 - y0
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        s = xx + 0.55 * yy
        smax = w + 0.55 * h
        wb = 22.0
        pos = -2 * wb + tau * (smax + 4 * wb)
        a = peak * (np.exp(-((s - pos) / wb) ** 2) + 0.5 * np.exp(-((s - pos + 2.6 * wb) / (0.35 * wb)) ** 2))
        a *= math.sin(math.pi * tau) ** 0.5
        spr = np.concatenate([np.repeat(255 * a[..., None], 3, -1), a[..., None]], -1).astype(np.float32)
        over(D, spr, x0, y0)

    def draw_glow(self, D, rect, lt, t0, d, color=PINK, peak=0.15):
        tau = (lt - t0) / d
        if not 0 <= tau <= 1:
            return
        x0, y0, x1, y1 = crect(rect)
        h, w = y1 - y0, x1 - x0
        yy = np.linspace(1.0, 0.45, h, dtype=np.float32)[:, None]
        a = (peak * math.sin(math.pi * tau)) * np.repeat(yy, w, 1)
        col = np.array(color, np.float32)
        spr = np.concatenate([col[None, None] * a[..., None], a[..., None]], -1)
        over(D, spr, x0, y0)

    def draw_lights(self, D, tr, lt):
        for e in tr['elems']:
            if e.anim not in ('light', 'flicker'):
                continue
            tau = (lt - e.t) / e.d
            x0, y0, x1, y1 = e.c
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            if e.anim == 'light' and 0 <= tau < 1:
                r = (10 + 22 * ease_out_cubic(tau)) * K
                draw_centered(D, soft_sprite(r, (255, 244, 222), 'glow'), mx, my, 0.75 * (1 - tau) ** 1.4)
            if e.anim == 'flicker' and 0 <= tau < 1.6:
                on = motion(e, min(tau, 0.999))['alpha'] > 0.5
                if on:
                    draw_centered(D, soft_sprite(30 * K, (255, 226, 150), 'glow'), mx, my, 0.30 * (1 - smoothstep(1.0, 1.6, tau)))

    def draw_particles(self, D, t):
        for p in self.particles:
            age = t - p['t0']
            if not 0 <= age < p['life']:
                continue
            q = age / p['life']
            x = p['x'] + p['vx'] * age
            y = p['y'] + p['vy'] * age + 0.5 * p['g'] * age * age
            if p['kind'] == 'dust':
                r = p['r0'] + (p['r1'] - p['r0']) * ease_out_cubic(q)
                draw_centered(D, soft_sprite(r, p['color']), x, y, p['a0'] * (1 - q) ** 1.5)
            else:
                a = math.sin(math.pi * q) ** 0.7
                draw_centered(D, star_sprite(round(p['r'] * 2) / 2, p['color']), x, y, a)

    def draw_ambient(self, D, t):
        for s in self.ambient:
            a = max(0.0, math.sin(2 * math.pi * (t * s['f'] + s['ph']))) ** 3 * 0.55
            if a < 0.02:
                continue
            draw_centered(D, star_sprite(round(s['r'] * 2) / 2, s['color']), s['x'], s['y'] + s['vy'] * t, a)

    def dynamic_layer(self, t):
        D = np.zeros((CH, CW, 4), np.float32)
        mode, key, tr, lt = self.locate(t)
        if mode == 'tr':
            if key in ('A', 'B'):
                self.draw_bricks(D, tr, lt)
            if key == 'A' and lt < 0.45:
                q = lt / 0.45
                x0, y0, x1, y1 = tr['bricks']['rect']
                draw_centered(D, soft_sprite((50 + 110 * ease_out_cubic(q)) * K, (255, 205, 215), 'glow'),
                              cx((x0 + x1) / 2), cy((y0 + y1) / 2), 0.6 * (1 - q) ** 2)
            for e in tr.get('removed', []):
                self.draw_elem(D, e, lt)
            if key == 'C':
                self.draw_lights(D, tr, lt)
            for e in tr['elems']:
                self.draw_elem(D, e, lt)
            for (rect, t0, d) in tr.get('glints', []):
                self.draw_glint(D, rect, lt, t0, d)
            if tr.get('glow'):
                rect, t0, d = tr['glow']
                self.draw_glow(D, rect, lt, t0, d)
        elif mode == 'final':
            self.draw_final(D, lt)
        self.draw_particles(D, t)
        self.draw_ambient(D, t)
        return D

    def draw_final(self, D, lt):
        s0, s1 = S.FINAL['sweep']
        tau = (lt - s0) / (s1 - s0)
        if 0 <= tau <= 1:
            (x0, y0, x1, y1), alpha = self.tr['D']['letter_mask']
            h, w = alpha.shape
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            s = xx + 0.5 * yy
            smax = w + 0.5 * h
            wb = 26.0
            pos = -2 * wb + tau * (smax + 4 * wb)
            a = 0.55 * np.exp(-((s - pos) / wb) ** 2) * np.clip(alpha * 1.4, 0, 1)
            spr = np.concatenate([np.repeat(255 * a[..., None], 3, -1), a[..., None]], -1).astype(np.float32)
            over(D, spr, x0, y0)
        rect, t0, d = S.FINAL['glass']
        self.draw_glint(D, rect, lt, t0, d, peak=0.26)

    # ------------------------------------------------------------ kompozicija kadra

    RULES = {'plain': (0, 479, 479), 'crop': (0, 395, 448)}   # (levo, desno gore, desno dole) u raw kolonama

    def sample_cols(self, plate, g, shx, shy, cols):
        gx, gy, gtx, gty = g
        j = np.arange(OH, dtype=np.float32)
        v = gy * j + MARGIN - gy * shy + K * (align.CY * (1 - gy) + gty)
        v0 = np.clip(np.floor(v).astype(int), 0, CH - 2)
        fv = (v - v0)[:, None]
        out = []
        for c in cols:
            u = MARGIN + gx * (K * c - shx) + K * (align.CX * (1 - gx) + gtx)
            u0 = int(np.clip(math.floor(u), 0, CW - 2))
            fu = u - u0
            a = plate[v0, u0] * (1 - fv) + plate[v0 + 1, u0] * fv
            b = plate[v0, u0 + 1] * (1 - fv) + plate[v0 + 1, u0 + 1] * fv
            out.append(a * (1 - fu) + b * fu)
        return out

    def assemble(self, Splate, g, X0, shx, shy, layers):
        """Centar kadra iz kompozicije, ivice razvucene iz kolona ploca (svaka po svom pravilu)."""
        gx, gy, gtx, gty = g
        Xi = int(math.floor(X0)) - 2
        Ws = int(480 * K) + 6
        cu = MARGIN + gx * (Xi - X0 - shx) + K * (align.CX * (1 - gx) + gtx)
        cv = MARGIN + gy * (0 - shy) + K * (align.CY * (1 - gy) + gty)
        im = Image.fromarray(np.clip(Splate + 0.5, 0, 255).astype(np.uint8))
        strip = np.asarray(im.transform((Ws, OH), Image.AFFINE, (gx, 0, cu, 0, gy, cv),
                                        resample=Image.BICUBIC)).astype(np.float32)
        band = int(round(TOP_BAND * K))
        iL = int(round(X0 - Xi))

        groups = {}
        for (w, plate, rule) in layers:
            if w <= 1e-4:
                continue
            cols = self.sample_cols(plate, g, shx, shy, self.RULES[rule])
            acc = groups.setdefault(rule, [0.0, [np.zeros((OH, 3), np.float32) for _ in range(3)]])
            acc[0] += w
            for i in range(3):
                acc[1][i] += w * cols[i]
        O = np.zeros((OH, OW, 3), np.float32)
        for rule, (wsum, cols) in groups.items():
            left, rtop, rbot = (c / wsum for c in cols)
            _, cT, cB = self.RULES[rule]
            Q = np.empty((OH, OW, 3), np.float32)
            Q[:, :Xi + iL] = left[:, None]
            for (ya, yb, c, side) in ((0, band, cT, rtop), (band, OH, cB, rbot)):
                iR = int(round(X0 + K * c - Xi))
                Q[ya:yb, Xi + iL:Xi + iR] = strip[ya:yb, iL:iR]
                Q[ya:yb, Xi + iR:] = side[ya:yb, None]
            O += wsum * Q
        return O

    def frame(self, t):
        g, X0 = self.geometry(t)
        shx, shy = self.shake(t)
        Sp = self.static_layer(t)
        O = self.assemble(Sp, g, X0, shx, shy, self.side_layers(t))
        D = self.dynamic_layer(t)
        if D[..., 3].max() > 0.002:
            gx, gy, gtx, gty = g
            # izlaz (x,y) -> platno (u,v)
            a = gx
            c = MARGIN + gx * (0 - X0 - shx) + K * (align.CX * (1 - gx) + gtx)
            e = gy
            f = MARGIN + gy * (0 - shy) + K * (align.CY * (1 - gy) + gty)
            Dim = pil_from_premul(D).transform((OW, OH), Image.AFFINE, (a, 0, c, 0, e, f), resample=Image.BICUBIC)
            Dp = premul_from_pil(Dim)
            O = O * (1 - Dp[..., 3:4]) + Dp[..., :3]
        # vinjeta i zrno se uvode postepeno, da prvi kadar bude isti kao kraj prethodnog klipa
        v = 0.08 * smoothstep(0.0, 1.2, t)
        if v > 0:
            O = O * (1 - v * self.vig_mask)
        O = O + self.grain[int(t * S.FPS) % len(self.grain)] * smoothstep(0.0, 0.6, t)
        return np.clip(O + 0.5, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base')
    ap.add_argument('out')
    ap.add_argument('--preview', type=float, nargs='*')
    ap.add_argument('--scale', type=float, default=0.5)
    args = ap.parse_args()
    sc = Scene(args.base)
    if args.preview:
        tiles = [Image.fromarray(sc.frame(t)) for t in args.preview]
        tw, th = int(OW * args.scale), int(OH * args.scale)
        cols = 2 if len(tiles) > 1 else 1
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new('RGB', (tw * cols, th * rows), 'white')
        for i, im in enumerate(tiles):
            sheet.paste(im.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
        sheet.save(args.out)
        return
    n = int(round(S.TOTAL * S.FPS))
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                           '-s', f'{OW}x{OH}', '-r', str(S.FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                           '-movflags', '+faststart', args.out], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(sc.frame(i / S.FPS).tobytes())
        if i % 30 == 0:
            print(f'{i}/{n}', flush=True)
    ff.stdin.close()
    ff.wait()
    print('gotovo', args.out)


if __name__ == '__main__':
    main()
