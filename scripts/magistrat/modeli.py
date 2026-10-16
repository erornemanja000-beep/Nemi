"""3D modeli: zidni stocic (Etsy, desna varijanta) i zicana stolica (sled baza).

Sve mere su u cm, u koordinatama sveta iz kamera.py:
X duz zida, Y nagore, Z od zida ka ulici.
"""
import numpy as np

# ---- zidni stocic (desna varijanta sa Etsy slike)
KRAK = 29.0        # vodoravni krak od zida do stuba
STUB = 46.0        # vertikalni stub od kraka do ploce
PLOCA_D = 50.0     # precnik ploce
PLOCA_DEB = 1.2    # debljina ploce
VISINA_STOLA = 75.0  # gornja ivica ploce od trotoara
CEV_R = 1.4        # poluprecnik cevi (fi 28 mm)
PLOCICA = 12.0     # zidna plocica 12 x 12 cm

# ---- stolica (kao na drugoj Etsy slici)
SED_SIR = 46.0     # sirina sedista (popreko, ovde upravno na zid)
SED_DUB = 38.0     # dubina sedista (u smeru sanki, ovde duz zida)
BAZA_DUB = 46.0    # duzina sanki na podu
SED_VIS = 46.0     # visina sedista
RAM_R = 0.6        # sipka rama fi 12 mm
LETVA_R = 0.4      # letvice sedista fi 8 mm
N_LETVI = 12


class Mesh:
    def __init__(self, V, N, F, mat):
        self.V, self.N, self.F, self.mat = (np.asarray(V, float), np.asarray(N, float),
                                            np.asarray(F, int), mat)


class Senka:
    """Pojednostavljen oblik za racunanje senki: izlomljena linija debljine 2r
    ili zatvoren poligon."""
    def __init__(self, tacke, r=None, poligon=False):
        self.tacke, self.r, self.poligon = np.asarray(tacke, float), r, poligon


def _norm(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def zaobljena_putanja(temena, r, n_luk=10, korak=None):
    """Izlomljena linija sa zaobljenim uglovima poluprecnika r."""
    T = [np.asarray(t, float) for t in temena]
    out = [T[0]]
    for i in range(1, len(T) - 1):
        p0, p1, p2 = T[i - 1], T[i], T[i + 1]
        d1 = _norm(p0 - p1); d2 = _norm(p2 - p1)
        th = np.arccos(np.clip(d1 @ d2, -1, 1))
        if th > np.pi - 1e-3 or r <= 0:
            out.append(p1); continue
        t = r / np.tan(th / 2)
        bis = _norm(d1 + d2)
        c = p1 + bis * r / np.sin(th / 2)
        a = p1 + d1 * t - c; b = p1 + d2 * t - c
        ang = np.arccos(np.clip(_norm(a) @ _norm(b), -1, 1))
        for s in np.linspace(0, 1, n_luk):
            v = (np.sin((1 - s) * ang) * a + np.sin(s * ang) * b) / np.sin(ang)
            out.append(c + v)
    out.append(T[-1])
    P = [out[0]]
    for q in out[1:]:
        if np.linalg.norm(q - P[-1]) > 1e-6:
            P.append(q)
    P = np.array(P)
    if korak:
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]):
            n = max(1, int(np.ceil(np.linalg.norm(b - a) / korak)))
            for s in np.linspace(0, 1, n + 1)[1:]:
                Q.append(a + (b - a) * s)
        P = np.array(Q)
    return P


def cev(putanja, r, mat, seg=14, kape=True):
    P = np.asarray(putanja, float)
    n = len(P)
    T = np.gradient(P, axis=0); T = _norm(T)
    a = np.array([0, 1.0, 0]) if abs(T[0, 1]) < 0.9 else np.array([1.0, 0, 0])
    Nf = [_norm(np.cross(T[0], a))]
    for i in range(1, n):
        v = Nf[-1] - (Nf[-1] @ T[i]) * T[i]
        Nf.append(_norm(v))
    Nf = np.array(Nf); Bf = np.cross(T, Nf)
    th = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    ring = np.cos(th)[None, :, None] * Nf[:, None, :] + np.sin(th)[None, :, None] * Bf[:, None, :]
    V = (P[:, None, :] + r * ring).reshape(-1, 3)
    N = ring.reshape(-1, 3)
    F = []
    for i in range(n - 1):
        for j in range(seg):
            a0 = i * seg + j; a1 = i * seg + (j + 1) % seg
            b0 = a0 + seg; b1 = a1 + seg
            F += [(a0, b0, b1), (a0, b1, a1)]
    V = list(V); N = list(N)
    if kape:
        for idx, sgn in ((0, -1), (n - 1, 1)):
            c = len(V); V.append(P[idx]); N.append(sgn * T[idx])
            base = idx * seg
            for j in range(seg):
                V.append(V[base + j]); N.append(sgn * T[idx])
            for j in range(seg):
                F.append((c, c + 1 + j, c + 1 + (j + 1) % seg))
    return Mesh(V, N, F, mat)


def disk(centar_gore, r, deb, mat, seg=72, zaobljenje=0.0):
    """Vodoravni disk; centar_gore je centar gornje povrsine."""
    c = np.asarray(centar_gore, float)
    th = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    ring = np.stack([np.cos(th), np.zeros(seg), np.sin(th)], -1)
    V, N, F = [], [], []
    # gornja i donja povrs
    for y, ny in ((0.0, 1.0), (-deb, -1.0)):
        k = len(V); V.append(c + [0, y, 0]); N.append([0, ny, 0])
        for j in range(seg):
            V.append(c + [0, y, 0] + r * ring[j]); N.append([0, ny, 0])
        for j in range(seg):
            F.append((k, k + 1 + j, k + 1 + (j + 1) % seg))
    # bocna strana (nekoliko prstenova za blago zaobljenu ivicu)
    prof = [(0.0, 0.0, 0.6), (-deb * 0.5, 0.0, 0.0), (-deb, 0.0, -0.6)]
    k = len(V)
    for y, _, ny in prof:
        for j in range(seg):
            V.append(c + [0, y, 0] + r * ring[j])
            N.append(_norm(ring[j] + [0, ny, 0]))
    for i in range(len(prof) - 1):
        for j in range(seg):
            a0 = k + i * seg + j; a1 = k + i * seg + (j + 1) % seg
            F += [(a0, a0 + seg, a1 + seg), (a0, a1 + seg, a1)]
    return Mesh(V, N, F, mat)


def kvadar_na_zidu(cx, cy, w, h, deb, mat, r_ugla=1.2, seg_ugla=5):
    """Pravougaona plocica na zidu (Z od 0 do deb) sa zaobljenim uglovima."""
    pts = []
    for (sx, sy, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ccx = cx + sx * (w / 2 - r_ugla); ccy = cy + sy * (h / 2 - r_ugla)
        for a in np.linspace(a0, a0 + 90, seg_ugla):
            pts.append((ccx + r_ugla * np.cos(np.radians(a)), ccy + r_ugla * np.sin(np.radians(a))))
    pts = np.array(pts); m = len(pts)
    V, N, F = [], [], []
    k = len(V); V.append((cx, cy, deb)); N.append((0, 0, 1))
    for p in pts:
        V.append((p[0], p[1], deb)); N.append((0, 0, 1))
    for j in range(m):
        F.append((k, k + 1 + j, k + 1 + (j + 1) % m))
    k = len(V)
    for p in pts:
        nn = _norm(np.array([p[0] - cx, p[1] - cy, 0.0]))
        V.append((p[0], p[1], deb)); N.append(nn)
        V.append((p[0], p[1], 0.0)); N.append(nn)
    for j in range(m):
        a0 = k + 2 * j; a1 = k + 2 * ((j + 1) % m)
        F += [(a0, a0 + 1, a1 + 1), (a0, a1 + 1, a1)]
    return Mesh(V, N, F, mat), pts


def stocic(xc):
    """Zidni stocic: plocica na zidu, krak 29 cm, stub 46 cm, ploca fi 50 cm."""
    y_ploca = VISINA_STOLA
    y_krak = y_ploca - PLOCA_DEB - STUB
    meshes, senke = [], []
    pl, pts = kvadar_na_zidu(xc, y_krak, PLOCICA, PLOCICA, 0.8, 'metal')
    meshes.append(pl)
    senke.append(Senka(np.c_[pts, np.full(len(pts), 0.8)], poligon=True))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = (xc + sx * 4.0, y_krak + sy * 4.0)
            meshes.append(cev([(p[0], p[1], 0.8), (p[0], p[1], 1.5)], 0.7, 'metal', seg=10))
    put = zaobljena_putanja([(xc, y_krak, 0.5), (xc, y_krak, KRAK), (xc, y_ploca - PLOCA_DEB - 0.8, KRAK)],
                            r=5.0, n_luk=12, korak=4.0)
    meshes.append(cev(put, CEV_R, 'metal', seg=18))
    senke.append(Senka(put, r=CEV_R))
    # prirubnica ispod ploce i ploca
    meshes.append(disk((xc, y_ploca - PLOCA_DEB, KRAK), 6.0, 0.8, 'metal', seg=36))
    meshes.append(disk((xc, y_ploca, KRAK), PLOCA_D / 2, PLOCA_DEB, 'ploca', seg=96))
    th = np.linspace(0, 2 * np.pi, 72, endpoint=False)
    senke.append(Senka(np.c_[xc + 25 * np.cos(th), np.full(72, y_ploca - 0.6), KRAK + 25 * np.sin(th)],
                       poligon=True))
    return meshes, senke


def stolica(xc, zc, napred=(1, 0, 0)):
    """Stolica (sanke napred-nazad). xc, zc: centar na podu;
    napred: vodoravni smer u kome gleda onaj ko sedi (ka stolu)."""
    meshes, senke = [], []
    u = np.asarray(napred, float); u = u / np.linalg.norm(u)
    v = np.cross(u, [0, 1.0, 0])         # bocno
    c = np.array([xc, 0, zc])

    def P(du, y, dv):
        return c + du * u + dv * v + np.array([0, y, 0])

    hs = SED_VIS
    w2 = SED_SIR / 2 - 1.0
    # sanke: prednja noga - klizac na podu - zadnja noga (sa obe strane)
    for s in (-1, 1):
        put = zaobljena_putanja([P(SED_DUB / 2 - 1.5, hs - 1.2, s * w2), P(BAZA_DUB / 2, RAM_R + 0.3, s * (w2 + 0.8)),
                                 P(-BAZA_DUB / 2, RAM_R + 0.3, s * (w2 + 0.8)),
                                 P(-SED_DUB / 2 + 1.5, hs - 1.2, s * w2)], r=2.5, n_luk=8, korak=3.0)
        meshes.append(cev(put, RAM_R, 'metal', seg=12))
        senke.append(Senka(put, r=RAM_R))
        for du in (BAZA_DUB / 2 - 1.5, -BAZA_DUB / 2 + 1.5):  # klizne papuce
            q = P(du, 0.0, s * (w2 + 0.8))
            meshes.append(cev([q, q + [0, 0.5, 0]], 1.0, 'guma', seg=10))
    # ram sedista (pravougaonik sa ugibom u sredini)
    def sag(dv):
        return 1.6 * (1 - (dv / (SED_SIR / 2)) ** 2)
    for du in (SED_DUB / 2 - 1.0, -SED_DUB / 2 + 1.0):
        dvs = np.linspace(-w2, w2, 15)
        put = [P(du, hs - sag(dv), dv) for dv in dvs]
        meshes.append(cev(put, RAM_R, 'metal', seg=12))
        senke.append(Senka(put, r=RAM_R))
    for s in (-1, 1):
        put = [P(du, hs - sag(s * w2), s * w2) for du in np.linspace(-SED_DUB / 2 + 1, SED_DUB / 2 - 1, 6)]
        meshes.append(cev(put, RAM_R * 0.9, 'metal', seg=10))
    # letvice (paralelne prednjoj ivici, savijene)
    for du in np.linspace(-SED_DUB / 2 + 3.5, SED_DUB / 2 - 3.5, N_LETVI):
        dvs = np.linspace(-w2, w2, 15)
        put = [P(du, hs - sag(dv) + 0.15, dv) for dv in dvs]
        meshes.append(cev(put, LETVA_R, 'metal', seg=8, kape=False))
        senke.append(Senka(put, r=LETVA_R))
    return meshes, senke


# ---- zardinjera (Pflanztrog) 75 x 20 x 60 cm, Sandbraun
TROG_D, TROG_S, TROG_V = 75.0, 20.0, 60.0   # duzina (od zida), sirina, visina
TROG_ZID = 1.8                              # debljina zida posude
TROG_DUBINA = 14.0                          # vidljiva dubina unutrasnjosti


def _kvadar(x0, x1, y0, y1, z0, z1, mat, strane='xXyYzZ', unutra=False):
    """Kvadar kao skup pravougaonika; strane: x=-X, X=+X, y=dole, Y=gore, z=-Z, Z=+Z."""
    V, N, F = [], [], []
    sgn = -1 if unutra else 1
    lica = {
        'x': ([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], (-1, 0, 0)),
        'X': ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], (1, 0, 0)),
        'y': ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0)),
        'Y': ([(x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0)], (0, 1, 0)),
        'z': ([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], (0, 0, -1)),
        'Z': ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1)),
    }
    for k in strane:
        pts, n = lica[k]
        b = len(V)
        V += pts; N += [tuple(sgn * np.array(n, float))] * 4
        F += [(b, b + 1, b + 2), (b, b + 2, b + 3)]
    return Mesh(V, N, F, mat)


def zardinjera(xc, z0=0.5):
    """Pravougaona posuda za biljke, duza strana upravno na zid."""
    x0, x1 = xc - TROG_S / 2, xc + TROG_S / 2
    z1 = z0 + TROG_D
    t = TROG_ZID
    meshes = [
        _kvadar(x0, x1, 0, TROG_V, z0, z1, 'beton', strane='xXzZ'),
        # gornji rub (4 trake)
        _kvadar(x0, x1, TROG_V - 0.01, TROG_V, z0, z0 + t, 'beton', strane='Y'),
        _kvadar(x0, x1, TROG_V - 0.01, TROG_V, z1 - t, z1, 'beton', strane='Y'),
        _kvadar(x0, x0 + t, TROG_V - 0.01, TROG_V, z0, z1, 'beton', strane='Y'),
        _kvadar(x1 - t, x1, TROG_V - 0.01, TROG_V, z0, z1, 'beton', strane='Y'),
        # unutrasnjost (zidovi okrenuti ka unutra) i dno
        _kvadar(x0 + t, x1 - t, TROG_V - TROG_DUBINA, TROG_V, z0 + t, z1 - t, 'beton_unutra',
                strane='xXzZ', unutra=True),
        _kvadar(x0 + t, x1 - t, TROG_V - TROG_DUBINA, TROG_V - TROG_DUBINA + 0.01, z0 + t, z1 - t,
                'zemlja', strane='Y'),
    ]
    senke = [Senka([(x0, 0, z0), (x1, 0, z0), (x1, 0, z1), (x0, 0, z1)], poligon=True)]  # otisak
    for pts in ([(x0, 0, z0), (x0, TROG_V, z0), (x0, TROG_V, z1), (x0, 0, z1)],
                [(x1, 0, z0), (x1, TROG_V, z0), (x1, TROG_V, z1), (x1, 0, z1)],
                [(x0, 0, z1), (x1, 0, z1), (x1, TROG_V, z1), (x0, TROG_V, z1)],
                [(x0, 0, z0), (x1, 0, z0), (x1, TROG_V, z0), (x0, TROG_V, z0)],
                [(x0, TROG_V, z0), (x1, TROG_V, z0), (x1, TROG_V, z1), (x0, TROG_V, z1)]):
        senke.append(Senka(pts, poligon=True))
    return meshes, senke


# ---- raspored (265 cm): zardinjera | sto sa stolicom ispred | stolica | stolica |
#      sto sa stolicom ispred | zardinjera
STOLOVI_X = [66.25, 198.75]
STOLICA_RAZMAK = 42.0            # od centra stola do centra bocne stolice
STOLICA_Z = SED_SIR / 2 + 3.0    # centar bocne stolice od zida
STOLICA_ISPRED_Z = 56.0          # centar stolice ispred stola (sediste 16 cm ispod ploce)
ZARDINJERE_X = [TROG_S / 2, 265.0 - TROG_S / 2]


def raspored():
    """Lista (vrsta, x, z, napred)."""
    t1, t2 = STOLOVI_X
    return [
        ('zardinjera', ZARDINJERE_X[0], 0.5, None),
        ('sto', t1, 0, None),
        ('stolica', t1, STOLICA_ISPRED_Z, (0, 0, -1)),
        ('stolica', t1 + STOLICA_RAZMAK, STOLICA_Z, (-1, 0, 0)),
        ('stolica', t2 - STOLICA_RAZMAK, STOLICA_Z, (1, 0, 0)),
        ('sto', t2, 0, None),
        ('stolica', t2, STOLICA_ISPRED_Z, (0, 0, -1)),
        ('zardinjera', ZARDINJERE_X[1], 0.5, None),
    ]


def scena():
    meshes, senke = [], []
    for vrsta, x, z, napred in raspored():
        if vrsta == 'sto':
            m, s = stocic(x)
        elif vrsta == 'stolica':
            m, s = stolica(x, z, napred)
        else:
            m, s = zardinjera(x, z)
        meshes += m; senke += s
    return meshes, senke, raspored()


def gabariti():
    """Najveca izbocina od zida po vrsti predmeta (cm), merena iz 3D modela."""
    out = {}
    for vrsta, x, z, napred in raspored():
        if vrsta == 'sto':
            m, _ = stocic(x)
        elif vrsta == 'stolica':
            m, _ = stolica(x, z, napred)
        else:
            m, _ = zardinjera(x, z)
        zmax = max(mm.V[:, 2].max() for mm in m)
        out[vrsta] = max(out.get(vrsta, 0), zmax)
    out['ukupno'] = max(out.values())
    return out
