// Kartica proizvoda u prodavnici (Z9, skica „7 · Prodavnica", tekstovi.md „Natpisi na kartici proizvoda").
//   Svuda: slika, čip „Demo", oznake (prženje, za šta, tag), ime (link na /p/<slug>), poreklo · obrada,
//          cena sa Grundpreisom u istom redu i „incl. VAT, plus shipping", „Add to cart".
//   Desktop (lg, 64rem) još: note, „Roasted on" (+ „Best before" kad postoji pravilo), 250 g / 1 kg i mlevenje.
//   Telefon: kraća kartica (mapa-skrola): bez nota, datuma i izbora; u korpu ide 250 g, cela zrna.
// ProductVisual (kesa ili oprema) koristi i modal proizvoda. Dok render ne postoji (ready: false),
// crta CSS kesu iz mockup.html ili sivu siluetu opreme (aria-hidden). Stilovi su u sections/shop.css.
import { useId, useState } from 'react'
import { Link } from 'react-router-dom'
import { media } from '../content/media'
import { shop } from '../content/shop'
import type { GrindId, L, Product } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { addToCart } from '../lib/cart'
import { productTags } from '../lib/filters'
import { bestBefore, formatDate, formatGrams, type CalendarDate } from '../lib/format'
import { Button } from './Button'
import { Icon } from './Icon'
import { Price } from './Price'
import '../sections/shop.css'

/** Slika proizvoda: kesa (kafa, set) ili oprema iz media.ts. */
function imageOf(product: Product) {
  return product.kind === 'gear' ? media.gear[product.image] : media.bags[product.image]
}

/** Sive siluete opreme iz mockup.html (mlin, kuvalo, dripper sa bokalom), bez zrna i nagiba. */
function GearSilhouette({ id }: { id: string }) {
  if (id === 'grinder') {
    return (
      <svg viewBox="30 -10 380 590" className="shop-gear" aria-hidden="true" focusable="false">
        <rect x="36" y="0" width="368" height="22" rx="7" />
        <path d="M52 22H388L352 188Q346 214 318 214H122Q94 214 88 188Z" opacity=".55" />
        <rect x="116" y="214" width="208" height="30" rx="6" />
        <rect x="148" y="244" width="144" height="22" rx="4" />
        <rect x="68" y="266" width="322" height="276" rx="24" />
        <rect x="88" y="542" width="282" height="26" rx="8" opacity=".85" />
      </svg>
    )
  }
  if (id === 'dripper') {
    return (
      <svg viewBox="0 0 380 560" className="shop-gear" aria-hidden="true" focusable="false">
        <path d="M14 26H366L262 228H118Z" opacity=".9" />
        <rect x="6" y="20" width="368" height="16" rx="8" />
        <rect x="104" y="228" width="172" height="16" rx="6" />
        <path d="M96 250H284Q300 250 300 268L320 468Q326 542 258 546H122Q54 542 60 468L80 268Q80 250 96 250Z" opacity=".6" />
        <path d="M300 300Q372 300 366 382Q360 442 314 452" fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" opacity=".7" />
      </svg>
    )
  }
  // kuvalo (gooseneck)
  return (
    <svg viewBox="0 40 600 340" className="shop-gear" aria-hidden="true" focusable="false">
      <path d="M200 140Q205 90 260 85H420Q470 90 475 140L500 330Q505 360 470 360H205Q170 360 175 330Z" />
      <ellipse cx="338" cy="84" rx="92" ry="14" opacity=".85" />
      <rect x="318" y="50" width="40" height="30" rx="10" />
      <path d="M475 150Q560 158 548 262Q538 322 496 332" fill="none" stroke="currentColor" strokeWidth="22" strokeLinecap="round" />
      <path d="M190 300C120 300 110 200 60 170C40 158 22 160 8 168" fill="none" stroke="currentColor" strokeWidth="13" strokeLinecap="round" />
    </svg>
  )
}

type VisualProps = {
  product: Product
  /** `sizes` za srcset (kartica i modal imaju različite širine) */
  sizes: string
  /** alt slike; na kartici je prazan (ime je u naslovu, Z3 1c), u modalu opisuje kesu */
  alt?: string
  className?: string
}

/** Kesa ili oprema: pravi render kad je ready, inače CSS kesa / silueta (aria-hidden). */
export function ProductVisual({ product, sizes, alt = '', className = '' }: VisualProps) {
  const image = imageOf(product)
  if (image?.ready) {
    const mid = image.srcs[Math.floor(image.srcs.length / 2)]
    return (
      <img
        src={mid.src}
        srcSet={image.srcs.map((s) => `${s.src} ${s.width}w`).join(', ')}
        sizes={sizes}
        width={mid.width}
        height={Math.round(mid.width / image.ratio)}
        alt={alt}
        loading="lazy"
        decoding="async"
        className={`shop-visual__img ${className}`}
      />
    )
  }
  if (product.kind === 'gear') return <GearSilhouette id={product.image} />
  return <span className={`shop-bag ${className}`} aria-hidden="true" />
}

type Props = {
  product: Product
  /** poslednji dan prženja (lastRoastDate), isti za sve kartice */
  roast: CalendarDate
}

export function ProductCard({ product, roast }: Props) {
  const { lang, tx } = useLang()
  const uid = useId()
  const titleId = `${uid}-title`
  const [grams, setGrams] = useState(product.sizes[0]?.grams ?? 0)
  const [grind, setGrind] = useState<GrindId>('whole')

  const size = product.sizes.find((s) => s.grams === grams) ?? product.sizes[0]
  const cents = size?.priceCents ?? product.priceCents
  if (cents == null) return null

  const isCoffee = product.kind === 'coffee'
  const href = `/p/${product.slug}`
  const name = tx(product.name)
  const tags = productTags(product)
  const meta = [product.origin, product.process].filter((v): v is L => !!v).map(tx).join(' · ')
  const best = bestBefore(roast)

  const add = () => {
    if (product.kind === 'gear') addToCart(product.slug, null, null)
    else if (size) addToCart(product.slug, size.grams, isCoffee ? grind : null)
  }

  return (
    <article className="shop-card" aria-labelledby={titleId}>
      {/* slika vodi na isti link kao ime; za tastaturu i čitač postoji samo link na imenu */}
      <Link to={href} tabIndex={-1} aria-hidden="true" className="shop-card__media">
        <ProductVisual product={product} sizes="(min-width: 64rem) 25rem, 50vw" />
        <span className="shop-demo">{tx(shop.card.demo)}</span>
      </Link>

      <div className="flex flex-1 flex-col gap-s2 p-s3 lg:gap-s3 lg:p-s4">
        {tags.length > 0 && (
          <ul role="list" className="m-0 flex list-none flex-wrap gap-1.5 p-0">
            {tags.map((t) => (
              <li key={t.en} className="shop-tag">
                {tx(t)}
              </li>
            ))}
          </ul>
        )}

        <div>
          <h4 id={titleId} className="m-0 font-text text-h3 leading-snug font-extrabold lg:text-[1.375rem]">
            <Link to={href} data-product-link={product.slug} className="-my-[11px] block py-[11px] text-text no-underline hover:underline">
              {name}
            </Link>
          </h4>
          <p className="sr-only">{tx(shop.card.demoSr)}</p>
          {meta && <p className="m-0 mt-1 line-clamp-2 text-small font-semibold text-muted lg:line-clamp-none">{meta}</p>}
        </div>

        {product.notes && <p className="m-0 hidden text-small lg:block">{tx(product.notes).join(' · ')}</p>}
        {!isCoffee && <p className="m-0 hidden text-small text-muted lg:line-clamp-3">{tx(product.description)}</p>}

        {isCoffee && (
          <p className="m-0 hidden border-t border-dashed border-line pt-s2 text-micro text-muted lg:block">
            {tx(shop.labels.roastedOn)} {formatDate(roast, lang)}
            {best && (
              <>
                {' · '}
                {tx(shop.labels.bestBefore)} {formatDate(best, lang)}
              </>
            )}
          </p>
        )}

        {isCoffee && product.sizes.length > 1 && (
          <fieldset className="shop-seg hidden lg:flex">
            <legend className="sr-only">{tx(shop.labels.size)}</legend>
            {product.sizes.map((s) => (
              <label key={s.grams} className="shop-seg__opt">
                <input
                  type="radio"
                  name={`${uid}-size`}
                  value={s.grams}
                  checked={s.grams === size?.grams}
                  onChange={() => setGrams(s.grams)}
                  className="sr-only"
                />
                {formatGrams(s.grams, lang)}
              </label>
            ))}
          </fieldset>
        )}

        <Price
          cents={cents}
          grams={size?.grams}
          showGrams={!!size}
          className="text-muted"
          amountClassName="text-[1.25rem] font-extrabold text-text lg:text-[1.5rem]"
        />

        {isCoffee && (
          <label className="hidden gap-1 lg:grid">
            <span className="text-micro font-bold tracking-[.12em] text-muted uppercase">{tx(shop.labels.grind)}</span>
            <span className="shop-select">
              <select value={grind} onChange={(e) => setGrind(e.target.value as GrindId)}>
                {shop.grinds.map((g) => (
                  <option key={g.id} value={g.id}>
                    {tx(g.label)}
                  </option>
                ))}
              </select>
              <Icon name="next" className="shop-select__icon" />
            </span>
          </label>
        )}

        <Button
          aria-describedby={titleId}
          onClick={add}
          className="mt-auto w-full justify-center px-3! text-center leading-[1.15]! lg:px-7!"
        >
          {tx(shop.labels.addToCart)}
        </Button>
      </div>
    </article>
  )
}
