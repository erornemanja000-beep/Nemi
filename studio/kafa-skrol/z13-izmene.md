# Z13: izmene zajedničkih fajlova (skuplja direktor)

Ove izmene su predložili agenti talasa 1–2. Radi ih **jedan** programer u Z13, posle talasa 2.

## Odluke direktora

- **Filter prodavnice iz drugih sekcija (Lenis problem iz Z1):** dugmad van prodavnice, npr. Brew guide, ne vode na `/?brew=filter#find-your-cup`. Umesto toga pozivaju:
  `window.dispatchEvent(new CustomEvent('kafa:shop-filter', { detail: { brew: 'filter' } }))`, pa `scrollToTarget('#find-your-cup')`.
  `Shop` (Z9) sluša taj događaj i postavlja filter. `?brew=` iz URL-a i dalje radi pri učitavanju stranice. `href` dugmeta ostaje `/?brew=filter#find-your-cup` kao rezerva bez JS-a.
- Paneli koji se skroluju (korpa, meni, modal, pretraga) imaju `data-lenis-prevent`.
- Footer link je „Cookies", a EN natpis za kontakt fotografiju je „Illustrative photo". Predlozi Z3 i Z11 su prihvaćeni.

## Spisak

| Fajl | Izmena | Ko je tražio |
|---|---|---|
| `KafaSkrol/package.json` | `"check": "node --experimental-strip-types scripts/check-data.ts && node --experimental-strip-types scripts/check-content.ts"` | Z11 |
| `KafaSkrol/vite.config.ts` | red u `<noscript>` koristi `site.noscript.en` umesto `site.demo.en` | Z11 |
| `KafaSkrol/src/lib/format.ts` + `scripts/check-data.ts` | EN datum „Oct 20, 2026" (en-US, kratak mesec) umesto „23 Oct 2026" | Z11 / Z3 |
| `KafaSkrol/src/content/types.ts` | `SipCard.notes?: L<string[]>` (tačne note na SIP karticama); `LegalEntry`, `LegalPageContent` iz `legal.ts` premestiti ovde; `SeqMedia.placeholder?: boolean` za red u Credits-u | Z11 |
| `KafaSkrol/src/lib/cart.ts` | koristi `shop.shipping.feeCents` i `freeFromCents` iz sadržaja umesto sopstvenih konstanti | Z11 (radi Z8, ne Z13) |
| `KafaSkrol/src/content/types.ts` + `media.ts` | `SeqMedia.geometry: { full: {W,H}, crop: {x0,y0,w,h} }`: grind `{1,1.25}` / `{0.22,0,0.56,1.25}`; pour `{1,1}` / `{0.26,0,0.72,1}`; sip `{1,1}` / `{0.2,0,0.64,0.86}`. Poster tada stoji na mestu isečka pre `seq.json` i u reduced motion | Z5 |

| `KafaSkrol/src/main.tsx` | `import './index.css'` ide **iznad** `import App`. Inače se CSS komponenti učita pre Tailwind-a, a preflight (`base`) pregazi `@layer components`. Kad se popravi, proveriti `wave.css`, `chrome.css`, `shop.css` i `sections.css`; `chapters.css` sada ima `@layer properties, theme, base, components, utilities;` kao zaštitu | Z7 |

| `KafaSkrol/src/lib/motion.ts` | `lockScroll` broji otvorene panele, umesto da/ne, da korpa preko modala ne otključa skrol | Z8 |
| `KafaSkrol/src/index.css` | `html { scrollbar-gutter: stable; }`, da se raspored ne pomera kad se skrol zaključa | Z8 |
| `KafaSkrol/src/components/Overlay.tsx` (nov) | `Overlay` premestiti iz `CartDrawer.tsx` u svoj fajl; uvoze ga `CartDrawer`, `MobileMenu`, `SearchPanel`, `ProductModal` | Z8 |

| `KafaSkrol/src/App.tsx` / `pages/Home.tsx` | ako se `Footer` premesti u `App.tsx`, izbaciti ga iz `Legal.tsx` i `Credits.tsx` (Z10 ga je tamo dodao) | Z10 |
| `KafaSkrol/src/content/legal.ts` + `types.ts` | polje `bodyReplacesText` umesto odluke po slug-u `cookies` | Z10 |
| `KafaSkrol/src/i18n/LangContext.tsx` | posle promene jezika ne upisivati naslov početne na drugim rutama (`PageMeta` to sada zaobilazi u sledećem kadru) | Z10 |

**Lenis 1.3.27, `anchors: true`:** ne radi `preventDefault`, pa pri kliku na `#sidro` skroluju i pregledač i Lenis. Z13 proverava da li `anchors` treba isključiti i sidra voditi preko `scrollToTarget` (Z10 je to rešio za dugme Brew guide-a).

**Sidra sa Lenis-om stanu prekratko** (Z8): sekcije iznad cilja narastu tokom skrola, `#find-your-cup` oko 310 px, a `#sip` oko 94 px na 390. Z9 i Z10 su dobili zadatak da rezervišu visine. Z12 radi isto za priču. Z13 proverava sve linkove iz menija na 1440 i 390.

**Za Z12 (iz Z7):**
- Slojevi imaju klase `ch-layer` i `ch-stage`. Redosled u sloju je `SceneBackdrop`, `ChapterText`, scena (`BackWord`, platno, `Sparkle`), pa `SipCards` kao direktno dete sloja i `ChapterNav`.
- `--table-y` se stavlja na sloj.
- Na telefonu je SIP sloj oko 144svh, a `mapa-skrola` kaže oko 120. Traka kartica se podiže preko `--sip-cards-pull`.
- Kartice uleću redom 2 → 1 → 0.
- Na 1024 px mlin po procentima iz mockupa pokriva kolonu teksta. Treba ga suziti ili pomeriti.

**Za Z12 (napomena direktora):** na desktopu je jedan dekodiran `d` kadar oko 4 MB, a tokom šava oko 400 MB. Zato `createClock(..., { retain: 16 })`.

Dopunjava se kako stižu izveštaji Z5–Z10.
