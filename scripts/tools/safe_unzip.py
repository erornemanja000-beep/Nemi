#!/usr/bin/env python3
"""python3 -I safe_unzip.py <arhiva.zip> <izlaz_dir> [ext,ext]  - raspakuje SAMO ravne .jpg/.png (podrazumevano),
bez podfoldera, '..', symlinkova i sa proverom magic bytes. Sve ostalo se preskace i ispisuje."""
import os, re, stat, sys, zipfile
src, out = sys.argv[1], sys.argv[2]
exts = (sys.argv[3] if len(sys.argv) > 3 else 'jpg,png').split(',')
MAGIC = {'jpg': b'\xff\xd8\xff', 'png': b'\x89PNG', 'exr': b'\x76\x2f\x31\x01'}
os.makedirs(out, exist_ok=True)
z = zipfile.ZipFile(src)
for i in z.infolist():
    n, b = i.filename, os.path.basename(i.filename)
    ext = b.rsplit('.', 1)[-1].lower() if '.' in b else ''
    link = stat.S_ISLNK(i.external_attr >> 16)
    if i.is_dir():
        continue
    if link or n != b or ext not in exts or not re.fullmatch(r'[A-Za-z0-9_\-]+\.[a-z]+', b) or i.file_size > 300_000_000:
        print('PRESKACEM', n); continue
    data = z.read(i)
    if not data.startswith(MAGIC[ext]):
        print('PRESKACEM (nije pravi', ext + ')', n); continue
    dst = os.path.join(out, b)
    if os.path.exists(dst):
        print('PRESKACEM (vec postoji)', n); continue
    with open(dst, 'xb') as f:
        f.write(data)
    print('OK', b, len(data))
