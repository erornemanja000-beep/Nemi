// Provera formata (npm run check): node --experimental-strip-types scripts/check-data.ts
// Izlazi moraju biti tačno kao u studio/kafa-skrol/tekstovi.md (plan, Z1 „Gotovo kad").
// Z11 dodaje scripts/check-content.ts (Grundpreis svakog proizvoda, L polja, slugovi, brend).
import {
  bestBefore,
  formatAltitude,
  formatDate,
  formatGrams,
  formatPrice,
  formatUnitPrice,
  lastRoastDate,
  NBSP,
  unitPriceCents,
} from '../src/lib/format.ts'

let failed = 0
let passed = 0

function eq(label: string, actual: unknown, expected: unknown) {
  if (actual === expected) {
    passed++
    return
  }
  failed++
  const show = (v: unknown) => JSON.stringify(v)
  console.error(`NIJE PROŠLO  ${label}\n  dobijeno:  ${show(actual)}\n  očekivano: ${show(expected)}`)
}

const n = (s: string) => s.replaceAll(' ', NBSP) // u očekivanom tekstu razmak = nelomljivi razmak

// cena i Grundpreis
eq('cena DE', formatPrice(1790, 'de'), n('€ 17,90'))
eq('cena EN', formatPrice(1790, 'en'), '€17.90')
eq('Grundpreis DE', formatUnitPrice(1790, 250, 'de'), n('€ 71,60/kg'))
eq('Grundpreis EN', formatUnitPrice(1790, 250, 'en'), '€71.60/kg')
eq('Grundpreis 1 kg DE', formatUnitPrice(6490, 1000, 'de'), n('€ 64,90/kg'))
eq('Grundpreis u centima', unitPriceCents(2600, 250), 10400)
eq('cena iznad 1000 DE', formatPrice(51000, 'de'), n('€ 510,00'))
eq('cena sa hiljadama DE', formatPrice(123450, 'de'), n('€ 1.234,50'))
eq('cena sa hiljadama EN', formatPrice(123450, 'en'), '€1,234.50')

// grami (nelomljivi razmak)
eq('250 g', formatGrams(250, 'de'), n('250 g'))
eq('1 kg', formatGrams(1000, 'en'), n('1 kg'))
eq('400 g', formatGrams(400, 'en'), n('400 g'))
eq('250 g bez običnog razmaka', formatGrams(250, 'en').includes(' '), false)

// visina
eq('visina DE', formatAltitude({ min: 1950, max: 2200 }, 'de'), n('1.950–2.200 m'))
eq('visina EN', formatAltitude({ min: 1950, max: 2200 }, 'en'), n('1,950–2,200 m'))
eq('visina jedna vrednost DE', formatAltitude({ min: 1750 }, 'de'), n('1.750 m'))

// datum prženja: poslednji utorak ili petak ≤ danas, Europe/Vienna
const at = (iso: string) => new Date(iso)
const roast = (iso: string) => formatDate(lastRoastDate(at(iso)), 'de')
eq('lastRoastDate 23.10.2026 (petak)', roast('2026-10-23T10:00:00Z'), '23.10.2026')
eq('lastRoastDate 22.10.2026 (četvrtak)', roast('2026-10-22T10:00:00Z'), '20.10.2026')
eq('lastRoastDate 26.10.2026 (ponedeljak)', roast('2026-10-26T10:00:00Z'), '23.10.2026')
eq('lastRoastDate 20.10.2026 (utorak)', roast('2026-10-20T10:00:00Z'), '20.10.2026')
// 22.10. u 23:30 UTC je već 23.10. u Beču (CEST): važi bečki datum, ne UTC
eq('lastRoastDate zona Beča', roast('2026-10-22T23:30:00Z'), '23.10.2026')
// posle prelaska na zimsko vreme (25.10.2026): 26.10. u 23:30 UTC je 27.10. u Beču (utorak)
eq('lastRoastDate posle DST', roast('2026-10-26T23:30:00Z'), '27.10.2026')
eq('datum EN (privremen format)', formatDate({ year: 2026, month: 10, day: 23 }, 'en'), n('23 Oct 2026'))

// MHD: dok korisnik ne odluči, nema vrednosti (red „Best before" se ne prikazuje)
eq('bestBefore bez pravila', bestBefore({ year: 2026, month: 10, day: 23 }), null)

if (failed) {
  console.error(`\n${failed} od ${passed + failed} provera nije prošlo.`)
  process.exit(1)
}
console.log(`check-data: svih ${passed} provera je prošlo.`)
