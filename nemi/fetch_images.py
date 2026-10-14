#!/usr/bin/env python3
"""Downloads the Unsplash photos listed in images.json into src/assets/img/<slot>.webp (1600x1000).

Runs on the hosting build (Netlify / Cloudflare) before build.py, so the live site serves
its own images (no requests to Unsplash from the visitor's browser, which keeps the
privacy page true). If a download fails, build.py falls back to loading that photo
from Unsplash, so the build never breaks.

    python3 fetch_images.py
"""
import json, pathlib, sys, urllib.request

root = pathlib.Path(__file__).parent
images = json.loads((root / 'images.json').read_text(encoding='utf-8'))
out = root / 'src' / 'assets' / 'img'
out.mkdir(parents=True, exist_ok=True)
ok = 0
for slot, im in images.items():
    url = '%s?w=%d&h=%d&fit=crop&fm=webp&q=78' % (im['raw'], im['w'], im['h'])
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'nemi-build'}), timeout=60).read()
        (out / (slot + '.webp')).write_bytes(data)
        ok += 1
        print(slot, len(data) // 1024, 'KB')
    except Exception as e:  # keep building with the hotlink fallback
        print('skip', slot, e, file=sys.stderr)
print('%d of %d photos saved' % (ok, len(images)))
