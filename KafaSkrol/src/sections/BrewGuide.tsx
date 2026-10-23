// Brew guide (skica: sekcija 9b, „3 koraka = 3 poglavlja"). Naslov (kraći na telefonu), recept,
// „You need", tri koraka sa slikom (GUIDE-1, GUIDE-2 i SIP poster), savet, preporuka i dugme.
// Koraci se pojavljuju redom sa razmakom 60 ms (reveal.ts; u reduced motion odmah).
// Dugme „Shop filter coffee" (odluka direktora, z13-izmene.md): href /?brew=filter#find-your-cup je
// rezerva (novi tab, bez JS-a), a običan klik ne učitava stranicu ponovo, nego javi prodavnici filter
// događajem `kafa:shop-filter` (sluša ga Shop, Z9) i skroluje do #find-your-cup.
import type { MouseEvent } from 'react'
import { Button } from '../components/Button'
import { Photo } from '../components/Photo'
import { chapters } from '../content/chapters'
import { media } from '../content/media'
import { sections } from '../content/sections'
import { useLang } from '../i18n/LangContext'
import { scrollToTarget } from '../lib/motion'
import { useReveal } from '../lib/reveal'

const guide = sections.brewGuide
const sipPoster = media.seq.sip
const sipAlt = chapters.items.find((c) => c.id === 'sip')?.alt

/** Ista kutija za sve tri slike, da koraci budu poravnati. */
const FRAME = 'block aspect-[4/3] h-auto w-full rounded-md'
const SIZES = '(min-width: 48rem) 30vw, 100vw'

function StepImage({ photo }: { photo: string | null }) {
  const { tx } = useLang()
  if (photo) return <Photo id={photo} sizes={SIZES} className={`${FRAME} object-cover`} />
  // korak 3: SIP poster (providna pozadina) na boji SIP poglavlja
  const { d, m } = sipPoster.poster
  return (
    <div data-chapter="sip" className={`${FRAME} overflow-hidden bg-bg`}>
      {sipPoster.ready ? (
        <img
          src={m.src}
          srcSet={`${m.src} ${m.width}w, ${d.src} ${d.width}w`}
          sizes={SIZES}
          width={m.width}
          height={m.height}
          alt={sipAlt ? tx(sipAlt) : ''}
          loading="lazy"
          decoding="async"
          className="block h-full w-full object-contain"
        />
      ) : (
        sipAlt && <span role="img" aria-label={tx(sipAlt)} className="block h-full w-full bg-placeholder" />
      )}
    </div>
  )
}

export function BrewGuide() {
  const { tx } = useLang()
  const reveal = useReveal<HTMLOListElement>()

  const shopFilter = (e: MouseEvent<HTMLAnchorElement>) => {
    // novi tab ili prozor: ostaje običan link sa ?brew=filter
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return
    e.preventDefault()
    // Lenis (anchors: true) sluša klik na window i skrolovao bi drugi put, posle promene filtera.
    // Prodavnica se tada skrati, pregledač pomeri skrol (scroll anchoring), pa Lenis promaši cilj.
    e.stopPropagation()
    // prvo skrol (cilj se meri pre promene mreže), pa filter
    scrollToTarget('#find-your-cup')
    window.dispatchEvent(new CustomEvent('kafa:shop-filter', { detail: { brew: 'filter' } }))
  }

  return (
    <section id="brew-guide" aria-labelledby="t-brew-guide" className="scroll-mt-header bg-bg px-gutter py-s8 text-text md:py-s9">
      <div className="mx-auto max-w-site">
        <h2 id="t-brew-guide" className="type-display m-0 text-h2 leading-none">
          <span className="md:hidden">{tx(guide.titleShort)}</span>
          <span className="max-md:hidden">{tx(guide.title)}</span>
        </h2>
        <p className="mt-s3 mb-0 font-bold">{tx(guide.subtitle)}</p>
        <p className="mt-s2 mb-0 md:text-small">
          <strong>{tx(guide.need.label)}:</strong> {tx(guide.need.text)}
        </p>

        <ol ref={reveal} className="mt-s6 mb-0 grid list-none gap-s4 p-0 md:grid-cols-3 md:gap-s5">
          {guide.steps.map((step, i) => (
            <li key={step.id} data-reveal className="flex flex-col rounded-card bg-surface p-s4 shadow-soft">
              <StepImage photo={step.photo} />
              {/* broj daje <ol>; vidljiv broj je ukras */}
              <p aria-hidden="true" className="type-eyebrow mt-s4 mb-0 text-muted">
                {String(i + 1).padStart(2, '0')}
              </p>
              <h3 className="type-display mt-s2 mb-0 text-[1.75rem] leading-none">{tx(step.title)}</h3>
              <p className="mt-s3 mb-0">{tx(step.text)}</p>
            </li>
          ))}
        </ol>

        <div className="mt-s6 flex flex-wrap items-center gap-x-s6 gap-y-s4">
          <p className="m-0 md:text-small">
            <strong>{tx(guide.tip.label)}:</strong> {tx(guide.tip.text)}
          </p>
          <p className="m-0 md:text-small">{tx(guide.recommendation)}</p>
          <Button href={guide.cta.href} onClick={shopFilter}>
            {tx(guide.cta.label)}
          </Button>
        </div>
      </div>
    </section>
  )
}
