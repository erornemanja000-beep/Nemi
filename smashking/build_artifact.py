#!/usr/bin/env python3
"""Smash King: verzija za pregled kao claude.ai Artifact (kad Netlify nije dostupan).

    python3 smashking/build_artifact.py <izlazni-folder>

Razlike u odnosu na src/: stranica bez <html>/<head>/<body> omotača (Artifact ga dodaje sam),
King sekvenca samo u jednom skupu kadrova (Artifact prima najviše 511 fajlova),
mapa se otvara kao link (Artifact ne dozvoljava iframe). Ispisuje i spisak fajlova po objavama (≤ 255).
"""
import json
import pathlib
import re
import shutil
import sys

root = pathlib.Path(__file__).resolve().parent
src = root / 'src'
out = pathlib.Path(sys.argv[1]).resolve()
if out.exists():
    shutil.rmtree(out)
shutil.copytree(src, out, ignore=lambda d, names: ['m'] if d.endswith('seq/king') else [])

page = out / 'index.html'
html = page.read_text(encoding='utf-8')
html = re.sub(r'<!doctype html>\s*', '', html, flags=re.I)
html = re.sub(r'</?(html|head|body)\b[^>]*>\s*', '', html)
html = re.sub(r'<meta charset="utf-8">\s*<meta name="viewport"[^>]*>\s*', '', html)
html = re.sub(r'<title>.*?</title>', '<title>Smash King Entwurf</title>', html, count=1)
html = html.replace('data-seq="king" data-count="196"', 'data-seq="king" data-set="d" data-count="196"')
html = re.sub(r'<button class="btn btn-ghost map-load" type="button" id="mapLoad"[^>]*>.*?</button>',
              '<a class="btn btn-ghost map-load" href="https://www.openstreetmap.org/?mlat=48.17674&amp;mlon=16.37641#map=17/48.17674/16.37641" '
              'target="_blank" rel="noopener" data-en="Open map ↗">Karte öffnen ↗</a>', html, flags=re.S)
page.write_text(html, encoding='utf-8')

# prva objava: sve osim kadrova, pa Smash; King ide u drugu
files = sorted((str(p.relative_to(out)) for p in out.rglob('*') if p.is_file() and p.name != 'index.html'),
               key=lambda f: (f.startswith('assets/seq/king'), f.startswith('assets/seq'), f))
first, rest = files[:248], files[248:]
(out.parent / 'publish_1.json').write_text(json.dumps([{'path': f} for f in first]))
(out.parent / 'publish_2.json').write_text(json.dumps([{'path': f} for f in rest]))
print(out, len(files) + 1, 'fajlova;', len(first), '+', len(rest), 'po objavama')
