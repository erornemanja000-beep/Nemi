"""Kotirane verzije fotomontaza (oznake na nemackom, za Magistrat)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from kamera import ZID, TROTOAR
from modeli import (STOLOVI_X, STOLICA_RAZMAK, KRAK, PLOCA_D, VISINA_STOLA, SED_VIS, SED_SIR, ZARDINJERE_X,
                    TROG_S, TROG_V, gabariti)
from render import srgb_u_lin

FONT = '/usr/share/fonts/opentype/inter/Inter-%s.otf'
NAR = np.array([0.95, 0.42, 0.05])     # narandzasta: zona namestaja
ZEL = np.array([0.10, 0.62, 0.22])     # zelena: slobodan trotoar
TAMNA = np.array([0.012, 0.012, 0.014])


def font(vel, tezina='Medium'):
    return ImageFont.truetype(FONT % tezina, vel)


def izbocina():
    """Najveca izbocina od zida, zaokruzena navise na ceo cm."""
    return float(np.ceil(gabariti()['ukupno']))


def tlo_koordinate(kam, W, H):
    X, Y = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
    d = kam.zrak(np.stack([X, Y], -1))
    with np.errstate(divide='ignore', invalid='ignore'):
        t = -kam.C[1] / d[..., 1]
    P = kam.C + t[..., None] * d
    ok = (t > 0) & (P[..., 2] >= 0)
    return P[..., 0], P[..., 2], ok


def _boji(lin, maska, boja, alfa):
    a = (np.clip(maska, 0, 1) * alfa)[..., None]
    lin[:] = lin * (1 - a) + boja * a


def podloga_trotoar(x_kota=100.0, x_od=-5.0, x_do=ZID + 5, bez=None):
    """Zone i kota na trotoaru (crtaju se pre objekata, pa ih objekti prekrivaju)."""
    def crtaj(lin, kam):
        H, W = lin.shape[:2]
        X, Z, ok = tlo_koordinate(kam, W, H)
        if bez is not None:          # stepenik nije trotoar
            ok = ok & (bez < 0.5)
        e = izbocina()
        uX = ok & (X >= x_od) & (X <= x_do)
        _boji(lin, uX & (Z <= e), NAR, 0.30)
        _boji(lin, uX & (Z > e) & (Z <= TROTOAR), ZEL, 0.16)
        # isprekidana granica zone namestaja
        crta = uX & (np.abs(Z - e) < 1.3) & ((np.mod(X, 20) < 12))
        _boji(lin, crta, NAR * 0.8, 0.95)
        # kota preko trotoara na X = x_kota
        uz = ok & (Z >= -2) & (Z <= TROTOAR + 2)
        _boji(lin, uz & (np.abs(X - x_kota) < 3.2), np.ones(3), 0.9)       # bela podloga
        _boji(lin, uz & (np.abs(X - x_kota) < 1.4), TAMNA, 1.0)
        for zt in (0.0, e, TROTOAR):   # kose crtice (arhitektonska kota)
            u = (X - x_kota) + (Z - zt)
            k = ok & (np.abs(u) < 1.6) & (np.abs(X - x_kota) < 9)
            _boji(lin, k, TAMNA, 1.0)
            r = ok & (np.abs(Z - zt) < 1.0) & (np.abs(X - x_kota) < 14)
            _boji(lin, r, TAMNA, 1.0)
    return crtaj


def _oznaka(d, xy, tekst, f, okvir=(30, 30, 30), pozadina=(255, 255, 255), boja_teksta=(20, 20, 20),
            pad=12, sidro='mm'):
    l, t, r, b = d.textbbox((0, 0), tekst, font=f)
    w, h = r - l, b - t
    x, y = xy
    if sidro[0] == 'm':
        x -= w / 2
    elif sidro[0] == 'r':
        x -= w
    if sidro[1] == 'm':
        y -= h / 2
    elif sidro[1] == 'b':
        y -= h
    box = (x - pad, y - pad, x + w + pad, y + h + pad)
    d.rounded_rectangle(box, radius=pad, fill=pozadina, outline=okvir, width=3)
    d.text((x - l, y - t), tekst, font=f, fill=boja_teksta)
    return box


def _pokazivac(d, od, do, boja=(20, 20, 20)):
    d.line([od, do], fill=(255, 255, 255), width=7)
    d.line([od, do], fill=boja, width=3)
    r = 7
    d.ellipse((do[0] - r, do[1] - r, do[0] + r, do[1] + r), fill=boja, outline=(255, 255, 255), width=2)


def oznake_trotoar(img, kam, x_kota=100.0):
    d = ImageDraw.Draw(img)
    e = izbocina()
    p, _ = kam.projektuj(np.array([[x_kota + 16, 0, (e + TROTOAR) / 2],
                                   [x_kota + 16, 0, e / 2]]))
    _oznaka(d, tuple(p[0]), 'ca. %s m frei' % ('%.2f' % ((TROTOAR - e) / 100)).replace('.', ','), font(46, 'Bold'),
            okvir=tuple(int(c * 255) for c in ZEL), boja_teksta=(10, 90, 30))
    q, _ = kam.projektuj(np.array([[x_kota - 20, 0, TROTOAR - 8]]))
    _oznaka(d, (max(q[0][0] + 40, 30), q[0][1] - 75), 'Gehsteig 3,00 m (Hauswand – Randstein)',
            font(38, 'SemiBold'), sidro='lm')
    a, _ = kam.projektuj(np.array([[200, 0, e]]))
    _pokazivac(d, (520, 1640), tuple(a[0]), boja=tuple(int(c * 255) for c in NAR * 0.8))
    _oznaka(d, (520, 1640), 'Möblierung max. %d cm ab Hauswand' % round(e), font(38, 'SemiBold'),
            okvir=tuple(int(c * 255) for c in NAR), boja_teksta=(150, 60, 0), sidro='mm')
    return img


def oznake_fasada(img, kam):
    d = ImageDraw.Draw(img)
    # kota sirine zida na visini 100 cm
    Y = 100.0
    p, _ = kam.projektuj(np.array([[0, Y, 0], [ZID, Y, 0]]))
    a, b = tuple(p[0]), tuple(p[1])
    for w, c in ((9, (255, 255, 255)), (4, (20, 20, 20))):
        d.line([a, b], fill=c, width=w)
    for q in (a, b):
        for w, c in ((9, (255, 255, 255)), (4, (20, 20, 20))):
            d.line([(q[0] - 16, q[1] + 16), (q[0] + 16, q[1] - 16)], fill=c, width=w)
            d.line([(q[0], q[1] - 34), (q[0], q[1] + 34)], fill=c, width=w)
    m = ((a[0] + b[0]) / 2 - 20, (a[1] + b[1]) / 2 - 40)   # izmedju dve table
    _oznaka(d, m, 'Wandabschnitt 265 cm', font(38, 'Bold'), pad=10)
    # opisi
    xt = STOLOVI_X[1]
    t, _ = kam.projektuj(np.array([[xt + PLOCA_D / 2 - 3, VISINA_STOLA, KRAK + 8]]))
    _pokazivac(d, (1500, 870), tuple(t[0]))
    _oznaka(d, (1500, 870), 'Wandtisch Ø 50 cm, Höhe 75 cm', font(36, 'SemiBold'), sidro='mm')
    s, _ = kam.projektuj(np.array([[STOLOVI_X[0] + STOLICA_RAZMAK - 8, SED_VIS - 1, SED_SIR / 2 + 3]]))
    _pokazivac(d, (975, 1010), tuple(s[0]))
    _oznaka(d, (975, 1010), 'Hocker, Sitzhöhe 46 cm', font(34, 'SemiBold'), sidro='mm')
    z, _ = kam.projektuj(np.array([[ZARDINJERE_X[0] + TROG_S / 2 - 2, TROG_V, 30]]))
    _pokazivac(d, (330, 880), tuple(z[0]))
    _oznaka(d, (330, 880), 'Pflanztrog 75 × 20 × 60 cm', font(34, 'SemiBold'), sidro='mm')
    return img


def sa_natpisom(img, naslov, redovi, legenda=None):
    """Dodaje beli pojas sa opisom ispod fotografije."""
    W, H = img.size
    fn, vel = font(46, 'Bold'), 34
    mer = ImageDraw.Draw(img)
    while vel > 24 and max(mer.textlength(r, font=font(vel, 'Regular')) for r in redovi) > W - 80:
        vel -= 1
    ft = font(vel, 'Regular')
    visina = 40 + 60 + len(redovi) * (vel + 16) + (60 if legenda else 0) + 30
    out = Image.new('RGB', (W, H + visina), (255, 255, 255))
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    y = H + 36
    d.text((40, y), naslov, font=fn, fill=(25, 25, 25)); y += 66
    for r in redovi:
        d.text((40, y), r, font=ft, fill=(55, 55, 55)); y += vel + 16
    if legenda:
        x = 40; y += 8
        for boja, tekst in legenda:
            d.rectangle((x, y + 4, x + 36, y + 40), fill=boja, outline=(60, 60, 60), width=2)
            d.text((x + 50, y + 2), tekst, font=ft, fill=(40, 40, 40))
            x += 50 + d.textlength(tekst, font=ft) + 60
    return out


def legenda_boje():
    nar = tuple(int(255 * c) for c in (0.98, 0.78, 0.6))
    zel = tuple(int(255 * c) for c in (0.72, 0.88, 0.74))
    return nar, zel
