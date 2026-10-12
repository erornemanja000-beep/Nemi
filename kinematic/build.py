#!/usr/bin/env python3
"""Pravi kinematic/dist/ za pravi hosting (Netlify i sl.).

- dodaje <!doctype html>, <head> i meta oznake (favicon, Open Graph)
- GSAP i Lenis učitava lokalno iz assets/js (bez CDN-a, zbog GDPR-a i brzine)
- formi dodaje data-endpoint="/" da bi je Netlify Forms primao
- slike: ako postoji src/assets/img/<slot>.webp kopira se; ako ne postoji, putanja se
  menja u Unsplash link iz images.json (hotlink, kako Unsplash i preporučuje), sa
  srcset-om da telefon skida manju verziju
"""
import json, pathlib, re, shutil

root = pathlib.Path(__file__).parent
src_dir, dist = root / 'src', root / 'dist'
src = (src_dir / 'index.html').read_text(encoding='utf-8')

# Biblioteke: CDN -> lokalne kopije iz vendor/
libs = {
    'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js': 'gsap.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js': 'ScrollTrigger.min.js',
    'https://unpkg.com/lenis@1.3.26/dist/lenis.min.js': 'lenis.min.js',
}
for url, name in libs.items():
    assert url in src, 'nema skripte ' + url
    src = src.replace(url, 'assets/js/' + name)

# Forma ide na Netlify Forms
src = src.replace('<form class="brief" id="brief"', '<form class="brief" id="brief" data-endpoint="/"', 1)

# Slike koje nisu skinute lokalno idu direktno sa Unsplasha
manifest = root / 'images.json'
images = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {}
local = {p.stem for p in (src_dir / 'assets' / 'img').glob('*.webp')}
sizes = {'reel': '100vw', 'push': '100vw', 'set': '100vw', 'grade': '(max-width: 1480px) 100vw, 1480px',
         'work': '(max-width: 700px) 80vw, 40vw', 'craft': '(max-width: 700px) 64px, 320px'}

def unsplash(slot, width=None):
    im = images[slot]
    w = width or im['w']
    h = round(im['h'] * w / im['w'])
    crop = '&crop=' + im['crop'] if im.get('crop') else ''
    return '%s?w=%d&h=%d&fit=crop%s&fm=webp&q=78' % (im['raw'], w, h, crop)

hotlinked = set()
def img_tag(m):
    tag, slot = m.group(0), m.group(1)
    if slot in local or slot not in images:
        return tag
    hotlinked.add(slot)
    w = images[slot]['w']
    widths = sorted({min(w, x) for x in (480, 960, 1600, w)})
    srcset = ', '.join('%s %dw' % (unsplash(slot, x), x) for x in widths)
    kind = slot.split('-')[0]
    tag = tag.replace('src="assets/img/%s.webp"' % slot, 'src="%s" srcset="%s" sizes="%s"' % (unsplash(slot), srcset, sizes.get(kind, '100vw')))
    return tag
src = re.sub(r'<img [^>]*src="assets/img/([\w-]+)\.webp"[^>]*>', img_tag, src)

# Ostale putanje (pozadine na timeline-u, lista za showreel u skripti)
def path_url(m):
    slot = m.group(1)
    if slot in local or slot not in images:
        return m.group(0)
    hotlinked.add(slot)
    return unsplash(slot, 1600 if images[slot]['w'] > 1600 else None)
src = re.sub(r'assets/img/([\w-]+)\.webp', path_url, src)

head_end = src.index('</style>') + len('</style>')
head, body = src[:head_end], src[head_end:]
meta = ('<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n'
        + ('<link rel="preconnect" href="https://images.unsplash.com">\n' if hotlinked else '') +
        '<meta property="og:title" content="Kinematic Shot">\n'
        '<meta property="og:description" content="Cinematography and film production studio in Belgrade.">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:image" content="assets/og.jpg">\n'
        '<meta name="twitter:card" content="summary_large_image">\n')
html = '<!doctype html>\n<html lang="en">\n<head>\n' + meta + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n'

if dist.exists():
    shutil.rmtree(dist)
shutil.copytree(src_dir / 'assets', dist / 'assets')
(dist / 'assets' / 'js').mkdir(exist_ok=True)
for name in libs.values():
    shutil.copy(root / 'vendor' / name, dist / 'assets' / 'js' / name)
(dist / 'index.html').write_text(html, encoding='utf-8')
print('dist/index.html', len(html), 'bytes; hotlinked from Unsplash:', ', '.join(sorted(hotlinked)) or 'nothing')
