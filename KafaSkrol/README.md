# Kafa skrol: koncept sajta pržionice kafe (Konzept / Demo)

Skrol-sajt koncepta „GRIND → POUR → SIP": tri poglavlja vezana za skrol (sekvence kadrova iz Blendera,
talas kafe, staklene kartice), pa prodavnica, pretplata, O nama, Brew guide, Kontakt i footer.

> **Konzept / Demo.** Brend, kafe, farme, adresa, telefon i cene su izmišljeni. Nema pravih porudžbina,
> forme ništa ne šalju, sajt se ne indeksira (`noindex` u meta tagu i u `X-Robots-Tag`).

Plan izrade i dogovori između zadataka: `studio/kafa-skrol/plan-izrade.md`. Dizajn: `studio/kafa-skrol/dizajn/`,
tekstovi: `studio/kafa-skrol/tekstovi.md`.

## Pokretanje

```bash
cd KafaSkrol
npm install --ignore-scripts
npm run dev          # http://localhost:5173 (dev rute: /dev/seq, /dev/wave, /dev/chapters)
```

## Build i provera

```bash
npm run build        # tsc -b && vite build → dist/
npm run lint         # oxlint
npm run check        # formati (scripts/check-data.ts) i sadržaj: cene, L polja, linkovi, mediji (scripts/check-content.ts)
npx vite preview     # http://localhost:4173, sa istim zaglavljima (CSP, X-Robots-Tag) kao Netlify
node scripts/shots.mjs <folder> [url] [--reduced]   # snimci na 390 i 1440 + greške, zahtevi, skrol
```

`shots.mjs` koristi Playwright. Ako Playwright nema svoj Chromium, putanja se daje preko `PW_CHROMIUM`
(npr. `PW_CHROMIUM=/opt/pw-browsers/chromium`).

Stack: Vite 8 · React 19 · TypeScript 6 · Tailwind CSS 4 · GSAP 3 + ScrollTrigger · Lenis.
Verzije su tačne (bez `^`), iste kao u `RealEstates/package-lock.json`. Paketi se instaliraju sa
`--ignore-scripts`; novi paket ide tek posle provere (`bezbednost`).

## Objava

Poseban Netlify sajt iz istog repoa (pravi ga korisnik kad sajt bude spreman):

- **Base directory:** `KafaSkrol`. Build, publish (`dist`), `NODE_VERSION` i `NPM_FLAGS = --ignore-scripts`
  su u `KafaSkrol/netlify.toml`.
- SPA preusmerenje: svaka ruta (`/p/guji`, `/impressum`, `/credits` …) dobija `index.html`;
  mediji i bundle koji ne postoje vraćaju 404.
- Zaglavlja: `X-Robots-Tag: noindex, nofollow, noarchive`, CSP samo sa `'self'`, `nosniff`,
  `Referrer-Policy`, `Permissions-Policy`. Isti CSP stoji u `vite.config.ts` (`preview.headers`):
  menjaju se oba mesta zajedno.

## Mapa foldera

```
index.html            bez imena brenda; naslov, opis i <noscript> upisuje vite.config.ts
vite.config.ts        plugin za index.html, chunk „motion" (gsap + lenis), preview zaglavlja
netlify.toml          build, SPA preusmerenje, zaglavlja, keš
public/
  media/              sekvence (seq/), para (steam/), fotografije (photos/), kese (bags/)
  licenses/           OFL licence fontova
scripts/
  check-data.ts       npm run check: formati cena, Grundpreisa, grama, visine i datuma
  check-content.ts    npm run check: sadržaj prema tekstovi.md, brend, mediji sa ready: true
  shots.mjs           snimci i provera u Playwright-u
  placeholder_seq.py  privremeni kadrovi sekvenci (Z2)
src/
  config/site.ts      brend, e-mail, demo telefon, fill(), prekidači (features), ključevi localStorage
  content/            sav tekst i podaci (EN + DE), čist podatak; types.ts su tipovi
  content/media.ts    putanje do medija i zastavice `ready`
  i18n/LangContext    jezik (EN podrazumevano), tx() i tf()
  lib/                motion (GSAP, Lenis), useMedia, format, reveal, chapterStore, cart
  components/         Header, Overlay (ljuska korpe, menija, pretrage i modala), korpa, dugmad, ikonice …
  story/              priča GRIND → POUR → SIP (sekvence, talas, para, kartice)
  sections/           prodavnica i sekcije ispod priče
  pages/              početna, modal proizvoda, pravne stranice, Credits, dev harness-i
  styles/             tokens.css (kopija dizajnerskih tokena), fonts.css
  index.css           Tailwind, @theme sa ulogama iz tokena, osnovni stilovi
```

## Brend

Ime brenda, e-mail adrese i demo telefon postoje **samo** u `src/config/site.ts` (`brand`). Tekstovi u
`src/content` koriste oznake `{brand}`, `{email}`, `{wholesale}` i `{phone}`, a menja ih `fill()`.
Promena imena je jedan red, plus ponovni render kesa jer je ime na etiketi
(`studio/kafa-skrol/dizajn/etiketa.md`). Provera je grep iz plana (Interfejs 7): ime brenda i domen
adresa sme da nađe samo u `src/config/site.ts`, zato ih ni ovaj README ne piše.

## Renderi i mediji

Kod čita medije samo preko `src/content/media.ts`. Novi renderi ulaze bez izmene koda:

1. Zameni ceo folder sekvence u `public/media/seq/<grind|pour|sip>/` (nivoi `l/`, `d/`, `m/`, fajlovi
   `0001.webp` …, posteri i `seq.json` po planu, Interfejs 4). Pravi render ima `"placeholder": false`,
   pa ga skripta za privremene kadrove više ne prepisuje.
2. U `media.ts` prebaci `ready` (`SEQ_READY`, kese, oprema) na `true` tek kad fajlovi postoje.
   Medij sa `ready: false` se ne traži: umesto njega stoji obojena kutija iste razmere. Za sekvence
   `SEQ_PLACEHOLDER` i `geometry` moraju da budu isti kao `placeholder`, `full` i `crop` u `seq.json`
   (poster stoji na mestu isečka pre `seq.json`; red o privremenim kadrovima u Credits nestaje kad su
   sve tri `false`).
3. Para (`public/media/steam/`): webm je prvi izvor, mp4 drugi. Fotografije: `<id>-sm.webp` i
   `<id>-lg.webp`. Izvor, autor, licenca i sha256 svakog stock fajla su u `studio/kafa-skrol/izvori.md`.

## Fontovi

Lokalno, bez CDN-a: Archivo (paket `@fontsource-variable/archivo`, osa `wdth`), Fraunces i Figtree
(`src/assets/fonts`, iz `sajt/`). Sva tri su SIL OFL 1.1, licence su u `public/licenses/`.
