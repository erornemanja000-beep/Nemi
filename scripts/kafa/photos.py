#!/usr/bin/env python3
"""Kafa skrol: izvedene fotografije (WebP -sm / -lg) iz licenciranih izvora, sa korekcijom boje ka paleti tokena.

    ~/.venvs/media/bin/python -I photos.py <studio/kafa-skrol/izvori/photos> <KafaSkrol/public/media/photos> \
        [--preview-dir <van repoa>] [ime ...]

Izvori su tudji JPEG-ovi: otvaraju se samo preko Pillow 13.0.0 sa formats=['JPEG'] (venv ~/.venvs/media).
Velicine kao u RealEstates: pejzaz -sm 828 / -lg 1920 px sirine, uspravne slike -sm 480 / -lg 900; WebP, kvalitet 78.
Korekcija boje (ista za sve, razlicita jacina po slici):
  1. ICC (Display P3 i slicno) -> sRGB;
  2. topli balans belog (w): vise crvene, manje plave;
  3. zelena i plava podrucja (hue) se prigusuju (d), da zelenilo ne odskace od terakote;
  4. tonska mapa ka paleti: crno -> #1B150D (ink-deep), belo -> #F4EEE4 (cream-light), mesano sa originalom (k).
"""
import argparse
import io
import os
import sys

from PIL import Image, ImageCms, ImageFilter, ImageStat

LO = (27, 21, 13)      # --pp-ink-deep
HI = (244, 238, 228)   # --pp-cream-light
QUALITY = 78

CREAM = (230, 221, 206)  # --pp-cream #E6DDCE

# ime: (izvor, isecak (l, t, r, b) u udelima, uspravno?, k, w, d[, sidro])
# sidro = (podrucje (l, t, r, b) u udelima isecka, ciljna boja): pozadina se podesi na tacnu boju sekcije
ITEMS = {
    'shop-1':    ('SHOP-1/SHOP-1.jpg',       (0, 0, 1, 1),                 True,  0.30, 0.02, 0.0),
    # pozadina fotografije = tacno krem tokena (#E6DDCE), da se spoji sa sekcijom prodavnice
    'shop-bg-1': ('ZRNA-2/ZRNA-2.jpg',       (0, 0, 1, 1),                 True,  0.20, 0.00, 0.0, ((0.1, 0.78, 0.9, 0.98), CREAM)),
    # kvadratna studijska fotografija zrna; donjih 6 % (svetlosivi rub) je odsecen
    'shop-bg-2': ('ZRNA-1/ZRNA-1.jpg',       (0, 0, 1, 0.94),              False, 0.20, 0.00, 0.0, ((0.1, 0.80, 0.9, 0.97), CREAM)),
    # zuti stub gore desno je odsecen
    'onama-1':   ('ONAMA-1/ONAMA-1.jpg',     (0, 0.35, 1, 1),              False, 0.30, 0.00, 0.0),
    'onama-2':   ('ONAMA-2/ONAMA-2.jpg',     (0, 0, 1, 1),                 False, 0.30, 0.00, 0.0),
    # iseceno iznad vage: natpis proizvodjaca na displeju i utisnuti natpis ispod posude ne ulaze u kadar
    'guide-1':   ('GUIDE-1/GUIDE-1-w4000.jpg', (0.23, 0.11, 0.77, 0.60),   False, 0.30, 0.02, 0.35),
    # leva petina (mlin sa zlatnim znakom) je odsecena
    'guide-2':   ('GUIDE-2/GUIDE-2.jpg',     (0.26, 0, 1, 1),              False, 0.30, 0.00, 0.0),
    # zamena za KONTAKT-1 (na meniju vidljiv natpis lokala, lice gosta): bec dvoriste bez ljudi
    'kontakt-1': ('KONTAKT-2/KONTAKT-2.jpg', (0, 0, 1, 1),                 True,  0.45, 0.07, 0.65),
}


def to_srgb(im, icc):
    if not icc:
        return im.convert('RGB')
    src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
    desc = ImageCms.getProfileDescription(src).strip().lower()
    if 'srgb' in desc:
        return im.convert('RGB')
    return ImageCms.profileToProfile(im.convert('RGB'), src, ImageCms.createProfile('sRGB'), outputMode='RGB')


def warm(im, w):
    if not w:
        return im
    r, g, b = im.split()
    r = r.point(lambda v: min(255, round(v * (1 + w))))
    b = b.point(lambda v: round(v * (1 - 1.3 * w)))
    return Image.merge('RGB', (r, g, b))


def mute_greens(im, d):
    """Prigusi zasicenost zelenih i plavih tonova (hue 55..200 od 255)."""
    if not d:
        return im
    h, s, v = im.convert('HSV').split()
    mask = h.point(lambda x: 255 if 55 <= x <= 200 else 0).filter(ImageFilter.GaussianBlur(6))
    s2 = s.point(lambda x: round(x * (1 - d)))
    s = Image.composite(s2, s, mask)
    return Image.merge('HSV', (h, s, v)).convert('RGB')


def anchor_to(im, box, target):
    """Pomnozi kanale tako da medijana izabranog podrucja bude ciljna boja."""
    W, H = im.size
    l, t, r, b = box
    med = ImageStat.Stat(im.crop((round(l * W), round(t * H), round(r * W), round(b * H)))).median
    gains = [target[c] / max(1, med[c]) for c in range(3)]
    return Image.merge('RGB', tuple(ch.point(lambda v, g=g: min(255, round(v * g))) for ch, g in zip(im.split(), gains)))


def palette_map(im, k):
    if not k:
        return im
    luts = [[round(LO[c] + (HI[c] - LO[c]) * (v / 255)) for v in range(256)] for c in range(3)]
    mapped = Image.merge('RGB', tuple(ch.point(luts[c]) for c, ch in enumerate(im.split())))
    return Image.blend(im, mapped, k)


def process(name, src_dir, out_dir, preview_dir):
    rel, crop, portrait, k, w, d, *anchor = ITEMS[name]
    path = os.path.join(src_dir, rel)
    with open(path, 'rb') as f:
        if f.read(3) != b'\xff\xd8\xff':
            sys.exit(f'{path}: nije JPEG (magic bytes)')
    im = Image.open(path, formats=['JPEG'])
    icc = im.info.get('icc_profile')
    im = to_srgb(im, icc)
    W, H = im.size
    l, t, r, b = crop
    im = im.crop((round(l * W), round(t * H), round(r * W), round(b * H)))
    im = warm(im, w)
    im = mute_greens(im, d)
    if anchor:
        im = anchor_to(im, *anchor[0])
    im = palette_map(im, k)
    sizes = {'sm': 480, 'lg': 900} if portrait else {'sm': 828, 'lg': 1920}
    for suffix, width in sizes.items():
        if im.width <= width:
            out = im
            width = im.width
        else:
            out = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        dst = os.path.join(out_dir, f'{name}-{suffix}.webp')
        out.save(dst, 'WEBP', quality=QUALITY, method=6)
        print(f'{dst}  {out.width}x{out.height}  {os.path.getsize(dst) / 1024:.0f} KB')
        if preview_dir and suffix == 'lg':
            out.save(os.path.join(preview_dir, f'{name}-lg.jpg'), quality=90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'), ap.add_argument('out'), ap.add_argument('names', nargs='*')
    ap.add_argument('--preview-dir', default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.preview_dir:
        os.makedirs(a.preview_dir, exist_ok=True)
    for name in a.names or ITEMS:
        process(name, a.src, a.out, a.preview_dir)


if __name__ == '__main__':
    main()
