// Sadržaj sajta: SEO, header, skip linkovi, pretraga, chat, demo napomena (tekstovi.md sa dopunama Z3).
// vite.config.ts čita site.seo.title.en, site.seo.description.en, site.h1.en i site.noscript.en.
// Oznake {brand}, {email}… menja fill(); {n} broj, {q} upit pretrage.
import type { L, Link } from './types.ts'

const seo: { title: L; description: L } = {
  title: {
    en: 'Specialty Coffee Roastery in Vienna | {brand}',
    de: 'Kaffeerösterei Wien · Specialty Coffee | {brand}',
  },
  description: {
    en: 'Specialty coffee roasted in Vienna: whole bean or ground for espresso, filter and moka pot. Brew guide, subscription, tasting set. Concept demo.',
    de: 'Specialty Coffee, frisch geröstet in Wien: ganze Bohne oder gemahlen für Espresso, Filter und Mokkakanne. Zubereitung, Abo, Probierset. Konzept-Demo.',
  },
}

const nav: Link[] = [
  { label: { en: 'Coffee', de: 'Kaffee' }, href: '#find-your-cup' },
  { label: { en: 'Subscription', de: 'Abo' }, href: '#subscription' },
  { label: { en: 'Brew guide', de: 'Zubereitung' }, href: '#brew-guide' },
  { label: { en: 'About', de: 'Über uns' }, href: '#about' },
  { label: { en: 'Visit', de: 'Kontakt' }, href: '#contact' },
]

export const site = {
  seo,
  /** Skriven H1 (vizuelno sakriven, čitač ga čita). */
  h1: {
    en: '{brand} – specialty coffee roastery in Vienna',
    de: '{brand} – Kaffeerösterei für Specialty Coffee in Wien',
  } satisfies L,
  logoLabel: { en: '{brand}, home', de: '{brand}, Startseite' } satisfies L,
  skip: {
    content: { en: 'Skip to content', de: 'Zum Inhalt springen' } satisfies L,
    shop: { en: 'Skip to shop', de: 'Zum Shop springen' } satisfies L,
  },
  nav,
  shopNow: { label: { en: 'Shop now', de: 'Zum Shop' }, href: '#find-your-cup' } satisfies Link,
  lang: {
    /** aria-label prekidača jezika, po trenutnom jeziku. */
    label: { en: 'Language: English. Switch to Deutsch', de: 'Sprache: Deutsch. Zu English wechseln' } satisfies L,
  },
  chat: {
    open: { en: 'Open chat', de: 'Chat öffnen' } satisfies L,
    tooltip: { en: 'Questions? Ask us.', de: 'Fragen? Schreib uns.' } satisfies L,
    /** Demo panel; {email} = brand.email */
    panel: {
      en: 'Hi! This chat is a demo. Write to {email} or come by the café.',
      de: 'Hallo! Dieser Chat ist eine Demo. Schreib an {email} oder komm im Café vorbei.',
    } satisfies L,
  },
  /** Pretraga: kafe i oprema po imenu, poreklu i notama (Z8). Broj se čita preko aria-live. */
  search: {
    placeholder: { en: 'Search coffee, origin or gear', de: 'Kaffee, Herkunft oder Zubehör suchen' } satisfies L,
    empty: { en: 'Nothing found for "{q}".', de: 'Nichts gefunden für „{q}“.' } satisfies L,
    resultOne: { en: '1 result', de: '1 Ergebnis' } satisfies L,
    results: { en: '{n} results', de: '{n} Ergebnisse' } satisfies L,
  },
  /** aria natpisi headera (tekstovi.md); {n} menja fill(). */
  aria: {
    mainNav: { en: 'Main menu', de: 'Hauptmenü' } satisfies L,
    menu: { en: 'Menu', de: 'Menü' } satisfies L,
    menuOpen: { en: 'Open menu', de: 'Menü öffnen' } satisfies L,
    menuClose: { en: 'Close menu', de: 'Menü schließen' } satisfies L,
    search: { en: 'Open search', de: 'Suche öffnen' } satisfies L,
    cart: { en: 'Cart, {n} items', de: 'Warenkorb, {n} Artikel' } satisfies L,
    cartOne: { en: 'Cart, 1 item', de: 'Warenkorb, 1 Artikel' } satisfies L,
    cartTitle: { en: 'Your cart', de: 'Dein Warenkorb' } satisfies L,
    close: { en: 'Close', de: 'Schließen' } satisfies L,
  },
  /** Stalna napomena o demou (footer, traka nad prodavnicom). */
  demo: {
    en: 'Concept / demo — not a real shop. Brand, coffees, farms, address and prices are made up.',
    de: 'Konzept / Demo — kein echter Shop. Marke, Kaffees, Farmen, Adresse und Preise sind erfunden.',
  } satisfies L,
  /** Kratka oznaka (traka nad prodavnicom, čipovi): početak napomene iznad. */
  demoShort: { en: 'Concept / demo', de: 'Konzept / Demo' } satisfies L,
  /** Red u <noscript> (Z3 tačka 4); plugin u vite.config.ts koristi EN. */
  noscript: {
    en: 'Concept / demo — not a real shop. Turn on JavaScript to see the animation and the shop.',
    de: 'Konzept / Demo — kein echter Shop. Mit JavaScript siehst du die Animation und den Shop.',
  } satisfies L,
}
