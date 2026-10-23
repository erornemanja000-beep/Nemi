# Plan izrade: Kafa skrol (`KafaSkrol/`)

Planer, 23.10.2026. Faze 5 (izrada) i 6 (kontrola). Korisnik je odobrio dizajn i besplatan plan fotorealizma (`fotorealizam.md`). Odluke direktora iz zadatka važe i ne menjaju se.

Na čemu se plan zasniva:
- `CLAUDE.md`;
- iz `studio/kafa-skrol/`: `analiza-videa.md`, `brief.md`, `tekstovi.md`, `skice/` (`mapa-skrola.md` i PNG skice), `storyboard.md`, `dizajn/` (`dizajn.md`, `tokens.css`, `mockup.html`, oba PNG-a), `fotorealizam.md`, `dijagnoza-3d.md`, `stock-video.md`, `fotografije.md`;
- iz `studio/znanje/`: `izvori-i-licence.md`, `trendovi.md`, `ai-alati.md` delovi B i C. Sve je provereno 2026-10-23, pa `trend-skaut` i `trziste` ne trebaju;
- `RealEstates/` (verzije iz `package-lock.json`, `src/lib/motion.ts`, `useReducedMotion.ts`, `i18n/`, `scripts/shots.mjs`);
- `freiraum-premium/src/assets/premium.js` (`Seq`, `Player`, `loadSeq`, format `seq.json`).

## Cilj
Napraviti `KafaSkrol/`: pravi skrol-sajt koncepta „POUR / PLAY" (GRIND → POUR → SIP, zatim prodavnica, pretplata, O nama, Brew guide, Kontakt i footer), na Vite + React + TS + Tailwind v4 + GSAP/ScrollTrigger + Lenis.

Kod mora da radi odmah, sa privremenim kadrovima. Blender renderi i stock mediji ulaze kasnije bez izmene koda: zameni se folder u `public/media/` i zastavica u `src/content/media.ts`. Sajt se objavljuje kao poseban Netlify sajt sa `noindex` i oznakom „Konzept / Demo".

## Interfejsi i dogovori (važe za sve zadatke)

### 1. Koji izvor važi kad se izvori razlikuju
- **Tekst:** `tekstovi.md` i dopune iz Z3. Tekstovi u `mockup.html` su privremeni (meni „Kurse/Zubehör", reč „Pourover", „Huila Nordhang", DE tekst GRIND).
- **Izgled poglavlja, headera i staklene kartice:** `mockup.html` + `tokens.css` + `dizajn.md`.
- **Sekcije ispod priče:** raspored iz `skice/skica.html`, `skica-1440.png` i `skica-390.png`, a boje, slova i razmaci iz tokena. Za te sekcije mockup ne postoji (otvoreno pitanje 9).
- **Tempo, broj kadrova, šav GRIND/POUR, talas, učitavanje:** `storyboard.md`. Noviji je od `mapa-skrola.md`. `--pin-length: 420vh` iz tokena se ne koristi.
- **Reduced motion, telefon, pojavljivanje sekcija:** `mapa-skrola.md`, gde se ne kosi sa storyboard-om.
- **Prelomna tačka priče:** desktop je od 64rem (1024 px) širine i 600 px visine (kao `dizajn.md`). Sve ispod toga je telefonski raspored.

### 2. Vremenska osa priče
U kodu postoji samo jedan izvor brojeva: `KafaSkrol/src/story/timeline.ts`.

| Segment | Desktop (vh) | Telefon (svh) | Kadrovi |
|---|---|---|---|
| GRIND zakačen | 0–200 | 0–150 | G1–G64 |
| Prelaz 1 (šav) | 200–300 | 150–250 | G65–G96, GRIND i POUR istovremeno |
| POUR zakačen | 300–540 | 250–430 | G97–G176 |
| Talas | 540–640 | 430–510 | G177–G192 + S1–S16 |
| SIP zakačen | 640–790 | 510–610 | S17–S64 |
| posle priče | od 790 | od 610 | prodavnica |

Događaji vezani za ovu osu:
- kartice SIP uleću na 45–80 % SIP opsega (540–790 vh);
- para u POUR počinje od G124, a u SIP od S20;
- kartice na telefonu se samo pojavljuju.

### 3. Mediji u `KafaSkrol/public/media/`
Putanje su fiksne. Kod ih čita samo preko `src/content/media.ts`.

| Folder | Ko ga puni | Kada | Sadržaj i ograničenja |
|---|---|---|---|
| `seq/grind`, `seq/pour`, `seq/sip` | Z2 (privremeni kadrovi), kasnije `mediji` (renderi) | talas 1, zatim talas 4 | Nivoi `l/` (1600, opciono), `d/` (1200) i `m/` (800). Fajlovi `0001.webp`… i `seq.json` (tačka 4). Poster GRIND je uvek `d/0001.webp` i `m/0001.webp` (= G1), jer ga `index.html` predučitava. Pour ima `poster-d.webp` i `poster-m.webp` (G150). Sip ima poster d = `d/0064.webp` i `poster-m.webp` (S64). Budžet po kadru (storyboard 8): GRIND ≤ 75 KB d i ≤ 40 KB m; POUR ≤ 80 / 42; SIP ≤ 60 / 28. |
| `steam/` | `mediji` (radi paralelno) | talasi 1–3 | `steam-d.mp4` (oko 720×1280) i `steam-m.mp4` (oko 480×854). Jedan uspravan pramen pare na **čistoj crnoj** (crna stegnuta na ≤ 2/255, inače `screen` ostavlja sivu koprenu). Petlja bez šava, 6–10 s. H.264 yuv420p, `-an`, faststart. d ≤ 2 MB, m ≤ 0,8 MB. Samo klip sa Free licencom, uz unos u `studio/kafa-skrol/izvori.md`. |
| `photos/` | `mediji` (radi paralelno) | talasi 1–3 | Sedam fotografija iz `fotografije.md`: SHOP-1, ONAMA-1, ONAMA-2, GUIDE-1, GUIDE-2, KONTAKT-1, KONTAKT-2. Imena `<id>-sm.webp` i `<id>-lg.webp` (`shop-1-sm.webp`…). Širine: položene 828 i 1920 px, uspravne 480 i 900 px; kvalitet 75–82. Brew guide korak 3 koristi SIP poster. Opciono `gear-{grinder,dripper,kettle}-{sm,lg}.webp` (mirni Blender snimci opreme, vidi ispod). |
| `bags/` | `mediji` iz Blender rendera | talas 4 | `kesa-{origin,flavor,roast}-{400,600,900}.webp` (storyboard 6; 400 telefon, 600 kartica, 900 prodavnica). |

**Šta očekujem od `blender-umetnik`:**
- kadrovi po storyboard-u: G1–G96 GRIND (1600×2000), G65–G192 POUR (1600²), S1–S64 SIP;
- uz svaku sekvencu `anchors.json` sa sidrima iz tačke 4, u jedinicama S;
- tri postera i tri kese 1200×1500 sa etiketom iz Z4;
- opciono tri mirna snimka opreme (mlin, dripper sa bokalom, kuvalo) za prodavnicu. Ako ih nema, kartica opreme koristi CSS siluetu.

**Šta očekujem od `mediji`:**
- pakovanje u tačno ove putanje i budžete;
- WebP podešavanja iz storyboard-a 8 (q 62–70, `alpha_quality` 90, method 6, Lanczos);
- `seq.json` po tački 4;
- manifest `studio/kafa-skrol/izvori.md` (URL, autor, licenca, datum, sha256) za svaki stock fajl;
- izveštaj sa dimenzijama i KB po fajlu.

Sirovi fajlovi ostaju u `studio/kafa-skrol/izvori/` (gitignored).

### 4. Format `seq.json`
Proširuje format iz `freiraum-premium`. Sve dužine i sidra su u jedinicama **S**, gde je S stranica kvadrata kadra. Koordinate se mere od gornjeg levog ugla punog kadra.

| Polje | Primer (grind) | Značenje |
|---|---|---|
| `id` | `grind` | isto kao ime foldera |
| `version`, `placeholder` | `placeholder-1`, `true` | `placeholder: false` znači pravi render. Z2 ne sme da ga prepiše. |
| `clock` | `G` | `grind` i `pour` dele sat G, a `sip` ima svoj sat S |
| `g_od`, `g_do` | 1, 96 | globalni kadrovi koje sekvenca pokriva (pour 65–192, sip 1–64) |
| `fps` | 30 | samo informacija |
| `full` | W 1, H 1,25 | pun kadar (pour i sip: 1 × 1) |
| `crop` | x0 0,22, y0 0, w 0,56, h 1,25 | isečak u fajlovima (pour: 0,26 / 0 / 0,72 / 1; sip: po probi) |
| `sets.l`, `sets.d`, `sets.m` | d: px 1200, w 672, h 1500, count 96, every 1; m: px 800, w 448, h 1000, count 48, every 2 | `px` = pikseli za S. Fajl `k` (od 1) prikazuje globalni kadar `g_od + (k−1)·every`. Bez `l` se koristi `d`. |
| `poster` | d `d/0001.webp`, m `m/0001.webp` | relativne putanje, po nivou |
| `steps` | pin 1–64, prelaz 65–96 | pour: prelaz 65–96, pin 97–176, talas 177–192; sip: talas 1–16, pin 17–64 |
| `anchors` | `otvor` x 0,5, y 0,84 | pour: `ivica_v60` (x, y, rx, ry: 0,5 / 0,47 / ≈0,128 / ≈0,03), `pult_y` 0,95, `kafa_y` (od G177, 16 vrednosti); sip: `sto_y`; svuda `osa_x` 0,5 |

### 5. `src/lib/sequence.ts` i `src/story/SeqCanvas.tsx`
Piše Z5, koristi Z12.

**`loadManifest(id)`**
- Čita `/media/seq/<id>/seq.json` i proverava obavezna polja.
- Kad ne uspe, vraća „nema" i piše `console.warn`, nikad `console.error`.

**`pickSet(manifest, …)`**
- Telefon: `m`.
- Desktop: `l` ako S u CSS px × min(DPR, 2) > 1250 i `l` postoji. Inače `d`.

**`createSequence(manifest, set)`**
- `url(g)`, `has(g)`, `isReady(g)`, `nearestReady(g)`;
- zahtevi: lista, raspon ili „svaki n-ti";
- `retain(g, 24)`: dekodirano najviše ±24 kadra oko trenutnog (ImageBitmap + `close()`), a ostali stoje kao komprimovani Blob;
- `dispose()`.

**Zajednički red učitavanja:** najviše 6 paralelnih zahteva, sa prioritetima i bez duplikata.

**`createClock(sekvence)`**
- jedan cilj `g`, ublažen **jednom** (faktor 0,22 kao `Player`; u reduced motion skok);
- `frameFor(seq)`: u preklopu G65–G96 daje najbliži kadar koji je učitan u **obe** sekvence;
- `subscribe`, start i stop preko `gsap.ticker`.

**`window.__seqStats`** (samo dev ili `?debug`): po sekvenci broj zatraženih, učitanih i dekodiranih kadrova.

**`SeqCanvas`**
- Props: `seq`, `clock`, `poster` (src, alt, `priority`) i `onFirstFrame`.
- Popunjava svoju kutiju razmere `full.W : full.H` i crta isečak na mestu iz `crop`.
- DPR najviše 2, ResizeObserver, bez čitanja layout-a u petlji.
- Poster `<img>` stoji ispod platna dok se ne nacrta prvi kadar.
- Platno ima `aria-hidden`. Van ekrana se ne crta.
- Reduced motion i Save-Data: samo poster, bez zahteva za kadrove.

### 6. Komponente priče: ko šta pomera
- **Story (Z12)** pomera samo omotače sa `data-anim` (`text`, `word`, `card`, `object`) i slojeve (`.layer-grind`, `.layer-pour`, `.layer-sip`), i to samo preko `transform` i `opacity`. Komponente stavljaju svoj mirni položaj i nagib na **unutrašnji** element.
- **`Wave` (Z6):**
  - imperativni handle `set(progress 0–1, startY u px viewporta)`;
  - props `pourClip` i `sipLens` (ref-ovi) i `variant` (`desktop`/`phone`);
  - menja samo `clip-path` na `pourClip` (unutrašnji `.layer-pour__clip`) i `transform`/`filter` na `sipLens` (`.layer-sip__lens`);
  - drugi izvoz je `WaveEdgeStatic` za reduced motion.
- **`Steam` (Z6):**
  - props `which` (`pour`/`sip`), `active`, `className`;
  - pušta video samo kad je aktivan, vidljiv, nije reduced, nije Save-Data i kad je medij `ready`;
  - opacity menja Story na omotaču.
- **`chapterStore` (Z1):**
  - `setActiveChapter` i `useActiveChapter`, sa vrednostima `grind`/`pour`/`sip`/`page`;
  - `registerChapterNavigator` i `goToChapter`;
  - u dev-u `window.__chapter`.
- **`--table-y`:** CSS promenljivu (položaj pulta ili stola) postavlja Story na sloj iz `pult_y`/`sto_y`. `SceneBackdrop` je čita, a bez nje koristi vrednost iz mockupa.
- **Raspored sloja:** sloj je `position: relative` blok visine sloja sa `data-chapter`. Delovi iz Z7 se pozicioniraju apsolutno unutar njega.

### 7. Sadržaj (`src/content/*.ts`) i brend
- Dvojezična polja su `L<T>` (`en`, `de`). Cene su u **centima**. Grundpreis se uvek računa (cena / grami × 1000), nikad se ne upisuje.
- Sadržaj je čist podatak: bez JSX-a, bez `window`-a, bez uvoza slika. `vite.config.ts` ga uvozi za `<noscript>`.
- Ime brenda, e-mail adrese i demo telefon postoje **samo** u `src/config/site.ts`. U tekstovima stoje oznake `{brand}`, `{email}`, `{wholesale}` i `{phone}`, a menja ih `fill()`.
- Provera u svakom zadatku: `grep -rn "POUR / PLAY\|pourplay" KafaSkrol --exclude-dir=node_modules --exclude-dir=dist` nalazi samo `src/config/site.ts` (i `public/licenses` ako se tamo pojavi).
- Naslovi se ne pišu velikim slovima u podacima, nego preko CSS-a (`tekstovi.md`). Nelomljivi razmak ide po pravilima iz `tekstovi.md`.

### 8. Rute, sidra i stanje
- **Rute (BrowserRouter):**
  - `/`, `/p/:slug` (modal proizvoda preko početne);
  - `/impressum`, `/datenschutz`, `/agb`, `/versand`, `/widerruf`, `/cookies`, `/credits`;
  - samo u dev-u `/dev/seq`, `/dev/wave`, `/dev/chapters`.
  - Netlify vraća `index.html` za sve (SPA preusmerenje). HashRouter se ne koristi, da bi sidra u meniju radila kao obični linkovi.
- **ID-jevi sekcija** (kao u skici):
  - priča: `#top`, `#grind`, `#pour`, `#sip`;
  - ispod nje: `#find-your-cup`, `#subscription` (unutra `#tasting-set`), `#about`, `#brew-guide`, `#contact`, `#footer`;
  - ostalo: `main#main`.
- **Meni** (`tekstovi.md`): Coffee → `#find-your-cup`, Subscription → `#subscription`, Brew guide → `#brew-guide`, About → `#about`, Visit → `#contact`. Dugme „Shop now" vodi na `#find-your-cup`.
- **Filter iz linka:** prodavnica čita `?brew=filter|espresso` iz URL-a pri učitavanju. Dugme Brew guide-a vodi na `/?brew=filter#find-your-cup`.
- **localStorage:** `kafa-lang` i `kafa-cart`. Kolačića nema.
- **`cart.ts`:** `addToCart(slug, grams, grind)`, `setQty`, `removeLine`, `useCart()` (stavke, broj, međuzbir, dostava, do besplatne dostave, ukupno, sve u centima), `openCart`/`closeCart`. Dostava u Austriji je € 4,50 ispod € 45, a od € 45 (uključivo) besplatna. `addToCart` sam prikazuje toast.

### 9. Pravila za sve zadatke izrade
- Menjaš samo fajlove iz svog zadatka. Ako ti treba izmena zajedničkog fajla (`src/content/types.ts`, `src/App.tsx`, `src/pages/Home.tsx`, `src/index.css`, `src/config/site.ts`, `vite.config.ts`, `index.html`, `netlify.toml`), napiši je u izveštaj. Direktor ih skuplja za Z13.
- Bez novih paketa. Paketi su samo oni iz Z1.
- CSS: prvo Tailwind klase. Ako ne može, sopstveni CSS fajl zadatka. `src/index.css` posle Z1 ne dira niko osim Z13.
- Animira se samo `transform` i `opacity`, a važe tokeni trajanja i easing-a. Bez `innerHTML` i `dangerouslySetInnerHTML`. Bez spoljnih URL-ova u vreme rada (fontovi i mediji su lokalni).
- Svaki zadatak koda završava se sa `cd KafaSkrol && npm run build && npm run lint`, na 390, na 1440 i sa reduced motion, bez grešaka u konzoli. Privremeni snimci i skripte idu u `mktemp -d`. Nema commit-a.

## Talas 1 (paralelno)

### Z1: Kostur projekta i zajednički temelji → programer
Fajlovi:
- `KafaSkrol/package.json`, `package-lock.json`, `index.html`, `vite.config.ts`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `.oxlintrc.json`, `.gitignore`, `netlify.toml`, `README.md`;
- `KafaSkrol/public/favicon.svg`, `KafaSkrol/public/licenses/OFL-Archivo.txt`, `OFL-Fraunces.txt`, `OFL-Figtree.txt`;
- `KafaSkrol/scripts/check-data.ts`, `KafaSkrol/scripts/shots.mjs`;
- `KafaSkrol/src/main.tsx`, `src/App.tsx`, `src/index.css`, `src/styles/tokens.css`, `src/styles/fonts.css`;
- `src/assets/fonts/` (`fraunces-latin-full-normal.woff2`, `fraunces-latin-ext-full-normal.woff2`, `figtree-latin-wght-normal.woff2`, `figtree-latin-ext-wght-normal.woff2`);
- `src/config/site.ts`, `src/i18n/LangContext.tsx`, `src/content/types.ts`;
- `src/lib/motion.ts`, `src/lib/useMedia.ts`, `src/lib/format.ts`, `src/lib/reveal.ts`, `src/lib/chapterStore.ts`;
- `src/components/Button.tsx`, `Icon.tsx`, `Price.tsx`, `Photo.tsx`;
- `src/pages/Home.tsx`;
- **stubovi**, u kojima posle radi drugi zadatak:
  - sadržaj: `src/content/site.ts`, `chapters.ts`, `products.ts`, `shop.ts`, `sections.ts`, `legal.ts`, `media.ts`;
  - `src/lib/cart.ts`;
  - komponente: `src/components/Header.tsx`, `MobileMenu.tsx`, `SearchPanel.tsx`, `CartDrawer.tsx`, `Toast.tsx`, `ChatBubble.tsx`, `LangSwitch.tsx`, `ProductCard.tsx`, `Grain.tsx`;
  - sekcije: `src/sections/Shop.tsx`, `Subscription.tsx`, `About.tsx`, `BrewGuide.tsx`, `Contact.tsx`, `Footer.tsx`;
  - priča: `src/story/Story.tsx`, `ChapterText.tsx`, `BackWord.tsx`, `ChapterNav.tsx`, `SipCards.tsx`, `Sparkle.tsx`, `SceneBackdrop.tsx`;
  - stranice: `src/pages/ProductModal.tsx`, `Legal.tsx`, `Credits.tsx`, `DevSeq.tsx`, `DevWave.tsx`, `DevChapters.tsx`.

Uradi:
1. **Paketi.** Tačne verzije iz `RealEstates/package-lock.json`, bez `^`:
   - `react` i `react-dom` 19.3.1, `react-router-dom` 7.18.4, `gsap` 3.15.0, `lenis` 1.3.27, `@fontsource-variable/archivo` 5.3.0;
   - dev: `vite` 8.3.5, `@vitejs/plugin-react` 6.1.2, `tailwindcss` i `@tailwindcss/vite` 4.3.3, `typescript` 6.0.3, `oxlint` 1.89.0, `@types/react` 19.3.0, `@types/react-dom` 19.3.0, `@types/node` 24.19.2, `playwright` 1.64.1.
   - Bez three, R3F, sharp i drugih fontova.
   - Instalacija: `npm install --ignore-scripts` u `KafaSkrol/`. Ako nešto ne radi bez install skripte, javi direktoru (ide preko `bezbednost`).
   - Skripte: `dev`, `build` (`tsc -b && vite build`), `lint` (`oxlint`), `preview`, `check` (`node --experimental-strip-types scripts/check-data.ts`).
2. **`vite.config.ts`** (kao RealEstates):
   - `base: '/'` i `manualChunks` za gsap i lenis;
   - mali ugrađeni plugin koji u `index.html` upisuje ime brenda i SEO (EN) iz `site.ts` i `site` sadržaja, i pravi `<noscript>` (skriven H1, tri naslova i teksta poglavlja na EN, GRIND poster `<img>`, red „Concept / demo");
   - `preview.headers` sa istim CSP-om i `X-Robots-Tag` kao `netlify.toml`, uz komentar „uskladiti sa netlify.toml";
   - `tsc -b` mora da prođe i sa uvozom sadržaja u config (bez DOM tipova u sadržaju).
3. **`index.html`:**
   - `lang="en"`, `viewport-fit=cover`, `<meta name="robots" content="noindex, nofollow">`, `theme-color` `#E6DDCE`, favicon;
   - predučitavanje postera sa `fetchpriority="high"`: `/media/seq/grind/d/0001.webp` za `(min-width: 64rem) and (min-height: 600px)` i `/media/seq/grind/m/0001.webp` za ostalo;
   - ime brenda ne piše ručno, upisuje ga plugin.
4. **Fontovi.**
   - Fraunces i Figtree kopiraj iz `sajt/src/assets/fonts/` i napiši `@font-face` sa `unicode-range` kao u `mockup.html`.
   - Archivo uvezi iz paketa preko CSS fajla koji ima osu `wdth`. Proveri ime fajla u `node_modules/@fontsource-variable/archivo/`.
   - Fontsource familija se zove „Archivo Variable". U kopiji `src/styles/tokens.css` promeni **samo** prvo ime u `--font-display` (uz komentar). Ostatak tokena ostaje identičan dizajnerskom fajlu.
   - Licence iskopiraj u `public/licenses/`.
5. **`src/index.css`:**
   - Tailwind, tokeni i fontovi;
   - `@theme inline` sa ulogama (bg, surface, text, muted, accent, line, word, btn) i fontovima, da utility klase prate `[data-chapter]`;
   - osnovni stilovi iz `mockup.html` (body, `.sr-only`, fokus, skip link, blok za reduced motion);
   - Lenis klase kao u RealEstates i klase za `reveal.ts`.
6. **`site.ts`:**
   - brend: ime, podnaslov `L`, e-mail adrese, demo telefon i `fill()`;
   - `features` (`smoothScroll: true`, `grain: true`);
   - ključevi za localStorage.
7. **`LangContext`** (kao RealEstates): podrazumevano EN, `tx(L)`. Pri promeni jezika menja `<html lang>`, `document.title` i meta description.
8. **`motion.ts`** (iz RealEstates):
   - Lenis samo kad je `features.smoothScroll` uključen, pokazivač je precizan (miš) i nije reduced motion; sa `anchors: true`;
   - `scrollToTarget`, `lockScroll`;
   - `ScrollTrigger.refresh()` posle `document.fonts.ready`.
9. **`useMedia.ts`:** `useReducedMotion`, `useIsPhone` (konstanta upita iz tačke 1 Interfejsa), `useFinePointer`, `useSaveData`.
10. **`format.ts`:** cena, Grundpreis, grami, visina, datum, `lastRoastDate` (poslednji utorak ili petak ≤ danas, Europe/Vienna) i `bestBefore` (vraća „nema" dok korisnik ne odluči). Izlazi su tačno kao u `tekstovi.md`.
11. **`reveal.ts`:** IntersectionObserver hook za pojavljivanje (fade + 16 px, razmak 60 ms). U reduced motion je sve odmah vidljivo.
12. **`chapterStore.ts`:** po tački 6 Interfejsa.
13. **`types.ts`:** `L`, `Lang`, `ChapterId`, `Chapter`, `SipCard`, `Product` (vrsta coffee/gear/set, polja iz kartice proizvoda u `tekstovi.md`, `sizes` sa gramima i centima, `priceCents` sme da bude prazno, grupe za filtere `brew`/`flavor`/`roastGroups`/`type`, ključ slike), `PhotoEntry`, `MediaManifest`, `LegalPage`.
14. **Zajedničke komponente:**
    - `Button`: pilula, obris za header i okruglo dugme, kao u `mockup.html`;
    - `Icon`: SVG ikonice iz mockupa;
    - `Price`: cena i Grundpreis u istom redu, uz napomenu o PDV-u;
    - `Photo`: `<img srcset sizes>` sa width i height, lazy. Kad je `ready: false`, prikazuje obojenu kutiju iste razmere.
15. **`App.tsx`:** rute iz tačke 8 (dev rute učitane lenjo, samo u `import.meta.env.DEV`). Globalno: `Header`, `ChatBubble`, `CartDrawer`, `Toast`, `Grain` i start smooth scroll-a.
16. **`Home.tsx`:** skriven H1 iz sadržaja, pa redom Story, Shop, Subscription, About, BrewGuide, Contact, Footer.
17. **Stubovi:** svaki izvozi konačno ime i props iz Interfejsa i prikazuje minimalan sadržaj (sekcija sa svojim id-jem i naslovom). Story stub prikazuje tri statična bloka od 100vh sa posterima. Sadržaj stubova: jedna kafa (Guji), jedna oprema (kuvalo, € 169), sva tri poglavlja, minimalan `site`, i `media` sa putanjama sekvenci i postera, a ostalo `ready: false`.
18. **`netlify.toml`:**
    - build `npm run build`, publish `dist`, okruženje `NODE_VERSION = "22"` i `NPM_FLAGS = "--ignore-scripts"`;
    - SPA preusmerenje na `/index.html` sa 200;
    - zaglavlja za `/*`: `X-Robots-Tag: noindex, nofollow, noarchive`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (camera, microphone, geolocation isključeni);
    - CSP: `default-src 'self'`, `script-src 'self'`, `style-src 'self'`, `img-src 'self' data: blob:`, `media-src 'self' blob:`, `font-src 'self'`, `connect-src 'self'`, `object-src 'none'`, `base-uri 'self'`, `form-action 'self'`, `frame-ancestors 'none'`. Ako `style-src 'self'` izazove greške u konzoli, javi; `'unsafe-inline'` dodaje tek `bezbednost`;
    - keš: `/assets/*` godinu dana `immutable`, a `/media/*` jedan dan (kao root `netlify.toml`).
19. **README:** pokretanje, build, objava (poseban Netlify sajt, base `KafaSkrol`), mapa foldera, kako se menjaju renderi (folder + `seq.json`, pa zastavice u `media.ts`), gde se menja brend i napomena „Konzept / Demo".
20. **Ostalo:**
    - `check-data.ts` proverava `format.ts` na primerima ispod;
    - `shots.mjs` je prilagođen iz RealEstates (ID-jevi sekcija iz tačke 8, `--reduced`, greške u konzoli, neuspeli zahtevi, horizontalni skrol);
    - `favicon.svg` je zvezdica iz mockupa, bez teksta brenda.

Gotovo kad:
- `npm run build`, `npm run lint` i `npm run check` prolaze.
- `check` potvrđuje sve ove izlaze:
  - DE `€ 17,90` i `€ 71,60/kg`, EN `€17.90` i `€71.60/kg`;
  - `250 g` i `1 kg` sa nelomljivim razmakom;
  - DE `1.950–2.200 m`, EN `1,950–2,200 m`;
  - `lastRoastDate`: 23.10.2026 → 23.10.2026, 22.10.2026 → 20.10.2026, 26.10.2026 → 23.10.2026.
- `npx vite preview` na 390 i 1440: početna se prikazuje sa stubovima, bez grešaka u konzoli, a svi zahtevi su ka istom originu. Postere daje Z2; dok Z2 ne završi, 404 za postere je očekivan.
- Merenje u Playwright-u: širina „GRIND" sa `wdth` 88 je 0,85–0,92 širine sa `wdth` 100. Ako nije, osa ne radi i treba javiti.
- Grep za brend nalazi samo `site.ts`.
- `<html lang>` i naslov se menjaju sa jezikom.
- `vite preview` vraća `X-Robots-Tag`.
- `netlify.toml` se parsira sa `python3 -I -c` i `tomllib`.

### Z2: Privremeni kadrovi iza pravog interfejsa → programer
Fajlovi: `KafaSkrol/scripts/placeholder_seq.py`, `KafaSkrol/public/media/seq/grind/**`, `KafaSkrol/public/media/seq/pour/**`, `KafaSkrol/public/media/seq/sip/**`

Uradi:
1. **Skripta.** Python 3 i sistemski Pillow (dozvoljeno, jer su slike naše, ne tuđe). Opis na vrhu, putanja kao argument, `--force`.
   - Odbija da prepiše folder čiji `seq.json` ima `placeholder: false`.
   - Pravi `d` (px 1200) i `m` (px 800), bez `l`, sa brojem kadrova, isečkom, sidrima, `steps` i posterima tačno po tačkama 2–4 Interfejsa:
     - grind: d 96, m 48;
     - pour: d 128, m 64;
     - sip: d 64, m 32.
2. **Šta se crta.** Sive siluete na providnoj pozadini, oblikom i položajem kao u `mockup.html`: mlin sa levkom, kuvalo, V60 sa bokalom, šolja.
   - Mlaz je niz tačaka u **zajedničkim koordinatama sveta**: y u POUR kadru = y u GRIND kadru − 1 S, jer je POUR kamera tačno 1 S niže. Otvor je aktivan G52–G88, a rep pada do oko G110.
   - Kuvalo se naginje 12° → 32° (G110–G120) i vraća (G164–G176).
   - Nivo u bokalu raste 0 → 38 % (G136–G192), a `kafa_y` se upisuje po kadru za G177–G192.
   - Šolja se spušta S1–S14.
   - U uglu isečka je mala oznaka kadra (G084, S032) i reč PLATZHALTER.
   - WebP sa alfom, q oko 60.
3. **Posteri** po tački 3. Opcija `--composite G <putanja>` pravi PNG: GRIND kadar iznad POUR kadra, pomeren za 1 S, za proveru šava (izlaz u privremeni folder, ne u repo).

Gotovo kad:
- `python3 -I KafaSkrol/scripts/placeholder_seq.py KafaSkrol/public/media/seq` pravi tačan broj fajlova po nivou.
- Ukupno ≤ 3 MB.
- Svaki `seq.json` ima sva polja iz tačke 4.
- Drugo pokretanje daje iste fajlove.
- Kompozit G84 (pogledan sa Read) pokazuje neprekinut niz tačaka preko granice, bez skoka.

### Z3: Dopune tekstova za izradu → tekstopisac
Fajlovi: `studio/kafa-skrol/tekstovi.md`. Samo novi odeljak na kraju, „Dopune za izradu (talas 1)". Postojeći tekst se ne menja.

Uradi (sve EN i DE, činjenice samo iz briefa, inače `[FEHLT]`):
1. **Fotografije i mediji:**
   - alt tekstovi za 7 fotografija iz tačke 3;
   - natpis „Symbolbild" / „Symbolic image" za KONTAKT-1 i KONTAKT-2;
   - alt za 3 kese i 3 komada opreme.
2. **Stranica Credits:** naslov, uvod, nazivi kolona (foto, autor, izvor, licenca), red o fontovima (OFL) i red o snimku pare.
3. **Pravne stranice kao demo stub** (Impressum, Datenschutz, AGB, Versand & Zahlung, Widerrufsrecht, Cookies): naslov, uvodni red „Konzept / Demo" i spisak naslova onoga što bi stajalo u pravom projektu (iz `[FEHLT]` spiskova). Sadržaj se ne izmišlja.
   - Za Cookies: „ovaj demo ne koristi kolačiće; jezik i korpa se čuvaju samo u pregledaču (localStorage)".
   - Natpis za mesto Gewährleistungslabel-a.
4. **Nedostajući natpisi:**
   - modal: zatvori, količina, ukloni;
   - kartica: „Demo";
   - pretraga: „{n} rezultata";
   - drugi skip link: „Skip to shop" / „Zum Shop springen";
   - demo napomena za dugmad „Start a subscription" i „Give as a gift";
   - `<noscript>` red;
   - format datuma na EN.
5. **Grupe prženja za filter:** potvrditi da se Huila („Light-medium") prikazuje i pod Light i pod Medium.
6. **Provera na EUR-Lex-u** (zvaničan izvor, sa datumom): EN tekst dugmeta za porudžbinu (Direktiva 2011/83/EU, čl. 8(2)) i tekst funkcije za odustanak (Direktiva (EU) 2023/2673). Ako ostane neprovereno, ostaje oznaka NEPROVERENO.

Gotovo kad: svaka stavka ima EN i DE; uz proveru sa EUR-Lex-a stoje link i datum; nijedna nova činjenica nije izmišljena (`[FEHLT]` gde fali).

### Z4: Etiketa za kese → dizajner
Fajlovi: `studio/kafa-skrol/dizajn/etiketa.svg` (ili `etiketa.html`), `studio/kafa-skrol/dizajn/etiketa-origin.png`, `etiketa-flavor.png`, `etiketa-roast.png`, `studio/kafa-skrol/dizajn/etiketa.md`

Uradi:
- Jedna zajednička etiketa u tri boje (boje kesa iz `scripts/blender/kafa/bags.py` i storyboard-a 6, usklađene sa tokenima).
- Tekst na etiketi:
  - privremeni brend iz `tekstovi.md`;
  - „Specialty Coffee · Wien", „250 g" i mala oznaka „Demo";
  - bez imena kafe, cene, Bio/Fairtrade ili bilo kakvih sertifikata.
- Fontovi samo lokalni (Archivo, Figtree, Fraunces). Izvoz preko Chromium-a (Playwright) bez CDN-a, PNG 2048×3072 RGBA.
- Prazna zona za ventil (krug od 16 mm, gore u sredini) i za nabore.
- U `etiketa.md` stoje boje, fontovi i gde se pojavljuje ime brenda. Ako se ime promeni, kese se ponovo renderuju (oko 20 min).

Gotovo kad: tri PNG-a 2048×3072; umanjeno na 400×500 tekst se i dalje čita (pregledano sa Read); `etiketa.md` je spreman za predaju `blender-umetnik`-u preko direktora.

## Talas 2 (posle talasa 1, paralelno)

### Z5: Sekvence, zajednički sat i platno → animator
Fajlovi: `KafaSkrol/src/lib/sequence.ts` (nov), `KafaSkrol/src/story/SeqCanvas.tsx` (nov), `KafaSkrol/src/pages/DevSeq.tsx` (stub iz Z1)

Uradi:
- Sve iz tačke 5 Interfejsa. Polaziš od `Seq`, `Player` i `loadSeq` iz `freiraum-premium/src/assets/premium.js`, ali sa jednim ublažavanjem za oba platna (`premium.js` ublažava svaki Player posebno).
- Zahtev za kadar koji vraća 404 se preskače i koristi se najbliži učitani kadar.
- `DevSeq` (samo dev) je harness za proveru:
  - GRIND i POUR scena, jedna ispod druge, bez razmaka;
  - skrol je linearno vezan za G1–G192, sa prelazom kao u tački 2;
  - dev panel prikazuje G, nivo i brojače.

Gotovo kad:
- U `npm run dev` na `/dev/seq`, na 1440 i 390, postoje snimci za G1, G40, G84, G96, G150 i G192.
- Na G84 niz tačaka prelazi granicu bez skoka (≤ 2 CSS px).
- Brz skrol do dna i nazad ne daje greške u konzoli, a `__seqStats` pokazuje ≤ 49 dekodiranih po sekvenci.
- Prvi zahtevi su svaki 6. kadar GRIND-a.
- Sa `reducedMotion: 'reduce'` i sa emuliranim Save-Data traže se samo posteri.
- 1440×900 pri DPR 2 bira `d`, a telefon bira `m`.
- Presretnut 404 za jedan kadar daje samo `console.warn`.

### Z6: Talas kafe i para → animator
Fajlovi: `KafaSkrol/src/story/Wave.tsx`, `KafaSkrol/src/story/wave.css`, `KafaSkrol/src/story/Steam.tsx` (novi), `KafaSkrol/src/pages/DevWave.tsx` (stub)

Uradi:
- **Wave** (storyboard 5):
  - ivica je zbir dve sinusoide, sa fazom koja klizi;
  - tamni meniskus od 1,5 px, svetao odsjaj od 2 px i 3–5 odsjaja koji klize duž ivice;
  - ispuna je gradijent od svetle ćilibarne do tamne kafe, ~0,88;
  - traka debljine 18–35 % vh na 30–70 %;
  - kroz traku se vidi živ SIP sloj (`scale(1.04)` + ton). Na 70–100 % traka izlazi gore.
- Ugovor je u tački 6 Interfejsa. Dimenzije se pamte pri promeni veličine, a ne čitaju u petlji.
- **Boje talasa** su CSS promenljive u `wave.css`, izvedene iz palete (u tokenima ih nema). Predlog proverava `recenzent`.
- **Varijante:**
  - desktop sme da ima `feDisplacementMap` samo ako je vreme kadra u granici;
  - telefon je bez displacement-a i `backdrop-filter`-a;
  - `WaveEdgeStatic` je statična talasasta ivica za reduced motion.
- **Steam** po tački 6 Interfejsa:
  - `<video>` muted, `playsInline`, loop, `preload="none"`, `aria-hidden`, `mix-blend-mode: screen`;
  - izvori iz `media.ts` po prelomnoj tački;
  - bez `ready` ne prikazuje ništa i ne šalje zahtev.
- **DevWave** (samo dev): terakota sloj sa lažnom linijom kafe na `startY` iznad braon SIP sloja sa siluetom šolje i natpisom; skrol vodi `progress`; Steam preko obe pozadine.

Gotovo kad:
- Snimci na p = 0; 0,15; 0,3; 0,5; 0,7; 0,85; 1, na 1440 i 390, plus statična ivica u reduced motion.
- Na p = 0 ivica počinje tačno na `startY` (±2 px).
- SIP natpis se vidi kroz traku i čist je posle p = 1.
- Merenje u Playwright-u daje prosečno vreme kadra < 16,7 ms na 1440 i < 33 ms na 390 uz 4× usporen CPU (CDP).
- Bez fajlova pare nema zahteva ni 404.
- Nema grešaka u konzoli.

### Z7: Statični delovi poglavlja → programer
Fajlovi:
- `KafaSkrol/src/story/ChapterText.tsx`, `BackWord.tsx`, `ChapterNav.tsx`, `SipCards.tsx`, `Sparkle.tsx`, `SceneBackdrop.tsx`;
- `KafaSkrol/src/story/chapters.css` (nov);
- `KafaSkrol/src/components/Grain.tsx`;
- `KafaSkrol/src/pages/DevChapters.tsx`.

Uradi (položaji i mere iz `mockup.html` i `dizajn.md`, tekst iz sadržaja):
- **`ChapterText`:** eyebrow, H2 (`t-grind`, `t-pour`, `t-sip`), tekst i CTA (GRIND → `#find-your-cup`, POUR → `#brew-guide`, SIP → `#find-your-cup`). Omotač ima `data-anim="text"`.
- **`BackWord`:** `aria-hidden`. Longberry ima `--fs-word`, Percolate i Frother `--fs-word-xl`; boja `--color-word`. Frother se ne prikazuje na telefonu.
- **`ChapterNav`:** strelice od 60 px i tačkice (samo desktop), sa `aria-label` iz `tekstovi.md`. Poziva `goToChapter`. Prva strelica levo i poslednja desno su onemogućene.
- **`SipCards`:**
  - 3 staklene kartice iz `chapters.sipCards`, sa podacima o proizvodu: oznaka, podnatpis, kafa, red sa poreklom, note, `Price` sa Grundpreisom i PDV-om, „Geröstet am" iz `lastRoastDate`, čip „Demo";
  - kartica je link na `/p/<slug>` sa `aria-label` iz `tekstovi.md`, a dugme „+" poziva `addToCart`;
  - kesa preko `Photo` ili CSS kese iz mockupa;
  - omotač `data-sip-card="0|1|2"`, nagib na unutrašnjem elementu;
  - desktop: kartica 1 kao u mockupu (desno, preko drške), kartice 2–3 su predlog rasporeda oko šolje (po `analiza-videa.md`; proverava `recenzent`);
  - telefon: horizontalna traka sa scroll-snap-om ispod šolje, 3 tačkice prate traku, plus „Swipe for more";
  - `@supports` rezerva bez `backdrop-filter`-a, iz tokena.
- **`Sparkle`:** treperi 2400 ms; u reduced motion stoji.
- **`SceneBackdrop`:** svetlosni gradijent iz smera key svetla (gore levo) i traka stola na `var(--table-y)` (POUR pult; SIP pod kao `.chapter--sip` u mockupu).
- **`Grain`:** fiksni sloj, statičan SVG šum kao data-URI, 3–5 %, `overlay` na desktopu. Na telefonu izmeri da li je bez blend-a jeftinije, pa izaberi. Prati `features.grain`.
- **`DevChapters`** (samo dev): tri sloja od 100vh/100svh sa `data-chapter` i svim delovima na mestu. Gde će biti platna, stoje sive kutije: desktop po merama predmeta iz `dizajn.md`, telefon sa visinama scene 28, 30 i 31 rem. Jezik se menja preko konteksta.

Gotovo kad:
- `DevChapters` na 1440×900 i 390×844 je poređen pored `mockup-1440.png` i `mockup-390.png`: kolona teksta na ~222 px, naslov 96 i 64 px, kartica 260 i 216 px (±8 px).
- Dodirne površine su ≥ 44 px i nema horizontalnog skrola.
- DE tekst GRIND staje u ≤ 6 redova na 390.
- U reduced motion ništa ne treperi.
- Kontrast i tokeni su nepromenjeni.

### Z8: Header, meni, pretraga, korpa, chat, jezik → programer
Fajlovi: `KafaSkrol/src/components/Header.tsx`, `MobileMenu.tsx`, `SearchPanel.tsx`, `CartDrawer.tsx`, `Toast.tsx`, `ChatBubble.tsx`, `LangSwitch.tsx`, `KafaSkrol/src/components/chrome.css` (nov), `KafaSkrol/src/lib/cart.ts`

Uradi:
- **Header:** jedan fiksni header (kao `mockup.html`), sa `data-chapter` iz `useActiveChapter()` i prelazom `--dur-base`.
  - Desktop: logo (brend + podnaslov), 5 stavki menija u sredini, jezik, pilula „Shop now", pretraga i korpa sa brojem.
  - Telefon (64 px): logo, korpa i meni.
  - Tanka linija ispod posle 20 px skrola. Dva skip linka (`#main` i `#find-your-cup`).
- **MobileMenu:** dijalog sa zarobljenim fokusom i Esc. Sadrži meni, pretragu, jezik i „Shop now".
- **SearchPanel:** pretraga kafa i opreme po imenu, poreklu i notama na oba jezika. Rezultat vodi na `/p/<slug>`. Tekstovi za prazan rezultat i broj rezultata dolaze iz sadržaja.
- **`cart.ts`** po tački 8, čuva se u `kafa-cart`.
- **CartDrawer:**
  - stavke sa +/− i ukloni;
  - međuzbir, dostava, „do besplatne dostave" i ukupno sa PDV-om;
  - onemogućeno dugme „Zahlungspflichtig bestellen" / EN tekst iz Z3, sa „Demo: keine echten Bestellungen." ispod.
- **Toast:** `aria-live="polite"`.
- **ChatBubble:** pojavljuje se posle 3 s (u reduced motion odmah) i otvara demo panel.
- **LangSwitch:** EN · DE, sa `aria-label`; koristi se i u footeru.

Gotovo kad:
- Korpa, oba jezika:
  - 2 × Guji 250 g → dostava € 4,50, „Noch € 9,20 bis zum Gratisversand", ukupno € 40,30;
  - + On Repeat 250 g → besplatna dostava, ukupno € 49,30;
  - korpa ostaje posle ponovnog učitavanja.
- Pretraga: „guji" → 1 rezultat, DE „Äthiopien" → Guji, „xyz" → poruka o praznom rezultatu.
- `window.__chapter('pour')` menja boje headera.
- Fokus ostaje zarobljen u meniju i korpi, Esc zatvara.
- Sve dodirne površine su ≥ 44 px, nema horizontalnog skrola na 390.

### Z9: Prodavnica i modal proizvoda → programer
Fajlovi: `KafaSkrol/src/sections/Shop.tsx`, `KafaSkrol/src/sections/shop.css` (nov), `KafaSkrol/src/components/ProductCard.tsx`, `KafaSkrol/src/pages/ProductModal.tsx`, `KafaSkrol/src/lib/filters.ts` (nov)

Uradi:
- **Sekcija `#find-your-cup`** (raspored iz skice):
  - naslov, podnaslov i tekst sa CTA na `#tasting-set`;
  - traka „Versandkostenfrei ab € 45" sa „Konzept / Demo";
  - filteri Brew, Flavor, Roast i Type kao čipovi (na telefonu horizontalna traka), sortiranje, broj rezultata, reset i prazno stanje;
  - grupe sa brojem: Coffee (6), Sets (Probierset), Equipment (samo oprema koja ima cenu);
  - blok o dostavi sa dugmetom na `/versand`;
  - pojavljivanje kartica preko `reveal.ts`, a promena filtera daje fade mreže (u reduced motion odmah).
- **`filters.ts`:**
  - čiste funkcije: unutar grupe važi „ili", između grupa „i";
  - set i oprema ispadaju kad je aktivan Brew, Flavor ili Roast filter;
  - Type Coffee obuhvata 5 kafa sa kofeinom, a Decaf jednu;
  - čita `?brew=` iz URL-a.
- **`ProductCard`:**
  - slika, oznake, ime, poreklo i obrada;
  - na desktopu još note, datum prženja i izbor mlevenja;
  - veličina 250 g / 1 kg, `Price` sa Grundpreisom u istom redu i „incl. VAT, plus shipping", „Add to cart";
  - na telefonu kraća kartica (mapa-skrola).
- **`ProductModal` (`/p/:slug`):**
  - sva polja kartice iz `tekstovi.md`: farma (fiktivna), „Roasted on" (izračunat datum), „Best before" (po odluci; dok je prazno, red se ne prikazuje);
  - mlevenje (5 opcija) i veličina;
  - Esc, nazad i zatvaranje vraćaju na `/` i vraćaju fokus;
  - fokus je zarobljen i koristi se `lockScroll`;
  - nepoznat slug vodi na `/`.

Gotovo kad:
- Broj proizvoda po filteru je tačno:

  | Filter | Broj |
  |---|---|
  | Espresso | 4 |
  | Filter | 5 |
  | Fruity & floral | 4 |
  | Chocolate & nuts | 3 |
  | Light | 3 |
  | Medium | 3 |
  | Medium-dark | 1 |
  | Decaf | 1 |
  | Sets | 1 |
  | Fruity & floral + Espresso | 2 (Huila, Tarrazú) |

- `/?brew=filter#find-your-cup` otvara prodavnicu sa izabranim Filter.
- Hladno otvaranje `/p/guji` prikazuje modal.
- Grundpreis stoji uz svaku cenu na oba jezika.
- Mreža ima 3 kolone na 1440 i 2 na 390, bez horizontalnog skrola.

### Z10: Sekcije ispod prodavnice, footer i pravne stranice → programer
Fajlovi: `KafaSkrol/src/sections/Subscription.tsx`, `About.tsx`, `BrewGuide.tsx`, `Contact.tsx`, `Footer.tsx`, `KafaSkrol/src/sections/sections.css` (nov), `KafaSkrol/src/pages/Legal.tsx`, `KafaSkrol/src/pages/Credits.tsx`

Uradi (raspored iz skice, tekst iz sadržaja):
- **`#subscription`:**
  - dve opcije, uslovi, poklon (3/6/12) i dugmad sa demo napomenom iz Z3;
  - `#tasting-set` sa „Add tasting set" (`addToCart`, 400 g).
- **`#about`:** ONAMA-1 i ONAMA-2 sa parallax-om ≤ 40 px (u reduced motion bez njega), tekst, demo red i dugme na `#contact`.
- **`#brew-guide`:** tri koraka sa GUIDE-1, GUIDE-2 i SIP posterom, pojavljivanje sa razmakom 60 ms, savet, preporuka i dugme na `/?brew=filter#find-your-cup`.
- **`#contact`:**
  - adresa uz demo napomenu, radno vreme, dani prženja, cupping;
  - `mailto` na adrese iz `site.ts`, demo telefon;
  - KONTAKT-1 i KONTAKT-2 sa natpisom „Symbolbild";
  - apstraktna SVG „mapa" bez pravih pločica i podataka.
- **`#footer`:**
  - kolone iz `tekstovi.md`;
  - newsletter: samo e-mail i kućica koja nije štiklirana; greške preko `aria-describedby`; uspeh je demo poruka; nema mrežnog zahteva;
  - dugme „Vertrag widerrufen" na `/widerruf`;
  - mesto za Gewährleistungslabel (po odluci, podrazumevano obeležen placeholder);
  - stalna napomena „Konzept / Demo", copyright, LangSwitch, link na Credits;
  - razmak ispod ≥ 72 px zbog chat balona.
- **`Legal`:** jedna stranica za sve slugove iz `legal.ts`.
- **`Credits`:** fotografije iz `media.ts`, fontovi i linkovi na `public/licenses/`; spoljni linkovi sa `rel="noopener noreferrer"`.
- Sve sekcije imaju `scroll-margin-top` = visina headera.

Gotovo kad:
- Prazna prijava na newsletter pokazuje grešku, a ispravna ne šalje nijedan zahtev (network log).
- Sve pravne rute i `/credits` rade i kad se otvore direktno.
- Linkovi iz menija pristaju na vrh sekcije ispod headera.
- Chat ne pokriva poslednje dugme.
- Nema horizontalnog skrola na 390, a dodirne površine su ≥ 44 px.

### Z11: Sadržaj sajta → programer
Fajlovi: `KafaSkrol/src/content/site.ts`, `chapters.ts`, `products.ts`, `shop.ts`, `sections.ts`, `legal.ts`, `media.ts`, `KafaSkrol/scripts/check-content.ts` (nov)

Uradi:
- Preneti `tekstovi.md` (sa dopunama iz Z3) tačno, po tački 7 Interfejsa:
  - SEO, header, poglavlja i pozadinske reči (Longberry, Percolate, Frother sa fusnotama);
  - SIP kartice;
  - 6 kafa, 3 komada opreme (mlin i dripper bez cene dok korisnik ne odluči), Probierset;
  - pretplata, prodavnica, filteri, korpa, O nama, Brew guide, Kontakt, footer, pravni stubovi.
- Grupe za filtere kao u Z9. Kratke verzije za telefon iz `tekstovi.md`.
- **`media.ts`:**
  - sekvence (osnovne putanje i posteri po tački 3);
  - para, 7 fotografija, kese i oprema, sve sa `ready: false`;
  - podaci o autoru i licenci iz `fotografije.md`;
  - koji proizvod koristi koju kesu (6 kafa dele 3 kese po boji).
- **`check-content.ts`** (pokreće se kao `check`) proverava:
  - Grundpreis za svaki proizvod: On Repeat € 54,00/kg, Guji € 71,60/kg, Nyeri € 78,00/kg, Huila € 104,00/kg, Tarrazú € 74,00/kg, Pause € 76,00/kg, Probierset € 72,50/kg, primer pretplate € 48,60/kg, „Surprise me" € 76,00/kg;
  - poklon 3/6/12 = € 127,50 / € 255,00 / € 510,00;
  - da svako `L` polje ima en i de;
  - da su slugovi jedinstveni i da SIP kartice pokazuju na postojeće proizvode;
  - da u sadržaju nema imena brenda.

Gotovo kad: `npm run check` prolazi; ručna provera 10 nasumičnih stringova prema `tekstovi.md` nema odstupanja; build i lint prolaze; početna sa svim sekcijama nema grešaka u konzoli.

## Talas 3 (posle talasa 2)

### Z12: Priča GRIND → POUR → SIP (spajanje) → animator
Fajlovi:
- novi i glavni: `KafaSkrol/src/story/Story.tsx` (stub), `KafaSkrol/src/story/timeline.ts`, `KafaSkrol/src/story/story.css`;
- u ovom talasu isti animator sme da menja i ostatak `KafaSkrol/src/story/**`, `KafaSkrol/src/lib/sequence.ts`, `KafaSkrol/src/pages/Dev*.tsx` i `KafaSkrol/scripts/shots.mjs`. Niko drugi ih ne dira.

Uradi:
1. **Osnova.**
   - Jedan visok kontejner `#top` sa lepljivom (sticky) scenom i tri sloja (`#grind`, `#pour`, `#sip`, svaki sa `data-chapter`).
   - Dužine iz `timeline.ts` (tačka 2).
   - Jedan ScrollTrigger sa scrub-om za ceo kontejner. Bez pin-spacer-a za svako poglavlje i bez unutrašnjeg skrol kontejnera.
2. **GRIND i POUR na zajedničkom satu.**
   - GRIND platno (S × 1,25 S) je uz vrh svog sloja, POUR platno (S × S) uz vrh svog sloja, bez razmaka između slojeva.
   - Desktop: S = 100vh, osa oko 58 % širine (podesiti da mlin padne kao u mockupu). Telefon po storyboard-u 1: S = min(100vw, 62svh); GRIND platno uz dno sa maskom gornjih 12 %, POUR platno uz vrh ispod headera, tekst ispod.
   - GRIND platno nikad ne crta preko POUR sloja.
   - Na iOS-u, kad se traka adrese skupi, ispod scene ne sme da se vidi praznina ni presečen mlaz.
3. **Učitavanje u delovima** (storyboard 8):
   - posle `load`: GRIND svaki 6., pa svaki 2., pa ostali;
   - na 30 % GRIND-a: POUR G65–G96 celi, pa svaki 6. (prelaz mora biti ceo pre 60 % GRIND-a);
   - ulaz u POUR pin: ostatak POUR-a, pa SIP svaki 6.;
   - na 60 % POUR-a: ostatak SIP-a i kese.
4. **Talas:** `wave.set(p, startY)`, gde je `startY` iz `kafa_y` za trenutni G preračunat u px. SIP ide na svoj sat S.
5. **Pokreti** (tokeni trajanja i easing-a):
   - tekst ulazi sa fade + 24 px;
   - reč klizi oko 10 % širine kroz pin;
   - kartice uleću jedna za drugom (3D okret, `--ease-settle`) na 45–80 % SIP opsega;
   - para je aktivna u opsezima iz tačke 2;
   - `--table-y` iz sidara;
   - header prelazi `grind` → `pour` → `sip` → `page` kad granica sloja pređe liniju headera;
   - `registerChapterNavigator`: početak GRIND-a, POUR pina i SIP pina.
6. **Telefon:** isti segmenti u svh, nivo `m`, talas bez displacement-a, bez reči Frother i bez strelica. SIP sloj sme da bude viši od ekrana; traka kartica mora da ostane dostupna i da se skroluje prstom.
7. **Reduced motion:**
   - bez sticky scene, platna i zahteva za kadrove;
   - tri bloka od 100vh sa posterom `<img>` (alt iz sadržaja);
   - kartice su statične, između POUR i SIP stoji `WaveEdgeStatic`, bez pare;
   - sav tekst je odmah vidljiv, strelice i tačkice skaču odmah.
8. **LCP:** GRIND poster `<img fetchpriority="high">` ima isti URL kao predučitavanje u `index.html` i prikazuje se pre učitavanja `seq.json`. Platno ga menja tek kad se nacrta prvi kadar, bez treptaja.
9. **Pauza:** kad je priča van ekrana, ništa se ne crta i para je pauzirana.
10. **`shots.mjs`:** tačke priče su granica i sredina svakog segmenta iz tačke 2, na desktopu i telefonu.

Gotovo kad:
- Snimci na svim tačkama, na 1440, 390 i u reduced motion.
- Šav na G84 nema skok (≤ 2 CSS px).
- Header menja boju na granicama (±5 vh).
- Strelice i tačkice pristaju na početke segmenata.
- Redosled zahteva u network log-u prati tačku 3, a `__seqStats` ostaje ≤ 49 dekodiranih.
- Skrol od vrha do dna i nazad: bez grešaka u konzoli; prosečno vreme kadra < 20 ms na 1440 i < 33 ms na 390 uz 4× usporen CPU.
- LCP element je GRIND poster.
- Build i lint prolaze.

### Z13: Zajednički fajlovi i prvi mediji → programer
Fajlovi: `KafaSkrol/src/App.tsx`, `src/pages/Home.tsx`, `src/index.css`, `src/config/site.ts`, `src/content/*.ts` (i `types.ts`), `src/lib/format.ts`, `src/lib/reveal.ts`, `src/lib/chapterStore.ts`, `src/lib/motion.ts`, `src/lib/useMedia.ts`, `KafaSkrol/index.html`, `vite.config.ts`, `netlify.toml`, `README.md`

Uradi:
- Izmene zajedničkih fajlova koje su zadaci talasa 2 tražili u izveštajima. Spisak daje direktor.
- Za ono što je `mediji` predao (para, fotografije):
  - proveri da fajlovi postoje i da imaju dimenzije i veličine iz tačke 3 (ffprobe i Pillow samo čitaju);
  - prebaci `ready: true` u `media.ts`;
  - podatke za Credits uzmi iz `studio/kafa-skrol/izvori.md`.
- Ako nema ni zahteva ni medija, zadatak se preskače.

Gotovo kad: build, lint i check prolaze; nijedan medij sa `ready: true` ne vraća 404; Credits prikazuje svaki stock fajl koji je u upotrebi.

### Z14: Prva provera sekcija ispod priče → tester (samo čita)
Fajlovi: nijedan (privremeni folder)

Uradi: na stanju posle talasa 2 proveri header, korpu, pretragu, prodavnicu, modal, sekcije, footer i pravne rute na 390 i 1440, normalno i sa reduced motion. Proveravaju se sve stavke iz „Gotovo kad" zadataka Z8–Z11 i odeljka „Provera" ispod, osim priče.

Gotovo kad: izveštaj sa PROŠLO / NIJE PROŠLO po stavci, i za svaku grešku: fajl, širina i poruka.

### Z15: Izgled sekcija ispod priče i delova poglavlja → recenzent (samo čita)
Fajlovi: nijedan

Uradi:
- Oceni sekcije ispod priče prema skici i tokenima, jer mockup za njih ne postoji.
- Oceni `/dev/chapters` (u `npm run dev`) prema `mockup-1440.png` i `mockup-390.png`.
- Oceni `/dev/wave` (boje talasa).
- Oceni predlog rasporeda kartica 2–3 oko šolje.

Gotovo kad: izveštaj po formatu recenzenta, sa listom popravki po fajlu.

### Z16: Zavisnosti i konfiguracija → bezbednost (samo čita)
Fajlovi: nijedan

Uradi: pregledaj `KafaSkrol/package.json` i `package-lock.json`: tačne verzije, poklapanje sa RealEstates i odobrenim Archivo 5.3.0, install skripte u stablu i poznate ranjivosti. Pregledaj i `netlify.toml` i `vite.config.ts` (zaglavlja, CSP, `NPM_FLAGS`), forme i spoljne URL-ove u `dist`.

Gotovo kad: izveštaj sa nalazima po ozbiljnosti, ili spisak šta je provereno.

## Talas 4 (posle talasa 3)
Popravke po nalazima iz Z14–Z16 i pakovanje rendera čim `blender-umetnik` preda odobrene sekvence. Ako renderi kasne, talas 4 radi samo popravke, a Z21 i talas 5 čekaju.

### Z17: Popravke headera, korpe i prodavnice → programer
Fajlovi: fajlovi iz Z8 i Z9
Uradi: samo nalazi koji se odnose na ove fajlove.
Gotovo kad: svaki nalaz je zatvoren ili obrazložen; build i lint prolaze.

### Z18: Popravke sekcija, footera i pravnih stranica → programer
Fajlovi: fajlovi iz Z10
Uradi: samo nalazi koji se odnose na ove fajlove.
Gotovo kad: isto kao Z17.

### Z19: Popravke sadržaja i zajedničkih fajlova → programer
Fajlovi: fajlovi iz Z13
Uradi: nalazi za ove fajlove i `ready` zastavice za medije koji su stigli u međuvremenu.
Gotovo kad: isto kao Z17, plus `npm run check` prolazi.

### Z20: Popravke priče → animator
Fajlovi: fajlovi iz Z12
Uradi: nalazi za priču, talas i delove poglavlja (u ovom talasu su `src/story/**` njegovi).
Gotovo kad: isto kao Z17, plus snimci tačaka priče posle izmene.

### Z21: Pakovanje Blender rendera → mediji
Fajlovi: `KafaSkrol/public/media/seq/grind/**`, `seq/pour/**`, `seq/sip/**`, `KafaSkrol/public/media/bags/**`, `KafaSkrol/public/media/photos/gear-*` (opciono)

Uradi:
- Zameni privremene kadrove pravim. Brišeš ceo folder sekvence pre upisa; Z2 skripta se posle toga ne pokreće.
- Pravi nivoe `l`, `d` i `m` po tački 4, sa `placeholder: false` i sidrima iz `anchors.json` (`blender-umetnik`).
- Posteri, kese i snimci opreme po tački 3.
- Proveri oreole na pari i staklu na tamnoj i svetloj pozadini.

Gotovo kad:
- Izveštaj sa KB po kadru po nivou, u budžetu iz tačke 3.
- Ukupno ≤ ~21 MB za desktop `d` i ≤ ~5,8 MB za telefon.
- Kompozit šava G84 iz pravih kadrova je pregledan.
- Komanda za ponovno pakovanje je u izveštaju.

## Talas 5 (posle Z21)

### Z22: Tempo sa pravim kadrovima → animator
Fajlovi: `KafaSkrol/src/story/timeline.ts`, `KafaSkrol/src/story/story.css`, `KafaSkrol/scripts/shots.mjs`

Uradi: podesi osu priče, osu x, ulet kartica i opsege pare prema pravim kadrovima, a šav proveri na pravom G84.

Gotovo kad: snimci tačaka priče na 1440 i 390; šav ≤ 2 CSS px; nema grešaka u konzoli.

### Z23: Mediji za kese i opremu → programer
Fajlovi: `KafaSkrol/src/content/media.ts`

Uradi: `ready: true` za kese i opremu koje je Z21 predao, posle provere fajlova.

Gotovo kad: nema 404; kartice SIP i prodavnice prikazuju prave kese.

Posle toga ide završna provera (odeljak „Provera"). Direktor popravlja nalaze ili ih vraća vlasniku fajla, pa radi commit (`Kafa skrol: …`).

## Odluke korisnika
- **Pre talasa 2** (najkasnije pre Z11): potvrditi ili promeniti podrazumevana rešenja iz otvorenih pitanja 2–8. Rad kreće sa podrazumevanim.
- **Pre talasa 3:** telefon (otvoreno pitanje 1).
- **Posle talasa 3, pre talasa 4:** korisnik gleda priču sa privremenim kadrovima, lokalno (`cd KafaSkrol && npm run build && npx vite preview`) ili na Netlify deploy preview-u sa `noindex`, i odobrava tempo, talas i raspored kartica.
- **Pravi renderi:** odobrava ih korisnik u toku `blender-umetnik`-a (probe → pun render). Tek posle toga ide Z21.
- **Pre objave:**
  - korisnik pravi novi Netlify sajt iz istog repoa (base directory `KafaSkrol`; build i publish dolaze iz `KafaSkrol/netlify.toml`) i bira ime sajta i granu za objavu;
  - potvrđuje da je ime „POUR / PLAY" i dalje privremeno ili daje novo (izmena u `site.ts` + ponovni render kesa);
  - odobrava dopunu tabele projekata u `CLAUDE.md` (KafaSkrol, `cd KafaSkrol && npm run build && npm run lint`).
- Privremeni kadrovi ne idu u konačnu objavu.

## Provera
**tester:**
- Build, lint i `npm run check`.
- `npx vite preview` + `node scripts/shots.mjs` (normalno i `--reduced`) na 390×844, 1440×900, 1024×768 i 1920×1080 (položaj kuvala iz `dizajn.md`).
- Sve tačke priče iz tačke 2. Šav na G84. Boje headera po poglavlju. Strelice i tačkice.
- Sidra iz menija i oba skip linka.
- Hladno otvaranje `/p/guji`, `/impressum`, `/credits` (SPA preusmerenje u preview-u).
- Jezik se menja i pamti.
- Slučajevi korpe iz Z8, broj proizvoda po filteru iz Z9, pretraga, newsletter.
- Bez grešaka u konzoli, bez neuspelih zahteva, bez CSP prekršaja (preview zaglavlja), bez horizontalnog skrola.
- LCP ≤ 2,5 s na 390 uz Fast 4G i 4× usporen CPU, a LCP element je GRIND poster.
- Prvi JS ≤ 180 KB gzip. Prvi ekran ≤ 400 KB na desktopu i ≤ 250 KB na telefonu.
- Ceo skrol priče ostaje u budžetu iz Z21. `__seqStats` ≤ 49 dekodiranih.
- U reduced motion se ne traži nijedan kadar sekvence.
- WebKit, ako je instaliran (`svh`, sticky, `mix-blend-mode: screen`, memorija). Ako nije, javi „iOS nije testiran".

**recenzent:**
- Poglavlja, header i kartice prema `mockup-1440.png` i `mockup-390.png`. Sekcije ispod prema skici i tokenima.
- Potpisni trenuci: mlaz preko granice GRIND/POUR, talas sa živim SIP slojem iza i kartice koje sleću oko šolje.
- Archivo `wdth` 88 prema opisu iz `analiza-videa.md`, pozadinske reči, kontrast teksta u POUR.
- Para preko `screen` bez sive koprene. Zrno filma i svetlosni gradijent su suptilni.
- Telefon: tekst ≥ 16 px, dodirne površine ≥ 44 px, kartice se čitaju.
- Reduced motion verzija deluje kao celovita stranica.
- Utisak prema cilju 3,5/5 iz `fotorealizam.md`, uz poređenje sa dve reference iz `studio/znanje/reference.md` (npr. Vibe, CoffeeTech).

**bezbednost:**
- Tačne verzije i lockfile. Ništa nije instalirano sa skriptama (`NPM_FLAGS`).
- Zaglavlja: `noindex` (`X-Robots-Tag` + meta), CSP, `nosniff`, Referrer-Policy, Permissions-Policy, `frame-ancestors`.
- Nema tajni. Nema `innerHTML` ni `dangerouslySetInnerHTML`. Spoljni linkovi imaju `rel="noopener noreferrer"`.
- U `dist` nema spoljnih URL-ova osim linkova na Credits stranici.
- Forme ne šalju ništa. localStorage drži samo jezik i korpu, i Cookies stub to tačno kaže.
- Svaki fajl u `public/media/photos` i `steam` ima unos u `studio/kafa-skrol/izvori.md` (licenca, sha256, Mixkit samo Free).
- Sirovi fajlovi nisu u repou: `git ls-files studio/kafa-skrol/izvori` je prazno.
- Nema AI-generisanog stocka (oznake na Pixabay/Coverr), pa obaveza označavanja po AI Act čl. 50 ne nastaje.
- Grep za brend.

## Otvorena pitanja
1. **Telefon:** sticky priča sa šavom po `storyboard.md` (podrazumevano; POUR platno je iznad teksta, suprotno `mockup-390.png`) ili tok bez pina po `mapa-skrola.md` (zrna padaju CSS-om kad POUR uđe, raspored kao mockup)?
2. **Meni:** `tekstovi.md` (Coffee, Subscription, Brew guide, About, Visit; podrazumevano) umesto mockupa (Kaffee, Zubehör, Abo, Kurse, Kontakt) i skice?
3. **Filteri prodavnice:** `tekstovi.md` (Brew, Flavor, Roast, Type; podrazumevano) ili skica (Origin, Flavor, Roast)?
4. **Pozadinska reč POUR:** „Percolate" (`tekstovi.md`, podrazumevano) ili „Pourover" (mockup)?
5. **SIP kartice:** tri kartice (`tekstovi.md`) uz dugme „+" i datum prženja iz mockupa (podrazumevano)?
6. **Cene mlina i drippera** (`[FEHLT]`): korisnik daje cene, ili `trziste` daje raspon u jednom malom zadatku? Do tada se ta dva proizvoda ne prikazuju (PrAG traži cenu).
7. **MHD pravilo, načini plaćanja i dostava van Austrije:** do odluke red „Best before" se ne prikazuje, a na Versand stubu stoji `[FEHLT]` kao naslov.
8. **Pravne stranice:** demo stubovi bez izmišljenog sadržaja (podrazumevano, kao u `tekstovi.md`) ili potpune izmišljene stranice (predlog iz briefa)? Zvanični Gewährleistungslabel: ko ga preuzima i odakle (EUR-Lex predložak)? Do tada stoji obeležen placeholder.
9. **Sekcije ispod priče** nemaju mockup. Da li se grade po skici i tokenima uz ocenu `recenzent`-a (podrazumevano), ili `dizajner` prvo pravi mockup?
10. **Lenis:** `dizajn.md` svesno izbegava smooth-scroll koji preuzima točkić, a direktor ga je izabrao. Plan ga pali samo na desktopu sa mišem i van reduced motion, uz zastavicu `features.smoothScroll` u `site.ts`. Da li to važi?
11. **Prelomna tačka:** 1024 px (`dizajn.md`, podrazumevano) umesto oko 900 px (`mapa-skrola.md`)?
12. **Boje talasa** nisu u tokenima. Predlog daje Z6, ocenjuje `recenzent`, a potvrđuje korisnik posle talasa 3.
13. **iOS:** ako Playwright WebKit nije instaliran, `svh`, sticky, `screen` i memoriju platna mora da proveri korisnik na pravom iPhone-u.
14. **Referentni kadrovi** reela (`f_001`, `f_090`, `f_213`) postoje samo lokalno i možda više nisu dostupni. Ako ih nema, recenzent poredi sa mockupom i `analiza-videa.md`.
15. **Ime brenda je na etiketama kesa** (Z4). Promena imena posle rendera znači ponovni render kesa (oko 20 min).

## Odluke direktora posle plana (23.10.2026)

1. **Lenis ostaje**, samo na desktopu sa mišem, sa zastavicom `features.smoothScroll` (gasi se jednim redom).
2. **Telefon prati odobreni `mockup-390.png` i `mapa-skrola.md`.** Poglavlja idu jedno ispod drugog, bez pina i bez šava. Svako poglavlje ima kraću sekvencu (`m`) koja se odvija dok je u ekranu. Šav GRIND → POUR postoji samo na desktopu. Z12 to implementira po ovoj odluci.
3. **Kad se izvori razlikuju**, važi pravilo plana: tekst iz `tekstovi.md`, tempo i kadrovi iz `storyboard.md`.
4. **Para:** `mediji` je napravio `steam/steam-cup-a.{webm,mp4}` i `steam-cup-b.{webm,mp4}` (+ `-seq/` WebP rezerva) umesto `steam-d/m.mp4`. `media.ts` koristi ove fajlove: `webm` je prvi `<source>`, `mp4` drugi; A za POUR, B za SIP.
5. **Fotografije** su u `photos/`: `shop-1`, `shop-bg-1`, `shop-bg-2`, `onama-1`, `onama-2`, `guide-1`, `guide-2`, `kontakt-1` (izvor KONTAKT-2, natpis „Symbolbild"). KONTAKT-1 je odbačen (natpis lokala, ljudi). Tačne veličine su u `studio/kafa-skrol/izvori.md`.
6. **Netlify:** poseban sajt sa base `KafaSkrol` napraviće korisnik kad sajt bude spreman. Do tada se ništa ne objavljuje.
