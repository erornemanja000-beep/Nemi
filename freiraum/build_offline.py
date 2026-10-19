#!/usr/bin/env python3
"""Pravi verziju sajta koja radi i bez servera (dvoklik na index.html) i pakuje je u ZIP.

    python3 build_offline.py <izlazni-folder>

Pregledači ne dozvoljavaju fetch() sa file://, pa se JSON podaci i SVG maske
ugrađuju direktno (assets/data.js, data: URI).
"""
import base64
import json
import pathlib
import re
import shutil
import sys
import urllib.parse

root = pathlib.Path(__file__).parent
src = root / 'src'
out = pathlib.Path(sys.argv[1]).resolve()
site = out / 'Freiraum-Entwurf'
if site.exists():
    shutil.rmtree(site)
shutil.copytree(src, site, ignore=shutil.ignore_patterns('pdf'))   # PDF-Karte gehört nicht auf die Seite


def data_uri(path):
    return 'data:image/svg+xml,' + urllib.parse.quote(path.read_text(encoding='utf-8'), safe='')


data = {
    'data/menu.json': json.loads((src / 'data/menu.json').read_text(encoding='utf-8')),
    'assets/svg/logo-skeleton.json': json.loads((src / 'assets/svg/logo-skeleton.json').read_text(encoding='utf-8')),
}
(site / 'assets/data.js').write_text(
    'window.FR_DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
    + 'window.FR_LOGO_URI=' + json.dumps(data_uri(src / 'assets/svg/logo-freiraum.svg')) + ';\n',
    encoding='utf-8')

# Chrome blokira fontove sa file:// (CORS), pa ih ugrađujemo u CSS
css_path = site / 'assets/site.css'
css = css_path.read_text(encoding='utf-8')
for font in (src / 'assets/fonts').glob('*.woff2'):
    b64 = base64.b64encode(font.read_bytes()).decode()
    css = css.replace(f'url(fonts/{font.name})', f'url(data:font/woff2;base64,{b64})')
css_path.write_text(css, encoding='utf-8')

tagline = data_uri(src / 'assets/svg/tagline.svg')
for page in site.glob('*.html'):
    html = page.read_text(encoding='utf-8')
    html = re.sub(r'<link rel="preload"[^>]*as="font"[^>]*>\n?', '', html)
    html = html.replace('<script src="assets/site.js"></script>',
                        '<script src="assets/data.js"></script>\n<script src="assets/site.js"></script>', 1)
    html = html.replace('url(assets/svg/tagline.svg)', f'url("{tagline}")')
    page.write_text(html, encoding='utf-8')

(site / 'PROCITAJ.txt').write_text(
    'Freiraum – nacrt sajta (nemistudio)\n\n'
    '1. Dva puta klikni na index.html (najbolje u Chrome-u ili Safariju).\n'
    '2. Klikni „Eintreten“ i skroluj.\n'
    '3. Prikaz telefona: Chrome → Cmd+Option+I → ikonica telefona → iPhone.\n\n'
    'Za prezentaciju: dodaj ?demo=1 na kraj adrese u pregledaču za panel\n'
    '(doba dana, Božić, jezik).\n', encoding='utf-8')

zip_path = shutil.make_archive(str(out / 'Freiraum-Entwurf'), 'zip', out, 'Freiraum-Entwurf')
size = pathlib.Path(zip_path).stat().st_size / 1e6
print(zip_path, f'{size:.1f} MB')
