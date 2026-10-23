// Poglavlja GRIND → POUR → SIP, staklene kartice i kontrole (tekstovi.md). STUB iz Z1, proverava i
// dopunjuje ga Z11. vite.config.ts čita chapters.items (naslov, tekst i alt na EN) za <noscript>.
// Nelomljivi razmak ( ) ide u „18 g", „93 °C" i „1.950 m" (tekstovi.md).
import type { Chapter, L, SipCard } from './types.ts'

const items: Chapter[] = [
  {
    id: 'grind',
    eyebrow: { en: 'Section 1', de: 'Kapitel 1 · Mahlen' },
    title: { en: 'Grind', de: 'Grind' },
    text: {
      en: 'It all starts with a whole bean. We roast twice a week in Vienna and grind to order: for espresso, filter, French press or moka pot. Or keep it whole and grind it fresh at home.',
      de: 'Alles beginnt mit der ganzen Bohne. Wir rösten zweimal pro Woche in Wien und mahlen erst, wenn du bestellst: für Siebträger, Filter, French Press oder Mokkakanne. Oder du mahlst selbst, frisch zu Hause.',
    },
    cta: { label: { en: 'Shop beans', de: 'Bohnen kaufen' }, href: '#find-your-cup' },
    word: 'Longberry',
    wordNote: { en: 'a long bean from Harar, Ethiopia', de: 'lange Bohne aus Harar, Äthiopien' },
    alt: {
      en: 'Coffee grinder of steel and glass. Beans fall into the hopper, ground coffee runs out below.',
      de: 'Kaffeemühle aus Stahl und Glas. Bohnen fallen in den Trichter, unten rieselt gemahlener Kaffee heraus.',
    },
  },
  {
    id: 'pour',
    eyebrow: { en: 'Section 2', de: 'Kapitel 2 · Aufgießen' },
    title: { en: 'Pour', de: 'Pour' },
    text: {
      en: 'Pour-over takes its time: 18 g of coffee, water at 93 °C, three minutes. Let it bloom, pour in slow circles, then wait for the last drop. Our guide walks you through it.',
      de: 'Filterkaffee braucht Zeit: 18 g Kaffee, Wasser mit 93 °C, drei Minuten. Erst aufquellen lassen, dann in ruhigen Kreisen gießen und auf den letzten Tropfen warten. Die Anleitung zeigt jeden Schritt.',
    },
    cta: { label: { en: 'Brew guide', de: 'Zur Anleitung' }, href: '#brew-guide' },
    word: 'Percolate',
    wordNote: { en: 'water runs through the coffee, once', de: 'das Wasser läuft einmal durch den Kaffee' },
    alt: {
      en: 'A gooseneck kettle pours water into a ceramic dripper on a glass carafe. Steam rises, coffee drips.',
      de: 'Ein Schwanenhals-Wasserkocher gießt Wasser in einen Keramik-Handfilter auf einer Glaskanne. Dampf steigt auf, Kaffee tropft.',
    },
  },
  {
    id: 'sip',
    eyebrow: { en: 'Section 3', de: 'Kapitel 3 · Genießen' },
    title: { en: 'Sip', de: 'Sip' },
    text: {
      en: 'Fruity, chocolaty or somewhere in between? Find your cup by origin, flavor or roast: from a floral Ethiopian to our house espresso. Every bag shows its roast date.',
      de: 'Fruchtig, schokoladig oder irgendwo dazwischen? Finde deine Tasse nach Herkunft, Geschmack oder Röstung: vom blumigen Äthiopier bis zum Haus-Espresso. Auf jeder Packung steht das Röstdatum.',
    },
    cta: { label: { en: 'Find your cup', de: 'Finde deine Tasse' }, href: '#find-your-cup' },
    word: 'Frother',
    wordNote: { en: 'makes the foam for your Melange', de: 'macht den Schaum für deine Melange' },
    alt: {
      en: 'Ceramic cup with a dripping glaze, surrounded by three coffee cards.',
      de: 'Keramiktasse mit herablaufender Glasur, umgeben von drei Kaffeekarten.',
    },
  },
]

/** Tri staklene kartice u SIP-u. Proizvode huila-pink-bourbon i on-repeat dodaje Z11 (products.ts);
    dok ih nema, kartica mora da preživi nepostojeći slug. */
const sipCards: SipCard[] = [
  {
    label: { en: 'Origin', de: 'Herkunft' },
    sub: { en: 'Where it grows', de: 'Wo er wächst' },
    product: 'guji',
    line: { en: 'Ethiopia · 1,950–2,200 m', de: 'Äthiopien · 1.950–2.200 m' },
  },
  {
    label: { en: 'Flavor', de: 'Geschmack' },
    sub: { en: 'What you taste', de: 'Was du schmeckst' },
    product: 'huila-pink-bourbon',
    line: { en: 'Colombia · Limited lot', de: 'Kolumbien · Limitiertes Lot' },
    shortName: { en: 'Pink Bourbon', de: 'Pink Bourbon' },
  },
  {
    label: { en: 'Roast', de: 'Röstung' },
    sub: { en: 'How dark we go', de: 'Wie dunkel wir rösten' },
    product: 'on-repeat',
    line: { en: 'House blend · Medium-dark', de: 'Hausmischung · Mittel-dunkel' },
  },
]

/** Kontrole karusela poglavlja. {n} menja fill(). */
const nav = {
  prev: { en: 'Previous section', de: 'Vorheriges Kapitel' } satisfies L,
  next: { en: 'Next section', de: 'Nächstes Kapitel' } satisfies L,
  dot: { en: 'Go to section {n} of 3', de: 'Zu Kapitel {n} von 3' } satisfies L,
  swipe: { en: 'Swipe for more', de: 'Wischen für mehr' } satisfies L,
}

export const chapters = { items, sipCards, nav }
