// Provera sadržaja (npm run check): node --experimental-strip-types scripts/check-content.ts
// Proverava src/content/*.ts prema studio/kafa-skrol/tekstovi.md i planu (Z11 „Gotovo kad"):
//   Grundpreis svakog proizvoda i cene iz tekstova (pretplata, poklon, Probierset), da svako L polje ima
//   en i de, jedinstvene slugove, SIP kartice, broj proizvoda po filteru (Z9), nelomljivi razmak,
//   oznake {…}, linkove, medije sa `ready: true` i da u sadržaju nema imena brenda.
import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { brand, fill, storageKeys } from '../src/config/site.ts'
import { chapters } from '../src/content/chapters.ts'
import { credits, legal, legalPages } from '../src/content/legal.ts'
import { media, steamCredit } from '../src/content/media.ts'
import { productBySlug, products } from '../src/content/products.ts'
import { giftPriceCents, sections, subscriptionPriceCents } from '../src/content/sections.ts'
import { shop } from '../src/content/shop.ts'
import { site } from '../src/content/site.ts'
import type { BrewGroup, FlavorGroup, L, Lang, Product, RoastGroup, TypeGroup } from '../src/content/types.ts'
import { formatGrams, formatPrice, formatUnitPrice, NBSP } from '../src/lib/format.ts'

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

function ok(label: string, condition: boolean, detail = '') {
  eq(detail ? `${label} (${detail})` : label, condition, true)
}

const LANGS: Lang[] = ['en', 'de']

// --- nelomljivi razmak (tekstovi.md): između broja i jedinice, i posle „€" na DE ---
const UNIT_GAP = /(\d) (?=(?:g|kg|°C|%|m)(?![\p{L}\d]))/gu
const EURO_GAP = /€ (?=\d)/g
/** Očekivani tekst se piše sa običnim razmacima, a ovo stavlja nelomljive tamo gde ih traži tekstovi.md. */
const nb = (s: string) => s.replace(UNIT_GAP, `$1${NBSP}`).replace(EURO_GAP, `€${NBSP}`)

// ============================================================================================
// 1. Grundpreis i cene proizvoda (tekstovi.md, „6 kafa" i Probierset)
// ============================================================================================

/** slug → [cena manjeg pakovanja DE, Grundpreis DE, cena 1 kg DE] */
const PRICES: Record<string, [string, string, string | null]> = {
  'on-repeat': ['€ 13,50', '€ 54,00/kg', '€ 48,90'],
  guji: ['€ 17,90', '€ 71,60/kg', '€ 64,90'],
  nyeri: ['€ 19,50', '€ 78,00/kg', '€ 69,90'],
  'huila-pink-bourbon': ['€ 26,00', '€ 104,00/kg', '€ 93,90'],
  'tarrazu-honey': ['€ 18,50', '€ 74,00/kg', '€ 66,90'],
  pause: ['€ 19,00', '€ 76,00/kg', '€ 68,90'],
  'tasting-set': ['€ 29,00', '€ 72,50/kg', null],
}

/** DE zapis → EN zapis („€ 1.234,50/kg" → „€1,234.50/kg"). */
const toEn = (de: string) =>
  de.replace('€ ', '€').replace(/[.,]/g, (c) => (c === '.' ? ',' : '.'))

for (const [slug, [price, unit, kg]] of Object.entries(PRICES)) {
  const p = productBySlug(slug)
  ok(`proizvod postoji: ${slug}`, Boolean(p))
  if (!p) continue
  const small = p.sizes[0]
  ok(`${slug}: manje pakovanje je prvo`, p.sizes.every((s) => s.grams >= small.grams))
  for (const lang of LANGS) {
    const want = (s: string) => (lang === 'de' ? nb(s) : toEn(s))
    eq(`${slug} cena ${lang}`, formatPrice(small.priceCents, lang), want(price))
    eq(`${slug} Grundpreis ${lang}`, formatUnitPrice(small.priceCents, small.grams, lang), want(unit))
    if (kg) {
      const big = p.sizes.find((s) => s.grams === 1000)
      ok(`${slug}: ima 1 kg`, Boolean(big))
      if (big) eq(`${slug} cena 1 kg ${lang}`, formatPrice(big.priceCents, lang), want(kg))
    }
  }
}

for (const p of products) {
  if (p.kind === 'gear') {
    eq(`${p.slug}: oprema nema pakovanja`, p.sizes.length, 0)
    ok(`${p.slug}: cena opreme je ceo broj centi ili null`, p.priceCents === null || Number.isInteger(p.priceCents))
  } else {
    ok(`${p.slug}: ima pakovanje`, p.sizes.length > 0)
    ok(`${p.slug}: cene i grami su celi pozitivni brojevi`, p.sizes.every((s) => Number.isInteger(s.priceCents) && s.priceCents > 0 && Number.isInteger(s.grams) && s.grams > 0))
    ok(`${p.slug}: Grundpreis je u listi provere`, p.slug in PRICES)
  }
  if (p.kind === 'coffee') eq(`${p.slug}: pakovanja 250 g i 1 kg`, p.sizes.map((s) => s.grams).join(','), '250,1000')
}

// oprema: kuvalo € 169, mlin i dripper bez cene dok korisnik ne odluči (PrAG)
eq('kuvalo € 169,00', formatPrice(productBySlug('gooseneck-kettle')?.priceCents ?? 0, 'de'), nb('€ 169,00'))
eq('mlin bez cene', productBySlug('burr-grinder')?.priceCents, null)
eq('dripper bez cene', productBySlug('ceramic-dripper')?.priceCents, null)

// ============================================================================================
// 2. Pretplata, poklon i Probierset: cene se računaju, a ceo tekst mora biti tačno kao tekstovi.md
// ============================================================================================

const sub = sections.subscription
const example = productBySlug(sub.example.product)
const exampleSize = example?.sizes.find((s) => s.grams === sub.example.grams)
ok('primer pretplate postoji (On Repeat 250 g)', Boolean(exampleSize))
const exampleCents = exampleSize ? subscriptionPriceCents(exampleSize.priceCents) : 0
eq('pretplata: On Repeat sa popustom (centi)', exampleCents, 1215)
eq('pretplata: Grundpreis primera DE', formatUnitPrice(exampleCents, sub.example.grams, 'de'), nb('€ 48,60/kg'))
eq('Surprise me: Grundpreis DE', formatUnitPrice(sub.surprise.priceCents, sub.surprise.grams, 'de'), nb('€ 76,00/kg'))
const GIFT: Record<number, string> = { 3: '€ 127,50', 6: '€ 255,00', 12: '€ 510,00' }
eq('poklon: 3, 6 i 12 isporuka', sub.giftDeliveries.join(','), '3,6,12')
for (const n of sub.giftDeliveries) eq(`poklon ${n} isporuka DE`, formatPrice(giftPriceCents(n), 'de'), nb(GIFT[n] ?? '?'))

const option = (id: 'yours' | 'surprise') => sub.options.find((o) => o.id === id)?.text ?? { en: '', de: '' }
const tasting = productBySlug(sections.tastingSet.product)?.sizes[0]

const filled: Record<Lang, Record<string, string>> = { en: {}, de: {} }
for (const lang of LANGS) {
  const price = (c: number) => formatPrice(c, lang)
  filled[lang].yours = fill(option('yours')[lang], {
    price: price(exampleCents),
    was: price(exampleSize?.priceCents ?? 0),
    unit: formatUnitPrice(exampleCents, sub.example.grams, lang),
  })
  filled[lang].surprise = fill(option('surprise')[lang], {
    price: price(sub.surprise.priceCents),
    unit: formatUnitPrice(sub.surprise.priceCents, sub.surprise.grams, lang),
    shipping: price(shop.shipping.feeCents),
  })
  filled[lang].gift = fill(sub.gift.text[lang], { p3: price(giftPriceCents(3)), p6: price(giftPriceCents(6)), p12: price(giftPriceCents(12)) })
  filled[lang].tasting = fill(sections.tastingSet.text[lang], {
    price: price(tasting?.priceCents ?? 0),
    unit: formatUnitPrice(tasting?.priceCents ?? 0, tasting?.grams ?? 1, lang),
  })
}

const EXACT: Record<Lang, Record<string, string>> = {
  en: {
    yours: 'Pick any coffee and grind, 1 to 3 bags of 250 g, every 2 or 4 weeks. You save 10 % on every delivery. For example, On Repeat for €12.15 instead of €13.50 (€48.60/kg).',
    surprise: "Every 4 weeks we send two different coffees we're excited about, 2 × 250 g, with a card on how to brew them. €38.00 per delivery (€76.00/kg), plus €4.50 shipping.",
    gift: 'As a gift: 3, 6 or 12 deliveries of Surprise me, paid once, ends by itself. 3 deliveries €127.50, 6 deliveries €255.00, 12 deliveries €510.00, shipping included in the price.',
    tasting: "Guji, Nyeri, Huila Pink Bourbon and Tarrazú Honey side by side, with a card for your notes. Brew them one after another and you'll know what you like. €29.00 (€72.50/kg), incl. VAT, plus shipping.",
  },
  de: {
    yours: 'Wähle Kaffee und Mahlgrad, 1 bis 3 Packungen à 250 g, alle 2 oder 4 Wochen. Du sparst 10 % bei jeder Lieferung. Zum Beispiel On Repeat um € 12,15 statt € 13,50 (€ 48,60/kg).',
    surprise: 'Alle 4 Wochen schicken wir dir zwei verschiedene Kaffees, die uns gerade begeistern, 2 × 250 g, mit einer Karte zur Zubereitung. € 38,00 pro Lieferung (€ 76,00/kg), zzgl. € 4,50 Versand.',
    gift: 'Als Geschenk: 3, 6 oder 12 Lieferungen „Überrasch mich“, einmal bezahlt, endet von selbst. 3 Lieferungen € 127,50, 6 Lieferungen € 255,00, 12 Lieferungen € 510,00, Versand im Preis enthalten.',
    tasting: 'Guji, Nyeri, Huila Pink Bourbon und Tarrazú Honey nebeneinander, mit einer Karte für deine Notizen. Brüh sie nacheinander, dann weißt du, was dir schmeckt. € 29,00 (€ 72,50/kg), inkl. MwSt., zzgl. Versand.',
  },
}
for (const lang of LANGS) {
  for (const key of Object.keys(EXACT[lang])) eq(`tekst sa cenom: ${key} ${lang}`, filled[lang][key], nb(EXACT[lang][key]))
}

// dostava: brojevi u tekstovima su isti kao shop.shipping (i cart.ts)
const euros = (c: number, lang: Lang) => (c % 100 === 0 ? (lang === 'de' ? `€${NBSP}${c / 100}` : `€${c / 100}`) : formatPrice(c, lang))
for (const lang of LANGS) {
  const fee = euros(shop.shipping.feeCents, lang)
  const free = euros(shop.shipping.freeFromCents, lang)
  ok(`dostava u tekstu ${lang}`, shop.shippingInfo.text[lang].includes(fee) && shop.shippingInfo.text[lang].includes(free), `${fee} / ${free}`)
  ok(`traka nad prodavnicom ${lang}`, shop.bar[lang].includes(free), free)
}

// ============================================================================================
// 3. Slugovi, SIP kartice, slike proizvoda, filteri (Z9)
// ============================================================================================

const slugs = products.map((p) => p.slug)
eq('slugovi su jedinstveni', new Set(slugs).size, slugs.length)
ok('slugovi su URL-bezbedni', slugs.every((s) => /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(s)))
eq('6 kafa', products.filter((p) => p.kind === 'coffee').length, 6)
eq('1 set', products.filter((p) => p.kind === 'set').length, 1)
eq('3 komada opreme', products.filter((p) => p.kind === 'gear').length, 3)

eq('3 SIP kartice', chapters.sipCards.length, 3)
for (const [i, card] of chapters.sipCards.entries()) {
  const p = productBySlug(card.product)
  ok(`SIP kartica ${i + 1} pokazuje na postojeći proizvod`, Boolean(p), card.product)
  ok(`SIP kartica ${i + 1}: kafa sa 250 g`, p?.kind === 'coffee' && p.sizes.some((s) => s.grams === 250))
}
eq('SIP kartice: Guji, Huila, On Repeat', chapters.sipCards.map((c) => c.product).join(','), 'guji,huila-pink-bourbon,on-repeat')

for (const p of products) {
  const set = p.kind === 'gear' ? media.gear : media.bags
  ok(`${p.slug}: slika postoji u media.${p.kind === 'gear' ? 'gear' : 'bags'}`, p.image in set, p.image)
}
for (const key of Object.keys(media.bags)) {
  ok(`kesa ${key} koristi bar jedna kafa`, products.some((p) => p.kind === 'coffee' && p.image === key))
}

type Filter = { brew?: BrewGroup[]; flavor?: FlavorGroup[]; roast?: RoastGroup[]; type?: TypeGroup[] }
/** Ista pravila kao Z9: unutar grupe „ili", između grupa „i"; set i oprema ispadaju uz Brew/Flavor/Roast; oprema bez cene se ne prikazuje. */
function count(f: Filter): number {
  const any = <T>(want: T[] | undefined, have: T[]) => !want?.length || want.some((w) => have.includes(w))
  const coffeeOnly = Boolean(f.brew?.length || f.flavor?.length || f.roast?.length)
  return products.filter((p: Product) => {
    if (p.kind === 'gear' && p.priceCents == null) return false
    if (coffeeOnly && p.kind !== 'coffee') return false
    return any(f.brew, p.brew) && any(f.flavor, p.flavor) && any(f.roast, p.roastGroups) && any(f.type, [p.type])
  }).length
}
const FILTERS: [string, Filter, number][] = [
  ['Espresso', { brew: ['espresso'] }, 4],
  ['Filter', { brew: ['filter'] }, 5],
  ['Fruity & floral', { flavor: ['fruity'] }, 4],
  ['Chocolate & nuts', { flavor: ['chocolate'] }, 3],
  ['Light', { roast: ['light'] }, 3],
  ['Medium', { roast: ['medium'] }, 3],
  ['Medium-dark', { roast: ['medium-dark'] }, 1],
  ['Decaf', { type: ['decaf'] }, 1],
  ['Sets', { type: ['set'] }, 1],
  ['Fruity & floral + Espresso', { flavor: ['fruity'], brew: ['espresso'] }, 2],
  ['Type Coffee (sa kofeinom)', { type: ['coffee'] }, 5],
  ['Equipment (samo sa cenom)', { type: ['equipment'] }, 1],
  ['bez filtera', {}, 8],
]
for (const [label, f, n] of FILTERS) eq(`filter ${label}`, count(f), n)
eq('Huila je light i medium', productBySlug('huila-pink-bourbon')?.roastGroups.join(','), 'light,medium')

// ============================================================================================
// 4. Svi stringovi: L polja, oznake {…}, nelomljivi razmak, [FEHLT], linkovi
// ============================================================================================

/** Dozvoljene oznake: config (brand…) i one koje popunjavaju komponente. */
const TOKENS = new Set(['brand', 'email', 'wholesale', 'phone', 'n', 'q', 'name', 'size', 'place', 'price', 'was', 'unit', 'shipping', 'amount', 'p3', 'p6', 'p12'])
/** alt="" je dozvoljen samo za dekor (Z3: pozadine prodavnice). */
const EMPTY_OK = new Set(['media.photos.shop-bg-1.alt', 'media.photos.shop-bg-2.alt'])
const SECTION_IDS = new Set(['top', 'grind', 'pour', 'sip', 'find-your-cup', 'subscription', 'tasting-set', 'about', 'brew-guide', 'contact', 'footer', 'main'])
const ROUTES = new Set(['/', '/credits', ...legalPages.map((p) => `/${p.slug}`)])

const roots: Record<string, unknown> = { site, chapters, products, shop, sections, legal, legalPages, credits, media, steamCredit }
const strings: { path: string; text: string }[] = []
let lFields = 0

const tokensOf = (s: string) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort().join(',')

function walk(value: unknown, path: string) {
  if (typeof value === 'string') {
    strings.push({ path, text: value })
    return
  }
  if (Array.isArray(value)) {
    value.forEach((v, i) => walk(v, `${path}.${i}`))
    return
  }
  if (!value || typeof value !== 'object') return
  const obj = value as Record<string, unknown>
  if ('en' in obj || 'de' in obj) {
    lFields++
    const { en, de } = obj as Partial<L<unknown>>
    ok(`L polje ima en i de: ${path}`, en !== undefined && de !== undefined)
    ok(`L polje nema druge ključeve: ${path}`, Object.keys(obj).every((k) => k === 'en' || k === 'de'))
    if (typeof en === 'string' || typeof de === 'string') {
      ok(`L polje je tekst na oba jezika: ${path}`, typeof en === 'string' && typeof de === 'string')
      if (!EMPTY_OK.has(path)) ok(`L polje nije prazno: ${path}`, Boolean(en) && Boolean(de))
      eq(`iste oznake {…} na en i de: ${path}`, tokensOf(String(de ?? '')), tokensOf(String(en ?? '')))
    } else if (Array.isArray(en) || Array.isArray(de)) {
      ok(`L niz je niz na oba jezika: ${path}`, Array.isArray(en) && Array.isArray(de))
      if (Array.isArray(en) && Array.isArray(de)) {
        eq(`L niz iste dužine: ${path}`, de.length, en.length)
        ok(`L niz bez praznih stavki: ${path}`, [...en, ...de].every((s) => typeof s === 'string' && s.length > 0))
      }
    }
    walk(en, `${path}.en`)
    walk(de, `${path}.de`)
    return
  }
  for (const [k, v] of Object.entries(obj)) {
    if (k === 'href' && typeof v === 'string') {
      const [route, hash] = v.split('#')
      const good =
        (route === '' && SECTION_IDS.has(hash)) ||
        (hash === undefined && ROUTES.has(route)) ||
        (/^\/\?brew=(filter|espresso)$/.test(route) && hash === 'find-your-cup') ||
        v === 'mailto:{email}' ||
        /^\/licenses\/OFL-\w+\.txt$/.test(v)
      ok(`link vodi na sekciju ili rutu sajta: ${path}.href`, good, v)
    }
    walk(v, `${path}.${k}`)
  }
}
for (const [name, value] of Object.entries(roots)) walk(value, name)

ok('pronađena su L polja', lFields > 300, String(lFields))
for (const { path, text } of strings) {
  const unknown = [...text.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).filter((t) => !TOKENS.has(t))
  ok(`poznate oznake {…}: ${path}`, unknown.length === 0, unknown.join(', '))
  ok(`nelomljivi razmak (broj + jedinica, „€ "): ${path}`, nb(text) === text, text)
  ok(`bez [FEHLT]/NEPROVERENO/TODO u tekstu: ${path}`, !/\[FEHLT|NEPROVERENO|TODO/.test(text))
  ok(`bez dvostrukog razmaka i razmaka na kraju: ${path}`, !/ {2}|^\s|\s$/.test(text))
}

// ============================================================================================
// 5. Ime brenda samo u src/config/site.ts (plan, Interfejs 7)
// ============================================================================================

// domen e-mail adrese bez TLD-a (grep iz plana traži i njega); ime se ne piše ovde, da grep nađe samo config
const mailDomain = brand.email.split('@')[1]?.split('.')[0] ?? brand.email
const forbidden = [brand.name, mailDomain, brand.email, brand.wholesale, brand.phone].map((s) => s.toLowerCase())
for (const { path, text } of strings) {
  const hit = forbidden.find((f) => text.toLowerCase().includes(f))
  ok(`bez imena brenda u sadržaju: ${path}`, !hit, hit)
}
const contentDir = new URL('../src/content/', import.meta.url)
for (const file of readdirSync(contentDir).filter((f) => f.endsWith('.ts'))) {
  const source = readFileSync(new URL(file, contentDir), 'utf8').toLowerCase()
  const hit = forbidden.find((f) => source.includes(f))
  ok(`bez imena brenda u izvoru: src/content/${file}`, !hit, hit)
}

// ============================================================================================
// 6. Pravne stranice, Credits, Cookies
// ============================================================================================

eq('šest pravnih stranica', legalPages.map((p) => p.slug).join(','), 'impressum,datenschutz,agb,versand,widerruf,cookies')
for (const p of legalPages) {
  for (const lang of LANGS) {
    eq(`${p.slug}: items = naslovi stavki ${lang}`, p.items[lang].join('|'), p.entries.map((e) => e.title[lang]).join('|'))
    const title = fill(p.docTitle[lang])
    ok(`${p.slug}: document.title ≤ 60 znakova ${lang}`, title.length <= 60, title)
  }
}
for (const lang of LANGS) {
  const title = fill(site.seo.title[lang])
  ok(`SEO naslov ≤ 60 znakova ${lang}`, title.length <= 60, title)
  ok(`meta description ≤ 160 znakova ${lang}`, fill(site.seo.description[lang]).length <= 160)
  const cookies = legalPages.find((p) => p.slug === 'cookies')?.body?.[lang] ?? ''
  ok(`Cookies tekst navodi ključeve iz storageKeys ${lang}`, cookies.includes(storageKeys.lang) && cookies.includes(storageKeys.cart))
}
eq('footer „Vertrag widerrufen" vodi na /widerruf', sections.footer.withdraw.href, '/widerruf')

const photoIds = Object.keys(media.photos)
eq('Credits: red za svaku fotografiju', Object.keys(credits.photos).sort().join(','), [...photoIds].sort().join(','))
const usedPhotos = [...sections.about.photos, sections.contact.photo, ...sections.brewGuide.steps.map((s) => s.photo).filter((p) => p !== null)]
for (const id of usedPhotos) ok(`fotografija postoji u media.photos: ${id}`, id in media.photos)
eq('Brew guide: koraci 1 i 2 su GUIDE-1 i GUIDE-2, korak 3 SIP poster', sections.brewGuide.steps.map((s) => s.photo ?? 'sip').join(','), 'guide-1,guide-2,sip')
ok('kontakt fotografija ima natpis Symbolbild', media.photos['kontakt-1']?.caption?.de === 'Symbolbild')

// ============================================================================================
// 7. Mediji sa `ready: true` postoje u public/ (inače 404)
// ============================================================================================

const pub = (src: string) => new URL(`../public${src}`, import.meta.url)
const fileOk = (label: string, src: string) => ok(`${label}: ${src}`, existsSync(pub(src)))
for (const p of Object.values(media.photos)) {
  ok(`fotografija ima autora i licencu: ${p.id}`, Boolean(p.credit.author && p.credit.url.startsWith('https://') && p.credit.license && p.credit.licenseUrl.startsWith('https://')))
  if (p.ready) [p.sm.src, p.lg.src].forEach((src) => fileOk('fotografija postoji', src))
}
for (const s of Object.values(media.seq)) {
  if (s.ready) [s.manifest, s.poster.d.src, s.poster.m.src].forEach((src) => fileOk(`sekvenca ${s.id}`, src))
}
for (const [which, s] of Object.entries(media.steam)) {
  if (s.ready) [...s.sources.d, ...s.sources.m].forEach((v) => fileOk(`para ${which}`, v.src))
}
for (const img of [...Object.values(media.bags), ...Object.values(media.gear)]) {
  if (img.ready) img.srcs.forEach((v) => fileOk('slika proizvoda', v.src))
}
for (const f of credits.fonts.files) fileOk('licenca fonta', f.href)
ok('Credits pare: autor i link', Boolean(steamCredit.author && steamCredit.url.startsWith('https://')))

// primer koji koristi kartica SIP (aria-label), da format veličine ostane „250 g"
eq('SIP aria-label primer', fill(chapters.card.aria.en, { name: 'Guji', place: 'Ethiopia', price: formatPrice(1790, 'en'), size: formatGrams(250, 'en') }), nb('Guji, Ethiopia, €17.90 for 250 g. View coffee'))

if (failed) {
  console.error(`\n${failed} od ${passed + failed} provera nije prošlo.`)
  process.exit(1)
}
console.log(`check-content: svih ${passed} provera je prošlo (${lFields} L polja, ${strings.length} stringova).`)
