---
name: Krume · Ein Fenster brennt
colors:
  background: "#14110f"
  on-background: "#f6f1e7"
  surface: "#201a15"
  surface-high: "#2a221b"
  on-surface: "#f6f1e7"
  on-surface-variant: "#b8a690"
  primary: "#e8792b"
  on-primary: "#14110f"
  outline: "#857462"
  outline-variant: "rgba(246,241,231,0.16)"
  error: "#e86a5a"
  day-surface: "#f6f1e7"
  on-day-surface: "#14110f"
  on-day-surface-variant: "#6e5a45"
  day-accent: "#7a4a24"
  day-outline: "#8a7d6c"
  day-error: "#a3341f"
typography:
  display:
    fontFamily: Bricolage Grotesque
    fontSize: clamp(40px → 84px)
    fontWeight: "640"
    lineHeight: "1.02"
    letterSpacing: -0.03em
    fontVariation: opsz 96
  headline:
    fontFamily: Bricolage Grotesque
    fontSize: clamp(32px → 56px)
    fontWeight: "640"
    lineHeight: "1.08"
    letterSpacing: -0.025em
  accent-word:
    fontFamily: Instrument Serif
    fontStyle: italic
    fontWeight: "400"
    note: samo jedna reč u naslovu ili futer
  title:
    fontFamily: Bricolage Grotesque
    fontSize: clamp(20px → 26px)
    fontWeight: "620"
  lead:
    fontFamily: Bricolage Grotesque
    fontSize: clamp(17px → 20px)
    fontWeight: "400"
    lineHeight: "1.55"
  body:
    fontFamily: Bricolage Grotesque
    fontSize: 16px
    fontWeight: "400"
    lineHeight: "1.55"
  kicker:
    fontFamily: Bricolage Grotesque
    fontSize: clamp(16px → 18px)
    fontWeight: "560"
    note: jedna reč poglavlja, bez verzala i bez vremena (vreme je u satu)
  oven-time:
    fontFamily: Bricolage Grotesque
    fontSize: clamp(20px → 24px)
    fontWeight: "600"
    fontFeature: tabular-nums
  display-mobile:
    fontFamily: Bricolage Grotesque
    fontSize: 34px
    lineHeight: "1.04"
  tick:
    fontFamily: Bricolage Grotesque
    fontSize: 12px
    note: samo oznake lenjira (nisu sadržaj)
  clock:
    fontFamily: Bricolage Grotesque
    fontSize: clamp(18px → 22px)
    fontWeight: "600"
    fontFeature: tabular-nums
rounded:
  xs: 2px
  sm: 6px
  md: 10px
  lg: 18px
  pill: 999px
spacing:
  unit: 4px
  scale: [4, 8, 12, 16, 24, 32, 48, 64, 96]
  gutter: clamp(20px → 56px)
  tap-min: 44px
  tap-bar: 52px
motion:
  ease-out: cubic-bezier(0.22, 1, 0.36, 1)
  ease-in-out: cubic-bezier(0.65, 0, 0.35, 1)
  ease-in: cubic-bezier(0.55, 0, 1, 0.45)
  camera: GSAP quickTo power3.out
  durations: [120ms, 240ms, 480ms, 720ms, 1200ms]
  stagger: 80ms
components:
  button-primary: { background: primary, color: on-primary, rounded: pill, height: 44px (52px u traci na 390) }
  button-primary-hover: { background: "#f08a40" }
  button-ghost: { background: transparent, border: 1px outline, color: on-surface, rounded: pill }
  button-day: { background: "#14110f", color: "#f6f1e7", rounded: pill, height: 52px }
  bread-label: { background: none (na nebu), border-left: 1px outline-variant, leader: 1px testo + 3px tamni halo do hleba; active: 2px primary, vreme i cena u primary }
  bread-label-mobile: { background: background, border: outline-variant, rounded: md, scroll-snap: x mandatory }
  hours-table: { background: none (na nebu), rows: 1px rgba(246,241,231,.28) }
  sackerl-form: { background: day-surface, rounded: "0 0 lg lg", top-edge: zigzag }
  input-field: { background: "#fffdf8", border: day-outline, rounded: sm, height: 48px; focus: day-accent + 3px ring }
---

# Krume: dizajn sistem HTML sloja (smer 3 „Ein Fenster brennt")

Dizajner, 27. 10. 2026, **v2 posle recenzije** (6/10 → popravke 1–8 direktora). Tokeni: `tokens.css`. Mockup: `mockup.html`, snimci `mockup-1440.png` i `mockup-390.png` (Chromium headless shell 1248).
Posao ovde je HTML sloj preko fiksnog Three.js canvas-a, ne 3D. Pozadina mockup-a su probni renderi `../blender/kuca-proba-1.png` i `-2.png`. U kadru 06:30 render je samo posvetljen CSS filterom, a kadar 05:00 nema pravi presek. Futer je zatamnjen render 1. Svi su označeni u uglu („Probe-Render").

## 1. Atmosfera

Maketa na dasci u mraku, i jedan topao prozor. HTML sloj se ponaša kao **natpis uz maketu u muzeju**: malo elemenata, tih, precizan, i nikad ne preuzima svetlo od scene.

- **Jedan topli izvor:** žar `#e8792b` je jedina zasićena boja u UI-ju. Koristi se za dugme Vorbestellen, kazaljku sata, aktivni hleb i mali „prozor" u logotipu, i nigde više. Tako UI ponavlja pravilo scene: „sve svetlo kreće iz pekare".
- **Tekst stoji na mirnom delu kadra** (nebo, tamni zid, prazna daska), bez senke i bez gradijent-mrlje. **Nema ploča ni kartica:** hlebovi dobijaju etikete sa tankom linijom do police, radno vreme je tipografska tabela na nebu.
- **Dan je papir:** Sackerl forma je jedini predmet u UI-ju: svetla ploča boje brašna sa nazubljenim gornjim rubom papirne kese. Jutro zato deluje kao promena materijala, a ne kao novi „light mode".
- Gustina: retka. Po kadru jedna reč poglavlja, jedan naslov, najviše dve rečenice. Vreme stoji samo u satu, ne ponavlja se u tekstu.

### Savremeno, i šta je svesno izbegnuto
Baza znanja je od danas (`studio/znanje/trendovi.md`, `reference.md`, 2026-10-27), pa nije ponovo istraživano (CLAUDE.md, Istraživanje t. 1). Alat `get_design_system` (Curated) u ovoj sesiji nije bio dostupan, pa tokeni nagrađenih sajtova nisu očitani. Principi su uzeti iz opisa u bazi znanja.

Uzeto (princip, ne kopija):
- **Skrol je vreme, a kamera kasni** (trend 1 i 3; Oryzo/Lusion, Awwwards SOTM 04/2026, prema sekundarnom izvoru utsubo.com). HTML tekst zato ne prati skrol 1:1, nego ulazi tek kad kamera „stane" na stanici.
- **Jedna scena, više stanja, i rezervni običan prikaz** (La Revoltosa, [Awwwards studija slučaja](https://www.awwwards.com/la-revoltosa-rebooting-a-70-year-old-spanish-soda-brand-for-the-scroll-generation.html)). Isti HTML služi i za 3D i za statične kadrove.
- **Kamera po putanji iz Blendera + `quickTo` power3.out** ([Codrops, 2026-07-07](https://tympanus.net/codrops/2026/07/07/building-a-scroll-driven-3d-gallery-using-a-blender-camera-path-with-three-js-and-gsap/)). Easing kamere je u tokenima kao string.
- Kod pekara bez 3D (Sonoma Bakery, UND NY, [Awwwards elementi](https://www.awwwards.com/inspiration/transition-sonoma-bakery)) samo ton: mnogo prostora, kratke rečenice, cena kao deo tipografije.

Izbegnuto kao izlizano:
- Tamni gradijent ispod teksta („scrim"), glassmorphism kartice sa blur-om preko 3D-a, teški bloom preko svega (`trendovi.md`, Izbegavati).
- Tekst kao 3D geometrija (La Revoltosa to radi; ovde bi pojeo čitljivost na telefonu i pristupačnost).
- Krupni „hero brojevi", scroll-procenat u uglu, numerisane kartice (01–04) i eyebrow-i u sitnim verzalima sa razmakom i crticom. Umesto toga postoji pravi sat sa lenjirom 04–07, koji nosi značenje.
- Mreža od 4 iste kartice za proizvode (šablon). Hleb je u vitrini, pa je etiketa uz njega.
- Na telefonu „slika gore, tamni blok sa tekstom dole". Kadar je ceo ekran, a tekst leži na mirnom dnu scene.
- Serif-display za sve (klišej „zanatske pekare"). Serif se pojavljuje samo kao jedna reč.

## 2. Boje

| Ime | Hex | Uloga |
|---|---|---|
| noć | `#14110f` | pozadina stranice, etiketa hleba u nizu na 390, tekst na žaru i na brašnu |
| površina | `#201a15` | donja traka na 390, meni, hint-ovi |
| površina visoka | `#2a221b` | hover / pritisnuto stanje |
| brašno | `#f6f1e7` | glavni tekst na tamnom; pozadina Sackerl forme |
| prigušen tekst | `#b8a690` | reč poglavlja, opisi hlebova, „aus dem Ofen um", meta |
| žar (akcenat) | `#e8792b` | primarno dugme, sat, aktivni hleb (linija, tačka, vreme, cena), tačka „otvoreno", fokus |
| linija | `rgba(246,241,231,.16)` | dekorativne linije (ne nose značenje) |
| linija jaka | `#857462` | ivica ghost dugmeta i polja na tamnom |
| testo | `#eadbc4` | serifna reč naglaska („Krume.", „Bis morgen früh."), vreme iz peći, linije do hleba |
| kora | `#7a4a24` | akcenat na svetlom: pečat „Krume · Für dich", fokus polja |
| prigušen na danu | `#6e5a45` | opis forme, napomena |
| greška | `#e86a5a` / `#a3341f` | tamni / svetli sloj |

Kamen `#2b2a28` i krov `#3b4048` žive samo u 3D sceni i nisu u UI-ju.

### Kontrast (WCAG 2.x, izračunato skriptom iz relativne luminanse, 27. 10. 2026)

Pozadina scene je izmerena u probnim renderima (prosek i najsvetliji piksel zone gde stoji tekst): nebo kadra 04:00 je `#12243b`, najsvetlije `#14263f`. Ulica pod prozorom je najsvetlija na `#8e5e2e`.

| Par | Odnos | Prag | |
|---|---|---|---|
| brašno na noći | 16.70 | 4.5 | da |
| brašno na površini `#201a15` | 15.29 | 4.5 | da |
| brašno na nebu, najsvetlije `#14263f` | 13.53 | 4.5 | da |
| brašno na ulici, najsvetlije `#8e5e2e` | 4.92 | 4.5 | da, ali tek na granici: tekst tamo ne ide |
| brašno na posvetljenom nebu 06:30 (`#203d5f` / `#2f4f74`) | 9.85 / 7.49 | 4.5 | da |
| prigušen `#b8a690` na noći / površini / nebu | 7.96 / 7.29 / 6.45 | 4.5 | da |
| prigušen na posvetljenom nebu `#2f4f74` | 3.57 | 4.5 | **ne**: u 06:30 je sav tekst na nebu u boji brašna (reč poglavlja, tabela, adresa) |
| prigušen na `#2a221b` (hover) | 6.62 | 4.5 | da |
| žar `#e8792b` na noći / površini / `#2a221b` | 6.45 / 5.90 / 5.36 | 4.5 | da |
| noć na žaru (tekst dugmeta) | 6.45 | 4.5 | da |
| brašno na žaru | 2.59 | | **ne**, zato je tekst na dugmetu taman |
| noć na brašnu (forma) | 16.70 | 4.5 | da |
| `#6e5a45` na brašnu / testu | 5.81 / 4.80 | 4.5 | da |
| kora na brašnu / testu | 6.59 / 5.45 | 4.5 | da |
| greška `#e86a5a` na površini; `#a3341f` na brašnu | 5.44 / 6.08 | 4.5 | da |
| ivica polja `#8a7d6c` na polju `#fffdf8` | 3.95 | 3 (ne-tekst) | da |
| ivica `#857462` na površini / noći | 3.83 / 4.18 | 3 (ne-tekst) | da |
| brašno / prigušen na tamnom zidu iza naslova „Brot des Tages" (izmereno `#110d0e`) | ~16.9 / ~8.1 | 4.5 | da |
| brašno / prigušen / žar na nebu iza etiketa (izmereno `#12233a`) | 13.6 / 6.5 / 5.2 | 4.5 | da (glava lampe je svetla, zato etikete počinju ispod nje) |
| brašno / prigušen / testo na večernjem nebu futera `#0b1524` | 16.26 / 7.76 / 13.45 | 4.5 | da |
| linija do hleba: testo 1 px preko tamnog haloa 3 px `rgba(20,17,15,.85)` | čita se i na staklu izloga i na zidu | 3 (ne-tekst) | da |
| placeholder `#8a7d6c` na `#fffdf8` | 3.95 | | placeholder nije labela; labela „Name" stoji iznad (16.7) |

## 3. Tipografija

**Dve familije, obe lokalne (woff2 u repou, bez CDN-a):**
1. **Bricolage Grotesque** (variable, `pekara/assets/fonts/bricolage-latin-var.woff2`, OFL). Proverene ose u Chromium-u: `wght` 200–800 i `opsz` 12–96. Ose `wdth` u ovom fajlu nema, iako je Google verzija ima. Cifre su tabularne (`tabular-nums` daje istu širinu za „11:11" i „00:00"). Zašto: grotesk sa malo „ručne" nepravilnosti (podsećanje na kartonsku maketu i natpise na izlogu), i optička veličina daje gust, težak naslov na 84 px, a čitljiv tekst na 16 px iz istog fajla. Smer 3 ga i predviđa.
2. **Instrument Serif Italic** (`freiraum-premium/src/assets/fonts/instrument-serif-italic.woff2`, OFL). Samo jedna reč naglaska: „Krume." u potpisnom naslovu i „Bis morgen früh." u futeru. Zašto: mekoća mrvice nasuprot kori groteska, ali u dozi koja ne pravi „rustik pekaru".

**Sat:** smer traži uski mono (OFL, self-host). Ovde je Bricolage sa tabularnim ciframa, da ne bude treća familija. **Predlog, ne odluka:** ako recenzent želi mono, kandidat je JetBrains Mono ili IBM Plex Mono (OFL) preko `@fontsource`, ali tek posle provere `bezbednost` (novi npm paket).

| Nivo | Veličina 390 → 1440 | Težina | Upotreba |
|---|---|---|---|
| display | 40 → 84 px, lh 1.02, −0.03em, opsz 96 | 640 | H1 i naslovi poglavlja na sceni |
| headline | 32 → 56 px | 640 | Brot des Tages, Sackerl (40 px u formi) |
| title | 20 → 26 px | 620 | ime i cena hleba |
| oven-time | 20 → 24 px, tabular | 600 | „6:10" iznad imena hleba (uvod „aus dem Ofen um" je 16 px, prigušen) |
| lead | 17 → 20 px | 400 | rečenica ispod naslova, najviše 34ch |
| body | 16 px | 400 | sve ostalo (nikad manje za čitanje) |
| kicker | 16 → 18 px, obična slova | 560 | reč poglavlja („Das Grätzl"), bez vremena, crtice i tačke |
| display (390) | 34 px, lh 1.04 | 640 | naslov poglavlja na telefonu |
| clock | 18 → 22 px, tabular | 600 | sat |
| tick | 12 px | 400 | oznake lenjira 04 · 05 · 06 · 07 (jedini tekst ispod 16 px; nije sadržaj) |

**Najmanje 16 px za sve što se čita:** lead, meta, opisi hlebova, hint-ovi („Dreh das Grätzl"), labele forme, napomene i futer. Ispod 16 px su samo oznake lenjira (12 px), pečat na kesi (12 px, ukras) i oznake „Probe-Render" u mockup-u (11 px, nisu deo sajta).

Naslovi imaju `text-wrap: balance`. H1 na 1440 je namerno u tri reda (max 8.5ch), da stane u levi mirni deo kadra pored makete.

## 4. Komponente

### Kako tekst stoji na sceni (najvažnije pravilo)
- **Strana neba.** Za svako poglavlje kamera u 3D ostavlja jednu stranu kadra praznu (nebo ili tamna daska), i tekst ide tamo. Nema senke iza slova, scrima ni blura. Programer i 3D dogovaraju kadar, a ne obrnuto. U mockup-u: 04:00 levo (kuća desno od centra), 05:00 desno (kuća levo, uz lampu), 06:30 levo.
- **Zabranjene zone:** osvetljen izlog, vrata, ulica ispred njih i glava ulične lampe. Tekst nikad ne prelazi preko toplog prozora: to je junak. Preko stakla smeju samo tanke linije do hleba (sa tamnim haloom).
- **Bez ploča za sadržaj.** Jedini predmet je Sackerl forma. Hint-ovi su male pilule, a donja traka je deo navigacije.
- Najveća širina pasusa je 34ch. Iznad naslova stoji samo reč poglavlja („Das Grätzl", „Der Anschnitt", „In der Auslage", „Das Grätzl wacht auf", „Vorbestellen"). Za čitač ekrana ispred nje ide skriveno vreme („vier Uhr. ").

### Sat 04:00 → 07:00
- Centar navigacije: vreme (tabular) i ispod lenjir 200 px (124 px na 390) sa podeocima 04 · 05 · 06 · 07 od 12 px. Krajnje oznake su poravnate sa krajevima lenjira. Ispunjen deo i tačka su žar sa malim sjajem (`--glow-window`). Tačka je isti „prozor" kao u logotipu.
- Jedini element vezan direktno za udeo skrola (mapa skrola, predlog). Vreme skače u koracima od 5 minuta, ne u svakom kadru, da cifre ne trepere. Lenjir je kontinualan.
- `aria-hidden="true"`. Za čitač ekrana vreme je skriven tekst na početku reči poglavlja („vier Uhr. ") u svakom poglavlju (tekstovi.md).
- U 06:30 sat staje dok se pojavi „Wir sperren auf.", pa ide do 07:00 (beleška tekstopisca).

### Dugmad
- **Primarno (žar):** `#e8792b` / tekst noć, pill (oblik zemičke), 44 px (u donjoj traci na 390 je 52 px, `btn-lg` 52 px). Hover `#f08a40`, active 1 px niže, fokus 2 px žar obris + 3 px razmak. Isključeno: `#3a3029` pozadina, tekst `#b8a690`, bez kursora.
- **Ghost:** providno, ivica `#857462` 1 px, tekst brašno („Menü").
- **Tekst-dugme „Ton an":** na desktopu stoji u navigaciji ispred Vorbestellen (prigušeno, 44 px visine), a na 390 je u meniju. Ovo je `<button aria-pressed>`, podrazumevano isključen.
- **Dnevno (u formi):** noć na brašnu, puna širina forme, 52 px.
- Na celoj stranici je jedno žar dugme u kadru. U formi je dugme tamno, da se Sackerl ne „takmiči" sa navigacijom.
- Strelica je deo teksta (`→`, `aria-hidden`), bez ikonice.

### Navigacija
- Bez trake i pozadine: logotip levo, sat u centru, linkovi i Vorbestellen desno, sve direktno na nebu (koje je tamno u svakom kadru do 06:30; od 07:00 nav dobija punu `#201a15` traku, prelaz `--dur-5`).
- Logotip: „Krume" u Bricolage 700 i mali žar pravougaonik 12×16, „jedini upaljen prozor".
- Aktivni link: `aria-current="location"` + podvlaka u žaru.
- **390:** logotip · sat · „Menü" (44 px). Meni je puna ploča `#201a15` preko ekrana, sa linkovima od 56 px i prekidačem „Ton an" na dnu. **Donja traka** sadrži samo „Für morgen vorbestellen" (52 px, cela širina). **Pojavljuje se tek kad hero kadar izađe** (prelaz `--dur-3`, translateY 100% → 0, bez pokreta sa reduced motion) i sakrije se kad je forma u vidu, da ne bude dva ista dugmeta. Koristi `env(safe-area-inset-bottom)`.

### Hint-ovi
- „← Dreh das Grätzl →" je mala puna pilula (površina, 16 px) u donjem desnom uglu kadra 04:00 (na 390 iznad naslova, ispod makete). Nestaje posle prvog povlačenja. Bez WebGL-a i sa reduced motion se ne prikazuje.
- „Klopf ans Fenster." je pilula sa žar tačkom pored vrata u 05:00 i pravi je `<button>` (44 px). Stoji uz prozor, ali nikad preko stakla.
- Skrol-hint „Scrollen" (16 px) sa linijom 36 px, samo u 04:00 na desktopu.

### Etikete hlebova („Brot des Tages")
- Kadar je izlog sa policama. **Nema ploče ni kartica.** Levo, na tamnom zidu pored izloga, stoji „In der Auslage" · „Brot des Tages" (56 px) · rečenica. Desno, na nebu, su 4 etikete jedna ispod druge, poravnate po levoj tankoj liniji.
- Etiketa: gore krupno vreme iz peći („aus dem Ofen um" 16 px prigušeno + **„6:10" 24 px tabular, testo**), ispod ime (26 px) i desno cena (26 px, tabular). Opis (16 px) ima samo aktivni hleb.
- **Linija do hleba:** iz leve ivice etikete ide kratak vodoravni krak, pa kosa linija do tačke na hlebu (1 px testo preko 3 px tamnog haloa, tačka 5 px). Linije se ne seku: gornja etiketa ide na gornju policu. U 3D: tačka je projekcija pozicije hleba (`Vector3.project`) i osvežava se u svakom frejmu, a SVG je jedan sloj preko canvas-a.
- **Aktivni hleb** (onaj koji je u 3D upravo izašao napred) ima liniju i tačku u žaru, levu ivicu od 2 px u žaru i vreme i cenu u žaru. Ostale ostaju pune boje, da se mogu čitati i van redosleda.
- Bez brojeva 01–04. `<ol>`, a aktivna dobija `aria-current="true"`.
- **390:** naslov stoji ispod izloga, na tamnoj ulici koja se gasi u noć. Ispod je **vodoravni niz etiketa sa `scroll-snap-type: x mandatory`**: vidi se jedna etiketa (širina 100% − 56 px) i ivica sledeće, i to je znak da niz može da se povuče. Etiketa je ovde puna (noć, ivica, radius 10), jer stoji preko scene. Ispod niza su tačke (aktivna je izdužena, u žaru). Prevlačenje niza menja aktivni hleb u 3D, a skrol stranice ide dalje. Linija do hleba se na telefonu ne crta: aktivni hleb izlazi napred skalom.

### Radno vreme
Tanka tipografska tabela **direktno na nebu**, bez ploče (`dl`, širina 26rem). Redovi su odvojeni linijom `rgba(246,241,231,.28)`, dani levo, sati desno (tabular, 600). Uz Dienstag bis Samstag **6:30 – 14:00** stoji tačka u žaru („otvoreno"), a u poslednjem redu adresa „Neubau, 1070 Wien · fünf Minuten vom Siebensternplatz". Sav tekst je u boji brašna (prigušen ne prolazi na jutarnjem nebu).

### Forma „Dein Sackerl für morgen"
- Jedini predmet na stranici. Ploča boje brašna, širine 440 px (desno od makete), sa zaobljenjem samo dole i **nazubljenim gornjim rubom** papirne kese (clip-path). Pečat „Krume · Für dich" u kori, rotiran 6°. Pečat je ukras (`aria-hidden`) i u stanju „Reserviert" menja tekst (tekstovi.md).
- Polja: Brot (select sa cenom), Stück (stepper − / + od 44 px, 1–40) u jednom redu, ispod Name (placeholder „z. B. Anna", `autocomplete="given-name"`). Visina polja je 48 px, a labela je uvek iznad (nikad samo placeholder).
- Fokus: ivica u kori i prsten od 3 px `rgba(122,74,36,.18)`. Greška: tekst `#a3341f` ispod polja i `aria-describedby`, ivica u istoj boji. Poruka ide doslovno iz tekstovi.md.
- Dugme „Für morgen reservieren" je puna širina, noć na brašnu. Napomena „Konzept: …" je small, prigušena.
- Iza forme 3D stoji dnevna maketa (mapa: blur u 3D-u, ne CSS `backdrop-filter`). Ploča je puna, pa čitljivost ne zavisi od blura. Na 390 kesa ide preko cele širine, ispod kadra 06:30.

### Futer
Futer je **večernji kadar** (7b iz mape): ista maketa, nebo palo u veče, svetli samo prozor pekare. U mockup-u je to zatamnjen render 1. Maketa je desno, a tekst levo na praznom nebu: „Bis morgen früh." u Instrument Serif Italic 48 → 104 px u boji testa (bez narandžastog kvadrata, jer je prozor u kadru). Ispod je rečenica iz tekstovi.md (16 px, prigušeno), pa linkovi (Vorbestellen, Brot des Tages, Öffnungszeiten, „Zurück auf vier Uhr ↑", 44 px), linija i Impressum-red „Krume ist ein Konzept von Nemi Studio …" · „Konzept · Nemi Studio" (16 px). Na 390 je kuća gore, a tekst ispod nje na nebu.

### Prelazi teksta između poglavlja
- Tekst poglavlja je vezan za **stanicu kamere, ne za piksel skrola**. Kad udeo uđe u opseg poglavlja (mapa skrola), elementi ulaze redom: reč poglavlja, naslov, tekst (`--stagger` 80 ms), opacity 0→1 i translateY 24→0 px, `--dur-4` 720 ms, `--ease-out`. Izlaz je kraći: opacity →0 i −12 px, `--dur-3` 480 ms, `--ease-in`. Dva poglavlja nikad nisu istovremeno vidljiva: izlaz se završi pre ulaza.
- 05:00: tekst se skloni (opacity 0) dok se kriška izvlači (pin 0,30–0,39), pa se vrati kad presek stoji.
- 05:15: tri koraka, uvek vidljiv jedan. Tekst se ne pomera, samo se pretopi (`--dur-3`).
- Brot des Tages: etikete uđu jednom (stagger), a linije se „docrtaju" (`stroke-dashoffset`, `--dur-4`). Posle toga se menja samo stanje aktivne (boja `--dur-3`). Ništa ne skače.
- **390:** prvo ulaze reč i naslov (kratko). Lead (17 px) ulazi tek posle dodatnih ~25 svh skrola unutar istog poglavlja, kad kamera stane, pa je kadar u prvom trenutku miran. U mockup-u hero prikazuje prvo stanje, a 05:00 stanje posle skrola.
- Bez SplitText animacije po slovima: tiho, čitljivo, jeftino na telefonu.

## 5. Raspored

- Osnova 4 px. Skala 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96. Ivica ekrana `--gutter` 20 → 56 px.
- Desktop: tekst je apsolutno postavljen u „mirnu stranu" kadra, sa donjom ivicom na 96 px (hero) ili gornjom na ~180 px (ostali). Nav je visok 92 px.
- Tekst i kesa se drže ivice ekrana (gutter), a ne centralne mreže, da maketa ostane u centru.
- 390: tekst je na dnu kadra, 24 px od ivice (96 px kad je donja traka vidljiva).

## 6. Dubina

Slojevi: canvas (0) · tekst, etikete i kesa (10) · nav (50) · donja traka (60) · skip-link (100).
Senke postoje samo na hint-pilulama (`--shadow-plate`) i na kesi (`--shadow-bag`). Tekst preko scene nema senku. Sjaj (`--glow-window`) imaju samo stvari koje „gore": logo-prozor, tačka sata i tačka „otvoreno".

## 7. Oblici

2 px tickovi · 6 px polja · 10 px etiketa u nizu na 390 · 18 px kesa · pill samo za dugmad i hint-ove (oblik zemičke). Oštri uglovi nigde osim gornjeg ruba kese, koji je nazubljen.

## 8. Sme / ne sme

Sme:
- Tekst na nebu ili na tamnom zidu, a forma na papirnoj kesi.
- Žar samo za stvari koje „gore" ili su glavna akcija.
- Prave reči iz tekstovi.md. Austrijski izrazi ostaju.

Ne sme:
- Gradijent, scrim ili blur iza teksta da bi se „spasila" čitljivost. Pomera se kamera.
- Ploče i kartice za sadržaj, numeracija 01–04, sitni verzali sa razmakom.
- Tekst za čitanje manji od 16 px.
- Tekst preko osvetljenog izloga, vrata ili ulice.
- Brašno (svetao tekst) na žaru (2.59:1).
- Prigušen tekst direktno na posvetljenom jutarnjem nebu (3.57:1).
- Treća familija fonta ili Google Fonts CDN.
- Dva žar dugmeta u istom kadru.

## 9. Odziv

### 1440 px
Kao u `mockup-1440.png`: tekst u mirnoj strani kadra, nav bez trake, etikete hlebova sa linijama, radno vreme kao tabela na nebu, kesa desno od makete, večernji futer.

### 390 px (nije umanjen desktop)
- **Svaki kadar je ceo ekran (100svh)**, a canvas je fiksan preko cele visine. Kamera drži ugaonu kuću i topli prozor u gornjih ~60%, a donji deo kadra je mirna praznina (tamna daska, ulica koja se gasi, nebo). Tamo leži tekst. Nema „slika gore, tamni blok dole".
- Na dnu stoje samo reč poglavlja i naslov 34 px (lh 1.04). Lead dolazi tek na skrol (vidi prelaze). Naslovi do 32 znaka staju u 2 reda.
- Dugmad u tekstu se sklanjaju. CTA je u donjoj traci (52 px), koja se pojavljuje tek posle hero kadra. „Ton an" je u meniju.
- Brot des Tages: vodoravni niz sa jednom etiketom i scroll-snap. 06:30: tabela na nebu ispod naslova, a kesa preko cele širine posle kadra. Futer: kuća gore, tekst ispod.
- Dodirne površine su najmanje 44 px: linkovi u nav-u i futeru, stepper, hint-ovi, „Menü", tačke niza (područje 44 px oko tačke).
- Ivice teksta su 20 px. Bez hover-zavisnosti.

### prefers-reduced-motion (i bez WebGL-a)
- Tokeni: sva trajanja su 0 ms, stagger 0, `--rise` 0 (u `tokens.css`).
- Umesto canvas-a idu statični WebP kadrovi po poglavlju (16:9 / 9:16) kao `<img>` sa alt tekstovima iz tekstovi.md. Menjaju se **tvrdim rezom** na granici poglavlja (bez pretapanja), ili stoje jedan ispod drugog u prirodnom toku stranice.
- Tekst je uvek vidljiv (bez ulaza i izlaza). Sat skače po poglavljima (04:00, 04:30, 05:00 …), bez kontinualnog lenjira. Lenjir pokazuje stanje poglavlja.
- Nema Lenisa, drag-a, čestica, sjaja koji pulsira ni zvuka. Hint-ovi „Dreh das Grätzl" i „Klopf ans Fenster." se ne prikazuju.
- Brot des Tages: sve 4 etikete i linije su odmah nacrtane, bez aktivnog stanja i bez docrtavanja. Na 390 niz ostaje (prevlačenje je korisnikov pokret), ali `scroll-behavior: auto`.
- Na 390 lead stoji odmah uz naslov, a donja traka je vidljiva odmah posle hero kadra, bez klizanja.
- Fokus obrisi, hover boje i forma rade isto. Menja se samo pokret, ne informacija.

## Odluke direktora (27. 10. 2026)
1. Naslov preseka: **B „Unter der Kruste: *Krume.*"**.
2. Sat ostaje u Bricolage sa tabularnim ciframa. **Mono font se ne uvodi.**

## Otvoreno
- Probni renderi imaju plavo nebo (`#12243b`), a brief kaže noć `#14110f`. Kontrast je proveren za oba. Ako 3D ide toplije i tamnije, odnosi samo rastu.
- Pozicije etiketa na desktopu su ručno namerene na probnom renderu. Na sajtu ih određuje projekcija iz 3D-a, a etikete ostaju u desnoj koloni na nebu.
