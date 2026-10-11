#!/usr/bin/env python3
"""Spaja planove kamere po scenama (i ispravke iz provere) u jedan plan.

  python3 merge_plans.py segments.json film > plans/film.json

segments.json: {"film1": {"keyframes": [...]}, "film2": {...}, ...} redom po vremenu.
Na spoju dva dela (ista sekunda) važi vrednost dela koji tu počinje.
Rez tačno na kadru pomera se 0,01 s ranije, da zaokruživanje vremena ne pomeri skok za jedan kadar.
"""
import json, sys

segs = json.load(open(sys.argv[1]))
prefix = sys.argv[2]
keys = sorted((k for k in segs if k.startswith(prefix)), key=lambda k: int(k[len(prefix):]))
out = []
for k in keys:
    for x in segs[k]['keyframes']:
        kf = {f: x[f] for f in ('t', 'cx', 'wc', 'by', 'cut')}
        kf['t'] = round(kf['t'], 3)
        kf['src'] = k
        if kf['cut'] and kf['t'] > 0 and abs(kf['t'] * 30 - round(kf['t'] * 30)) < 0.02:
            kf['t'] = round(kf['t'] - 0.01, 3)
        prev = out[-1] if out else None
        if prev and abs(prev['t'] - kf['t']) < 0.02 and prev['src'] != k:
            kf['cut'] = kf['cut'] or prev['cut']
            out[-1] = kf          # na spoju važi deo koji tu počinje
            continue
        out.append(kf)
out.sort(key=lambda k: k['t'])
out[0]['cut'] = False
# Rez kojem odmah sledi tačka drugog dela sa drugom vrednošću (npr. 15.433 -> 15.5): rez preuzima tu vrednost
for a, b in zip(out, out[1:]):
    if a['cut'] and not b['cut'] and a['src'] != b['src'] and b['t'] - a['t'] < 0.2:
        a['cx'], a['wc'], a['by'] = b['cx'], b['wc'], b['by']
print(json.dumps({'note': 'Kamera za uspravnu verziju (vreme = kadar/30 s, px izvora 1920x1080), spojeno iz planova po scenama i njihovih provera.',
                  'keyframes': out}, indent=1, ensure_ascii=False))
