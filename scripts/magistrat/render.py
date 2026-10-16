"""Mali softverski renderer (z-buffer) i senke za fotomontazu."""
import numpy as np
from PIL import Image, ImageDraw
import scipy.ndimage as nd


def srgb_u_lin(c):
    c = np.asarray(c, float) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_u_srgb(c):
    c = np.clip(c, 0, 1)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


# ------------------------------------------------------------ osvetljenje
class Svetlo:
    """Pojednostavljeno okruzenje: trotoar je u senci zgrade, svetlo dolazi
    od neba i od suncem obasjane fasade preko puta (sa strane ulice, +Z)."""

    def __init__(self, nebo=1.0, fasada=1.0, zid=0.45, tlo=0.18):
        el = np.radians(np.arange(5, 90, 10.0))
        az = np.radians(np.arange(-175, 180, 10.0))
        E, A = np.meshgrid(el, az, indexing='ij')
        L = np.stack([np.cos(E) * np.sin(A), np.sin(E), np.cos(E) * np.cos(A)], -1).reshape(-1, 3)
        dO = (np.cos(E) * np.radians(10) ** 2).reshape(-1)
        e = E.reshape(-1); a = A.reshape(-1)
        rad = np.zeros((len(L), 3))
        nebo_boja = np.array([0.80, 0.90, 1.05]) * nebo
        fas_boja = np.array([1.15, 1.0, 0.78]) * fasada
        zid_boja = np.array([1.0, 0.96, 0.93]) * zid
        ispred = L[:, 2] > 0
        rad[:] = nebo_boja
        fas = ispred & (e < np.radians(40)) & (np.abs(a) < np.radians(75))
        rad[fas] = fas_boja
        iza = ~ispred & (e < np.radians(70))      # beli zid iza (iznad 70 je nebo)
        rad[iza] = zid_boja
        self.L, self.dO, self.rad, self.ispred = L, dO, rad, ispred
        self.tlo = np.array([0.95, 0.95, 1.0]) * tlo

    def ozracenje(self, n):
        """Ozracenje (RGB) za normale n (..., 3)."""
        sh = n.shape[:-1]
        n2 = n.reshape(-1, 3)
        E = np.empty_like(n2)
        for a in range(0, len(n2), 100000):    # u delovima, zbog memorije
            cos = np.clip(n2[a:a + 100000] @ self.L.T, 0, None)
            E[a:a + 100000] = (cos * self.dO) @ self.rad
        E += np.clip(-n2[:, 1:2], 0, None) * np.pi * self.tlo
        return E.reshape(sh + (3,))

    def okolina(self, r):
        """Sjaj okoline u smeru r (za odsjaj)."""
        y, z = r[..., 1], r[..., 2]
        out = np.empty(r.shape)
        nebo = np.array([0.80, 0.90, 1.05]) * 1.1
        fas = np.array([1.15, 1.0, 0.78]) * 1.5
        zid = np.array([1.0, 0.96, 0.93]) * 0.5
        tlo = np.array([0.95, 0.95, 1.0]) * 0.2
        el = np.arcsin(np.clip(y, -1, 1))
        t_fas = np.clip((np.radians(40) - el) / np.radians(15), 0, 1)[..., None]
        ispred = np.where((z > 0)[..., None], fas * t_fas + nebo * (1 - t_fas), zid)
        ispred = np.where((el > np.radians(70))[..., None], nebo, ispred)
        t_tlo = np.clip(-y / 0.15, 0, 1)[..., None]
        out = ispred * (1 - t_tlo) + tlo * t_tlo
        return out

    def tezine_ravni(self, n_ravni):
        """Tezine smerova za senke na ravni sa normalom n_ravni."""
        w = np.clip(self.L @ np.asarray(n_ravni, float), 0, None) * self.dO * self.rad.mean(1)
        w[~self.ispred] = 0      # iza zida nema svetla za tlo/zid
        return w


MATERIJALI = {
    'metal': dict(albedo=np.array([0.016, 0.017, 0.018]), spek=0.012, sjaj=0.4),
    'ploca': dict(albedo=np.array([0.018, 0.019, 0.020]), spek=0.015, sjaj=0.55),
    'guma': dict(albedo=np.array([0.02, 0.02, 0.02]), spek=0.02, sjaj=0.1),
    # zardinjera, boja "Sandbraun" (beton/fiberglas)
    'beton': dict(albedo=np.array([0.47, 0.43, 0.35]), spek=0.01, sjaj=0.1, tekstura=0.11),
    'beton_unutra': dict(albedo=np.array([0.20, 0.18, 0.15]), spek=0.0, sjaj=0.1, tekstura=0.07),
    'zemlja': dict(albedo=np.array([0.035, 0.028, 0.022]), spek=0.0, sjaj=0.1, tekstura=0.25),
}


def vrednosni_sum(P, skala):
    """Glatki 3D sum vrednosti u [0, 1] (za teksturu betona)."""
    q = P / skala
    i = np.floor(q); f = q - i; f = f * f * (3 - 2 * f)

    def h(ix, iy, iz):
        v = np.sin(ix * 127.1 + iy * 311.7 + iz * 74.7) * 43758.5453
        return v - np.floor(v)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = ((f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) *
                     (f[:, 2] if dz else 1 - f[:, 2]))
                out = out + w * h(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz)
    return out


# ------------------------------------------------------------ rasterizacija
def rasterizuj(kam, meshes, roi, ss=3):
    x0, y0, x1, y1 = roi
    w, h = (x1 - x0) * ss, (y1 - y0) * ss
    dub = np.full((h, w), np.inf)
    nbuf = np.zeros((h, w, 3))
    pbuf = np.zeros((h, w, 3))
    mbuf = np.full((h, w), -1, int)
    imena = list(MATERIJALI)
    for m in meshes:
        p, z = kam.projektuj(m.V)
        ps = (p - [x0, y0]) * ss
        mid = imena.index(m.mat)
        for (i, j, k) in m.F:
            za, zb, zc = z[i], z[j], z[k]
            if za <= 1 or zb <= 1 or zc <= 1:
                continue
            a, b, c = ps[i], ps[j], ps[k]
            bx0 = int(max(0, np.floor(min(a[0], b[0], c[0]))))
            bx1 = int(min(w, np.ceil(max(a[0], b[0], c[0])) + 1))
            by0 = int(max(0, np.floor(min(a[1], b[1], c[1]))))
            by1 = int(min(h, np.ceil(max(a[1], b[1], c[1])) + 1))
            if bx1 <= bx0 or by1 <= by0:
                continue
            D = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(D) < 1e-9:
                continue
            X, Y = np.meshgrid(np.arange(bx0, bx1) + 0.5, np.arange(by0, by1) + 0.5)
            l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / D
            l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / D
            l3 = 1 - l1 - l2
            unutra = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
            if not unutra.any():
                continue
            iz = l1 / za + l2 / zb + l3 / zc
            zz = 1 / iz
            sl = (slice(by0, by1), slice(bx0, bx1))
            bolje = unutra & (zz < dub[sl])
            if not bolje.any():
                continue
            q1, q2, q3 = (l1 / za / iz)[bolje], (l2 / zb / iz)[bolje], (l3 / zc / iz)[bolje]
            dub[sl][bolje] = zz[bolje]
            nbuf[sl][bolje] = q1[:, None] * m.N[i] + q2[:, None] * m.N[j] + q3[:, None] * m.N[k]
            pbuf[sl][bolje] = q1[:, None] * m.V[i] + q2[:, None] * m.V[j] + q3[:, None] * m.V[k]
            mbuf[sl][bolje] = mid
    return dub, nbuf, pbuf, mbuf


def osenci(kam, svetlo, nbuf, pbuf, mbuf, ekspozicija):
    imena = list(MATERIJALI)
    maska = mbuf >= 0
    n = nbuf[maska]; n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    P = pbuf[maska]
    v = kam.C - P; v /= np.linalg.norm(v, axis=1, keepdims=True)
    # normala uvek ka kameri (unutrasnjost cevi se ne vidi)
    okr = (n * v).sum(1) < 0
    n[okr] *= -1
    alb = np.zeros_like(n); spek = np.zeros(len(n)); sjaj = np.zeros(len(n))
    mm = mbuf[maska]
    for i, ime in enumerate(imena):
        s = mm == i
        if not s.any():
            continue
        mat = MATERIJALI[ime]
        alb[s] = mat['albedo']; spek[s] = mat['spek']; sjaj[s] = mat['sjaj']
        if mat.get('tekstura'):
            Ps = P[s]
            n_ = (0.5 * vrednosni_sum(Ps, 0.35) + 0.3 * vrednosni_sum(Ps, 1.7) +
                  0.2 * vrednosni_sum(Ps, 7.0)) - 0.5
            alb[s] *= (1 + 2 * mat['tekstura'] * n_)[:, None]
    E = svetlo.ozracenje(n)
    # ambijentalna okluzija: blizu poda i zida je tamnije
    ao = np.clip(0.55 + 0.45 * np.minimum(P[:, 1] / 25.0, 1) * 0.5 + 0.45 * np.minimum(P[:, 2] / 25.0, 1) * 0.5,
                 0, 1)[:, None]
    dif = alb * E / np.pi * ao
    r = 2 * (n * v).sum(1, keepdims=True) * n - v
    # hrapav odsjaj: mesavina smera odsjaja i normale
    rr = r * sjaj[:, None] + n * (1 - sjaj[:, None])
    rr /= np.linalg.norm(rr, axis=1, keepdims=True)
    fres = spek + (1 - spek) * (1 - np.clip((n * v).sum(1), 0, 1)) ** 5 * 0.12
    odsjaj = fres[:, None] * svetlo.okolina(rr) * (0.6 + 0.4 * ao)
    lin = (dif + odsjaj) * ekspozicija
    out = np.zeros(nbuf.shape)
    out[maska] = lin
    return out, maska


def smanji(arr, ss):
    h, w = arr.shape[:2]
    return arr.reshape(h // ss, ss, w // ss, ss, *arr.shape[2:]).mean((1, 3))


# ------------------------------------------------------------ senke na ravnima
class Ravan:
    """Mreza na ravni zida (Z=0) ili tla (Y=0) za racunanje senki."""

    def __init__(self, tip, u_opseg, v_opseg, cm_po_px=0.5):
        self.tip = tip
        self.u0, self.u1 = u_opseg; self.v0, self.v1 = v_opseg
        self.s = cm_po_px
        self.W = int((self.u1 - self.u0) / self.s); self.H = int((self.v1 - self.v0) / self.s)
        self.n = np.array([0, 0, 1.0]) if tip == 'zid' else np.array([0, 1.0, 0])

    def u_px(self, P):
        P = np.asarray(P, float)
        if self.tip == 'zid':
            u, v = P[..., 0], P[..., 1]
        else:
            u, v = P[..., 0], P[..., 2]
        return np.stack([(u - self.u0) / self.s, (v - self.v0) / self.s], -1)

    def projektuj_duz(self, P, L):
        """Projekcija tacaka P na ravan duz smera svetla L."""
        P = np.asarray(P, float)
        d = (P @ self.n) / (L @ self.n)
        return P - d[..., None] * L

    def okluzija(self, senke, svetlo):
        w = svetlo.tezine_ravni(self.n)
        uk = w.sum()
        acc = np.zeros((self.H, self.W))
        for L, wk in zip(svetlo.L, w):
            if wk <= 0:
                continue
            img = Image.new('L', (self.W, self.H), 0)
            d = ImageDraw.Draw(img)
            for s in senke:
                q = self.projektuj_duz(s.tacke, L)
                px = self.u_px(q)
                pts = [tuple(p) for p in px]
                if s.poligon:
                    d.polygon(pts, fill=255)
                else:
                    # sirina trake: precnik / sin ugla upada
                    sin = abs(L @ self.n)
                    sirina = max(1, int(round(2 * s.r / self.s / max(sin, 0.25) ** 0.5)))
                    d.line(pts, fill=255, width=sirina, joint='curve')
            acc += wk * (np.asarray(img, float) / 255.0)
        return acc / uk

    def uzorkuj(self, mapa, P):
        px = self.u_px(P)
        return nd.map_coordinates(mapa, [px[..., 1], px[..., 0]], order=1, mode='constant', cval=0.0)


def senke_na_fotografiji(kam, slika_lin, senke, svetlo, roi, jacina=1.0, tlo_z_max=300.0):
    """Zatamnjuje zid i trotoar na fotografiji tamo gde objekti zaklanjaju svetlo."""
    x0, y0, x1, y1 = roi
    zid = Ravan('zid', (-60, 330), (0, 140))
    tlo = Ravan('tlo', (-60, 330), (0, 140))
    okl_zid = nd.gaussian_filter(zid.okluzija(senke, svetlo), 1.2)
    okl_tlo = nd.gaussian_filter(tlo.okluzija(senke, svetlo), 1.2)
    # kontaktna senka uz donju ivicu punih predmeta (zardinjere)
    otisak = Image.new('L', (tlo.W, tlo.H), 0)
    do = ImageDraw.Draw(otisak)
    for s in senke:
        if s.poligon and np.all(np.abs(s.tacke[:, 1]) < 1e-6):
            do.polygon([tuple(p) for p in tlo.u_px(s.tacke)], fill=255)
    kont = nd.gaussian_filter(np.asarray(otisak, float) / 255.0, 5.0)   # ~2.5 cm
    okl_tlo = np.clip(okl_tlo + 0.9 * kont, 0, 1)
    X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
    d = kam.zrak(np.stack([X, Y], -1))
    C = kam.C
    with np.errstate(divide='ignore', invalid='ignore'):
        t_zid = -C[2] / d[..., 2]
        t_tlo = -C[1] / d[..., 1]
    P_zid = C + t_zid[..., None] * d
    P_tlo = C + t_tlo[..., None] * d
    ok_zid = (t_zid > 0) & (P_zid[..., 1] >= 0)
    ok_tlo = (t_tlo > 0) & (P_tlo[..., 2] >= 0) & (P_tlo[..., 2] <= tlo_z_max)
    uz = np.where(ok_zid & (~ok_tlo | (t_zid < t_tlo)), 1, 0)
    ut = np.where(ok_tlo & (uz == 0), 1, 0)
    o = np.zeros(X.shape)
    o += uz * zid.uzorkuj(okl_zid, P_zid)
    o += ut * tlo.uzorkuj(okl_tlo, P_tlo)
    f = 1 - jacina * np.clip(o, 0, 1)
    slika_lin[y0:y1, x0:x1] *= f[..., None]
    return o
