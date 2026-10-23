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

Čeka izveštaj.

## Z15: vizuelni pregled (recenzent)

Čeka izveštaj.
