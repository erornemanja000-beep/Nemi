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

Dopunjava se kako stižu izveštaji Z5–Z10.
