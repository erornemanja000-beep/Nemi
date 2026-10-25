"""Voksel diorama „Würfelwelt": lebdeće ostrvo sa kafićem, drvetom i lampom.

Isti podaci idu u MagicaVoxel (diorama.vox), u Blender (blender_scena.py) i u Remotion (podaci.json).
Pokretanje: python3 motion/wuerfelwelt/voxel_welt.py
"""
import json
import math
import os
import struct

import numpy as np

W, D, H = 32, 32, 22
CX, CY = 16, 16
VRH = 9  # sloj trave na vrhu ostrva

# ime, boja (sRGB); redosled = indeks boje u MagicaVoxel-u (od 1)
BOJE = [
    ("trava", (112, 170, 76)),
    ("trava2", (92, 150, 64)),
    ("zemlja", (128, 86, 54)),
    ("zemlja2", (106, 70, 44)),
    ("kamen", (100, 98, 106)),
    ("kamen2", (80, 78, 86)),
    ("zid", (239, 234, 226)),
    ("zid2", (228, 221, 210)),
    ("krov", (24, 25, 28)),
    ("tenda", (255, 90, 36)),
    ("tenda2", (239, 234, 226)),
    ("prozor", (255, 190, 110)),
    ("vrata", (78, 50, 34)),
    ("staza", (198, 184, 160)),
    ("stablo", (94, 64, 42)),
    ("krosnja", (74, 142, 68)),
    ("krosnja2", (98, 164, 80)),
    ("cvet1", (255, 122, 150)),
    ("cvet2", (255, 214, 92)),
    ("stub", (34, 35, 38)),
    ("lampa", (255, 214, 150)),
]
INDEKS = {ime: i + 1 for i, (ime, _) in enumerate(BOJE)}
SVETLE = {"prozor", "lampa"}  # u Blender-u noću svetle

# vreme gradnje u Blender kadrovima (Remotion čita isto iz podaci.json)
PRVI_SLOJ = 1  # jedna kocka sama
OSTALI_OD = 24
KORAK = 3
SLETANJE = 9  # koliko kadrova pada jedan sloj


def napravi():
    rng = np.random.default_rng(7)
    g = np.zeros((W, D, H), dtype=np.uint8)
    c = INDEKS

    # ostrvo: na dnu jedna kocka, prema vrhu sve šire, ivica malo talasasta
    for z in range(VRH + 1):
        r = 0.5 + 13.0 * (z / VRH) ** 0.62
        for x in range(W):
            for y in range(D):
                ugao = math.atan2(y - CY, x - CX)
                rr = r * (1 + 0.07 * math.sin(3 * ugao + 1) + 0.04 * math.sin(5 * ugao))
                if (x - CX) ** 2 + (y - CY) ** 2 <= rr * rr:
                    if z == VRH:
                        ime = "trava" if rng.random() > 0.3 else "trava2"
                    elif z >= VRH - 3:
                        ime = "zemlja" if rng.random() > 0.35 else "zemlja2"
                    else:
                        ime = "kamen" if rng.random() > 0.35 else "kamen2"
                    g[x, y, z] = c[ime]

    # prva kocka (dno ostrva) je narandžasta: od nje sve počinje
    g[CX, CY, 0] = c["tenda"]

    # staza od vrata do ivice
    for y in range(2, 13):
        for x in (9, 10):
            if g[x, y, VRH]:
                g[x, y, VRH] = c["staza"]

    # kafić: fasada gleda ka -y
    z0 = VRH + 1
    for x in range(6, 15):
        for y in range(13, 20):
            for z in range(z0, z0 + 6):
                g[x, y, z] = c["zid"] if (x + z) % 5 else c["zid2"]
    for x in (9, 10):
        for z in range(z0, z0 + 3):
            g[x, 13, z] = c["vrata"]
    for x in (7, 8, 12, 13):
        for z in (z0 + 1, z0 + 2):
            g[x, 13, z] = c["prozor"]
        g[x, 13, z0 + 4] = c["prozor"]
    for y in (15, 16, 18):
        for z in (z0 + 1, z0 + 2, z0 + 4):
            g[6, y, z] = c["prozor"]
            g[14, y, z] = c["prozor"]
    # tenda iznad vrata i prozora, na pruge
    for x in range(6, 15):
        boja = c["tenda"] if x % 2 == 0 else c["tenda2"]
        g[x, 12, z0 + 3] = boja
        g[x, 11, z0 + 2] = boja
    # ravan krov sa prepustom
    for x in range(5, 16):
        for y in range(12, 21):
            g[x, y, z0 + 6] = c["krov"]

    # drvo
    for z in range(z0, z0 + 4):
        g[22, 21, z] = c["stablo"]
    for x in range(18, 27):
        for y in range(17, 26):
            for z in range(z0 + 3, z0 + 10):
                d = math.sqrt((x - 22) ** 2 + (y - 21) ** 2 + (z - (z0 + 6)) ** 2)
                if d <= 3.3 and rng.random() > 0.08:
                    g[x, y, z] = c["krosnja"] if rng.random() > 0.4 else c["krosnja2"]

    # ulična lampa pored staze
    for z in range(z0, z0 + 5):
        g[13, 8, z] = c["stub"]
    g[13, 8, z0 + 5] = c["lampa"]

    # cveće po travi
    trava = {c["trava"], c["trava2"]}
    postavljeno = 0
    while postavljeno < 16:
        x, y = rng.integers(0, W), rng.integers(0, D)
        if g[x, y, VRH] in trava and g[x, y, z0] == 0:
            g[x, y, z0] = c["cvet1"] if postavljeno % 2 else c["cvet2"]
            postavljeno += 1
    return g


def slojevi(g):
    """Za svaki z: koliko kocaka i u kom kadru počinje da pada."""
    out = []
    for z in range(H):
        n = int(np.count_nonzero(g[:, :, z]))
        if n == 0:
            continue
        i = len(out)
        start = PRVI_SLOJ if i == 0 else OSTALI_OD + (i - 1) * KORAK
        out.append({"z": z, "kocke": n, "start": start, "sleteo": start + SLETANJE})
    return out


def zapisi_vox(g, putanja):
    xs, ys, zs = np.nonzero(g)

    def chunk(oznaka, sadrzaj, deca=b""):
        return oznaka + struct.pack("<ii", len(sadrzaj), len(deca)) + sadrzaj + deca

    size = chunk(b"SIZE", struct.pack("<iii", W, D, H))
    tacke = bytearray()
    for x, y, z in zip(xs, ys, zs):
        tacke += bytes((int(x), int(y), int(z), int(g[x, y, z])))
    xyzi = chunk(b"XYZI", struct.pack("<i", len(xs)) + bytes(tacke))
    paleta = bytearray(256 * 4)
    for i, (_, (r, gg, b)) in enumerate(BOJE):
        paleta[i * 4 : i * 4 + 4] = bytes((r, gg, b, 255))
    rgba = chunk(b"RGBA", bytes(paleta))
    main = chunk(b"MAIN", b"", size + xyzi + rgba)
    with open(putanja, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 150) + main)


if __name__ == "__main__":
    ovde = os.path.dirname(os.path.abspath(__file__))
    g = napravi()
    zapisi_vox(g, os.path.join(ovde, "diorama.vox"))
    s = slojevi(g)
    podaci = {"slojevi": s, "ukupno": int(np.count_nonzero(g))}
    with open(os.path.join(ovde, "..", "src", "wuerfel-podaci.json"), "w") as f:
        json.dump(podaci, f, indent=1)
    print("kocaka:", podaci["ukupno"], "slojeva:", len(s), "poslednji sleće:", s[-1]["sleteo"])
