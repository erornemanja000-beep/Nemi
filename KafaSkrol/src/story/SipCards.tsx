// Tri staklene kartice u SIP-u (mockup .glass-card, tekstovi.md „SIP: staklene kartice").
// Podaci: chapters.sipCards (natpis, podnatpis, red, note) + proizvod (ime, note ako ih kartica nema, cena 250 g). Grundpreis i
// PDV daje Price, „Geröstet am" je lastRoastDate(). Kartica je link na /p/<slug> (rastegnut preko cele
// kartice), a dugme „+" stavlja 250 g (cela zrna) u korpu.
// Omotač <li data-anim="card" data-sip-card="0|1|2"> pomera Story (Z12, ulet); nagib je na <article>.
// Raspored (chapters.css): u .ch-layer na desktopu špil uz dršku šolje, na širokom desktopu (od 80rem ×
// 53,75rem) kartice oko šolje, gde su 1 i 2 kompaktne (glass-card--compact, Z15), a na telefonu i van
// scene horizontalna traka sa scroll-snap-om, tačkicama koje prate traku i „Swipe for more".
// Nepostojeći slug ili proizvod bez pakovanja: kartica se ne prikazuje (u dev-u console.warn).
// `loadImages={false}` (Story, Z12): slike kesa se još ne traže (storyboard 8: kese tek na 60 % POUR-a),
// a do tada stoji CSS kesa.
import { useEffect, useId, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/Button'
import { Icon } from '../components/Icon'
import { Price } from '../components/Price'
import { chapters } from '../content/chapters'
import { media } from '../content/media'
import { productBySlug } from '../content/products'
import { shop } from '../content/shop'
import type { Product, ProductSize, SipCard } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { addToCart } from '../lib/cart'
import { formatDate, formatGrams, formatPrice, lastRoastDate } from '../lib/format'
import { isReducedMotion } from '../lib/useMedia'
import './chapters.css'

/** Pakovanje na kartici (tekstovi.md: cena za 250 g). */
const CARD_GRAMS = 250

type Entry = { card: SipCard; product: Product; size: ProductSize; index: number }

const entries: Entry[] = chapters.sipCards.flatMap((card, index) => {
  const product = productBySlug(card.product)
  const size = product?.sizes.find((s) => s.grams === CARD_GRAMS) ?? product?.sizes[0]
  if (!product || !size) {
    if (import.meta.env.DEV) console.warn(`[SipCards] proizvod „${card.product}" ne postoji ili nema pakovanje: kartica ${index} se ne prikazuje`)
    return []
  }
  return [{ card, product, size, index }]
})

function GlassCard({ entry, roast, loadImage }: { entry: Entry; roast: string; loadImage: boolean }) {
  const { lang, tx, tf } = useLang()
  const titleId = useId()
  const { card, product, size } = entry
  const name = tx(product.name)
  const short = card.shortName ?? product.shortName
  const sizeLabel = formatGrams(size.grams, lang)
  // {place} je prvi deo reda kartice („Ethiopia", „Colombia", „House blend"), chapters.card.aria
  const place = tx(card.line).split(' · ')[0]
  const bag = media.bags[product.image]
  // note sa kartice (tekstovi.md, tabela SIP kartica); bez njih važe note proizvoda
  const notes = card.notes ?? product.notes

  return (
    <article className={`glass-card ${entry.index === 0 ? '' : 'glass-card--compact'}`} aria-labelledby={titleId}>
      <div className="glass-card__head">
        <p className="glass-card__label">
          {tx(card.label)}
          <small className="glass-card__chip" aria-hidden="true">
            {tx(shop.card.demo)}
          </small>
          <span className="sr-only"> {tx(shop.card.demoSr)}</span>
        </p>
        <Link
          to={`/p/${product.slug}`}
          className="glass-card__link"
          aria-label={tf(chapters.card.aria, { name, place, price: formatPrice(size.priceCents, lang), size: sizeLabel })}
        >
          <Icon name="external" className="size-4" />
        </Link>
      </div>
      <p className="glass-card__sub">{tx(card.sub)}</p>
      <div className="glass-card__pack" aria-hidden="true">
        {bag?.ready && loadImage ? (
          <img
            src={bag.srcs.find((s) => s.width === 600)?.src ?? bag.srcs[0].src}
            srcSet={bag.srcs.map((s) => `${s.src} ${s.width}w`).join(', ')}
            sizes="(min-width: 64rem) 7rem, 5rem"
            width={600}
            height={Math.round(600 / bag.ratio)}
            alt=""
            loading="lazy"
            decoding="async"
          />
        ) : (
          <span className="glass-card__bag" />
        )}
      </div>
      <h3 id={titleId} className="glass-card__title">
        {short ? (
          <>
            <span className="desk:hidden">{tx(short)}</span>
            <span className="phone:hidden">{name}</span>
          </>
        ) : (
          name
        )}
      </h3>
      <p className="glass-card__meta">
        {tx(card.line)}
        {notes && (
          <>
            <br />
            {tx(notes).join(' · ')}
          </>
        )}
      </p>
      <div className="glass-card__buy">
        <Price
          cents={size.priceCents}
          grams={size.grams}
          showGrams
          className="text-glass-muted"
          amountClassName="text-[1.25rem] font-extrabold text-glass-text"
        />
        <Button
          variant="round"
          aria-label={tf(shop.card.add, { name, size: sizeLabel })}
          onClick={() => addToCart(product.slug, size.grams, 'whole')}
        >
          <Icon name="plus" className="size-[18px]" />
        </Button>
      </div>
      <p className="glass-card__roast">
        {tx(shop.labels.roastedOn)} {roast}
      </p>
    </article>
  )
}

type Props = { className?: string; loadImages?: boolean }

export function SipCards({ className = '', loadImages = true }: Props) {
  const { lang, tx } = useLang()
  const roastDate = useMemo(() => lastRoastDate(), [])
  const strip = useRef<HTMLUListElement>(null)
  const [active, setActive] = useState(0)

  // tačkice prate traku (telefon); na desktopu se traka ne skroluje, pa se ništa ne dešava
  useEffect(() => {
    const el = strip.current
    if (!el) return
    let frame = 0
    const update = () => {
      frame = 0
      const items = el.children
      if (items.length < 2) return
      const max = el.scrollWidth - el.clientWidth
      const step = (items[1] as HTMLElement).offsetLeft - (items[0] as HTMLElement).offsetLeft
      if (max <= 0 || step <= 0) return
      const i = el.scrollLeft >= max - 4 ? items.length - 1 : Math.round(el.scrollLeft / step)
      setActive(Math.min(items.length - 1, Math.max(0, i)))
    }
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update)
    }
    el.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      cancelAnimationFrame(frame)
      el.removeEventListener('scroll', onScroll)
    }
  }, [])

  const goTo = (i: number) => {
    const el = strip.current
    const item = el?.children[i] as HTMLElement | undefined
    if (!el || !item) return
    const pad = parseFloat(getComputedStyle(el).paddingLeft) || 0
    const left = el.scrollLeft + item.getBoundingClientRect().left - el.getBoundingClientRect().left - pad
    el.scrollTo({ left, behavior: isReducedMotion() ? 'auto' : 'smooth' })
  }

  if (entries.length === 0) return null
  const roast = formatDate(roastDate, lang)

  return (
    <div className={`sip-cards ${className}`}>
      <ul ref={strip} role="list" className="sip-cards__strip">
        {entries.map((entry) => (
          <li key={entry.card.product} data-anim="card" data-sip-card={entry.index} className="sip-card-slot">
            <GlassCard entry={entry} roast={roast} loadImage={loadImages} />
          </li>
        ))}
      </ul>
      {entries.length > 1 && (
        <>
          <div className="sip-cards__dots">
            {entries.map((entry, i) => (
              <button
                key={entry.card.product}
                type="button"
                className="ch-dot"
                aria-label={`${tx(entry.card.label)}: ${tx(entry.product.name)}`}
                aria-current={i === active ? 'true' : undefined}
                onClick={() => goTo(i)}
              />
            ))}
          </div>
          <p className="sip-cards__swipe" aria-hidden="true">
            {tx(chapters.nav.swipe)}
          </p>
        </>
      )}
    </div>
  )
}
