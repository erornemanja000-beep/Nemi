#!/usr/bin/env python3
"""Preuzima HDRI ili teksturu sa Poly Haven-a (CC0) po pravilima iz pregleda `bezbednost` (25. 10. 2026).

- samo API api.polyhaven.com i fajlovi sa https://dl.polyhaven.org/file/ph-assets/
- samo slike (.hdr, .exr, .jpg, .png); bez .blend, .fbx, .usd, .zip
- obavezan User-Agent, provera veličine, MD5 i prvih bajtova fajla
- svaki asset u svoj folder: motion/assets/polyhaven/<slug>/

Primeri:
  python3 tools/polyhaven/preuzmi.py hdri brown_photostudio_02 --res 2k
  python3 tools/polyhaven/preuzmi.py tekstura dark_wood --res 2k
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request

API = "https://api.polyhaven.com/files/"
DOZVOLJEN_PREFIKS = "https://dl.polyhaven.org/file/ph-assets/"
USER_AGENT = "Nemi-Studio-Blender/1.0"
MAX_BAJTOVA = 300 * 1024 * 1024
POTPISI = {
    ".hdr": [b"#?RADIANCE", b"#?RGBE"],
    ".exr": [b"\x76\x2f\x31\x01"],
    ".jpg": [b"\xff\xd8\xff"],
    ".png": [b"\x89PNG\r\n\x1a\n"],
}
MAPE = ["Diffuse", "nor_gl", "Rough", "AO", "Displacement", "arm"]
KOREN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "motion", "assets", "polyhaven"))


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(MAX_BAJTOVA + 1)


def preuzmi(info, folder):
    url = info["url"]
    if not url.startswith(DOZVOLJEN_PREFIKS) or ".." in url:
        sys.exit(f"odbijeno, nedozvoljen link: {url}")
    ext = os.path.splitext(url)[1].lower()
    if ext not in POTPISI:
        sys.exit(f"odbijeno, nedozvoljen format: {ext}")
    if info.get("size", 0) > MAX_BAJTOVA:
        sys.exit(f"odbijeno, prevelik fajl: {info['size']} B")
    podaci = get(url)
    if len(podaci) != info["size"]:
        sys.exit(f"veličina se ne poklapa: {len(podaci)} != {info['size']}")
    if hashlib.md5(podaci).hexdigest() != info["md5"]:
        sys.exit("MD5 se ne poklapa")
    if not any(podaci.startswith(p) for p in POTPISI[ext]):
        sys.exit(f"sadržaj nije {ext}")
    ime = os.path.basename(url)
    with open(os.path.join(folder, ime), "wb") as f:
        f.write(podaci)
    print(f"ok  {ime}  {len(podaci) // 1024} KB")
    return ime


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vrsta", choices=["hdri", "tekstura"])
    ap.add_argument("slug")
    ap.add_argument("--res", default="2k", choices=["1k", "2k", "4k"])
    a = ap.parse_args()
    if not a.slug.replace("_", "").isalnum():
        sys.exit("neispravno ime asseta")

    fajlovi = json.loads(get(API + a.slug))
    folder = os.path.join(KOREN, a.slug)
    os.makedirs(folder, exist_ok=True)
    preuzeto = []
    if a.vrsta == "hdri":
        preuzeto.append(preuzmi(fajlovi["hdri"][a.res]["hdr"], folder))
    else:
        for mapa in MAPE:
            if mapa in fajlovi and a.res in fajlovi[mapa]:
                formati = fajlovi[mapa][a.res]
                fmt = "jpg" if "jpg" in formati else "png"
                preuzeto.append(preuzmi(formati[fmt], folder))
    with open(os.path.join(folder, "IZVOR.txt"), "w") as f:
        f.write(f"https://polyhaven.com/a/{a.slug}\nLicenca: CC0 (polyhaven.com/license)\nFajlovi: {', '.join(preuzeto)}\n")


if __name__ == "__main__":
    main()
