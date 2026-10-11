#!/usr/bin/env python3
"""Pravi zvučnu podlogu intro filma iz tabele efekata i plana muzike.

  python3 mix.py cues.json music.json out.wav [--dur 37.367]

cues.json:  {"events": [{"t", "dur", "type", "intensity", "pan", "pitch", "what"}, ...]}
music.json: {"key", "bpm", "sections", "chords", "melody", "counter", "accents"}
Rezultat: stereo WAV 48 kHz, glasnoća oko -16 LUFS (web), bez seckanja vrhova.
"""
import argparse, json, os, sys, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import synth as S  # noqa: E402

SR = S.SR
KEYS = {'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63, 'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67,
        'G#': 68, 'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71}


def key_root(key):
    k = key.strip().split()[0].replace('♭', 'b').replace('♯', '#')
    k = k[:2] if len(k) > 1 and k[1] in '#b' else k[:1]
    return KEYS.get(k.capitalize(), 72) % 12 + 72   # koren lestvice u oktavi C5..B5


def curve(points, n, default=1.0):
    """Glatka kriva glasnoće iz tačaka (vreme, vrednost)."""
    if not points:
        return np.full(n, default, np.float32)
    pts = sorted(points)
    t = np.arange(n) / SR
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts]).astype(np.float32)


def render_music(m, n):
    root = key_root(m.get('key', 'C'))
    mus = np.zeros((n, 2), np.float32)
    pads = np.zeros((n, 2), np.float32)
    beat = 60.0 / max(40, m.get('bpm', 90))
    for c in m.get('chords', []):
        S.place(pads, S.pad(c['notes'], c['dur'] + 0.15, 0.55), c['t'])
        S.place(mus, S.bass(c['bass'], min(c['dur'], 2.4), 0.55), c['t'])
    for k, nt in enumerate(m.get('melody', [])):
        S.place(mus, S.music_box(nt['note'], 0.35 + 0.6 * nt.get('vel', 0.7), max(0.4, nt['dur']), 0.12 * np.sin(k)), nt['t'])
    for k, nt in enumerate(m.get('counter', [])):
        S.place(mus, S.harp(nt['note'], 0.3 + 0.5 * nt.get('vel', 0.6), -0.25 + 0.5 * ((k % 4) / 3)), nt['t'])
    # dinamika po delovima
    secs = m.get('sections', [])
    dyn = []
    for s in secs:
        dyn += [(s['start'] + 0.05, 0.35 + 0.65 * s['dynamics']), (s['end'] - 0.05, 0.35 + 0.65 * s['dynamics'])]
    g = curve(dyn, n)
    # lagani šejker u življim delovima
    perc = np.zeros((n, 2), np.float32)
    for s in secs:
        if s['dynamics'] >= 0.55 and any('shaker' in x.lower() or 'perc' in x.lower() for x in s.get('instruments', [])):
            t = s['start']
            k = 0
            while t < s['end'] - 0.05:
                S.place(perc, S.shaker(0.25 + (0.15 if k % 2 == 0 else 0), 0.25 if k % 2 else -0.15), t)
                t += beat / 2
                k += 1
    # naglasci
    acc_pts = []
    for a in m.get('accents', []):
        if a['kind'] == 'drop_out':
            acc_pts += [(a['t'] - 0.08, 1.0), (a['t'], 0.12), (a['t'] + 0.6, 0.12), (a['t'] + 1.2, 1.0)]
        elif a['kind'] == 'stop':
            acc_pts += [(a['t'] - 0.05, 1.0), (a['t'], 0.0)]
        elif a['kind'] == 'swell':
            acc_pts += [(a['t'] - 1.2, 0.85), (a['t'], 1.15), (a['t'] + 0.4, 1.0)]
        elif a['kind'] == 'hit':
            S.place(mus, S.bell(root, 0.45, 3.0), a['t'])
        elif a['kind'] == 'final_chord':
            S.place(mus, S.sting(0.85, 0, root, (0, 4, 7, 12, 16)), a['t'])
    ga = curve(acc_pts, n) if acc_pts else np.ones(n, np.float32)
    out = (mus + pads * 1.0 + perc) * (g * ga)[:, None]
    return out, root


def duck_curve(events, n):
    """Muzika se malo stiša ispod velikih udaraca (napad 10 ms, povratak 350 ms)."""
    d = np.zeros(n, np.float32)
    for e in events:
        if e['intensity'] >= 0.72:
            i0 = int(e['t'] * SR)
            i1 = min(n, i0 + int((min(e['dur'], 0.8) + 0.05) * SR))
            if i0 < n:
                d[max(0, i0 - int(0.01 * SR)):i1] = np.maximum(d[max(0, i0 - int(0.01 * SR)):i1], 0.42 * e['intensity'])
    # glatko vraćanje
    out = np.empty_like(d)
    acc = 0.0
    rel = np.exp(-1 / (0.35 * SR))
    for i, v in enumerate(d):
        acc = v if v > acc else acc * rel
        out[i] = acc
    return 1 - out


def limiter(x, ceiling=0.89, look=0.004, release=0.12):
    a = np.max(np.abs(x), 1)
    la = int(look * SR)
    # najveća vrednost u narednih la uzoraka
    from numpy.lib.stride_tricks import sliding_window_view
    pad = np.concatenate([a, np.zeros(la)])
    peak = sliding_window_view(pad, la + 1).max(1)[:len(a)]
    need = np.minimum(1.0, ceiling / np.maximum(peak, 1e-9))
    g = np.empty_like(need)
    acc = 1.0
    rel = np.exp(-1 / (release * SR))
    for i, v in enumerate(need):
        acc = v if v < acc else 1 - (1 - acc) * rel
        g[i] = acc
    return x * g[:, None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cues'); ap.add_argument('music'); ap.add_argument('out')
    ap.add_argument('--dur', type=float, default=37.367)
    ap.add_argument('--lufs', type=float, default=-16.0)
    ap.add_argument('--music-gain', type=float, default=1.0)
    ap.add_argument('--sfx-gain', type=float, default=1.0)
    ap.add_argument('--stems', action='store_true')
    a = ap.parse_args()
    cues = json.load(open(a.cues))
    events = sorted(cues['events'], key=lambda e: e['t'])
    music = json.load(open(a.music))
    n = int(a.dur * SR)

    mus, root = render_music(music, n + SR * 2)
    mus = mus[:n]
    sfx = np.zeros((n + SR * 4, 2), np.float32)
    for e in events:
        y = S.render_event(e, root) * (0.55 + 0.45 * e['intensity'])
        S.place(sfx, y, e['t'])
    sfx = sfx[:n]

    ir_long = S.make_ir(2.6, 0.75, 0.025, 6000, seed=5)
    ir_short = S.make_ir(1.2, 0.35, 0.012, 7500, seed=9)
    mus = S.reverb(mus, ir_long, 0.30)
    sfx = S.reverb(sfx, ir_short, 0.16)
    mus *= duck_curve(events, n)[:, None]

    mix = mus * 0.9 * a.music_gain + sfx * 1.0 * a.sfx_gain
    mix = np.stack([S.hp(mix[:, c], 28) for c in range(2)], 1)
    # na kraju kratko utišavanje da nema pucketanja
    fade = int(0.25 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 0.5
    mix[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))[:, None]

    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    for _ in range(3):
        lufs = meter.integrated_loudness(mix.astype(np.float64))
        mix = mix * 10 ** ((a.lufs - lufs) / 20)
        mix = limiter(mix)
    lufs = meter.integrated_loudness(mix.astype(np.float64))
    pcm = (np.clip(mix, -1, 1) * 32767).astype('<i2')
    with wave.open(a.out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    if a.stems:
        for name, x in (('music', mus), ('sfx', sfx)):
            p = a.out.replace('.wav', f'_{name}.wav')
            x = x / (np.max(np.abs(x)) + 1e-9) * 0.8
            with wave.open(p, 'wb') as w:
                w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype('<i2').tobytes())
    print(json.dumps({'lufs': round(lufs, 1), 'peak': round(float(np.max(np.abs(mix))), 3), 'events': len(events), 'key_root': root}))


if __name__ == '__main__':
    main()
