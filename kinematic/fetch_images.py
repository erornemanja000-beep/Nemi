#!/usr/bin/env python3
"""Skida Unsplash fotografije iz images.json u src/assets/img/<slot>.webp.

Unsplash (imgix) sam iseče i smanji sliku na zadatu veličinu, pa nema obrade ovde.
Radi samo ako mreža dozvoljava images.unsplash.com. Bez skinutih slika build.py
u dist/ stavlja direktne Unsplash linkove, pa sajt i dalje radi na hostingu.

    python3 kinematic/fetch_images.py            # sve slike
    python3 kinematic/fetch_images.py reel-1     # samo jedna
"""
import json, pathlib, sys, urllib.request

root = pathlib.Path(__file__).parent
images = json.loads((root / 'images.json').read_text(encoding='utf-8'))
out = root / 'src' / 'assets' / 'img'
out.mkdir(parents=True, exist_ok=True)
only = set(sys.argv[1:])
for slot, im in images.items():
    if only and slot not in only:
        continue
    crop = '&crop=' + im['crop'] if im.get('crop') else ''
    url = '%s?w=%d&h=%d&fit=crop%s&fm=webp&q=78' % (im['raw'], im['w'], im['h'], crop)
    data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'kinematic-build'}), timeout=60).read()
    (out / (slot + '.webp')).write_bytes(data)
    print(slot, len(data) // 1024, 'KB', '·', im['photographer'])
