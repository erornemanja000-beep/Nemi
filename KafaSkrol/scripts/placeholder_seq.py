#!/usr/bin/env python3
"""Kafa skrol: privremeni kadrovi sekvenci grind / pour / sip iza pravog interfejsa (plan-izrade.md, Z2).

    python3 -I placeholder_seq.py <KafaSkrol/public/media/seq> [--force] [--only grind pour sip]
    python3 -I placeholder_seq.py <KafaSkrol/public/media/seq> --composite 84 <van repoa>/sav-G084.png

Crta sive siluete na providnoj pozadini, oblikom i polozajem kao `studio/kafa-skrol/dizajn/mockup.html`
(mlin sa levkom, kuvalo, V60 sa bokalom, solja), u koordinatama punog kadra (jedinica S = stranica kvadrata).
Brojevi kadrova, isecci, sidra, `steps` i posteri su tacno po tackama 2-4 Interfejsa u plan-izrade.md:
  grind  sat G, G1-G96,   pun kadar 1 x 1,25, isecak x 0,22-0,78;  d 96 kadrova, m 48 (svaki drugi)
  pour   sat G, G65-G192, pun kadar 1 x 1,    isecak x 0,26-0,98;  d 128, m 64
  sip    sat S, S1-S64,   pun kadar 1 x 1,    isecak x 0,20-0,84 / y 0-0,86;  d 64, m 32
Nivoi: d (1200 px za S) i m (800 px za S), bez l. WebP sa alfom, q 60, method 6.
Posteri: grind d/0001 i m/0001 (= G1); pour poster-d i poster-m (G150); sip d/0064 i poster-m (S64).

Mlaz mlevene kafe je niz tacaka u zajednickim koordinatama sveta (y u kadru GRIND; POUR kamera je tacno 1 S
nize, pa je y_pour = y_grind - 1). Otvor je aktivan G52-G88, a rep pada do oko G110. Zato se tacke na savu
poklapaju piksel na piksel. Kuvalo se naginje 12 -> 32 stepeni (G110-G120) i vraca (G164-G176), nivo u bokalu
raste 0 -> 38 % (G136-G192, `kafa_y` po kadru za G177-G192), solja se spusta S1-S14.
U donjem levom uglu isecka je oznaka kadra (G084, S032) i rec PLATZHALTER.

Zastita: folder ciji seq.json ima "placeholder": false (pravi render) se nikad ne prepisuje, ni sa --force.
Folder sa sadrzajem bez naseg seq.json ("placeholder": true) prepisuje se samo sa --force.
Isti ulaz daje iste bajtove (fiksno seme, bez vremena u fajlovima).

--composite G IZLAZ.png: GRIND d kadar iznad POUR d kadra, pomeren tacno 1 S, sa uvecanim savom desno.
Cita vec napravljene fajlove; izlaz mora biti van repoa (privremeni folder).
Slike su nase (crta ih ova skripta), pa se koristi sistemski Pillow.
"""
import argparse
import json
import math
import pathlib
import random
import re
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

VERSION = 'placeholder-1'
SS = 2             # nadsempliranje pri crtanju, pa Lanczos na pravu velicinu
QUALITY = 60
ALPHA_QUALITY = 90
LEVELS = {'d': 1200, 'm': 800}

GRIND_PH = (0xBD, 0xB6, 0xAC)   # --color-placeholder (krem)
POUR_PH = (0xB3, 0xA6, 0x9B)    # --color-placeholder (terakota)
SIP_PH = (0xA2, 0x94, 0x8A)     # --color-placeholder (braon)
INK_DEEP = (0x1B, 0x15, 0x0D)   # --pp-ink-deep
CREAM_LIGHT = (0xF4, 0xEE, 0xE4)  # --pp-cream-light
CREAM = (0xE6, 0xDD, 0xCE)      # --pp-cream (samo kompozit)
TERRACOTTA = (0x91, 0x54, 0x39)  # --pp-terracotta (samo kompozit)
BEAN = (0x4A, 0x2A, 0x1C)       # zrna, kao .beans-pair u mockupu
GROUNDS = (0x3B, 0x24, 0x18)    # mlevena kafa
COFFEE = (0x3A, 0x1F, 0x14)     # kafa u bokalu, kao u mockupu
WHITE = (0xFF, 0xFF, 0xFF)

SPEC = {
    'grind': dict(clock='G', g_od=1, g_do=96, full=(1, 1.25), crop=(0.22, 0, 0.56, 1.25),
                  counts={'d': (96, 1), 'm': (48, 2)},
                  poster={'d': 'd/0001.webp', 'm': 'm/0001.webp'}, poster_files={},
                  steps=[('pin', 1, 64), ('prelaz', 65, 96)]),
    'pour': dict(clock='G', g_od=65, g_do=192, full=(1, 1), crop=(0.26, 0, 0.72, 1),
                 counts={'d': (128, 1), 'm': (64, 2)},
                 poster={'d': 'poster-d.webp', 'm': 'poster-m.webp'},
                 poster_files={'poster-d.webp': ('d', 150), 'poster-m.webp': ('m', 150)},
                 steps=[('prelaz', 65, 96), ('pin', 97, 176), ('talas', 177, 192)]),
    'sip': dict(clock='S', g_od=1, g_do=64, full=(1, 1), crop=(0.20, 0, 0.64, 0.86),
                counts={'d': (64, 1), 'm': (32, 2)},
                poster={'d': 'd/0064.webp', 'm': 'poster-m.webp'},
                poster_files={'poster-m.webp': ('m', 64)},
                steps=[('talas', 1, 16), ('pin', 17, 64)]),
}


# ---------------- pomocne funkcije ----------------
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def pw(points, g):
    """Deo po deo linearno: [(g, v), ...] sortirano po g."""
    if g <= points[0][0]:
        return points[0][1]
    for (g0, v0), (g1, v1) in zip(points, points[1:]):
        if g <= g1:
            return v0 + (v1 - v0) * (g - g0) / (g1 - g0)
    return points[-1][1]


_TOK = re.compile(r'[MHVLQCZ]|-?\d*\.?\d+')
_ARGS = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'Q': 4, 'C': 6, 'Z': 0}


def svg_path(d, n=10):
    """Apsolutne M/L/H/V/Q/C/Z putanje iz mockupa -> lista tacaka (krive uzorkovane sa n tacaka)."""
    toks, i, cmd, pts, cur = _TOK.findall(d), 0, None, [], (0.0, 0.0)
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd == 'Z':
                continue
        elif cmd == 'M':
            cmd = 'L'
        a = [float(t) for t in toks[i:i + _ARGS[cmd]]]
        i += _ARGS[cmd]
        if cmd in 'ML':
            cur = (a[0], a[1])
            pts.append(cur)
        elif cmd == 'H':
            cur = (a[0], cur[1])
            pts.append(cur)
        elif cmd == 'V':
            cur = (cur[0], a[0])
            pts.append(cur)
        elif cmd == 'Q':
            (x0, y0), (x1, y1), (x2, y2) = cur, a[0:2], a[2:4]
            for k in range(1, n + 1):
                t = k / n
                pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t * t * x2,
                            (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t * t * y2))
            cur = (x2, y2)
        elif cmd == 'C':
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = cur, a[0:2], a[2:4], a[4:6]
            for k in range(1, n + 1):
                t = k / n
                mt = 1 - t
                pts.append((mt ** 3 * x0 + 3 * mt * mt * t * x1 + 3 * mt * t * t * x2 + t ** 3 * x3,
                            mt ** 3 * y0 + 3 * mt * mt * t * y1 + 3 * mt * t * t * y2 + t ** 3 * y3))
            cur = (x3, y3)
    return pts


def ellipse_pts(cx, cy, rx, ry, rot=0.0, n=28):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def rrect_pts(x, y, w, h, r, n=5):
    r = min(r, w / 2, h / 2)
    out = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def mapped(pts, fn):
    return [fn(u, v) for u, v in pts]


# ---------------- platno u koordinatama punog kadra ----------------
class Canvas:
    """Crta oblike zadate u jedinicama S (od gornjeg levog ugla punog kadra) u isecak, nadsemplirano."""

    def __init__(self, crop, px):
        self.x0, self.y0, cw, ch = crop
        self.size = (round(cw * px), round(ch * px))
        self.k = px * SS
        self.img = Image.new('RGBA', (self.size[0] * SS, self.size[1] * SS), (0, 0, 0, 0))

    def p(self, x, y):
        return ((x - self.x0) * self.k, (y - self.y0) * self.k)

    def _geom(self, shapes):
        out, xs, ys = [], [], []
        for s in shapes:
            kind = s[0]
            if kind == 'poly':
                pts = [self.p(*q) for q in s[1]]
                out.append(('poly', pts))
                xs += [q[0] for q in pts]
                ys += [q[1] for q in pts]
            elif kind == 'line':
                pts = [self.p(*q) for q in s[1]]
                w = max(1.0, s[2] * self.k)
                out.append(('line', pts, w))
                xs += [q[0] - w for q in pts] + [q[0] + w for q in pts]
                ys += [q[1] - w for q in pts] + [q[1] + w for q in pts]
            elif kind == 'circle':
                (cx, cy), r = self.p(s[1], s[2]), s[3] * self.k
                out.append(('circle', cx, cy, r))
                xs += [cx - r, cx + r]
                ys += [cy - r, cy + r]
            elif kind == 'text':
                (x, y), font = self.p(s[1], s[2]), ImageFont.load_default(size=max(8, round(s[4] * self.k)))
                l, t, r, b = font.getbbox(s[3])
                out.append(('text', x, y, s[3], font))
                xs += [x + l, x + r]
                ys += [y + t, y + b]
        return out, xs, ys

    def draw(self, shapes, color, alpha=1.0, clip=None):
        geom, xs, ys = self._geom(shapes)
        if not xs:
            return
        W, H = self.img.size
        bx0, by0 = max(0, math.floor(min(xs)) - 2), max(0, math.floor(min(ys)) - 2)
        bx1, by1 = min(W, math.ceil(max(xs)) + 2), min(H, math.ceil(max(ys)) + 2)
        if bx1 <= bx0 or by1 <= by0:
            return
        mask = self._mask(geom, bx0, by0, bx1 - bx0, by1 - by0)
        if clip:
            mask = ImageChops.multiply(mask, self._mask(self._geom(clip)[0], bx0, by0, bx1 - bx0, by1 - by0))
        if alpha < 1:
            a = round(alpha * 255)
            mask = mask.point([v * a // 255 for v in range(256)])
        layer = Image.new('RGBA', mask.size, color + (0,))
        layer.putalpha(mask)
        self.img.alpha_composite(layer, dest=(bx0, by0))

    @staticmethod
    def _mask(geom, ox, oy, w, h):
        m = Image.new('L', (w, h), 0)
        d = ImageDraw.Draw(m)
        for g in geom:
            if g[0] == 'poly':
                d.polygon([(x - ox, y - oy) for x, y in g[1]], fill=255)
            elif g[0] == 'line':
                pts, wid = [(x - ox, y - oy) for x, y in g[1]], g[2]
                if len(pts) > 1:
                    d.line(pts, fill=255, width=round(wid), joint='curve')
                for x, y in (pts[0], pts[-1]):
                    d.ellipse([x - wid / 2, y - wid / 2, x + wid / 2, y + wid / 2], fill=255)
            elif g[0] == 'circle':
                _, cx, cy, r = g
                d.ellipse([cx - ox - r, cy - oy - r, cx - ox + r, cy - oy + r], fill=255)
            elif g[0] == 'text':
                _, x, y, s, font = g
                d.text((x - ox, y - oy), s, font=font, fill=255)
        return m

    def label(self, x, y, text):
        """Oznaka kadra: tamna pilula sa svetlim tekstom, gornji levi ugao u (x, y) S."""
        size = 0.015
        font = ImageFont.load_default(size=max(8, round(size * self.k)))
        l, t, r, b = font.getbbox(text)
        tw, th = (r - l) / self.k, (b - t) / self.k
        pad = 0.006
        w, h = tw + 2 * pad, th + 2 * pad
        self.draw([('poly', rrect_pts(x, y, w, h, h / 2))], INK_DEEP, 0.62)
        self.draw([('text', x + pad - l / self.k, y + pad - t / self.k, text, size)], CREAM_LIGHT)

    def result(self):
        return self.img.resize(self.size, Image.LANCZOS)


# ---------------- GRIND ----------------
G_K = 0.69 / 568            # mockup jedinice -> S: vrh levka 0,15 S, dno postolja 0,84 S


def gm(u, v):
    return (0.5 + (u - 220) * G_K, 0.15 + v * G_K)


SPOUT_Y = 0.84               # sidro `otvor` (y u kadru GRIND)
V0, ACC = 0.00708, 0.002385  # S po kadru i S po kadru^2: rep 6 cm ispod otvora na G96, pada na dno filtera do G110
HOPPER = svg_path('M52 22H388L352 188Q346 214 318 214H122Q94 214 88 188Z')
BODY_R = 161 * G_K          # poluprecnik tela mlina u S (za lazni okret)


def _rng_beans():
    rng = random.Random(1801)
    beans, t = [], -22.0
    while t < 47.5:
        rate = 1.35 if t < 40 else 1.15
        t += rng.uniform(0.35, 1.15) / rate
        beans.append(dict(t0=t, x=0.5 + clamp(rng.gauss(0, 0.017), -0.042, 0.042), vx=rng.uniform(-0.0007, 0.0007),
                          rot=rng.uniform(0, 180), spin=rng.uniform(-9, 9), s=rng.uniform(0.9, 1.1)))
    return beans


def _rng_grounds():
    rng = random.Random(5288)
    out = []
    for i in range(int((88 - 52) * 3) + 1):
        out.append(dict(e=52 + i / 3 + rng.uniform(-0.12, 0.12), j=rng.uniform(-1, 1), r=rng.uniform(0.0026, 0.0040)))
    return out


BEANS = _rng_beans()
GROUNDS_P = _rng_grounds()


def grounds_at(g):
    """Tacke mlaza u svetu: (x, y_grind, r). Isti spisak crtaju i GRIND i POUR."""
    out = []
    for p in GROUNDS_P:
        t = g - p['e']
        if t < 0:
            continue
        d = V0 * t + 0.5 * ACC * t * t
        out.append((0.5 + p['j'] * (0.002 + 0.012 * d), SPOUT_Y + d, p['r']))
    return out


def hopper_fill(g):
    return pw([(1, 0.45), (40, 0.80), (48, 0.85), (64, 0.85), (88, 0.72), (96, 0.72)], g)


def grind_rot(g):
    return -25.0 * (1 - smooth((g - 1) / 39))   # -25 -> 0 stepeni, G1-G40


def rot_x(x, a):
    """Lazni okret oko vertikalne ose kroz otvor (x = 0,5): (novo x, sabijanje sirine)."""
    th = math.asin(clamp((x - 0.5) / BODY_R, -1, 1))
    return 0.5 + BODY_R * math.sin(th + math.radians(a)), max(0.15, math.cos(th + math.radians(a))) / max(0.15, math.cos(th))


def draw_grind(c, g):
    a = grind_rot(g)
    v_top = 205 - hopper_fill(g) * (205 - 30)
    dip = 10 * smooth((g - 48) / 16)
    fill_y = gm(220, v_top + dip)[1]
    # zrna u padu (iza staklenog levka)
    beans = []
    for b in BEANS:
        t = g - b['t0']
        if t < 0:
            continue
        y = -0.03 + 0.012 * t + 0.00075 * t * t
        if y > fill_y:
            continue
        beans.append(('poly', ellipse_pts(b['x'] + b['vx'] * t, y, 0.0134 * b['s'], 0.0182 * b['s'], b['rot'] + b['spin'] * t, 20)))
    c.draw(beans, GRIND_PH, 0.75)
    # levak: prsten, staklo, gomila zrna
    c.draw([('poly', mapped(rrect_pts(36, 0, 368, 22, 7), gm))], GRIND_PH)
    c.draw([('poly', mapped(HOPPER, gm))], GRIND_PH, 0.55)
    surf = [(u, v_top + dip * max(0.0, 1 - ((u - 220) / 120) ** 2)) for u in range(40, 404, 8)]
    c.draw([('poly', mapped(surf + [(404, 230), (40, 230)], gm))], GRIND_PH, 0.55, clip=[('poly', mapped(HOPPER, gm))])
    # vrat, rucica, prsten, telo
    for x, y, w, h, r in ((116, 214, 208, 30, 6), (296, 230, 112, 9, 4.5), (148, 244, 144, 22, 4), (68, 266, 322, 276, 24)):
        c.draw([('poly', mapped(rrect_pts(x, y, w, h, r), gm))], GRIND_PH)
    # dugme gore levo na telu, prati okret
    bx, bs = rot_x(gm(115, 0)[0], a)
    bw = 62 * G_K * bs
    c.draw([('poly', rrect_pts(bx - bw / 2, gm(0, 270)[1], bw, 26 * G_K, 9 * G_K * bs))], WHITE, 0.16)
    # odsjaj koji klizi preko inoksa
    hx, hs = rot_x(0.5 + BODY_R * math.sin(math.radians(20)), a)
    hw = 0.03 * hs
    c.draw([('poly', rrect_pts(hx - hw / 2, gm(0, 280)[1], hw, 248 * G_K, hw / 2))], WHITE, 0.14)
    # postolje
    c.draw([('poly', mapped(rrect_pts(88, 542, 282, 26, 8), gm))], GRIND_PH, 0.85)
    # tocak za finocu mlevenja (napred levo), prati okret
    dx, dsx = rot_x(gm(112, 0)[0], a)
    dy = gm(0, 420)[1]
    c.draw([('poly', ellipse_pts(dx, dy, 64 * G_K * dsx, 64 * G_K))], WHITE, 0.22)
    c.draw([('poly', ellipse_pts(dx, dy, 44 * G_K * dsx, 44 * G_K))], WHITE, 0.18)
    # crni otvor na x = 0,5, donja ivica = sidro `otvor`
    c.draw([('poly', [(0.478, 0.795), (0.522, 0.795), (0.514, SPOUT_Y), (0.486, SPOUT_Y)])], INK_DEEP, 0.85)
    # mlaz mlevene kafe
    c.draw([('circle', x, y, r) for x, y, r in grounds_at(g)], GROUNDS)
    c.label(0.232, 0.952, f'G{g:03d} · PLATZHALTER')


# ---------------- POUR ----------------
V60 = dict(x=0.5, y=0.47, rx=0.128, ry=0.03)   # sidro `ivica_v60`
PULT_Y = 0.95
KD = 0.256 / 368                # V60 iz mockupa: ivica 368 jedinica = 2 rx
CONE_TOP_HW, CONE_BOT_HW = 176 * KD, 72 * KD
CONE_BOT_Y = V60['y'] + 200 * KD
BED_Y0 = CONE_BOT_Y - 0.006     # unutrasnje dno filtera
CARAFE_TOP = CONE_BOT_Y + 22 * KD
CK_X, CK_Y = 0.0008, (PULT_Y - CARAFE_TOP) / 296   # bokal: mockup 250..546 jedinica -> do pulta


def cm(u, v):
    return (0.5 + (u - 190) * CK_X, CARAFE_TOP + (v - 250) * CK_Y)


CARAFE = mapped(svg_path('M96 250H284Q300 250 300 268L320 468Q326 542 258 546H122Q54 542 60 468L80 268Q80 250 96 250Z'), cm)
CARAFE_HANDLE = mapped(svg_path('M300 300Q372 300 366 382Q360 442 314 452'), cm)
CARAFE_IN_TOP, CARAFE_IN_BOT = cm(0, 268)[1], PULT_Y - 0.012

KK = 0.00068                    # kuvalo: mockup jedinice -> S
K_PIV = (338, 222)
K_BODY = svg_path('M200 140Q205 90 260 85H420Q470 90 475 140L500 330Q505 360 470 360H205Q170 360 175 330Z')
K_LID = ellipse_pts(338, 84, 92, 14)
K_KNOB = rrect_pts(318, 50, 40, 30, 10)
K_HANDLE = svg_path('M475 150Q560 158 548 262Q538 322 496 332')
K_SPOUT = svg_path('M190 300C120 300 110 200 60 170C40 158 22 160 8 168')
K_TIP = (8, 168)
TIP_POUR = (0.533, 0.372)       # vrh grlica pri sipanju (storyboard 1, koordinate)


def _k_rot(u, v, deg):
    du, dv = u - K_PIV[0], v - K_PIV[1]
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return du * c + dv * s, -du * s + dv * c     # okret suprotno od kazaljke na ekranu (grlic ide dole)


_tx, _ty = _k_rot(*K_TIP, 32)
K_PX, K_PY = TIP_POUR[0] - _tx * KK, TIP_POUR[1] - _ty * KK


def kettle_tilt(g):
    if g < 164:
        return 12 + 20 * smooth((g - 110) / 10)
    return 32 - 20 * smooth((g - 164) / 12)


def km(deg):
    def f(u, v):
        x, y = _k_rot(u, v, deg)
        return (K_PX + x * KK, K_PY + y * KK)
    return f


def carafe_level(g):
    return pw([(136, 0.0), (164, 0.26), (176, 0.30), (192, 0.38)], g)


def kafa_y(g):
    return CARAFE_IN_BOT - carafe_level(g) * (CARAFE_IN_BOT - CARAFE_IN_TOP)


def bed_top(g):
    """Gornja povrsina kafe u filteru (y u kadru POUR)."""
    mound = 0.044 * clamp((g - 74) / 36) - 0.004 * smooth((g - 110) / 8)
    water = 0.06 * smooth((g - 116) / 48) - 0.045 * smooth((g - 164) / 28)
    return BED_Y0 - mound - max(0.0, water)


def cone_inner():
    return [(0.5 - CONE_TOP_HW + 0.008, V60['y']), (0.5 + CONE_TOP_HW - 0.008, V60['y']),
            (0.5 + CONE_BOT_HW - 0.004, CONE_BOT_Y), (0.5 - CONE_BOT_HW + 0.004, CONE_BOT_Y)]


def draw_pour(c, g):
    # bokal i kafa u njemu
    c.draw([('poly', CARAFE)], POUR_PH, 0.6)
    c.draw([('line', CARAFE_HANDLE, 16 * CK_X)], POUR_PH, 0.7)
    lv = carafe_level(g)
    if lv > 0:
        ky = kafa_y(g)
        c.draw([('poly', [(0.3, ky), (0.7, ky), (0.7, CARAFE_IN_BOT), (0.3, CARAFE_IN_BOT)])], COFFEE, 0.72, clip=[('poly', CARAFE)])
        c.draw([('poly', [(0.3, ky - 0.002), (0.7, ky - 0.002), (0.7, ky + 0.002), (0.3, ky + 0.002)])], CREAM_LIGHT, 0.35,
               clip=[('poly', CARAFE)])
    # V60: prsten ispod, kupa, papir, ivica, otvor
    c.draw([('poly', rrect_pts(0.5 - 86 * KD, CONE_BOT_Y, 172 * KD, 22 * KD, 6 * KD))], POUR_PH)
    c.draw([('poly', [(0.5 - CONE_TOP_HW, V60['y']), (0.5 + CONE_TOP_HW, V60['y']),
                      (0.5 + CONE_BOT_HW, CONE_BOT_Y), (0.5 - CONE_BOT_HW, CONE_BOT_Y)])], POUR_PH, 0.9)
    paper_top = [(0.5 - 0.108 + 0.216 * k / 28, 0.418 + (0.004 if k % 2 else 0.0)) for k in range(29)]
    c.draw([('poly', [(0.5 - 0.118, V60['y'])] + paper_top + [(0.5 + 0.118, V60['y'])])], WHITE, 0.42)
    c.draw([('poly', ellipse_pts(V60['x'], V60['y'], V60['rx'], V60['ry'], 0, 40))], POUR_PH)
    c.draw([('poly', ellipse_pts(V60['x'], V60['y'], V60['rx'] - 0.014, V60['ry'] - 0.006, 0, 40))], (0x8E, 0x81, 0x77), 0.9)
    # kafa u filteru (staklena kupa, vidi se kroz nju)
    top = bed_top(g)
    if top < BED_Y0 - 0.001:
        surf = [(0.5 + dx / 20 * 0.13, top + 0.008 * (dx / 20) ** 2) for dx in range(-20, 21)]
        c.draw([('poly', surf + [(0.63, CONE_BOT_Y), (0.37, CONE_BOT_Y)])], GROUNDS, 0.85, clip=[('poly', cone_inner())])
        if g >= 120:
            foam = [(x, y - 0.0025) for x, y in surf] + [(x, y + 0.0025) for x, y in reversed(surf)]
            c.draw([('poly', foam)], (0xD6, 0xB4, 0x8C), 0.55, clip=[('poly', cone_inner())])
    # kapanje iz V60 u bokal (G132-G192)
    if 132 <= g and lv >= 0 and g <= 192:
        y_end = kafa_y(g) if lv > 0 else CARAFE_IN_BOT
        y0 = CONE_BOT_Y + 22 * KD
        if 140 <= g <= 170:
            c.draw([('line', [(0.5, y0), (0.5, y_end)], 0.0028)], COFFEE, 0.8)
        else:
            drops = []
            step = 2 if g < 140 else 4
            first = 132 if g < 140 else 172
            for e in range(first, int(g) + 1, step):
                t = g - e
                y = y0 + 0.02 * t + 0.004 * t * t
                if y < y_end:
                    drops.append(('circle', 0.5, y, 0.0032))
            c.draw(drops, COFFEE, 0.85)
    # cetiri zrna na pultu
    beans = [('poly', ellipse_pts(x, PULT_Y - 0.0085, 0.0115, 0.0085, r, 20))
             for x, r in ((0.695, 15), (0.728, -20), (0.762, 38), (0.795, 6))]
    c.draw(beans, BEAN)
    # kuvalo
    f = km(kettle_tilt(g))
    c.draw([('line', mapped(K_HANDLE, f), 22 * KK)], POUR_PH)
    c.draw([('line', mapped(K_SPOUT, f), 13 * KK)], POUR_PH)
    c.draw([('poly', mapped(K_BODY, f))], POUR_PH)
    c.draw([('poly', mapped(K_LID, f))], (0xA3, 0x96, 0x8B), 0.85)
    c.draw([('poly', mapped(K_KNOB, f))], POUR_PH)
    # voda iz grlica: krene G112, udari u kupu G116, prestaje G170 (rep pada 4 kadra)
    head, tail = clamp((g - 112) / 4), clamp((g - 170) / 4)
    if head > tail:
        x0, y0 = f(*K_TIP)
        x1, y1 = 0.5, top
        n = 24
        pts = []
        for k in range(n + 1):
            s = tail + (head - tail) * k / n
            pts.append((x0 + (x1 - x0) * (1 - (1 - s) ** 2), y0 + (y1 - y0) * s * s))
        c.draw([('line', pts, 0.0075)], CREAM_LIGHT, 0.75)
    # mlaz mlevene kafe iz GRIND sveta (y_pour = y_grind - 1), do povrsine u filteru
    c.draw([('circle', x, y - 1, r) for x, y, r in grounds_at(g) if y - 1 < top], GROUNDS)
    c.label(0.275, 0.915, f'G{g:03d} · PLATZHALTER')


# ---------------- SIP ----------------
STO_Y = 0.78                    # sidro `sto_y`
SK = 0.36 / 392                 # solja iz mockupa: telo 392 jedinice = 0,36 S
DROP = 0.1875                   # 4,5 cm iznad stola u kadru od 24 cm
MUG_BODY = svg_path('M40 40Q40 20 62 20H410Q432 20 432 40L414 398Q408 450 348 450H124Q64 450 58 398Z')
MUG_HANDLE = svg_path('M418 112Q512 100 506 220Q500 332 408 332')
DRIPS = [(0, 42), (58, 56), (118, 34), (178, 62), (236, 46), (300, 54), (352, 38)]   # (polozaj, duzina) curenja glazure


def sip_drop(s):
    t = clamp((s - 1) / 13)
    return -DROP * (1 - t) ** 3                     # ease-out, sleti na S14


def sip_turn(s):
    return pw([(1, 28.0), (14, 3.0), (30, 0.0)], s)  # ruka 28 stepeni unazad -> konacni ugao


def draw_sip(c, s):
    dy, phi = sip_drop(s), sip_turn(s)
    land = 1 - abs(dy) / DROP

    def sm(u, v):
        return (0.5 + (u - 236) * SK, STO_Y - (450 - v) * SK + dy)

    # senka na stolu: skuplja se i tamni kako solja silazi
    c.draw([('poly', ellipse_pts(0.5, STO_Y + 2 * SK, 250 * SK * (0.72 + 0.28 * land), 16 * SK, 0, 36))], INK_DEEP, 0.1 + 0.18 * land)
    # drska: sabijena dok je okrenuta unazad
    hs = 1 - 0.55 * phi / 28

    def hm(u, v):
        return sm(418 + (u - 418) * hs, v)
    c.draw([('line', mapped(MUG_HANDLE, hm), 34 * SK)], SIP_PH)
    body = mapped(MUG_BODY, sm)
    c.draw([('poly', body)], SIP_PH)
    # glazura sa curenjima, klizi sa okretom
    shift = phi * 3.4
    edge = []
    for u in range(20, 456, 4):
        v = 150.0
        for pos, ln in DRIPS:
            dx = (u - pos - shift - 40) % 420 - 210
            v = max(v, 150 + ln * math.exp(-(dx / 16) ** 2))
        edge.append((u, v))
    glaze = mapped([(20, 0), (456, 0)] + edge[::-1], sm)
    c.draw([('poly', glaze)], WHITE, 0.2, clip=[('poly', body)])
    c.draw([('poly', ellipse_pts(*sm(236, 30), 196 * SK, 20 * SK, 0, 40))], (0x2A, 0x1A, 0x12), 0.35)
    c.label(0.215, 0.822, f'S{s:03d} · PLATZHALTER')


DRAW = {'grind': draw_grind, 'pour': draw_pour, 'sip': draw_sip}


def render(seq_id, g, px):
    c = Canvas(SPEC[seq_id]['crop'], px)
    DRAW[seq_id](c, g)
    return c.result()


# ---------------- manifest i zapis ----------------
def manifest(seq_id):
    sp = SPEC[seq_id]
    x0, y0, cw, ch = sp['crop']
    sets = {}
    for lv, px in LEVELS.items():
        count, every = sp['counts'][lv]
        sets[lv] = {'px': px, 'w': round(cw * px), 'h': round(ch * px), 'count': count, 'every': every}
    anchors = {'osa_x': 0.5}
    if seq_id == 'grind':
        anchors['otvor'] = {'x': 0.5, 'y': SPOUT_Y}
    elif seq_id == 'pour':
        anchors['ivica_v60'] = dict(V60)
        anchors['pult_y'] = PULT_Y
        anchors['kafa_y'] = {'from': 177, 'values': [round(kafa_y(g), 4) for g in range(177, 193)]}
    else:
        anchors['sto_y'] = STO_Y
    return {
        'id': seq_id, 'version': VERSION, 'placeholder': True, 'clock': sp['clock'],
        'g_od': sp['g_od'], 'g_do': sp['g_do'], 'fps': 30,
        'full': {'W': sp['full'][0], 'H': sp['full'][1]},
        'crop': {'x0': x0, 'y0': y0, 'w': cw, 'h': ch},
        'sets': sets, 'poster': sp['poster'],
        'steps': [{'name': n, 'from': a, 'to': b} for n, a, b in sp['steps']],
        'anchors': anchors,
        'units': 'S (stranica kvadrata kadra), od gornjeg levog ugla punog kadra; steps i kafa_y u kadrovima sata',
        'generator': 'KafaSkrol/scripts/placeholder_seq.py',
    }


def check_target(folder, force):
    man = folder / 'seq.json'
    data = None
    if man.exists():
        try:
            data = json.loads(man.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            data = None
    if isinstance(data, dict) and data.get('placeholder') is False:
        sys.exit(f'{folder}: seq.json ima "placeholder": false (pravi render). Ne prepisujem, ni sa --force.')
    if isinstance(data, dict) and data.get('placeholder') is True:
        return
    if folder.exists() and any(folder.iterdir()) and not force:
        sys.exit(f'{folder}: nije prazan, a nema seq.json sa "placeholder": true. Prepisuje se samo sa --force.')


def clear(folder):
    for lv in ('l', 'd', 'm'):
        sub = folder / lv
        if sub.is_dir():
            for f in sub.glob('*.webp'):
                f.unlink()
            if lv == 'l' and not any(sub.iterdir()):
                sub.rmdir()
    for f in list(folder.glob('poster-*.webp')) + [folder / 'seq.json']:
        if f.exists():
            f.unlink()


def save_webp(img, path):
    img.save(path, 'WEBP', quality=QUALITY, alpha_quality=ALPHA_QUALITY, method=6)


def build(root, seq_id):
    sp, folder = SPEC[seq_id], root / seq_id
    clear(folder)
    sizes = {}
    for lv, px in LEVELS.items():
        (folder / lv).mkdir(parents=True, exist_ok=True)
        count, every = sp['counts'][lv]
        total = 0
        for k in range(1, count + 1):
            path = folder / lv / f'{k:04d}.webp'
            save_webp(render(seq_id, sp['g_od'] + (k - 1) * every, px), path)
            total += path.stat().st_size
        sizes[lv] = (count, total)
    for name, (lv, g) in sp['poster_files'].items():
        save_webp(render(seq_id, g, LEVELS[lv]), folder / name)
        sizes[name] = (1, (folder / name).stat().st_size)
    (folder / 'seq.json').write_text(json.dumps(manifest(seq_id), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return sizes


# ---------------- kompozit sava ----------------
def composite(root, g, out):
    repo = pathlib.Path(__file__).resolve().parents[2]
    out = pathlib.Path(out).resolve()
    if repo == out or repo in out.parents:
        sys.exit(f'{out}: kompozit ide u privremeni folder, ne u repo.')
    mans = {}
    for sid in ('grind', 'pour'):
        mf = root / sid / 'seq.json'
        if not mf.exists():
            sys.exit(f'{mf} ne postoji: prvo napravi kadrove.')
        mans[sid] = json.loads(mf.read_text(encoding='utf-8'))
    frames = {}
    for sid, m in mans.items():
        st = m['sets']['d']
        k = (g - m['g_od']) / st['every'] + 1
        if k != int(k) or not 1 <= k <= st['count']:
            sys.exit(f'G{g} nije u nivou d sekvence {sid} (G{m["g_od"]}-G{m["g_do"]}).')
        with Image.open(root / sid / 'd' / f'{int(k):04d}.webp', formats=['WEBP']) as im:
            frames[sid] = im.convert('RGBA')
    px = mans['grind']['sets']['d']['px']
    gx0 = round(mans['grind']['crop']['x0'] * px)
    px0 = round(mans['pour']['crop']['x0'] * px)
    # sajt: GRIND platno se sece na gornjoj ivici POUR scene, POUR je prislonjen uz vrh svoje scene
    full = Image.new('RGBA', (px, 2 * px), CREAM + (255,))
    full.paste(TERRACOTTA + (255,), (0, px, px, 2 * px))
    full.alpha_composite(frames['grind'].crop((0, 0, frames['grind'].width, px)), dest=(gx0, 0))
    full.alpha_composite(frames['pour'], dest=(px0, px))
    d = ImageDraw.Draw(full)
    for x0 in (0, px - 60):
        d.line([(x0, px), (x0 + 60, px)], fill=INK_DEEP + (255,), width=3)
    # uvecan sav (x 0,42-0,58 S, +-0,2 S oko granice), 3x
    zx0, zx1, zy0, zy1 = round(0.42 * px), round(0.58 * px), round(0.8 * px), round(1.2 * px)
    zoom = full.crop((zx0, zy0, zx1, zy1)).resize(((zx1 - zx0) * 3, (zy1 - zy0) * 3), Image.NEAREST)
    canvas = Image.new('RGBA', (px + 24 + zoom.width, 2 * px), (255, 255, 255, 255))
    canvas.paste(full, (0, 0))
    canvas.paste(zoom, (px + 24, 0))
    d = ImageDraw.Draw(canvas)
    ys = (px - zy0) * 3
    for x0 in (px + 24, px + 24 + zoom.width - 40):
        d.line([(x0, ys), (x0 + 40, ys)], fill=INK_DEEP + (255,), width=3)
    d.text((px + 24, (zy1 - zy0) * 3 + 20), f'G{g:03d}  sav 3x  (x 0,42-0,58 S)', font=ImageFont.load_default(size=28),
           fill=INK_DEEP + (255,))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert('RGB').save(out, 'PNG')
    # brojevi: produzetak GRIND kadra (y 1-1,25 S) i vrh POUR kadra moraju da pokazu iste tacke na istom mestu
    win = (round(0.46 * px), round(0.54 * px))
    ga = frames['grind'].getchannel('A').crop((win[0] - gx0, px, win[1] - gx0, px + round(0.15 * px)))
    best = None
    for sh in range(-8, 9):
        pa = frames['pour'].getchannel('A').crop((win[0] - px0, sh, win[1] - px0, sh + round(0.15 * px)))
        hist = ImageChops.difference(ga, pa).histogram()
        diff = sum(i * n for i, n in enumerate(hist)) / max(1, sum(hist))
        if best is None or diff < best[1]:
            best = (sh, diff)
        if sh == 0:
            at0 = diff
    print(f'kompozit: {out}')
    print(f'sav G{g}: najbolji vertikalni pomak POUR prema GRIND produzetku = {best[0]} px '
          f'(srednja razlika alfe {best[1]:.2f}/255; na 0 px {at0:.2f}/255)')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('root', help='KafaSkrol/public/media/seq')
    ap.add_argument('--force', action='store_true', help='prepisi folder bez naseg seq.json (nikad pravi render)')
    ap.add_argument('--only', nargs='+', choices=list(SPEC), help='samo ove sekvence')
    ap.add_argument('--composite', nargs=2, metavar=('G', 'IZLAZ'), help='PNG sava GRIND/POUR za kadar G (van repoa)')
    a = ap.parse_args()
    root = pathlib.Path(a.root).resolve()
    if a.composite:
        composite(root, int(a.composite[0].lstrip('Gg')), a.composite[1])
        return
    ids = a.only or list(SPEC)
    for sid in ids:
        check_target(root / sid, a.force)
    grand = 0
    for sid in ids:
        sizes = build(root, sid)
        for name, (n, b) in sizes.items():
            grand += b
            print(f'{sid:5s} {name:14s} {n:4d} fajl(ova) {b / 1024:8.1f} KB' + (f'  (prosek {b / n / 1024:.1f} KB)' if n > 1 else ''))
    print(f'ukupno {grand / 1024 / 1024:.2f} MB')


if __name__ == '__main__':
    main()
