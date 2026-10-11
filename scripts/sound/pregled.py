#!/usr/bin/env python3
"""Slika zvuka za proveru bez slušanja: spektrogram + talasni oblik, sa trakom kadrova iz filma iznad.

  python3 pregled.py audio.wav out.png [--video film.mp4] [--from 0 --to 37.4] [--cues cues.json]
"""
import argparse, json, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw


def load(p):
    with wave.open(p) as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        x = np.frombuffer(w.readframes(n), '<i2').astype(np.float32).reshape(-1, ch) / 32768
    return x.mean(1), sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wav'); ap.add_argument('out')
    ap.add_argument('--video'); ap.add_argument('--cues')
    ap.add_argument('--from', dest='a', type=float, default=0); ap.add_argument('--to', dest='b', type=float, default=None)
    ap.add_argument('--width', type=int, default=2400)
    o = ap.parse_args()
    x, sr = load(o.wav)
    b = o.b or len(x) / sr
    x = x[int(o.a * sr):int(b * sr)]
    W, H = o.width, 360
    hop = max(1, len(x) // W)
    nfft = 2048
    cols = []
    for i in range(W):
        seg = x[i * hop:i * hop + nfft]
        if len(seg) < nfft:
            seg = np.pad(seg, (0, nfft - len(seg)))
        s = np.abs(np.fft.rfft(seg * np.hanning(nfft)))
        cols.append(s)
    S = np.array(cols).T                      # (freq, time)
    f = np.fft.rfftfreq(nfft, 1 / sr)
    # logaritamska osa frekvencija 40 Hz - 16 kHz
    ys = np.geomspace(40, 16000, H)[::-1]
    idx = np.searchsorted(f, ys).clip(0, len(f) - 1)
    db = 20 * np.log10(S[idx] + 1e-9)
    db -= np.percentile(db, 99.5)            # relativno: najjači delovi = 0 dB
    img = np.clip((db + 60) / 60, 0, 1)
    rgb = (np.stack([img ** 0.6, img ** 1.4, img ** 3.0], -1) * 255).astype(np.uint8)
    spec = Image.fromarray(rgb)
    # talasni oblik
    wav = Image.new('RGB', (W, 120), (20, 20, 24)); d = ImageDraw.Draw(wav)
    for i in range(W):
        seg = x[i * hop:(i + 1) * hop]
        if len(seg):
            m = float(np.max(np.abs(seg)))
            d.line((i, 60 - m * 58, i, 60 + m * 58), fill=(120, 200, 140))
    parts = [spec, wav]
    if o.video:
        tmp = tempfile.mkdtemp()
        n_th = 16
        th_w = W // n_th
        strip = Image.new('RGB', (W, int(th_w * 9 / 16)), 'black')
        for k in range(n_th):
            t = o.a + (b - o.a) * (k + 0.5) / n_th
            p = f'{tmp}/f{k}.jpg'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', o.video, '-frames:v', '1', '-vf', f'scale={th_w}:-2', p])
            try:
                strip.paste(Image.open(p), (k * th_w, 0))
            except Exception:
                pass
        parts.insert(0, strip)
    out = Image.new('RGB', (W, sum(p.height for p in parts) + 24), (255, 255, 255))
    y = 0
    for p in parts:
        out.paste(p, (0, y)); y += p.height
    d = ImageDraw.Draw(out)
    step = 1.0 if b - o.a <= 12 else 2.0
    t = np.ceil(o.a / step) * step
    while t <= b:
        xx = int((t - o.a) / (b - o.a) * W)
        d.line((xx, 0, xx, y), fill=(255, 255, 255) if True else 0)
        d.text((xx + 2, y + 4), f'{t:.0f}s', fill=(0, 0, 0))
        t += step
    if o.cues:
        for e in json.load(open(o.cues))['events']:
            if o.a <= e['t'] <= b:
                xx = int((e['t'] - o.a) / (b - o.a) * W)
                d.line((xx, y - 120, xx, y - 100), fill=(255, 80, 120), width=2)
    out.save(o.out)


if __name__ == '__main__':
    main()
