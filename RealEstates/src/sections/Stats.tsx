import { useLayoutEffect, useRef } from 'react'
import { Counter } from '../components/ui/Counter'
import { SplitText } from '../components/ui/SplitText'
import { useLang } from '../i18n/LangContext'
import { gsap, prefersReducedMotion } from '../lib/motion'

export function Stats() {
  const { t, lang } = useLang()
  const root = useRef<HTMLElement>(null)
  const locale = lang === 'de' ? 'de-DE' : 'en-GB'

  useLayoutEffect(() => {
    if (prefersReducedMotion()) return
    const ctx = gsap.context(() => {
      gsap.from('.stat-line', { scaleX: 0, transformOrigin: 'left', duration: 1.6, stagger: 0.12, scrollTrigger: { trigger: '.stat-grid', start: 'top 85%' } })
      gsap.from('.stat-label', { opacity: 0, y: 16, duration: 1, stagger: 0.12, delay: 0.3, scrollTrigger: { trigger: '.stat-grid', start: 'top 85%' } })
    }, root)
    return () => ctx.revert()
  }, [])

  return (
    <section ref={root} id="main" aria-labelledby="stats-title" className="gutter section-y relative overflow-hidden">
      <div className="breath -right-[10%] top-0 h-[40vw] w-[40vw] bg-dusk" />
      <p className="eyebrow">{t.stats.eyebrow}</p>
      <SplitText as="h2" id="stats-title" text={t.stats.title} className="display mt-6 max-w-[18ch] text-5xl md:text-7xl" />
      <dl className="stat-grid mt-16 grid grid-cols-2 gap-x-6 gap-y-14 md:mt-24 md:grid-cols-4">
        {t.stats.items.map((s) => (
          <div key={s.label}>
            <dd className="font-serif text-[15vw] leading-none text-sand tabular-nums md:text-[6.4vw]">
              <Counter value={s.value} decimals={s.decimals ?? 0} prefix={s.prefix ?? ''} suffix={s.suffix} locale={locale} />
            </dd>
            <div className="stat-line mt-5 h-px w-full bg-gold/70" />
            <dt className="stat-label mt-4 text-sm text-sand-muted">{s.label}</dt>
          </div>
        ))}
      </dl>
    </section>
  )
}
