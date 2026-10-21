# KERN: sajt studija (beleška o napretku)

Eksperiment: sajt za izmišljeni digitalni studio **KERN**, koji pravi sajtove za male i velike firme širom sveta.
Ako se svidi, može da postane sajt za naš studio i promociju.
Ništa iz starijih projekata (Smash King, Freiraum, DON'S, Villa) nije korišćeno.

**Uživo (GitHub Pages, noindex): https://erornemanja000-beep.github.io/Nemi/kern/**

## Ime i logo
- **KERN** = jezgro (nem.) i *kerning* (razmak slova u tipografiji). Poruka: „Websites built around your core.“ / „Websites, gebaut um Ihren Kern.“
- Logo: slovo K čija se dva kraka sastaju u narandžastom jezgru (`src/components/Logo.jsx`, `public/favicon.svg`).
- Boje: skoro crna `#0a0a0b`, krem tekst `#edebe6`, narandžasta `#ff5b24`, svetli preseci `#f2f0eb`.
- Fontovi (na našem serveru, ne sa Google-a, zbog austrijskih tužbi oko Google Fonts): Inter Tight, Instrument Serif (kurziv), JetBrains Mono.

## Kako sajt radi
Jedna 3D scena (three.js + React Three Fiber) stoji iza cele strane i pomera se skrolom (GSAP ScrollTrigger + Lenis):
1. **Uvod**: brojač, pa se kamera odmiče od užarenog jezgra dok se stakleni K slaže (staklo lomi natpis KERN i topli sjaj iza sebe).
   Jezgro jače sija kad mu se kursor približi.
2. **Manifest**: K se rasklopi, kamera uleti u jezgro (bljesak, širi ugao), pa tunel svetla; tekst se pali reč po reč.
3. **Radovi**: 6 konceptnih sajtova na unutrašnjosti valjka oko kamere; skrol ih okreće, svaki zastane u centru.
   Svaki „sajt“ je nacrtan u kodu preko Unsplash fotke (`src/world/textures.js`). Klik na ploču ili indeks skroluje do projekta.
4. **Usluge** (slika prati kursor), **Mali / veliki biznis** (prekidač), **Proces** (krug napretka), **Standardi** (brojači),
   **Paketi** (kartice se naginju u 3D), **Kalkulator cene** (igračka), **FAQ**, **Kraj** (K se ponovo slaže), **Kontakt**, footer.
- Engleski je glavni jezik, nemački na dugme (ili sam ako je pregledač na nemačkom).
- Na telefonu: niža rezolucija stakla i scene, manji tunel; meni preko celog ekrana.
- Bez WebGL-a: radovi se pokazuju kao obična mreža slika.

## Fajlovi
| Putanja | Šta je |
|---|---|
| `src/content.js` | svi tekstovi (EN + DE), projekti, paketi, FAQ |
| `src/world/Scene.jsx` | 3D scena: staklo, jezgro, oreol, tunel, galerija, režiser kamere |
| `src/world/useWorldScroll.js` | veza između preseka strane i 3D scene |
| `src/components/*` | preseci strane |
| `src/components/Estimate.jsx` | kalkulator: **okvirne cene stoje na vrhu fajla** |
| `public/img/` | Unsplash fotke (zasluge u `src/credits.json` i u footeru) |

## Pokretanje i objava
```
cd kern
npm install
npm run dev            # lokalno
npm run build          # gotov sajt u dist/
python3 build_pages.py <folder-grane-gh-pages>   # kopira dist u /kern/ na grani gh-pages
```
Ako je kontejner nov: `git fetch origin gh-pages && git worktree add ../gh-pages gh-pages`, pa commit i push na `gh-pages`.

## Odakle su ideje
- **Curated Design**: Basement Studio, Lusion, Deeo, Our Life's Work, Twingate (boje, tipografija, raspored preseka).
- **21st.dev**: stakleni „prism hero“ (staklo lomi natpis u sceni), lista sa slikom koja prati kursor, magnetna dugmad.
- **Originkit**: dugme sa strelicom, tačkasti kursor, pojavljivanje teksta.
- **getlayers.ai**: uvod koji prelazi u logo, jezgro koje reaguje na kursor.
- **Istraživanje tržišta**: niko ne spaja vrhunski izgled sa jasnim cenama, pa su tu paketi „od“ i kalkulator; EU zakon o pristupačnosti kao argument.
- **Unsplash**: 12 fotki (6 konceptnih projekata, 6 usluga).

## Pre nego što postane pravi sajt
- **Cene** (paketi od 1.900 / 4.900 / 9.500 €, održavanje od 49 €/mes., sve u kalkulatoru) su okvirne, iz tržišnih podataka.
- **„Vienna“** u tekstu i satu: potvrditi gde je studio.
- **Forma** još nigde ne šalje (pokazuje potvrdu da je pregled); treba e-mail ili servis (npr. Formspree).
- **Impressum, Datenschutz, cookie** (obavezno u Austriji/EU) još ne postoje.
- **Projekti** su konceptne studije (tako i piše na sajtu); kad bude pravih radova, menjaju se u `content.js`.
- Obećanja (2–4 nedelje, odgovor za 24 h, WCAG 2.2 AA, Lighthouse 100 kao cilj) proveriti da li ih studio može da drži.
