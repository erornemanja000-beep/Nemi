import './style.css'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'
import { loadContent, render } from './content'
import { CoverCanvas, FrameLoader, FrameSequence, loadImage, loadManifest } from './sequence'

gsap.registerPlugin(ScrollTrigger)

type SeqName = 'descent' | 'grow' | 'lefka' | 'pefko' | 'enter' | 'aerial'

/** Still that stands in for a clip until its frames arrive. */
const POSTER: Record<SeqName, string> = {
  descent: './media/img/hero.jpg',
  grow: './media/img/plot.jpg',
  lefka: './media/img/lefka.jpg',
  pefko: './media/img/pefko.jpg',
  enter: './media/img/selene.jpg',
  aerial: './media/img/aerial.jpg',
}

const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches
const $ = <T extends Element = HTMLElement>(sel: string, root: ParentNode = document) => root.querySelector<T>(sel)!
const $$ = <T extends Element = HTMLElement>(sel: string, root: ParentNode = document) =>
  Array.from(root.querySelectorAll<T>(sel))

async function boot() {
  const [content, manifest] = await Promise.all([loadContent(), loadManifest()])
  document.title = `${content.brand.name} — ${content.brand.descriptor}`
  document.documentElement.lang = content.lang
  $('#app').innerHTML = render(content)

  const seq = Object.fromEntries(
    Object.entries(manifest).map(([name, info]) => [name, new FrameSequence(name, info)]),
  ) as Record<SeqName, FrameSequence>

  const loader = new FrameLoader(6)
  ;(Object.keys(POSTER) as SeqName[]).forEach((n) => loader.enqueue(seq[n]))
  const posters = Promise.all(
    (Object.keys(POSTER) as SeqName[]).map((n) =>
      loadImage(POSTER[n]).then((img) => (seq[n].poster = img)).catch(() => {}),
    ),
  )

  const lenis = new Lenis({ duration: reduceMotion ? 0 : 1.15, smoothWheel: !reduceMotion })
  lenis.on('scroll', ScrollTrigger.update)
  gsap.ticker.add((t) => lenis.raf(t * 1000))
  gsap.ticker.lagSmoothing(0)
  lenis.stop()

  await introLoader(seq.descent, posters)
  await document.fonts.ready
  fitText()

  const canvases = setupStages(seq, loader, content.locale)
  setupSections(lenis)
  setupChrome(lenis)

  window.addEventListener('resize', () => {
    fitText()
    canvases.forEach((c) => c.resize())
    ScrollTrigger.refresh()
  })

  lenis.start()
  revealPage()
}

/* ---------------------------------------------------------------- loader */

function introLoader(first: FrameSequence, posters: Promise<unknown>) {
  const pct = $('#loader-pct')
  const bar = $('#loader-bar')
  const shown = { v: 0 }
  let postersReady = false
  posters.then(() => (postersReady = true))

  return new Promise<void>((resolve) => {
    const started = performance.now()
    const tick = () => {
      // Ready once the hero still is in and a coarse pass of the first clip can play.
      const target = Math.min(1, (first.progress / 0.25) * 0.85 + (postersReady ? 0.15 : 0))
      shown.v += (target - shown.v) * 0.12
      const p = Math.round(shown.v * 100)
      pct.textContent = String(p)
      bar.style.transform = `scaleX(${shown.v})`
      const elapsed = performance.now() - started
      if ((p >= 99 && elapsed > 900) || elapsed > 9000) {
        gsap.ticker.remove(tick)
        pct.textContent = '100'
        bar.style.transform = 'scaleX(1)'
        resolve()
      }
    }
    gsap.ticker.add(tick)
  })
}

function revealPage() {
  const tl = gsap.timeline({ defaults: { ease: 'expo.inOut' } })
  tl.to('.loader__mark', { yPercent: -30, opacity: 0, duration: 0.9 })
    .to('.loader__foot, .loader__bar', { opacity: 0, duration: 0.4 }, 0)
    .to('#loader', { clipPath: 'inset(0% 0% 100% 0%)', duration: 1.2 }, 0.25)
    .from('.arrival__mark', { yPercent: 60, duration: 1.4, ease: 'expo.out' }, 0.8)
    .from('.arrival__intro > *, .arrival__hint', { y: 24, opacity: 0, stagger: 0.08, duration: 1, ease: 'power3.out' }, 1.0)
    .from('.hdr', { y: -20, opacity: 0, duration: 0.9, ease: 'power3.out' }, 1.0)
    .set('#loader', { display: 'none' })
}

/* ----------------------------------------------------------- scroll stages */

/** Title block for a villa: index, name sliding up out of a mask, then the summary row. */
function titleIn(el: HTMLElement) {
  return gsap
    .timeline()
    .to(el, { autoAlpha: 1, y: 0, duration: 0.01 })
    .fromTo(el.querySelector('.vt__index'), { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.5 }, 0)
    .fromTo(el.querySelectorAll('.vt__name .mask__in'), { yPercent: 105 }, { yPercent: 0, stagger: 0.12, duration: 0.8, ease: 'power3.out' }, 0.05)
    .fromTo(el.querySelector('.vt__foot'), { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 }, 0.35)
}

function titleOut(el: HTMLElement) {
  return gsap
    .timeline()
    .to(el.querySelectorAll('.vt__name .mask__in'), { yPercent: -130, stagger: 0.08, duration: 0.6, ease: 'power2.in' }, 0)
    .to(el.querySelectorAll('.vt__index, .vt__foot'), { opacity: 0, y: -14, duration: 0.4 }, 0)
}

function setupStages(seq: Record<SeqName, FrameSequence>, loader: FrameLoader, locale: string) {
  const arrivalCv = new CoverCanvas($<HTMLCanvasElement>('#cv-arrival'))
  const layerCv = $$('.stage--villas .layer').map((l) => new CoverCanvas($<HTMLCanvasElement>('canvas', l)))
  const planCv = new CoverCanvas($<HTMLCanvasElement>('#cv-plan'))

  const A = { d: 0, g: 0 }
  const V = { lefka: 0, pefko: 0, enter: 0 }
  const P = { a: 0 }

  // Repaint every tick; CoverCanvas skips work when the image has not changed.
  gsap.ticker.add(() => {
    arrivalCv.draw(A.g > 0.5 ? seq.grow.image(A.g) : seq.descent.image(A.d))
    layerCv[0].draw(seq.lefka.image(V.lefka))
    layerCv[1].draw(seq.pefko.image(V.pefko))
    layerCv[2].draw(seq.enter.image(V.enter))
    planCv.draw(seq.aerial.image(P.a))
  })

  // Arrival: coast → plot → the villa grows → its name.
  const yearEl = $('#build-year')
  const yr = { v: Number(yearEl.textContent) }
  const buildTo = Number(yearEl.dataset.to)
  const kyma = $('.stage--arrival .vt')
  gsap.set(kyma, { autoAlpha: 0 })

  gsap
    .timeline({
      defaults: { ease: 'none' },
      scrollTrigger: { trigger: '.stage--arrival', start: 'top top', end: 'bottom bottom', scrub: true },
    })
    .to(A, { d: seq.descent.count - 1, duration: 4.4 }, 0)
    .to('.arrival__mark', { yPercent: 40, opacity: 0, duration: 1.6, ease: 'power1.in' }, 0)
    .to('.arrival__intro, .arrival__hint', { opacity: 0, y: -30, duration: 0.9 }, 0)
    .fromTo('.arrival__plot .mono', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 }, 3.3)
    .fromTo('.arrival__plotline .mask__in', { yPercent: 110 }, { yPercent: 0, stagger: 0.05, duration: 0.7, ease: 'power3.out' }, 3.5)
    .to('.arrival__plot', { opacity: 0, y: -40, duration: 0.6 }, 5.3)
    .to(A, { g: seq.grow.count - 1, duration: 4.0 }, 4.6)
    .fromTo('.arrival__build', { opacity: 0 }, { opacity: 1, duration: 0.4 }, 5.0)
    .to(yr, { v: buildTo, duration: 3.4, onUpdate: () => (yearEl.textContent = String(Math.round(yr.v))) }, 5.0)
    .to('.arrival__build', { opacity: 0, duration: 0.4 }, 8.5)
    .add(titleIn(kyma), 8.6)
    .to({}, { duration: 0.6 })

  // Villas: three clips stacked, each wiped in from below over the previous one.
  const layers = $$('.stage--villas .layer')
  const titles = $$('.stage--villas .vt')
  gsap.set(titles, { autoAlpha: 0 })
  gsap.set(layers.slice(1), { clipPath: 'inset(100% 0% 0% 0%)' })

  const vt = gsap.timeline({
    defaults: { ease: 'none' },
    scrollTrigger: {
      trigger: '.stage--villas',
      start: 'top top',
      end: 'bottom bottom',
      scrub: true,
      onEnter: () => loader.prioritise(seq.lefka),
    },
  })
  vt.to(V, { lefka: seq.lefka.count - 1, duration: 10 }, 0)
    .add(titleIn(titles[0]), 0.3)
    .add(titleOut(titles[0]), 8.0)
    .to(layers[1], { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.8, ease: 'power2.inOut' }, 8.6)
    .to(layers[0].querySelector('canvas'), { scale: 1.12, duration: 1.8, ease: 'power1.in' }, 8.6)
    .to(V, { pefko: seq.pefko.count - 1, duration: 10 }, 8.6)
    .add(titleIn(titles[1]), 10.4)
    .add(titleOut(titles[1]), 17.6)
    .to(layers[2], { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.8, ease: 'power2.inOut' }, 18.2)
    .to(layers[1].querySelector('canvas'), { scale: 1.12, duration: 1.8, ease: 'power1.in' }, 18.2)
    .to(V, { enter: seq.enter.count - 1, duration: 10 }, 18.2)
    .add(titleIn(titles[2]), 20.0)
    .add(titleOut(titles[2]), 24.6)
    .to('#villas-dim', { opacity: 1, duration: 1.4 }, 28.4)

  // Seen from above: the aerial clip rises and turns, figures count up.
  const stats = $$('.stat__v')
  const counters = stats.map(() => ({ v: 0 }))
  const pt = gsap.timeline({
    defaults: { ease: 'none' },
    scrollTrigger: {
      trigger: '.stage--plan',
      start: 'top top',
      end: 'bottom bottom',
      scrub: true,
      onEnter: () => loader.prioritise(seq.aerial),
    },
  })
  pt.to(P, { a: seq.aerial.count - 1, duration: 10 }, 0)
    .fromTo('.plan__title .mask__in', { yPercent: 110 }, { yPercent: 0, stagger: 0.08, duration: 1.2, ease: 'power3.out' }, 0.2)
    .fromTo('.plan__h', { scaleX: 0 }, { scaleX: 1, duration: 2.5, ease: 'power2.out' }, 0.5)
    .fromTo('.plan__v', { scaleY: 0 }, { scaleY: 1, duration: 2.5, ease: 'power2.out' }, 0.7)
    .fromTo('.plan__ring', { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 1.5 }, 1.6)
    .fromTo('.stat', { opacity: 0, y: 30 }, { opacity: 1, y: 0, stagger: 0.25, duration: 1 }, 2.0)
  stats.forEach((el, i) => {
    const to = Number(el.dataset.value)
    pt.to(counters[i], { v: to, duration: 4, ease: 'power2.out', onUpdate: () => (el.textContent = Math.round(counters[i].v).toLocaleString(locale)) }, 2.2 + i * 0.3)
  })

  // Prefetch the next clip a little before its section arrives.
  ScrollTrigger.create({ trigger: '.stage--arrival', start: '60% bottom', onEnter: () => loader.prioritise(seq.lefka) })
  ScrollTrigger.create({ trigger: '#process', start: 'top bottom', onEnter: () => loader.prioritise(seq.aerial) })

  return [arrivalCv, ...layerCv, planCv]
}

/* ------------------------------------------------------- regular sections */

function maskUp(selector: string, trigger: string) {
  gsap.fromTo(
    selector,
    { yPercent: 110 },
    { yPercent: 0, stagger: 0.08, duration: 1.1, ease: 'power3.out', scrollTrigger: { trigger, start: 'top 80%' } },
  )
}

function setupSections(lenis: Lenis) {
  // Manifesto: words light up as you read down.
  gsap.fromTo(
    '.manifesto__text .w',
    { opacity: 0.12 },
    { opacity: 1, stagger: 0.1, ease: 'none', scrollTrigger: { trigger: '.manifesto__text', start: 'top 78%', end: 'bottom 45%', scrub: true } },
  )
  $$('.reveal').forEach((el) =>
    gsap.from(el, { y: 40, opacity: 0, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 88%' } }),
  )

  // Index of villas with a cursor-following preview.
  maskUp('.index__title .mask__in', '.index')
  gsap.from('.row', { y: 30, opacity: 0, stagger: 0.08, duration: 0.9, ease: 'power3.out', scrollTrigger: { trigger: '.index__list', start: 'top 85%' } })

  const preview = $('.index__preview')
  const previewImg = $<HTMLImageElement>('img', preview)
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches
  gsap.set(preview, { xPercent: -50, yPercent: -50, scale: 0.6 })
  if (fine) {
    const qx = gsap.quickTo(preview, 'x', { duration: 0.6, ease: 'power3' })
    const qy = gsap.quickTo(preview, 'y', { duration: 0.6, ease: 'power3' })
    window.addEventListener('mousemove', (e) => {
      qx(e.clientX)
      qy(e.clientY)
    })
    $$('.row').forEach((row) => {
      row.addEventListener('mouseenter', () => {
        previewImg.src = row.dataset.img!
        gsap.to(preview, { scale: 1, opacity: 1, duration: 0.5, ease: 'power3.out' })
      })
      row.addEventListener('mouseleave', () => gsap.to(preview, { scale: 0.6, opacity: 0, duration: 0.4 }))
    })
  }
  $$('.row').forEach((row) =>
    row.addEventListener('click', () => {
      const i = Number(row.dataset.villaIndex)
      if (i === 0) {
        const stage = $('.stage--arrival')
        lenis.scrollTo(stage.offsetTop + (stage.offsetHeight - innerHeight) * 0.93)
      } else {
        // Land on each villa's own stretch of the stacked stage.
        const stage = $('.stage--villas')
        const at = [0.06, 0.4, 0.69][i - 1] ?? 0
        lenis.scrollTo(stage.offsetTop + (stage.offsetHeight - innerHeight) * at)
      }
    }),
  )

  // Process: the sticky picture follows the step in view.
  maskUp('.process__title .mask__in', '.process')
  const imgs = $$('[data-step-img]')
  $$('.step').forEach((step) => {
    ScrollTrigger.create({
      trigger: step,
      start: 'top 60%',
      end: 'bottom 60%',
      onToggle: ({ isActive }) => {
        if (!isActive) return
        $$('.step').forEach((s) => s.classList.toggle('is-active', s === step))
        const n = Number(step.dataset.step)
        const pick = imgs.filter((im) => Number(im.dataset.stepImg) <= n).pop() ?? imgs[0]
        imgs.forEach((im) => im.classList.toggle('is-on', im === pick))
      },
    })
  })

  // Contact.
  maskUp('.contact__title .mask__in', '.contact')
  gsap.fromTo('.contact__bg img', { yPercent: -8 }, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: '.contact', start: 'top bottom', end: 'bottom top', scrub: true } })
  gsap.from('.form', { y: 60, opacity: 0, duration: 1.2, ease: 'power3.out', scrollTrigger: { trigger: '.form', start: 'top 90%' } })

  const form = $<HTMLFormElement>('#enquiry')
  form.addEventListener('submit', (e) => {
    e.preventDefault()
    if (!form.reportValidity()) return
    const thanks = $('.form__thanks', form)
    thanks.hidden = false
    gsap.from(thanks, { opacity: 0, y: 10, duration: 0.6 })
    form.reset()
  })
}

/* ------------------------------------------------------- header and rail */

function setupChrome(lenis: Lenis) {
  $$<HTMLAnchorElement>('a[href^="#"]').forEach((a) =>
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href')!
      const target = id === '#top' ? 0 : document.querySelector<HTMLElement>(id)
      if (target === null) return
      e.preventDefault()
      lenis.scrollTo(target as number | HTMLElement, { duration: 1.6 })
    }),
  )

  const fill = $('#rail-fill')
  const pct = $('#rail-pct')
  lenis.on('scroll', (l: Lenis) => {
    fill.style.transform = `scaleY(${l.progress})`
    pct.textContent = String(Math.round(l.progress * 100)).padStart(2, '0')
    $('#hdr').classList.toggle('is-scrolled', window.scrollY > 40)
  })
}

/** Sizes [data-fit] text so a single line spans its container exactly. */
function fitText() {
  const range = document.createRange()
  $$('[data-fit]').forEach((el) => {
    el.style.fontSize = '100px'
    range.selectNodeContents(el)
    const w = range.getBoundingClientRect().width
    el.style.fontSize = `${(100 * el.clientWidth) / w}px`
  })
  const mark = $('.arrival__mark')
  $('.stage--arrival').style.setProperty('--mark-h', `${mark.getBoundingClientRect().height}px`)
  fitWords()
}

/**
 * Big titles wrap between words but a single long word (German "Grundstück") can be wider
 * than its column. Shrink such a title just enough that its longest word fits.
 */
function fitWords() {
  $$('.vt__name, .index__title, .process__title, .plan__title, .contact__title').forEach((el) => {
    el.style.fontSize = ''
    const longest = Math.max(...$$('.mask__in', el).map((w) => w.getBoundingClientRect().width))
    const avail = el.clientWidth
    if (longest > avail) {
      const size = parseFloat(getComputedStyle(el).fontSize)
      el.style.fontSize = `${Math.floor((size * avail * 0.97) / longest)}px`
    }
  })
}

boot()
