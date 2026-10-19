#!/usr/bin/env python3
"""Premium-Version des Freiraum-Sajta kao samostalan folder (dvoklik na index.html) i ZIP.

    python3 build_offline.py <izlazni-folder>

`src/shared` je link na `freiraum/src/assets` (zajedničke slike, reelsi, fontovi, site.js).
Kopira se samo ono što stranice koriste. Podstranice (Speisekarte, Spielraum, Datenschutz)
uzimaju se iz `freiraum/src` sa putanjama prepisanim na `shared/`.
Kao i u `freiraum/build_offline.py`: JSON i logo idu u assets/data.js, fontovi u CSS kao base64.
"""
import base64
import json
import pathlib
import re
import shutil
import sys
import urllib.parse

root = pathlib.Path(__file__).resolve().parent
src = root / 'src'
v1 = root.parent / 'freiraum' / 'src'
shared_src = v1 / 'assets'
out = pathlib.Path(sys.argv[1]).resolve()
site = out / 'Freiraum-Premium'
if site.exists():
    shutil.rmtree(site)
shutil.copytree(src, site, ignore=shutil.ignore_patterns('shared', 'data'))

SUBPAGES = ['speisekarte.html', 'spielraum.html', 'datenschutz.html']
for name in SUBPAGES:
    html = (v1 / name).read_text(encoding='utf-8')
    html = re.sub(r'''(["'`(])assets/''', r'\1shared/', html)
    if 'name="fr-assets"' not in html:
        html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="fr-assets" content="shared/">', 1)
    if name != 'spielraum.html':   # Spielraum behält seine eigene bunte Welt
        html = html.replace('</head>', '<link rel="stylesheet" href="assets/menu-premium.css">\n</head>', 1)
    (site / name).write_text(html, encoding='utf-8')

pages = list(site.glob('*.html')) + [site / 'assets/premium.js']
text = '\n'.join(p.read_text(encoding='utf-8') for p in pages)

# zajednički fajlovi: fontovi, slike, SVG, runtime, PDF jelovnika, korišćeni reelsi i dve AI sekvence
shared = site / 'shared'
for d in ('fonts', 'img', 'svg'):
    shutil.copytree(shared_src / d, shared / d)
for f in ('site.js', 'site.css'):
    shutil.copy2(shared_src / f, shared / f)
(shared / 'video').mkdir(parents=True)
for v in sorted(set(re.findall(r'(?:video/|v: *[\'"])(reel-[a-z0-9-]+|spiel-[a-z]+|feuer)', text))):
    for ext in ('.mp4', '.jpg'):
        if (shared_src / 'video' / (v + ext)).exists():
            shutil.copy2(shared_src / 'video' / (v + ext), shared / 'video' / (v + ext))
for s in sorted(set(re.findall(r'shared/seq/([a-z]+)', text))):
    shutil.copytree(shared_src / 'seq' / s, shared / 'seq' / s)
(site / 'data').mkdir()
shutil.copy2(v1 / 'data/menu.json', site / 'data/menu.json')


def data_uri(path):
    return 'data:image/svg+xml,' + urllib.parse.quote(path.read_text(encoding='utf-8'), safe='')


skeleton = json.loads((shared_src / 'svg/logo-skeleton.json').read_text(encoding='utf-8'))
data = {'data/menu.json': json.loads((v1 / 'data/menu.json').read_text(encoding='utf-8')),
        'shared/svg/logo-skeleton.json': skeleton}
(site / 'assets/data.js').write_text(
    'window.FR_DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
    + 'window.FR_LOGO_URI=' + json.dumps(data_uri(shared_src / 'svg/logo-freiraum.svg')) + ';\n', encoding='utf-8')

# Chrome blokira fontove sa file:// (CORS), pa ih ugrađujemo u CSS
def embed(css_path, prefix):
    css = css_path.read_text(encoding='utf-8')
    for font in list((site / 'assets/fonts').glob('*.woff2')) + list((shared / 'fonts').glob('*.woff2')):
        rel = ('fonts/' if font.parent == css_path.parent / 'fonts' else prefix) + font.name
        b64 = base64.b64encode(font.read_bytes()).decode()
        css = css.replace(f'url({rel})', f'url(data:font/woff2;base64,{b64})')
    css_path.write_text(css, encoding='utf-8')


embed(site / 'assets/premium.css', '../shared/fonts/')
embed(site / 'assets/menu-premium.css', '../shared/fonts/')
embed(shared / 'site.css', 'fonts/')

tagline = data_uri(shared_src / 'svg/tagline.svg')
for page in site.glob('*.html'):
    html = page.read_text(encoding='utf-8')
    html = re.sub(r'<link rel="preload"[^>]*as="font"[^>]*>\n?', '', html)
    html = html.replace('<script src="shared/site.js"></script>',
                        '<script src="assets/data.js"></script>\n<script src="shared/site.js"></script>', 1)
    html = html.replace('url(shared/svg/tagline.svg)', f'url("{tagline}")')
    page.write_text(html, encoding='utf-8')

(site / 'PROCITAJ.txt').write_text(
    'Freiraum Premium – nacrt sajta (nemistudio)\n\n'
    '1. Raspakuj ZIP i dva puta klikni na index.html (najbolje Chrome ili Safari).\n'
    '2. Skroluj polako: jutro (kafa iz Röstraum šoljice, doručak), podne, Spielraum,\n'
    '   16:59 → 17:00 i sajt prelazi u noć (kokteli, Sprizz, vatra i pica), pa bar, proslave, 18 godina.\n'
    '3. Prikaz telefona: Chrome → Cmd+Option+I → ikonica telefona → iPhone.\n', encoding='utf-8')

zip_path = shutil.make_archive(str(out / 'Freiraum-Premium'), 'zip', out, 'Freiraum-Premium')
print(zip_path, f'{pathlib.Path(zip_path).stat().st_size / 1e6:.1f} MB')
