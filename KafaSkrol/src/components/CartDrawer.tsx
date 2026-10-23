// Korpa (demo): stavke sa +/− i „ukloni", međuzbir, dostava, „do besplatne dostave", ukupno sa PDV-om i
// onemogućeno dugme porudžbine sa napomenom „Demo". Stanje je u src/lib/cart.ts (openCart/closeCart).
//
// Ovde je i Overlay: zajednička ljuska modalnih panela headera (korpa, meni, pretraga). Daje zatamnjenu
// pozadinu, role="dialog" + aria-modal, zarobljen fokus, Esc, zaključan skrol stranice (lockScroll),
// data-lenis-prevent (panel se skroluje sam) i povratak fokusa na dugme koje je panel otvorilo.
import { useEffect, useRef, useState, type ReactNode, type RefObject } from 'react'
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
import { isReducedMotion } from '../lib/useMedia'
import { Button } from './Button'
import { Icon } from './Icon'
import { Price } from './Price'
import './chrome.css'

// ---------------------------------------------------------------------------------------------
// Overlay
// ---------------------------------------------------------------------------------------------

/** Trajanje izlaza panela = --dur-base (tokens.css). */
const EXIT_MS = 360

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

const focusables = (root: HTMLElement) =>
  Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter((el) => el.getClientRects().length > 0)

type OverlayProps = {
  open: boolean
  /** Esc, klik na zatamnjenu pozadinu (i dugme za zatvaranje u panelu) */
  onClose: () => void
  /** naziv dijaloga: aria-label ili id naslova u panelu */
  label?: string
  labelledBy?: string
  /** drawer = korpa (desno), sheet = meni na telefonu (ceo ekran), top = pretraga (traka odozgo) */
  variant: 'drawer' | 'sheet' | 'top'
  /** dobija fokus pri otvaranju; inače prvi fokusabilan element u panelu */
  initialFocus?: RefObject<HTMLElement | null>
  /**
   * Pita se pri zatvaranju. false kad fokus preuzima neko drugi: link na sidro (pregledač nastavlja od
   * sekcije) ili rezultat pretrage (fokus uzima modal proizvoda).
   */
  restoreFocus?: () => boolean
  className?: string
  children: ReactNode
}

export function Overlay({ open, onClose, label, labelledBy, variant, initialFocus, restoreFocus, className = '', children }: OverlayProps) {
  const panelRef = useRef<HTMLDivElement>(null)
  // panel ostaje u DOM-u dok traje izlaz (data-state="closed"), pa se skida
  const [mounted, setMounted] = useState(open)
  if (open && !mounted) setMounted(true)

  const latest = useRef({ onClose, restoreFocus, initialFocus })
  useEffect(() => {
    latest.current = { onClose, restoreFocus, initialFocus }
  })

  useEffect(() => {
    if (open || !mounted) return
    const t = window.setTimeout(() => setMounted(false), isReducedMotion() ? 0 : EXIT_MS)
    return () => window.clearTimeout(t)
  }, [open, mounted])

  useEffect(() => {
    const panel = panelRef.current
    if (!open || !panel) return
    const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null
    lockScroll(true)
    const first = latest.current.initialFocus?.current ?? focusables(panel)[0] ?? panel
    first.focus({ preventScroll: true })

    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        latest.current.onClose()
        return
      }
      if (e.key !== 'Tab') return
      const list = focusables(panel)
      if (list.length === 0) {
        e.preventDefault()
        panel.focus({ preventScroll: true })
        return
      }
      const active = document.activeElement
      const firstEl = list[0]
      const lastEl = list[list.length - 1]
      if (e.shiftKey && (active === firstEl || !panel.contains(active))) {
        e.preventDefault()
        lastEl.focus()
      } else if (!e.shiftKey && (active === lastEl || !panel.contains(active))) {
        e.preventDefault()
        firstEl.focus()
      }
    }
    // fokus koji ipak pobegne (klik van panela, čitač ekrana) vraća se u panel
    const onFocusIn = (e: FocusEvent) => {
      if (e.target instanceof Node && !panel.contains(e.target)) (focusables(panel)[0] ?? panel).focus({ preventScroll: true })
    }
    document.addEventListener('keydown', onKey)
    document.addEventListener('focusin', onFocusIn)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.removeEventListener('focusin', onFocusIn)
      lockScroll(false)
      if (latest.current.restoreFocus?.() !== false && opener?.isConnected) opener.focus({ preventScroll: true })
    }
  }, [open])

  if (!mounted) return null
  return (
    <div className="chrome-overlay" data-variant={variant} data-state={open ? 'open' : 'closed'} inert={!open}>
      <div className="chrome-backdrop" aria-hidden="true" onClick={onClose} />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-label={label}
        aria-labelledby={labelledBy}
        tabIndex={-1}
        className={`chrome-panel ${className}`}
        data-lenis-prevent
      >
        {children}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------------------------
// Korpa
// ---------------------------------------------------------------------------------------------

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
