import { useLayoutEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Img } from '../components/ui/Img'
import { SplitText } from '../components/ui/SplitText'
import { properties, type Property } from '../data/content'
import { formatPrice, useLang } from '../i18n/LangContext'
import { gsap } from '../lib/motion'

function Card({ p, index }: { p: Property; index: number }) {
  const { t, lang } = useLang()
  const card = useRef<HTMLAnchorElement>(null)

  // 3D tilt toward the pointer (inspired by 21st.dev “Property Preview Card” / “3D Flip Card”)
  const onMove = (e: React.PointerEvent) => {
    if (e.pointerType !== 'mouse' || !card.current) return
    const r = card.current.getBoundingClientRect()
    const x = (e.clientX - r.left) / r.width - 0.5
    const y = (e.clientY - r.top) / r.height - 0.5
    gsap.to(card.current, { rotateY: x * 10, rotateX: -y * 8, duration: 0.6, ease: 'power3.out' })
    gsap.to(card.current.querySelector('.card-shine'), { opacity: 0.25, x: x * 120, y: y * 120, duration: 0.6 })
  }
  const onLeave = () => {
    gsap.to(card.current, { rotateY: 0, rotateX: 0, duration: 1, ease: 'elastic.out(1, 0.5)' })
    gsap.to(card.current?.querySelector('.card-shine') ?? null, { opacity: 0, duration: 0.6 })
  }

  return (
    <div className="feat-card shrink-0 [perspective:1200px] md:w-[min(34vw,520px)]">
      <Link
        ref={card}
        to={`/property/${p.slug}`}
        data-cursor={t.featured.view}
        onPointerMove={onMove}
        onPointerLeave={onLeave}
        className="group block [transform-style:preserve-3d]"
        aria-label={`${p.name}, ${p.area}, ${formatPrice(p.price, lang)}`}
      >
        <div className="relative aspect-[4/5] overflow-hidden rounded-[2px] bg-stone-900">
          <Img name={p.cover} sizes="(min-width: 768px) 34vw, 92vw" className="h-full w-full scale-[1.04] object-cover transition-transform duration-[1.4s] ease-[var(--ease-expo)] group-hover:scale-[1.12]" />
          <div className="card-shine pointer-events-none absolute -inset-1/4 bg-[radial-gradient(circle,rgba(255,236,210,.9),transparent_55%)] opacity-0 mix-blend-overlay" />
          <div className="absolute inset-0 bg-gradient-to-t from-ink/85 via-ink/10 to-transparent" />
          <span className="eyebrow absolute left-5 top-5 rounded-full bg-ink/50 px-3 py-1.5 text-sand backdrop-blur">
            0{index + 1} · {p.kind[lang]}
          </span>
          {/* details pop up on hover (always visible on touch) */}
          <div className="absolute inset-x-0 bottom-0 p-5 md:p-6">
            <p className="font-serif text-3xl text-gold md:translate-y-6 md:opacity-0 md:transition-all md:duration-700 md:ease-[var(--ease-expo)] md:group-hover:translate-y-0 md:group-hover:opacity-100 md:group-focus-visible:translate-y-0 md:group-focus-visible:opacity-100">
              {formatPrice(p.price, lang)}
            </p>
            <dl className="mt-3 grid grid-cols-3 gap-2 border-t border-sand/20 pt-3 font-mono text-[11px] uppercase tracking-wider text-sand/80 md:translate-y-8 md:opacity-0 md:transition-all md:delay-75 md:duration-700 md:ease-[var(--ease-expo)] md:group-hover:translate-y-0 md:group-hover:opacity-100 md:group-focus-visible:translate-y-0 md:group-focus-visible:opacity-100">
              <div><dt className="text-sand-muted">{t.featured.beds}</dt><dd className="mt-1 text-sand">{p.beds}</dd></div>
              <div><dt className="text-sand-muted">{t.featured.baths}</dt><dd className="mt-1 text-sand">{p.baths}</dd></div>
              <div><dt className="text-sand-muted">{t.featured.size}</dt><dd className="mt-1 text-sand">{p.size} m²</dd></div>
            </dl>
          </div>
        </div>
        <div className="mt-5 flex items-baseline justify-between gap-4">
          <h3 className="font-serif text-3xl md:text-4xl">{p.name}</h3>
          <span className="eyebrow shrink-0">{p.area}</span>
        </div>
      </Link>
    </div>
  )
}

export function Featured() {
  const { t } = useLang()
  const root = useRef<HTMLElement>(null)
  const track = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    const mm = gsap.matchMedia()
    mm.add('(min-width: 768px) and (prefers-reduced-motion: no-preference)', () => {
      const el = track.current!
      const distance = () => el.scrollWidth - window.innerWidth
      const tween = gsap.to(el, {
        x: () => -distance(),
        ease: 'none',
        scrollTrigger: {
          trigger: root.current,
          start: 'top top',
          end: () => `+=${distance()}`,
          pin: true,
          scrub: 0.8,
          invalidateOnRefresh: true,
        },
      })
      // cards lean slightly with scroll velocity
      gsap.utils.toArray<HTMLElement>('.feat-card', el).forEach((c, i) => {
        gsap.from(c, { y: 80 + i * 20, opacity: 0, duration: 1.2, scrollTrigger: { trigger: c, containerAnimation: tween, start: 'left 95%' } })
      })
    })
    mm.add('(max-width: 767px) and (prefers-reduced-motion: no-preference)', () => {
      gsap.utils.toArray<HTMLElement>('.feat-card').forEach((c) => {
        gsap.from(c, { y: 60, opacity: 0, duration: 1.2, scrollTrigger: { trigger: c, start: 'top 90%' } })
      })
    })
    return () => mm.revert()
  }, [])

  return (
    <section ref={root} id="properties" aria-labelledby="featured-title" className="relative overflow-hidden bg-ink md:flex md:h-[100svh] md:items-center">
      <div ref={track} className="gutter flex flex-col gap-14 py-[var(--section-y)] md:flex-row md:items-end md:gap-[4vw] md:py-0 md:pr-[12vw]">
        <div className="shrink-0 md:w-[32vw] md:self-center">
          <p className="eyebrow">{t.featured.eyebrow}</p>
          <SplitText as="h2" id="featured-title" text={t.featured.title} className="display mt-6 text-5xl md:text-[4.6vw]" />
          <p className="eyebrow mt-10 hidden items-center gap-3 md:flex">
            {t.featured.drag}
            <span className="inline-block h-px w-16 bg-sand/40" />→
          </p>
        </div>
        {properties.map((p, i) => (
          <Card key={p.slug} p={p} index={i} />
        ))}
      </div>
    </section>
  )
}
