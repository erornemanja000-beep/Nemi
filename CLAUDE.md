# Nemi

Sajtovi i videi za klijente (lokali u Beču) i koncept-sajtovi kao maketa za buduće klijente.
Beleške o napretku su u `NAPREDAK.md`.

## Projekti

| Folder | Šta je | Build / provera |
|---|---|---|
| `sajt/` | DON'S Eisdiele, statički sajt (Netlify objavljuje `sajt/dist`) | `python3 sajt/build.py` |
| `freiraum/` | Freiraum Wien, statički sajt + Netlify funkcije (`booking.js`, `team.js`) | `cd freiraum && python3 build.py` |
| `freiraum-premium/` | premium verzija Freiraum-a sa skrol animacijama (`src/shared` je link na `freiraum/src/assets`) | `python3 freiraum-premium/build_offline.py <izlaz>` |
| `RealEstates/` | Vista Estates, Vite + React + TS + Tailwind + GSAP + Three.js | `cd RealEstates && npm run build && npm run lint` |
| `video/`, `frames/`, `assets/` | gotovi videi, kadrovi za AI klipove, promptovi | skripte u `scripts/` |

Tekstovi na sajtovima klijenata su podrazumevano na nemačkom. Sve mora da radi na 390 px, na 1440 px i sa `prefers-reduced-motion`.

## Studio: odeljenja i agenti (`.claude/agents/`)

Glavni agent je direktor: raspoređuje posao, pokreće agente paralelno, spaja rezultate, pita korisnika za odluke i radi commit. Agenti ne mogu sami da pozivaju druge agente, sve ide preko direktora.

| Odeljenje | Agenti | Šta predaje |
|---|---|---|
| 1. Planiranje | `istrazivac`, `planer` | brief sa činjenicama i referencama; plan u talasima |
| 2. Ideje | `kreativac`, `tekstopisac` | 2–3 smera koncepta; tekstovi DE/EN |
| 3. Skice | `skicar`, `storyboard` | skica sajta (PNG) i mapa skrola; storyboard videa |
| 4. Dizajn | `dizajner`, `animator` | dizajn sistem i mockup (PNG); kod za pokret |
| 5. Promptovi | `prompt-slike`, `prompt-video` | promptovi za AI slike i AI video |
| 6. Izrada | `programer`, `mediji` | kod sajta; obrađene slike, video i zvuk |
| 7. Kontrola | `tester`, `recenzent`, `bezbednost` | radi li; kako izgleda; da li je bezbedno |

Isti agent može da radi u više primeraka odjednom: tri `kreativac`-a sa različitim polaznim tačkama, dva `planer`-a (jedan za sajt, jedan za video), više `programer`-a na različitim fajlovima.

Radni materijal odeljenja ide u `studio/<projekat>/`. Ne objavljuje se, jer Netlify objavljuje samo `dist` foldere.

```
studio/<projekat>/
  brief.md          istrazivac
  ideje/smer-N.md   kreativac (svaki svoj fajl)
  tekstovi.md       tekstopisac
  skice/            skicar (skica.html, PNG, mapa-skrola.md)
  storyboard.md     storyboard
  dizajn/           dizajner (tokens.css, mockup.html, PNG, dizajn.md)
  promptovi/        prompt-slike (slike.md), prompt-video (video.md)
```

Stari promptovi ostaju u `video/prompt_*.md`, a kadrovi za AI klipove u `frames/`.

### Faze novog projekta (u svakoj fazi agenti rade istovremeno)

1. **Brief:** `istrazivac`.
2. **Ideje:** 2–3 `kreativac`-a, svaki sa drugom polaznom tačkom. → **Korisnik bira smer.**
3. **Skice:** `skicar`, `storyboard` i `tekstopisac` zajedno.
4. **Dizajn i promptovi:** `dizajner`, `prompt-slike` i `prompt-video` zajedno, pa `recenzent` ocenjuje mockup. → **Korisnik odobrava dizajn.**
5. **Izrada:** `planer` podeli posao u talase. U istom talasu rade `programer`-i, `animator` i `mediji`, svaki na svojim fajlovima. Dva agenta nikad ne dobijaju isti fajl u istom talasu.
6. **Kontrola:** `tester`, `recenzent` i `bezbednost` zajedno. Direktor popravlja nalaze ili ih vraća autoru, pa radi commit i push.

Za izmenu postojećeg sajta preskaču se faze koje ne trebaju (npr. samo 5 i 6). Mali zadaci (jedan-dva fajla) ne traže tim, nego se rade direktno, pa ide `tester`. Svaki agent troši tokene, pa se pokreće samo onoliko agenata koliko zadatak stvarno traži.

## Pravila

- Novi npm paket, CDN skripta, MCP server, plugin ili skripta sa interneta: prvo `bezbednost`, pa tek onda instalacija.
- Bez `--dangerously-skip-permissions` i bez širokih dozvola (`mcp__*__*`, `Bash(*)`) u `.claude/settings.json`.
- Ključevi i lozinke samo u Netlify env promenljivama, nikad u kodu ni kao rezervna vrednost.
- Commit poruke na engleskom, u stilu postojećih (`Projekat: šta se promenilo`).
