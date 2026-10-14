#!/usr/bin/env python3
"""Builds the Nemi Studio site from src/ into dist/ (and an artifact preview).

src/index.html is the page skeleton. It pulls in:
  <!--@css-->   src/css/<name>.css in the CSS order below
  <!--@html-->  src/html/NN-*.html (sorted by name), the scenes inside <main>
  <!--@foot-->  src/html/footer.html
  <!--@js-->    src/js/<name>.js: the shared files first (one scope), every other module in its own { block }

All copy is written as {{Deutsch||English}}. The build writes one page per language:
  dist/index.html (de)  and  dist/en.html (en)

    python3 build.py                   # dist/
    python3 build.py --artifact DIR    # also DIR/nemi.html (de, artifact format) and DIR/en.html
    python3 build.py --form web3forms:KEY   # contact form via Web3Forms instead of Netlify Forms
"""
import argparse, json, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).parent
SRC, DIST = ROOT / 'src', ROOT / 'dist'
CSS = ['base', 'mini', 'intro', 'stage', 'manifesto', 'showroom', 'services', 'process', 'faq', 'contact', 'finale', 'footer', 'sound', 'responsive']
JS_SHARED = ['core', 'data', 'mini', 'fx', 'voice', 'particles']
JS_MODULES = ['intro', 'stage', 'manifesto', 'showroom', 'services', 'process', 'faq', 'contact', 'finale', 'footer', 'nav', 'sound', 'main']
LANGS = [('de', 'index.html'), ('en', 'en.html')]
CDN = {
    'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js': 'gsap.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js': 'ScrollTrigger.min.js',
    'https://unpkg.com/lenis@1.3.26/dist/lenis.min.js': 'lenis.min.js',
}
GOOGLE_FONTS = ('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,200..800'
                '&family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..700'
                '&family=Geist+Mono:wght@300..600&family=Instrument+Serif:ital@0;1&display=swap')
MARK = re.compile(r'\{\{(.*?)\|\|(.*?)\}\}', re.S)


def read(path):
    return path.read_text(encoding='utf-8') if path.exists() else ''


def split_lang(text, i, where):
    out = MARK.sub(lambda m: m.group(1 + i), text)
    if '{{' in out:
        line = out[:out.index('{{')].count('\n') + 1
        sys.exit('build: unclosed {{ marker in %s near line %d' % (where, line))
    return out


def assemble():
    """Returns the page in artifact format (starts with <title>, no doctype), still with {{de||en}} markers."""
    skel = read(SRC / 'index.html')
    css = '\n'.join(read(SRC / 'css' / (n + '.css')) for n in CSS if (SRC / 'css' / (n + '.css')).exists())
    scenes = '\n'.join(read(p) for p in sorted((SRC / 'html').glob('[0-9]*.html')))
    foot = read(SRC / 'html' / 'footer.html')
    shared = [read(SRC / 'js' / (n + '.js')) for n in JS_SHARED if (SRC / 'js' / (n + '.js')).exists()]
    blocks = ['{ /* %s */\n%s}' % (n, read(SRC / 'js' / (n + '.js'))) for n in JS_MODULES if (SRC / 'js' / (n + '.js')).exists()]
    js = "(() => {\n'use strict';\n" + '\n'.join(shared + blocks) + '\n})();'
    page = skel.replace('<!--@css-->', css).replace('<!--@html-->', scenes).replace('<!--@foot-->', foot).replace('<!--@js-->', js)
    images = json.loads(read(ROOT / 'images.json') or '{}')
    credits = '\n'.join('<li><a href="%s?utm_source=nemi_studio&amp;utm_medium=referral" target="_blank" rel="noopener">%s</a></li>'
                        % (im['profile'], im['photographer']) for im in images.values())
    return page.replace('<!--CREDITS-->', credits), images


def head_body(page):
    """Splits the artifact-format page after the early inline script that sets html classes."""
    cut = page.index('</script>', page.index("classList.add('js')")) + len('</script>')
    return page[:cut], page[cut:]


def unsplash(im, w=1600):
    h = round(im['h'] * w / im['w'])
    return '%s?w=%d&h=%d&fit=crop&fm=webp&q=78' % (im['raw'], w, h)


def build_dist(page, images, form, site_url):
    local = {p.stem for p in (SRC / 'assets' / 'img').glob('*.webp')}
    missing = [s for s in images if s not in local]
    for slot in missing:
        page = page.replace('assets/img/%s.webp' % slot, unsplash(images[slot]))
    for url, name in CDN.items():
        if url not in page:
            sys.exit('build: missing script ' + url)
        page = page.replace(url, 'assets/js/' + name)
    if form.startswith('web3forms:'):
        page = page.replace('<form class="form" id="brief"', '<form class="form" id="brief" data-web3forms="%s"' % form.split(':', 1)[1], 1)
    elif form == 'netlify':
        page = page.replace('<form class="form" id="brief"', '<form class="form" id="brief" data-endpoint="/" data-netlify="true" netlify-honeypot="website"', 1)
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC / 'assets', DIST / 'assets')
    (DIST / 'assets' / 'js').mkdir(exist_ok=True)
    for name in CDN.values():
        shutil.copy(ROOT / 'vendor' / name, DIST / 'assets' / 'js' / name)
    base = site_url.rstrip('/') + '/' if site_url else ''
    for i, (lang, fname) in enumerate(LANGS):
        text = split_lang(page, i, fname)
        head, body = head_body(text)
        alt = ''.join('<link rel="alternate" hreflang="%s" href="%s%s">\n' % (l, base, '' if f == 'index.html' else f) for l, f in LANGS)
        meta = ('<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n' + alt +
                ('<link rel="preconnect" href="https://images.unsplash.com">\n' if missing else '') +
                '<meta property="og:type" content="website">\n<meta property="og:title" content="Nemi Studio">\n'
                '<meta property="og:image" content="%sassets/og-%s.jpg">\n<meta property="og:locale" content="%s">\n'
                '<meta name="twitter:card" content="summary_large_image">\n' % (base, lang, 'de_AT' if lang == 'de' else 'en_GB'))
        html = '<!doctype html>\n<html lang="%s">\n<head>\n%s%s\n</head>\n<body>\n%s\n</body>\n</html>\n' % (lang, meta, head, body)
        (DIST / fname).write_text(html, encoding='utf-8')
        print('dist/%s %d KB' % (fname, len(html.encode()) // 1024))
    if missing:
        print('NOTE: %d photos are not in src/assets/img, dist loads them from images.unsplash.com '
              '(run fetch_images.py on an open network to self-host them).' % len(missing))


def build_artifact(page, out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    page = re.sub(r'<link rel="preload"[^>]*>\n?', '', page)
    page = page.replace('<link rel="stylesheet" href="assets/fonts/fonts.css">', '<link rel="stylesheet" href="%s">' % GOOGLE_FONTS)
    for i, (lang, fname) in enumerate(LANGS):
        text = split_lang(page, i, fname)
        if lang == 'de':
            (out / 'nemi.html').write_text(text, encoding='utf-8')
        else:
            head, body = head_body(text)
            (out / fname).write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                                     '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                                     + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n', encoding='utf-8')
    print('artifact:', out / 'nemi.html', '+', out / 'en.html')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--form', default='netlify', help='netlify | web3forms:KEY | none')
    ap.add_argument('--site-url', default='', help='e.g. https://nemistudio.at (absolute og:image and hreflang URLs)')
    ap.add_argument('--artifact', help='folder for the artifact preview files')
    a = ap.parse_args()
    page, images = assemble()
    build_dist(page, images, a.form, a.site_url)
    if a.artifact:
        build_artifact(page, a.artifact)
