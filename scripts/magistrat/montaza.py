"""Fotomontaza: 2 zidna stocica + 4 stolice na fotografijama zida.

Pokretanje:  python3 scripts/magistrat/montaza.py
Ulaz:  magistrat/fotografije/zid_frontalno.jpg, magistrat/fotografije/trotoar.jpg
Izlaz: magistrat/*.jpg
"""
import os
import sys
import numpy as np
from PIL import Image
import scipy.ndimage as nd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kamera import kalibrisi_sliku1, kalibrisi_sliku4  # noqa: E402
from modeli import scena  # noqa: E402
from render import (Svetlo, rasterizuj, osenci, smanji, senke_na_fotografiji,  # noqa: E402
                    srgb_u_lin, lin_u_srgb)

KOREN = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FOTO = os.path.join(KOREN, 'magistrat', 'fotografije')
IZLAZ = os.path.join(KOREN, 'magistrat')


def roi_za(kam, meshes, W, H, margina=40):
    V = np.concatenate([m.V for m in meshes])
    p, z = kam.projektuj(V)
    p = p[z > 1]
    x0 = int(max(0, p[:, 0].min() - margina)); x1 = int(min(W, p[:, 0].max() + margina))
    y0 = int(max(0, p[:, 1].min() - margina)); y1 = int(min(H, p[:, 1].max() + margina))
    return x0, y0, x1, y1


def renderuj(foto, kam, zid_srgb, zaklon=None, ss=3, seme=1):
    """Vraca fotografiju sa senkama (linearno) i sloj objekata (premult, alfa, roi)."""
    slika = np.asarray(Image.open(foto).convert('RGB')).astype(float)
    H, W = slika.shape[:2]
    lin = srgb_u_lin(slika)
    meshes, senke, _ = scena()
    svetlo = Svetlo()
    # ekspozicija: beli zid (albedo ~0.6) mora da ispadne kao na fotografiji
    E_zid = svetlo.ozracenje(np.array([[0, 0, 1.0]]))[0]
    ekspozicija = (srgb_u_lin(zid_srgb).mean() / (0.6 * E_zid.mean() / np.pi))

    roi = roi_za(kam, meshes, W, H)
    # senke na zidu i trotoaru (pre objekata)
    senke_na_fotografiji(kam, lin, senke, svetlo, (0, 0, W, H))

    dub, nbuf, pbuf, mbuf = rasterizuj(kam, meshes, roi, ss=ss)
    boja, maska = osenci(kam, svetlo, nbuf, pbuf, mbuf, ekspozicija)
    x0, y0, x1, y1 = roi
    if zaklon is not None:
        # stepenik (visok ~12 cm) je blizi kameri: zaklanja samo najnize delove predmeta
        z = np.kron(zaklon[y0:y1, x0:x1], np.ones((ss, ss))) > 0.5
        maska = maska & ~(z & (pbuf[..., 1] < 12.0))
    premult = smanji(boja * maska[..., None], ss)
    alfa = smanji(maska.astype(float), ss)
    # blago omeksavanje kao kod kamere telefona + sum
    premult = nd.gaussian_filter(premult, (0.45, 0.45, 0))
    alfa = nd.gaussian_filter(alfa, 0.45)
    rng = np.random.default_rng(seme)
    premult = np.clip(premult + rng.normal(0, 0.0025, premult.shape) * alfa[..., None], 0, None)
    return lin, (premult, alfa, roi)


def sklopi(lin, sloj, podloga=None, kam=None):
    """Spaja sloj objekata sa fotografijom; podloga(lin, kam) crta po tlu/zidu
    pre objekata (npr. zone i kote, koje onda objekti prirodno prekrivaju)."""
    lin = lin.copy()
    if podloga is not None:
        podloga(lin, kam)
    premult, alfa, (x0, y0, x1, y1) = sloj
    lin[y0:y1, x0:x1] = lin[y0:y1, x0:x1] * (1 - alfa[..., None]) + premult
    return Image.fromarray(lin_u_srgb(lin).round().astype(np.uint8))


def montiraj(foto, kam, zid_srgb, ime, zaklon=None):
    lin, sloj = renderuj(foto, kam, zid_srgb, zaklon=zaklon)
    out = sklopi(lin, sloj)
    out.save(os.path.join(IZLAZ, ime), quality=93)
    return out


def main(koje=('1', '2')):
    os.makedirs(IZLAZ, exist_ok=True)
    if '1' in koje:
        k1, _, _ = kalibrisi_sliku1()
        montiraj(os.path.join(FOTO, 'zid_frontalno.jpg'), k1, np.array([192, 186, 181]),
                 'montaza_1_zid_frontalno.jpg')
    if '2' in koje:
        k4, _, _ = kalibrisi_sliku4()
        montiraj(os.path.join(FOTO, 'trotoar.jpg'), k4, np.array([212, 201, 195]),
                 'montaza_2_trotoar.jpg')


if __name__ == '__main__':
    main(sys.argv[1:] or ('1', '2'))
