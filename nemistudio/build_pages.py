#!/usr/bin/env python3
"""Nemi Studio: copies the finished build (dist/) into the gh-pages branch, folder /nemistudio/.

    npm run build
    python3 build_pages.py <gh-pages-folder>

The same branch feeds Cloudflare (nemistudio.at): wrangler.jsonc and cloudflare/ go to its root,
with the byte sizes of the films for the Worker that answers range requests.
"""
import json
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
cf = out / 'cloudflare'
cf.mkdir(exist_ok=True)
shutil.copy(root / 'cloudflare' / 'worker.js', cf / 'worker.js')
shutil.copy(root / 'cloudflare' / 'wrangler.jsonc', out / 'wrangler.jsonc')
sizes = {'/' + p.relative_to(site).as_posix(): p.stat().st_size for p in sorted((site / 'v').glob('*.mp4'))}
(cf / 'sizes.json').write_text(json.dumps(sizes, indent=1) + '\n')
print(site, sum(1 for p in site.rglob('*') if p.is_file()), 'files')
