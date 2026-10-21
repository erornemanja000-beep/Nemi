import { useLayoutEffect, useRef } from 'react'
import { Img } from '../components/ui/Img'
import { MagneticButton } from '../components/ui/MagneticButton'
import { SplitText } from '../components/ui/SplitText'
import { agents } from '../data/content'
import { useLang } from '../i18n/LangContext'
import { gsap, prefersReducedMotion } from '../lib/motion'

export function Team() {
  const { t, lang } = useLang()
  const root = useRef<HTMLElement>(null)

  useLayoutEffect(() => {
    if (prefersReducedMotion()) return
    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>('.agent').forEach((el, i) => {
        gsap.fromTo(el.querySelector('.agent-mask'), { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.4, delay: (i % 4) * 0.1, ease: 'expo.inOut', scrollTrigger: { trigger: el, start: 'top 88%' } })
      })
    }, root)
    return () => ctx.revert()
  }, [])

  return (
    <section ref={root} id="team" aria-labelledby="team-title" className="gutter section-y">
      <p className="eyebrow">{t.team.eyebrow}</p>
      <SplitText as="h2" id="team-title" text={t.team.title} className="display mt-6 max-w-[14ch] text-5xl md:text-7xl" />
      <ul className="mt-16 grid gap-x-6 gap-y-14 sm:grid-cols-2 lg:grid-cols-4">
        {agents.map((a) => (
          <li key={a.name} className="agent group">
            <div className="agent-mask relative aspect-[3/4] overflow-hidden rounded-[2px] bg-stone-900">
              <Img name={a.photo} sizes="(min-width: 1024px) 24vw, (min-width: 640px) 46vw, 92vw" className="h-full w-full object-cover grayscale transition-[filter,transform] duration-[1.2s] ease-[var(--ease-expo)] group-hover:scale-105 group-hover:grayscale-0" />
              <div className="absolute inset-x-0 bottom-0 h-0 bg-ember/90 mix-blend-multiply transition-[height] duration-700 ease-[var(--ease-expo)] group-hover:h-1.5" />
              <span className="eyebrow absolute left-4 top-4 rounded-full bg-ink/60 px-3 py-1.5 text-sand backdrop-blur">{a.langs}</span>
            </div>
            <h3 className="mt-5 font-serif text-3xl">{a.name}</h3>
            <p className="mt-1 text-sm text-sand-muted">{a.role[lang]}</p>
            <div className="mt-5 flex flex-wrap gap-2">
              <MagneticButton href={`tel:${a.phone.replace(/\s/g, '')}`} variant="outline" className="!px-5 !py-3">{t.team.call}</MagneticButton>
              <MagneticButton href={`mailto:${a.email}`} variant="ghost" className="!px-4 !py-3 underline decoration-sand/30 underline-offset-4">{t.team.email}</MagneticButton>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
