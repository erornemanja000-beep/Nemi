# Trendovi: 3D / skrol sajtovi proizvoda, tipografija, prelazi, tehnika browsera

Poslednja provera: 2026-10-23
Vodi: `trend-skaut`. Prvo punjenje (fokus: kafa / pića / hrana sa 3D proizvodom na skrol).

**Granica ovog prolaza (čitaj pre upotrebe):** uzorak je 13 sajtova sa Awwwards-a (nagrade 2025-11 do 2026-10), detalji u `reference.md`. FWA, CSSDA i Godly nisu mogli da se pročitaju. Trend = ponavlja se na bar 3 sajta (pravilo agenta). Za "izlizano" nema dovoljno dokaza iz tako malog uzorka, zato je odeljak "Izbegavati" kratak i označava šta je dokumentovano, a šta mišljenje. Telefonsko ponašanje nije gledano uživo.

## 1. Trendovi (3 i više primera)

### T1. Unapred renderovana sekvenca slika na sticky canvas-u, vezana za skrol
- Primeri: More Nutrition (SOTD 2025-11, `data-sequence-canvas` + ScrollTrigger), Vibe (HM 2026-09, 150 WebP kadrova), Seasats (SOTD 2026-09, `AnimateFrames` canvas, Cinema 4D), Koffiracha (2025, 3D render → sekvenca za skrol), delimično CoffeeTech (SOTD 2026-07, AVIF kadrovi iz rendera). (2026-10, HTML sajtova + Awwwards)
- Razlog (moje tumačenje iz HTML-a): proizvod izgleda fotorealno bez opterećenja GPU-a telefona, a ceo kadar je pod kontrolom režisera (svetlo, materijali).
- Suprotna struja: realno-vremenski WebGL/Three.js. Primeri: CIAO ENERGY (Three.js + Blender), /zeroz (Three.js + Blender), SŌM (WebGL), Santioni (Active Theory, WebGL), NewmixCoffee (Three.js). (2026-10, Awwwards tagovi)
- Kada šta: sekvenca kad je proizvod fiksan objekat i putanja kamere se zna unapred (naš mlin → kuvalo → šolja). WebGL kad korisnik treba slobodno da vrti ili "sipa" (Santioni, NewmixCoffee). Hibrid je moguć.
- Merljivo: Vibe 150 kadrova × 34–52 KB (WebP) ≈ 6–7 MB; naše sekvence u `freiraum` 80 kadrova × 36–58 KB. Tehnički detalji i budžet: `ai-alati.md`, odeljak "Blender za web sekvence". (2026-10, merenje)

### T2. Zasebna mobilna verzija pokreta, ne samo skaliranje
- Primeri: Best Bean Best Cup (`herobanner-desktop.mp4` + `herobanner-mobile.mp4`), NewmixCoffee (`Footer_animation_desktop/mobile.mp4`), /zeroz (`hero-mobile` slike), SŌM (`hero-mobile-*`), More Nutrition ("3D Product Animation on Mobile" kao poseban element). (2026-10, HTML + Awwwards)
- Naš `freiraum` već radi tako: set `d` 720×1280 i set `m` 540×960, prag širine 860 px. (2026-10, kod u repou)

### T3. Webflow ili Shopify + GSAP (ScrollTrigger, SplitText) + Lenis kao standardni stek
- Primeri: CIAO ENERGY, CoffeeTech, More Nutrition, Sunbeam (Webflow + GSAP 3.15.0), Best Bean Best Cup i Koffiracha (Shopify + GSAP), Lenis na CIAO, Seasats i Vibe. (2026-10, HTML)
- GSAP je besplatan za sve, uključujući dodatke ("GSAP is now free for everyone, thanks to Webflow's support", gsap.com, 2026). Lenis 1.3.27, licenca MIT. `RealEstates` već koristi `gsap ^3.15.0` i `lenis ^1.3.27`. (2026-10, gsap.com + GitHub)

### T4. Zvuk kao deo iskustva
- Primeri sa tagom Sound-Audio: CIAO ENERGY, More Nutrition, Sunbeam (skriveni zvuci), Santioni. (2026-10, Awwwards)
- Pravilo za nas: zvuk samo na zahtev (dugme), isključen po defaultu. Browseri ionako blokiraju zvuk bez radnje korisnika (opšte poznato, u ovom prolazu nije ponovo proveravano). Pristupačnost: nikad jedini nosilac informacije.

### T5. Ciklični / beskonačni hero
- Primeri: CIAO ENERGY ("Looping Site", "Hero with infinite scrolling"), SŌM (Infinite Scroll), Seasats (Infinite Scroll). (2026-10, Awwwards tagovi)
- Rizik: za čitače ekrana i "End" taster treba pažljivo. Nije obavezan za naš projekat.

### T6. Urednička numeracija i oznake poglavlja
- Primeri: /zeroz (poglavlja 1–5, oznake "( About / Concept )"), CoffeeTech ("(01)", "01"), SŌM (sitne verzalne oznake sa velikim razmakom iznad naslova). (2026-10, HTML)
- Za nas: "poglavlje = jedna radnja proizvoda" (mlin, kuvalo, šolja), brojevi 01–03 kao navigacija.

### T7. Ručno crtani / ilustrovani sloj uz 3D ili fotografiju
- Primeri: More Nutrition (SVG potpisi i strelice sa "wiggle"), Santioni (stripski mastilo-svet), Best Bean Best Cup (tag Art & Illustration), Little Amps Coffee (tag Illustration). (2026-10, Awwwards + HTML)
- Efekat: toplina i karakter kad je 3D render previše "hladan". Dobro za kafu (rukom pisana poreklo / visina / godina berbe).

### T8. Podnožje kao završna scena
- Primeri: Sunbeam (3D bagel pada u podnožju), Seasats ("Footer Design" tag), NewmixCoffee (footer animacija), SŌM (Footer istaknut). (2026-10, Awwwards)
- Za nas: zrna padaju / para se diže u podnožju, uz jasan kontakt i radno vreme iznad. Kontakt i adresa moraju ostati običan tekst (SEO, pristupačnost).

### T9. Paleta izvedena iz pakovanja ili ukusa
- Primeri: More Nutrition (#90b96d, #335c30 iz pakovanja), Vibe (#DB98F9 / #FFF1E7 sa limenke), SŌM (#FF3A1F), CoffeeTech (#0D0E13 + terakota #C8603D). (2026-10, Awwwards + share-kartice)
- Za nas: boju pozadine uzeti iz papira i etikete pakovanja, ne obrnuto, i menjati je po sekciji.

## 2. Zapažanja (1 do 2 primera, još nisu trend)

- **Ogromna reč iza proizvoda.** Potvrđeno na 1 sajtu: Vibe (reč "Vibe Vibe" iza limenke, limenka preseca slova, share-kartica + DOM: `vibe-spin__text` iza canvasa). Delimično: /zeroz (krupne latinične reči u hero-u, preklapanje nije proverljivo bez browsera). Po našem pravilu još nije trend. Tehnički je jednostavno: reč u HTML-u iza canvasa sa PNG/WebP alfa kanalom (sekvenca mora biti renderovana sa providnom pozadinom). Preporuka (mišljenje): `font-size: clamp()` u `vw`, `aria-hidden="true"`, kontrast reči prema pozadini mekan, a proizvod ima jasnu senku. (2026-10, share-kartica + HTML)
- **Tečnost koja preplavi ekran.** U uzorku 2026. nema potvrđenog primera. Najbliže: Matcha Cartel ("Matcha Pouring Scroll Video" i prelaz "Matcha Obsession", Awwwards elementi, mehanizam nije potvrđen), UND NY ("Page Transition by Content Color", Awwwards element), Victor Sin ("liquid effect", WebGL shaderi i simulacija fluida, samo oznaka u Awwwards inspiration listi, nije otvoreno). Preporuka (mišljenje, nije izvor): nemojte 3D simulaciju preko celog ekrana. Opcije po ceni: (1) CSS/SVG maska sa `clip-path` ili SVG filter (`feTurbulence` + `feDisplacementMap`) za "tečan rub", (2) kratka unapred renderovana providna sekvenca u pola rezolucije, (3) WebGL shader (traži bezbednosnu proveru ako se uvozi biblioteka). (2026-10, Awwwards)
- **Dve struje display slova.** Izražajni debeli serif: Vibe (zaobljeni), Sunbeam (slab), Santioni (display serif sa preklapanjem slova). Krupni grotesk: More Nutrition, CoffeeTech, SŌM. Za specialty kafu oba rade, serif daje toplinu, grotesk preciznost. (2026-10, share-kartice)

## 3. Izbegavati / oprez

- **Obavezni dugi preloader.** Skoro svaki sajt iz uzorka ga ima (CIAO "0%", More Nutrition, Vibe, Matcha Cartel sa lozinkom, SŌM, CoffeeTech, Santioni "Opening"), pa je prešao u standard, ali skriva težinu stranice. Mišljenje: preloader samo dok stvarno stiže prvi kadar sekvence, bez lažnog brojača. (2026-10, Awwwards + HTML)
- **Varanje alata za merenje.** CoffeeTech služi lakšu stranu kad prepozna Lighthouse/PageSpeed. Ne kopirati. (2026-10, pročitano kao tekst)
- **Ne oslanjati se na pregovaranje formata na CDN-u.** Vibe: isti kadar kao WebP 34–52 KB, a kao PNG 360–600 KB zavisno od `Accept` zaglavlja. Servirati format eksplicitno (`<picture>` ili ime fajla). (2026-10, merenje)
- **Sekvence samo u AVIF-u.** MDN: AVIF ima bolju kompresiju od WebP-a (medijana 50 % naspram 30 % u odnosu na JPEG) ali nema progresivno prikazivanje. Brzina dekodiranja na telefonu: izvori se ne slažu, **NEPROVERENO**. Dok se ne izmeri na ciljnom telefonu, WebP je podrazumevani za sekvencu, AVIF za mirne slike. (2026-10, MDN + pretraga)
- **Sve u WebGL-u bez rezerve.** CIAO ENERGY ima najnižu Responsive ocenu u uzorku (7,20). Uvek planirati statičnu sliku i `prefers-reduced-motion` granu. (2026-07, Awwwards)
- **Smooth-scroll koji menja skrol kontejner.** Vibe u komentaru piše da je tema skrolovala unutrašnji kontejner (`.page-wrapper`), pa `IntersectionObserver` nije radio dok nisu prešli na merenje pozicije. Naša pouka: jedan skrol kontejner (dokument), ništa unutra. (2026-10, HTML sajta)
- **"Izlizano":** nema dovoljno dokaza za ovaj prolaz. Sledeći prolaz: uporediti sa Awwwards arhivom 2024. do 2025. za iste tagove.

## 4. Tehnika browsera (podrška, datum, da li sme)

| Mogućnost | Podrška | Sme li? | Rezerva |
|---|---|---|---|
| **CSS scroll-driven animations** (`animation-timeline: scroll()` / `view()`, `animation-range`) | Chrome i Edge 115, Safari 26, Firefox 159 | **Da, kao poboljšanje.** | `@supports (animation-timeline: scroll())`; bez podrške stranica mora da izgleda potpuno u mirnom stanju |
| **View Transitions, isti dokument** (`document.startViewTransition`) | Chrome i Edge 111, Safari 18.0, Firefox 144; 92,9 % globalno | **Da.** | `if (!document.startViewTransition) { direktno promeni stanje }` |
| **View Transitions, između stranica** (`@view-transition { navigation: auto }`) | Chrome i Edge 126, Safari 18.2, **Firefox ne** | **Da, uz rezervu.** | u Firefox-u klasična navigacija bez animacije; prelaz nikad ne sme biti jedini nosilac informacije |
| **WebCodecs `VideoDecoder`** | Chrome 94, Firefox 130, Safari 16.4 | Moguće, ali traži biblioteku za razdvajanje MP4 | bezbednost mora da odobri biblioteku; rezerva je WebP sekvenca |
| **WebCodecs `ImageDecoder`** | Chrome 94, Firefox 133, Safari samo "preview" | **Ne.** | koristiti `Image` + `decode()` |
| **WebP / AVIF** | WebP 97,08 %, AVIF 96,33 % (AVIF: Chrome 85, Firefox 93 slike, Safari 16.4, iOS 16.0 samo mirne slike) | WebP da; AVIF za mirne slike uz `<picture>` | JPEG ili PNG kao `<img src>` |

Detalji i izvori:
- **Scroll-driven animations.** MDN browser-compat-data (`animation-timeline`, `animation-range`): Chrome 115, Safari 26, Firefox 159, status standard-track, nije eksperimentalno. Chrome/Edge 115 je od 2023-07. Safari 26.0 je izašao 2025-09-15 (WebKit blog). **Firefox 159 izlazi 2026-10-27**, a sada je Beta u kojoj su scroll-driven animations "enabled by default" (MDN, beleške o izdanju Firefox 159, ažurirano 2026-10-22; datum izlaska sa whattrainisitnow.com). Dakle, od 4 dana sva tri velika engine-a imaju podršku, ali starije verzije i iPhone-i koji ne mogu na iOS 26 nemaju. Da li je to već "Baseline", proveriti na MDN-u posle 2026-10-27. (2026-10, MDN BCD + WebKit + Mozilla)
- **Ograničenje:** CSS animira CSS svojstva, **ne može da postavi indeks kadra u canvasu**. Za sekvencu i dalje treba JS (GSAP ScrollTrigger ili sopstveni `requestAnimationFrame`). CSS dobro radi za: sporiji parallax velike reči, `clip-path` otkrivanje, `opacity` i `transform` kartica, traku napretka. Chrome dokumentacija (2023-05) preporučuje `transform`, `opacity`, `clip-path`; `animation-duration` mora biti `auto`; `animation-timeline` se piše posle `animation` skraćenice. Savet o `prefers-reduced-motion` dokumentacija ne daje, to je naše pravilo: celu skrol-animaciju staviti u `@media (prefers-reduced-motion: no-preference)`. (2026-10, MDN + developer.chrome.com)
- **View Transitions.** caniuse: isti dokument Chrome/Edge 111, Safari 18.0, Firefox 144 (143 samo preko flag-a u Nightly), globalno 92,9 % (statistika StatCounter, septembar 2026). Između stranica: MDN BCD `@view-transition` Chrome 126, Safari 18.2, Firefox nije implementirano (Bugzilla 1860854). Shopify teme već isporučuju `view-transitions.js` (viđeno na Vibe). (2026-10, caniuse + MDN BCD + HTML)
- **Slike.** caniuse WebP 97,08 % (Chrome 32, Firefox 65, Safari 16.0); AVIF 96,33 %. MDN: WebP lossy je u proseku 25–35 % manji od JPEG-a; AVIF još manji ali bez progresivnog prikaza. Maksimalna dimenzija WebP-a 16.383 px. (2026-09, caniuse + MDN)
- **iOS Safari memorija za canvas.** WebKit upozorenje "Total canvas memory use exceeds the maximum limit (384 MB)"; stvarna granica zavisi od uređaja i verzije iOS-a (u prijavama od 224 do 384 MB), **tačan broj NEPROVERENO**. Pravilo: jedan canvas po sekvenci, bez novih canvas-a po kadru. (2026-10, WebKit Bugzilla 195325 i 190280)

## 5. Šta ovo znači za projekte

- **Kafa projekat (skrol sa 3D proizvodima):** Blender sekvence na sticky canvas-u su glavni tok savremenih sajtova, nema potrebe za Three.js. Ogromna reč iza proizvoda i prelaz tečnošću rešavaju se u CSS/SVG-u i providnim sekvencama, ne u 3D-u.
- **Freiraum premium:** već ima `Seq` + `Player` (WebP kadrovi na canvas-u, `d`/`m` setovi). Moguće dopune: učitavanje po blizini sekcije (kao Vibe), jedan kadar za reduced-motion.
- **RealEstates:** GSAP 3.15 i Lenis 1.3.27 su aktuelni. CSS scroll-driven animations mogu zameniti deo ScrollTrigger-a za jednostavne efekte posle 2026-10-27, ali ne treba menjati radni kod bez razloga.
- **DON'S:** bez promene.

## Arhiva

- Pretpostavka "GSAP dodaci (SplitText, ScrollTrigger) se plaćaju" više ne važi: gsap.com 2026 navodi da je GSAP besplatan za sve. (2026-10, gsap.com)
