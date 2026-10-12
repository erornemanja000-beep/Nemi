#!/usr/bin/env python3
"""Pravi sajt/dist/ za pravi hosting: dodaje <!doctype html>, <head> i kopira assets."""
import pathlib, re, shutil
root = pathlib.Path(__file__).parent
src = (root / 'src' / 'index.html').read_text(encoding='utf-8')
head_end = src.index('</style>') + len('</style>')
head, body = src[:head_end], src[head_end:]
html = ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="theme-color" content="#F6DADC">\n<link rel="icon" href="assets/img/don-badge.png">\n'
        + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
dist = root / 'dist'
if dist.exists(): shutil.rmtree(dist)
shutil.copytree(root / 'src' / 'assets', dist / 'assets')
(dist / 'index.html').write_text(html, encoding='utf-8')
# ostale stranice (npr. datenschutz.html) su već pune HTML stranice
for extra in (root / 'src').glob('*.html'):
    if extra.name != 'index.html':
        shutil.copy(extra, dist / extra.name)
print('dist/index.html', len(html), 'bytes')
