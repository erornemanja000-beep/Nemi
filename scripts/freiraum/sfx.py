#!/usr/bin/env python3
"""Zvučni efekti i ambijenti za Freiraum sajt, sintetizovano (na osnovu scripts/sound/synth.py).

    python3 sfx.py outdir/            -> outdir/*.mp3 + outdir/_pregled.mp3 (sve redom, za slušanje)

Jednokratni efekti su normalizovani na -1 dBFS (glasnoću podešava sajt kroz WebAudio),
ambijenti su petlje bez šava (poslednje 2 s pretopljene u početak).
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sound'))
import synth as S  # noqa: E402

SR = S.SR
RNG = np.random.default_rng(117)


def buf(dur):
    return np.zeros((int(dur * SR), 2), np.float32)


def mono_env(x, e):
    return (x * e[:len(x)]).astype(np.float32)


# ---------------------------------------------------------------- jednokratni
def spray_rattle():
    """Kuglica u limenci: 5 protresanja, svako sa 2-3 metalna udarca."""
    out = buf(1.5)
    for k in range(5):
        t0 = 0.08 + k * 0.24
        for j in range(RNG.integers(2, 4)):
            n = int(0.05 * SR)
            t = np.arange(n) / SR
            f = RNG.uniform(2300, 3400)
            x = sum(a * np.sin(2 * np.pi * f * r * t) for r, a in [(1, 1), (2.76, 0.5), (5.4, 0.25)])
            x = (x * np.exp(-t / 0.012) + S.hp(S.noise(0.05), 3000) * np.exp(-t / 0.004) * 0.6)
            S.place(out, S.stereo(x * RNG.uniform(0.35, 0.6), RNG.uniform(-0.2, 0.2)), t0 + j * 0.035)
        S.place(out, S.stereo(S.lp(S.noise(0.12), 900) * np.hanning(int(0.12 * SR)) * 0.25), t0 - 0.03)
    return out


def spray_hiss(dur=3.4, strokes=((0.0, 0.7), (0.78, 1.4), (1.5, 2.25), (2.35, 3.2))):
    """Šištanje spreja koje prati poteze crtanja (početak, kraj u sekundama)."""
    n = int(dur * SR)
    x = S.bp(S.noise(dur), 2200, 11000, 3)
    x += S.bp(S.noise(dur), 6000, 14000, 2) * 0.5
    t = np.arange(n) / SR
    x *= 0.85 + 0.15 * np.sin(2 * np.pi * 7 * t + RNG.uniform(0, 6))
    e = np.zeros(n)
    for a, b in strokes:
        i, j = int(a * SR), min(n, int(b * SR))
        e[i:j] = S.env_asr(j - i, 0.025, 0.06)
    return S.stereo(x * e * 0.5, 0, 0.3)


def spray_loop():
    x = S.bp(S.noise(2.6), 2200, 11000, 3) + S.bp(S.noise(2.6), 6000, 14000, 2) * 0.5
    return loopify(S.stereo(x * 0.5, 0, 0.3), 0.6)


def door():
    out = buf(1.6)
    S.place(out, S.click(0.8, 'mid', -0.1), 0.0)            # kvaka
    S.place(out, S.click(0.5, 'low', -0.1), 0.05)
    S.place(out, S.creak(0.45, 0.25, 'low', 0.1), 0.12)       # šarke
    S.place(out, S.whoosh(0.9, 0.35, 'low', 0.2), 0.2)        # vazduh iznutra
    return out


def switch():
    out = buf(0.4)
    S.place(out, S.click(0.9, 'mid'), 0)
    S.place(out, S.thud(0.25, 'mid'), 0.004)
    S.place(out, S.click(0.4, 'high'), 0.06)
    return out


def clock_tick():
    out = buf(0.25)
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 4200 * t) * 0.5 + S.hp(S.noise(0.03), 2500)) * np.exp(-t / 0.004)
    S.place(out, S.stereo(x * 0.45, 0.15), 0)
    return out


def chime_17():
    """Blagi zvon za 17:00 (A-dur, topao)."""
    out = buf(4.8)
    for i, s in enumerate((0, 4, 7, 12)):
        S.place(out, S.bell(57 + 12 + s, 0.45, 4.4, (i - 1.5) * 0.3), i * 0.09)
    S.place(out, S.shimmer(1.4, 0.25, 'high', 0, 69), 0.05)
    return out


def fire_whoosh():
    out = buf(3.0)
    S.place(out, S.whoosh(1.6, 0.8, 'low', 0), 0)
    S.place(out, S.rumble(2.2, 0.5), 0.25)
    S.place(out, S.crackle(2.4, 0.55), 0.3)
    return out


def espresso():
    """Mlaz pare pa curenje kafe."""
    out = buf(3.6)
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    steam = S.bp(S.noise(2.0), 1800, 9000, 2) * S.env_asr(n, 0.08, 0.5)
    steam *= 0.8 + 0.2 * np.sin(2 * np.pi * 23 * t)
    S.place(out, S.stereo(steam * 0.45, -0.2, 0.3), 0)
    S.place(out, S.pour(1.6, 0.35, 'low', 0.1), 1.7)
    for k in range(5):
        S.place(out, S.drip(0.25, 'mid', 0.1), 2.0 + k * 0.28 + RNG.uniform(0, 0.05))
    return out


def cup():
    out = buf(1.0)
    S.place(out, S.glass_clink(0.55, 'low', 0.1), 0)
    S.place(out, S.thud(0.2, 'mid', 0.1), 0)
    return out


def ice():
    out = buf(1.6)
    for k in range(6):
        S.place(out, S.glass_clink(RNG.uniform(0.25, 0.6), 'high', RNG.uniform(-0.3, 0.3)), k * RNG.uniform(0.06, 0.16))
    return out


def wings():
    return S.flutter(1.1, 0.45, 'mid', 0)


def spielraum_chimes():
    out = buf(2.6)
    S.place(out, S.sparkle(1.6, 0.55, 'high', 0, 76, 16), 0)
    for k, nt in enumerate((76, 79, 81, 84, 88)):
        S.place(out, S.harp(nt, 0.5, -0.4 + k * 0.2), 0.05 + k * 0.08)
    return out


def ui_hover():
    out = buf(0.15)
    S.place(out, S.bloop(0.18, 'high', 0, 0.08), 0)
    return out


def ui_click():
    out = buf(0.3)
    S.place(out, S.pop(0.35, 'mid'), 0)
    return out


def confetti():
    out = buf(2.6)
    for k in range(6):
        S.place(out, S.pop(RNG.uniform(0.3, 0.6), 'mid', RNG.uniform(-0.6, 0.6)), k * 0.07)
    S.place(out, S.sparkle(2.0, 0.6, 'high', 0, 72, 22), 0.1)
    return out


# ---------------------------------------------------------------- ambijenti
def babble(dur, voices=12, level=0.5, bright=3200):
    """Žamor: više „glasova" (šum kroz formante sa slogovnim ritmom), rasutih po panorami."""
    n = int(dur * SR)
    out = np.zeros((n, 2), np.float32)
    t = np.arange(n) / SR
    for v in range(voices):
        f1, f2 = RNG.uniform(350, 800), RNG.uniform(1100, 2300)
        x = S.bp(S.noise(dur), f1 * 0.8, f1 * 1.25, 2) + 0.6 * S.bp(S.noise(dur), f2 * 0.85, f2 * 1.15, 2)
        rate = RNG.uniform(3.2, 5.5)
        syl = np.clip(np.sin(2 * np.pi * rate * t + RNG.uniform(0, 6)) + RNG.uniform(-0.2, 0.4), 0, None)
        phrase = np.clip(np.sin(2 * np.pi * RNG.uniform(0.08, 0.2) * t + RNG.uniform(0, 6)) + 0.3, 0, 1)
        x = S.lp(x * syl * phrase, bright)
        out += S.stereo(x * RNG.uniform(0.6, 1.0), RNG.uniform(-0.8, 0.8))
    ir = S.make_ir(1.4, 0.4, 0.02, 5000)
    out = S.reverb(out, ir, 0.35)[:n]
    return out / (np.abs(out).max() + 1e-9) * level


def clinks(dur, rate=0.8):
    out = np.zeros((int(dur * SR), 2), np.float32)
    t = RNG.uniform(0.2, 1.0)
    while t < dur - 1:
        fn = RNG.choice([lambda: S.glass_clink(RNG.uniform(0.1, 0.25), 'mid', RNG.uniform(-0.7, 0.7)),
                         lambda: S.click(RNG.uniform(0.08, 0.18), 'high', RNG.uniform(-0.7, 0.7))])
        S.place(out, fn(), t)
        t += RNG.exponential(1 / rate)
    return out


def loopify(x, fade=2.0):
    """Petlja bez šava: rep se pretopi u početak."""
    nf = int(fade * SR)
    body, tail = x[:-nf].copy(), x[-nf:]
    w = np.linspace(0, 1, nf)[:, None]
    body[:nf] = body[:nf] * w + tail * (1 - w)
    return body


def amb_street(dur=16):
    n = int(dur * SR)
    t = np.arange(n) / SR
    traffic = S.stereo(S.lp(S.noise(dur), 380, 3) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t)), 0, 0.6) * 1.6
    out = traffic + babble(dur, 8, 0.25, 2600)
    for k in range(3):
        S.place(out, S.whoosh(3.0, 0.25, 'low', RNG.uniform(-0.8, 0.8)), RNG.uniform(1, dur - 4))
    return loopify(out)


def amb_cafe(dur=16):
    out = babble(dur, 16, 0.5) + clinks(dur, 1.1)
    return loopify(out)


def amb_lounge(dur=16):
    out = babble(dur, 8, 0.28, 2600) + clinks(dur, 0.5)
    pads = np.zeros_like(out)
    for i, ch in enumerate(([57, 61, 64, 68], [54, 57, 61, 64], [50, 54, 57, 61], [52, 56, 59, 62])):
        S.place(pads, S.pad(ch, 4.4, 0.35, 1400), i * 4)
    return loopify(out + pads[:len(out)] * 0.6)


def amb_fire(dur=14):
    n = int(dur * SR)
    t = np.arange(n) / SR
    roar = S.stereo(S.lp(S.noise(dur), 260, 3) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.3 * t)), 0, 0.5) * 2.2
    out = roar.copy()
    S.place(out, S.crackle(dur - 0.2, 0.45) * 0.8, 0)
    return loopify(out)


def amb_night(dur=16):
    n = int(dur * SR)
    out = babble(dur, 10, 0.25, 2200)
    beat = np.zeros((n, 2), np.float32)
    k = 0.0
    while k < dur - 0.5:           # prigušen bas iz susedne prostorije, 118 bpm
        S.place(beat, S.thud(0.35, 'low', 0, True), k)
        k += 60 / 118
    beat = np.stack([S.lp(beat[:, 0], 140), S.lp(beat[:, 1], 140)], 1).astype(np.float32)
    return loopify(out + beat * 0.9)


# ---------------------------------------------------------------- izvoz
def normalize(x, peak_db=-1.0):
    return x / (np.abs(x).max() + 1e-9) * 10 ** (peak_db / 20)


def write_mp3(x, path, kbps=128):
    wav = path[:-4] + '.wav'
    y = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(wav, 'wb') as w:
        w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes(y.tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-ar', '44100', '-b:a', f'{kbps}k', path], check=True)
    os.remove(wav)


SHOTS = [spray_rattle, spray_hiss, door, switch, clock_tick, chime_17, fire_whoosh, espresso, cup, ice,
         wings, spielraum_chimes, ui_hover, ui_click, confetti]
LOOPS = [spray_loop, amb_street, amb_cafe, amb_lounge, amb_fire, amb_night]


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    preview = []
    for fn in SHOTS + LOOPS:
        x = normalize(fn(), -1.0 if fn in SHOTS else -3.0)
        write_mp3(x, os.path.join(outdir, fn.__name__ + '.mp3'), 128 if fn in LOOPS else 112)
        preview += [x[:int(6 * SR)], buf(0.6)]
        print(fn.__name__, f'{len(x) / SR:.1f}s')
    write_mp3(np.concatenate(preview), os.path.join(outdir, '_pregled.mp3'))


if __name__ == '__main__':
    main(sys.argv[1])
