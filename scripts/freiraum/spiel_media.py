#!/usr/bin/env python3
"""Spielraum-Polaroids aus dem heute.at-Beitrag (Video 1024×576 + Artikelfoto von Hari).

    python3 -I spiel_media.py <heute.mp4> <hari.jpg> <freiraum/src/assets>

Ausschnitte sind 4:5 und so gewählt, dass weder das „Heute“-Logo (oben rechts) noch der
Namensbalken (unten links) im Bild sind. Die Reporterin bekommt eine nahtlose Schleife mit Ton
(Tippen für Ton), die zwei Montagen sind stumm.
"""
import os
import subprocess
import sys

from PIL import Image

W, H = 544, 680
ENC = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '25', '-pix_fmt', 'yuv420p', '-movflags', '+faststart']

# (von, bis, x, y, Breite) – Höhe = Breite · 5/4
REPORTER = (4.4, 13.3, 310, 0, 461)
BAELLE = [(2.8, 4.1, 120, 0, 461), (75.2, 76.3, 400, 76, 400), (76.4, 78.7, 340, 70, 405), (26.8, 28.4, 380, 70, 405)]
PARTY = [(1.5, 2.7, 280, 0, 461), (0.0, 1.45, 60, 0, 461), (97.7, 100.0, 170, 0, 461), (100.1, 102.4, 230, 0, 461)]


def crop(x, y, w):
    return f'crop={w}:{w * 5 // 4}:{x}:{y},scale={W}:{H}:flags=lanczos,setsar=1,fps=25'


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def poster(mp4, at):
    run(['-ss', str(at), '-i', mp4, '-frames:v', '1', '-q:v', '3', mp4[:-4] + '.jpg'])


def reporter(src, dst, d=0.5):
    a, b, x, y, w = REPORTER
    n = b - a - d
    f = (f'[0:v]trim={a + d}:{b},setpts=PTS-STARTPTS,{crop(x, y, w)}[m];'
         f'[0:v]trim={a}:{a + d},setpts=PTS-STARTPTS,{crop(x, y, w)}[h];'
         f'[m][h]xfade=transition=fade:duration={d}:offset={n - d:.2f}[v];'
         f'[0:a]atrim={a + d}:{b},asetpts=PTS-STARTPTS[ma];[0:a]atrim={a}:{a + d},asetpts=PTS-STARTPTS[ha];'
         f'[ma][ha]acrossfade=d={d}[au]')
    run(['-i', src, '-filter_complex', f, '-map', '[v]', '-map', '[au]', *ENC, '-c:a', 'aac', '-b:a', '96k', dst])
    poster(dst, 4.0)


def montage(src, shots, dst):
    parts = ''.join(f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS,{crop(x, y, w)}[s{i}];' for i, (a, b, x, y, w) in enumerate(shots))
    f = parts + ''.join(f'[s{i}]' for i in range(len(shots))) + f'concat=n={len(shots)}:v=1[v]'
    run(['-i', src, '-filter_complex', f, '-map', '[v]', '-an', *ENC, dst])
    poster(dst, 0.4)


def hari(src, img_dir):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    cw = h * 4 // 5
    x = min(max(int(w * 0.52) - cw // 2, 0), w - cw)   # Hari sitzt knapp rechts der Mitte
    im = im.crop((x, 0, x + cw, h))
    im.resize((1080, 1350), Image.LANCZOS).save(os.path.join(img_dir, 'spielraum-hari.webp'), quality=80, method=6)
    im.resize((720, 900), Image.LANCZOS).save(os.path.join(img_dir, 'spielraum-hari-s.webp'), quality=78, method=6)


def main():
    src, photo, assets = sys.argv[1:]
    vid = os.path.join(assets, 'video')
    reporter(src, os.path.join(vid, 'spiel-heute.mp4'))
    montage(src, BAELLE, os.path.join(vid, 'spiel-baelle.mp4'))
    montage(src, PARTY, os.path.join(vid, 'spiel-party.mp4'))
    hari(photo, os.path.join(assets, 'img'))
    for n in ('spiel-heute', 'spiel-baelle', 'spiel-party'):
        p = os.path.join(vid, n + '.mp4')
        print(n, f'{os.path.getsize(p) / 1e3:.0f} KB')


if __name__ == '__main__':
    main()
