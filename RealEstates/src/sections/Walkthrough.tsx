import { useLayoutEffect, useRef, useState } from 'react'
import { Img } from '../components/ui/Img'
import { SplitText } from '../components/ui/SplitText'
import { rooms } from '../data/content'
import { useLang } from '../i18n/LangContext'
import { gsap } from '../lib/motion'
import { useIsMobile, useReducedMotion } from '../lib/useReducedMotion'

const DEPTH = 1400

/** Rooms hang in a CSS 3D corridor; scrolling moves the viewer through them (after 21st.dev “3D Animation” hallway). */
export function Walkthrough() {
  const { t, lang } = useLang()
  const reduced = useReducedMotion()
  const mobile = useIsMobile()
  const sway = mobile ? 4 : 14
  const root = useRef<HTMLElement>(null)
  const stage = useRef<HTMLDivElement>(null)
  const [active, setActive] = useState(0)

  useLayoutEffect(() => {
    if (reduced) return
    const cards = gsap.utils.toArray<HTMLElement>('.room-card', root.current)
    const last = (rooms.length - 1) * DEPTH
    const state = { z: 0 }
    const render = () => {
      if (stage.current) stage.current.style.transform = `translate3d(0,0,${state.z}px)`
      cards.forEach((c, i) => {
        const d = i * DEPTH - state.z
        const o = d < -300 ? 0 : d < 0 ? 1 + d / 300 : Math.max(0, 1 - d / (DEPTH * 2.6))
        c.style.opacity = String(o)
        c.style.visibility = o < 0.01 ? 'hidden' : 'visible'
      })
      setActive(Math.min(rooms.length - 1, Math.max(0, Math.round(state.z / DEPTH))))
    }
    render()
    const ctx = gsap.context(() => {
      gsap.to(state, {
        z: last,
        ease: 'none',
        onUpdate: render,
        scrollTrigger: { trigger: root.current, start: 'top top', end: () => `+=${rooms.length * window.innerHeight}`, pin: true, scrub: 0.8 },
      })
    }, root)
    return () => ctx.revert()
  }, [reduced])

  if (reduced) {
    return (
      <section id="walkthrough" aria-labelledby="walk-title" className="gutter section-y">
        <p className="eyebrow">{t.walk.eyebrow}</p>
        <h2 id="walk-title" className="display mt-6 text-5xl md:text-7xl">{t.walk.title}</h2>
        <div className="mt-12 grid gap-6 md:grid-cols-2">
          {rooms.map((r) => (
            <figure key={r.photo}>
              <Img name={r.photo} sizes="(min-width: 768px) 45vw, 92vw" className="aspect-[16/10] w-full rounded-[2px] object-cover" />
              <figcaption className="eyebrow mt-3">{r.name[lang]}</figcaption>
            </figure>
          ))}
        </div>
      </section>
    )
  }

  return (
    <section ref={root} id="walkthrough" aria-labelledby="walk-title" className="relative h-[100svh] overflow-hidden bg-ink">
      <div className="absolute inset-0 [perspective:900px] [perspective-origin:50%_45%]">
        <div ref={stage} className="absolute inset-0 [transform-style:preserve-3d]">
          {rooms.map((r, i) => (
            <figure
              key={r.photo}
              className="room-card absolute left-1/2 top-1/2 w-[86vw] md:w-[58vw]"
              style={{ transform: `translate(-50%, -50%) translate3d(${i % 2 ? sway : -sway}vw, ${i % 2 ? 4 : -3}vh, ${-i * DEPTH}px)` }}
            >
              <Img name={r.photo} sizes="(min-width: 768px) 58vw, 86vw" className="aspect-[16/10] w-full rounded-[2px] object-cover shadow-[0_40px_120px_-20px_rgba(0,0,0,.8)]" />
              <figcaption className="sr-only">{r.name[lang]}</figcaption>
            </figure>
          ))}
        </div>
      </div>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,rgba(14,13,11,.85)_100%)]" />
      <div className="gutter pointer-events-none absolute inset-x-0 top-0 pt-28">
        <p className="eyebrow">{t.walk.eyebrow}</p>
        <SplitText as="h2" id="walk-title" text={t.walk.title} className="display mt-4 max-w-[12ch] text-4xl md:text-6xl" />
      </div>
      <div className="gutter pointer-events-none absolute inset-x-0 bottom-0 flex items-end justify-between pb-10" aria-live="polite">
        <div className="relative h-[1.1em] w-[64vw] overflow-hidden font-serif text-[12vw] leading-none md:text-[6vw]">
          {rooms.map((r, i) => (
            <span
              key={r.photo}
              className="absolute left-0 top-0 whitespace-nowrap italic transition-transform duration-[900ms] ease-[var(--ease-expo)]"
              style={{ transform: `translateY(${i === active ? 0 : i > active ? 110 : -110}%)` }}
              aria-hidden={i !== active}
            >
              {r.name[lang]}
            </span>
          ))}
        </div>
        <div className="text-right">
          <p className="font-mono text-sm text-gold">
            {String(active + 1).padStart(2, '0')} / {String(rooms.length).padStart(2, '0')}
          </p>
          <p className="eyebrow mt-2">{t.walk.hint}</p>
        </div>
      </div>
    </section>
  )
}
