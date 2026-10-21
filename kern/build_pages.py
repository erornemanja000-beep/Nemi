#!/usr/bin/env python3
"""KERN: kopira gotov build (dist/) u granu gh-pages, u podfolder /kern/.

    npm run build
    python3 build_pages.py <folder-grane-gh-pages>
"""
import pathlib
import shutil
import sys

root = pathlib.Path(__file__).resolve().parent
dist = root / 'dist'
if not (dist / 'index.html').exists():
    sys.exit('Nema dist/index.html: prvo pokreni "npm run build".')
out = pathlib.Path(sys.argv[1]).resolve()
site = out / 'kern'
if site.exists():
    shutil.rmtree(site)
shutil.copytree(dist, site)
(out / '.nojekyll').write_text('')
print(site, sum(1 for p in site.rglob('*') if p.is_file()), 'fajlova')
