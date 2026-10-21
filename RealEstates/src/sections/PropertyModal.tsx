import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Img } from '../components/ui/Img'
import { MagneticButton } from '../components/ui/MagneticButton'
import { properties, type Property } from '../data/content'
import { formatPrice, useLang } from '../i18n/LangContext'
import { gsap, lockScroll, prefersReducedMotion } from '../lib/motion'

function FloorPlan({ p }: { p: Property }) {
  const { lang, t } = useLang()
  const root = useRef<SVGSVGElement>(null)
  useLayoutEffect(() => {
    if (prefersReducedMotion()) return
    const ctx = gsap.context(() => {
      gsap.fromTo('.plan-room', { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.6, stagger: 0.08, ease: 'power2.inOut', delay: 0.5 })
      gsap.from('.plan-label', { opacity: 0, duration: 0.8, stagger: 0.06, delay: 1.2 })
    }, root)
    return () => ctx.revert()
  }, [p.slug])
  return (
    <svg ref={root} viewBox="-2 -2 104 74" className="w-full" role="img" aria-label={`${t.modal.plan}: ${p.name}`}>
      {p.plan.map((r, i) => (
        <g key={i}>
          <rect className="plan-room" x={r.x} y={r.y} width={r.w} height={r.h} pathLength={1} strokeDasharray={1} fill={i === 0 ? 'rgba(224,122,63,0.08)' : 'none'} stroke="#c8a46a" strokeWidth="0.4" />
          <text className="plan-label" x={r.x + 2} y={r.y + 5} fill="#a39b8d" fontSize="2.6" fontFamily="JetBrains Mono, monospace">
            {r.label[lang].toUpperCase()}
          </text>
        </g>
      ))}
      <path d="M44 70 v-3 h10 v3" stroke="#e07a3f" strokeWidth="0.6" fill="none" />
    </svg>
  )
}

function Booking({ p }: { p: Property }) {
  const { t } = useLang()
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const submit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const data = new FormData(e.currentTarget)
    if (!String(data.get('name') ?? '').trim() || String(data.get('phone') ?? '').replace(/\D/g, '').length < 6) {
      setError(`${t.contact.errors.name} / ${t.modal.phone}`)
      return
    }
    setError('')
    setSent(true)
  }
  if (sent)
    return (
      <p role="status" className="rounded-[2px] border border-gold/40 p-5 text-sand">
        <span className="mr-2 text-ember">✓</span>
        {t.modal.booked}
      </p>
    )
  return (
    <form onSubmit={submit} noValidate className="grid gap-3 sm:grid-cols-3" aria-label={`${t.modal.book} — ${p.name}`}>
      <label className="sr-only" htmlFor="bk-name">{t.modal.name}</label>
      <input id="bk-name" name="name" placeholder={t.modal.name} autoComplete="name" className="border-b border-sand/25 bg-transparent py-3 outline-none placeholder:text-sand-muted focus:border-ember" />
      <label className="sr-only" htmlFor="bk-phone">{t.modal.phone}</label>
      <input id="bk-phone" name="phone" type="tel" placeholder={t.modal.phone} autoComplete="tel" className="border-b border-sand/25 bg-transparent py-3 outline-none placeholder:text-sand-muted focus:border-ember" />
      <label className="sr-only" htmlFor="bk-date">{t.modal.date}</label>
      <input id="bk-date" name="date" type="date" aria-label={t.modal.date} className="border-b border-sand/25 bg-transparent py-3 text-sand-muted outline-none focus:border-ember [color-scheme:dark]" />
      {error && <p role="alert" className="text-sm text-ember sm:col-span-3">{error}</p>}
      <div className="mt-3 sm:col-span-3">
        <MagneticButton type="submit">{t.modal.book}</MagneticButton>
      </div>
    </form>
  )
}

export function PropertyModal() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const { t, lang } = useLang()
  const p = properties.find((x) => x.slug === slug)
  const root = useRef<HTMLDivElement>(null)
  const panel = useRef<HTMLDivElement>(null)
  const [idx, setIdx] = useState(0)
  const lastFocus = useRef<Element | null>(null)

  const close = () => {
    const done = () => navigate('/', { preventScrollReset: true })
    if (prefersReducedMotion() || !root.current) return done()
    gsap.to(panel.current, { yPercent: 100, duration: 0.7, ease: 'expo.in' })
    gsap.to(root.current, { opacity: 0, duration: 0.5, delay: 0.3, onComplete: done })
  }

  useEffect(() => {
    if (!p) navigate('/', { replace: true })
  }, [p, navigate])

  useLayoutEffect(() => {
    if (!p) return
    lastFocus.current = document.activeElement
    lockScroll(true)
    if (!prefersReducedMotion()) {
      gsap.fromTo(root.current, { opacity: 0 }, { opacity: 1, duration: 0.4 })
      gsap.fromTo(panel.current, { yPercent: 100 }, { yPercent: 0, duration: 1.1, ease: 'expo.out' })
      gsap.from('.modal-reveal', { y: 30, opacity: 0, stagger: 0.07, delay: 0.35, duration: 1 })
    }
    panel.current?.querySelector<HTMLElement>('[data-autofocus]')?.focus()
    return () => {
      lockScroll(false)
      ;(lastFocus.current as HTMLElement | null)?.focus?.()
    }
  }, [p])

  // Esc to close + focus trap
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close()
      if (e.key === 'ArrowRight') setIdx((i) => (p ? (i + 1) % p.gallery.length : 0))
      if (e.key === 'ArrowLeft') setIdx((i) => (p ? (i - 1 + p.gallery.length) % p.gallery.length : 0))
      if (e.key !== 'Tab' || !panel.current) return
      const f = panel.current.querySelectorAll<HTMLElement>('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])')
      const first = f[0]
      const last = f[f.length - 1]
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [p])

  useEffect(() => {
    if (prefersReducedMotion()) return
    gsap.fromTo('.gallery-main img', { scale: 1.08, opacity: 0.4 }, { scale: 1, opacity: 1, duration: 1.2 })
  }, [idx])

  if (!p) return null
  const shot = p.gallery[idx]

  return (
    <div ref={root} className="fixed inset-0 z-[80] bg-ink/80 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="modal-title" onClick={(e) => e.target === root.current && close()}>
      <div ref={panel} data-lenis-prevent className="absolute inset-x-0 bottom-0 top-0 overflow-y-auto bg-stone-900 md:top-[4vh] md:mx-[3vw] md:rounded-t-[4px]">
        <div className="sticky top-0 z-10 flex items-center justify-between bg-stone-900/90 px-[var(--gutter)] py-4 backdrop-blur">
          <span className="eyebrow">{p.kind[lang]} · {p.area}</span>
          <button data-autofocus onClick={close} className="group flex h-11 items-center gap-3 rounded-full border border-sand/25 px-5 text-sm hover:border-sand">
            {t.modal.close}
            <span aria-hidden="true" className="transition-transform duration-500 group-hover:rotate-90">✕</span>
          </button>
        </div>

        <div className="gutter grid gap-10 pb-20 pt-4 lg:grid-cols-[1.4fr_1fr] lg:gap-16">
          <div>
            <div className="gallery-main relative aspect-[4/3] overflow-hidden rounded-[2px] bg-ink" data-cursor={t.featured.drag}>
              <Img key={shot} name={shot} eager sizes="(min-width: 1024px) 58vw, 100vw" className="h-full w-full object-cover" />
              <div className="absolute bottom-4 right-4 flex gap-2">
                <button onClick={() => setIdx((idx - 1 + p.gallery.length) % p.gallery.length)} aria-label={t.modal.prev} className="flex h-11 w-11 items-center justify-center rounded-full bg-ink/60 backdrop-blur hover:bg-ember hover:text-ink">←</button>
                <button onClick={() => setIdx((idx + 1) % p.gallery.length)} aria-label={t.modal.next} className="flex h-11 w-11 items-center justify-center rounded-full bg-ink/60 backdrop-blur hover:bg-ember hover:text-ink">→</button>
              </div>
              <span className="eyebrow absolute left-4 top-4 rounded-full bg-ink/60 px-3 py-1.5 text-sand backdrop-blur">{String(idx + 1).padStart(2, '0')} / {String(p.gallery.length).padStart(2, '0')}</span>
            </div>
            <div className="mt-3 grid grid-cols-4 gap-3" role="group" aria-label={t.modal.gallery}>
              {p.gallery.map((g, i) => (
                <button key={g} onClick={() => setIdx(i)} aria-pressed={i === idx} className={`aspect-[4/3] overflow-hidden rounded-[2px] transition-opacity ${i === idx ? 'opacity-100 ring-1 ring-ember' : 'opacity-50 hover:opacity-100'}`}>
                  <Img name={g} sizes="20vw" className="h-full w-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          <div>
            <h2 id="modal-title" className="modal-reveal display text-5xl md:text-7xl">{p.name}</h2>
            <p className="modal-reveal mt-4 font-serif text-3xl text-gold">{formatPrice(p.price, lang)}</p>
            <p className="modal-reveal mt-6 leading-relaxed text-sand/80">{p.summary[lang]}</p>
            <dl className="modal-reveal mt-8 grid grid-cols-4 border-y border-sand/15 py-5 font-mono text-[11px] uppercase tracking-wider">
              {[
                [t.featured.size, `${p.size} m²`],
                [t.featured.beds, p.beds],
                [t.featured.baths, p.baths],
                [t.modal.year, p.year],
              ].map(([k, v]) => (
                <div key={String(k)}>
                  <dt className="text-sand-muted">{k}</dt>
                  <dd className="mt-2 text-base text-sand">{v}</dd>
                </div>
              ))}
            </dl>
            <h3 className="modal-reveal eyebrow mt-10">{t.modal.plan}</h3>
            <div className="modal-reveal mt-4">
              <FloorPlan p={p} />
            </div>
            <h3 className="modal-reveal eyebrow mb-4 mt-10">{t.modal.book}</h3>
            <div className="modal-reveal">
              <Booking p={p} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
