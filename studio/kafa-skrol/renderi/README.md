# Rezervne kopije Blender rendera

Gotovi kadrovi iz `scripts/blender/kafa/` čuvaju se ovde kao WebP (q95, sa alfom), da se ne izgube ako se kontejner ugasi pre kraja rendera. Ne objavljuje se. Za sajt kadrove pakuje `mediji` (Z21) iz PNG originala, a ako PNG ne postoji, onda iz ovih kopija.

- `sip-1200/`: šolja (SIP), desktop 1200 px, kadrovi 1–64 (`sip.py --end 64 --res 1200`).
