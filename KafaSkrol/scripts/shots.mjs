// Snimci i provera (uzor: RealEstates/scripts/shots.mjs).
// Upotreba: node scripts/shots.mjs <outDir> [url] [--reduced]
//   url podrazumevano http://localhost:4173/ (npx vite preview)
//   PW_CHROMIUM=/putanja/do/chrome  ako Playwright nema svoj Chromium (npr. /opt/pw-browsers/chromium)
// Na 390×844 i 1440×900 snima početnu po sekcijama (id-jevi iz plana, Interfejs 8), modal /p/guji,
// /impressum i /credits. Prijavljuje greške u konzoli, neuspele zahteve (≥ 400 i prekinute),
// zahteve ka drugom originu i horizontalni skrol. Na desktopu meri osu wdth fonta Archivo.
// Tačke priče (granice i sredine segmenata iz src/story/timeline.ts) dodaje Z12.
import { mkdirSync } from 'node:fs'
import { chromium } from 'playwright'

const out = process.argv[2] ?? 'shots'
const url = process.argv[3] && !process.argv[3].startsWith('--') ? process.argv[3] : 'http://localhost:4173/'
const reduced = process.argv.includes('--reduced')
const origin = new URL(url).origin
const sections = ['top', 'grind', 'pour', 'sip', 'find-your-cup', 'subscription', 'tasting-set', 'about', 'brew-guide', 'contact', 'footer']
const pages = [['modal', 'p/guji'], ['impressum', 'impressum'], ['credits', 'credits']]
const wait = (ms) => new Promise((r) => setTimeout(r, ms))

mkdirSync(out, { recursive: true })
const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM || undefined })
let failures = 0

for (const [label, viewport] of [['mobile', { width: 390, height: 844 }], ['desktop', { width: 1440, height: 900 }]]) {
  const mobile = label === 'mobile'
  const ctx = await browser.newContext({
    viewport,
    deviceScaleFactor: 1,
    reducedMotion: reduced ? 'reduce' : 'no-preference',
    hasTouch: mobile,
    isMobile: mobile,
  })
  const page = await ctx.newPage()
  const errors = []
  const requests = []
  page.on('console', (m) => m.type() === 'error' && errors.push(`console: ${m.text()}`))
  page.on('pageerror', (e) => errors.push(`pageerror: ${e}`))
  page.on('requestfailed', (r) => requests.push(`failed: ${r.url()} (${r.failure()?.errorText})`))
  page.on('response', (r) => r.status() >= 400 && requests.push(`${r.status()}: ${r.url()}`))
  page.on('request', (r) => {
    const u = new URL(r.url())
    if (!['data:', 'blob:'].includes(u.protocol) && u.origin !== origin) requests.push(`other origin: ${r.url()}`)
  })
  const tag = `${out}/${label}${reduced ? '-reduced' : ''}`
  const overflow = async (where) => {
    const px = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
    if (px > 0) errors.push(`horizontal overflow ${px}px (${where})`)
  }

  await page.goto(url, { waitUntil: 'networkidle' })
  await wait(1500)
  await page.screenshot({ path: `${tag}-00-first.png` })
  await overflow('home')

  let i = 1
  for (const id of sections) {
    const y = await page.evaluate((id) => {
      const el = document.getElementById(id)
      return el ? el.getBoundingClientRect().top + window.scrollY : null
    }, id)
    if (y === null) {
      errors.push(`missing section #${id}`)
      continue
    }
    await page.evaluate((y) => window.scrollTo(0, y), y)
    await wait(1200)
    await page.screenshot({ path: `${tag}-${String(i++).padStart(2, '0')}-${id}.png` })
  }

  if (!mobile) {
    // osa wdth: „GRIND" sa wdth 88 mora biti 0,85–0,92 širine sa wdth 100 (plan, Z1)
    const ratio = await page.evaluate(async () => {
      await document.fonts.load('800 96px "Archivo Variable"', 'GRIND')
      const width = (wdth) => {
        const s = document.createElement('span')
        s.textContent = 'GRIND'
        s.style.cssText = `position:absolute;visibility:hidden;white-space:nowrap;font:800 96px "Archivo Variable";font-variation-settings:"wdth" ${wdth}`
        document.body.append(s)
        const w = s.getBoundingClientRect().width
        s.remove()
        return w
      }
      return { ratio: width(88) / width(100), loaded: document.fonts.check('800 96px "Archivo Variable"', 'GRIND') }
    })
    console.log(`[${label}] Archivo wdth 88/100 = ${ratio.ratio.toFixed(3)} (font učitan: ${ratio.loaded})`)
    if (!ratio.loaded || ratio.ratio < 0.85 || ratio.ratio > 0.92) errors.push(`Archivo wdth ratio ${ratio.ratio.toFixed(3)} van 0,85–0,92`)
  }

  for (const [name, path] of pages) {
    await page.goto(new URL(path, url).href, { waitUntil: 'networkidle' })
    await wait(1000)
    await page.screenshot({ path: `${tag}-${String(i++).padStart(2, '0')}-${name}.png` })
    await overflow(path)
  }

  const issues = [...errors, ...requests]
  console.log(`\n[${label}${reduced ? ' reduced' : ''}] ${issues.length ? 'ISSUES:' : 'OK'}`)
  issues.forEach((e) => console.log('  -', e.slice(0, 300)))
  failures += issues.length
  await ctx.close()
}
await browser.close()
process.exit(failures ? 1 : 0)
