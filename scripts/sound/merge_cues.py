#!/usr/bin/env python3
"""Spaja tabele zvučnih efekata po delovima filma u jednu (bez duplikata na spojevima).

  python3 merge_cues.py seg1.json seg2.json ... > cues.json
"""
import json, sys

events = []
for p in sys.argv[1:]:
    events += json.load(open(p))['events']
events.sort(key=lambda e: e['t'])
out = []
for e in events:
    dup = next((o for o in out[-12:] if o['type'] == e['type'] and abs(o['t'] - e['t']) < 0.1), None)
    if dup:
        dup['intensity'] = max(dup['intensity'], e['intensity'])
        dup['dur'] = max(dup['dur'], e['dur'])
        continue
    out.append({k: e[k] for k in ('t', 'dur', 'type', 'intensity', 'pan', 'pitch', 'what')})
print(json.dumps({'events': out}, indent=1, ensure_ascii=False))
