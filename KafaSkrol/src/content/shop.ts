// Prodavnica „Find your cup", natpisi kartice proizvoda, mlevenje, korpa (tekstovi.md).
// STUB iz Z1: samo ono što koriste zajedničke komponente (Price, ProductCard). Z11 dopunjuje.
import type { GrindId, L } from './types.ts'

export const shop = {
  title: { en: 'Find your cup', de: 'Finde deine Tasse' } satisfies L,
  subtitle: {
    en: 'Roasted in Vienna every Tuesday and Friday. Whole bean or ground the way you brew.',
    de: 'Geröstet in Wien, jeden Dienstag und Freitag. Ganze Bohne oder gemahlen, so wie du zubereitest.',
  } satisfies L,
  /** Napomena uz cenu (Price). */
  priceNote: {
    full: { en: 'incl. VAT, plus shipping', de: 'inkl. MwSt., zzgl. Versand' } satisfies L,
    short: { en: 'incl. VAT', de: 'inkl. MwSt.' } satisfies L,
  },
  labels: {
    roastedOn: { en: 'Roasted on', de: 'Geröstet am' } satisfies L,
    size: { en: 'Size', de: 'Größe' } satisfies L,
    grind: { en: 'Grind', de: 'Mahlgrad' } satisfies L,
    addToCart: { en: 'Add to cart', de: 'In den Warenkorb' } satisfies L,
  },
  grinds: [
    { id: 'whole', label: { en: 'Whole bean', de: 'Ganze Bohne' } },
    { id: 'espresso', label: { en: 'Espresso', de: 'Espresso / Siebträger' } },
    { id: 'filter', label: { en: 'Filter', de: 'Filter (Handfilter & Maschine)' } },
    { id: 'french-press', label: { en: 'French press', de: 'French Press' } },
    { id: 'moka', label: { en: 'Moka pot', de: 'Mokkakanne' } },
  ] satisfies { id: GrindId; label: L }[],
  cart: {
    toast: {
      en: 'Added to cart. This is a demo, so nothing will be ordered.',
      de: 'Im Warenkorb. Das ist eine Demo, es wird nichts bestellt.',
    } satisfies L,
  },
}
