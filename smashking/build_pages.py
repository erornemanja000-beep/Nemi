#!/usr/bin/env python3
"""Smash King: verzija za GitHub Pages (grana gh-pages), sajt u podfolderu /smashking/.

    python3 smashking/build_pages.py <folder-grane-gh-pages>

Kopira src/ u <folder>/smashking/, dodaje noindex (Entwurf, ne za Google),
u koren stavlja .nojekyll i index.html koji vodi na /smashking/.
"""
import pathlib
import shutil
import sys

root = pathlib.Path(__file__).resolve().parent
out = pathlib.Path(sys.argv[1]).resolve()
site = out / 'smashking'
if site.exists():
    shutil.rmtree(site)
shutil.copytree(root / 'src', site)
for page in site.glob('*.html'):
    html = page.read_text(encoding='utf-8')
    if 'name="robots"' not in html:
        html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
    page.write_text(html, encoding='utf-8')
(out / '.nojekyll').write_text('')
if not (out / 'index.html').exists():
    (out / 'index.html').write_text(
        '<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
        '<meta http-equiv="refresh" content="0; url=smashking/"><title>nemistudio</title>'
        '<a href="smashking/">Smash King</a>\n', encoding='utf-8')
print(site, sum(1 for p in site.rglob('*') if p.is_file()), 'fajlova')
