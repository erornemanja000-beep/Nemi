# Reference: nagrađeni sajtovi (poslednjih ~6 meseci)

Poslednja provera: 2026-10-27
Vodi: `trend-skaut`. Prvo punjenje baze. Težište: gastronomija i sladoledžinice (DON'S), pa hoteli (Freiraum), pa nekretnine (Vista Estates).

## Kako je proveravano i šta nije

- Otvorio sam Awwwards stranicu svakog sajta ispod (datum nagrade, ocene, tehnologije, opis) i, gde je moglo, sam sajt kao tekst. (2026-10, awwwards.com)
- **Pokret i telefon NISU viđeni.** Moj alat ne renderuje stranice ni JS. „Telefon" ispod je ocena „Responsive Design" iz Awwwards Developer Award-a (žiri, skala 1–10), plus ono što tekst sajta otkriva. Pre uzimanja bilo koje reference u dizajn: `tester`/`recenzent` je otvara na 390 px i 1440 px. Ocena žirija nije naša provera.
- Pokret je opisan samo koliko ga pokazuju Awwwards oznake i tekst sajta. Gde piše „oznaka", to je tvrdnja autora, ne merenje.
- Od referenci uzimamo princip, ne kopiju (tekst, logo, fotografije i brend ostaju njihovi).
- Datum nagrade piše tačno kako ga daje Awwwards. SOTD = Site of the Day, HM = Honorable Mention, SOTM = Site of the Month (po listi Awwwards).

## Pregled ocena (Awwwards Developer Award, 1–10)

| Sajt | Nagrada (datum) | SOTD ocena | Animacije | Responsive | Pristupačnost | WPO |
|---|---|---|---|---|---|---|
| Santioni Spirits | SOTD 2026-10-05 | 8.09 | 9.40 | 8.20 | 6.60 | 7.00 |
| Tengile Malamala Collection | SOTD 2026-10-03 | 7.22 | 7.40 | 7.60 | 7.40 | 7.60 |
| ERA Residence | SOTD 2026-08-31, SOTM 2026-08 | 7.61 | 8.00 | 7.00 | 7.20 | 7.00 |
| Son Daven | SOTD 2026-06-05, SOTM 2026-06 | 7.62 | 8.20 | **8.40** | 7.40 | 8.00 |
| Bucks Sauce | SOTD 2026-07-03 | 7.34 | 7.80 | 7.40 | 6.20 | 7.00 |
| Ciao Energy | SOTD 2026-07-30 | 7.22 | 8.00 | 7.20 | 7.00 | 7.80 |
| Lama Lama | SOTD 2026-07-20, SOTM 2026-07 | 7.51 | 7.80 | 7.20 | 6.60 | 7.60 |
| Realevate | SOTD 2026-09-27 | 7.22 | 7.60 | 7.40 | 6.60 | 7.40 |
| Délice | HM 2026-09-24 | nema | nema | nema | nema | nema |
| Sunbeam Bagels & Coffee | HM 2026-07-23 | nema | nema | nema | nema | nema |
| Agrumea Farm | HM 2026-10-01 | nema (zajednica: 8.5, 15 glasova) | nema | nema | nema | nema |

(2026-10, stranice sajtova na awwwards.com; SOTM po listi awwwards.com/websites/sites_of_the_month)

## 1. Gastronomija, kafići, sladoledžinice (težište: DON'S Eisdiele)

Napomena: na Awwwards-u nisam našao sladoledžinicu koja je u 2026. dobila SOTD. Pretraga je vratila samo starije ili neocenjene (Burrocacao Gelateria, NOPE, Gelato La Boca je Webby 2025). Zato niže stoje najbliži primeri: brendovi hrane i pića sa ličnošću. (2026-10, pretraga + awwwards.com/websites/food-drink)

### Santioni Spirits (piće, strip-iskustvo)
- Link: https://santionispirits.com/ · https://www.awwwards.com/sites/santioni-spirits
- Nagrada: SOTD **2026-10-05**, Business & Services Honors 2026-08, Developer Award; Active Theory + plan8. SOTD 8.09 (najviša u uzorku). (2026-10, awwwards.com)
- Šta je dobro: „immersive, comic book-inspired experience" oko „The Notturno Experience"; oznake: Illustration, Typography, Sound-Audio, Storytelling, Interaction Design, WebGL. Animacije 9.40 (najviše u uzorku). (2026-10, awwwards.com)
- Telefon: Responsive 8.20 (žiri). Naša provera: **nije urađena**. Pristupačnost samo 6.60.
- Princip za DON'S: priča kroz ilustrovane „panele" i lik, ne kroz katalog ukusa. Zvuk samo na zahtev.

### Bucks Sauce (sos, jaka ličnost)
- Link: https://buckssauce.com/ · https://www.awwwards.com/sites/bucks-sauce
- Nagrada: SOTD **2026-07-03**, E-commerce Honors 2026-06, Developer Award; Buzzworthy + Juraj Molnár. (2026-10, awwwards.com)
- Šta je dobro: tehnologije GSAP, Vercel, JS; oznake: Icons, Vertical Menu, Microinteractions, About Page, UI Design. Karakter brenda nose ikone i sitni pokreti, ne veliki 3D. (2026-10, awwwards.com)
- Telefon: Responsive 7.40 (žiri), pristupačnost 6.20 (najniža u uzorku). Naša provera: **nije urađena**. Pokušaj čitanja HTML-a sajta dao je samo ~34 KB sa `viewport` metom, bez ikakvih tragova biblioteka u HTML-u, pa iz toga ništa ne zaključujem. (2026-10, čitanje HTML-a bez čuvanja)
- Princip za DON'S: ikone ukusa i mikro-reakcije dodaju ličnost bez teškog WebGL-a.

### Ciao Energy, lansiranje (piće, 3D predmet + zvuk)
- Link: https://www.ciaoenergy.com/ · https://www.awwwards.com/sites/ciao-energy-launch-website
- Nagrada: SOTD **2026-07-30**, Developer Award; Skaald. (2026-10, awwwards.com)
- Šta je dobro: „immersive experience … centered on an interactive 3D object, sound design, and a minimalist identity"; Webflow, Three.js, Blender; oznake Infinite Scroll, Sound-Audio. Paleta `#EEEEEE`/`#191917`. (2026-10, awwwards.com)
- Telefon: Responsive 7.20, pristupačnost 7.00 (žiri). Naša provera: **nije urađena**.
- Princip za DON'S i Nemi reklamu: jedan 3D predmet iz Blender-a kao junak; isti workflow (Blender → web) kao voksel/Blender u reklami.

### Sunbeam Bagels & Coffee (kafić, pekara)
- Link: https://sunbeambagels.com/ · https://www.awwwards.com/sites/sunbeam-bagels-coffee
- Nagrada: HM **2026-07-23**; Drifting Creatives. (2026-10, awwwards.com)
- Šta je dobro: slogan „A website designed to surprise"; Webflow + Figma; oznake 3D, Music & Sound, Footer Design, Navigation Menu. Developer ocena na stranici ne postoji. (2026-10, awwwards.com)
- Telefon: **NEPROVERENO** (nema ocene, nije renderovano).
- Princip: kafić može da bude „iznenađenje" kroz zvuk, 3D i podnožje stranice, a ostane Webflow (jeftina izrada).

### Délice, Pizza Délice u Lévisu (lokalni restoran)
- Link: https://delice.ca/ · https://www.awwwards.com/sites/delice
- Nagrada: HM **2026-09-24**; Monument. (2026-10, awwwards.com)
- Šta je dobro: porodični lokal od 1970, sajt cilja na „warmth, sophistication, and a welcoming atmosphere". WordPress + GSAP + Sass; oznake Photo & Video, Microinteractions, Transitions, Responsive; elementi: Menu, Promotions, Hero. Paleta `#DE2B2B` crvena + `#F5DBCA` breskva. (2026-10, awwwards.com)
- Telefon: oznaka „Responsive", ocena žirija ne postoji. **NEPROVERENO**.
- Princip: najbliže budžetu lokalnog klijenta (WordPress, topla paleta, meni i akcije).

### Agrumea Farm (proizvođač hrane, Sicilija)
- Link: https://www.agrumeafarm.it/en · https://www.awwwards.com/sites/agrumea-farm
- Nagrada: HM **2026-10-01**; Studio K95. Prema sažetku pretrage i WOTD na CSS Design Awards 2026-10-06: **NEPROVERENO** (nisam otvorio cssdesignawards.com direktno). (2026-10, awwwards.com; pretraga)
- Šta je dobro: „immersive web journey" kroz sicilijansku baštinu; Three.js, Nuxt, GSAP, Lenis (smooth scroll); 3D, Header Design, Navigation Menu, Typography. Paleta `#762530` + `#E94E1B`. Zajednica: prosek 8.5 (15 glasova). (2026-10, awwwards.com)
- Telefon: **NEPROVERENO**.
- Princip: kombinacija Lenis + GSAP + Three.js (isti stack kao RealEstates) u hrani.

### Neotvoreno, samo sa liste (provera kasnije)
Flora Café (HM 2026-07-17, Hello-World), Matcha Cartel (HM 2026-06-28, Surd Studio), Pizza Amici (HM 2026-07-05), Caffè Gilli (HM 2026-08-04, thebrandingcrew), Burrito Madre (HM 2026-07-09), La table de Joakim (HM 2026-08-13), Ballena Fine Dining (HM 2026-06-17). (2026-10, awwwards.com/websites/food-drink, strana 1–2)

## 2. Hoteli i smeštaj (Freiraum)

### Son Daven (hotel/aparthotel u Karpatima)
- Link: https://sondaven.com/en · https://www.awwwards.com/sites/son-daven
- Nagrada: SOTD **2026-06-05**, po listi Awwwards SOTM 2026-06; The First The Last (Maksym Stepenko, Ivan Chopei). SOTD 7.62, Developer 8.09. (2026-10, awwwards.com)
- Šta je dobro: Webflow + GSAP + WebGL; oznake Animation, Scrolling, Storytelling, Microinteractions. Struktura iz teksta: loader, hero sa dva broja, lokacija sa mapom i minutima peške, harmonika sa prednostima, kartice šest tipova jedinica sa galerijom i videom, vremenska linija izgradnje, FAQ (8 pitanja), forma za upit. (2026-10, sondaven.com)
- Telefon: **Responsive 8.40 (najviši u uzorku)**, pristupačnost 7.40. Naša provera: **nije urađena**.
- Oprez: sajt prodaje investicione jedinice, ne rezervacije; tekst nudi „Rotate your phone for better experience" (prisiljava pejzaž, protivi se našem pravilu 390 px); jedna kartica pokazuje „0 UAH per m²" (greška u sadržaju). (2026-10, sondaven.com)
- Princip za Freiraum: kartice tipova sa galerijom i FAQ, mapa sa vremenima peške.

### Tengile Malamala Collection (safari lodge)
- Link: https://tengilemalamala.com/ · https://www.awwwards.com/sites/tengile-malamala-collection
- Nagrada: SOTD **2026-10-03**, Developer Award; DashDigital + Ingamana. (2026-10, awwwards.com)
- Šta je dobro: „quiet luxury through cinematic storytelling"; React + Sanity (CMS) + AWS; oznake Big Background Images, Menu - Horizontal, Photo & Video, Microinteractions. (2026-10, awwwards.com)
- Telefon: Responsive 7.60, **pristupačnost 7.40 (među najboljima u uzorku)**. Naša provera: **nije urađena**.
- Princip: mirni veliki kadrovi i horizontalni meni; sa CMS-om (Sanity) kao što Freiraum traži izmenu sadržaja.

### Neotvoreno, samo sa liste (provera kasnije)
White Desert (SOTD 2026-09-11, Malvah), Villa Aurelia (HM 2026-09-25, MadeByCat), Velaa Private Island (HM 2026-09-25, STRV), Masia Mont Rural (HM 2026-09-21, emblematica), Faith Ibiza (HM 2026-09-01, Yellowball), Vander Hotel (HM 2026-08-29, .RAW), KUBE Saint-Tropez (HM 2026-08-27, Digidop), Tandjung Sari (HM 2026-08-05, Fleava). CSS Design Awards: Terreno Barrio Hotel (Special Kudos 2026-10-13), po sažetku pretrage, **NEPROVERENO**. (2026-10, awwwards.com/websites/hotel-restaurant)

## 3. Nekretnine (Vista Estates)

### ERA Residence (butik rezidencije, Estepona)
- Link: https://www.era-residence.com/ · https://www.awwwards.com/sites/era-residence
- Nagrada: SOTD **2026-08-31**, SOTM 2026-08 (po listi), Developer Award; The First The Last. SOTD 7.61. (2026-10, awwwards.com)
- Šta je dobro: Webflow + GSAP; oznake Parallax, Storytelling, Photo & Video. Iz teksta: hero „A place to return to" sa prekidačem **dan/noć** (dve slike), tri numerisana razloga, **prevlačiva glavna skica** („Drag to see more"), kartice tipova stanova sa „Explore" na filtrirane oglase, dugme „Book a call", **modal za upit sa obećanjem odgovora u roku od jednog radnog dana**, status gradnje. (2026-10, era-residence.com)
- Telefon: Responsive 7.00 (žiri, najniže među hotelima/nekretninama), pristupačnost 7.20. Naša provera: **nije urađena**.
- Princip za Vista Estates: prekidač dan/noć, plan koji se prevlači, jasan modal za upit. U tekstu stoji dvostruka kvadratura (104–244 m² i 97–243 m²), znak nepažnje u sadržaju.

### Realevate (agencija za investitore)
- Link: https://realevate.agency/ · https://www.awwwards.com/sites/realevate
- Nagrada: SOTD **2026-09-27**, Developer Award; Or Halevi. SOTD 7.22, usability samo 6.88. (2026-10, awwwards.com)
- Šta je dobro: GSAP, JS, Node.js; oznake Fullscreen, Horizontal Menu, Microinteractions; paleta `#1F2B5E` + `#FFFFFF`. (2026-10, awwwards.com)
- Telefon: Responsive 7.40, pristupačnost 6.60. Naša provera: **nije urađena**.
- Oprez: niska upotrebljivost; uzeti stil, ne tok.

### Neotvoreno, samo sa liste (provera kasnije)
Belgrade Arbor (SOTD 2026-10-17, Square43 Studio), Sobha Privy Collection (SOTD 2026-09-23, Vide Infra; CSSDA WOTD 2026-10-05 po sažetku pretrage, **NEPROVERENO**), Kononenko Architectural Bureau (SOTD 2026-08-23), LIKOVA (SOTD 2026-08-19, Vide Infra), Quinta D. Amália (HM 2026-09-16), Loam House (HM 2026-09-24). (2026-10, awwwards.com/websites/real-estate)

## 4. Agencije i studiji (Nemi Studio, nemistudio.at)

### Lama Lama (digitalna agencija)
- Link: https://lamalama.com/ · https://www.awwwards.com/sites/lama-lama-2
- Nagrada: SOTD **2026-07-20**, SOTM 2026-07 (po listi), Developer Award. (2026-10, awwwards.com)
- Šta je dobro: GSAP, JS, WebGL; paleta `#F9F4EB` + `#1A1C1C`, vrlo blizu Nemi paleti (bone `#efeae2`, ink `#0b0b0c`). (2026-10, awwwards.com)
- Telefon: Responsive 7.20, pristupačnost 6.60. Naša provera: **nije urađena**.
- Princip: topla krem + skoro crna je ozbiljna paleta za agenciju u 2026.

### Butter (video editor, proizvod)
- Link: https://www.butter.video/ · https://www.awwwards.com/sites/butter
- Nagrada: SOTD **2026-09-28**, Developer Award; ToyFight. SOTD 7.5. WebGL, React, P5.js. Animacije 8.20, responsive 7.20, pristupačnost 6.60. (2026-10, awwwards.com)
- Princip: igra sa „alatom na sajtu" kao demo. Nije naša branša.

## 5. Zapažanje o samoj listi

Od 31 sajta „Site of the Day" u poslednjih mesec dana (2026-09-27 do 2026-10-27), bar 4 su iz naših branši (po kategorijama Awwwards-a; ostale nisam razvrstavao): Belgrade Arbor (nekretnine), Santioni Spirits (piće), Tengile Malamala (hotel), Realevate (nekretnine). Većinu čine portfolia, automobilski, agencijski i tehnološki sajtovi. Nagrade se dobijaju više za eksperiment nego za ugostiteljstvo. (2026-10, awwwards.com/websites/sites_of_the_day)

## Arhiva

(prazno, prvo punjenje)
