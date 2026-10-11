#!/usr/bin/env python3
"""Zvučna podloga za intro film DON'S: instrumenti i zvučni efekti, sve sintetizovano (numpy/scipy).

Svaka funkcija vraća stereo niz oblika (N, 2), float32, 48 kHz. Glasnoća 1.0 = pun signal.
"""
import numpy as np
from scipy import signal

SR = 48000
RNG = np.random.default_rng(7)


# ---------------------------------------------------------------- osnovno
def t_axis(dur):
    return np.arange(int(round(dur * SR))) / SR


def mtof(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def stereo(x, pan=0.0, width=0.0):
    """Mono -> stereo sa konstantnom snagom; width malo razmakne kanale (kratko kašnjenje)."""
    p = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    l, r = np.cos(p) * x, np.sin(p) * x
    if width > 0:
        d = int(width * 0.012 * SR)
        r = np.concatenate([np.zeros(d), r[:len(r) - d]]) if d else r
    return np.stack([l, r], 1).astype(np.float32)


def env_ad(n, a, d, curve=4.0):
    """Napad a sekundi, pa eksponencijalni pad sa vremenskom konstantom d."""
    t = np.arange(n) / SR
    e = np.where(t < a, (t / max(a, 1e-4)), np.exp(-(t - a) / max(d, 1e-4)))
    return e


def env_asr(n, a, r):
    """Napad, zadržavanje, otpuštanje (linearno/kosinusno)."""
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, na))
    if nr:
        e[-nr:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, nr))
    return e


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [max(20, lo), min(hi, SR / 2 - 100)], 'bandpass', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, min(f, SR / 2 - 100), 'lowpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, max(20, f), 'highpass', fs=SR, output='sos'), x)


def noise(dur):
    return RNG.uniform(-1, 1, int(dur * SR))


def sweep_filter(x, f0, f1, q=2.0, steps=24):
    """Pojasni filter čija se sredina pomera od f0 do f1 (preklapanje blokova)."""
    n = len(x)
    out = np.zeros(n)
    edges = np.linspace(0, n, steps + 1).astype(int)
    win_len = max(64, n // steps)
    for i in range(steps):
        c = f0 * (f1 / f0) ** (i / max(1, steps - 1))
        bw = c / q
        seg = bp(x, c - bw / 2, c + bw / 2)
        w = np.zeros(n)
        a, b = edges[i], edges[i + 1]
        lo, hi = max(0, a - win_len // 2), min(n, b + win_len // 2)
        w[lo:hi] = np.hanning(hi - lo)
        out += seg * w
    return out


def normalize(x, peak=1.0):
    m = np.max(np.abs(x)) or 1.0
    return x * (peak / m)


def place(dst, src, t):
    """Doda zvuk src u dst od trenutka t (sekunde)."""
    i = int(round(t * SR))
    if i >= len(dst):
        return
    if i < 0:
        src, i = src[-i:], 0
    n = min(len(src), len(dst) - i)
    dst[i:i + n] += src[:n]


# ---------------------------------------------------------------- prostor
def make_ir(dur=2.2, decay=0.55, predelay=0.018, bright=6500, seed=3):
    """Veštački odjek (impulsni odziv): dva nekorelisana kanala, eksponencijalni pad, mekši visoki tonovi."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n + int(predelay * SR), 2))
    for c in range(2):
        x = rng.standard_normal(n) * np.exp(-t / decay * 3.0)
        x = lp(x, bright * (1 - 0.15 * c))
        ir[int(predelay * SR):, c] = x
    ir /= np.sqrt(np.sum(ir ** 2, 0, keepdims=True)) + 1e-9
    return ir.astype(np.float32)


def reverb(x, ir, wet=0.25):
    y = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)
    return (x * (1 - wet) + y * wet * 2.2).astype(np.float32)


# ---------------------------------------------------------------- instrumenti
def music_box(note, vel=0.7, dur=1.6, pan=0.0):
    """Muzička kutija / čelesta: zvonasti parcijali, brz napad, dug pad."""
    f = mtof(note)
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    parts = [(1, 1.0, 1.4), (2.0, 0.45, 0.7), (3.0, 0.18, 0.45), (4.16, 0.22, 0.22), (5.43, 0.08, 0.12)]
    x = sum(a * np.sin(2 * np.pi * f * r * t + 0.3 * r) * np.exp(-t / d) for r, a, d in parts)
    x += 0.15 * np.sin(2 * np.pi * f * 8.0 * t) * np.exp(-t / 0.015)          # tihi "tink" napada
    x *= np.minimum(1, t / 0.002) * vel
    return stereo(lp(x, 9000) * 0.32, pan, 0.3)


def harp(note, vel=0.6, pan=0.0):
    """Trzaj harfe/pizzicato: harmonici koji se gase brže što su viši."""
    f = mtof(note)
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    x = sum((1 / k ** 1.3) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.6 + 1.1 * k)) for k in range(1, 9))
    x *= np.minimum(1, t / 0.003) * vel
    return stereo(lp(x, 6500) * 0.28, pan, 0.4)


def pad(notes, dur, vel=0.5, bright=1800, pan=0.0):
    """Topao, mek akord: po tri blago raštimovana talasa po noti, filtar, spor napad."""
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    L = np.zeros(n)
    R = np.zeros(n)
    for note in notes:
        f = mtof(note)
        for k, det in enumerate((-0.07, 0.0, 0.08)):
            ph = RNG.uniform(0, 2 * np.pi)
            ff = f * 2 ** (det / 12)
            # meki "saw": prvih 6 harmonika
            w = sum(np.sin(2 * np.pi * ff * h * t + ph * h) / h for h in range(1, 7))
            if k == 0:
                L += w
            elif k == 2:
                R += w
            else:
                L += 0.6 * w
                R += 0.6 * w
    lfo = 1 + 0.25 * np.sin(2 * np.pi * 0.35 * t)
    L = lp(L, bright) * lfo
    R = lp(R, bright * 1.08) * lfo
    e = env_asr(n, 0.7, 1.4)
    out = np.stack([L * e, R * e], 1) * (vel * 0.06 / max(1, len(notes) ** 0.5))
    return out.astype(np.float32)


def bass(note, dur, vel=0.6):
    f = mtof(note)
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.08 * np.sin(6 * np.pi * f * t)
    x *= env_asr(n, 0.03, 0.35) * np.exp(-t / (dur * 1.5 + 0.3)) * vel * 0.35
    return stereo(lp(x, 900), 0)


def shaker(vel=0.3, pan=0.2):
    x = hp(noise(0.09), 5000) * env_ad(int(0.09 * SR), 0.004, 0.025) * vel * 0.35
    return stereo(x, pan)


def bell(note, vel=0.8, dur=4.5, pan=0.0):
    """Cevasto zvono za završni akord (neharmonični parcijali, dug zvuk)."""
    f = mtof(note)
    n = int(dur * SR)
    t = np.arange(n) / SR
    parts = [(0.5, 0.35, 2.5), (1, 1.0, 2.2), (1.19, 0.5, 1.6), (1.56, 0.35, 1.2), (2.0, 0.4, 1.0), (2.51, 0.22, 0.7), (3.01, 0.18, 0.5), (4.1, 0.1, 0.25)]
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, a, d in parts)
    x *= np.minimum(1, t / 0.002) * vel
    return stereo(lp(x, 10000) * 0.22, pan, 0.5)


# ---------------------------------------------------------------- zvučni efekti
PENTA = [0, 2, 4, 7, 9]  # pentatonska lestvica za svetlucanja (uvek "lepo" zvuči uz muziku)


def _ping(f, dur, decay, amp):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / (decay * 0.3))
    return x * np.exp(-t / decay) * np.minimum(1, t / 0.001) * amp


def sparkle(dur, intensity=0.5, pitch='high', pan=0.0, key_root=72, density=14):
    n = int((dur + 0.8) * SR)
    L, R = np.zeros(n), np.zeros(n)
    base = {'low': key_root, 'mid': key_root + 12, 'high': key_root + 24}[pitch]
    count = max(2, int(density * dur * (0.5 + intensity)))
    for i in range(count):
        tt = RNG.uniform(0, dur) * (0.6 + 0.4 * i / count)
        note = base + PENTA[RNG.integers(5)] + 12 * RNG.integers(0, 2)
        g = _ping(mtof(note), 0.6, RNG.uniform(0.08, 0.25), RNG.uniform(0.25, 1.0))
        p = np.clip(pan + RNG.uniform(-0.5, 0.5), -1, 1)
        s = stereo(g, p)
        a = int(tt * SR)
        m = min(len(s), n - a)
        L[a:a + m] += s[:m, 0]
        R[a:a + m] += s[:m, 1]
    out = np.stack([L, R], 1) * intensity * 0.09
    return out.astype(np.float32)


def shimmer(dur, intensity=0.5, pitch='high', pan=0.0, key_root=72):
    n = int((dur + 0.8) * SR)
    air = hp(noise(dur + 0.8), 6000) * env_asr(n, dur * 0.4, dur * 0.6 + 0.6) * 0.05
    out = sparkle(dur, intensity, pitch, pan, key_root, density=28)
    m = min(len(out), n)
    out[:m] += stereo(air[:m] * intensity, pan, 0.6)
    return out


def magic_wand(dur, intensity=0.6, pan=0.0, key_root=72):
    """Uzlazni niz zvončića + svetlucavi rep."""
    n = int((dur + 1.0) * SR)
    out = np.zeros((n, 2), np.float32)
    steps = 7
    for i in range(steps):
        note = key_root + 12 + PENTA[i % 5] + 12 * (i // 5)
        g = _ping(mtof(note), 0.7, 0.18, 0.8 - i * 0.05)
        place(out, stereo(g, pan + (i - 3) * 0.06), i * dur * 0.45 / steps)
    tail = shimmer(dur * 0.8, intensity * 0.8, 'high', pan, key_root)
    place(out, tail, dur * 0.3)
    return out * intensity * 0.45


def twinkle(dur, intensity=0.4, pitch='high', pan=0.0, key_root=72):
    return sparkle(dur, intensity, pitch, pan, key_root, density=6)


def chime(dur, intensity=0.5, pitch='high', pan=0.0, key_root=72):
    out = np.zeros((int((dur + 1.5) * SR), 2), np.float32)
    base = key_root + (24 if pitch == 'high' else 12)
    for i, step in enumerate([0, 4, 7, 12][:max(2, int(2 + dur * 3))]):
        place(out, music_box(base + step, 0.6 * intensity + 0.2, 1.2, pan), i * 0.07)
    return out


def bell_hit(intensity=0.7, pitch='mid', pan=0.0, key_root=72):
    note = key_root + {'low': -12, 'mid': 0, 'high': 12}[pitch]
    return bell(note, 0.5 + 0.5 * intensity, 3.0, pan)


def whoosh(dur, intensity=0.5, pitch='mid', pan=0.0, fast=False):
    f0, f1 = {'low': (180, 900), 'mid': (300, 2400), 'high': (900, 6000)}[pitch]
    x = noise(dur)
    # gore pa dole: brzo naraste, pa se spusti
    up = sweep_filter(x, f0, f1, q=1.6, steps=18)
    n = len(x)
    pk = 0.35 if fast else 0.55
    t = np.linspace(0, 1, n)
    e = np.where(t < pk, (t / pk) ** 2, np.exp(-(t - pk) / ((1 - pk) * 0.45)))
    y = up * e * intensity * (0.9 if fast else 0.7)
    # pan putuje kroz kadar (prolaz)
    L, R = [], []
    pan_track = np.clip(pan + np.linspace(-0.6, 0.6, n) * (1 if pan >= 0 else -1), -1, 1)
    p = (pan_track + 1) * np.pi / 4
    return np.stack([np.cos(p) * y, np.sin(p) * y], 1).astype(np.float32)


def swish(dur, intensity=0.5, pitch='high', pan=0.0):
    return whoosh(max(0.12, dur), intensity, pitch, pan, fast=True)


def flutter(dur, intensity=0.4, pitch='mid', pan=0.0):
    y = whoosh(dur, intensity, pitch, pan)
    t = np.arange(len(y)) / SR
    am = 0.55 + 0.45 * np.sin(2 * np.pi * (11 + 4 * np.sin(2 * np.pi * 0.7 * t)) * t)
    return (y * am[:, None]).astype(np.float32)


def swirl(dur, intensity=0.5, pitch='mid', pan=0.0):
    y = whoosh(dur, intensity, pitch, 0)
    mono = y.sum(1)
    t = np.arange(len(mono)) / SR
    p = (np.sin(2 * np.pi * 1.6 * t) * 0.8 + 1) * np.pi / 4
    return np.stack([np.cos(p) * mono, np.sin(p) * mono], 1).astype(np.float32)


def pop(intensity=0.5, pitch='mid', pan=0.0):
    f0, f1 = {'low': (420, 120), 'mid': (900, 220), 'high': (1800, 500)}[pitch]
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.012)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03)
    x[:int(0.002 * SR)] += hp(noise(0.002), 2000) * 0.6
    return stereo(x * intensity * 0.55, pan)


def bloop(intensity=0.4, pitch='mid', pan=0.0, dur=0.18):
    f0, f1 = {'low': (180, 520), 'mid': (300, 950), 'high': (600, 1900)}[pitch]
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur) ** 1.5
    return stereo(x * intensity * 0.45, pan)


def thud(intensity=0.5, pitch='low', pan=0.0, big=False):
    f0, f1 = {'low': (130, 48), 'mid': (220, 80), 'high': (380, 140)}[pitch]
    d = 0.35 if big else 0.22
    n = int(d * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.04)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.12 if big else 0.07))
    tr = lp(noise(0.03), 3000) * env_ad(int(0.03 * SR), 0.001, 0.008)
    x[:len(tr)] += tr * (0.6 if big else 0.35)
    return stereo(x * intensity * (0.95 if big else 0.7), pan)


def bounce(intensity=0.5, pitch='mid', pan=0.0):
    out = np.zeros((int(0.6 * SR), 2), np.float32)
    for i, (dt, a) in enumerate([(0, 1.0), (0.16, 0.45), (0.27, 0.2)]):
        place(out, thud(intensity * a, pitch, pan), dt)
        place(out, pop(intensity * a * 0.5, 'high', pan), dt)
    return out


def crack(intensity=0.6, pitch='mid', pan=0.0):
    n = int(0.5 * SR)
    burst = hp(noise(0.5), 1200) * env_ad(n, 0.001, 0.03)
    res = sum(bp(noise(0.5), f * 0.97, f * 1.03) * env_ad(n, 0.001, 0.06) * 6 for f in (1350, 2280, 3650))
    x = burst * 0.8 + res * 0.5
    out = stereo(x * intensity * 0.6, pan)
    place(out, crumble(0.4, intensity * 0.5, pitch, pan), 0.02)
    return out


def crumble(dur, intensity=0.5, pitch='mid', pan=0.0):
    n = int((dur + 0.2) * SR)
    out = np.zeros((n, 2), np.float32)
    lo, hi = {'low': (300, 2000), 'mid': (900, 5000), 'high': (2000, 9000)}[pitch]
    count = int(60 * dur * (0.5 + intensity))
    for i in range(count):
        tt = dur * (RNG.uniform(0, 1) ** 1.6)
        g = bp(noise(0.025), lo, hi) * env_ad(int(0.025 * SR), 0.0005, 0.006) * RNG.uniform(0.2, 1)
        place(out, stereo(g, np.clip(pan + RNG.uniform(-0.4, 0.4), -1, 1)), tt)
    return out * intensity * 0.8


def goo(dur, intensity=0.5, pitch='low', pan=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = noise(dur)
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 3.2 * t + np.sin(2 * np.pi * 0.9 * t) * 2)
    lo = bp(x, 120, 700) * (0.4 + 0.6 * lfo)
    y = lo * env_asr(n, 0.15, 0.4) * 0.6
    out = stereo(y * intensity, pan, 0.3)
    for i in range(int(dur * 7)):
        place(out, bloop(intensity * RNG.uniform(0.2, 0.5), 'low', pan + RNG.uniform(-0.3, 0.3), RNG.uniform(0.1, 0.22)), RNG.uniform(0, dur))
    return out


def snap(intensity=0.5, pitch='mid', pan=0.0):
    f = {'low': 900, 'mid': 1800, 'high': 3200}[pitch]
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * t) * 0.6 + hp(noise(0.08), 2500)) * np.exp(-t / 0.008)
    x += np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t / 0.02) * 0.4
    return stereo(x * intensity * 0.6, pan)


def click(intensity=0.4, pitch='high', pan=0.0):
    x = hp(noise(0.012), {'low': 1500, 'mid': 3000, 'high': 5000}[pitch]) * env_ad(int(0.012 * SR), 0.0003, 0.002)
    return stereo(x * intensity * 0.7, pan)


def glass_clink(intensity=0.5, pitch='high', pan=0.0):
    base = {'low': 1300, 'mid': 2100, 'high': 3100}[pitch]
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * base * r * t) * np.exp(-t / d) for r, a, d in [(1, 1, 0.35), (1.53, 0.6, 0.25), (2.31, 0.4, 0.15), (3.07, 0.2, 0.08)])
    x[:int(0.002 * SR)] += hp(noise(0.002), 4000)
    return stereo(x * intensity * 0.22, pan)


def glass_shine(dur, intensity=0.5, pan=0.0, key_root=72):
    n = int((dur + 0.6) * SR)
    x = sweep_filter(noise(dur + 0.6), 3000, 11000, q=3, steps=12) * env_asr(n, dur * 0.5, dur * 0.5 + 0.5) * 0.25
    out = stereo(x * intensity, pan, 0.5)
    place(out, sparkle(dur, intensity * 0.7, 'high', pan, key_root, 10), dur * 0.3)
    return out


def rumble(dur, intensity=0.5, pan=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = lp(noise(dur), 160, 4) * 3 * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 9 * t + RNG.uniform(0, 6))))
    return stereo(x * env_asr(n, 0.05, 0.2) * intensity * 0.7, pan, 0.2)


def glitch(dur, intensity=0.5, pan=0.0):
    n = int(dur * SR)
    out = np.zeros(n)
    i = 0
    while i < n:
        seg = int(RNG.uniform(0.015, 0.06) * SR)
        kind = RNG.integers(3)
        t = np.arange(seg) / SR
        if kind == 0:
            s = np.sign(np.sin(2 * np.pi * RNG.choice([220, 440, 880, 1320]) * t)) * 0.35
        elif kind == 1:
            s = np.round(RNG.uniform(-1, 1, seg) * 4) / 4 * 0.5
        else:
            s = np.zeros(seg)
        out[i:i + seg] = s[:max(0, min(seg, n - i))]
        i += seg
    return stereo(hp(out, 300) * intensity * 0.45, pan, 0.4)


def riser(dur, intensity=0.6, pitch='mid', pan=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 200 * (8 ** (t / dur))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    air = sweep_filter(noise(dur), 400, 8000, q=1.5, steps=16)
    e = (t / dur) ** 2
    return stereo((tone + air) * e * intensity * 0.6, pan, 0.5)


def downer(dur, intensity=0.5, pitch='mid', pan=0.0):
    y = riser(dur, intensity, pitch, pan)
    return y[::-1].copy()


def pour(dur, intensity=0.5, pitch='mid', pan=0.0):
    n = int(dur * SR)
    base = bp(noise(dur), 500, 2600) * 0.25 * env_asr(n, 0.08, 0.15)
    out = stereo(base * intensity, pan, 0.3)
    for i in range(int(dur * 14)):
        place(out, bloop(intensity * RNG.uniform(0.15, 0.4), RNG.choice(['mid', 'high']), pan + RNG.uniform(-0.2, 0.2), RNG.uniform(0.05, 0.11)), RNG.uniform(0, dur))
    return out


def drip(intensity=0.4, pitch='mid', pan=0.0):
    return bloop(intensity, pitch, pan, 0.09)


def splash(intensity=0.6, pitch='mid', pan=0.0):
    n = int(0.6 * SR)
    x = bp(noise(0.6), 600, 7000) * env_ad(n, 0.004, 0.09) * 0.6
    out = stereo(x * intensity, pan, 0.5)
    for i in range(8):
        place(out, bloop(intensity * RNG.uniform(0.15, 0.35), 'high', pan + RNG.uniform(-0.4, 0.4), RNG.uniform(0.05, 0.1)), RNG.uniform(0.02, 0.35))
    return out


def squirt(dur, intensity=0.5, pitch='mid', pan=0.0):
    n = int(dur * SR)
    x = sweep_filter(noise(dur), 700, 2600, q=4, steps=10) * env_asr(n, 0.02, dur * 0.5) * 0.8
    return stereo(x * intensity, pan, 0.2)


def crunch(intensity=0.5, pitch='mid', pan=0.0):
    return crumble(0.18, intensity, pitch, pan)


def creak(dur, intensity=0.4, pitch='low', pan=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = {'low': 140, 'mid': 260, 'high': 480}[pitch] * (1 + 0.15 * np.sin(2 * np.pi * 0.8 * t)) * (1 + 0.03 * RNG.standard_normal(n).cumsum() / np.sqrt(np.arange(1, n + 1)))
    saw = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    x = bp(saw, 300, 2500) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 23 * t))) * env_asr(n, 0.1, 0.2)
    return stereo(x * intensity * 0.25, pan)


def rustle(dur, intensity=0.4, pitch='high', pan=0.0):
    return crumble(dur, intensity * 0.6, 'high', pan)


def firework_launch(dur, intensity=0.6, pan=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 900 * (2.8 ** (t / dur))
    wh = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 * (t / dur)
    air = hp(noise(dur), 2500) * 0.12 * (t / dur)
    return stereo((wh + air) * intensity, pan, 0.3)


def boom(intensity=0.8, pan=0.0):
    out = thud(intensity, 'low', pan, big=True)
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * (45 + 30 * np.exp(-t / 0.08)) * t) * np.exp(-t / 0.35) * 0.6
    tail = lp(noise(1.4), 900) * np.exp(-t / 0.4) * 0.25
    o2 = stereo((sub + tail) * intensity, pan, 0.5)
    place(o2, out, 0)
    return o2


def crackle(dur, intensity=0.5, pan=0.0):
    n = int((dur + 0.1) * SR)
    out = np.zeros((n, 2), np.float32)
    for i in range(int(45 * dur * (0.5 + intensity))):
        tt = dur * RNG.uniform(0, 1) ** 1.3
        place(out, click(RNG.uniform(0.2, 1) * intensity, 'high', np.clip(pan + RNG.uniform(-0.8, 0.8), -1, 1)), tt)
    return out


def firework_burst(intensity=0.9, pan=0.0, key_root=72):
    out = np.zeros((int(3.2 * SR), 2), np.float32)
    place(out, boom(intensity, pan), 0)
    place(out, crackle(1.6, intensity * 0.8, pan), 0.08)
    place(out, sparkle(1.8, intensity, 'high', pan, key_root, 22), 0.05)
    return out


def heart_ping(intensity=0.35, pitch='high', pan=0.0, key_root=72):
    note = key_root + {'low': 12, 'mid': 19, 'high': 24}[pitch] + PENTA[RNG.integers(5)]
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * mtof(note) * t * (1 + 0.004 * np.sin(2 * np.pi * 6 * t))) * np.exp(-t / 0.35) * np.minimum(1, t / 0.004)
    return stereo(x * intensity * 0.25, pan)


def chirp(intensity=0.4, pitch='high', pan=0.0):
    out = np.zeros((int(0.4 * SR), 2), np.float32)
    for i in range(3):
        n = int(0.05 * SR)
        t = np.arange(n) / SR
        f = 2600 + 1800 * np.sin(np.pi * t / 0.05)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.05)
        place(out, stereo(x * intensity * 0.18, pan), i * 0.075)
    return out


def sting(intensity=0.8, pan=0.0, key_root=72, chord=(0, 4, 7, 12)):
    out = np.zeros((int(4.5 * SR), 2), np.float32)
    for i, s in enumerate(chord):
        place(out, bell(key_root + s, 0.5 * intensity, 4.2, (i - 1.5) * 0.25), i * 0.012)
    place(out, shimmer(1.5, intensity * 0.6, 'high', pan, key_root), 0)
    return out


def render_event(ev, key_root=72):
    """Pretvara jedan red iz tabele efekata u zvuk."""
    ty, d, i, p, pi = ev['type'], max(0.05, ev['dur']), ev['intensity'], ev['pan'], ev['pitch']
    f = {
        'whoosh_soft': lambda: whoosh(d, i, pi, p), 'whoosh_fast': lambda: whoosh(d, i, pi, p, fast=True),
        'swish': lambda: swish(d, i, pi, p), 'flutter': lambda: flutter(d, i, pi, p),
        'sparkle': lambda: sparkle(d, i, pi, p, key_root), 'shimmer': lambda: shimmer(d, i, pi, p, key_root),
        'magic_wand': lambda: magic_wand(d, i, p, key_root), 'twinkle': lambda: twinkle(d, i, pi, p, key_root),
        'chime': lambda: chime(d, i, pi, p, key_root), 'bell_hit': lambda: bell_hit(i, pi, p, key_root),
        'pop': lambda: pop(i, pi, p), 'bloop': lambda: bloop(i, pi, p, min(0.35, max(0.1, d))),
        'thud_soft': lambda: thud(i, pi, p), 'impact': lambda: thud(i, pi, p, big=True), 'bounce': lambda: bounce(i, pi, p),
        'crack': lambda: crack(i, pi, p), 'crumble': lambda: crumble(d, i, pi, p), 'goo': lambda: goo(d, i, pi, p),
        'snap': lambda: snap(i, pi, p), 'click': lambda: click(i, pi, p), 'glass_clink': lambda: glass_clink(i, pi, p),
        'glass_shine': lambda: glass_shine(d, i, p, key_root), 'rumble': lambda: rumble(d, i, p), 'shake': lambda: rumble(d, i, p),
        'glitch': lambda: glitch(d, i, p), 'riser': lambda: riser(d, i, pi, p), 'downer': lambda: downer(d, i, pi, p),
        'swirl': lambda: swirl(d, i, pi, p), 'pour': lambda: pour(d, i, pi, p), 'drip': lambda: drip(i, pi, p),
        'splash': lambda: splash(i, pi, p), 'squirt': lambda: squirt(d, i, pi, p), 'crunch': lambda: crunch(i, pi, p),
        'creak': lambda: creak(d, i, pi, p), 'rustle': lambda: rustle(d, i, pi, p),
        'firework_launch': lambda: firework_launch(d, i, p), 'firework_burst': lambda: firework_burst(i, p, key_root),
        'crackle': lambda: crackle(d, i, p), 'boom': lambda: boom(i, p), 'heart_ping': lambda: heart_ping(i, pi, p, key_root),
        'sting': lambda: sting(i, p, key_root), 'chirp': lambda: chirp(i, pi, p),
    }[ty]
    return f().astype(np.float32)
