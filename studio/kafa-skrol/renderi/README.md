# Rezervne kopije Blender rendera

Gotovi kadrovi iz `scripts/blender/kafa/` čuvaju se ovde kao WebP (q95, sa alfom), da se ne izgube ako se kontejner ugasi pre kraja rendera. Ne objavljuje se. Za sajt kadrove pakuje `mediji` (Z21) iz PNG originala, a ako PNG ne postoji, onda iz ovih kopija.

- `sip-1200/`: šolja (SIP), desktop 1200 px, kadrovi 1–64 (`sip.py --end 64 --res 1200`).
- `grind-1200/`: mlin (GRIND), 1200×1500, kadrovi G1–G96 (WebP q90), plus `anchors.json`.
- `pour-1200/`: prelivanje (POUR), 1200×1200, fajl L = G − 64 (G65–G192, WebP q90), plus `anchors.json`.
- `kese/`: tri kese (bags.py, 900×1125, WebP q95). Za sajt se seku na 750×900 i senka bledi od x 700 do 900 (vidi komandu u commit-u „real coffee bags").
