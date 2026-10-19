#!/usr/bin/env python3
"""Pravi freiraum/dist/ za Netlify: kopira src/ i svakoj stranici dodaje noindex (nacrt za prezentaciju)."""
import pathlib
import shutil

root = pathlib.Path(__file__).parent
src, dist = root / 'src', root / 'dist'
if dist.exists():
    shutil.rmtree(dist)
shutil.copytree(src, dist)
for page in dist.glob('*.html'):
    html = page.read_text(encoding='utf-8')
    if 'name="robots"' not in html:
        html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
        page.write_text(html, encoding='utf-8')
size = sum(f.stat().st_size for f in dist.rglob('*') if f.is_file())
print(f'dist/ {len(list(dist.glob("*.html")))} Seiten, {size / 1e6:.1f} MB')
