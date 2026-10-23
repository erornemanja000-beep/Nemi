// Korpa (demo): stavke sa +/− i „ukloni", međuzbir, dostava, „do besplatne dostave", ukupno sa PDV-om i
// onemogućeno dugme porudžbine sa napomenom „Demo". Stanje je u src/lib/cart.ts (openCart/closeCart).
// Ljuska panela je Overlay (./Overlay.tsx).
import { useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { media } from '../content/media'
import { productBySlug } from '../content/products'
import { shop } from '../content/shop'
import { site } from '../content/site'
import type { Product } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { closeCart, MAX_QTY, removeLine, setQty, useCart } from '../lib/cart'
import { formatGrams, formatPrice } from '../lib/format'
import { lockScroll } from '../lib/motion'
import { Button } from './Button'
import { Icon } from './Icon'
import { Overlay } from './Overlay'
import { Price } from './Price'
import './chrome.css'

/** Mala slika stavke: kesa (kafa, set) ili oprema; dok render ne stigne, obojena kutija iste razmere. */
function Thumb({ product }: { product: Product }) {
  const image = product.kind === 'gear' ? media.gear[product.image] : media.bags[product.image]
  const box = 'block w-14 flex-none rounded-sm bg-placeholder aspect-[4/5]'
  if (!image?.ready) return <span aria-hidden="true" className={box} />
  return <img src={image.srcs[0].src} width={image.srcs[0].width} height={Math.round(image.srcs[0].width / image.ratio)} alt="" loading="lazy" className={`${box} h-auto object-cover`} />
}

export function CartDrawer() {
  const { lang, tx, tf } = useLang()
  const cart = useCart()
  const onHome = useLocation().pathname === '/'
  const titleRef = useRef<HTMLHeadingElement>(null)
  const restore = useRef(true)

  const close = (restoreFocus = true) => {
    restore.current = restoreFocus
    closeCart()
  }
  /** Link na sidro iz korpe: skrol se otključava odmah, pre nego što pregledač (ili Lenis) skoči. */
  const leave = () => {
    lockScroll(false)
    close(false)
  }
  const shouldRestore = () => {
    const r = restore.current
    restore.current = true
    return r
  }

  const { freeFromCents } = shop.shipping
  const progress = Math.min(1, cart.subtotalCents / freeFromCents)

  return (
    <Overlay open={cart.open} onClose={() => close()} labelledBy="cart-title" variant="drawer" restoreFocus={shouldRestore}>
      <div className="flex h-header flex-none items-center justify-between gap-s3 border-b border-line pr-s3 pl-s5">
        <h2 id="cart-title" ref={titleRef} tabIndex={-1} className="type-display m-0 text-[1.75rem] leading-none outline-none">
          {tx(site.aria.cartTitle)}
          {cart.count > 0 && <span className="ml-s2 align-[.15em] font-label text-label font-bold tracking-normal text-muted">({cart.count})</span>}
        </h2>
        <Button variant="icon" aria-label={tx(shop.cart.close)} onClick={() => close()}>
          <Icon name="close" />
        </Button>
      </div>

      {cart.lines.length === 0 ? (
        <div className="flex flex-1 flex-col items-start gap-s5 overflow-y-auto px-s5 py-s6">
          <p className="m-0">{tx(shop.cart.empty)}</p>
          <Button href={onHome ? site.shopNow.href : `/${site.shopNow.href}`} onClick={leave}>
            {tx(site.shopNow.label)}
          </Button>
        </div>
      ) : (
        <>
          <ul className="m-0 min-h-0 flex-1 list-none overflow-y-auto px-s5 py-0">
            {cart.lines.map((line) => {
              const product = productBySlug(line.slug)
              if (!product) return null
              const name = tx(product.name)
              const size = line.grams ? formatGrams(line.grams, lang) : ''
              const grind = line.grind ? shop.grinds.find((g) => g.id === line.grind) : undefined
              const details = [size, grind ? tx(grind.label) : ''].filter(Boolean).join(' · ')
              // oprema nema veličinu: „Remove {name}, , from cart" → „Remove {name}, from cart"
              const removeLabel = tf(shop.cart.removeAria, { name, size }).replace(/,\s*,/, ',')
              const atMin = line.qty <= 1
              const atMax = line.qty >= MAX_QTY
              return (
                <li key={line.key} className="flex gap-s4 border-b border-line py-s4 last:border-b-0">
                  <Thumb product={product} />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-s3">
                      <h3 className="m-0 text-body leading-snug font-bold">{name}</h3>
                      <p className="m-0 font-bold whitespace-nowrap">{formatPrice(line.lineCents, lang)}</p>
                    </div>
                    {details && <p className="m-0 text-small text-muted">{details}</p>}
                    <Price cents={line.unitCents} grams={line.grams ?? undefined} note="none" className="mt-1 text-muted" amountClassName="text-small font-semibold" />
                    <div className="mt-s2 flex items-center justify-between gap-s3">
                      <div role="group" aria-label={`${tx(shop.cart.quantity)}: ${name}`} className="flex items-center rounded-pill border border-line-strong">
                        <button
                          type="button"
                          aria-label={tx(shop.cart.decrease)}
                          aria-disabled={atMin || undefined}
                          onClick={() => !atMin && setQty(line.key, line.qty - 1)}
                          className="grid size-tap cursor-pointer place-items-center rounded-pill border-0 bg-transparent text-text aria-disabled:cursor-not-allowed aria-disabled:opacity-40"
                        >
                          <Icon name="minus" className="size-4" />
                        </button>
                        <span className="min-w-[2ch] text-center font-bold tabular-nums">
                          <span className="sr-only">{tx(shop.cart.quantity)} </span>
                          {line.qty}
                        </span>
                        <button
                          type="button"
                          aria-label={tx(shop.cart.increase)}
                          aria-disabled={atMax || undefined}
                          onClick={() => !atMax && setQty(line.key, line.qty + 1)}
                          className="grid size-tap cursor-pointer place-items-center rounded-pill border-0 bg-transparent text-text aria-disabled:cursor-not-allowed aria-disabled:opacity-40"
                        >
                          <Icon name="plus" className="size-4" />
                        </button>
                      </div>
                      <button
                        type="button"
                        aria-label={removeLabel}
                        onClick={() => {
                          removeLine(line.key)
                          // dugme nestaje sa stavkom: fokus ide na naslov korpe
                          titleRef.current?.focus({ preventScroll: true })
                        }}
                        className="inline-flex min-h-tap cursor-pointer items-center border-0 bg-transparent px-s2 text-small text-accent-text underline underline-offset-4"
                      >
                        {tx(shop.cart.remove)}
                      </button>
                    </div>
                  </div>
                </li>
              )
            })}
          </ul>

          <div className="flex-none border-t border-line px-s5 pt-s4 pb-[calc(var(--space-5)+env(safe-area-inset-bottom))]">
            <dl aria-live="polite" className="m-0 grid grid-cols-[1fr_auto] gap-x-s4 gap-y-s1 text-small">
              <dt>{tx(shop.cart.subtotal)}</dt>
              <dd className="m-0 text-right tabular-nums">{formatPrice(cart.subtotalCents, lang)}</dd>
              <dt>{tx(shop.cart.shipping)}</dt>
              <dd className="m-0 text-right tabular-nums">{formatPrice(cart.shippingCents, lang)}</dd>
              {cart.toFreeShippingCents > 0 && (
                <dd className="col-span-2 m-0 pt-s1 text-muted">
                  {tf(shop.cart.toFree, { amount: formatPrice(cart.toFreeShippingCents, lang) })}
                  <span aria-hidden="true" className="chrome-progress mt-s2 block">
                    <span style={{ transform: `scaleX(${progress})` }} />
                  </span>
                </dd>
              )}
              <dt className="mt-s3 text-body font-bold">{tx(shop.cart.total)}</dt>
              <dd className="m-0 mt-s3 text-right text-body font-bold tabular-nums">{formatPrice(cart.totalCents, lang)}</dd>
            </dl>
            <Button disabled aria-describedby="cart-order-note" className="mt-s5 w-full justify-center">
              {tx(shop.cart.order)}
            </Button>
            <p id="cart-order-note" className="m-0 mt-s2 text-center text-micro text-muted">
              {tx(shop.cart.orderNote)}
            </p>
          </div>
        </>
      )}
    </Overlay>
  )
}
