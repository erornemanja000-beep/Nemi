#!/usr/bin/env python3
"""Pravi uspravnu (9:16) verziju širokog videa pomoću "virtuelne kamere".

Plan (JSON):
{
  "fps": 30, "size": [1080, 1920],
  "inputs": [{"path": "...", "from_frame": 0, "frames": 300}, ...],   # redom, spajaju se
  "keyframes": [{"t": 0, "cx": 960, "wc": 607.5, "by": 0.5, "cut": false}, ...],
  "post_vf": "...",            # ffmpeg filteri posle isecanja (izoštravanje itd.)
  "audio": "putanja ili null", "crf": 21,
  "logo": {"x": 567, "y": 81, "w": 825.6}   # opciono: gde je logo u izvornom kadru (px, 1920x1080)
}
Koordinate kamere su u pikselima izvora 1920x1080: cx = sredina kadra, wc = širina izvora koja staje
u širinu izlaza (607.5 = puna visina, bez popune; veće = udaljavanje, gore/dole zamućena pozadina).
"""
import json, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter

MIN_WC = 1080 * 1080 / 1920  # 607.5: širina izvora za pun 9:16 isečak


def camera(kfs, t):
    """Kamera u trenutku t: glatko (smoothstep) između tačaka, skok na tački sa cut=true."""
    if t <= kfs[0]['t']:
        k = kfs[0]
        return k['cx'], k['wc'], k.get('by', .5)
    for a, b in zip(kfs, kfs[1:]):
        if t < b['t']:
            if b.get('cut'):
                return a['cx'], a['wc'], a.get('by', .5)
            u = (t - a['t']) / max(1e-6, b['t'] - a['t'])
            s = u * u * (3 - 2 * u)
            lerp = lambda p, q: p + (q - p) * s
            return lerp(a['cx'], b['cx']), lerp(a['wc'], b['wc']), lerp(a.get('by', .5), b.get('by', .5))
    k = kfs[-1]
    return k['cx'], k['wc'], k.get('by', .5)


def clamp_cam(cx, wc):
    wc = min(1920.0, max(MIN_WC, wc))
    return min(1920 - wc / 2, max(wc / 2, cx)), wc


def frames(inp):
    """Čita kadrove jednog ulaza u punoj rezoluciji (RGB)."""
    w, h = map(int, subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                             'stream=width,height', '-of', 'csv=p=0', inp['path']]).decode().strip().split(','))
    first, n = inp.get('from_frame', 0), inp.get('frames')
    vf = f'select=gte(n\\,{first})' + (f'*lt(n\\,{first + n})' if n else '')
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', inp['path'], '-vf', vf, '-vsync', '0', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=w * h * 3 * 2)
    size = w * h * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield Image.frombuffer('RGB', (w, h), buf, 'raw', 'RGB', 0, 1)
    p.wait()


def render_frame(img, cx, wc, by, OW, OH):
    k = img.width / 1920.0
    cx, wc = clamp_cam(cx, wc)
    x0, x1 = (cx - wc / 2) * k, (cx + wc / 2) * k
    s = OW / wc                                   # izlazni px po px izvora (1920-skala)
    bh = 1080 * s                                 # visina oštre trake u izlazu
    if bh >= OH - 0.5:                            # pun isečak, bez popune
        y_over = (bh - OH) / s / 2 * k            # (samo zbog zaokruživanja)
        return img.resize((OW, OH), Image.LANCZOS, box=(x0, y_over, x1, img.height - y_over))
    band_h = int(round(bh))
    band = img.resize((OW, band_h), Image.LANCZOS, box=(x0, 0, x1, img.height))
    top = int(round((OH - band_h) * by))
    # Popuna iznad i ispod: najkrajnji tanki pojas ivice kadra razvučen preko praznine, pa jako zamućen
    # (pastelna pozadina se čisto nastavlja, bez ponavljanja predmeta iz kadra)
    canvas = Image.new('RGB', (OW, OH))
    canvas.paste(band, (0, top))
    strip = max(2, int(band_h * 0.025))
    if top > 0:
        canvas.paste(band.crop((0, 0, OW, strip)).resize((OW, top), Image.BILINEAR), (0, 0))
    gap = OH - top - band_h
    if gap > 0:
        canvas.paste(band.crop((0, band_h - strip, OW, band_h)).resize((OW, gap), Image.BILINEAR), (0, top + band_h))
    q = 12
    bg = canvas.resize((OW // q, OH // q), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2.2)).resize((OW, OH), Image.BICUBIC)
    # mekani prelaz na gornjoj i donjoj ivici trake (uži kad je praznina mala, da nema skoka)
    F = int(OH * 0.05)
    a = np.ones(band_h, np.float32)
    ft, fb = min(F, int(top * 1.5)), min(F, int((OH - top - band_h) * 1.5))
    if ft > 1:
        a[:ft] = np.linspace(0, 1, ft, dtype=np.float32)
    if fb > 1:
        a[-fb:] = np.minimum(a[-fb:], np.linspace(1, 0, fb, dtype=np.float32))
    mask = Image.fromarray((np.repeat(a[:, None], OW, 1) * 255).astype(np.uint8), 'L')
    bg.paste(band, (0, top), mask)
    return bg


def main():
    plan = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    OW, OH = plan.get('size', [1080, 1920])
    fps = plan.get('fps', 30)
    kfs = sorted(plan['keyframes'], key=lambda k: k['t'])
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(fps), '-i', '-']
    if plan.get('audio'):
        cmd += ['-i', plan['audio'], '-map', '0:v', '-map', '1:a?', '-c:a', 'aac', '-b:a', '128k', '-shortest']
    if plan.get('post_vf'):
        cmd += ['-vf', plan['post_vf']]
    cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', str(plan.get('crf', 21)), '-profile:v', 'high',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = 0
    for inp in plan['inputs']:
        for img in frames(inp):
            cx, wc, by = camera(kfs, n / fps)
            enc.stdin.write(render_frame(img, cx, wc, by, OW, OH).tobytes())
            n += 1
            if n % 150 == 0:
                print(f'{n} frames', file=sys.stderr, flush=True)
    enc.stdin.close(); enc.wait()
    info = {'frames': n}
    if plan.get('logo'):
        # Gde logo završi u poslednjem kadru (udeo širine/visine izlaza) - za let loga na sajtu
        cx, wc, by = camera(kfs, (n - 1) / fps); cx, wc = clamp_cam(cx, wc)
        s = OW / wc; top = (OH - 1080 * s) * by if 1080 * s < OH else (OH - 1080 * s) / 2
        L = plan['logo']
        info['logo'] = {'x': round(((L['x'] - (cx - wc / 2)) * s) / OW, 4), 'y': round((top + L['y'] * s) / OH, 4),
                        'w': round(L['w'] * s / OW, 4)}
    print(json.dumps(info))


if __name__ == '__main__':
    main()
