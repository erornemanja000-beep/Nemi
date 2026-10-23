# Etiketa za kese (Z4): KORN / KANNE · kafa-skrol

> 23.10.2026: ime je promenjeno iz POUR / PLAY (brend iz referentnog videa) u izmišljeno KORN / KANNE. Sada je drugi red širi, pa skript ime podešava po širem redu. Mere u tabeli ispod važe za staro ime.

Dizajner, 23.10.2026. Ovo je predaja za `blender-umetnik` preko direktora. Zadatak je Z4 iz `plan-izrade.md`: jedna etiketa u tri boje za `scripts/blender/kafa/bags.py`.

Fajlovi u ovom folderu:
- `etiketa.html`: izvor. Boja se bira sa `?v=origin|flavor|roast`, a sa `&guides=1` se vide zaštićene zone (te zone ne ulaze u PNG).
- `etiketa-origin.png`, `etiketa-flavor.png`, `etiketa-roast.png`: 2048 × 3072 px, RGBA (alfa je svuda 255), oko 155 KB svaki. Izvezeni Chromium-om preko Playwright-a i pregledani.

---

## 1. Šta je na etiketi

Raspored je isti za sve tri kese, a menjaju se samo boje.

| Element | Font | Veličina u PNG-u | Na kesi | Položaj (px, od gornjeg levog ugla) |
|---|---|---|---|---|
| **POUR /** i **PLAY** (dva reda) | Archivo 800, `wdth` 88, verzal, −0,01em | 548 px, verzal 376 px | 22,0 mm | x 171, y 1372–2293; prvi red je tačno širine sigurne zone (1706 px) |
| SPECIALTY COFFEE · WIEN | Figtree 700, verzal, razmak 0,2em | 100 px, verzal 72 px | 4,2 mm | x 171, y 2322; iste širine kao ime |
| 250 g (sa nelomljivim razmakom) | Archivo 800, `wdth` 88 | 236 px, cifre 167 px | 9,8 mm | x 171, y 2660 |
| DEMO (pilula sa obrisom) | Figtree 700, verzal, 0,16em | 76 px, verzal 55 px | 3,2 mm | desno do x 1877, y 2708–2844 |
| talas kafe | SVG | ivica oko y 1210 ±55 | | od ivice do dna, preko cele širine |
| tamna linija i odsjaji na ivici | SVG | linija 18 px, odsjaji 22 px | | kao `Wave` na sajtu (storyboard 5) |
| zvezdica | SVG (ista kao favicon i Sparkle) | 180 px | 10,5 mm | centar (1702, 986), na papiru |

Svesno izostavljeno (plan Z4):
- ime kafe, cena, Bio, Fairtrade i drugi sertifikati;
- datum prženja i MHD. Šest kafa deli tri kese po boji, pa kesa ne sme da nosi podatke jedne kafe.

Zato otpada i ono što storyboard 6 traži po kesi (region, čipovi sa notama, skala prženja). Kese se razlikuju samo bojom.

Znak **℮** je namerno izostavljen. On znači da pakovač garantuje punjenje, a ovde je pakovač izmišljen.

**Visina cifara „250 g"** je 9,8 mm. Direktiva 76/211/EEZ, Prilog I, tačka 3.1 (izmena 78/891/EEZ) traži najmanje 4 mm za količine iznad 200 g do 1000 g.
- Pročitano 23.10.2026 na [legislation.gov.uk](https://www.legislation.gov.uk/eudr/1976/211/annex/I) (UK verzija direktive).
- [EUR-Lex konsolidovani tekst](https://eur-lex.europa.eu/eli/dir/1976/211/2019-07-26) se nije učitao, pa je EU tekst **NEPROVERENO**.
- Pravilo LMIV o x-visini od najmanje 1,2 mm (Uredba (EU) 1169/2011, čl. 13) je iz znanja, u ovom prolazu **NEPROVERENO**. Najmanji tekst (DEMO) ima verzal od 3,2 mm.

### Gde se pojavljuje ime brenda
- **Samo na jednom mestu:** `etiketa.html`, element `<h1 class="brand" data-brand>`, sa dva `<span>` („Pour /" i „Play"). Veličina se sama podešava tako da prvi red popuni širinu od 1706 px.
- **Ako se ime promeni:**
  1. izmeniti ta dva reda (deli se na mestu gde ime ima prirodan prelom);
  2. pogledati `&guides=1`, jer drugi red ne sme biti širi od prvog;
  3. ponovo izvesti tri PNG-a (odeljak 5);
  4. ponovo renderovati kese u Blenderu (~20 min za sve tri, storyboard 6, PROCENA).
- Podnaslov „Specialty Coffee · Wien" nije ime brenda i ostaje.

---

## 2. Mapa na model iz `bags.py`

Platno je prednja strana kese, **120 × 180 mm**, sa **17,0667 px/mm**.

| | Vrednost |
|---|---|
| U | `u = (x + 0,060) / 0,120` (x u metrima, Object koordinate kao u `mat_bag`) |
| V | `v = (z − 0,010) / 0,180`, gde v = 0 znači dno slike. Etiketa pokriva z 10–190 mm. |
| piksel → model | `x_mm = px / 17,0667 − 60`, `z_mm = 190 − py / 17,0667` |
| Image Texture | Color Space **sRGB**, Interpolation Cubic, **Extension EXTEND** |
| maska | postojeća `front` iz `mat_bag` (štampa samo spreda, ispod vara) |
| zakrivljenost | ispupčenje od 6,5 mm na polovini širine od 60 mm daje istezanje manje od 1 %, pa ispravka nije potrebna |

**Zašto EXTEND:**
- ispod z 10 mm (zaobljeno dno) nastavlja se boja talasa iz poslednjeg reda slike;
- iznad z 190 mm nastavlja se papir.

Bez toga se na dnu kese pojavi traka u boji papira (videlo se na probi).

### Zone

| Zona | Na modelu | U PNG-u | Šta je tu |
|---|---|---|---|
| var i zipper | z 169–190 mm (zipper `ZIP_Z` = 179 i 175,8 mm) | y 0–358 | samo papir. Grebeni zippera su na y ≈ 188 i 242 |
| **ventil** Ø 16 mm | centar x 0, z 158 mm | centar (1024, 546), r 137 | prazno. Zona Ø 24 mm (r 205, y 341–751) bez ikakvog crteža |
| bokovi i zaobljeni uglovi | spoljnih 10 mm levo i desno | x < 171 i x > 1877 | samo boja (papir ili talas), bez teksta |
| dno | z 10–18 mm | y > 2935 | samo boja talasa |
| sigurna zona za tekst | x ±50 mm, z 18–143 mm | x 171–1877, y 800–2935 | ceo tekst (provereno sa `&guides=1`) |

**Ventil** u `bags.py` još ne postoji. Predlog je okrugao plastični ventil Ø 16 mm na mestu iz tabele: ispupčen ~1 mm, beo ili papirne boje, sa sitnim rupicama u sredini.

### Ostatak kese u Blenderu
- **Bokovi, leđa i var:** boja `paper` iz tabele u odeljku 3. Var se već sam zatamni za 12 % u `mat_bag`.
- **Postojeće proceduralne šare** (pravougaonik, pruge, mrlje i luk) zamenjuje ova tekstura.
- Ako talas treba da se nastavi oko boka, za bokove se uzima ista slika sa `u = 0` i istim `v`. To je opcija, nije obavezno.

---

## 3. Boje

Uzete su iz `bags.py` (`DESIGNS`) i storyboard-a 6 (origin terakota/glina, flavor tirkiz/žalfija, roast roze/krem). Usklađene su sa `tokens.css`: sav tekst je u bojama tokena, a promenjeni su samo tonovi koji nisu davali kontrast.

| Uloga | origin | flavor | roast |
|---|---|---|---|
| `paper` (papir kese = `base` u `bags.py`) | `#EEE5D5` (bilo `#E8DDCB`) | `#E6D6BF` (isto) | `#EDB8A0` (isto) |
| `field` (talas) | `#AD4731` (bilo `label` `#C4513C`) | `#3A9A96` (bilo `teal` `#2B9AA2`) | `#D8826A` (`blob`, isto) |
| `meniscus` (tamna linija ivice) | `#86321F` (bilo `label_dark` `#963629`) | `#1E5C86` (`blue`, isto) | `#B25A45` (bilo `line` `#C46C56`) |
| `glint` (odsjaji) | `#F7E6C6` = `--pp-crema` | `#8FCBC6` (`mint`, isto) | `#F6ECE4` (`arc`, isto) |
| zvezdica | `#AD4731` | `#1E5C86` | `#9A4734` |
| tekst | `#F4EEE4` = `--pp-cream-light` | `#1B150D` = `--pp-ink-deep` | `#1B150D` = `--pp-ink-deep` |

**Zašto ove promene:**
- **Origin `#C4513C` → `#AD4731`.** Krem tekst na staroj boji ima 3,99:1, pa ne prolazi. Nova boja je između korala iz videa i terakote brenda `#915439`.
- **Origin papir `#E8DDCB` → `#EEE5D5`.** Stari papir je skoro ista boja kao pozadina prodavnice `#E6DDCE`. Novi je bliži `--pp-paper`. Razlika je i dalje mala (1,08:1), a kesu odvajaju senka i crveni talas.
- **Flavor `#2B9AA2` → `#3A9A96`.** Malo ka žalfiji, da se slaže sa braon paletom. Kontrast teksta ostaje isti (5,39 → 5,38).
- **Tamne linije** su malo tamnije, da se ivica talasa vidi. One su ukras.
- **Zvezdica na roast** je tamnija (`#9A4734`), jer se na breskvi slabo videla (2,69 → 3,60).

### Kontrast (WCAG 2.x, izračunato skriptom 23.10.2026)

| Par | Odnos | Prag | Prolazi |
|---|---|---|---|
| origin: tekst `#F4EEE4` / `#AD4731` | **4,89** | 4,5 (važi i za sitan tekst) | da |
| flavor: tekst `#1B150D` / `#3A9A96` | **5,38** | 4,5 | da |
| roast: tekst `#1B150D` / `#D8826A` | **6,31** | 4,5 | da |
| zvezdica / papir: origin, flavor, roast | 4,51 / 5,03 / 3,60 | 3 (grafika) | da |
| tamna linija / papir: origin, flavor, roast | 6,75 / 5,03 / 2,69 | ukras | – |
| talas / staklena kartica (≈ `#D6C3B8`): origin, flavor, roast | 3,32 / 1,98 / 1,69 | – | ukras, kesu odvajaju oblik i senka |
| talas / prodavnica `#E6DDCE`: origin, flavor, roast | 4,19 / 2,50 / 2,13 | – | ukras |

Na papiru nema teksta. Svaki tekst stoji na talasu, a veličina naslova nije korišćena kao izgovor za niži prag.

---

## 4. Da li se čita kad se umanji (pregledano sa Read)

Napravljena su dva pregleda (privremeni, nisu u repou):
- etiketa uklopljena u 400 × 500 (333 × 500 px);
- gruba kesa u kadru kao kod `blender-umetnik`. Kesa zauzima ~69 % visine kadra 1200 × 1500 sa 85 mm (storyboard 6), umanjeno na 400 × 500 i 600 × 750.

| Tekst | kesa 400 × 500 (telefon) | kesa 600 × 750 (kartica) | etiketa u 400 × 500 |
|---|---|---|---|
| POUR / PLAY (verzal) | 35 px, čita se | 53 px | 61 px |
| 250 g (cifre) | 16 px, čita se | 23 px | 27 px |
| SPECIALTY COFFEE · WIEN | 6,7 px, čita se uz razmak slova | 10 px | 12 px |
| DEMO | 5 px, razaznaje se | 7,7 px, čita se | 9 px |

Napomena za `recenzent`: u `mockup.html` kutija kese u staklenoj kartici je visoka 132 px (desktop) i 88 px (telefon). Na toj veličini se čita samo ime, kao i u referentnom videu. Sitni redovi se čitaju u prodavnici (900 × 1125) i u modalu.

---

## 5. Izvoz (ponovljiv)

**Fontovi.** Samo lokalni, bez CDN-a:
- Archivo je iz `KafaSkrol/node_modules/@fontsource-variable/archivo/files/archivo-latin-wdth-normal.woff2` (paket 5.3.0, OFL-1.1). Isti je bajt po bajt kao provereni paket. Zato prvo `cd KafaSkrol && npm install --ignore-scripts`.
- Figtree je iz `sajt/src/assets/fonts/`.
- Fraunces nije korišćen. Etiketa je namerno u dva fonta.
- Osa `wdth` je izmerena u Chromium-u: „GRIND" na 88 ima 0,894 širine na 100. Osa radi, pa je NEPROVERENO iz `dizajn.md` odeljak 4 rešeno.

**Koraci:**
1. Server iz korena repoa (`file://` blokira fontove): `python3 -I -m http.server 8765 --bind 127.0.0.1 --directory <repo>`.
2. Playwright (`KafaSkrol/node_modules/playwright`) otvara `http://127.0.0.1:8765/studio/kafa-skrol/dizajn/etiketa.html?v=<boja>`:
   - viewport 2048 × 3072, `deviceScaleFactor: 1`;
   - čeka `#label[data-ready]`, koji mora biti `ok`. Ako fontovi ne stignu, vrednost je `font-error` i preko cele etikete stoji crveno upozorenje;
   - `page.screenshot({ omitBackground: true, clip: {x:0, y:0, width:2048, height:3072} })`;
   - svaki zahtev van `127.0.0.1` se prekida. Na ovoj probi ih je bilo 0, kao i grešaka u konzoli.
3. **Chromium:** Playwright 1.64.1 očekuje build 1248, a na mašini je 1194. Zato `chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' })`. Ništa nije preuzimano.
4. Chromium daje RGB PNG, pa se dodaje alfa (bez gubitka): `Image.open(p).convert('RGBA').save(p, optimize=True)` (sistemski Pillow 12.3).

**sha256 (23.10.2026):**
- origin `13266feb…af68`
- flavor `a0dbda95…63dd`
- roast `1e78f7e4…c5b6`

---

## 6. Istraživanje, savremeno i izbegnuto

**Polazište:**
- `studio/znanje/trendovi.md` i `reference.md` su od 23.10.2026, pa nisu ponovo istraživani.
- Nagrađeni sajtovi kafe (CoffeeTech, NewmixCoffee, Apocalypse) obrađeni su danas u `dizajn.md`.
- Curated za njih nema design.md (`search_sites` „specialty coffee roaster packaging" ponovo vraća samo Coffee Collective bez design.md).
- Nijedna stranica nije tražila radnju od agenta.

**Savremeno (mišljenje, uz trag iz baze):**
- **Paleta stranice i pakovanja kao jedan sistem** (`trendovi.md` T9). Talas na kesi je isti oblik kao prelaz POUR → SIP (zbir dve sinusoide, tamna linija, odsjaji), a zvezdica je ista kao na sajtu.
- **Krupna tipografija kao glavni crtež.** Ime je preko cele širine, u istom rezu kao naslovi poglavlja (Archivo `wdth` 88). Krupni grotesk je jedna od dve struje u `trendovi.md` (CoffeeTech, SŌM, More Nutrition).
- **Ravne površine boje** umesto ilustracije, pa se na 400 px kese razlikuju po boji, a ime ostaje čitljivo.

**Svesno izbegnuto kao izlizano (mišljenje):**
- kraft papir sa pečatom, crno-zlatna „premium" kombinacija;
- ikona zrna, rukopisni font, trake i značke „artisan / small batch";
- lažni pečati kvaliteta;
- tekst iz AI generatora (storyboard 6: „Nikad AI tekst").

**Od reference** (kadar 213 iz videa) uzeti su samo:
- stojeća kesa;
- svetao papir gore i velika obojena površina dole;
- tri boje.

Ne uzimaju se njihove etikete, natpisi „ORIGIN/FLAVOR/ROAST" ni oblici.

**Pokret:** etiketa nema pokret. Talas na kesi je statičan crtež, pa mirna verzija za `prefers-reduced-motion` nije potrebna. Kese na kartici pokreće kod (Z7), a ta mirna verzija je u `dizajn.md` odeljak 6.
