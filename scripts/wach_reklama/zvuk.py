#!/usr/bin/env python3
"""Zvuk za WACH. reklamu (12 s): budilnik, hrkanje, pad limenke, ritam 120 BPM od udara (4.5 s), led, završni akord.

python3 scripts/wach_reklama/zvuk.py <izlaz.wav>   (samo numpy, 48 kHz stereo)
"""
import sys
import wave
import numpy as np

SR, DUR = 48000, 12.0
N = int(SR * DUR)
RNG = np.random.default_rng(5)
mix = np.zeros((N, 2))


def ta(d):
    return np.arange(int(d * SR)) / SR


def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    if hi:
        X *= 1 / np.sqrt(1 + (f / hi) ** 4)
    if lo:
        X *= 1 - 1 / np.sqrt(1 + (f / lo) ** 4)
    return np.fft.irfft(X, len(x))


def put(sig, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    p = (pan + 1) * np.pi / 4
    mix[i:i + len(sig), 0] += sig * g * np.cos(p) * 1.41
    mix[i:i + len(sig), 1] += sig * g * np.sin(p) * 1.41


def tone(f, d, dec=8.0, kind='sin'):
    t = ta(d)
    ph = 2 * np.pi * f * t
    w = np.sin(ph) if kind == 'sin' else np.sign(np.sin(ph)) * 0.6
    return w * np.exp(-t * dec)


def kick(g=1.0):
    t = ta(0.4)
    ph = 2 * np.pi * np.cumsum(45 + 120 * np.exp(-t * 35)) / SR
    return (np.sin(ph) * np.exp(-t * 7) + 0.2 * RNG.standard_normal(len(t)) * np.exp(-t * 90)) * g


def clap():
    t = ta(0.25)
    n = filt(RNG.standard_normal(len(t)), lo=900, hi=6000)
    env = sum(np.exp(-np.maximum(t - o, 0) * 60) * (t >= o) for o in (0, 0.012, 0.024)) * np.exp(-t * 10)
    return n / np.abs(n).max() * env * 0.8


def hat():
    t = ta(0.05)
    n = filt(RNG.standard_normal(len(t)), lo=7000)
    return n / np.abs(n).max() * np.exp(-t * 90)


def whoosh(d=0.5, lo=300, hi=5000):
    t = ta(d)
    n = filt(RNG.standard_normal(len(t)), lo, hi)
    return n / np.abs(n).max() * np.sin(np.pi * t / d) ** 2


def boom():
    t = ta(1.5)
    sub = np.sin(2 * np.pi * np.cumsum(32 + 110 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.5)
    crash = filt(RNG.standard_normal(len(t)), lo=3500) * np.exp(-t * 4) * 0.3
    return sub + crash


def saw_chord(notes, d, fc=2500, att=0.01, dec=1.2):
    t = ta(d)
    x = np.zeros(len(t))
    for m in notes:
        f = 440 * 2 ** ((m - 69) / 12)
        for det in (-0.15, 0, 0.15):
            x += 2 * ((f * (1 + det / 100) * t + RNG.random()) % 1) - 1
    x = filt(x, hi=fc) / (len(notes) * 3)
    return x * np.minimum(1, t / att) * np.exp(-t / dec)


# 0–1: tiha noćna podloga
put(saw_chord([50, 57, 62, 65], 4.2, fc=700, att=0.8, dec=6) * np.minimum(1, (4.2 - ta(4.2)) / 0.3), 0.0, 0.25)
# 1–2: budilnik
for k in range(8):
    put(tone(2100, 0.07, 30, 'sq'), 1.0 + k * 0.125, 0.22, pan=0.2 * ((-1) ** k))
put(kick(0.6), 1.0, 0.5)
# 2.0: snooze klik
put(tone(900, 0.05, 80), 2.05, 0.6)
put(tone(300, 0.08, 40), 2.05, 0.6)
# 2.4–3.9: hrkanje (filtriran šum, udisaj/izdisaj)
for s in (2.5, 3.25):
    t = ta(0.7)
    n = filt(RNG.standard_normal(len(t)), lo=80, hi=500) * (np.sin(np.pi * t / 0.7) ** 2) * (1 + 0.5 * np.sin(2 * np.pi * 28 * t))
    put(n / np.abs(n).max(), s, 0.35)
# 3.9–4.5: zvižduk pada
t = ta(0.6)
put(np.sin(2 * np.pi * np.cumsum(1800 - 1300 * t / 0.6) / SR) * (t / 0.6) * 0.5, 3.9, 0.35)
# 4.5: udar + ritam
put(boom(), 4.5, 1.0)
put(kick(1.2), 4.5, 1.0)
bass = [38, 38, 41, 43]
beat = 0.5
k = 0
while 4.5 + k * beat < 10.45:
    at = 4.5 + k * beat
    put(kick(), at, 0.85)
    if k % 2 == 1:
        put(clap(), at, 0.45)
    put(hat(), at + beat / 2, 0.18, pan=0.3)
    put(hat(), at + beat / 4 * 3, 0.08, pan=-0.3)
    m = bass[(k // 4) % 4]
    tb = ta(beat * 0.9)
    f = 440 * 2 ** ((m - 69) / 12)
    put(filt(np.sign(np.sin(2 * np.pi * f * tb)) * np.exp(-tb * 4), hi=500), at, 0.25)
    k += 1
# akordi na reči i promene boja
for at, ch in [(5.0, [62, 66, 69, 74]), (6.0, [64, 67, 71, 76]), (7.0, [66, 69, 74, 78]), (8.0, [62, 66, 69, 74])]:
    put(whoosh(0.45), at - 0.3, 0.35)
    put(saw_chord(ch, 0.9, fc=3500, dec=0.35), at, 0.3)
    put(tone(1400, 0.1, 40), at, 0.25)
# led: zvonjava na doskocima kocki
for t0, i in zip([8.0, 8.15, 8.35, 8.5, 8.7, 8.9, 9.05], range(7)):
    for b in (0.33, 0.55, 0.7):
        put(tone(3000 + i * 230, 0.12, 35), t0 + 0.9 * b, 0.12, pan=-0.6 + i * 0.2)
        put(tone(4700 + i * 180, 0.08, 50), t0 + 0.9 * b, 0.06, pan=-0.6 + i * 0.2)
# 10.5: CTA + završni akord
put(saw_chord([50, 57, 62, 66, 69, 74], 1.5, fc=4000, dec=0.9), 10.5, 0.45)
put(kick(1.1), 10.5, 0.9)
put(tone(1600, 0.12, 25), 10.5, 0.3)
mix *= np.minimum(1, (DUR - np.arange(N) / SR) / 0.25)[:, None]
mix = np.tanh(mix * 1.3)
mix /= np.abs(mix).max() / 0.9
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', sys.argv[1])
