#!/usr/bin/env python3
"""„Vom Teig zum Feuer“: niz kvadratnih kadrova za skrol, sastavljen od neprekinutih delova njihovih reelsa.

    python3 -I pizza_seq.py <scratchpad/freiraum> <izlaz/seq/pizza> [--preview tabak.jpg]

Svaki deo: (reel, od, do, centar isečka po visini 0–1, korak). Između delova ide kratko pretapanje,
pa skrol ne „skače“ na rezovima. Izlaz: d/0001.webp (720 px), m/0001.webp (540 px), poster.jpg, seq.json
sa granicama koraka (steps) da stranica zna kad menja tekst.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

REELS = {
    'machen': 'ig/media/2026-08-09_Db1EiFUo9FD_0.mp4',
    'slice': 'ig/links/C8bc4q_MkK9_0.mp4',
    'trueffel': 'ig/media/2026-07-23_DbJLHs9I2rQ_0.mp4',
}
FPS = 15
FADE = 3   # kadrova pretapanja između delova

# korak priče -> delovi
STEPS = [
    ('teig', [('machen', 2.15, 2.68, .50), ('machen', 2.75, 3.50, .62), ('machen', 3.58, 4.34, .55)]),
    ('belag', [('trueffel', 2.92, 3.85, .52), ('trueffel', 6.10, 6.95, .50)]),
    ('ofen', [('machen', 5.58, 7.06, .45), ('machen', 7.14, 8.56, .38), ('trueffel', 2.20, 2.85, .45)]),
    ('feuer', [('slice', 2.80, 7.62, .57)]),
    ('genuss', [('machen', 10.99, 12.28, .62), ('slice', 11.65, 13.52, .56)]),
]
SIZES = {'d': (720, 58), 'm': (540, 54)}


def frames(src, a, b, cy, tmp):
    out = tempfile.mkdtemp(dir=tmp)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-to', str(b), '-i', src, '-vf',
                    f'fps={FPS},crop=iw:iw:0:(ih-iw)*{cy}', f'{out}/%04d.png'], check=True)
    return [Image.open(p).convert('RGB') for p in sorted(glob.glob(f'{out}/*.png'))]


def main():
    sp, dst = sys.argv[1], sys.argv[2]
    preview = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    tmp = tempfile.mkdtemp()
    seq, steps, heads = [], [], []
    try:
        for name, parts in STEPS:
            start = len(seq)
            for reel, a, b, cy in parts:
                fr = frames(os.path.join(sp, REELS[reel]), a, b, cy, tmp)
                heads.append((name, fr[0], fr[len(fr) // 2], fr[-1]))
                if seq and FADE:
                    for i in range(FADE):   # poslednji kadrovi prethodnog dela se pretapaju u prve kadrove ovog
                        t = (i + 1) / (FADE + 1)
                        seq[-FADE + i] = Image.blend(seq[-FADE + i], fr[i], t)
                    fr = fr[FADE:]
                seq.extend(fr)
            steps.append({'id': name, 'from': start, 'to': len(seq) - 1})
        if preview:
            tw = 180
            sheet = Image.new('RGB', (tw * 3, tw * len(heads)))
            for r, (_, *ims) in enumerate(heads):
                for c, im in enumerate(ims):
                    sheet.paste(im.resize((tw, tw)), (c * tw, r * tw))
            sheet.save(preview, quality=82)
        os.makedirs(dst, exist_ok=True)
        png = os.path.join(tmp, 'all')
        os.makedirs(png)
        for i, im in enumerate(seq):
            im.save(f'{png}/{i + 1:04d}.png')
        for key, (w, q) in SIZES.items():
            d = os.path.join(dst, key)
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{png}/%04d.png', '-vf', f'scale={w}:{w}',
                            '-c:v', 'libwebp', '-quality', str(q), '-compression_level', '6', f'{d}/%04d.webp'],
                           check=True)
        seq[0].resize((720, 720)).save(os.path.join(dst, 'poster.jpg'), quality=80)
        json.dump({'count': len(seq), 'fps': FPS, 'w': 720, 'h': 720, 'steps': steps},
                  open(os.path.join(dst, 'seq.json'), 'w'))
        size = {k: sum(os.path.getsize(f) for f in glob.glob(os.path.join(dst, k, '*.webp'))) / 1e6 for k in SIZES}
        print(dst, len(seq), 'kadrova', steps, {k: f'{v:.1f} MB' for k, v in size.items()})
    finally:
        shutil.rmtree(tmp)


if __name__ == '__main__':
    main()
