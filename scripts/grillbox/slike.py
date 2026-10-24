#!/usr/bin/env python3
"""Grillbox: slike za sajt iz njihovih Wolt fotki.

    python3 scripts/grillbox/slike.py

Ulaz (grillbox/izvor/):
  wolt/*.jpg            originalne fotke sa Wolt-a (svetlo siva pozadina) i logo
  bez-pozadine/*.png    iste fotke bez pozadine (Artlist, Pixelcut Background Removal);
                        kaesekrainer-bacon i chilly su spojene sa AI izmenom (spoj.py, ai/*.png)
Izlaz (grillbox/src/assets/img/):
  menu/<jelo>-1000.webp, -560.webp   tanjir na providnoj pozadini, kvadrat
  emblem.webp                        logo isečen u krug (providni uglovi)
  favicon.png, apple-touch-icon.png, og.jpg
  cevapi-tamno.webp (Versprechen), hotdog-tamno.webp (Besuch), grill-tisch.webp (pokrivač mape)
"""
import pathlib

from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[2] / 'grillbox'
SRC, OUT = ROOT / 'izvor', ROOT / 'src' / 'assets' / 'img'
BG = (5, 4, 3)            # --bg iz sk.css
GLOW = (40, 20, 8)        # topli sjaj iza tanjira, kao b-glow


def plate(name):
    im = Image.open(SRC / 'bez-pozadine' / f'{name}.png').convert('RGBA')
    return im.crop(im.getchannel('A').getbbox())


def dark(size, center, radius):
    """tamna pozadina sa toplim radijalnim sjajem"""
    w, h = size
    bg = Image.new('RGB', size, BG)
    glow = Image.new('L', size, 0)
    cx, cy = center
    ImageDraw.Draw(glow).ellipse((cx - radius, cy - radius * .7, cx + radius, cy + radius * .7), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * .45))
    bg.paste(Image.new('RGB', size, GLOW), (0, 0), glow)
    return bg


def place(canvas, im, width, center):
    im = im.resize((round(width), round(im.height * width / im.width)), Image.LANCZOS)
    canvas.paste(im, (round(center[0] - im.width / 2), round(center[1] - im.height / 2)), im)


def menu():
    (OUT / 'menu').mkdir(parents=True, exist_ok=True)
    for name in ['cevape', 'pljeskavica', 'kaesekrainer', 'kaesekrainer-bacon', 'classic', 'chilly', 'bacon', 'double']:
        p = plate(name)
        side = round(p.width / .86)   # tanjir zauzima 86 % širine kvadrata
        sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        sq.paste(p, ((side - p.width) // 2, (side - p.height) // 2 + side // 40), p)
        for px in (1000, 560):
            sq.resize((px, px), Image.LANCZOS).save(OUT / 'menu' / f'{name}-{px}.webp', quality=82, method=6)


def logo():
    im = Image.open(SRC / 'wolt' / 'logo.jpg').convert('RGB')
    cx, cy, r = 252, 258, 236          # spoljna ivica belog prstena (izmereno na 510 px)
    box = (cx - r, cy - r, cx + r, cy + r)
    sq = im.crop(box)
    big = 4 * sq.width                 # maska crtana 4× veća, pa umanjena = glatka ivica
    mask = Image.new('L', (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    mask = mask.resize(sq.size, Image.LANCZOS)
    em = sq.copy(); em.putalpha(mask)
    em = em.resize((360, 360), Image.LANCZOS)
    em.save(OUT / 'emblem.webp', quality=90, method=6)
    em.resize((64, 64), Image.LANCZOS).save(OUT / 'favicon.png', optimize=True)
    # iOS ne podržava providnost: logo na crnom, sa malo vazduha
    touch = Image.new('RGB', (180, 180), (0, 0, 0))
    touch.paste(em.resize((164, 164), Image.LANCZOS), (8, 8), em.resize((164, 164), Image.LANCZOS))
    touch.save(OUT / 'apple-touch-icon.png', optimize=True)
    return em


def posters(em):
    # Versprechen: ćevapi, uspravno 800×1000 (natpis stoji dole preko slike)
    c = dark((800, 1000), (400, 430), 520)
    place(c, plate('cevape'), 1060, (430, 430))
    c.save(OUT / 'cevapi-tamno.webp', quality=82, method=6)
    # Besuch: hot dog, uspravno 765×1020
    c = dark((765, 1020), (382, 500), 500)
    place(c, plate('kaesekrainer'), 980, (382, 500))
    c.save(OUT / 'hotdog-tamno.webp', quality=82, method=6)
    # pokrivač mape 1360×765: tri tanjira
    c = dark((1360, 765), (680, 400), 760)
    place(c, plate('kaesekrainer'), 620, (330, 330))
    place(c, plate('cevape'), 600, (1040, 340))
    place(c, plate('double'), 700, (680, 470))
    c.save(OUT / 'grill-tisch.webp', quality=80, method=6)
    # og.jpg 1200×630: logo levo, Double Smash desno
    c = dark((1200, 630), (780, 330), 620)
    place(c, plate('double'), 760, (790, 330))
    place(c, em, 330, (220, 315))
    c.save(OUT / 'og.jpg', quality=86, optimize=True, progressive=True)


if __name__ == '__main__':
    menu()
    posters(logo())
    print('gotovo:', OUT)
