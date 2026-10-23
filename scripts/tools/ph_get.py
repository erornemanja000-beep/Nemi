#!/usr/bin/env python3
"""Poly Haven: bezbedno preuzimanje glTF modela / HDRI / tekstura preko zvanicnog API-ja.
python3 -I ph_get.py <asset_id> <kind: gltf|hdri|tex> <res: 1k|2k|4k> <izlaz_dir> [--dry-run]
Proverava: https + host dl.polyhaven.org, relativne putanje bez '..', dozvoljene ekstenzije,
velicinu i md5 iz API-ja, magic bytes, i da .gltf referencira samo fajlove iz 'include'."""
import hashlib, json, os, re, sys, urllib.request
UA = {'User-Agent': 'Nemi-asset-fetch/1.0'}
HOST = 'https://dl.polyhaven.org/file/ph-assets/'
ALLOWED = {'gltf': {'.gltf', '.bin', '.jpg', '.png'}, 'hdri': {'.hdr', '.exr'}, 'tex': {'.jpg', '.png', '.exr'}}
MAGIC = {'.jpg': b'\xff\xd8\xff', '.png': b'\x89PNG', '.exr': b'\x76\x2f\x31\x01', '.hdr': b'#?'}
SAFE = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.\-/]*$')
MAX = 600 * 1024 * 1024

def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)

def plan(files, kind, res):
    out = []
    if kind == 'gltf':
        e = files['gltf'][res]['gltf']
        out.append((os.path.basename(e['url']), e))
        out += list(e.get('include', {}).items())
    elif kind == 'hdri':
        out.append((os.path.basename(files['hdri'][res]['hdr']['url']), files['hdri'][res]['hdr']))
    else:
        for m in ('Diffuse', 'nor_gl', 'Rough', 'AO', 'Displacement', 'arm'):
            if m in files and res in files[m]:
                e = files[m][res]['jpg']; out.append((os.path.basename(e['url']), e))
    for rel, e in out:
        ext = os.path.splitext(rel)[1].lower()
        if not SAFE.match(rel) or '..' in rel.split('/') or rel.startswith('/'):
            sys.exit(f'ODBIJENO: nesigurna putanja {rel!r}')
        if ext not in ALLOWED[kind]:
            sys.exit(f'ODBIJENO: ekstenzija {ext} ({rel})')
        if not e['url'].startswith(HOST):
            sys.exit(f'ODBIJENO: URL van dl.polyhaven.org: {e["url"]}')
        if not (0 < int(e['size']) <= MAX):
            sys.exit(f'ODBIJENO: velicina {e["size"]} ({rel})')
        if not re.fullmatch(r'[0-9a-f]{32}', e['md5']):
            sys.exit(f'ODBIJENO: nema md5 ({rel})')
    return out

def fetch(rel, e, dst):
    path = os.path.join(dst, rel)
    os.makedirs(os.path.dirname(path) or dst, exist_ok=True)
    h, h2, n = hashlib.md5(), hashlib.sha256(), 0
    with urllib.request.urlopen(urllib.request.Request(e['url'], headers=UA), timeout=120) as r, open(path + '.part', 'wb') as f:
        if not r.geturl().startswith(HOST):
            sys.exit(f'ODBIJENO: preusmerenje na {r.geturl()}')
        while chunk := r.read(1 << 20):
            n += len(chunk)
            if n > int(e['size']):
                sys.exit(f'ODBIJENO: {rel} veci od najavljenog')
            h.update(chunk); h2.update(chunk); f.write(chunk)
    if n != int(e['size']) or h.hexdigest() != e['md5']:
        os.remove(path + '.part'); sys.exit(f'ODBIJENO: md5/velicina se ne slazu za {rel}')
    ext = os.path.splitext(rel)[1].lower()
    with open(path + '.part', 'rb') as f:
        head = f.read(8)
    if ext in MAGIC and not head.startswith(MAGIC[ext]):
        os.remove(path + '.part'); sys.exit(f'ODBIJENO: {rel} nije {ext} (magic {head!r})')
    os.replace(path + '.part', path)
    return h2.hexdigest()

def check_gltf(dst, items):
    gl = [r for r, _ in items if r.endswith('.gltf')][0]
    doc = json.load(open(os.path.join(dst, gl)))
    allowed = {r for r, _ in items}
    for sec in ('buffers', 'images'):
        for b in doc.get(sec, []):
            u = b.get('uri')
            if u is not None and u not in allowed:
                sys.exit(f'ODBIJENO: {gl} referencira {u!r} van include liste')
    ext = set(doc.get('extensionsUsed', []))
    bad = {x for x in ext if not x.startswith(('KHR_materials_', 'KHR_texture_transform'))}
    if bad:
        sys.exit(f'ODBIJENO: neocekivane glTF ekstenzije {sorted(bad)}')

def main():
    aid, kind, res, dst, *rest = sys.argv[1:]
    if not re.fullmatch(r'[A-Za-z0-9_\-]+', aid):
        sys.exit('ODBIJENO: asset id')
    info = get_json(f'https://api.polyhaven.com/info/{aid}')
    files = get_json(f'https://api.polyhaven.com/files/{aid}')
    items = plan(files, kind, res)
    for rel, e in items:
        print(f'{rel}\t{e["size"]}\tmd5:{e["md5"]}')
    if '--dry-run' in rest:
        print('DRY-RUN ok:', aid, info.get('name'), 'autori:', list(info.get('authors', {})), 'licenca: CC0 (polyhaven.com/license)'); return
    os.makedirs(dst, exist_ok=True)
    manifest = []
    for rel, e in items:
        manifest.append({'file': rel, 'url': e['url'], 'md5': e['md5'], 'sha256': fetch(rel, e, dst)})
    if kind == 'gltf':
        check_gltf(dst, items)
    json.dump({'source': f'https://polyhaven.com/a/{aid}', 'license': 'CC0-1.0', 'authors': list(info.get('authors', {})),
               'files': manifest}, open(os.path.join(dst, 'IZVOR.json'), 'w'), indent=1)
    print('OK', dst)

if __name__ == '__main__':
    main()
