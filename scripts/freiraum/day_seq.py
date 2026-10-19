#!/usr/bin/env python3
"""AI prelazi (Kling) -> niz WebP kadrova sa providnom pozadinom, za skrol na premium sajtu.

    python3 -I day_seq.py <izlaz/seq/ime> <bg> clip1.mp4[:od:do] clip2.mp4[:od:do] ...

<bg> je boja podloge na kojoj je klip generisan ('cream' ili 'black'). Alfa = rembg maska (isnet)
∪ razlika od boje podloge, pa para, pena i prskanje ostaju i kad ih maska izgubi. Klipovi se
nadovezuju (kraj jednog = početak sledećeg). seq.json beleži gde počinje koji klip (steps).
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

import cv2
import numpy as np
from PIL import Image, ImageFilter

os.environ.setdefault('U2NET_HOME', os.path.expanduser('~/.rembg'))
from rembg import new_session, remove  # noqa: E402

FPS = 12
SIZES = {'d': (720, 70), 'm': (540, 66)}
BG = {'cream': (243, 235, 223), 'black': (0, 0, 0)}


def frames(spec, tmp):
    path, *rng = spec.split(':')
    out = tempfile.mkdtemp(dir=tmp)
    trim = (['-ss', rng[0]] if rng and rng[0] else []) + (['-to', rng[1]] if len(rng) > 1 and rng[1] else [])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *trim, '-i', path, '-vf', f'fps={FPS},scale=900:900',
                    f'{out}/%04d.png'], check=True)
    return sorted(glob.glob(f'{out}/*.png'))


def background(rgb, m):
    """Glatter Hintergrund pro Pixel (Kling-Hintergründe haben Verläufe): Objekt ausblenden, grob mitteln, Löcher füllen."""
    h, w = m.shape
    cover = cv2.dilate((m > 0.05).astype(np.uint8), np.ones((31, 31), np.uint8))
    wgt = (1 - cover).astype(np.float32)
    n = 24
    num = cv2.resize(rgb * wgt[..., None], (n, n), interpolation=cv2.INTER_AREA)
    den = cv2.resize(wgt, (n, n), interpolation=cv2.INTER_AREA)
    small = num / np.maximum(den, 1e-4)[..., None]
    hole = (den < 0.08).astype(np.uint8)
    small = cv2.inpaint(np.clip(small, 0, 255).astype(np.uint8), hole, 3, cv2.INPAINT_TELEA).astype(np.float32)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)


def fill_holes(a, min_frac=0.004):
    """Große geschlossene Löcher (Tellerinneres) deckend machen; kleine (Henkel) bleiben offen."""
    solid = cv2.morphologyEx((a > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(1 - solid, connectivity=4)
    h, w = a.shape
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    hole = np.zeros_like(a)
    for i in range(1, n):
        if i not in edge and stats[i, cv2.CC_STAT_AREA] >= min_frac * h * w:
            hole[lab == i] = 1
    hole = cv2.GaussianBlur(cv2.dilate(hole, np.ones((5, 5), np.uint8)), (0, 0), 1.5)
    return np.maximum(a, hole)


def matte(im, sess, bg):
    rgb = np.asarray(im.convert('RGB')).astype(np.float32)
    m = np.asarray(remove(im, session=sess, only_mask=True, post_process_mask=False)).astype(np.float32) / 255
    solid = cv2.erode((m > 0.5).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
    if bg == BG['black']:
        # Nacht: Licht auf Schwarz. Feste Objekte (Inneres der Maske) bleiben deckend, Ränder, Glas,
        # Flammen und Funken kommen über die Helligkeit – so entstehen keine dunklen Säume.
        lum = np.clip((rgb.max(-1) - 10) / 70, 0, 1)
        soft = cv2.GaussianBlur(solid, (0, 0), 2.0)
        a = np.maximum(soft * m, lum)
        af = np.maximum(a, 1e-3)[..., None]
        fg = np.where(af > 0.02, rgb / af, rgb)   # vor Schwarz „vormultipliziert“ → zurückrechnen
    else:
        # Tag: Objekt aus der Maske; dazu nur, was heller als der Hintergrund ist (Milch, Dampf)
        # oder dunkel UND farbig (Espresso-Strahl). Graue Schlagschatten bleiben draußen.
        # weißes Porzellan (Teller, Tasse) ist neutral, der Hintergrund und seine warmen Schatten
        # sind cremig-farbig (Sättigung > 20); daran erkennt man den Teller, den die Maske verliert
        sat = rgb.max(-1) - rgb.min(-1)
        neutral = np.clip((16 - sat) / 6, 0, 1) * np.clip((rgb.mean(-1) - 140) / 30, 0, 1)
        m = np.maximum(m, neutral)
        bgimg = background(rgb, m)
        diff = (rgb - bgimg).mean(-1)
        sat_bg = bgimg.max(-1) - bgimg.min(-1)
        # heller UND weißer (Milch, Dampf); nur heller in Hintergrundfarbe ist Lichtkante des Schattens
        lighter = np.clip((diff - 8) / 30, 0, 1) * np.clip((sat_bg - sat - 2) / 8, 0, 1)
        dark_col = np.clip((-diff - 20) / 40, 0, 1) * np.clip((sat - sat_bg - 15) / 40, 0, 1)
        # weißes Porzellan (Teller, Tasse): fast weiß und deutlich weniger farbig als der cremige Hintergrund
        white = np.clip((rgb.min(-1) - 222) / 14, 0, 1) * np.clip((sat_bg - sat - 6) / 10, 0, 1)
        a = np.maximum(m, np.maximum(np.maximum(lighter, dark_col), white))
        a = cv2.morphologyEx(a.astype(np.float32), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        a = fill_holes(a)
        fg = rgb
    a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
    out = np.dstack([np.clip(fg, 0, 255), a]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def main():
    dst, bgname, *clips = sys.argv[1:]
    bg = BG[bgname]
    sess = new_session('isnet-general-use')
    tmp = tempfile.mkdtemp()
    try:
        allp, steps = [], []
        for i, spec in enumerate(clips):
            fr = frames(spec, tmp)
            if allp:
                fr = fr[1:]   # erster Kadar = letzter Kadar des vorigen Clips
            steps.append({'from': len(allp), 'to': len(allp) + len(fr) - 1})
            allp += fr
        os.makedirs(dst, exist_ok=True)
        rgba = os.path.join(tmp, 'rgba')
        os.makedirs(rgba)
        for i, p in enumerate(allp):
            matte(Image.open(p), sess, bg).save(f'{rgba}/{i + 1:04d}.png')
        for key, (w, q) in SIZES.items():
            d = os.path.join(dst, key)
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            for f in sorted(glob.glob(f'{rgba}/*.png')):
                Image.open(f).resize((w, w), Image.LANCZOS).save(os.path.join(d, os.path.basename(f)[:-4] + '.webp'),
                                                               quality=q, method=5, alpha_quality=90)
        Image.open(f'{rgba}/0001.png').resize((720, 720)).save(os.path.join(dst, 'poster.webp'), quality=80)
        json.dump({'count': len(allp), 'fps': FPS, 'w': 720, 'h': 720, 'steps': steps},
                  open(os.path.join(dst, 'seq.json'), 'w'))
        size = {k: sum(os.path.getsize(f) for f in glob.glob(os.path.join(dst, k, '*.webp'))) / 1e6 for k in SIZES}
        print(dst, len(allp), 'kadrova', steps, {k: f'{v:.1f} MB' for k, v in size.items()})
    finally:
        shutil.rmtree(tmp)


if __name__ == '__main__':
    main()
