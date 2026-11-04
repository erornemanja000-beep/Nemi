"""Bojanka za DON'S Eisdiele: 5 strana A4, crteži su vektorske linije pisane kodom.

Upotreba:
    python3 scripts/bojanka/bojanka.py studio/dons-bojanka

Pravi <izlaz>/dons-malbuch-a4.pdf i pregled svake strane u <izlaz>/vorschau/.
Treba: node + playwright (već su u okruženju) i pdftoppm.
"""
import math
import os
import re
import subprocess
import sys
import tempfile

KOREN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTOVI = os.path.join(KOREN, "sajt", "src", "assets", "fonts", "fonts.css")

W, H = 1000, 1414  # A4 uspravno, 1 jedinica = 0,21 mm
INK = "#1d1d1b"

# ---------------------------------------------------------------- putanje

_TOK = re.compile(r"[MLCQZ]|-?\d*\.?\d+")


def tp(d, s=1.0, x=0.0, y=0.0, rot=0.0, flip=False):
    """Pomeri, uveća, okrene i preslika putanju (samo apsolutne M L C Q Z)."""
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out, nums = [], []

    def flush():
        for i in range(0, len(nums), 2):
            px, py = nums[i], nums[i + 1]
            if flip:
                px = -px
            px, py = px * s, py * s
            out.append(f"{px * ca - py * sa + x:.1f} {px * sa + py * ca + y:.1f}")
        nums.clear()

    for t in _TOK.findall(d):
        if t.isalpha():
            flush()
            out.append(t)
        else:
            nums.append(float(t))
    flush()
    return " ".join(out)


class Pero:
    """Crta u lokalnim koordinatama; debljina linije ostaje ista na svakoj veličini."""

    def __init__(self, s=1.0, x=0.0, y=0.0, rot=0.0, flip=False):
        self.s, self.x, self.y, self.rot, self.flip = s, x, y, rot, flip
        self.svg = []

    def pt(self, px, py):
        d = tp(f"M {px} {py}", self.s, self.x, self.y, self.rot, self.flip)
        a, b = d.split()[1:3]
        return float(a), float(b)

    def p(self, d, k="l"):
        self.svg.append(f'<path class="{k}" d="{tp(d, self.s, self.x, self.y, self.rot, self.flip)}"/>')

    def krug(self, cx, cy, r, k="l"):
        x, y = self.pt(cx, cy)
        self.svg.append(f'<circle class="{k}" cx="{x:.1f}" cy="{y:.1f}" r="{r * self.s:.1f}"/>')

    def elipsa(self, cx, cy, rx, ry, ugao=0, k="l"):
        x, y = self.pt(cx, cy)
        u = (-ugao if self.flip else ugao) + self.rot
        self.svg.append(
            f'<ellipse class="{k}" cx="{x:.1f}" cy="{y:.1f}" rx="{rx * self.s:.1f}" '
            f'ry="{ry * self.s:.1f}" transform="rotate({u:.1f} {x:.1f} {y:.1f})"/>'
        )

    def jedinica(self, d, s, cx, cy, k="l", rot=0, flip=False):
        """Putanja zadata u jediničnim merama (poluprečnik 1) postavljena u lokalne koordinate."""
        self.p(tp(d, s, cx, cy, rot, flip), k)

    def dodaj(self, tekst):
        self.svg.append(tekst)

    def __str__(self):
        return "\n".join(self.svg)


_klip = [0]


def novi_id(ime):
    _klip[0] += 1
    return f"{ime}{_klip[0]}"


# ---------------------------------------------------------------- delovi

KUGLA = (
    "M -1 0.2 C -1.08 -0.6 -0.55 -1.02 0 -1.02 C 0.55 -1.02 1.08 -0.6 1 0.2 "
    "C 0.98 0.38 0.82 0.42 0.74 0.3 C 0.66 0.62 0.42 0.66 0.38 0.36 "
    "C 0.28 0.48 0.1 0.48 0.04 0.34 C -0.04 0.56 -0.3 0.58 -0.34 0.34 "
    "C -0.46 0.48 -0.68 0.46 -0.72 0.3 C -0.84 0.44 -1 0.38 -1 0.2 Z"
)
KUGLA_SJAJ = "M -0.62 -0.42 C -0.52 -0.66 -0.32 -0.78 -0.12 -0.8"

SRCE = (
    "M 0 0.42 C -0.62 0 -0.6 -0.58 -0.27 -0.6 C -0.12 -0.6 0 -0.5 0 -0.36 "
    "C 0 -0.5 0.12 -0.6 0.27 -0.6 C 0.6 -0.58 0.62 0 0 0.42 Z"
)

LATICA = "M 0 1 C -0.86 0.62 -0.92 -0.62 -0.4 -0.9 C -0.2 -1 -0.06 -0.88 0 -0.74 C 0.06 -0.88 0.2 -1 0.4 -0.9 C 0.92 -0.62 0.86 0.62 0 1 Z"
LIST = "M -1 0 C -0.5 -0.55 0.5 -0.55 1 0 C 0.5 0.55 -0.5 0.55 -1 0 Z"


def zvezda_d(r):
    tacke = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.48
        tacke.append(f"{rr * math.cos(a):.2f} {rr * math.sin(a):.2f}")
    return "M " + " L ".join(tacke) + " Z"


def kugla(pero, cx, cy, r, sjaj=True):
    pero.jedinica(KUGLA, r, cx, cy)
    if sjaj:
        pero.jedinica(KUGLA_SJAJ, r, cx, cy, "d")


def kornet(pero, cx, top, w, h, korak=None):
    """Kornet sa vafl mrežom; vrh kornjeta je na (cx, top)."""
    half = w / 2
    obris = f"M {cx - half} {top} L {cx + half} {top} L {cx + 9} {top + h - 8} Q {cx} {top + h + 6} {cx - 9} {top + h - 8} Z"
    pero.p(obris)
    kid = novi_id("k")
    pero.dodaj(f'<clipPath id="{kid}"><path d="{tp(obris, pero.s, pero.x, pero.y, pero.rot, pero.flip)}"/></clipPath>')
    korak = korak or w / 3.6
    linije = []
    n = int((w + h) / korak) + 2
    for i in range(-n, n + 1):
        x0 = cx + i * korak
        linije.append(f"M {x0 - h * 0.62} {top - 10} L {x0 + h * 0.62} {top + h + 10}")
        linije.append(f"M {x0 + h * 0.62} {top - 10} L {x0 - h * 0.62} {top + h + 10}")
    d = " ".join(tp(l, pero.s, pero.x, pero.y, pero.rot, pero.flip) for l in linije)
    pero.dodaj(f'<g clip-path="url(#{kid})"><path class="d" d="{d}"/></g>')
    pero.p(obris, "o")  # obris preko mreže, da ivica ostane čista
    # obod kornjeta
    pero.p(
        f"M {cx - half - 10} {top - 4} L {cx + half + 10} {top - 4} Q {cx + half + 12} {top + 22} {cx + half - 1} {top + 24} "
        f"L {cx - half + 1} {top + 24} Q {cx - half - 12} {top + 22} {cx - half - 10} {top - 4} Z"
    )


def srce(pero, cx, cy, s, rot=0):
    pero.jedinica(SRCE, s, cx, cy, rot=rot)


def zvezda(pero, cx, cy, r, rot=0):
    pero.jedinica(zvezda_d(1), r, cx, cy, rot=rot)


def mrvica(pero, cx, cy, duz, ugao):
    """Šarena mrvica (posip) kao mala kapsula."""
    a = math.radians(ugao)
    dx, dy = math.cos(a) * duz / 2, math.sin(a) * duz / 2
    x1, y1 = pero.pt(cx - dx, cy - dy)
    x2, y2 = pero.pt(cx + dx, cy + dy)
    pero.dodaj(
        f'<line class="m1" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
        f'<line class="m2" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
    )


def oblak(pero, cx, cy, s):
    pero.jedinica(
        "M -1 0.35 C -1.25 0.35 -1.3 -0.15 -0.95 -0.2 C -0.95 -0.6 -0.45 -0.75 -0.25 -0.45 "
        "C -0.1 -0.85 0.55 -0.85 0.6 -0.35 C 1 -0.45 1.3 0.05 1 0.35 Z",
        s, cx, cy,
    )


def sunce(pero, cx, cy, r):
    for i in range(10):
        a = math.radians(i * 36 + 18)
        x1, y1 = cx + math.cos(a) * (r + 14), cy + math.sin(a) * (r + 14)
        x2, y2 = cx + math.cos(a) * (r + 40), cy + math.sin(a) * (r + 40)
        pero.p(f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}", "d")
    pero.krug(cx, cy, r)
    pero.krug(cx - r * 0.35, cy - r * 0.1, r * 0.09, "k")
    pero.krug(cx + r * 0.35, cy - r * 0.1, r * 0.09, "k")
    pero.p(f"M {cx - r * 0.4} {cy + r * 0.25} Q {cx} {cy + r * 0.6} {cx + r * 0.4} {cy + r * 0.25}", "d")


def cvet(pero, cx, cy, r):
    for i in range(5):
        a = math.radians(-90 + i * 72)
        pero.krug(cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.62, r * 0.48)
    pero.krug(cx, cy, r * 0.38)


# ---------------------------------------------------------------- Don (francuski buldog)


def don_glava(pero, jezik=False, pogled=(0, 0)):
    """Glava sa centrom u (0, 0), širina oko 400, vrhovi ušiju na y = -275."""
    for flip in (False, True):
        u = Pero(pero.s, pero.x, pero.y, pero.rot, pero.flip != flip)
        u.p("M -190 -36 C -222 -116 -232 -196 -206 -236 C -180 -272 -124 -262 -98 -218 C -78 -184 -62 -152 -48 -124 Z")
        u.p("M -170 -82 C -192 -138 -198 -192 -182 -214 C -166 -234 -136 -226 -118 -196 C -104 -172 -94 -152 -86 -134 C -112 -110 -142 -94 -170 -82 Z", "d")
        pero.dodaj(str(u))
    # glava
    pero.p(
        "M 0 -136 C 122 -136 206 -94 214 6 C 222 92 180 152 106 172 C 54 184 -54 184 -106 172 "
        "C -180 152 -222 92 -214 6 C -206 -94 -122 -136 0 -136 Z"
    )
    # bore na čelu
    pero.p("M -30 -78 Q 0 -92 30 -78", "d")
    for sgn in (-1, 1):
        # obrve (svetle tačke iznad očiju)
        pero.elipsa(sgn * 78, -62, 22, 12, k="d")
        # nabori obraza
        pero.p(f"M {sgn * 128} 70 C {sgn * 120} 112 {sgn * 92} 138 {sgn * 58} 144", "d")
        # oči
        pero.krug(sgn * 74, 0, 38)
        px, py = sgn * 74 + pogled[0], 4 + pogled[1]
        pero.krug(px, py, 24, "k")
        pero.krug(px - 8, py - 9, 8, "b")
        pero.krug(px + 9, py + 8, 3.5, "b")
    pero.p("M -28 -12 Q 0 -26 28 -12", "d")
    # nos
    pero.p("M -44 36 C -44 14 44 14 44 36 C 44 62 16 76 0 76 C -16 76 -44 62 -44 36 Z", "k")
    pero.elipsa(-15, 30, 11, 5, k="b")
    # usta i obrazi
    pero.p("M 0 76 L 0 94", "d")
    pero.p("M -64 98 C -42 120 -14 114 0 94 C 14 114 42 120 64 98", "d")
    if jezik:
        don_jezik(pero)


def don_jezik(pero):
    pero.p("M 6 106 C 30 110 60 126 64 158 C 68 188 36 198 22 180 C 12 164 6 136 6 106 Z")
    pero.p("M 30 120 Q 40 146 38 172", "d")


def don_telo(pero, sapa_gore=False):
    """Telo psa koji sedi, ispod glave (glava se crta posle)."""
    for flip in (False, True):
        u = Pero(pero.s, pero.x, pero.y, pero.rot, pero.flip != flip)
        # zadnja noga
        u.p("M -140 290 C -240 280 -268 384 -214 420 C -180 438 -128 428 -118 400 Z")
        pero.dodaj(str(u))
    pero.p("M -150 110 C -202 190 -216 300 -196 402 C -190 428 190 428 196 402 C 216 300 202 190 150 110 Z")
    pero.p("M -62 168 C -46 242 -20 312 0 348 C 20 312 46 242 62 168 C 32 154 -32 154 -62 168 Z", "d")
    strane = (False,) if sapa_gore else (False, True)
    for flip in strane:
        u = Pero(pero.s, pero.x, pero.y, pero.rot, pero.flip != flip)
        u.p("M -108 236 C -114 300 -114 360 -110 404", "d")
        u.p("M -46 300 C -46 350 -48 380 -50 404", "d")
        u.elipsa(-80, 410, 50, 25)
        u.p("M -94 434 L -94 420", "d")
        u.p("M -66 434 L -66 420", "d")
        pero.dodaj(str(u))


def ivica_tela(y):
    """x desne ivice tela (Bezier iz don_telo) za zadato y."""
    p0, p1, p2, p3 = (150, 110), (202, 190), (216, 300), (196, 402)
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        yy = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]
        lo, hi = (t, hi) if yy < y else (lo, t)
    return (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0]


def sapa(pero, cx, cy, ugao=0):
    pero.elipsa(cx, cy, 44, 32, ugao)
    a = math.radians(ugao)
    for t in (-12, 12):
        x0, y0 = cx + math.cos(a) * t, cy + math.sin(a) * t
        x1, y1 = x0 - math.sin(a) * -30, y0 + math.cos(a) * -30
        x2, y2 = x0 - math.sin(a) * -14, y0 + math.cos(a) * -14
        pero.p(f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}", "d")


# ---------------------------------------------------------------- strana


def naslov(tekst, y=172, vel=104):
    return (
        f'<text class="t" x="{W / 2}" y="{y}" text-anchor="middle" font-size="{vel}">{tekst}</text>'
    )


def podnozje():
    return (
        '<text class="f1" x="70" y="1352">Gemalt von:</text>'
        '<path class="d" d="M 232 1356 L 560 1356"/>'
        '<text class="f2" x="930" y="1338" text-anchor="end">DON’S <tspan class="f3">eisdiele</tspan></text>'
        '<text class="f4" x="930" y="1366" text-anchor="end">Geiselbergstraße 24 · 1110 Wien</text>'
    )


def strana(sadrzaj):
    return f'<section class="s"><svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{sadrzaj}{podnozje()}</svg></section>'


# 1 ---------------------------------------------------------------- Don liebt Eis!


def strana1():
    p = Pero()
    p.dodaj(naslov("Don liebt Eis!"))
    p.dodaj('<text class="f1" x="500" y="232" text-anchor="middle">Das Malbuch von DON’S Eisdiele</text>')
    don = Pero(1.18, 500, 640)
    don_telo(don, sapa_gore=True)
    don_glava(don, pogled=(10, 12))
    # kornet koji Don drži u podignutoj šapi
    kornet(don, 96, 262, 112, 196)
    kugla(don, 96, 232, 64)
    don_jezik(don)
    ya, yb = 270, 346
    xa, xb = ivica_tela(ya), ivica_tela(yb)
    don.p(f"M {xa:.1f} {ya} C 180 {ya} 150 286 112 298 L 112 352 C 150 358 182 352 {xb:.1f} {yb} Z")
    don.elipsa(104, 325, 36, 33)
    for yy in (312, 338):
        don.p(f"M 70 {yy} L 86 {yy}", "d")
    p.dodaj(str(don))
    # ukrasi
    for (x, y, r, u) in [(120, 380, 34, -10), (880, 360, 30, 12), (110, 1120, 28, 8), (895, 1150, 36, -6)]:
        zvezda(p, x, y, r, u)
    for (x, y, s, u) in [(170, 560, 44, -12), (850, 560, 40, 14), (150, 830, 36, 8)]:
        srce(p, x, y, s, u)
    for (x, y, d, u) in [(180, 290, 34, 30), (800, 270, 34, -40), (860, 830, 34, 60), (120, 980, 34, -20),
                         (880, 990, 34, 20), (230, 1210, 34, 70), (790, 1240, 34, -15)]:
        mrvica(p, x, y, d, u)
    return strana(str(p))


# 2 ---------------------------------------------------------------- Der Eisladen


def strana2():
    p = Pero()
    p.dodaj(naslov("Der Eisladen"))
    sunce(p, 892, 108, 40)
    oblak(p, 118, 110, 62)
    # fasada
    p.p("M 80 250 L 920 250 L 920 1170 L 80 1170 Z")
    # gornji prozori sa saksijama
    for x0 in (170, 640):
        p.p(f"M {x0} 280 L {x0 + 190} 280 L {x0 + 190} 420 L {x0} 420 Z")
        p.p(f"M {x0 + 95} 280 L {x0 + 95} 420 M {x0} 330 L {x0 + 190} 330", "d")
        for i, cx in enumerate((x0 + 30, x0 + 95, x0 + 160)):
            p.p(f"M {cx} 440 L {cx} {412 - (i % 2) * 14}", "d")
            cvet(p, cx, 400 - (i % 2) * 14, 26)
        p.p(f"M {x0 - 12} 420 L {x0 + 202} 420 L {x0 + 194} 458 L {x0 - 4} 458 Z")
    srce(p, 500, 352, 46)
    # venac
    p.p("M 66 482 L 934 482 L 934 512 L 66 512 Z")
    # natpis
    p.dodaj('<text class="z" x="500" y="622" text-anchor="middle" font-size="138">DON’S</text>')
    # okvir izloga
    p.p("M 140 650 L 860 650 L 860 1120 L 140 1120 Z")
    # vrata
    p.p("M 172 680 L 372 680 L 372 1120 L 172 1120 Z")
    p.p("M 196 704 L 348 704 L 348 1066 L 196 1066 Z")
    p.p("M 330 860 L 330 940", "l")
    p.p("M 230 770 L 270 734 L 310 770", "d")
    p.krug(270, 732, 6, "k")
    p.p("M 214 770 L 326 770 L 326 826 L 214 826 Z")
    p.dodaj('<text class="f5" x="270" y="809" text-anchor="middle">OFFEN</text>')
    # izlog
    p.p("M 396 680 L 832 680 L 832 1010 L 396 1010 Z")
    for x0 in (424, 562, 700):
        p.p(f"M {x0} 704 L {x0 + 108} 704 L {x0 + 108} 780 L {x0} 780 Z")
        for j, yy in enumerate((726, 744, 762)):
            p.p(f"M {x0 + 16} {yy} L {x0 + 92 - j * 14} {yy}", "d")
    # vitrina sa sladoledom
    for i in range(5):
        kugla(p, 462 + i * 76, 858, 34, sjaj=False)
    p.p("M 420 880 L 808 880 L 808 1010 L 420 1010 Z")
    p.p("M 420 880 L 444 836", "d")
    p.p("M 808 880 L 784 836", "d")
    p.p("M 444 836 L 784 836", "d")
    znak = Pero(0.16, 478, 948)
    don_glava(znak)
    p.krug(478, 945, 50)
    p.dodaj(str(znak))
    p.dodaj('<text class="z2" x="602" y="962" text-anchor="middle" font-size="42">DON’S</text>')
    # prag i rešetka
    p.p("M 384 1010 L 844 1010 L 844 1036 L 384 1036 Z")
    p.p("M 520 1056 L 700 1056 L 700 1096 L 520 1096 Z")
    for x in range(540, 700, 20):
        p.p(f"M {x} 1060 L {x} 1092", "d")
    # trotoar
    p.p("M 40 1170 L 960 1170 L 960 1250 L 40 1250 Z")
    for x in range(150, 960, 150):
        p.p(f"M {x} 1170 L {x - 30} 1250", "d")
    # tabla na trotoaru
    p.p("M 88 1240 L 112 1060 L 176 1060 L 200 1240", "l")
    p.p("M 100 1080 L 188 1080 L 188 1206 L 100 1206 Z")
    kugla(p, 144, 1116, 24, sjaj=False)
    kornet(p, 144, 1128, 40, 62)
    # Don sedi ispred izloga
    don = Pero(0.42, 800, 1030)
    don_telo(don)
    don_glava(don, pogled=(-8, 4))
    p.dodaj(str(don))
    return strana(str(p))


# 3 ---------------------------------------------------------------- Der Eisbecher


def slag(pero, cx, cy, s):
    """Šlag (Schlagobers) u tri sloja, odozdo nagore."""
    slojevi = [
        (1.0, 0.0),
        (0.78, -0.36),
        (0.54, -0.68),
    ]
    for sc, dy in slojevi:
        pero.jedinica(
            "M -1 0.28 C -1.12 0.02 -0.86 -0.24 -0.52 -0.18 C -0.24 -0.36 0.26 -0.36 0.54 -0.18 "
            "C 0.88 -0.24 1.12 0.02 1 0.28 C 0.62 0.44 -0.62 0.44 -1 0.28 Z",
            s * sc, cx, cy + dy * s,
        )
    pero.jedinica("M -0.26 -0.82 C -0.2 -1.02 -0.02 -1.16 0.12 -1.24 C 0.12 -1.08 0.26 -0.94 0.24 -0.82 Z", s, cx, cy)


def visnja(pero, cx, cy, r):
    pero.p(f"M {cx + 4} {cy - r + 4} C {cx + 14} {cy - r - 40} {cx + 34} {cy - r - 62} {cx + 54} {cy - r - 74}", "l")
    pero.jedinica(LIST, 26, cx + 46, cy - r - 52, rot=-40)
    pero.krug(cx, cy, r)
    pero.p(f"M {cx - r * 0.55} {cy - r * 0.2} Q {cx - r * 0.5} {cy - r * 0.55} {cx - r * 0.15} {cy - r * 0.62}", "d")


def strana3():
    p = Pero()
    p.dodaj(naslov("Der Eisbecher"))
    for (x, y, r, u) in [(130, 330, 36, -8), (880, 1120, 34, 10)]:
        zvezda(p, x, y, r, u)
    for (x, y, s, u) in [(880, 330, 46, 12), (120, 1110, 44, -10)]:
        srce(p, x, y, s, u)
    for (x, y, r) in [(110, 760, 40), (900, 780, 34)]:
        p.krug(x, y, r)
        p.p(f"M {x - r * 0.5} {y - r * 0.15} Q {x - r * 0.45} {y - r * 0.5} {x - r * 0.1} {y - r * 0.55}", "d")
    for (x, y, d, u) in [(170, 420, 34, 30), (860, 560, 34, -40), (150, 940, 34, 70), (860, 960, 34, -20)]:
        mrvica(p, x, y, d, u)
    p.dodaj('<g transform="translate(0 56)">')
    # vafl štapići i lepeza (iza kugli)
    for (x1, y1, x2, y2) in [(612, 560, 700, 336), (650, 576, 760, 382)]:
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln * 17, dx / ln * 17
        p.p(f"M {x1 + nx:.1f} {y1 + ny:.1f} L {x2 + nx:.1f} {y2 + ny:.1f} L {x2 - nx:.1f} {y2 - ny:.1f} L {x1 - nx:.1f} {y1 - ny:.1f} Z")
        p.elipsa(x2, y2, 17, 8, math.degrees(math.atan2(dy, dx)) + 90)
        for t in (0.25, 0.5, 0.75):
            ax, ay = x1 + dx * t, y1 + dy * t
            p.p(f"M {ax + nx:.1f} {ay + ny:.1f} L {ax - nx + dx * 0.08:.1f} {ay - ny + dy * 0.08:.1f}", "d")
    # lepeza od vafla
    lep = []
    for i in range(6):
        a = math.radians(-160 + i * 22)
        lep.append((340 + math.cos(a) * 190, 560 + math.sin(a) * 190))
    d = "M 340 560 " + " ".join(f"L {x:.1f} {y:.1f}" for (x, y) in lep)
    p.p(d + " Z")
    for (x, y) in lep[1:-1]:
        p.p(f"M 340 560 L {x:.1f} {y:.1f}", "d")
    # čaša: posuda
    p.p("M 236 700 L 764 700 C 760 850 640 960 560 984 L 440 984 C 360 960 240 850 236 700 Z")
    p.p("M 262 790 C 360 820 640 820 738 790", "d")
    p.p("M 300 880 C 400 905 600 905 700 880", "d")
    p.p("M 320 724 C 322 790 352 850 400 900", "d")
    # noga i postolje
    p.p("M 460 984 L 540 984 L 528 1130 L 472 1130 Z")
    p.p("M 330 1176 C 330 1130 670 1130 670 1176 C 670 1196 330 1196 330 1176 Z")
    # kugle
    kugla(p, 372, 640, 112)
    kugla(p, 628, 640, 112)
    kugla(p, 500, 548, 122)
    # preliv
    p.p("M 410 470 C 450 455 550 455 590 470 C 600 500 580 520 572 500 C 566 540 540 548 536 512 "
        "C 520 530 494 532 490 506 C 480 552 452 552 448 512 C 436 528 416 520 410 470 Z")
    slag(p, 500, 448, 112)
    for (x, y, u) in [(440, 430, 20), (520, 410, -30), (560, 440, 60), (470, 380, -60), (530, 360, 10), (420, 460, 80)]:
        mrvica(p, x, y, 22, u)
    visnja(p, 500, 288, 40)
    # jagoda na ivici
    p.p("M 780 690 C 830 690 846 742 820 790 C 806 816 784 822 772 800 C 752 764 744 716 780 690 Z")
    p.p("M 756 694 C 772 672 800 670 814 690 C 800 684 786 690 780 696 Z", "l")
    for (x, y) in [(790, 720), (808, 748), (786, 770), (800, 790)]:
        p.elipsa(x, y, 3, 5, k="k")
    p.dodaj("</g>")
    return strana(str(p))


# 4 ---------------------------------------------------------------- Die Eisrose


def ruza(pero, cx, cy, s):
    j = lambda d, k="l": pero.jedinica(d, s, cx, cy, k)
    # zadnje latice
    j("M -1 0.1 C -1.06 -0.5 -0.74 -0.86 -0.36 -0.8 C -0.22 -1.04 0.22 -1.04 0.36 -0.8 C 0.74 -0.86 1.06 -0.5 1 0.1 Z")
    j("M -0.72 -0.32 C -0.76 -0.6 -0.46 -0.78 -0.2 -0.66 C -0.06 -0.82 0.24 -0.8 0.32 -0.62 C 0.6 -0.7 0.8 -0.46 0.72 -0.3", "d")
    # srce ruže (spirala)
    j("M -0.56 -0.12 C -0.62 -0.5 -0.26 -0.66 0.02 -0.6 C 0.38 -0.54 0.56 -0.3 0.52 -0.08 C 0.2 0.04 -0.3 0.04 -0.56 -0.12 Z")
    j("M 0.08 -0.3 C -0.12 -0.32 -0.18 -0.16 0 -0.12 C 0.24 -0.08 0.3 -0.44 0 -0.48 C -0.34 -0.52 -0.44 -0.2 -0.3 -0.04", "d")
    # prednje latice
    j("M -0.36 -0.06 C -0.46 0.3 -0.3 0.7 0.04 0.96 C 0.36 0.66 0.46 0.26 0.3 -0.06 C 0.1 0.1 -0.16 0.1 -0.36 -0.06 Z")
    j("M -1 0.1 C -1 0.6 -0.56 0.96 0.04 0.96 C -0.3 0.7 -0.46 0.3 -0.36 -0.06 C -0.6 -0.12 -0.86 -0.06 -1 0.1 Z")
    j("M 1 0.1 C 1 0.6 0.6 0.96 0.04 0.96 C 0.36 0.66 0.46 0.26 0.3 -0.06 C 0.6 -0.12 0.86 -0.06 1 0.1 Z")


def strana4():
    p = Pero()
    p.dodaj(naslov("Die Eisrose"))
    # listovi iza
    p.jedinica(LIST, 120, 300, 790, rot=-24)
    p.p("M 196 838 C 260 800 340 780 404 744", "d")
    p.jedinica(LIST, 120, 700, 790, rot=24)
    p.p("M 804 838 C 740 800 660 780 596 744", "d")
    kornet(p, 500, 790, 320, 420)
    ruza(p, 500, 600, 236)
    # latice u vazduhu
    for (x, y, s, u) in [(170, 420, 46, -30), (840, 470, 52, 35), (150, 1060, 42, 20), (860, 1010, 48, -25), (790, 300, 36, 60)]:
        p.jedinica(LATICA, s, x, y, rot=u)
    for (x, y, s, u) in [(230, 290, 38, -10), (760, 1180, 42, 12), (240, 1200, 34, 0)]:
        srce(p, x, y, s, u)
    zvezda(p, 880, 760, 30, 10)
    zvezda(p, 120, 760, 26, -10)
    return strana(str(p))


# 5 ---------------------------------------------------------------- Erfinde deine Sorte!


def strana5():
    p = Pero()
    p.dodaj(naslov("Erfinde deine Sorte!", vel=92))
    p.dodaj('<text class="f1" x="500" y="226" text-anchor="middle">Male die Kugeln so, wie du dein Eis am liebsten hast.</text>')
    kornet(p, 500, 856, 300, 376)
    kugla(p, 500, 780, 166)
    kugla(p, 500, 582, 152)
    kugla(p, 500, 404, 136)
    # Don viri iz ugla
    don = Pero(0.5, 190, 1100)
    don_glava(don, pogled=(14, -10))
    p.dodaj(str(don))
    sapa(p, 128, 1190, 0)
    sapa(p, 252, 1190, 0)
    p.dodaj('<text class="f1" x="420" y="1290">Meine Sorte heißt:</text>')
    p.p("M 640 1294 L 930 1294", "d")
    for (x, y, r, u) in [(160, 380, 34, -8), (850, 420, 30, 10), (860, 1000, 36, 16)]:
        zvezda(p, x, y, r, u)
    for (x, y, s, u) in [(150, 640, 42, -10), (856, 680, 40, 12)]:
        srce(p, x, y, s, u)
    for (x, y, d, u) in [(250, 300, 34, 40), (760, 290, 34, -30), (220, 860, 34, 70), (800, 860, 34, -60), (760, 1160, 34, 20)]:
        mrvica(p, x, y, d, u)
    return strana(str(p))


# ---------------------------------------------------------------- HTML i PDF

CSS = f"""
@page {{ size: A4; margin: 0; }}
html, body {{ margin: 0; padding: 0; background: #fff; }}
.s {{ width: 210mm; height: 297mm; page-break-after: always; break-after: page; overflow: hidden; }}
.s:last-child {{ page-break-after: auto; break-after: auto; }}
svg {{ display: block; width: 210mm; height: 297mm; }}
.l, .o {{ stroke: {INK}; stroke-width: 7; stroke-linejoin: round; stroke-linecap: round; }}
.l {{ fill: #fff; }}
.o {{ fill: none; }}
.d {{ fill: none; stroke: {INK}; stroke-width: 4.5; stroke-linejoin: round; stroke-linecap: round; }}
.k {{ fill: {INK}; stroke: none; }}
.b {{ fill: #fff; stroke: none; }}
.m1 {{ stroke: {INK}; stroke-width: 19; stroke-linecap: round; }}
.m2 {{ stroke: #fff; stroke-width: 9; stroke-linecap: round; }}
.t {{ font-family: Fraunces, serif; font-weight: 900; font-variation-settings: "SOFT" 100, "WONK" 0;
      fill: #fff; stroke: {INK}; stroke-width: 5; stroke-linejoin: round; letter-spacing: 1px; }}
.z {{ font-family: Figtree, sans-serif; font-weight: 900; fill: #fff; stroke: {INK}; stroke-width: 6;
      stroke-linejoin: round; letter-spacing: 4px; }}
.z2 {{ font-family: Fraunces, serif; font-weight: 900; font-variation-settings: "SOFT" 100;
       fill: #fff; stroke: {INK}; stroke-width: 3.5; stroke-linejoin: round; }}
.f1 {{ font-family: Figtree, sans-serif; font-weight: 600; font-size: 26px; fill: {INK}; }}
.f2 {{ font-family: Fraunces, serif; font-weight: 800; font-size: 30px; fill: {INK}; }}
.f3 {{ font-family: Caveat, cursive; font-weight: 700; font-size: 32px; }}
.f4 {{ font-family: Figtree, sans-serif; font-weight: 500; font-size: 17px; fill: {INK}; }}
.f5 {{ font-family: Figtree, sans-serif; font-weight: 800; font-size: 26px; fill: {INK}; letter-spacing: 2px; }}
"""


def html():
    strane = [strana1(), strana2(), strana3(), strana4(), strana5()]
    return (
        "<!doctype html><html lang=\"de\"><head><meta charset=\"utf-8\">"
        "<title>DON'S Eisdiele – Malbuch</title>"
        f'<link rel="stylesheet" href="file://{FONTOVI}"><style>{CSS}</style></head><body>'
        + "".join(strane)
        + "</body></html>"
    )


def main():
    izlaz = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "studio/dons-bojanka")
    os.makedirs(os.path.join(izlaz, "vorschau"), exist_ok=True)
    pdf = os.path.join(izlaz, "dons-malbuch-a4.pdf")
    with tempfile.TemporaryDirectory() as tmp:
        ulaz = os.path.join(tmp, "malbuch.html")
        with open(ulaz, "w", encoding="utf-8") as f:
            f.write(html())
        subprocess.run(["node", os.path.join(os.path.dirname(__file__), "pdf.js"), ulaz, pdf], check=True)
    subprocess.run(["pdftoppm", "-png", "-r", "60", pdf, os.path.join(izlaz, "vorschau", "seite")], check=True)
    print(pdf)


if __name__ == "__main__":
    main()
