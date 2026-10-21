// Usage: node scripts/shots.mjs <outDir> [url] [--reduced]
// Captures every section at 390px and 1440px, reports console errors and horizontal overflow.
import { chromium } from 'playwright'

const out = process.argv[2] ?? 'shots'
const url = process.argv[3] && !process.argv[3].startsWith('--') ? process.argv[3] : 'http://localhost:4173/'
const reduced = process.argv.includes('--reduced')
const sections = ['main', 'properties', 'areas', 'process', 'walkthrough', 'mortgage', 'team', 'reviews', 'contact']
const wait = (ms) => new Promise((r) => setTimeout(r, ms))

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
let failures = 0
for (const [label, viewport] of [['mobile', { width: 390, height: 844 }], ['desktop', { width: 1440, height: 900 }]]) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion: reduced ? 'reduce' : 'no-preference', hasTouch: label === 'mobile', isMobile: label === 'mobile' })
  const page = await ctx.newPage()
  const errors = []
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()))
  page.on('pageerror', (e) => errors.push(String(e)))
  await page.goto(url, { waitUntil: 'networkidle' })
  await page.waitForFunction(() => !document.querySelector('[role="status"][aria-live="polite"].fixed'), null, { timeout: 20000 }).catch(() => errors.push('loader did not finish'))
  await wait(2500)
  const tag = `${out}/${label}${reduced ? '-reduced' : ''}`
  await page.screenshot({ path: `${tag}-00-hero.png` })

  const heroH = await page.evaluate(() => document.querySelector('#top')?.getBoundingClientRect().height ?? 0)
  for (const f of reduced ? [] : [0.3, 0.55, 0.8, 0.97]) {
    await page.evaluate((y) => window.scrollTo(0, y), (heroH - viewport.height) * f)
    await wait(2200)
    await page.screenshot({ path: `${tag}-01-hero-${Math.round(f * 100)}.png` })
  }
  let i = 2
  for (const id of sections) {
    const y = await page.evaluate((id) => {
      const el = document.getElementById(id)
      if (!el) return null
      // pinned sections live inside a pin-spacer; scroll a bit into them so the pin is engaged
      const top = (el.parentElement?.classList.contains('pin-spacer') ? el.parentElement : el).getBoundingClientRect().top + window.scrollY
      return top
    }, id)
    if (y === null) {
      errors.push(`missing section #${id}`)
      continue
    }
    const extra = ['properties', 'walkthrough'].includes(id) && !reduced ? viewport.height * 1.2 : 40
    await page.evaluate((y) => window.scrollTo(0, y), y + extra)
    await wait(1800)
    await page.screenshot({ path: `${tag}-${String(i++).padStart(2, '0')}-${id}.png` })
  }
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
  await wait(1800)
  await page.screenshot({ path: `${tag}-${String(i++).padStart(2, '0')}-footer.png` })

  // property modal
  await page.goto(url + '#/property/villa-solenne', { waitUntil: 'networkidle' })
  await page.waitForFunction(() => !document.querySelector('[role="status"][aria-live="polite"].fixed'), null, { timeout: 20000 }).catch(() => {})
  await wait(2500)
  await page.screenshot({ path: `${tag}-${String(i++).padStart(2, '0')}-modal.png` })

  // contact form validation
  await page.goto(url, { waitUntil: 'networkidle' })
  await page.waitForFunction(() => !document.querySelector('[role="status"][aria-live="polite"].fixed'), null, { timeout: 20000 }).catch(() => {})
  await page.evaluate(() => document.getElementById('contact')?.scrollIntoView())
  await wait(1500)
  await page.click('form[name="contact"] button[type="submit"]')
  await wait(500)
  const alerts = await page.locator('form[name="contact"] [role="alert"]').count()
  if (alerts !== 3) errors.push(`expected 3 validation errors, got ${alerts}`)
  await page.fill('#c-name', 'Test Person')
  await page.fill('#c-email', 'test@example.com')
  await page.fill('#c-message', 'Looking for a villa with a sea view.')
  await page.click('form[name="contact"] button[type="submit"]')
  await wait(2500)
  if (!(await page.locator('#contact [role="status"]').count())) errors.push('contact success message missing')
  await page.screenshot({ path: `${tag}-${String(i++).padStart(2, '0')}-contact-success.png` })

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
  if (overflow > 0) errors.push(`horizontal overflow ${overflow}px`)
  console.log(`\n[${label}${reduced ? ' reduced' : ''}] ${errors.length ? 'ISSUES:' : 'OK'}`)
  errors.forEach((e) => console.log('  -', e.slice(0, 300)))
  failures += errors.length
  await ctx.close()
}
await browser.close()
process.exit(failures ? 1 : 0)
