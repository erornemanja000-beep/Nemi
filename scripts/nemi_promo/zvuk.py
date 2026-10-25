#!/usr/bin/env python3
"""Zvuk za Nemi Studio promo (10 s): podloga + efekti vezani za vremena iz promo.html.

python3 scripts/nemi_promo/zvuk.py <izlaz.wav>
Sve je sintetizovano (samo numpy), 48 kHz stereo.
"""
import sys
import wave
import numpy as np

SR = 48000
DUR = 10.0
N = int(SR * DUR)
RNG = np.random.default_rng(3)
mix = np.zeros((N, 2), np.float64)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def lowpass(x, fc):
    """Niskopropusni filter preko FFT (fc može biti broj ili niz po vremenu se ne koristi)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def highpass(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def put(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    if sig.ndim == 1:
        p = (pan + 1) * np.pi / 4
        sig = np.stack([np.cos(p) * sig, np.sin(p) * sig], 1) * np.sqrt(2)
    mix[i : i + len(sig)] += sig * gain


def thud(f0=110, f1=42, d=0.35):
    t = t_axis(d)
    ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 30)) / SR
    return np.sin(ph) * np.exp(-t * 9) + 0.15 * RNG.standard_normal(len(t)) * np.exp(-t * 80)


def kick():
    return thud(160, 45, 0.45) * 1.1


def pop(f=900, d=0.09):
    t = t_axis(d)
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.8 * np.exp(-t * 60))) / SR
    return np.sin(ph) * np.exp(-t * 45)


def tick(f=2400):
    t = t_axis(0.04)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 140)


def whoosh(d=0.6, peak=0.5, lo=300, hi=3000):
    t = t_axis(d)
    n = RNG.standard_normal(len(t))
    env = np.exp(-((t / d - peak) ** 2) / 0.04)
    a = lowpass(highpass(n, lo), hi)
    return a * env / (np.abs(a).max() + 1e-9)


def riser(d=0.5):
    t = t_axis(d)
    n = highpass(RNG.standard_normal(len(t)), 800)
    k = t / d
    tone = np.sin(2 * np.pi * np.cumsum(200 + 1600 * k ** 2) / SR) * 0.4
    return (n / np.abs(n).max() * 0.6 + tone) * k ** 2.5


def boom(d=1.8):
    t = t_axis(d)
    sub = np.sin(2 * np.pi * np.cumsum(30 + 90 * np.exp(-t * 12)) / SR) * np.exp(-t * 2.2)
    crash = highpass(RNG.standard_normal(len(t)), 4000) * np.exp(-t * 3.5) * 0.35
    return sub + crash


def chord(notes, d, attack=0.02, decay=1.5, fc=1800):
    t = t_axis(d)
    x = np.zeros(len(t))
    for m in notes:
        f = 440 * 2 ** ((m - 69) / 12)
        for det in (-0.12, 0.0, 0.12):
            ph = (f * (1 + det / 100) * t + RNG.random()) % 1
            x += 2 * ph - 1
    x = lowpass(x, fc) / (len(notes) * 3)
    env = np.minimum(1, t / attack) * np.exp(-t / decay)
    return x * env


def pad(notes, d, fc):
    t = t_axis(d)
    x = np.zeros(len(t))
    for m in notes:
        f = 440 * 2 ** ((m - 69) / 12)
        for det in (-0.2, 0.2):
            x += np.sin(2 * np.pi * f * (1 + det / 100) * t) + 0.3 * np.sin(4 * np.pi * f * t)
    x = lowpass(x, fc) / len(notes)
    env = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.3)
    return x * env


# ------------------------------------------------ lopta
for at, g in [(0.42, 0.9), (0.74, 0.6), (0.95, 0.4)]:
    put(thud(130, 50, 0.3), at, g)
put(riser(0.3), 1.0, 0.5)
put(boom(1.2), 1.3, 0.7)
put(kick(), 1.3, 0.8)

# ------------------------------------------------ logo
for i in range(5):
    put(pop(500 + i * 120), 1.55 + i * 0.1, 0.5, pan=-0.4 + i * 0.2)
put(whoosh(0.6, 0.4, 2000, 9000), 2.0, 0.25)

# podloga: bas puls i pad od 1.3 do 8.2 (F-mol: F, Db, Eb)
beat = 0.275
k = 1.3
bass_notes = [29, 29, 25, 27]
while k < 8.1:
    bar = int((k - 1.3) / (beat * 8)) % 4
    t = t_axis(beat * 0.9)
    f = 440 * 2 ** ((bass_notes[bar] - 69) / 12)
    b = lowpass(np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 6), 400)
    put(b, k, 0.22)
    put(tick(7000) * RNG.uniform(0.5, 1), k + beat / 2, 0.08, pan=0.3)
    k += beat
put(pad([53, 56, 60, 63], 6.95, 900), 1.3, 0.14)

# ------------------------------------------------ kocka: tri okreta
for s in (3.05, 4.15, 5.25):
    put(whoosh(0.62, 0.5, 250, 4000), s, 0.55, pan=0)
    put(kick(), s + 0.31, 0.75)
for s, n in ((3.35, 9), (4.45, 7), (5.55, 12)):
    for i in range(n):
        put(tick(1800 + i * 90), s + i * 0.025 + 0.12, 0.18, pan=-0.5 + i / n)

# ------------------------------------------------ uređaji
put(whoosh(0.7, 0.6, 150, 2500), 6.1, 0.6)
put(whoosh(0.6, 0.3, 400, 6000), 6.4, 0.45, pan=0.3)
for at, f in [(6.6, 600), (6.8, 900), (6.88, 1000), (6.96, 1100), (7.04, 1300), (6.9, 700), (7.15, 800), (7.24, 950), (7.33, 1100)]:
    put(pop(f), at, 0.4, pan=(f - 900) / 900)

# ------------------------------------------------ završnica
put(riser(0.45), 7.78, 0.7)
put(boom(1.8), 8.22, 1.0)
put(kick(), 8.22, 1.0)
put(chord([53, 60, 65, 68, 72], 1.78, 0.01, 1.4, 2600), 8.22, 0.35)
for i in range(13):
    put(tick(2200 + i * 110), 8.6 + i * 0.035 + 0.16, 0.16, pan=-0.6 + i * 0.1)
put(pop(1400, 0.12), 9.18, 0.5)
# blagi utišaj kraja
fade = np.minimum(1, (DUR - np.arange(N) / SR) / 0.35)[:, None]
mix *= fade

# ------------------------------------------------ master: soft-clip i normalizacija
mix = np.tanh(mix * 1.2)
mix /= np.abs(mix).max() / 0.89
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok", sys.argv[1])
