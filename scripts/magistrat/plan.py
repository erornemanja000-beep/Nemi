"""Planskizze (Grundriss, Ansicht, Schnitt) za Magistrat, A4 polozeno, mere u cm."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from kamera import ZID, TROTOAR
from modeli import (STOLOVI_X, KRAK, STUB, PLOCA_D, PLOCA_DEB, VISINA_STOLA, CEV_R, PLOCICA,
                    SED_SIR, SED_DUB, BAZA_DUB, SED_VIS, STOLICA_ISPRED_Z, TROG_D, TROG_S, TROG_V,
                    ZARDINJERE_X, ZARDINJERA_RAZMAK,
                    raspored, gabariti)

FONT = '/usr/share/fonts/opentype/inter/Inter-%s.otf'
DPI = 300
CRNA = (25, 25, 25)
SIVA = (120, 120, 120)
SVETLO_SIVA = (232, 232, 232)
NAR = (240, 120, 20)
NAR_SVETLA = (253, 226, 200)
PESAK = (214, 204, 184)       # zardinjera "Sandbraun"
PESAK_TAMNO = (150, 140, 120)
ZEL = (40, 150, 70)
ZEL_SVETLA = (214, 238, 218)

ADRESA = 'DON\'S Eisdiele · Geiselbergstraße 24, 1110 Wien'
STAND = 'Stand: Oktober 2026'


def broj(v):
    """Broj u nemackom formatu: 66,25 / 132,5 / 265."""
    return ('%.2f' % v).rstrip('0').rstrip('.').replace('.', ',')


def broj_m(v):
    """Metri sa dve decimale i zarezom: 2,20 m."""
    return ('%.2f m' % v).replace('.', ',')


class List:
    def __init__(self, w_mm=297, h_mm=210):
        self.k = DPI / 25.4
        self.img = Image.new('RGB', (int(w_mm * self.k), int(h_mm * self.k)), (255, 255, 255))
        self.d = ImageDraw.Draw(self.img)

    def px(self, p):
        return (p[0] * self.k, p[1] * self.k)

    def linija(self, pts, w=0.25, boja=CRNA, crtice=None):
        pts = [self.px(p) for p in pts]
        sw = max(1, int(round(w * self.k)))
        if not crtice:
            self.d.line(pts, fill=boja, width=sw, joint='curve')
            return
        duz, raz = crtice[0] * self.k, crtice[1] * self.k
        for a, b in zip(pts[:-1], pts[1:]):
            a, b = np.array(a), np.array(b)
            L = np.linalg.norm(b - a)
            if L == 0:
                continue
            u = (b - a) / L
            t = 0.0
            while t < L:
                t2 = min(L, t + duz)
                self.d.line([tuple(a + u * t), tuple(a + u * t2)], fill=boja, width=sw)
                t = t2 + raz

    def poligon(self, pts, ispuna=None, obod=CRNA, w=0.25):
        pts = [self.px(p) for p in pts]
        self.d.polygon(pts, fill=ispuna)
        if obod:
            self.d.line(pts + [pts[0]], fill=obod, width=max(1, int(round(w * self.k))), joint='curve')

    def krug(self, c, r, ispuna=None, obod=CRNA, w=0.25):
        x, y = self.px(c); r *= self.k
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=ispuna, outline=obod,
                       width=max(1, int(round(w * self.k))))

    def tekst(self, p, s, vel=2.6, tezina='Regular', sidro='lm', boja=CRNA, rot=0):
        f = ImageFont.truetype(FONT % tezina, int(vel * self.k))
        if rot == 0:
            self.d.text(self.px(p), s, font=f, fill=boja, anchor=sidro)
            return
        l, t, r, b = self.d.textbbox((0, 0), s, font=f, anchor='lt')
        tmp = Image.new('RGBA', (r - l + 8, b - t + 8), (255, 255, 255, 0))
        ImageDraw.Draw(tmp).text((4 - l, 4 - t), s, font=f, fill=boja + (255,), anchor='lt')
        tmp = tmp.rotate(rot, expand=True)
        x, y = self.px(p)
        self.img.paste(tmp, (int(x - tmp.size[0] / 2), int(y - tmp.size[1] / 2)), tmp)

    def kota(self, A, B, pomak, s, vel=2.3, boja=CRNA, produzi=True):
        """Kota izmedju A i B (mm na listu), horizontalna ili vertikalna;
        pomak je udaljenost kotne linije (mm, + desno/dole)."""
        A, B = np.array(A, float), np.array(B, float)
        horiz = abs(B[1] - A[1]) < abs(B[0] - A[0])
        if horiz:
            y = A[1] + pomak
            a, b = np.array([A[0], y]), np.array([B[0], y])
            if produzi:
                for P, q in ((A, a), (B, b)):
                    self.linija([(P[0], P[1] + np.sign(pomak) * 1.0), (q[0], q[1] + np.sign(pomak) * 1.2)],
                                w=0.12, boja=boja)
            self.linija([a - [1.5, 0], b + [1.5, 0]], w=0.15, boja=boja)
            for q in (a, b):
                self.linija([q + [-1.0, 1.0], q + [1.0, -1.0]], w=0.35, boja=boja)
            self.tekst(((a[0] + b[0]) / 2, y - 0.9), s, vel=vel, sidro='mb', boja=boja)
        else:
            x = A[0] + pomak
            a, b = np.array([x, A[1]]), np.array([x, B[1]])
            if produzi:
                for P, q in ((A, a), (B, b)):
                    self.linija([(P[0] + np.sign(pomak) * 1.0, P[1]), (q[0] + np.sign(pomak) * 1.2, q[1])],
                                w=0.12, boja=boja)
            self.linija([a - [0, 1.5], b + [0, 1.5]], w=0.15, boja=boja)
            for q in (a, b):
                self.linija([q + [-1.0, 1.0], q + [1.0, -1.0]], w=0.35, boja=boja)
            self.tekst((x - 1.2 - vel * 0.45, (a[1] + b[1]) / 2), s, vel=vel, rot=90, boja=boja)


def izbocina():
    return float(np.ceil(gabariti()['ukupno']))


class Pogled:
    """Preslikavanje sveta (cm) na list (mm): x = ox + a*s, y = oy + znak*b*s."""
    def __init__(self, ox, oy, razmera, znak=-1):
        self.ox, self.oy, self.s, self.znak = ox, oy, 10.0 / razmera, znak

    def __call__(self, a, b):
        return (self.ox + a * self.s, self.oy + self.znak * b * self.s)

    def pts(self, lst):
        return [self(a, b) for a, b in lst]


def okvir_lista(L, naslov, podnaslov):
    L.linija([(8, 8), (289, 8), (289, 202), (8, 202), (8, 8)], w=0.35)
    L.tekst((14, 16), naslov, vel=5.0, tezina='Bold')
    L.tekst((14, 23.5), podnaslov, vel=2.9, boja=(70, 70, 70))
    L.tekst((283, 16), ADRESA, vel=2.9, tezina='SemiBold', sidro='rm')
    L.tekst((283, 197), STAND + ' · Maße in cm · Planskizze (maßstäblich), Maße vor Ort geprüft',
            vel=2.3, sidro='rm', boja=(90, 90, 90))
    L.linija([(8, 28), (289, 28)], w=0.2)


# ------------------------------------------------------------------ list 1: Grundriss
def grundriss(L, P):
    izb = izbocina()
    x_l, x_d = -45, 310
    # fahrbahn, gehsteig
    L.poligon(P.pts([(x_l, TROTOAR), (x_d, TROTOAR), (x_d, TROTOAR + 28), (x_l, TROTOAR + 28)]),
              ispuna=(205, 205, 205), obod=None)
    L.poligon(P.pts([(x_l, 0), (x_d, 0), (x_d, TROTOAR), (x_l, TROTOAR)]), ispuna=(246, 246, 246), obod=None)
    # zone
    L.poligon(P.pts([(0, 0), (ZID, 0), (ZID, izb), (0, izb)]), ispuna=NAR_SVETLA, obod=None)
    L.poligon(P.pts([(0, izb), (ZID, izb), (ZID, TROTOAR), (0, TROTOAR)]), ispuna=ZEL_SVETLA, obod=None)
    L.linija(P.pts([(0, izb), (ZID, izb)]), w=0.3, boja=NAR, crtice=(2.0, 1.2))
    # randstein
    L.linija(P.pts([(x_l, TROTOAR), (x_d, TROTOAR)]), w=0.5)
    L.tekst(P(x_l + 6, TROTOAR + 14), 'Fahrbahn', vel=2.4, boja=(80, 80, 80))
    L.tekst(P(x_d - 4, TROTOAR + 14), 'Gehsteigkante / Randstein', vel=2.4, sidro='rm', boja=(80, 80, 80))
    # gebaeude
    zgr = [(x_l, -32), (x_d, -32), (x_d, 0), (x_l, 0)]
    L.poligon(P.pts(zgr), ispuna=(255, 255, 255), obod=None)
    srafura(L, P.pts(zgr))
    L.linija(P.pts([(x_l, 0), (x_d, 0)]), w=0.6)
    # beli zidni deo
    L.poligon(P.pts([(0, -3), (ZID, -3), (ZID, 0), (0, 0)]), ispuna=(250, 228, 228), obod=CRNA, w=0.2)
    L.tekst(P(-22, -16), 'Nachbar-', vel=2.0, sidro='mm', boja=(60, 60, 60))
    L.tekst(P(-22, -9), 'fassade', vel=2.0, sidro='mm', boja=(60, 60, 60))
    L.tekst(P(288, -16), 'Eingang', vel=2.0, sidro='mm', boja=(60, 60, 60))
    L.tekst(P(288, -9), 'DON\'S', vel=2.0, sidro='mm', boja=(60, 60, 60))
    L.tekst(P(ZID / 2, -16), 'Hauswand (weißer Wandabschnitt)', vel=2.4, sidro='mm', tezina='Medium')
    # stolice i zardinjere (iz istog rasporeda kao 3D model)
    for vrsta, x, z, napred in raspored():
        if vrsta == 'stolica':
            stolica_tlocrt(L, P, x, z, napred)
        elif vrsta == 'zardinjera':
            z0, z1 = z, z + TROG_D
            L.poligon(P.pts([(x - TROG_S / 2, z0), (x + TROG_S / 2, z0), (x + TROG_S / 2, z1),
                             (x - TROG_S / 2, z1)]), ispuna=PESAK, obod=CRNA, w=0.35)
            L.poligon(P.pts([(x - TROG_S / 2 + 2, z0 + 2), (x + TROG_S / 2 - 2, z0 + 2),
                             (x + TROG_S / 2 - 2, z1 - 2), (x - TROG_S / 2 + 2, z1 - 2)]),
                      ispuna=(236, 230, 216), obod=PESAK_TAMNO, w=0.12)
    # stolovi
    for xt in STOLOVI_X:
        L.krug(P(xt, KRAK), PLOCA_D / 2 * P.s, ispuna=(255, 255, 255), obod=CRNA, w=0.35)
        L.linija(P.pts([(xt, 0.8), (xt, KRAK)]), w=0.15, crtice=(1.0, 0.7), boja=SIVA)
        L.poligon(P.pts([(xt - PLOCICA / 2, 0), (xt + PLOCICA / 2, 0), (xt + PLOCICA / 2, 1.2),
                         (xt - PLOCICA / 2, 1.2)]), ispuna=CRNA, obod=CRNA, w=0.1)
        L.tekst(P(xt, KRAK - 9), 'Ø 50', vel=2.2, sidro='mm', tezina='SemiBold')
    # oznake zona
    L.tekst(P(ZID / 2, (izb + TROTOAR) / 2 - 8), 'freier Gehsteig', vel=3.4, sidro='mm',
            tezina='Bold', boja=ZEL)
    L.tekst(P(ZID / 2, (izb + TROTOAR) / 2 + 12), 'ca. ' + broj_m((TROTOAR - izb) / 100), vel=3.4,
            sidro='mm', tezina='Bold', boja=ZEL)
    # kote
    L.kota(P(0, -32), P(ZID, -32), -6, '265')
    xs = [0, STOLOVI_X[0], STOLOVI_X[1], ZID]
    for a, b in zip(xs[:-1], xs[1:]):
        L.kota(P(a, -32), P(b, -32), -1.5, broj(b - a), vel=2.0, produzi=False)
    L.kota(P(ZID, 0), P(ZID, izb), 8, '%d' % round(izb), boja=NAR)
    L.kota(P(ZID, izb), P(ZID, TROTOAR), 8, '%d frei' % round(TROTOAR - izb), boja=ZEL)
    L.kota(P(ZID, 0), P(ZID, TROTOAR), 17, '300 Gehsteig')
    # zardinjera: 75 od zida, sirina 20
    L.kota(P(-45, 0), P(-45, TROG_D + 0.5), -4, '75', vel=1.9)
    L.linija(P.pts([(-45, TROG_D + 0.5), (0, TROG_D + 0.5)]), w=0.1, boja=SIVA, crtice=(0.8, 0.8))
    xz0 = ZARDINJERE_X[0] - TROG_S / 2
    L.kota(P(0, TROG_D + 0.5), P(xz0, TROG_D + 0.5), 4.5, '%d' % ZARDINJERA_RAZMAK, vel=1.8)
    L.kota(P(xz0, TROG_D + 0.5), P(xz0 + TROG_S, TROG_D + 0.5), 4.5, '20', vel=1.8, produzi=False)
    L.tekst(P(ZARDINJERE_X[0], TROG_D + 22), 'Pflanztrog', vel=2.0, sidro='mm', tezina='SemiBold')
    L.tekst(P(ZARDINJERE_X[0], TROG_D + 30), '75/20/60', vel=1.9, sidro='mm')
    # presek
    xp = STOLOVI_X[0]
    for zz, oz in ((-40, 'A'), (TROTOAR + 24, 'A')):
        L.krug(P(xp, zz), 2.2, ispuna=(255, 255, 255), obod=CRNA, w=0.25)
        L.tekst(P(xp, zz), oz, vel=2.4, sidro='mm', tezina='Bold')
    L.linija(P.pts([(xp, -36), (xp, -10)]), w=0.25, crtice=(3, 1))
    L.linija(P.pts([(xp, TROTOAR + 5), (xp, TROTOAR + 20)]), w=0.25, crtice=(3, 1))


def stolica_tlocrt(L, P, x, z, napred):
    u = np.array([napred[0], napred[2]], float); v = np.array([-u[1], u[0]])
    c = np.array([x, z], float)
    w2 = SED_SIR / 2 - 1.0

    def q(du, dv):
        return tuple(c + du * u + dv * v)
    L.poligon(P.pts([q(SED_DUB / 2, w2), q(-SED_DUB / 2, w2), q(-SED_DUB / 2, -w2), q(SED_DUB / 2, -w2)]),
              ispuna=(255, 255, 255), obod=CRNA, w=0.25)
    for du in np.linspace(-SED_DUB / 2 + 3.5, SED_DUB / 2 - 3.5, 12):
        L.linija(P.pts([q(du, -w2 + 1), q(du, w2 - 1)]), w=0.08, boja=(110, 110, 110))
    for dv in (-(w2 + 0.8), w2 + 0.8):
        L.linija(P.pts([q(-BAZA_DUB / 2, dv), q(BAZA_DUB / 2, dv)]), w=0.3)


def stolica_bocno(L, P, a, _, boja=CRNA, napred=1):
    """Sanke stolice u bocnom pogledu; a = polozaj centra na horizontalnoj osi pogleda."""
    s = napred
    L.linija(P.pts([(a + s * (SED_DUB / 2 - 1.5), SED_VIS - 1), (a + s * BAZA_DUB / 2, 0.6),
                    (a - s * BAZA_DUB / 2, 0.6), (a - s * (SED_DUB / 2 - 1.5), SED_VIS - 1)]), w=0.35, boja=boja)
    L.linija(P.pts([(a - SED_DUB / 2, SED_VIS), (a + SED_DUB / 2, SED_VIS)]), w=0.5, boja=boja)


def stolica_spreda(L, P, a, _, boja=CRNA):
    """Stolica gledana spreda (sirina 46, noge sa obe strane, ulegnuto sediste)."""
    w2 = SED_SIR / 2 - 0.2
    xs = np.linspace(-w2, w2, 15)
    sag = 1.6 * (1 - (xs / (SED_SIR / 2)) ** 2)
    L.linija(P.pts(list(zip(a + xs, SED_VIS - sag))), w=0.5, boja=boja)
    for dx in (-w2, w2):
        L.linija(P.pts([(a + dx, SED_VIS - 0.3), (a + dx, 0.3)]), w=0.35, boja=boja)


def srafura(L, pts_mm):
    """Kosa srafura zgrade (jednostavno, crtanjem linija pa maskiranjem)."""
    maska = Image.new('L', L.img.size, 0)
    ImageDraw.Draw(maska).polygon([L.px(p) for p in pts_mm], fill=255)
    sloj = L.img.copy()
    ds = ImageDraw.Draw(sloj)
    xs = [L.px(p)[0] for p in pts_mm]; ys = [L.px(p)[1] for p in pts_mm]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    h = y1 - y0; korak = 1.8 * L.k
    x = x0 - h
    while x < x1 + h:
        ds.line([(x, y1), (x + h, y0)], fill=SIVA, width=max(1, int(0.15 * L.k)))
        x += korak
    L.img.paste(sloj, (0, 0), maska)


def list_grundriss():
    L = List()
    okvir_lista(L, 'Grundriss – Möblierung an der Fassade',
                '2 Wandtische, 4 Hocker, 2 Pflanztröge als seitliche Abgrenzung · M 1:25 (A4)')
    P = Pogled(ox=40, oy=58, razmera=25, znak=1)
    grundriss(L, P)
    # legenda i napomene desno
    x0, y = 188, 44
    L.tekst((x0, y), 'Legende', vel=3.2, tezina='Bold'); y += 8
    izb = izbocina()
    for ispuna, obod, tekst in ((NAR_SVETLA, NAR, 'Möblierungszone (max. %d cm ab Hauswand)' % izb),
                                (ZEL_SVETLA, ZEL, 'freier Gehsteig'),
                                (PESAK, CRNA, 'Pflanztrog 75 × 20 × 60 cm')):
        L.poligon([(x0, y - 2.2), (x0 + 6, y - 2.2), (x0 + 6, y + 2.2), (x0, y + 2.2)], ispuna=ispuna, obod=obod)
        L.tekst((x0 + 9, y), tekst, vel=2.4); y += 7
    y += 4
    L.tekst((x0, y), 'Möblierung', vel=3.2, tezina='Bold'); y += 7
    napomene = [
        '2 × Wandtisch, Metall schwarz:',
        '   Tischplatte Ø 50 cm, Wandarm 29 cm,',
        '   Stütze 46 cm, Wandplatte 12 × 12 cm,',
        '   Tischhöhe ca. 75 cm, keine Bodenteile',
        '4 × Hocker, Metall schwarz:',
        '   ca. 46 × 46 cm, Sitzhöhe 46 cm,',
        '   je 1 Hocker vor jedem Tisch, 2 dazwischen',
        '2 × Pflanztrog (Sandbraun), seitliche',
        '   Abgrenzung links und rechts:',
        '   75 × 20 × 60 cm (L × B × H)',
        '',
        'Größte Ausladung ab Hauswand:',
        '   ca. %d cm (Hocker vor dem Tisch),' % izb,
        '   Pflanztrog 75 cm, Tischplatte 54 cm',
        'Gehsteigbreite Hauswand – Randstein:',
        '   3,00 m (vor Ort gemessen)',
        'Verbleibende freie Gehsteigbreite:',
        '   ca. ' + broj_m((TROTOAR - izb) / 100),
        'Breite des Wandabschnitts: 2,65 m',
    ]
    for s in napomene:
        fett = s and not s.startswith('   ')
        L.tekst((x0, y), s, vel=2.35, tezina='SemiBold' if fett else 'Regular'); y += 5.0
    return L.img


# ------------------------------------------------------------------ list 2: Ansicht + Schnitt
def ansicht(L, P):
    x_l, x_d = -45, 310
    # zid
    L.poligon(P.pts([(x_l, 0), (0, 0), (0, 140), (x_l, 140)]), ispuna=(236, 233, 228), obod=None)
    L.poligon(P.pts([(0, 0), (ZID, 0), (ZID, 140), (0, 140)]), ispuna=(252, 240, 240), obod=CRNA, w=0.3)
    L.poligon(P.pts([(0, 0), (ZID, 0), (ZID, 14), (0, 14)]), ispuna=(225, 220, 210), obod=SIVA, w=0.15)
    L.tekst(P(ZID / 2, 128), 'Hauswand (weißer Wandabschnitt)', vel=2.4, sidro='mm', tezina='Medium')
    L.tekst(P(-22, 70), 'Nachbar-', vel=2.0, sidro='mm', boja=(80, 80, 80))
    L.tekst(P(-22, 63), 'fassade', vel=2.0, sidro='mm', boja=(80, 80, 80))
    L.tekst(P(288, 70), 'Eingang', vel=2.0, sidro='mm', boja=(80, 80, 80))
    L.linija(P.pts([(x_l, 0), (x_d, 0)]), w=0.5)
    # stolice uz zid (bocni pogled na sanke), iza stolova
    for vrsta, x, z, napred in raspored():
        if vrsta == 'stolica' and z < 40:
            stolica_bocno(L, P, x, None, napred=np.sign(napred[0]))
    # stolovi
    for xt in STOLOVI_X:
        yk = VISINA_STOLA - PLOCA_DEB - STUB
        L.poligon(P.pts([(xt - PLOCICA / 2, yk - PLOCICA / 2), (xt + PLOCICA / 2, yk - PLOCICA / 2),
                         (xt + PLOCICA / 2, yk + PLOCICA / 2), (xt - PLOCICA / 2, yk + PLOCICA / 2)]),
                  ispuna=(60, 60, 60), obod=CRNA, w=0.15)
        L.poligon(P.pts([(xt - CEV_R, yk), (xt + CEV_R, yk), (xt + CEV_R, VISINA_STOLA - PLOCA_DEB),
                         (xt - CEV_R, VISINA_STOLA - PLOCA_DEB)]), ispuna=CRNA, obod=CRNA, w=0.1)
        L.krug(P(xt, yk), CEV_R * P.s * 1.2, ispuna=CRNA, obod=CRNA, w=0.1)
        L.poligon(P.pts([(xt - PLOCA_D / 2, VISINA_STOLA - PLOCA_DEB), (xt + PLOCA_D / 2, VISINA_STOLA - PLOCA_DEB),
                         (xt + PLOCA_D / 2, VISINA_STOLA), (xt - PLOCA_D / 2, VISINA_STOLA)]),
                  ispuna=CRNA, obod=CRNA, w=0.1)
    # stolice ispred stolova i zardinjere (najblize posmatracu)
    for vrsta, x, z, napred in raspored():
        if vrsta == 'stolica' and z >= 40:
            stolica_bocno(L, P, x, None, napred=np.sign(napred[0]))
        elif vrsta == 'zardinjera':
            L.poligon(P.pts([(x - TROG_S / 2, 0), (x + TROG_S / 2, 0), (x + TROG_S / 2, TROG_V),
                             (x - TROG_S / 2, TROG_V)]), ispuna=PESAK, obod=CRNA, w=0.35)
    # kote
    L.kota(P(0, 0), P(ZID, 0), 9, '265')
    L.kota(P(STOLOVI_X[1] - PLOCA_D / 2, VISINA_STOLA), P(STOLOVI_X[1] + PLOCA_D / 2, VISINA_STOLA),
           -2.5, 'Ø 50', vel=2.0)
    xt = STOLOVI_X[1]
    L.kota(P(ZID, 0), P(ZID, VISINA_STOLA), 6, '75')
    L.linija(P.pts([(xt + PLOCA_D / 2 + 2, VISINA_STOLA), (ZID + 2, VISINA_STOLA)]), w=0.1, boja=SIVA,
             crtice=(0.8, 0.8))
    L.kota(P(ZID, 0), P(ZID, TROG_V), 13, '60')
    L.kota(P(ZID, 0), P(ZID, SED_VIS), 20, '46')
    L.linija(P.pts([(xt + SED_SIR / 2, SED_VIS), (ZID + 2, SED_VIS)]), w=0.1, boja=SIVA, crtice=(0.8, 0.8))
    xz0 = ZARDINJERE_X[0] - TROG_S / 2
    L.kota(P(0, 0), P(xz0, 0), 3.5, '%d' % ZARDINJERA_RAZMAK, vel=1.8, produzi=False)
    L.kota(P(xz0, 0), P(xz0 + TROG_S, 0), 3.5, '20', vel=1.8, produzi=False)
    L.tekst(P(ZARDINJERE_X[0], TROG_V + 6), 'Pflanztrog', vel=1.9, sidro='mm', tezina='SemiBold')


def schnitt(L, P):
    izb = izbocina()
    # zardinjera iza (pogled ka levom kraju zida)
    L.poligon(P.pts([(0.5, 0), (TROG_D + 0.5, 0), (TROG_D + 0.5, TROG_V), (0.5, TROG_V)]),
              ispuna=(236, 230, 216), obod=PESAK_TAMNO, w=0.25)
    # zid (presek)
    zid = [(-28, -12), (0, -12), (0, 95), (-28, 95)]
    L.poligon(P.pts(zid), ispuna=(255, 255, 255), obod=None)
    srafura(L, P.pts(zid))
    L.linija(P.pts([(0, -12), (0, 95)]), w=0.6)
    # tlo, ivicnjak, kolovoz
    L.poligon(P.pts([(0, 0), (TROTOAR, -4), (TROTOAR, -12), (0, -12)]), ispuna=(238, 238, 238), obod=None)
    L.linija(P.pts([(0, 0), (TROTOAR, -4), (TROTOAR, -12)]), w=0.5)
    L.linija(P.pts([(TROTOAR, -12), (TROTOAR + 35, -12)]), w=0.5)
    L.tekst(P(TROTOAR + 18, -6), 'Fahrbahn', vel=2.0, sidro='mm', boja=(80, 80, 80))
    L.tekst(P(TROTOAR - 2, 8), 'Randstein', vel=2.0, sidro='rm', boja=(80, 80, 80))
    L.poligon(P.pts([(0, 0), (izb, -0.7), (izb, 2.5), (0, 2.5)]), ispuna=NAR_SVETLA, obod=None)
    L.poligon(P.pts([(izb, -0.7), (TROTOAR, -4), (TROTOAR, -1), (izb, 2.5)]), ispuna=ZEL_SVETLA, obod=None)
    # stolica ispred stola (bocni pogled na sanke, lice ka zidu)
    stolica_spreda(L, P, STOLICA_ISPRED_Z, None, boja=(70, 70, 70))
    # sto u preseku
    yk = VISINA_STOLA - PLOCA_DEB - STUB
    L.poligon(P.pts([(0, yk - PLOCICA / 2), (0.8, yk - PLOCICA / 2), (0.8, yk + PLOCICA / 2), (0, yk + PLOCICA / 2)]),
              ispuna=CRNA, obod=CRNA, w=0.1)
    put = [(0.8, yk), (KRAK - 5, yk)]
    for a in np.linspace(-90, 0, 10):
        put.append((KRAK - 5 + 5 * np.cos(np.radians(a)) * 1, yk + 5 + 5 * np.sin(np.radians(a))))
    put.append((KRAK, VISINA_STOLA - PLOCA_DEB))
    L.linija(P.pts(put), w=CEV_R * 2 * P.s, boja=CRNA)
    L.poligon(P.pts([(KRAK - PLOCA_D / 2, VISINA_STOLA - PLOCA_DEB), (KRAK + PLOCA_D / 2, VISINA_STOLA - PLOCA_DEB),
                     (KRAK + PLOCA_D / 2, VISINA_STOLA), (KRAK - PLOCA_D / 2, VISINA_STOLA)]),
              ispuna=CRNA, obod=CRNA, w=0.1)
    # kote
    L.kota(P(0, VISINA_STOLA), P(KRAK + PLOCA_D / 2, VISINA_STOLA), -8, '54', vel=2.0)
    L.kota(P(0, VISINA_STOLA), P(KRAK, VISINA_STOLA), -3.5, '29', vel=1.9, produzi=False)
    L.kota(P(0, -12), P(izb, -12), 5.5, '%d' % round(izb), boja=NAR)
    L.kota(P(izb, -12), P(TROTOAR, -12), 5.5, 'freier Gehsteig ca. %d' % round(TROTOAR - izb), boja=ZEL)
    L.kota(P(0, -12), P(TROTOAR, -12), 11, 'Gehsteig 300 (Hauswand – Randstein)')
    xk = KRAK + PLOCA_D / 2
    L.linija(P.pts([(xk + 1, VISINA_STOLA), (95, VISINA_STOLA)]), w=0.1, boja=SIVA, crtice=(0.8, 0.8))
    L.linija(P.pts([(KRAK + 2, yk), (105, yk)]), w=0.1, boja=SIVA, crtice=(0.8, 0.8))
    L.kota(P(95, 0), P(95, VISINA_STOLA), 0, 'Tisch 75', vel=1.9, produzi=False)
    L.kota(P(105, yk), P(105, VISINA_STOLA - PLOCA_DEB), 0, 'Stütze 46', vel=1.9, produzi=False)
    L.tekst(P(125, 66), 'Wandtisch: Platte Ø 50, Arm 29, Stütze 46', vel=2.2)
    L.tekst(P(125, 56), 'Hocker vor dem Tisch: Breite 46, Sitzhöhe 46', vel=2.2, boja=(70, 70, 70))
    L.tekst(P(125, 46), 'Pflanztrog dahinter: 75 × 20 × 60', vel=2.2, boja=PESAK_TAMNO)


def list_ansicht_schnitt():
    L = List()
    okvir_lista(L, 'Ansicht und Schnitt A–A',
                'Ansicht der Hauswand von der Straße und Querschnitt durch Gehsteig und Wandtisch')
    L.tekst((14, 36), 'Ansicht von der Straße (M 1:20)', vel=3.0, tezina='Bold')
    ansicht(L, Pogled(ox=40, oy=112, razmera=20))
    L.tekst((14, 133), 'Schnitt A–A durch den linken Tisch (M 1:25)', vel=3.0, tezina='Bold')
    schnitt(L, Pogled(ox=40, oy=180, razmera=25))
    return L.img


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    list_grundriss().save(out + '/plan_1_grundriss.png')
    list_ansicht_schnitt().save(out + '/plan_2_ansicht_schnitt.png')
