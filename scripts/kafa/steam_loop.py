#!/usr/bin/env python3
"""Kafa skrol: para iz stock snimka -> petlja na cistoj crnoj za `mix-blend-mode: screen`.

    ~/.venvs/media/bin/python -I steam_loop.py <izvor.mp4> <izlaz_dir> <ime> \
        --crop X Y W H --width 900 [--ss 0] [--t 12] [--start 0] [--frames 120] \
        [--xfade 24] [--fps 24] [--black 3] [--gain 2.2] [--fade 0.12 0.08 0.10] \
        [--flat] [--transpose 2] [--tint 1.0 0.965 0.91] [--seq 30] [--preview 0x6E3A27 --preview-dir <van repoa>]

Postupak (izvor je tudj fajl, pa se dekodira samo izolovano, kao u izvori-i-licence.md):
1. `unshare -rn ffmpeg ... -f mov` iseca (crop), po potrebi rotira (transpose) i smanjuje kadar, daje sirove RGB kadrove.
2. Ploca pozadine = minimum (po pikselu) svih zamucenih kadrova. Para samo posvetli piksel, pa je minimum cista pozadina.
3. Para po kadru = kadar - ploca (sivo, tamna pozadina i vinjeta postaju 0), pa levels (crna tacka --black, pojacanje --gain).
4. Ivice se utope u crno (gore, dole, levo/desno), da `screen` ne pokaze rez isecka.
5. Petlja: --frames kadrova + prelaz (--xfade kadrova) iz repa u pocetak, bez soka na spoju.
6. Izlaz: <ime>.webm (VP9), <ime>.mp4 (H.264, faststart), bez zvuka, + <ime>-seq/NNN.webp (--seq kadrova, rezerva).
Ulazni kadrovi su sirovi bajtovi iz ffmpeg-a; Pillow nikad ne otvara tudj fajl.
"""
import argparse
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageFilter

HEX = lambda s: tuple(int(s[i:i + 2], 16) for i in (2, 4, 6))  # '0x6E3A27' -> (110, 58, 39)


def decode(src, crop, width, ss, t, transpose):
    x, y, w, h = crop
    vf = [f'crop={w}:{h}:{x}:{y}']
    if transpose is not None:
        vf.append(f'transpose={transpose}')
        w, h = h, w
    out_w = width
    out_h = round(h * width / w / 2) * 2
    vf.append(f'scale={out_w}:{out_h}:flags=lanczos')
    cmd = ['unshare', '-rn', 'ffmpeg', '-v', 'error', '-protocol_whitelist', 'file', '-f', 'mov']
    if ss:
        cmd += ['-ss', str(ss)]
    if t:
        cmd += ['-t', str(t)]
    cmd += ['-i', src, '-an', '-vf', ','.join(vf), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = out_w * out_h * 3
    frames = []
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        frames.append(Image.frombytes('RGB', (out_w, out_h), b))
    if p.wait() != 0 or not frames:
        sys.exit('ffmpeg nije dekodirao izvor')
    return frames


def plate_of(frames, blur):
    plate = None
    for f in frames:
        g = f.filter(ImageFilter.GaussianBlur(blur))
        plate = g if plate is None else ImageChops.darker(plate, g)
    return plate


def edge_mask(size, top, bottom, side):
    """Maska 'L': 255 u sredini, linearno do 0 na ivicama (udeo visine/sirine)."""
    w, h = size
    col = Image.linear_gradient('L')  # 256x256, crno gore -> belo dole
    mask_v = Image.new('L', (1, h), 255)
    px = mask_v.load()
    for yy in range(h):
        a = 1.0
        if top and yy < h * top:
            a = min(a, yy / (h * top))
        if bottom and yy > h * (1 - bottom):
            a = min(a, (h - 1 - yy) / (h * bottom))
        px[0, yy] = int(255 * max(0.0, a) ** 1.3)
    mask_h = Image.new('L', (w, 1), 255)
    px = mask_h.load()
    for xx in range(w):
        a = 1.0
        if side and xx < w * side:
            a = min(a, xx / (w * side))
        if side and xx > w * (1 - side):
            a = min(a, (w - 1 - xx) / (w * side))
        px[xx, 0] = int(255 * max(0.0, a) ** 1.3)
    return ImageChops.multiply(mask_v.resize((w, h)), mask_h.resize((w, h)))


def steam_of(frame, plate, lut, mask, tint):
    d = ImageChops.subtract(frame.filter(ImageFilter.GaussianBlur(0.8)), plate)
    # bela para preko tamne boje daje razliku koja je u sva tri kanala; luma je dovoljna
    g = d.convert('L').point(lut)
    g = ImageChops.multiply(g, mask)
    chans = [g.point(lambda v, k=k: min(255, round(v * k))) for k in tint]
    return Image.merge('RGB', chans)


def make_lut(black, gain):
    lut = []
    for v in range(256):
        o = max(0.0, v - black) * gain
        o = 255 * (1 - 2.718281828 ** (-o / 255 * 2.2)) / (1 - 2.718281828 ** -2.2)  # meko skracivanje svetlina
        lut.append(max(0, min(255, round(o))))
    return lut


def encode(frames, out, fps, kind):
    w, h = frames[0].size
    color = ['-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv']
    vf = 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p'
    base = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(fps), '-i', '-',
            '-an', '-vf', vf]
    if kind == 'webm':
        enc = ['-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '37', '-deadline', 'good', '-cpu-used', '1', '-row-mt', '1',
               '-g', str(len(frames)), '-auto-alt-ref', '0']
    else:
        enc = ['-c:v', 'libx264', '-preset', 'veryslow', '-crf', '24', '-profile:v', 'high', '-movflags', '+faststart',
               '-g', str(len(frames)), '-tune', 'grain']
    p = subprocess.Popen(base + enc + color + [out], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit(f'kodiranje {out} nije uspelo')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'), ap.add_argument('out'), ap.add_argument('name')
    ap.add_argument('--crop', type=int, nargs=4, required=True, metavar=('X', 'Y', 'W', 'H'))
    ap.add_argument('--width', type=int, default=900)
    ap.add_argument('--ss', type=float, default=0)
    ap.add_argument('--t', type=float, default=0)
    ap.add_argument('--start', type=int, default=0, help='prvi kadar petlje (u dekodiranom delu)')
    ap.add_argument('--frames', type=int, default=120)
    ap.add_argument('--xfade', type=int, default=24)
    ap.add_argument('--fps', type=float, default=24)
    ap.add_argument('--black', type=float, default=3)
    ap.add_argument('--gain', type=float, default=2.2)
    ap.add_argument('--flat', action='store_true', help='ploca = jedna crna vrednost (izvor je prava crna, bez vinjete)')
    ap.add_argument('--blur', type=float, default=3, help='zamucenje kadra pre minimuma (ploca)')
    ap.add_argument('--fade', type=float, nargs=3, default=(0.12, 0.08, 0.10), metavar=('GORE', 'DOLE', 'STRANE'))
    ap.add_argument('--transpose', type=int, default=None, help='ffmpeg transpose (2 = 90 stepeni ulevo)')
    ap.add_argument('--tint', type=float, nargs=3, default=(1.0, 0.965, 0.91))
    ap.add_argument('--seq', type=int, default=30)
    ap.add_argument('--preview', default='0x6E3A27', help='boja sekcije za proveru screen mesanja')
    ap.add_argument('--preview-dir', default=None, help='ako je zadat, tu idu PNG provere (van repoa)')
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    frames = decode(a.src, a.crop, a.width, a.ss, a.t, a.transpose)
    print(f'dekodirano {len(frames)} kadrova {frames[0].size}')
    need = a.start + a.frames + a.xfade
    if need > len(frames):
        sys.exit(f'treba {need} kadrova, ima {len(frames)}')
    plate = plate_of(frames, a.blur)
    if a.flat:
        plate = Image.new('RGB', plate.size, tuple(lo for lo, hi in plate.getextrema()))
    lut = make_lut(a.black, a.gain)
    mask = edge_mask(frames[0].size, *a.fade)
    st = [steam_of(f, plate, lut, mask, a.tint) for f in frames[a.start:need]]
    L, X = a.frames, a.xfade
    loop = []
    for i in range(L):
        if i < X:
            w = i / X  # 0 = rep (nastavak), 1 = pocetak
            w = w * w * (3 - 2 * w)
            loop.append(Image.blend(st[L + i], st[i], w))
        else:
            loop.append(st[i])
    base = os.path.join(a.out, a.name)
    encode(loop, base + '.webm', a.fps, 'webm')
    encode(loop, base + '.mp4', a.fps, 'mp4')
    sd = base + '-seq'
    os.makedirs(sd, exist_ok=True)
    step = L / a.seq
    for k in range(a.seq):
        loop[int(k * step)].save(os.path.join(sd, f'{k:03d}.webp'), 'WEBP', quality=72, method=6)
    # provera: sredina petlje preko boje sekcije (screen)
    if a.preview_dir:
        os.makedirs(a.preview_dir, exist_ok=True)
        bgc = Image.new('RGB', loop[0].size, HEX(a.preview))
        for idx in (0, L // 4, L // 2, 3 * L // 4):
            ImageChops.screen(bgc, loop[idx]).save(os.path.join(a.preview_dir, f'{a.name}-{idx:03d}.png'))
    print('gotovo', base)


if __name__ == '__main__':
    main()
