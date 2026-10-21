import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { Logo } from '../components/ui/Logo'
import { useLang } from '../i18n/LangContext'
import { img } from '../lib/img'
import { gsap, lockScroll, prefersReducedMotion } from '../lib/motion'

type Props = { sceneReady: boolean; onDone: () => void }

const CRITICAL = ['villa-cypress', 'villa-coast', 'penthouse-dark']

function preload(src: string) {
  return new Promise<void>((resolve) => {
    const i = new Image()
    i.onload = i.onerror = () => resolve()
    i.src = src
  })
}

/** Logo draws itself while fonts, key photos and the 3D scene load; then the page opens like a curtain. */
export function Loader({ sceneReady, onDone }: Props) {
  const { t } = useLang()
  const root = useRef<HTMLDivElement>(null)
  const num = useRef<HTMLSpanElement>(null)
  const bar = useRef<HTMLDivElement>(null)
  const [loaded, setLoaded] = useState(0)
  const total = CRITICAL.length + 2
  const shown = useRef({ v: 0 })
  const finished = useRef(false)

  useEffect(() => {
    lockScroll(true)
    window.scrollTo(0, 0)
    const small = window.innerWidth < 768
    const tick = () => setLoaded((n) => n + 1)
    document.fonts.ready.then(tick)
    CRITICAL.forEach((name) => preload(small ? `${import.meta.env.BASE_URL}images/${name}-sm.webp` : img(name).src).then(tick))
  }, [])

  const ratio = Math.min(1, (loaded + (sceneReady ? 1 : 0)) / total)

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      gsap.to('.logo-path', { strokeDashoffset: 0, duration: 1.8, ease: 'power2.inOut', stagger: 0.25 })
      gsap.from('.logo-sun', { scale: 0, transformOrigin: '50% 50%', duration: 1, delay: 1.2, ease: 'back.out(2)' })
    }, root)
    return () => ctx.revert()
  }, [])

  useEffect(() => {
    gsap.to(shown.current, {
      v: ratio * 100,
      duration: prefersReducedMotion() ? 0.2 : 1.1,
      ease: 'power2.out',
      overwrite: true,
      onUpdate: () => {
        const v = Math.round(shown.current.v)
        if (num.current) num.current.textContent = String(v).padStart(3, '0')
        if (bar.current) bar.current.style.transform = `scaleX(${shown.current.v / 100})`
      },
      onComplete: () => {
        if (ratio >= 1) finish()
      },
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ratio])

  // never trap visitors behind a stalled asset
  useEffect(() => {
    const id = window.setTimeout(() => finish(), 9000)
    return () => window.clearTimeout(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function finish() {
    if (finished.current || !root.current) return
    finished.current = true
    const reduced = prefersReducedMotion()
    const tl = gsap.timeline({
      delay: reduced ? 0 : 0.5,
      onComplete: () => {
        lockScroll(false)
        onDone()
      },
    })
    if (reduced) {
      tl.to(root.current, { opacity: 0, duration: 0.5 })
    } else {
      tl.to('.loader-inner', { opacity: 0, y: -20, duration: 0.6, ease: 'power3.in' }, 0)
        .to('.curtain-top', { yPercent: -100, duration: 1.3, ease: 'expo.inOut' }, 0.4)
        .to('.curtain-bottom', { yPercent: 100, duration: 1.3, ease: 'expo.inOut' }, 0.4)
    }
    tl.add(() => window.dispatchEvent(new Event('vista:reveal')), reduced ? 0.2 : 1.1)
  }

  return (
    <div ref={root} className="fixed inset-0 z-[100]" role="status" aria-live="polite" aria-label={t.loader.loading}>
      <div className="curtain-top absolute inset-x-0 top-0 h-1/2 bg-ink" />
      <div className="curtain-bottom absolute inset-x-0 bottom-0 h-1/2 bg-ink" />
      <div className="loader-inner gutter absolute inset-0 flex flex-col items-center justify-center text-sand">
        <Logo draw withWord={false} className="h-20 w-20 md:h-24 md:w-24" />
        <p className="mt-8 font-serif text-2xl tracking-[0.3em] md:text-3xl">VISTA ESTATES</p>
        <div className="absolute inset-x-[var(--gutter)] bottom-10 flex items-end justify-between gap-6">
          <span className="eyebrow">{t.loader.loading}</span>
          <span className="font-serif text-6xl leading-none tabular-nums md:text-8xl">
            <span ref={num}>000</span>
            <span className="text-ember">%</span>
          </span>
        </div>
        <div className="absolute inset-x-0 bottom-0 h-px bg-stone-600">
          <div ref={bar} className="h-full origin-left scale-x-0 bg-ember" />
        </div>
      </div>
    </div>
  )
}
