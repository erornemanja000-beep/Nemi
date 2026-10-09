#!/usr/bin/env python3
"""Zvucni efekti za "Gradnju DON'S-a", tacno uskladjeni sa slikom.

Svaki udarac, cigla, svetlo i iskrica dobija svoj kratak zvuk, a zvuk
prati polozaj elementa levo-desno (stereo). Vremena se citaju iz iste
scene koju koristi render.py, pa su uvek sinhronizovana.

Upotreba:
  python3 sfx.py assets/lokal video/gradnja_sfx.wav
"""
import math
import os
import random
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R  # noqa: E402
import scenario as S  # noqa: E402

SR = 48000


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def lowpass(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def noise(dur, rng):
    return rng.uniform(-1, 1, int(dur * SR))


def thump(f0, f1, dur, amp):
    t = tt(dur)
    f = f1 + (f0 - f1) * np.exp(-t / 0.035)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.075)


def tok(freq, dur, amp):
    t = tt(dur)
    s = np.sin(2 * np.pi * freq * t) + 0.45 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t / 0.012)
    return amp * s * np.exp(-t / 0.028)


def click(amp, rng):
    n = noise(0.006, rng)
    return amp * (n - lowpass(n, 0.2)) * np.linspace(1, 0, len(n))


def crumble(dur, amp, rng):
    n = noise(dur, rng)
    n = lowpass(n, 0.18)
    t = tt(dur)
    grains = (rng.uniform(0, 1, len(t)) > 0.985) * rng.uniform(0.4, 1, len(t))
    g = lowpass(grains, 0.35)
    return amp * (0.6 * n + 1.6 * g) * np.exp(-t / (dur * 0.45))


def bloop(f0, f1, dur, amp):
    t = tt(dur)
    f = f0 + (f1 - f0) * (t / dur) ** 0.6
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur) ** 0.8


def tink(freq, dur, amp):
    t = tt(dur)
    s = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2.01 * t) + 0.15 * np.sin(2 * np.pi * freq * 3.03 * t)
    return amp * s * np.exp(-t / (dur * 0.3)) * np.minimum(1, t / 0.002)


def shimmer(dur, amp, rng):
    t = tt(dur)
    s = np.zeros_like(t)
    for _ in range(7):
        f = rng.uniform(3200, 6400)
        s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(5, 11) * t))
    return amp * s / 7 * np.sin(np.pi * t / dur) ** 1.5


def whoosh(dur, amp, rng):
    n = noise(dur, rng)
    t = tt(dur)
    a = 0.02 + 0.25 * (t / dur) ** 2
    y = np.empty_like(n)
    acc = 0.0
    for i, v in enumerate(n):
        acc += a[i] * (v - acc)
        y[i] = acc
    return amp * y * (t / dur) ** 1.5


def buzz(dur, amp):
    t = tt(dur)
    s = np.sign(np.sin(2 * np.pi * 100 * t)) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.5
    return amp * s * np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.004)


class Mix:
    def __init__(self, dur):
        self.L = np.zeros(int(dur * SR) + SR)
        self.Rc = np.zeros_like(self.L)

    def add(self, t, sig, pan=0.0, gain=1.0):
        i = int(t * SR)
        if i < 0:
            sig = sig[-i:]
            i = 0
        n = min(len(sig), len(self.L) - i)
        if n <= 0:
            return
        gl = math.cos((pan + 1) * math.pi / 4) * math.sqrt(2)
        gr = math.sin((pan + 1) * math.pi / 4) * math.sqrt(2)
        self.L[i:i + n] += sig[:n] * gain * gl
        self.Rc[i:i + n] += sig[:n] * gain * gr


def pan_of(c):
    x = (c[0] + c[2]) / 2
    xo = R.X0_R + (x - R.MARGIN)
    return max(-0.7, min(0.7, (xo - R.OW / 2) / (R.OW / 2) * 0.9))


def main():
    base, out = sys.argv[1], sys.argv[2]
    rng = np.random.default_rng(11)
    random.seed(11)
    sc = R.Scene(base)
    mix = Mix(S.TOTAL)

    for key in 'ABCD':
        tr = sc.tr[key]
        st = tr['start']
        # cigle: pucanje, krckanje, tutnjava
        if 'brick_list' in tr:
            bs = tr['bricks']
            mix.add(st + bs['seams'][0], crumble(0.35, 0.10, rng), 0, 1)
            for b in tr['brick_list']:
                mix.add(st + b.tdet, crumble(rng.uniform(0.08, 0.16), rng.uniform(0.05, 0.09), rng),
                        pan_of(b.c), 1)
                mix.add(st + b.tdet + 0.45, tok(rng.uniform(260, 420), 0.08, 0.04), pan_of(b.c), 1)
            mix.add(st + bs['t0'], thump(70, 38, 0.9, 0.35) * 0.8, 0, 1)
            mix.add(st + bs['t0'], lowpass(noise(bs['spread'] + 0.5, rng), 0.03) * 0.5
                    * np.sin(np.pi * tt(bs['spread'] + 0.5) / (bs['spread'] + 0.5)), 0, 1)
        if key == 'A':
            mix.add(st, thump(55, 35, 0.6, 0.28), 0, 1)
            mix.add(st, shimmer(0.6, 0.09, rng), 0, 1)
        for e in tr.get('removed', []):
            mix.add(st + e.t, shimmer(0.45, 0.10, rng)[::-1].copy(), pan_of(e.c), 1)
        for e in tr['elems']:
            p = pan_of(e.c)
            t0 = st + e.t
            ti = R.impact_tau(e)
            if e.anim in ('drop', 'rise', 'slide_l') and ti is not None:
                ts = t0 + ti * e.d
                if e.heavy:
                    mix.add(ts, thump(72, 38, 0.35, 0.80), p)
                    mix.add(ts, tok(430, 0.14, 0.30), p)
                    mix.add(ts + 0.01, tink(3100, 0.25, 0.06), p)
                elif e.kind == 'letter':
                    mix.add(ts - 0.14, whoosh(0.14, 0.10, rng), p)
                    mix.add(ts, thump(82, 44, 0.28, 0.60), p)
                    mix.add(ts, tok(rng.uniform(1050, 1250), 0.12, 0.22), p)
                elif e.kind == 'facade':
                    mix.add(ts, thump(90, 50, 0.24, 0.45), p)
                    mix.add(ts, tok(rng.uniform(620, 880), 0.10, 0.20), p)
                else:
                    mix.add(ts, thump(105, 58, 0.2, 0.32), p)
                    mix.add(ts, tok(rng.uniform(820, 1050), 0.09, 0.16), p)
                mix.add(ts, click(0.18, rng), p)
            elif e.anim == 'swing':
                mix.add(t0, whoosh(e.d * 0.6, 0.10, rng), p)
                mix.add(t0 + e.d * 0.55, tok(980, 0.06, 0.12), p)
            elif e.anim == 'pop':
                mix.add(t0, bloop(380, 980, 0.13, 0.22), p)
                mix.add(t0 + 0.08, tink(rng.choice([2093, 2637, 3136]), 0.4, 0.07), p)
            elif e.anim == 'light':
                mix.add(t0, tink(rng.uniform(2400, 3000), 0.35, 0.09), p)
                mix.add(t0, click(0.10, rng), p)
            elif e.anim == 'flicker':
                for (a, b) in ((0.0, 0.08), (0.20, 0.28), (0.40, 1.2)):
                    mix.add(t0 + a * e.d, buzz((b - a) * e.d, 0.025), p)
            elif e.anim == 'wipe_up':
                mix.add(t0, shimmer(e.d + 0.25, 0.10, rng), p)
        for (rect, t0, d) in tr.get('glints', []):
            mix.add(st + t0, shimmer(d, 0.06, rng), pan_of(R.crect(rect)))

    # zavrsni "ta-da": arpeggio iznad natpisa
    fs = S.FINAL_START + S.FINAL['sweep'][0]
    for i, f in enumerate((1047, 1319, 1568, 2093)):
        mix.add(fs + i * 0.09, tink(f, 0.9, 0.10), -0.3 + 0.2 * i)
    mix.add(fs, shimmer(1.0, 0.07, rng), 0)

    st = np.stack([mix.L, mix.Rc], 1)[:int(S.TOTAL * SR)]
    peak = np.abs(st).max() or 1
    st = np.tanh(st / peak * 1.3) / math.tanh(1.3) * 0.85
    pcm = (st * 32767).astype('<i2')
    with wave.open(out, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('gotovo', out)


if __name__ == '__main__':
    main()
