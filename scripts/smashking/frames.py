#!/usr/bin/env python3
"""Smash King: AI klipovi -> nizovi WebP kadrova za skrol (canvas), posebno za kompjuter i telefon.

    python3 frames.py smash  smashking/izvor/smash.mp4 smashking/src/assets/seq/smash
    python3 frames.py king   smashking/izvor/slaganje.mp4 smashking/izvor/kruna.mp4 smashking/src/assets/seq/king

smash: 16:9 kadar preko celog ekrana; telefon dobija uspravni isečak iz sredine (9:16).
king:  kvadratni kadar na crnoj pozadini; više klipova se lepi redom (kraj jednog = početak drugog).
Piše outdir/d/0001.webp..., outdir/m/0001.webp..., outdir/poster.jpg i outdir/seq.json.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

FPS = 15
# vrsta -> {d|m: (ffmpeg filter, WebP kvalitet)}
KINDS = {
    'smash': {'d': ('scale=1280:-2', 60), 'm': ('crop=ih*9/16:ih,scale=540:-2', 58)},
    'king': {'d': ('scale=960:960', 62), 'm': ('scale=640:640', 60)},
}


def run(*a):
    subprocess.run(a, check=True)


def main():
    kind, *srcs, out = sys.argv[1:]
    tmp = tempfile.mkdtemp()
    try:
        n = 0
        for i, src in enumerate(srcs):
            # prvi kadar sledećeg klipa je isti kao poslednji prethodnog, pa ga preskačemo
            skip = [] if i == 0 else ['-ss', str(1 / 24)]
            run('ffmpeg', '-v', 'error', '-y', *skip, '-i', src, '-vf', f'fps={FPS}', '-start_number', str(n + 1),
                f'{tmp}/%04d.png')
            n = len(glob.glob(f'{tmp}/*.png'))
        meta = {'count': n, 'fps': FPS, 'parts': []}
        for key, (vf, q) in KINDS[kind].items():
            d = os.path.join(out, key)
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            run('ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/%04d.png', '-vf', vf, '-c:v', 'libwebp', '-quality', str(q),
                '-compression_level', '6', f'{d}/%04d.webp')
            w, h = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
                                   f'{d}/0001.webp'], capture_output=True, text=True).stdout.strip().split(',')
            meta[key] = [int(w), int(h)]
        run('ffmpeg', '-v', 'error', '-y', '-i', f'{tmp}/0001.png', '-vf', KINDS[kind]['d'][0], '-q:v', '4',
            os.path.join(out, 'poster.jpg'))
        json.dump(meta, open(os.path.join(out, 'seq.json'), 'w'))
        size = {k: sum(os.path.getsize(f) for f in glob.glob(os.path.join(out, k, '*.webp'))) for k in ('d', 'm')}
        print(out, n, 'kadrova', {k: f'{v / 1e6:.1f} MB' for k, v in size.items()})
    finally:
        shutil.rmtree(tmp)


if __name__ == '__main__':
    main()
