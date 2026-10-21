import { SplitText } from '../components/ui/SplitText'
import { reviews, type Review } from '../data/content'
import { useLang } from '../i18n/LangContext'

function Row({ items, reverse, duration }: { items: Review[]; reverse?: boolean; duration: number }) {
  const { lang } = useLang()
  const cards = [...items, ...items]
  return (
    <div className="marquee relative flex overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_10%,black_90%,transparent)]">
      <ul className="marquee-track flex w-max shrink-0 gap-5 pr-5" style={{ '--marquee-duration': `${duration}s`, animationDirection: reverse ? 'reverse' : 'normal' } as React.CSSProperties}>
        {cards.map((r, i) => (
          <li key={i} aria-hidden={i >= items.length} className="w-[78vw] shrink-0 rounded-[2px] border border-sand/12 bg-stone-900 p-7 transition-colors duration-500 hover:border-ember/60 sm:w-[420px]">
            <p className="font-serif text-2xl leading-snug md:text-[1.7rem]">“{r.quote[lang]}”</p>
            <div className="mt-6 flex flex-col gap-1 border-t border-sand/10 pt-4 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
              <span className="text-sm">{r.name}</span>
              <span className="eyebrow">{r.place}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}

/** Two opposing marquee rows with edge fades (after 21st.dev “Testimonials Marquee”). */
export function Reviews() {
  const { t } = useLang()
  const half = Math.ceil(reviews.length / 2)
  return (
    <section id="reviews" aria-labelledby="reviews-title" className="section-y overflow-hidden bg-stone-900/40">
      <div className="gutter">
        <p className="eyebrow">{t.reviews.eyebrow}</p>
        <SplitText as="h2" id="reviews-title" text={t.reviews.title} className="display mt-6 text-5xl md:text-7xl" />
      </div>
      <div className="mt-16 flex flex-col gap-5">
        <Row items={reviews.slice(0, half)} duration={55} />
        <Row items={reviews.slice(half)} duration={65} reverse />
      </div>
    </section>
  )
}
