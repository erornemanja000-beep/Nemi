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
