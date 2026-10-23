// Pravne stranice kao demo stub (tekstovi.md, footer i „šta fali"). Sadržaj se ne izmišlja:
// spisak naslova (`items`) dopunjuju Z3 (tekstovi) i Z11. STUB iz Z1: naslovi i uvodni red.
import type { L, LegalPage } from './types.ts'

const intro: L = {
  en: 'Concept / demo — not a real shop.',
  de: 'Konzept / Demo — kein echter Shop.',
}

export const legalPages: LegalPage[] = [
  { slug: 'impressum', title: { en: 'Imprint', de: 'Impressum' }, intro, items: { en: [], de: [] } },
  { slug: 'datenschutz', title: { en: 'Privacy policy', de: 'Datenschutz' }, intro, items: { en: [], de: [] } },
  { slug: 'agb', title: { en: 'Terms', de: 'AGB' }, intro, items: { en: [], de: [] } },
  { slug: 'versand', title: { en: 'Shipping & payment', de: 'Versand & Zahlung' }, intro, items: { en: [], de: [] } },
  { slug: 'widerruf', title: { en: 'Right of withdrawal', de: 'Widerrufsrecht' }, intro, items: { en: [], de: [] } },
  { slug: 'cookies', title: { en: 'Cookie settings', de: 'Cookie-Einstellungen' }, intro, items: { en: [], de: [] } },
]

export const credits = {
  title: { en: 'Credits', de: 'Credits' } satisfies L,
}
