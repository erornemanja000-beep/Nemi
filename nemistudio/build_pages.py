#!/usr/bin/env python3
"""Nemi Studio: copies the finished build (dist/) into the gh-pages branch, folder /nemistudio/.

    npm run build
    python3 build_pages.py <gh-pages-folder>
"""
import pathlib
import shutil
import sys

root = pathlib.Path(__file__).resolve().parent
dist = root / 'dist'
if not (dist / 'index.html').exists():
    sys.exit('No dist/index.html: run "npm run build" first.')
out = pathlib.Path(sys.argv[1]).resolve()
site = out / 'nemistudio'
if site.exists():
    shutil.rmtree(site)
shutil.copytree(dist, site)
(out / '.nojekyll').write_text('')
print(site, sum(1 for p in site.rglob('*') if p.is_file()), 'files')
