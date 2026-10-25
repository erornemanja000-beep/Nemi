# DON'S Eisdiele: sajt i video (beleška o napretku)

Cilj: vrhunski "3D" sajt za DON'S Eisdiele (sladoled, roze-zelene boje) koji
sam pušta animaciju, kao maketa za buduće klijente.

## Koncept videa (redom)
1. **Ruža od sladoleda**: kugla na kornetu procveta u ružu (AI klipovi u MiniMax-u)
2. **Latica**: deo ruže se odlomi i odleti do lokala (Video C)
3. **Gradnja lokala**: zid → cigle → prozor → izlog → unutrašnjost → slova DON'S (gotovo, kodom)
4. Posle toga ide sam sajt (još nije počet)

Boje: puder roze `#F6DCDC`, prašnjava ruža `#E5B3B6`, pistaći `#CFE0C3`,
žalfija `#A9BFA2`, krem `#FFF8F1`, topla čokolada (tekst) `#4A3A35`.

## Gotovo
| Fajl | Šta je |
|---|---|
| `video/gradnja_lokala_zvuk.mp4` | gradnja lokala, 17 s, 1920×1080, sa zvučnim efektima (original) |
| `video/gradnja_lokala.mp4` | isto bez zvuka (original, za CapCut) |
| `video/gradnja_lokala_zvuk_web.mp4`, `video/gradnja_lokala_web.mp4` | iste verzije, 6 MB (za sajt i slanje) |
| `video/gradnja_lokala_1344x768.mp4` | veličina kao MiniMax klipovi |
| `video/gradnja_sfx.wav` | samo zvučni efekti |
| `video/gradnja_deo1.mp4`, `video/gradnja_deo2.mp4` | video podeljen na dva dela ispod 10 s (za AI programe) |
| `video/prompt_gradnja.md` | promptovi za AI program (ceo video i oba dela) + negativni prompt |
| `video/prompt_radnja1.md` | filmski prompt za RADNJA-1 (zid → prozor) sa pokretom kamere |
| `video/dons_natpis.mp4` | ranija verzija samo za slova DON'S |
| `frames/` | početni i završni kadrovi za AI klipove (16:9) |
| `assets/lokal/faza_1..5.png` | originalne slike lokala po fazama |

Prvi kadar gradnje je isti kao `frames/video_c_end_frame.png`, pa se Video C
seče direktno na gradnju.

### Vremena u videu gradnje (za sečenje)
- 0:00 zazidan prozor → 0:04 prozor gotov (faza 2)
- 0:08,4 izlog sa praznom vitrinom (faza 3)
- 0:12,7 pun lokal (faza 4)
- 0:13,2–0:14,2 padaju slova → 0:15,4 gotov lokal (faza 5)

## Kako se video pravi ponovo
```
python3 scripts/gradnja/render.py assets/lokal video/gradnja_lokala.mp4
python3 scripts/gradnja/sfx.py assets/lokal video/gradnja_sfx.wav
```
Scenario (šta pada, gde i kada) je u `scripts/gradnja/scenario.py`. Tu se menjaju
vremena, redosled i vrste pokreta.

## Sledeći koraci
- Spojiti AI klipove (ruža, latica) sa gradnjom u CapCut-u
- Po želji: uspravna 9:16 verzija za Instagram
- Napraviti sam sajt (video kao početna animacija, pa sekcije o ukusima, lokalu, kontaktu)

## Nemi Studio promo (10 s)
`video/nemi_studio_promo_10s.mp4`, 1920×1080, 30 fps, sa zvukom. Sve je kodom: lopta skače i otvara scenu,
slova NEMI. padaju sa oprugom, 3D kocka okreće „Websites / Videos / 3D & Motion", uređaji (browser i telefon)
uleću u 3D, pa završna kartica sa URL-om i konfetama.
```
node scripts/nemi_promo/render.js <folder_kadrova> 30 4
python3 scripts/nemi_promo/zvuk.py <zvuk.wav>
ffmpeg -framerate 30 -pattern_type glob -i '<folder_kadrova>/f*.jpg' -i <zvuk.wav> -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -shortest video/nemi_studio_promo_10s.mp4
```
Tekstovi i URL su u `scripts/nemi_promo/promo.html` (`URL_TEXT`). Pregled uživo: otvori `promo.html` u browseru.

## Nemi Studio promo u Blenderu (PAUZIRANO, nastavlja se kasnije)
Priča (19 s, 16:9): koralna tačka-ideja odskače u mraku („Alles beginnt mit einer Idee."), svaki odskok gradi
voxel bečku ulicu (zgrade, kafić CAFÉ, Riesenrad, tramvaj; „Wir geben ihr Form."), telefon u vazduhu
(„Websites. Videos. 3D."), sumrak i ljudi („Damit Wien dich sieht."), tačka postaje tačka u logu NEMI.
Scena je cela u kodu: `scripts/nemi_promo/blender/scena.py` (Blender 4.5 LTS, EEVEE).
```
xvfb-run -a blender -b --factory-startup -Y --offline-mode -P scripts/nemi_promo/blender/scena.py -- stills <folder> 2.4 9.8 17.6
xvfb-run -a blender -b --factory-startup -Y --offline-mode -P scripts/nemi_promo/blender/scena.py -- final <folder> 6 1 475 1600x900
```
Render u oblaku traje ~9 s po kadru (oko 70 min za ceo film). Ostalo: zvuk (sintetizovan ili Artlist numera)
i spajanje kadrova u MP4.
