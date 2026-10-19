#!/usr/bin/env python3
"""Video -> niz WebP kadrova za skrol (canvas), posebno za kompjuter i telefon.

    python3 frames.py in.mp4 outdir/ [--fps 12] [--from 0 --to 8]

Piše outdir/d/0001.webp... (720 px širine), outdir/m/0001.webp... (540 px),
outdir/poster.jpg (prvi kadar) i outdir/seq.json {"count", "fps", "w", "h"}.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import tempfile

SIZES = {'d': (720, 55), 'm': (540, 52)}   # širina, WebP kvalitet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'), ap.add_argument('out')
    ap.add_argument('--fps', type=float, default=12)
    ap.add_argument('--from', dest='a', type=float, default=0)
    ap.add_argument('--to', dest='b', type=float, default=None)
    o = ap.parse_args()
    trim = ['-ss', str(o.a)] + (['-to', str(o.b)] if o.b else [])
    os.makedirs(o.out, exist_ok=True)
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', *trim, '-i', o.src, '-vf', f'fps={o.fps}', f'{tmp}/%04d.png'],
                       check=True)
        pngs = sorted(glob.glob(f'{tmp}/*.png'))
        for key, (w, q) in SIZES.items():
            d = os.path.join(o.out, key)
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/%04d.png', '-vf', f'scale={w}:-2',
                            '-c:v', 'libwebp', '-quality', str(q), '-compression_level', '6', f'{d}/%04d.webp'],
                           check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pngs[0], '-vf', 'scale=720:-2', '-q:v', '4',
                        os.path.join(o.out, 'poster.jpg')], check=True)
        h = int(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=height', '-of', 'csv=p=0',
                                os.path.join(o.out, 'd', '0001.webp')], capture_output=True, text=True).stdout)
        json.dump({'count': len(pngs), 'fps': o.fps, 'w': 720, 'h': h}, open(os.path.join(o.out, 'seq.json'), 'w'))
        size = {k: sum(os.path.getsize(f) for f in glob.glob(os.path.join(o.out, k, '*.webp'))) for k in SIZES}
        print(o.out, len(pngs), 'kadrova', {k: f'{v / 1e6:.1f} MB' for k, v in size.items()})
    finally:
        shutil.rmtree(tmp)


if __name__ == '__main__':
    main()
