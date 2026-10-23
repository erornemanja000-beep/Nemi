// Modal proizvoda na /p/:slug, preko početne (Home je roditeljska ruta, pa prodavnica ostaje ispod).
//   - <dialog> sa showModal(): top layer, ostatak stranice je inert; Tab dodatno kruži unutar dijaloga.
//   - Esc, „×", klik pored panela i „Back to the shop" zatvaraju: ako je modal otvoren iz aplikacije,
//     korak nazad u istoriji (vraća na /), a pri hladnom otvaranju zamena sa / i skok na prodavnicu.
//     Dugme „nazad" u pregledaču radi isto. Fokus se vraća na element koji je otvorio modal, a ako ga nema
//     (hladno otvaranje, Safari ne fokusira link na klik), na link kartice u prodavnici.
//   - lockScroll + data-lenis-prevent: stranica stoji, a dijalog se skroluje sam.
//   - Polja iz tekstovi.md („Natpisi na kartici proizvoda"): farma (fiktivna), „Roasted on" (lastRoastDate),
//     „Best before" samo kad bestBefore() ima pravilo (do odluke korisnika red se ne prikazuje).
//   - Nepoznat slug i oprema bez cene (PrAG) vode na /.
// Toast iz korpe je ispod top layer-a, pa modal ima svoju poruku (role="status") posle „Add to cart".
import { useEffect, useId, useMemo, useRef, useState, type KeyboardEvent, type MouseEvent, type PointerEvent } from 'react'
import { Navigate, useLocation, useNavigate, useParams } from 'react-router-dom'
import { Button, buttonClass } from '../components/Button'
import { Icon } from '../components/Icon'
import { Price } from '../components/Price'
import { ProductVisual } from '../components/ProductCard'
import { productBySlug } from '../content/products'
import { shop } from '../content/shop'
import { site } from '../content/site'
import type { GrindId, L, Product } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { addToCart } from '../lib/cart'
import { isListed, productTags } from '../lib/filters'
import { bestBefore, formatAltitude, formatDate, formatGrams, lastRoastDate } from '../lib/format'
import { lockScroll, scrollToTarget } from '../lib/motion'
import '../sections/shop.css'

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
const STATUS_MS = 4000

export default function ProductModal() {
  const { slug = '' } = useParams()
  const product = productBySlug(slug)
  if (!product || !isListed(product)) return <Navigate to="/" replace />
  return <ProductDialog key={product.slug} product={product} />
}

type Restore = 'opener' | 'shop'

function ProductDialog({ product }: { product: Product }) {
  const { lang, tx, tf } = useLang()
  const navigate = useNavigate()
  const location = useLocation()
  const uid = useId()
  const titleId = `${uid}-title`

  const dialogRef = useRef<HTMLDialogElement>(null)
  const closeRef = useRef<HTMLButtonElement>(null)
  const openerRef = useRef<HTMLElement | null>(null)
  const closingRef = useRef(false)
  const mountedRef = useRef(false)
  const pressedOutside = useRef(false)
  // otvoren iz aplikacije (postoji korak nazad) ili hladno (/p/<slug> u adresi)
  const inApp = location.key !== 'default'
  const restoreRef = useRef<Restore>(inApp ? 'opener' : 'shop')

  const [grams, setGrams] = useState(product.sizes[0]?.grams ?? 0)
  const [grind, setGrind] = useState<GrindId>('whole')
  const [added, setAdded] = useState(false)
  const roast = useMemo(() => lastRoastDate(), [])

  const slug = product.slug
  const isCoffee = product.kind === 'coffee'
  const size = product.sizes.find((s) => s.grams === grams) ?? product.sizes[0]
  const cents = size?.priceCents ?? product.priceCents ?? 0
  const name = tx(product.name)

  // otvaranje, zaključavanje skrola i vraćanje fokusa
  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    closingRef.current = false
    const active = document.activeElement
    openerRef.current = active instanceof HTMLElement && active !== document.body ? active : null
    lockScroll(true)
    if (!dialog.open) dialog.showModal()
    closeRef.current?.focus()

    mountedRef.current = true

    return () => {
      mountedRef.current = false
      closingRef.current = true
      if (dialog.open) dialog.close()
      lockScroll(false)
      // fokus se vraća posle commit-a; StrictMode (dev) odmah ponovo montira, pa tada nema vraćanja
      queueMicrotask(() => {
        if (mountedRef.current) return
        const card = document.querySelector<HTMLElement>(`[data-product-link="${CSS.escape(slug)}"]`)
        const opener = openerRef.current?.isConnected ? openerRef.current : null
        if (restoreRef.current === 'opener') {
          const target = opener ?? card
          target?.focus({ preventScroll: true })
          return
        }
        // na prodavnicu: kartica ovog proizvoda (ako je u filtriranoj mreži), inače naslov prodavnice
        scrollToTarget('#find-your-cup', true)
        const target = card ?? document.getElementById('t-shop')
        target?.focus({ preventScroll: true })
      })
    }
  }, [slug])

  // poruka posle „Add to cart" se briše, da se sledeće dodavanje ponovo pročita
  useEffect(() => {
    if (!added) return
    const id = window.setTimeout(() => setAdded(false), STATUS_MS)
    return () => window.clearTimeout(id)
  }, [added])

  const close = (restore: Restore) => {
    if (closingRef.current) return
    closingRef.current = true
    restoreRef.current = restore
    if (inApp) navigate(-1)
    else navigate('/', { replace: true })
  }

  const onKeyDown = (e: KeyboardEvent<HTMLDialogElement>) => {
    if (e.key !== 'Tab') return
    const items = [...e.currentTarget.querySelectorAll<HTMLElement>(FOCUSABLE)].filter((el) => el.getClientRects().length > 0)
    if (items.length === 0) return
    const first = items[0]
    const last = items[items.length - 1]
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault()
      last.focus()
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault()
      first.focus()
    }
  }

  // klik pored panela zatvara, ali samo ako je i pritisak počeo pored panela (ne posle označavanja teksta)
  const onPointerDown = (e: PointerEvent<HTMLDialogElement>) => {
    pressedOutside.current = e.target === e.currentTarget
  }
  const onClick = (e: MouseEvent<HTMLDialogElement>) => {
    if (e.target === e.currentTarget && pressedOutside.current) close('opener')
    pressedOutside.current = false
  }

  const add = () => {
    if (product.kind === 'gear') addToCart(slug, null, null)
    else if (size) addToCart(slug, size.grams, isCoffee ? grind : null)
    setAdded(false)
    // posle praznog kadra, da čitač ponovo pročita istu poruku
    requestAnimationFrame(() => setAdded(true))
  }

  const best = bestBefore(roast)
  const L_ = shop.labels
  const rows: [L, string][] = []
  const push = (label: L, value: string | undefined) => {
    if (value) rows.push([label, value])
  }
  push(L_.origin, product.origin && tx(product.origin))
  push(L_.process, product.process && tx(product.process))
  push(L_.variety, product.variety && tx(product.variety))
  push(L_.altitude, product.altitude && formatAltitude(product.altitude, lang))
  push(L_.notes, product.notes && tx(product.notes).join(' · '))
  push(L_.bestFor, product.bestFor && tx(product.bestFor))
  push(L_.roast, product.roast && tx(product.roast))
  push(L_.farm, product.farm && tx(product.farm))
  if (isCoffee) push(L_.roastedOn, formatDate(roast, lang))
  if (isCoffee && best) push(L_.bestBefore, formatDate(best, lang))
  if (product.kind === 'set' && size) push(L_.size, formatGrams(size.grams, lang))

  const image = product.kind === 'gear' ? undefined : tf(shop.modal.imageAlt, { name })
  const tags = productTags(product)

  return (
    <dialog
      ref={dialogRef}
      className="pm"
      aria-labelledby={titleId}
      data-lenis-prevent
      onCancel={(e) => {
        e.preventDefault()
        close('opener')
      }}
      onClose={() => {
        // pregledač je sam zatvorio dijalog (npr. drugi Esc): i ruta se zatvara
        if (!closingRef.current && !dialogRef.current?.open) close('opener')
      }}
      onKeyDown={onKeyDown}
      onPointerDown={onPointerDown}
      onClick={onClick}
    >
      <div className="pm__panel">
        <div className="pm__bar">
          <button type="button" onClick={() => close('shop')} className={buttonClass('icon', 'w-auto! gap-1 px-3 font-bold text-small text-text')}>
            <Icon name="prev" className="size-[18px]" />
            {tx(shop.modal.back)}
          </button>
          <button ref={closeRef} type="button" onClick={() => close('opener')} aria-label={tx(shop.modal.close)} className={buttonClass('icon', 'text-text')}>
            <Icon name="close" />
          </button>
        </div>

        <div className="grid gap-s5 pb-s7 lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)] lg:items-start lg:gap-s7 lg:px-s7 lg:pt-s3 lg:pb-s7">
          <div className="pm-media">
            <ProductVisual product={product} sizes="(min-width: 64rem) 28rem, 90vw" alt={image} />
            <span className="shop-demo">{tx(shop.card.demo)}</span>
          </div>

          <div className="px-gutter lg:px-0">
            {tags.length > 0 && (
              <ul role="list" className="m-0 mb-s3 flex list-none flex-wrap gap-1.5 p-0">
                {tags.map((t) => (
                  <li key={t.en} className="shop-tag">
                    {tx(t)}
                  </li>
                ))}
              </ul>
            )}
            <h2 id={titleId} className="type-display m-0 text-h2 leading-none">
              {name}
            </h2>
            <p className="sr-only">{tx(shop.card.demoSr)}</p>
            <p className="m-0 mt-s3 max-w-[36rem]">{tx(product.description)}</p>

            {rows.length > 0 && (
              <dl className="pm-dl mt-s5 border-t border-line pt-s4">
                {rows.map(([label, value]) => (
                  <div key={label.en} className="contents">
                    <dt>{tx(label)}</dt>
                    <dd>{value}</dd>
                  </div>
                ))}
              </dl>
            )}

            <div className="mt-s5 grid gap-s4 border-t border-line pt-s5">
              {isCoffee && product.sizes.length > 1 && (
                <fieldset className="m-0 border-0 p-0">
                  <legend className="mb-s2 p-0 type-label text-muted">{tx(L_.size)}</legend>
                  <div className="shop-seg max-w-[20rem]">
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
                  </div>
                </fieldset>
              )}

              {isCoffee && (
                <fieldset className="m-0 border-0 p-0" aria-describedby={`${uid}-grind-help`}>
                  <legend className="mb-s2 p-0 type-label text-muted">{tx(L_.grind)}</legend>
                  <div className="pm-grind">
                    {shop.grinds.map((g) => (
                      <label key={g.id} className="pm-grind__opt">
                        <input
                          type="radio"
                          name={`${uid}-grind`}
                          value={g.id}
                          checked={g.id === grind}
                          onChange={() => setGrind(g.id)}
                          className="sr-only"
                        />
                        {tx(g.label)}
                      </label>
                    ))}
                  </div>
                  <p id={`${uid}-grind-help`} className="m-0 mt-s2 text-small text-muted">
                    {tx(shop.grindHelp)}
                  </p>
                </fieldset>
              )}

              <Price
                cents={cents}
                grams={size?.grams}
                showGrams={!!size}
                className="text-muted"
                amountClassName="text-[1.75rem] font-extrabold text-text"
              />

              <div>
                <Button onClick={add} aria-describedby={titleId} className="w-full justify-center sm:w-auto">
                  {tx(L_.addToCart)}
                </Button>
                <p role="status" className="m-0 mt-s2 min-h-[1.5em] text-small font-semibold">
                  {added ? tx(shop.cart.toast) : ''}
                </p>
              </div>

              <p className="m-0 text-micro text-muted">{tf(site.demo)}</p>
            </div>
          </div>
        </div>
      </div>
    </dialog>
  )
}
