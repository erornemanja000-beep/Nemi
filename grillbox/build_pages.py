#!/usr/bin/env python3
"""Grillbox: verzija za GitHub Pages (grana gh-pages), sajt u podfolderu /grillbox/.

    python3 grillbox/build_pages.py <folder-grane-gh-pages>

Kopira src/ u <folder>/grillbox/ i dodaje noindex (Entwurf, ne za Google).
Koren grane (index.html, .nojekyll) i ostali sajtovi u njoj ostaju kakvi jesu.
"""
import pathlib
import shutil
import sys

root = pathlib.Path(__file__).resolve().parent
out = pathlib.Path(sys.argv[1]).resolve()
site = out / 'grillbox'
if site.exists():
    shutil.rmtree(site)
shutil.copytree(root / 'src', site)
for page in site.glob('*.html'):
    html = page.read_text(encoding='utf-8')
    if 'name="robots"' not in html:
        html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
    page.write_text(html, encoding='utf-8')
(out / '.nojekyll').write_text('')
print(site, sum(1 for p in site.rglob('*') if p.is_file()), 'fajlova')
