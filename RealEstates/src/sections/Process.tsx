import { useLayoutEffect, useRef } from 'react'
import { SplitText } from '../components/ui/SplitText'
import { useLang } from '../i18n/LangContext'
import { gsap, prefersReducedMotion } from '../lib/motion'

/** Vertical timeline whose line is drawn by scroll (after 21st.dev “Scroll animated timeline”). */
export function Process() {
  const { t } = useLang()
  const root = useRef<HTMLElement>(null)

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      if (prefersReducedMotion()) {
        gsap.set('.tl-line', { scaleY: 1 })
        return
      }
      gsap.fromTo('.tl-line', { scaleY: 0 }, { scaleY: 1, ease: 'none', scrollTrigger: { trigger: '.tl', start: 'top 60%', end: 'bottom 60%', scrub: 0.5 } })
      gsap.utils.toArray<HTMLElement>('.tl-step').forEach((el) => {
        const dot = el.querySelector('.tl-dot')
        const tl = gsap.timeline({ scrollTrigger: { trigger: el, start: 'top 62%', toggleActions: 'play none none reverse' } })
        tl.to(dot, { backgroundColor: '#e07a3f', borderColor: '#e07a3f', scale: 1.3, duration: 0.5 })
          .from(el.querySelectorAll('.tl-pop'), { y: 40, opacity: 0, stagger: 0.08, duration: 1 }, 0)
      })
    }, root)
    return () => ctx.revert()
  }, [])

  return (
    <section ref={root} id="process" aria-labelledby="process-title" className="gutter section-y relative overflow-hidden bg-stone-900">
      <div className="breath left-[-15%] top-[30%] h-[50vw] w-[50vw] bg-ember/60" />
      <div className="relative grid gap-12 md:grid-cols-[1fr_1.3fr] md:gap-[6vw]">
        <div className="md:sticky md:top-[18vh] md:self-start">
          <p className="eyebrow">{t.process.eyebrow}</p>
          <SplitText as="h2" id="process-title" text={t.process.title} className="display mt-6 text-5xl md:text-7xl" />
        </div>
        <ol className="tl relative">
          <div aria-hidden="true" className="absolute bottom-0 left-[11px] top-0 w-px bg-sand/15">
            <div className="tl-line h-full w-full origin-top bg-gradient-to-b from-gold via-ember to-ember" />
          </div>
          {t.process.steps.map((s, i) => (
            <li key={s.t} className="tl-step relative pb-20 pl-14 last:pb-0 md:pb-28">
              <span className="tl-dot absolute left-0 top-2 h-[23px] w-[23px] rounded-full border border-sand/40 bg-stone-900" aria-hidden="true" />
              <p className="tl-pop font-mono text-xs text-gold">0{i + 1} / 0{t.process.steps.length}</p>
              <h3 className="tl-pop display mt-3 text-4xl md:text-5xl">{s.t}</h3>
              <p className="tl-pop mt-4 max-w-md leading-relaxed text-sand/75">{s.d}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
