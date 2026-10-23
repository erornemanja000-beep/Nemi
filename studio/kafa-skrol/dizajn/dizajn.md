# Dizajn: POUR / PLAY · Specialty Coffee (kafa-skrol)

Dizajner, 23.10.2026. Zadatak je isti izgled, boje i raspored kao u referentnom videu (test tima). Ime brenda je privremeno, a pozadinske reči („Longberry", „Pourover", „Frother") i nemački tekstovi važe dok ih tekstopisac ne potvrdi.

Fajlovi u ovom folderu:
- `tokens.css`: paleta po ulogama, tipografija, razmaci, zaobljenja, senke, pokret i mirna verzija.
- `mockup.html`: header i prvi ekran poglavlja GRIND, POUR i SIP, sa najavom prodavnice.
- `mockup-1440.png` (1440 × 2858) i `mockup-390.png` (390 × 2768 pri DPR 2): snimci Playwright-om, pregledani.

Polazište su `analiza-videa.md`, nalaz o kontrastu iz `brief.md` i kadrovi videa. Kadrovi su lokalni i nisu u repou.

---

## 1. Istraživanje

**Baza znanja.** Fajlovi `studio/znanje/trendovi.md` i `reference.md` ne postoje (stanje 23.10.2026, u folderu je samo `README.md`). Zato sam istraživao sam. Bilo je oko deset upita.

**Nagrađeni sajtovi iz branše.** Curated nema design.md ni za jedan sajt kafe: `get_design_system` za Coffee Collective (4268), Two Good Co (3281) i Cob (2584) vraća „No design.md yet". Boje, fontovi i tehnika su zato uzeti sa Awwwards stranica i iz HTML-a sajta. Sve je otvoreno 23.10.2026.

| Sajt | Nagrada | Boje | Tipografija i ritam | Šta uzimamo |
|---|---|---|---|---|
| [CoffeeTech](https://coffee-tech.com/) ([Awwwards](https://www.awwwards.com/sites/coffeetech-r)) | SOTD 16.07.2026, Developer Award | Awwwards navodi `#C8603D` i `#0D0E13`; u HTML-u je i `#F3EDE3` | Inter i Google Sans **preko fonts.googleapis.com**; slova veličine `15vw`; tagovi 3D, 360, GSAP, Transitions | Potvrdu da je trio krem, terakota i skoro crna aktuelan u nagrađenom sajtu kafe; ogromna slova kao pozadinu; 3D predmet na skrol. **Ne uzimamo** Google Fonts CDN (DSGVO) ni Inter kao naslovni font. |
| [NewmixCoffee](https://www.newmixcoffee.com/) ([Awwwards](https://www.awwwards.com/sites/newmixcoffee)) | Honorable Mention 13.04.2026 | `#000000`, `#FFFFFF` | Three.js, React, Canvas, mikrointerakcije | Jednu interakciju sa predmetom; ostalo ne. |
| [Apocalypse Coffee Roasters](https://www.awwwards.com/sites/apocalypse-coffee-roasters) | Nominee 25.08.2026 (nije SOTD) | nisu navedene | GSAP, Locomotive Scroll, gestovi, mikrointerakcije; cilj „find the right roast faster" | Brz put do prave kafe (naš „Find your cup"). Smooth-scroll biblioteku ne uzimamo, vidi „izbegnuto". |
| [Coffee Collective](https://coffeecollective.dk/) ([Curated 4268](https://curated.design/sites/s/4268/), sekcija 1486) | bez nagrade, kurirano | krem i bež, tamni tekst | navigacija verzalom sa razmakom, traka sa uslovima dostave | Mirnu navigaciju verzalom. |

Napomena: Awwwards ne navodi fontove ni za jedan od ova tri sajta. Fontove CoffeeTech-a sam pročitao iz HTML-a kao podatak, ništa nije pokrenuto. Nijedna stranica nije tražila nikakvu radnju od agenta.

### Šta je u dizajnu savremeno
Ovo je mišljenje dizajnera, uz dokaz gde postoji.
- **Poglavlja vezana za skrol sa 3D predmetom koji prelazi granicu sekcija.** Isti pravac imaju CoffeeTech (SOTD jul 2026, 3D/360/GSAP) i NewmixCoffee (HM april 2026). Kod nas je to predmet iz Blendera kao sekvenca, a ne WebGL scena, pa je lakše za telefon.
- **Topla zemljana paleta** (krem, terakota, espreso) umesto crno-zlatne. CoffeeTech je ima u istom rasponu.
- **Promenljivi fontovi sa osama**: SOFT/WONK kod Fraunces-a za mekani serif iz 70-ih i `wdth` kod Archivo-a za uži grotesk. Jedan fajl daje ceo karakter bez dodatnih rezova.
- **Ogromna dekorativna reč kao sloj iza predmeta** (CoffeeTech: `15vw`). Kod nas je to `aria-hidden` HTML tekst, a ne slika.
- **Staklo samo tamo gde ima šta da se zamuti**: kartica proizvoda iznad 3D šolje, sa neprovidnom rezervom (`@supports`) i kontrastom računatim za najgori slučaj.
- **Podaci kao deo dizajna**: na kartici su kilopreis, „inkl. MwSt." i datum prženja. Konkurencija ih nema (`brief.md`).

### Šta je svesno izbegnuto kao izlizano
Ovo je mišljenje.
- „Kafa" kao crno-zlatna paleta, rukopisni font, ikona zrna i stok fotografija latte arta.
- Inter ili Helvetica kao jedini font za naslove (CoffeeTech: Inter). Kod nas je Inter Display samo privremena zamena u mockupu.
- Staklo kao zamućene mrlje na ljubičastom gradijentu (stil iz 2021) i 3D naginjanje kartica na hover.
- Skrol koji preuzima točkić i menja mu brzinu (smooth-scroll biblioteke). Kod nas ostaje izvorni skrol sa pinom.
- Kursor koji prati miša, naslov koji se „kuca" i zvezdice svuda. Imamo jednu zvezdicu, kao u videu.

---

## 2. Boje

Uzorci iz kadrova (medijana površine, moj uzorak se slaže sa analizom):
- GRIND pozadina `#E5DCCF` (analiza `#E6DDCE`);
- reč „Lon" `#AF998F`;
- POUR reč `#5C3120`;
- SIP pozadina `#703C29` (analiza `#6E3A27`).

POUR u videu ima svetlo iz prozora (gore levo `#AF7051`). Zato je kao ton brenda uzeta vrednost iz analize, `#915439`.

| Uloga | GRIND / prodavnica | POUR | SIP |
|---|---|---|---|
| pozadina | `#E6DDCE` | `#915439` (kao u videu) | `#6E3A27` (kao u videu) |
| površina | `#F1EBE1` | `#84492F` | `#5E3020` |
| tekst | `#2B2316` | `#F4EEE4` | `#F4EEE4` |
| prigušen tekst | `#665847` | `#EDE3D5` | `#E3D6C6` |
| akcenat (tekst) | `#7A4128` | `#F7E6C6` | `#F7E6C6` |
| akcenat (površina) | `#915439` | – | – |
| linija | `rgba(43,35,22,.14)`, polja `#857563` | `rgba(244,238,228,.22)` | `rgba(244,238,228,.20)` |
| pozadinska reč | `#AF998F` (tamnija) | `#5C3120` (tamnija) | `#8A5440` (svetlija) |
| dugme | `#1B150D` + tekst `#F4EEE4` | isto + prsten `rgba(244,238,228,.65)` | isto + prsten |
| staklo | – | – | `rgba(255,249,241,.72)` + blur 16 px, rezerva `#EFE5DA` |

Zašto ove boje: to su boje iz videa. Jedina razlika su tri tona koja prave AA, a oko ih ne razlikuje od videa (odeljak 3).

## 3. Kontrast (WCAG 2.x, izračunato skriptom 23.10.2026)

**Problem iz briefa:** krem `#E6DDCE` na terakoti ima 4,42:1, a tamni tekst `#2B2316` na terakoti 2,61:1.

**Izabrano rešenje (A): terakota ostaje `#915439`, a tekst u POUR je svetliji krem `#F4EEE4`.**
- Kontrast je 5,15:1.
- Razlika u svetlini je oko 4 %, pa na ekranu deluje kao isti krem iz videa.
- Tamna dugmad su `#1B150D` umesto `#2B2316`. Pilula na terakoti ima 3,04:1, što je prag za ne-tekst (1.4.11).
- **Rezerva (B):** terakota `#8E5237` daje sa originalnim kremom 4,57:1. Pomera boju brenda, pa je nisam uzeo.

| Par | Odnos | Prag | Prolazi |
|---|---|---|---|
| *Video:* krem `#E6DDCE` / terakota | 4,42 | 4,5 | ne |
| *Video:* `#2B2316` / terakota | 2,61 | 4,5 | ne |
| GRIND tekst `#2B2316` / `#E6DDCE` | 11,51 | 4,5 | da |
| prigušen `#665847` / krem | 5,11 | 4,5 | da |
| akcenat `#7A4128` / krem | 5,97 | 4,5 | da |
| `#2B2316` / površina `#F1EBE1` | 13,07 | 4,5 | da |
| tekst dugmeta `#F4EEE4` / `#1B150D` | 15,69 | 4,5 | da |
| tekst pilule u headeru `#1B150D` / `#F4EEE4` | 15,69 | 4,5 | da |
| ivica polja `#857563` / krem | 3,30 | 3 | da |
| **POUR tekst `#F4EEE4` / `#915439`** | **5,15** | 4,5 | da |
| POUR prigušen `#EDE3D5` / terakota | 4,69 | 4,5 | da |
| POUR akcenat `#F7E6C6` / terakota | 4,84 | 4,5 | da |
| POUR tekst preko reči `#5C3120` | 9,50 | 4,5 | da |
| POUR dugme `#1B150D` / terakota (ne-tekst) | 3,04 | 3 | da |
| prsten dugmeta / terakota, reč, SIP, pod (ne-tekst) | 3,15 / 5,02 / 4,36 / 3,82 | 3 | da |
| SIP tekst `#F4EEE4` / `#6E3A27` | 7,92 | 4,5 | da |
| SIP prigušen `#E3D6C6` / braon | 6,40 | 4,5 | da |
| SIP akcenat `#F7E6C6` / braon | 7,44 | 4,5 | da |
| SIP tekst preko reči `#8A5440` | 5,32 | 4,5 | da |
| SIP tekst na podu `#7C4532` | 6,61 | 4,5 | da |
| staklo: `#2B2316` u najgorem slučaju (ispod `#1B150D`) | 7,96 | 4,5 | da |
| staklo: prigušen `#4A3D2F` u najgorem slučaju | 5,40 | 4,5 | da |
| staklo bez blura `#EFE5DA`: tekst / prigušen | 12,47 / 8,45 | 4,5 | da |
| fokus: `#2B2316` na kremu, `#F4EEE4` na terakoti | 11,51 / 5,15 | 3 | da |
| chat `#1B150D` / krem, / terakota | 13,45 / 3,04 | 3 | da |
| *ukras:* reč GRIND, POUR, SIP prema pozadini | 2,01 / 1,84 / 1,49 | – | ukras, `aria-hidden` |

Veliki naslovi (64–96 px) imaju isti odnos kao običan tekst, pa ispunjavaju i prag 4,5, ne samo 3. Pozadinske reči ne nose informaciju. Siluete su privremene.

## 4. Fontovi (samo lokalno, OFL)

Poređeno sa kadrom: probni list je renderovan pored isečka GRIND iz ispravljenog kadra.

| Uloga | Font | Podešavanje | Izvor | Status |
|---|---|---|---|---|
| naslovi poglavlja, natpisi kartica | **Archivo** (promenljiv) | `wght` 800, `wdth` 88, verzal, −0,01em | `@fontsource-variable/archivo` 5.3.0, OFL-1.1 ([npm](https://www.npmjs.com/package/@fontsource-variable/archivo), [Fontsource](https://fontsource.org/fonts/archivo)) | **PREDLOG, čeka `bezbednost`** |
| pozadinske reči | **Fraunces** | `wght` 800, `SOFT` 100, `WONK` 1, `opsz` 144 | već u repou: `sajt/src/assets/fonts/fraunces-*-full-normal.woff2` + `OFL-Fraunces.txt` | odobren (koristi DON'S) |
| tekst, meni, sitni natpisi | **Figtree** | 400 tekst; 700 verzal sa razmakom 0,12–0,32em | već u repou: `sajt/src/assets/fonts/figtree-*` + `OFL-Figtree.txt` | odobren |

**Zašto Archivo.** Izmerio sam GRIND u kadru 1440 × 900. Visina verzala je 68 px, a slova su široka 0,81–0,88 visine verzala (G 60, R 55, N 59, D 56 px). Običan težak grotesk ima oko 1,0, pa je slovo iz videa za 12–15 % uže, odnosno semi-condensed. Krive su malo kvadratne, kao kod Archivo-a. Lista fajlova paketa na jsDelivr-u (23.10.2026) ima `files/archivo-latin-wdth-normal.woff2` (90 KB) i `latin-ext` (86 KB), a to su fajlovi sa osama `wdth` i `wght`. Sažetak Fontsource stranice pominje samo `wght`. Opseg ose `wdth` nisam proverio u samom fajlu jer fontTools nije instaliran, pa je **NEPROVERENO**. Treba ga potvrditi pri instalaciji.

**Šta pokazuje mockup:** Archivo nije instaliran, pa stack pada na **Inter Display ExtraBold**. To je sistemski font na ovoj mašini (OFL), a u slučaju nužde ide Figtree iz repoa. Naslovi u PNG-u su zato oko 12 % širi nego što će biti. Osa `wdth` je već u CSS-u (`font-variation-settings`) i počinje da radi čim se Archivo doda.

**Zašto Fraunces SOFT.** Na probnom listu SOFT 100 + WONK daju zaobljen, „Cooper" oblik iz 70-ih, kao „Lon" i „Peu…are" u videu. Fraunces je širi od fonta u videu. Zato POUR i SIP koriste veći korak `--fs-word-xl`, da reč ide preko cele širine.

Za programera: woff2 i OFL fajlovi se kopiraju u assets novog projekta. CDN se ne koristi.

## 5. Raspored

**1440 (mere iz ispravljenog kadra):**
- kolona teksta počinje na ~222 px (`--chapter-inset`, 15,4 %), široka je 400 px i centrirana malo iznad sredine;
- mlin je na 46,5–77 % širine i do 800 px visine; zrna padaju iz vrha ekrana;
- strelice su prečnika 60 px na x 82 i 1370;
- reč „Lon…" počinje desno od mlina;
- POUR: kuvalo gore desno, vrh izliva tačno iznad drippera (52 %), bokal izlazi ispod ivice;
- SIP: šolja na 37–73 %, kartica desno preko drške, zvezdica, tačkice dole;
- header: logo levo, 5 stavki menija u sredini, EN, pilula „Shop", pretraga i korpa sa brojem; chat dole desno.

**390 (telefon nije umanjen desktop):**
- header je visok 64 px: logo, korpa i meni (po 44 px); meni, pretraga i EN idu u meni;
- naslov poglavlja je 64 px, a tekst 16 px;
- strelice karusela su uklonjene: telefon koristi swipe i tačkice, svaka sa 44 px dodirne površine;
- scena ima fiksnu visinu ispod teksta (28, 30 i 31 rem), pa predmet nikad ne ide preko teksta;
- kartica je 216 px sa nagibom −3° umesto −6°, radi čitljivosti;
- GRIND i POUR staju u jedan ekran (844 px), a SIP ima 938 px jer kartica mora biti čitljiva;
- izmereno: nema dodirne površine ispod 44 px i nema horizontalnog skrola na 390 i 1440.

**Svesna odstupanja od videa:**
1. **Kuvalo počinje ispod headera.** U videu ulazi u zonu headera iza pilule i ikonica. Preko čelika bi meni, pretraga i korpa bili nečitljivi. Zbog toga je mlaz kraći (oko 140 umesto 190 px).
2. Tekst u POUR je `#F4EEE4`, a dugmad `#1B150D`, sa tankim svetlim prstenom na obojenim poglavljima, jer dugme stoji preko tamne reči (odeljak 3).
3. Kartica je veća od kartica u videu (260 umesto ~160 px). Mora da nosi čitljivo ime, cenu, kilopreis, „inkl. MwSt." i datum prženja (`brief.md`: PrAG, LMIV). Dodata je oznaka „Demo" i napomena „Konzept / Demo – keine echten Bestellungen".
4. Dodat je EN prekidač (brief: DE/EN). „Section 1" je postao „Kapitel 1".
5. Siluete su sive i obeležene („3D · Mühle (Blender)"), iste veličine i položaja kao predmeti u videu.

## 6. Pokret i mirna verzija

Tokeni su u `tokens.css`, a kod piše animator.

| Pokret (obična verzija) | Trajanje / easing | Mirna verzija (`prefers-reduced-motion: reduce`) |
|---|---|---|
| poglavlje je zakačeno, a 3D sekvenca ide sa skrolom | `--pin-length` 420vh, `--ease-scrub` | bez pina; poglavlja jedno ispod drugog, po jedan statičan kadar (mlin sa zrnima u levku, dripper sa mlazom, šolja) |
| zrna i mleta kafa padaju preko granice GRIND → POUR | vezano za skrol | nema prelaza; granica je običan rez |
| talas kafe POUR → SIP | vezano za skrol | nema talasa; SIP počinje odmah |
| pozadinska reč klizi horizontalno | `--parallax-word` 0,35 | reč stoji (`--parallax-word: 0`) |
| tekst poglavlja ulazi (fade + 24 px) | `--dur-slow` 700 ms, `--ease-out` | odmah vidljiv |
| staklene kartice uleću i rotiraju se u 3D | `--dur-scene` 1100 ms, `--ease-settle` | odmah na mestu; statičan nagib ostaje jer nije pokret |
| zvezdica treperi | `--dur-twinkle` 2400 ms | ne treperi |
| boje headera se menjaju pri ulasku u poglavlje | `--dur-base` 360 ms, `--ease-in-out` | promena bez prelaza |
| hover na dugmetu (−1 px) | `--dur-fast` 200 ms | samo boja, bez pomeranja |

Sva trajanja u tokenima padaju na 1 ms u mirnoj verziji. Mockup je statičan: snimak sa `reducedMotion: 'reduce'` je identičan običnom (provereno poređenjem piksela).

## 7. Za sledeće korake

- **`bezbednost`:** provera `@fontsource-variable/archivo@5.3.0` pre instalacije. Ja ništa nisam instalirao.
- **`tekstopisac`:** pozadinske reči i tekstovi poglavlja; sada su privremeni DE tekstovi bez neproverivih tvrdnji.
- **Blender:** okviri sekvenci na 1440: mlin sa zrnima 440 × 810, kuvalo širine ~490, dripper sa bokalom 380 × 560, šolja 520 × 470. Pozadina mora biti providna.
- **programer:**
  - u produkciji je **jedan** `position: fixed` header, a `data-chapter` se menja skrolom (IntersectionObserver); isto važi za chat;
  - kopije headera i chata u POUR i SIP u mockupu su samo prikaz stanja (`aria-hidden`, `inert`);
  - položaj kuvala je računat u `vw` i proveren samo na 1440 i 390; na 1920 i na tabletu (1024) treba ga proveriti.
- **recenzent:** porediti sa kadrovima `f_001`, `f_090` i `f_213`; naslovni font u PNG-u je privremena zamena (odeljak 4).
