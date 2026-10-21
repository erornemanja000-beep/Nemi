import { useLayoutEffect, useRef, useState } from 'react'
import { Img } from '../components/ui/Img'
import { SplitText } from '../components/ui/SplitText'
import { neighborhoods } from '../data/content'
import { useLang } from '../i18n/LangContext'
import { gsap, ScrollTrigger } from '../lib/motion'

function CoastMap({ active, label }: { active: number; label: string }) {
  return (
    <svg viewBox="0 0 100 90" className="h-full w-full" role="img" aria-label={label}>
      <defs>
        <pattern id="grid" width="6" height="6" patternUnits="userSpaceOnUse">
          <path d="M6 0H0V6" fill="none" stroke="rgba(233,226,214,.06)" strokeWidth=".3" />
        </pattern>
      </defs>
      <rect width="100" height="90" fill="url(#grid)" />
      {/* fictional coastline */}
      <path d="M0 52 C12 48 18 60 30 56 S48 66 58 62 S72 48 82 44 S94 30 100 28 V90 H0Z" fill="rgba(43,58,85,.55)" />
      <path d="M0 52 C12 48 18 60 30 56 S48 66 58 62 S72 48 82 44 S94 30 100 28" fill="none" stroke="#c8a46a" strokeWidth=".4" strokeDasharray="1 1.2" />
      <path d="M8 10 C24 20 30 30 28 40 S40 50 52 48 S70 30 78 22" fill="none" stroke="rgba(233,226,214,.25)" strokeWidth=".35" />
      {neighborhoods.map((n, i) => (
        <g key={n.name} transform={`translate(${n.pin[0]} ${n.pin[1]})`}>
          {i === active && <circle r="2.2" fill="#e07a3f" className="pulse-ring" style={{ transformBox: 'fill-box', transformOrigin: 'center' }} />}
          <circle r={i === active ? 1.6 : 1} fill={i === active ? '#e07a3f' : '#e9e2d6'} style={{ transition: 'all .6s' }} />
          <text x="3" y="1" fontSize="2.6" fill={i === active ? '#e9e2d6' : 'rgba(233,226,214,.45)'} fontFamily="JetBrains Mono, monospace">
            {n.name.toUpperCase()}
          </text>
        </g>
      ))}
    </svg>
  )
}

export function Locations() {
  const { t, lang } = useLang()
  const root = useRef<HTMLElement>(null)
  const [active, setActive] = useState(0)

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>('.area-item').forEach((el, i) => {
        ScrollTrigger.create({ trigger: el, start: 'top 55%', end: 'bottom 55%', onToggle: (s) => s.isActive && setActive(i) })
      })
    }, root)
    return () => ctx.revert()
  }, [])

  return (
    <section ref={root} id="areas" aria-labelledby="areas-title" className="gutter section-y relative">
      <p className="eyebrow">{t.areas.eyebrow}</p>
      <SplitText as="h2" id="areas-title" text={t.areas.title} className="display mt-6 max-w-[16ch] text-5xl md:text-7xl" />
      <div className="mt-16 grid gap-10 md:mt-24 md:grid-cols-2 md:gap-[6vw]">
        <ol className="relative">
          {neighborhoods.map((n, i) => (
            <li key={n.name} className="area-item border-t border-sand/15 py-10 md:flex md:min-h-[62vh] md:flex-col md:justify-center md:py-0">
              <div className="flex items-baseline gap-5">
                <span className={`font-mono text-xs transition-colors duration-500 ${active === i ? 'text-ember' : 'text-sand-muted'}`}>0{i + 1}</span>
                <h3 className={`display text-[13vw] transition-all duration-700 md:text-[5.2vw] ${active === i ? 'translate-x-0 text-sand' : 'text-sand/30 md:-translate-x-2'}`}>{n.name}</h3>
              </div>
              <p className="ml-10 mt-4 max-w-sm text-sand/75">{n.blurb[lang]}</p>
              <p className="eyebrow ml-10 mt-4 text-gold">
                {n.listings} {t.areas.listings}
              </p>
              <div className="mt-6 aspect-[4/3] overflow-hidden rounded-[2px] md:hidden">
                <Img name={n.photo} sizes="92vw" className="h-full w-full object-cover" />
              </div>
            </li>
          ))}
        </ol>
        <div className="hidden md:block">
          <div className="sticky top-[12vh] h-[76vh]">
            <div className="relative h-full overflow-hidden rounded-[2px] bg-stone-900">
              {neighborhoods.map((n, i) => (
                <div
                  key={n.name}
                  className="absolute inset-0 transition-[clip-path] duration-[1.2s] ease-[var(--ease-expo)]"
                  style={{ clipPath: i === active ? 'inset(0% 0% 0% 0%)' : i < active ? 'inset(0% 0% 100% 0%)' : 'inset(100% 0% 0% 0%)', zIndex: i === active ? 2 : 1 }}
                >
                  <Img name={n.photo} sizes="45vw" className={`h-full w-full object-cover transition-transform duration-[1.6s] ease-[var(--ease-expo)] ${i === active ? 'scale-100' : 'scale-110'}`} />
                </div>
              ))}
              <div className="absolute inset-0 z-[3] bg-gradient-to-t from-ink/70 to-transparent" />
              <div className="absolute bottom-5 right-5 z-[4] w-[46%] rounded-[2px] border border-sand/15 bg-ink/70 p-2 backdrop-blur-md">
                <CoastMap active={active} label={t.areas.map} />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-10 rounded-[2px] border border-sand/15 bg-stone-900 p-3 md:hidden">
        <CoastMap active={active} label={t.areas.map} />
      </div>
    </section>
  )
}
