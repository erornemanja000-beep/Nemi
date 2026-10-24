# Talas 4: nalazi za popravku (skuplja direktor)

Ovde se upisuju nalazi iz Z14 (tester), Z15 (recenzent) i Z16 (bezbednost), po zadatku iz `plan-izrade.md` koji ih popravlja. Dva zadatka ne dobijaju isti fajl.

## Z16: zavisnosti i podešavanja (bezbednost, 23.10.2026)

Nema kritičnih, visokih ni srednjih nalaza. Prošlo je:
- tačne verzije u `package.json`;
- bez install skripti, osim `fsevents` (samo macOS);
- 0 ranjivosti (npm audit, OSV);
- CSP bez kršenja i bez spoljnih zahteva;
- nema tajni;
- u `public/media` su samo izvedeni fajlovi.

Šest niskih nalaza:

| # | Nalaz | Odluka direktora | Ko popravlja |
|---|---|---|---|
| 1 | `rolldown` 1.2.15 (objavljen 21.10.2026), a RealEstates ima 1.2.14 | Vite 8.3.5 traži `~1.2.14`, pa i 1.2.14 odgovara. Dodati `"overrides": { "rolldown": "1.2.14" }`, jer je ta verzija već proverena u RealEstates i starija je od dve nedelje. Lock se pravi ponovo sa `npm install --ignore-scripts`, pa build i lint. | Z19 |
| 2 | `--ignore-scripts` važi samo na Netlify-u | Dodati `KafaSkrol/.npmrc` sa `ignore-scripts=true` i `save-exact=true` | Z19 |
| 3 | Komentar u `netlify.toml` (red 12–22) ne opisuje tačno pravila za 404 | Ispraviti komentar i dodati `/licenses/*` u pravila za 404 | Z19 |
| 4 | Nema HSTS i COOP zaglavlja | `Cross-Origin-Opener-Policy: same-origin` dodati odmah u `netlify.toml` i u preview zaglavlja u `vite.config.ts`. HSTS se proverava posle objave, jer ga Netlify sam šalje na HTTPS domenima. | Z19 |
| 5 | Datenschutz: stavka o hostingu je [FEHLT] (`legal.ts`, red 87–88) | Za demo ostaje. Za pravog klijenta upisati Netlify kao obrađivača. | posle, pravi klijent |
| 6 | U `Credits.tsx` (red 54) nema linka na Mixkit licencu | Dodati link na Mixkit Free licencu | Z18 |

## Z13: ostaci (programer)

| Nalaz | Ko popravlja |
|---|---|
| `cart.ts`: konstante dostave zameniti sa `shop.shipping.feeCents` i `freeFromCents` | Z17 |
| Zastareli komentar „Overlay iz CartDrawer.tsx" u `src/components/chrome.css` (red 46) | Z17 |
| Isti komentar u `src/pages/ProductModal.tsx` (red 2) i `src/sections/shop.css` (oko reda 328) | Z17 |
| `scripts/check-content.ts`: porediti `media.seq[*].geometry` i `placeholder` sa `seq.json` | Z19 |
| SIP poster u `#sip` bez rezervisane visine, pa `#find-your-cup` na 390 staje 74–94 px prekratko | Z12 (poslato), proverava Z20 |

## Z14: sekcije ispod priče (tester)

Testiran je commit `741a892` na kopiji iz `git archive`, na 390 i 1440, normalno i reduced, EN i DE. To je 196 provera. Prošlo je 20 od 21 stavke: build, lint, check, header, pretraga, korpa, prodavnica, modal, pretplata, sekcije, footer, pravne rute, sidra (±0,5 px), jezik, horizontalni skrol, konzola, CSP, reduced motion i izmene Z13.

| Nalaz | Ko popravlja |
|---|---|
| **NIJE PROŠLO (minorno):** kratki footer linkovi su uži od 44 px: „Terms" 43, „Abo" 30–31 i „AGB" 32–34 px (`Footer.tsx:26`, `linkClass`). Popravka je `min-w-tap` ili horizontalni padding. | Z18 (već na spisku iz Z15) |
| Toast na 390 (`Toast.tsx:44`, z-index iznad korpe): ako se korpa otvori u roku od 4 s posle „Add to cart", toast pokriva traku besplatne dostave i dugme za porudžbinu. Spustiti ga ispod panela ili ga sakriti dok je korpa otvorena. | Z17 |

**Za sve agente talasa 4:** zajednički `KafaSkrol/dist` su tokom Z14 više puta prebrisali drugi agenti, pa su se javljali lažni 404. Zato svako pravi build u svoj folder (`npx vite build --outDir <scratchpad>/...`) i koristi svoj port.

## Z15: vizuelni pregled (recenzent)

Ocenjen je commit `d8a4ccf`, na 390, 1024, 1280, 1440 i 1920, na EN i DE i sa reduced motion. **Ocena je 7/10.**

**Najveći problemi:**
- filteri se preklapaju na desktopu;
- u modalu je dugme za kupovinu ispod ivice ekrana;
- talas i kartice oko šolje još ne liče na referencu.

Snimci su u `pregled/z15/`:
- `filters.png`, `modal390.png`;
- `wave1440.png`, a uz njega isečak reference `f137crop.png`;
- `1440-en-sip.png`, a uz njega predlog `proto-sip-1440-en.png`.

**Odluka direktora za tačku 14 (veličina naslova sekcija):** prihvata se novi token `--fs-section: clamp(2.5rem, 1.5rem + 4vw, 4.5rem)`. On vraća veličinu iz odobrene skice (oko 76 px), pa nije nov smer dizajna.

### Z17 (programer, fajlovi iz Z8 i Z9)

- **`src/sections/shop.css`:**
  - **P1:** `.shop-strip` od 64rem: `flex-wrap: wrap; margin-inline: 0; padding-inline: 0; overflow: visible`. Sada čipovi prelaze u susednu kolonu i van kontejnera na 1024 (EN), na 1280 (EN i DE) i na 1440 (DE).
  - Oznake na kartici proizvoda 11 → 12 px.
  - Slika zrna kod „Shipping" ne sme da dodiruje razdelnik.
- **`src/sections/Shop.tsx`:**
  - **P1:** `lg:grid-cols-[1fr_1.15fr_1.35fr_1.4fr]` (red 183) zameniti sa `lg:flex lg:flex-wrap lg:gap-x-s7 lg:gap-y-s4`.
  - Na telefonu Sets i Equipment idu u jedan red od 2 kolone.
  - Na uvodu `lg:items-start` (red 161), jer je naslov sada 100 px ispod vrha fotografije.
- **`src/components/ProductCard.tsx`:** ispod 40rem kratak natpis dugmeta (`addToCartShort` iz Z19) i `whitespace-nowrap`. „IN DEN WARENKORB" se sada lomi u 2 reda.
- **`src/pages/ProductModal.tsx`:**
  - **P1:** blok sa veličinom, mlevenjem, cenom i dugmetom ide odmah ispod opisa, a tabela (Origin … Roasted on) ispod njega. Na telefonu ide lepljiva traka na dnu dijaloga (`sticky bottom: 0`, `bg-bg`, linija gore) sa cenom, Grundpreis-om i dugmetom. Sada je dugme na y 971 na 1440×900 i na y 1240 na 390.
  - Dugme za zatvaranje 16 px od ivica dijaloga i ekrana.
- **`src/components/Header.tsx`** (red 63–66): u dev-u i na `/dev/*` računati kao početnu, da se POUR i SIP mogu porediti sa mockupom.

### Z18 (programer, fajlovi iz Z10)

- **`src/sections/Subscription.tsx` + `sections.css`:**
  - CSS kese iz prodavnice dok ne stignu renderi: 2 kese za pretplatu i 4 male u redu za Probierset.
  - Napomena „Pause, skip or cancel…" na telefonu je 16 px.
- **`src/sections/BrewGuide.tsx`:**
  - linkovi iz skice po koracima (→ Gooseneck Kettle, → Find your cup);
  - korak 3 pokazuje „S064 PLATZHALTER", pa privremeno ide fotografija dok ne stigne render.
- **`src/sections/Contact.tsx`:** demo napomene na telefonu su 16 px.
- **`src/sections/Footer.tsx`:**
  - kućica `accent-color: var(--pp-cream-light)`, 22 px ili krem ivica 1,5 px;
  - `min-w-tap` na kratkim linkovima („Abo" 30, „AGB" 32, „Terms" 43 px);
  - demo red i copyright na telefonu su 16 px.
- **Naslovi sekcija:** FIND YOUR CUP, THREE STEPS, COME BY i A ROASTERY dobijaju `--fs-section` (token dodaje Z19). FIND YOUR CUP je u Z9 fajlovima, pa ga radi Z17.

### Z19 (programer, zajednički fajlovi i sadržaj)

- **`src/index.css`:**
  - `text-wrap: balance` u `@utility type-display` i `p { text-wrap: pretty }` u base. Sada se pojavljuju usamljene reči: „…TRY / FOUR.", „…OF / BEANS", „…WITH / CHAIRS", „…IM / MONAT", „…tasting / set.".
  - novi token `--fs-section` (odluka direktora gore).
- **`src/content/shop.ts`:**
  - `addToCartShort` (EN „Add", DE „In den Korb");
  - nelomljivi razmaci u „2–4 Werktage".
- **`src/content/sections.ts`** (red 197): `10 Uhr` sa nelomljivim razmakom.

### Z20 (animator, `src/story/**` i `Dev*.tsx`)

**`src/story/wave.css`, talas (P1).** Sada je to mutna kakao traka iste svetline kao POUR i SIP. U referenci (kadrovi 121–149) to je sjajno ćilibarno sočivo.
- **Boje iz reference:**
  - telo `#5A2010`–`#6A2008`;
  - osvetljeno dno `#B35915`–`#C77A2E`;
  - gornji odsjaj `#AF6F40`.
- **Nove promenljive:** `--wave-coffee: #4A1C0B; --wave-amber: #8E3F15; --wave-amber-light: #C9732A; --wave-glow: #F0A04B`.
- **Gradijent se obrće:**
  - gore tamna kafa 0,72;
  - sredina ćilibar 0,6;
  - dole svetli ćilibar 0,5.
- **Odsjaji:**
  - `.wave__glow` 16 → 28 px, 0,2 → 0,45;
  - `.wave__shine` 2 → 3 px, 0,5 → 0,8;
  - `.wave__shine-soft` 6 → 12 px, 0,12 → 0,22;
  - meniskus 0,92 → 0,6.

**`src/story/Wave.tsx`, oblik talasa:**
- `A1` 0,04 → ~0,10 i `L1` 1,2 → 1,8, da bude jedan veliki talas preko ekrana.
- Donja ivica dobija suprotnu fazu, pa traka postaje sočivo: oko 35 % vh u sredini i 8–10 % na krajevima.
- Sočivo 1,04 → 1,08, ako vreme kadra dozvoli.
- Statična ivica za reduced motion ostaje kakva je.

**`src/story/chapters.css` i `SipCards.tsx`, SIP kartice oko šolje (P1).** Važi od `(min-width: 80rem) and (min-height: 53.75rem)`, a ispod toga ostaje sadašnji špil. Prototip je `pregled/z15/proto-sip-1440-en.png`.
- **Kartica 0, Origin, puna:**
  - left `min(68.5%, 100% - gutter - 3.75rem - 16.25rem - 6px)`;
  - top `clamp(header-h + 1rem, 31%, 100% - 27rem)`;
  - nagib −6°, z 4.
- **Kartica 1, Flavor, kompaktna (`glass-card--compact`):**
  - širina 12,5rem, pakovanje 5,5rem;
  - bez reda sa notama i bez datuma prženja; cena, Grundpreis i „inkl. MwSt." ostaju;
  - left 44 %, top `max(header-h + .75rem, 12%)`, nagib +5°, z 3.
- **Kartica 2, Roast, kompaktna:** left 33,5 %, top `min(61%, 100% - 20rem)`, nagib −3°, z 4.
- **Zvezdica:** left 62 %, top 17 %.
- **Sitnice:** čip „DEMO" 10 → 12 px, a podnatpis kartice na telefonu 12 → 13 px.

**`src/story/Story.tsx`:**
- kartice uleću redom 1 → 2 → 0, tako da puna Origin kartica sleće poslednja;
- header prelazi na `sip` kad gornja ivica talasa pređe liniju headera (sada je tamni meni na tamnoj traci na p 0,85);
- GRIND platno ide do y 0 iza menija, pa treba maska vrha ili podloga iza menija.

**`src/pages/DevChapters.tsx`:** kutija šolje `desk:left-[40%] desk:w-[min(30vw,27rem)]`. Sada ulazi 67 px u kolonu teksta na 1440, a na 1024 tekst stoji preko šolje.

**Ne kvariti:**
- tokene i smenu krem i papirnih pozadina;
- poglavlja, koja odgovaraju mockupu;
- obradu fotografija;
- espresso footer;
- Grundpreis, PDV i demo oznake;
- SIP traku na telefonu;
- reduced motion;
- paru preko `screen`.

## Stanje

- **Z18 + Z19:** gotovo (commit „section, footer and config fixes"). rolldown je 1.2.14 (isti integrity kao u RealEstates), a `npm audit` daje 0.
- **Z17:** gotovo (commit „header, cart and shop fixes"). Na 16 kombinacija nema nalaza.
- **Z12 i Z20:** priča je spojena i popravljena (talas je ćilibarno sočivo, kartice stoje oko šolje). Vreme kadra na 1440 je 24 ms na opterećenoj mašini; tester meri ponovo na rasterećenoj.
- **Za Z22:** u `timeline.ts` treba promeniti `FALLBACK_ANCHORS` na `pult_y` 0,8851 i `kafa_y` ~0,92 (`pregled/blender/pour-anchors.json`). Druga mogućnost je da `media.ts` dobije `anchors`, kao `geometry`.
- **Ostaci za sledeći krug:**
  - prvi JS je 189,5 KB gzip, a budžet je 180 (isto je bilo i pre Z12);
  - EN „2–4 working days" bez preloma (`2–⁠4`) u `shop.ts`;
  - klizač panela modala na desktopu viri preko zaobljenog ugla (`.pm-panel`, `scrollbar-color` / `scrollbar-gutter`);
  - tester proverava: toast iznad lepljive trake modala na telefonu, nestanak toast-a pri otvaranju korpe, dugme modala na 1024×768;
  - na 390 DE se dugme „Probierset in den Warenkorb" (`Subscription.tsx`) lomi u 2 reda;
  - `tekstopisac` treba da potvrdi `credits.standIn` u `legal.ts` („Zubereitung, Schritt 3 (bis das Rendering da ist)").

## Završni pregled (recenzent, 24.10.2026, HEAD dc22b02)

Ukupna ocena je 7/10, a priča je na oko 60 % reference. Ocene po trenucima:
- GRIND 3,5;
- prelaz 3;
- POUR 3;
- talas 2;
- SIP 2,5.

Ocene rendera:
- šolja 5/5;
- mlin 4;
- bokal 4;
- kese 4;
- dripper 3;
- kuvalo 2, jer izgleda kao zgužvana folija; to traži nov render.

**Z25 (animator), popravke u kodu:**
- header pun posle vrha stranice;
- talas kao neprovidna ćilibarna tečnost;
- SIP tekst ulazi posle talasa, a dripper ostaje iznad talasa;
- kartice raspoređene oko šolje, sa većim kesama;
- svetao sto/pult kao u referenci;
- kraći GRIND pin.

**Posle sastanka (nov render):**
- kuvalo: manje bump-a, anizotropni brušeni čelik;
- gust mlaz zrna u GRIND-u, 40–60 zrna;
- rebra drippera;
- širi mlaz mlevene kafe;
- slika za Gooseneck Kettle u prodavnici.

## Završni test (tester, 24.10.2026, HEAD dc22b02)

Prošlo:
- build, lint i check;
- `shots.mjs`;
- svi kadrovi su pravi renderi, bez praznih platana;
- šav ≤ 0,1 px;
- mreža: 0 × 404, 0 spoljnih zahteva, 0 CSP kršenja i 0 grešaka;
- brend: nigde ne piše POUR / PLAY;
- reduced motion;
- sekcije: filteri, modal, korpa, footer i Credits;
- LCP 1,1–1,3 s (Fast 4G, 4× CPU).

Preuzeto do kraja priče: 13,3 MB na 1440 i 5,6 MB na 390.

Nije prošlo (prosleđeno u Z25):
- header se sudara sa sadržajem priče na desktopu;
- kuvalo je na 390 odsečeno 8 px pre ivice;
- vreme kadra talasa je 61 ms (4× CPU), a SIP 29 ms;
- prvi JS je 189,6 KB gzip, a budžet je 180 (poznato).

Sitnice:
- poster se vidi 3–6 kadrova pri ulasku POUR/SIP platna;
- SIP S56–S64 su isti kadrovi;
- toast na 1024 DE pokriva 3 px dugmeta u modalu;
- footer ima „Placeholder:" za zakonsku garanciju (namerno, demo).
