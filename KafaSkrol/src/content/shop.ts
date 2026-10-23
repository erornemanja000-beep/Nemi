// Prodavnica „Find your cup": filteri, natpisi kartice proizvoda, mlevenje, dostava, korpa i modal
// (tekstovi.md sa dopunama Z3). Oznake u {…} menja fill() (LangContext tf):
//   {n} broj, {q} upit, {name} ime proizvoda, {size} formatGrams(), {amount} formatPrice().
import type { BrewGroup, FlavorGroup, GrindId, L, RoastGroup, TypeGroup } from './types.ts'

/** Sortiranje prodavnice (tekstovi.md: Newest roast, Price: low to high, Price: high to low). */
export type SortId = 'newest' | 'price-asc' | 'price-desc'

/** Dostava u Austriji (tekstovi.md, brief): € 4,50 ispod € 45, od € 45 (uključivo) besplatna. Isti brojevi su u tekstovima ispod (proverava check-content.ts). */
const shipping = {
  feeCents: 450,
  freeFromCents: 4500,
}

/**
 * Tekst o dostavi (tekstovi.md, „Dostava") u tri dela, da pravna stranica Versand & Zahlung može da
 * prikaže dostavu i preuzimanje posebno. Ceo tekst za prodavnicu je shippingInfo.text.
 */
const shippingParts = {
  delivery: {
    en: 'Free shipping within Austria from €45, otherwise €4.50. We roast on Tuesdays and Fridays and ship within one working day. Delivery in Austria takes 2–4 working days.',
    de: 'Innerhalb Österreichs versandkostenfrei ab €\u00a045, sonst €\u00a04,50. Wir rösten dienstags und freitags und versenden innerhalb eines Werktags. Die Lieferung in Österreich dauert 2–4 Werktage.',
  } satisfies L,
  pickup: {
    en: 'Or pick up your order free of charge at the café in 1070 Vienna.',
    de: 'Oder du holst deine Bestellung gratis im Café in 1070 Wien ab.',
  } satisfies L,
  vat: { en: 'All prices incl. VAT.', de: 'Alle Preise inkl. MwSt.' } satisfies L,
}

const join = (...parts: L[]): L => ({
  en: parts.map((p) => p.en).join(' '),
  de: parts.map((p) => p.de).join(' '),
})

export const shop = {
  title: { en: 'Find your cup', de: 'Finde deine Tasse' } satisfies L,
  subtitle: {
    en: 'Roasted in Vienna every Tuesday and Friday. Whole bean or ground the way you brew.',
    de: 'Geröstet in Wien, jeden Dienstag und Freitag. Ganze Bohne oder gemahlen, so wie du zubereitest.',
  } satisfies L,
  text: {
    en: 'Not sure where to start? Four filter coffees side by side in the tasting set.',
    de: 'Du weißt nicht, wo du anfangen sollst? Im Probierset stehen vier Filterkaffees nebeneinander.',
  } satisfies L,
  cta: { label: { en: 'Try the tasting set', de: 'Zum Probierset' } satisfies L, href: '#tasting-set' },
  /** Traka nad prodavnicom (kratko), uz site.demoShort. */
  bar: { en: 'Free shipping in Austria from €45', de: 'Versandkostenfrei in Österreich ab €\u00a045' } satisfies L,

  filters: {
    brew: {
      label: { en: 'Brew', de: 'Zubereitung' } satisfies L,
      all: { en: 'All', de: 'Alle' } satisfies L,
      options: [
        { id: 'espresso', label: { en: 'Espresso', de: 'Espresso' } },
        { id: 'filter', label: { en: 'Filter', de: 'Filter' } },
      ] satisfies { id: BrewGroup; label: L }[],
    },
    flavor: {
      label: { en: 'Flavor', de: 'Geschmack' } satisfies L,
      options: [
        { id: 'fruity', label: { en: 'Fruity & floral', de: 'Fruchtig & blumig' } },
        { id: 'chocolate', label: { en: 'Chocolate & nuts', de: 'Schokoladig & nussig' } },
      ] satisfies { id: FlavorGroup; label: L }[],
    },
    roast: {
      label: { en: 'Roast', de: 'Röstung' } satisfies L,
      options: [
        { id: 'light', label: { en: 'Light', de: 'Hell' } },
        { id: 'medium', label: { en: 'Medium', de: 'Mittel' } },
        { id: 'medium-dark', label: { en: 'Medium-dark', de: 'Mittel-dunkel' } },
      ] satisfies { id: RoastGroup; label: L }[],
      /** Pomoćni tekst ispod grupe (opciono, Z3 tačka 5). */
      help: {
        en: 'Light-medium roasts show up under Light and Medium.',
        de: 'Hell-mittel geröstete Kaffees findest du unter Hell und unter Mittel.',
      } satisfies L,
    },
    type: {
      label: { en: 'Type', de: 'Kategorie' } satisfies L,
      // isti natpisi su i naslovi grupa u mreži (Coffee, Sets, Equipment)
      options: [
        { id: 'coffee', label: { en: 'Coffee', de: 'Kaffee' } },
        { id: 'decaf', label: { en: 'Decaf', de: 'Entkoffeiniert' } },
        { id: 'equipment', label: { en: 'Equipment', de: 'Zubehör' } },
        { id: 'set', label: { en: 'Sets', de: 'Sets' } },
      ] satisfies { id: TypeGroup; label: L }[],
    },
    sort: {
      label: { en: 'Sort', de: 'Sortieren' } satisfies L,
      options: [
        { id: 'newest', label: { en: 'Newest roast', de: 'Neueste Röstung' } },
        { id: 'price-asc', label: { en: 'Price: low to high', de: 'Preis aufsteigend' } },
        { id: 'price-desc', label: { en: 'Price: high to low', de: 'Preis absteigend' } },
      ] satisfies { id: SortId; label: L }[],
    },
    count: { en: '{n} products', de: '{n} Produkte' } satisfies L,
    /** PREDLOG (nema u tekstovi.md, po uzoru na „1 result" iz Z3): jednina za {n} = 1. */
    countOne: { en: '1 product', de: '1 Produkt' } satisfies L,
    reset: { en: 'Reset filters', de: 'Filter zurücksetzen' } satisfies L,
    empty: { en: 'No coffee matches these filters.', de: 'Kein Kaffee passt zu diesen Filtern.' } satisfies L,
  },

  /** Napomena uz cenu (Price). */
  priceNote: {
    full: { en: 'incl. VAT, plus shipping', de: 'inkl. MwSt., zzgl. Versand' } satisfies L,
    short: { en: 'incl. VAT', de: 'inkl. MwSt.' } satisfies L,
  },
  /** Natpisi polja na kartici i u modalu (tekstovi.md, „Natpisi na kartici proizvoda"). */
  labels: {
    origin: { en: 'Origin', de: 'Herkunft' } satisfies L,
    process: { en: 'Process', de: 'Aufbereitung' } satisfies L,
    variety: { en: 'Variety', de: 'Varietät' } satisfies L,
    altitude: { en: 'Altitude', de: 'Höhe' } satisfies L,
    notes: { en: 'Tasting notes', de: 'Geschmack' } satisfies L,
    bestFor: { en: 'Best for', de: 'Ideal für' } satisfies L,
    roast: { en: 'Roast', de: 'Röstung' } satisfies L,
    farm: { en: 'Farm / co-op (fictional)', de: 'Farm / Kooperative (fiktiv)' } satisfies L,
    roastedOn: { en: 'Roasted on', de: 'Geröstet am' } satisfies L,
    /** MHD: red se ne prikazuje dok bestBefore() u format.ts vraća null ([FEHLT: MHD-Regel]). */
    bestBefore: { en: 'Best before', de: 'Mindestens haltbar bis' } satisfies L,
    size: { en: 'Size', de: 'Größe' } satisfies L,
    grind: { en: 'Grind', de: 'Mahlgrad' } satisfies L,
    addToCart: { en: 'Add to cart', de: 'In den Warenkorb' } satisfies L,
  },
  /** Čip „Demo" na SIP kartici i kartici u prodavnici (Z3 tačka 4). */
  card: {
    demo: { en: 'Demo', de: 'Demo' } satisfies L,
    /** sr-only uz čip */
    demoSr: { en: 'Demo product, not for sale', de: 'Demo-Produkt, nicht erhältlich' } satisfies L,
    /** aria-label dugmeta „+" ({size} = formatGrams, na SIP kartici uvek 250 g) */
    add: { en: 'Add {name}, {size}, to cart', de: '{name}, {size}, in den Warenkorb' } satisfies L,
  },
  grinds: [
    { id: 'whole', label: { en: 'Whole bean', de: 'Ganze Bohne' } },
    { id: 'espresso', label: { en: 'Espresso', de: 'Espresso / Siebträger' } },
    { id: 'filter', label: { en: 'Filter', de: 'Filter (Handfilter & Maschine)' } },
    { id: 'french-press', label: { en: 'French press', de: 'French Press' } },
    { id: 'moka', label: { en: 'Moka pot', de: 'Mokkakanne' } },
  ] satisfies { id: GrindId; label: L }[],
  grindHelp: {
    en: 'Whole beans keep their aroma longest. We grind on the day we ship.',
    de: 'Ganze Bohnen halten das Aroma am längsten. Gemahlen wird am Versandtag.',
  } satisfies L,

  shipping,
  /** Blok o dostavi ispod mreže, sa dugmetom na /versand. Plaćanje i dostava van Austrije su [FEHLT]. */
  shippingInfo: {
    title: { en: 'Shipping & pickup', de: 'Versand & Abholung' } satisfies L,
    text: join(shippingParts.delivery, shippingParts.pickup, shippingParts.vat),
    parts: shippingParts,
    cta: { label: { en: 'Shipping & payment', de: 'Versand & Zahlung' } satisfies L, href: '/versand' },
  },

  /** Korpa (demo). Naslov korpe je site.aria.cartTitle. {amount} = formatPrice(do besplatne dostave). */
  cart: {
    empty: { en: 'Your cart is empty.', de: 'Dein Warenkorb ist leer.' } satisfies L,
    subtotal: { en: 'Subtotal', de: 'Zwischensumme' } satisfies L,
    shipping: { en: 'Shipping', de: 'Versand' } satisfies L,
    toFree: { en: '{amount} to free shipping', de: 'Noch {amount} bis zum Gratisversand' } satisfies L,
    total: { en: 'Total incl. VAT', de: 'Gesamt inkl. MwSt.' } satisfies L,
    /** Onemogućeno dugme. EN je NEPROVERENO na EUR-Lex-u (Direktiva 2011/83/EU, čl. 8(2); tekstovi.md, Z3 tačka 6). */
    order: { en: 'Order with obligation to pay', de: 'Zahlungspflichtig bestellen' } satisfies L,
    orderNote: { en: 'Demo: no real orders.', de: 'Demo: keine echten Bestellungen.' } satisfies L,
    toast: {
      en: 'Added to cart. This is a demo, so nothing will be ordered.',
      de: 'Im Warenkorb. Das ist eine Demo, es wird nichts bestellt.',
    } satisfies L,
    close: { en: 'Close cart', de: 'Warenkorb schließen' } satisfies L,
    quantity: { en: 'Quantity', de: 'Menge' } satisfies L,
    decrease: { en: 'Decrease quantity', de: 'Menge verringern' } satisfies L,
    increase: { en: 'Increase quantity', de: 'Menge erhöhen' } satisfies L,
    remove: { en: 'Remove', de: 'Entfernen' } satisfies L,
    removeAria: { en: 'Remove {name}, {size}, from cart', de: '{name}, {size}, aus dem Warenkorb entfernen' } satisfies L,
  },

  /** Modal proizvoda (/p/:slug). */
  modal: {
    close: { en: 'Close details', de: 'Details schließen' } satisfies L,
    back: { en: 'Back to the shop', de: 'Zurück zum Shop' } satisfies L,
    /** alt velike slike kese u modalu (na karticama je alt="") */
    imageAlt: { en: '{name}, 250\u00a0g bag', de: '{name}, Packung à 250\u00a0g' } satisfies L,
  },
}
