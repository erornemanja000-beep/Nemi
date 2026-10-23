// Formati za cene, Grundpreis, grame, visinu i datume, tačno kao u tekstovi.md:
//   DE „€ 17,90", „€ 71,60/kg", „1.950–2.200 m", „23.10.2026"
//   EN „€17.90",  „€71.60/kg",  „1,950–2,200 m"
// Separatori su ručni (ne Intl), da izlaz bude isti u svakom pregledaču i u Node-u.
// Bez DOM-a: fajl proverava scripts/check-data.ts (`npm run check`).
import type { Lang } from '../content/types.ts'

/** Nelomljivi razmak (U+00A0). */
export const NBSP = '\u00a0'

/** Datum u kalendaru (bez sata i zone). month je 1–12. */
export type CalendarDate = { year: number; month: number; day: number }

const SEP: Record<Lang, { group: string; decimal: string }> = {
  de: { group: '.', decimal: ',' },
  en: { group: ',', decimal: '.' },
}

function groupDigits(n: number, lang: Lang): string {
  return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, SEP[lang].group)
}

/** Broj sa tačno `decimals` decimala i separatorima jezika (1234.5 → „1.234,50" / „1,234.50"). */
export function formatNumber(value: number, lang: Lang, decimals = 0): string {
  const sign = value < 0 ? '-' : ''
  const fixed = Math.abs(value).toFixed(decimals)
  const [int, frac] = fixed.split('.')
  return sign + groupDigits(Number(int), lang) + (frac ? SEP[lang].decimal + frac : '')
}

/** Cena iz centi: DE „€ 17,90" (nelomljivi razmak), EN „€17.90". */
export function formatPrice(cents: number, lang: Lang): string {
  const amount = formatNumber(cents / 100, lang, 2)
  return lang === 'de' ? `€${NBSP}${amount}` : `€${amount}`
}

/** Grundpreis u centima po kg: cena / grami × 1000, zaokruženo na cent. */
export function unitPriceCents(cents: number, grams: number): number {
  return Math.round((cents / grams) * 1000)
}

/** Grundpreis: DE „€ 71,60/kg", EN „€71.60/kg". */
export function formatUnitPrice(cents: number, grams: number, lang: Lang): string {
  return `${formatPrice(unitPriceCents(cents, grams), lang)}/kg`
}

/** Pakovanje: „250 g", „1 kg", „1,5 kg" / „1.5 kg" (nelomljivi razmak). */
export function formatGrams(grams: number, lang: Lang): string {
  if (grams >= 1000) {
    const kg = grams / 1000
    return `${formatNumber(kg, lang, Number.isInteger(kg) ? 0 : 1)}${NBSP}kg`
  }
  return `${formatNumber(grams, lang)}${NBSP}g`
}

/** Visina: DE „1.950–2.200 m", EN „1,950–2,200 m" (crtica U+2013, nelomljivi razmak pre „m"). */
export function formatAltitude(altitude: { min: number; max?: number }, lang: Lang): string {
  const min = formatNumber(altitude.min, lang)
  const range = altitude.max && altitude.max !== altitude.min ? `${min}–${formatNumber(altitude.max, lang)}` : min
  return `${range}${NBSP}m`
}

const MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

/**
 * Datum: DE „23.10.2026". EN „23 Oct 2026" je privremen: konačan EN format daje Z3 (tekstovi.md).
 */
export function formatDate(date: CalendarDate, lang: Lang): string {
  if (lang === 'de') {
    return `${String(date.day).padStart(2, '0')}.${String(date.month).padStart(2, '0')}.${date.year}`
  }
  return `${date.day}${NBSP}${MONTHS_EN[date.month - 1]}${NBSP}${date.year}`
}

/** Današnji datum u Beču (Europe/Vienna), bez obzira na zonu pregledača. */
export function viennaDate(now: Date = new Date()): CalendarDate {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Europe/Vienna',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(now)
  const get = (type: string) => Number(parts.find((p) => p.type === type)?.value)
  return { year: get('year'), month: get('month'), day: get('day') }
}

/** Dani prženja (tekstovi.md): utorak i petak. 0 = nedelja. */
const ROAST_WEEKDAYS = [2, 5]

/** Poslednji dan prženja ≤ danas (Europe/Vienna): utorak ili petak. */
export function lastRoastDate(now: Date = new Date()): CalendarDate {
  const today = viennaDate(now)
  // podne po UTC-u: dodavanje i oduzimanje dana nikad ne prelazi granicu dana
  const t = new Date(Date.UTC(today.year, today.month - 1, today.day, 12))
  while (!ROAST_WEEKDAYS.includes(t.getUTCDay())) t.setUTCDate(t.getUTCDate() - 1)
  return { year: t.getUTCFullYear(), month: t.getUTCMonth() + 1, day: t.getUTCDate() }
}

/**
 * „Best before" (MHD). Pravilo još nije odlučeno (tekstovi.md: `[FEHLT: MHD-Regel]`), pa vraća null
 * i red „Best before" se ne prikazuje. Kad korisnik odluči (npr. prženje + X meseci), menja se samo ovde.
 */
export function bestBefore(_roast: CalendarDate): CalendarDate | null {
  return null
}
