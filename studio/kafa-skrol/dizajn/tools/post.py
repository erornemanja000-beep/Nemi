"""RGBA + pregledi. python3 -I post.py <outDir>"""
import sys, pathlib
from PIL import Image, ImageDraw, ImageFilter
out = pathlib.Path(sys.argv[1])
names = ['origin', 'flavor', 'roast']
paper = {'origin': (0xEE,0xE5,0xD5), 'flavor': (0xE6,0xD6,0xBF), 'roast': (0xED,0xB8,0xA0)}
labels = {}
for n in names:
    im = Image.open(out / f'etiketa-{n}.png')
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    im.save(out / f'etiketa-{n}.png', optimize=True)
    labels[n] = im
    print(n, im.size, im.mode, im.getextrema()[3])

# A: etiketa uklopljena u 400x500 (333x500), tri jedna do druge
fit = Image.new('RGB', (3 * 400 + 40, 500), (110, 58, 39))
for i, n in enumerate(names):
    t = labels[n].convert('RGB').resize((333, 500), Image.LANCZOS)
    fit.paste(t, (i * 420 + 33, 0))
fit.save(out / 'prev-fit-400x500.png')

# B: gruba kesa u kadru 1200x1500 kao kod blender-umetnik (kesa ~69 % visine), pa umanjeno na 400x500 i 600x750
def bag(n):
    W, H = 1200, 1500
    im = Image.new('RGBA', (W, H), (214, 195, 184, 255))      # staklena kartica preko SIP braon (#D6C3B8)
    bag_h = int(H * 0.69); s = bag_h / 216.0                   # px po mm
    bw = int(120 * s); x0 = (W - bw) // 2; y0 = (H - bag_h) // 2 + 30
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).ellipse((x0 - 20, y0 + bag_h - 30, x0 + bw + 20, y0 + bag_h + 40), fill=120)
    im.paste((60, 30, 20, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bag_h), radius=int(8 * s), fill=paper[n] + (255,))
    lab = labels[n].resize((bw, int(180 * s)), Image.LANCZOS)
    im.alpha_composite(lab, (x0, y0 + int((216 - 190) * s)))      # z 190 mm = 26 mm ispod vrha (var 16 + 10)
    d.rectangle((x0, y0, x0 + bw, y0 + int(16 * s)), fill=tuple(int(c * .9) for c in paper[n]) + (255,))  # var
    cx, cy, r = x0 + bw // 2, y0 + int((216 - 158) * s), int(8 * s)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 247, 240, 255), outline=(150, 140, 130, 255), width=3)  # ventil
    return im.convert('RGB')
for size in ((400, 500), (600, 750)):
    row = Image.new('RGB', (3 * size[0] + 40, size[1]), (110, 58, 39))
    for i, n in enumerate(names):
        row.paste(bag(n).resize(size, Image.LANCZOS), (i * (size[0] + 20), 0))
    row.save(out / f'prev-bag-{size[0]}x{size[1]}.png')
