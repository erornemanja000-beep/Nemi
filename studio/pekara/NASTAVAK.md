# Krume: gde smo stali (za nastavak)

Poslednje ažuriranje: 28. 10. 2026, ujutru (krug 3 peći gotov). Komanda za nastavak u terminalu: **NASTAVAK.PEKARA**

## Ukratko
Krume (`pekara/`) je koncept-sajt bečke pekare: noć u kvartu od 04:00 do 07:00 na skrol.
- **Commit `c2b2d78`:** gotova je verzija u Three.js-u (Vite + GSAP + Lenis, Blender bake). Prošla je tester, recenzent i bezbednost i radi na `npm run dev` / `vite preview`.
- **Novi smer (korisnik, 27. 10.):** fotorealistično. Sajt prelazi na **sekvencu slika renderovanu u Blender Cycles-u, koja se vrti na skrol** (canvas, kao Apple sajtovi). Three.js izlazi.
- **Trenutna faza:** **proba izgleda, krug 3** (pre punog rendera).

## Odluke korisnika (upisane i u `studio/pekara/dizajn/dizajn.md`)
1. Smer je Cycles sekvenca (ne AI video, ne doterivanje three).
2. Prave PBR teksture i HDRI sa Poly Haven-a (CC0). `bezbednost` ih je pregledao, MD5 je proveren, izvori su u `studio/pekara/blender/teksture/QUELLEN.md`. Fajlovi nisu u git-u; ponovo se preuzimaju komandom iz QUELLEN.md.
3. Rez kriške (poglavlje 3) je **pravi zid** (cigla, malter, tavanica sa gredama), ne mrvica hleba.
4. „Dreh das Grätzl" postaje **lažna dubina** (pomeranje slike za mišem ili nagibom telefona). Hint u `studio/pekara/tekstovi.md` treba promeniti ili ukloniti (`tekstopisac`).
5. Zvuka nema (ranija odluka).

## Otvoreno pitanje za korisnika
Rok i brzina rendera. Predlog direktora je **1 + 3**: oko 200 kadrova po obliku umesto 310 i manje uzoraka u daljim kadrovima, što daje oko 20 h rendera i sve gotovo za 3–4 dana. Korisnik još nije odgovorio.

## Probni kadrovi (`studio/pekara/blender/proba-foto/`)
| Fajl | Šta | Stanje |
|---|---|---|
| `1-wide.png`, `1-hoch.png` | grad u 04:00, krug 2 (teksture) | dobro: mokra kaldrma, prednje kuće, svetlije |
| `3-wide.png`, `3-hoch.png` | presek sa izvučenom kriškom, krug 3 | dobro, ali vidi popravke |
| `4-ofen-wide.png` | peć, krug 3 | dobro: cepana drva kao prava, niša sa dubinom, izmaglica brašna i prašina. Slabo: snopovi sa prugama nisu uspeli (kamera je u osi otvora), „šator" cepanica u komori je prosvetao, dve kose cepanice desno su neprirodne, vrh vrata je svetao |
| `krug1/`, `krug2/` | stari krugovi za poređenje | |

**Popravke za sledeći mali krug** (posle kruga 3 peći):
- izlog spolja (kadar 3) je hladan, beo i prazan; treba topao i pun hleba;
- tavanica i zidovi u preseku su velike ravne bele površine; treba više detalja i toplije;
- prazna tabla iznad vrata;
- foto materijali enterijera (`foto_sloj()`, `M_FOTO`, UV `foto_uv` u `enterijer.py`) postoje samo za kadar „ofen". Treba ih sačuvati u `enterijer.blend`, da ih koristi `kadrovi.py -- foto`, i ponovo napraviti `enterijer.blend` posle novog `kuca_kit.blend`;
- peć: potamneti „šator" cepanica u komori (ugljenisano, jače tinjanje), ukloniti dve kose cepanice desno, prigušiti vrh vrata. Snopovi: svetlo visoko pod svodom i ivica ili rešetka pod uglom, ili light group u kompozitu (kamera se ne pomera).

## Kako se renderuje (važno)
- **Uvek preko** `studio/pekara/blender/render_red.sh <argumenti za Blender>`. Skripta ima zajedničku bravu (`/tmp/krume-render.lock`), pa radi samo jedan Blender odjednom (dva istovremena su rušila Blender), i `caffeinate` (Mac ne zaspi).
- **Samo Metal GPU.** CPU uz GPU je na M1 usporavao do 20×; ispravljeno u svim skriptama.
- **Mac na punjaču, poklopac otvoren.** Na bateriji sa zatvorenim poklopcem Mac zaspi i `caffeinate` to ne sprečava: noću 27./28. 10. peć od ~5 min je trajala 4,6 h, a kadar 3 od 9 min 1 h.
- **Primeri:**
  - grad: `kvart.py` gradi `kvart.blend`; render kadra 1 je bio skripta Z1 u scratchpad-u (`render2.py`);
  - presek i ostali kadrovi: `./render_red.sh -b -P kadrovi.py -- foto 3` (wide 1600×1000 i hoch 720×1440 u `proba-foto/`);
  - peć: `./render_red.sh -b -P enterijer.py -- ofen` (env `KRUME_*` opisane u zaglavlju `enterijer.py`);
  - stari statični kadrovi za sajt: `kadrovi.py` bez `foto`, pa `-- webp`.
- **Izmerena vremena (bez spavanja):** kadar 1 wide 103 s / hoch 128 s; kadar 3 wide 540 s / hoch 416 s; peć 330 s. Mem peak je do ~5,4 GB na 8 GB.

## Plan posle probe (planer, 27. 10.)
- **Talas 2** (paralelno):
  - `sekvenca.py` + `koreografija.py` (Python prepis `timeline.js apply(u)`; kamera iz `pekara/public/data/kamera.json` po pravilima iz `src/motion/camera.js`; izvoz 2D tačaka hlebova po kadru u `public/data/sekvenca.json`) → programer;
  - `src/seq/player.js` (canvas, cover-fit, pretapanje, tačke na bus `labels`) → animator;
  - `src/seq/loader.js` (po poglavljima, prvo svaki 4. kadar, prozor dekodiranih bitmapa) → programer.
- **Talas 3:**
  - pun render po poglavljima, sa nastavkom posle prekida (`pekara/public/seq/<oblik>/NNNN.webp`) → mediji;
  - uklanjanje three (`src/scene/*`, `camera.js`, `public/models|textures`) → programer;
  - UI: etikete, lažna dubina, Klopf → programer.
- **Talas 4:** tester, recenzent, bezbednost, pa commit.
- **Ciljevi:** WebP ~70 KB desktop / ~40 KB telefon po kadru; ukupno ≤ 22 / 12 MB; prvi ekran ≤ 2,5 / 1,5 MB. Reduced-motion = statični kadrovi kao sada.
- **Otvoreno:** da li `pekara/public/seq/` ide u git (~35 MB po renderu u istoriji).

## Sitnice
- `ffmpeg` nije na PATH-u (CLAUDE.md kaže da postoji). Za sada ne treba, jer WebP pravi Blender.
- Statični režim na 390 px: naslov „In der Backstube" je slabog kontrasta na svetlom delu slike (tester, 27. 10.). Proveriti posle novih kadrova.
