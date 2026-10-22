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

## Tim agenata (`.claude/agents/`)

| Agent | Uloga | Menja fajlove |
|---|---|---|
| `planer` | deli zadatak na delove koji mogu paralelno | ne |
| `programer` | radi jedan zadatak, samo u fajlovima koje dobije | da |
| `mediji` | slike, video, zvuk, AI promptovi (ffmpeg, `scripts/`) | da |
| `tester` | build, lint, Playwright na telefonu i desktopu | ne |
| `bezbednost` | pregled izmena i provera svakog novog paketa ili alata pre instalacije | ne |

Tok rada za veći zadatak:

1. `planer` napravi plan u talasima.
2. Zadaci iz istog talasa idu **istovremeno**: više `programer` / `mediji` agenata, svaki sa svojim fajlovima. Dva agenta nikad ne dobijaju isti fajl u istom talasu.
3. Posle poslednjeg talasa `tester` i `bezbednost` rade istovremeno.
4. Glavni agent popravlja nalaze (ili ih vraća programeru), pa radi commit i push.

Mali zadaci (jedan-dva fajla) ne traže ceo tim. Uradi ih direktno, pa pusti `tester`-a.

## Pravila

- Novi npm paket, CDN skripta, MCP server, plugin ili skripta sa interneta: prvo `bezbednost`, pa tek onda instalacija.
- Bez `--dangerously-skip-permissions` i bez širokih dozvola (`mcp__*__*`, `Bash(*)`) u `.claude/settings.json`.
- Ključevi i lozinke samo u Netlify env promenljivama, nikad u kodu ni kao rezervna vrednost.
- Commit poruke na engleskom, u stilu postojećih (`Projekat: šta se promenilo`).
