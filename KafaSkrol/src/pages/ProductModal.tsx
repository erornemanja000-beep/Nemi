// Modal proizvoda na /p/:slug, preko početne (Home je roditeljska ruta, pa prodavnica ostaje ispod).
//   - Ljuska je Overlay (components/Overlay.tsx, Z8): role="dialog" + aria-modal, zarobljen fokus, Esc,
//     klik na pozadinu, lockScroll i data-lenis-prevent. Na telefonu je ceo ekran (variant „sheet"), a od
//     64rem panel u sredini (.pm-panel u sections/shop.css). Nivo je isti kao paneli headera, ispod toast-a.
//   - Redosled (Z15): opis, pa izbor veličine i mlevenja, cena i dugme, pa tabela (Origin … Roasted on).
//     Ispod 64rem su cena i dugme lepljiva traka na dnu dijaloga (.pm-buy), a tabela i demo napomena
//     idu iznad nje (CSS order), pa je dugme uvek u ekranu. U DOM-u (i za tastaturu) redosled je isti na
//     svim širinama.
//   - Esc, „×", klik na pozadinu i „Back to the shop" zatvaraju: ako je modal otvoren iz aplikacije, korak
//     nazad u istoriji (vraća na /), a pri hladnom otvaranju zamena sa / i skok na prodavnicu.
//     Dugme „nazad" u pregledaču radi isto.
//   - Fokus vraća ovaj fajl, ne Overlay (restoreFocus → false): na element koji je otvorio modal, uz isti
//     položaj stranice. Korak nazad na adresu sa #sidrom (/#find-your-cup) natera pregledač da skoči na
//     sidro i skine fokus, pa se vraćanje ponavlja u sledećem kadru. Kad otvarača nema (hladno otvaranje,
//     rezultat pretrage, Safari ne fokusira link na klik): prodavnica i link kartice ovog proizvoda.
//   - Polja iz tekstovi.md („Natpisi na kartici proizvoda"): farma (fiktivna), „Roasted on" (lastRoastDate),
//     „Best before" samo kad bestBefore() ima pravilo (do odluke korisnika red se ne prikazuje).
//   - Nepoznat slug i oprema bez cene (PrAG) vode na /.
import { useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { Navigate, useLocation, useNavigate, useParams } from 'react-router-dom'
import { Button, buttonClass } from '../components/Button'
import { Icon } from '../components/Icon'
import { Overlay } from '../components/Overlay'
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
import { getLenis, scrollToTarget } from '../lib/motion'
import '../sections/shop.css'

/** Položaj elementa na stranici, uz scroll-margin-top (visina headera). */
const pageY = (el: HTMLElement) => window.scrollY + el.getBoundingClientRect().top - (parseFloat(getComputedStyle(el).scrollMarginTop) || 0)

/**
 * Skok na položaj bez animacije. Lenis prvo ponovo meri stranicu: dok je skrol bio zaključan, nestao je
 * klizač, pa je visina bila drugačija, a Lenis bi skok skratio na staru granicu.
 */
function jumpTo(y: number) {
  getLenis()?.resize()
  scrollToTarget(y, true)
}

/** Fokus ostaje kod nas (vidi gore), Overlay ga ne vraća. */
const noRestore = () => false

export default function ProductModal() {
  const { slug = '' } = useParams()
  const product = productBySlug(slug)
  if (!product || !isListed(product)) return <Navigate to="/" replace />
  return <ProductDialog key={product.slug} product={product} />
}

type Restore = 'opener' | 'shop'

/** Prodavnica u ekranu, zajedno sa karticom proizvoda; fokus na kartici (ili naslovu prodavnice). */
function backToShop(card: HTMLElement | null) {
  const shopEl = document.getElementById('find-your-cup')
  if (!shopEl) return
  let y = pageY(shopEl)
  const box = card?.closest('article')
  if (box) {
    const bottom = window.scrollY + box.getBoundingClientRect().bottom
    if (bottom - y > window.innerHeight) y = bottom - window.innerHeight + 16
  }
  jumpTo(y)
  const target = card ?? document.getElementById('t-shop')
  target?.focus({ preventScroll: true })
}

function ProductDialog({ product }: { product: Product }) {
  const { lang, tx, tf } = useLang()
  const navigate = useNavigate()
  const location = useLocation()
  const uid = useId()
  const titleId = `${uid}-title`

  const closeRef = useRef<HTMLButtonElement>(null)
  const openerRef = useRef<HTMLElement | null>(null)
  const pageYRef = useRef(0)
  const closingRef = useRef(false)
  const mountedRef = useRef(false)
  // otvoren iz aplikacije (postoji korak nazad) ili hladno (/p/<slug> u adresi)
  const inApp = location.key !== 'default'
  const restoreRef = useRef<Restore>(inApp ? 'opener' : 'shop')

  const [grams, setGrams] = useState(product.sizes[0]?.grams ?? 0)
  const [grind, setGrind] = useState<GrindId>('whole')
  const roast = useMemo(() => lastRoastDate(), [])

  const slug = product.slug
  const isCoffee = product.kind === 'coffee'
  const size = product.sizes.find((s) => s.grams === grams) ?? product.sizes[0]
  const cents = size?.priceCents ?? product.priceCents ?? 0
  const name = tx(product.name)

  // otvarač i položaj stranice: pre nego što Overlay (useEffect) pomeri fokus u panel, i samo jednom
  // (StrictMode u dev-u ponovo pokreće efekat kad je fokus već u panelu)
  const capturedRef = useRef(false)
  useLayoutEffect(() => {
    if (capturedRef.current) return
    capturedRef.current = true
    const active = document.activeElement
    openerRef.current = active instanceof HTMLElement && active !== document.body ? active : null
    pageYRef.current = window.scrollY
  }, [])

  // vraćanje fokusa posle zatvaranja; posle Overlay-evog lockScroll(false), zato u microtask-u.
  // StrictMode (dev) odmah ponovo montira, pa tada nema vraćanja.
  useEffect(() => {
    mountedRef.current = true
    closingRef.current = false
    return () => {
      mountedRef.current = false
      closingRef.current = true
      queueMicrotask(() => {
        if (mountedRef.current) return
        const card = document.querySelector<HTMLElement>(`[data-product-link="${CSS.escape(slug)}"]`)
        const opener = openerRef.current?.isConnected ? openerRef.current : null
        if (restoreRef.current === 'shop' || !opener) {
          // u sledećem kadru, posle eventualnog skoka pregledača na #sidro
          requestAnimationFrame(() => backToShop(card))
          return
        }
        const restore = () => {
          if (Math.abs(window.scrollY - pageYRef.current) > 1) jumpTo(pageYRef.current)
          opener.focus({ preventScroll: true })
        }
        restore()
        requestAnimationFrame(restore)
      })
    }
  }, [slug])

  const close = (restore: Restore) => {
    if (closingRef.current) return
    closingRef.current = true
    // posle hladnog otvaranja nema stranice iza modala: uvek na prodavnicu
    restoreRef.current = inApp ? restore : 'shop'
    if (inApp) navigate(-1)
    else navigate('/', { replace: true })
  }

  // visina lepljive trake (ispod 64rem): toast (Toast.tsx, chrome.css) stoji iznad nje, ne preko dugmeta
  const buyRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const el = buyRef.current
    const root = document.documentElement
    if (!el || typeof ResizeObserver === 'undefined') return
    const ro = new ResizeObserver(() => {
      if (getComputedStyle(el).position === 'sticky') root.style.setProperty('--pm-buy-h', `${el.offsetHeight}px`)
      else root.style.removeProperty('--pm-buy-h')
    })
    ro.observe(el)
    return () => {
      ro.disconnect()
      root.style.removeProperty('--pm-buy-h')
    }
  }, [])

  // toast iz korpe (iznad panela, aria-live) javlja dodavanje
  const add = () => {
    if (product.kind === 'gear') addToCart(slug, null, null)
    else if (size) addToCart(slug, size.grams, isCoffee ? grind : null)
  }

  const best = bestBefore(roast)
  const T = shop.labels
  const rows: [L, string][] = []
  const push = (label: L, value: string | undefined) => {
    if (value) rows.push([label, value])
  }
  push(T.origin, product.origin && tx(product.origin))
  push(T.process, product.process && tx(product.process))
  push(T.variety, product.variety && tx(product.variety))
  push(T.altitude, product.altitude && formatAltitude(product.altitude, lang))
  push(T.notes, product.notes && tx(product.notes).join(' · '))
  push(T.bestFor, product.bestFor && tx(product.bestFor))
  push(T.roast, product.roast && tx(product.roast))
  push(T.farm, product.farm && tx(product.farm))
  if (isCoffee) push(T.roastedOn, formatDate(roast, lang))
  if (isCoffee && best) push(T.bestBefore, formatDate(best, lang))
  if (product.kind === 'set' && size) push(T.size, formatGrams(size.grams, lang))

  // alt velike slike: kesa (Z3 1c) ili oprema (media.gear); CSS rezerva je aria-hidden
  const imageAlt = product.kind === 'gear' ? '' : tf(shop.modal.imageAlt, { name })
  const tags = productTags(product)

  return (
    <Overlay
      open
      onClose={() => close('opener')}
      labelledBy={titleId}
      variant="sheet"
      initialFocus={closeRef}
      restoreFocus={noRestore}
      className="pm-panel"
    >
      <div className="pm__bar">
        <button type="button" onClick={() => close('shop')} className="inline-flex min-h-tap cursor-pointer items-center gap-1 rounded-pill border-0 bg-transparent px-3 text-small font-bold text-text">
          <Icon name="prev" className="size-[18px]" />
          {tx(shop.modal.back)}
        </button>
        <button ref={closeRef} type="button" onClick={() => close('opener')} aria-label={tx(shop.modal.close)} className={buttonClass('icon', 'text-text')}>
          <Icon name="close" />
        </button>
      </div>

      {/* 64–80rem: uža slika i razmak, da izbor mlevenja stane u 2 reda i dugme bude u ekranu i na 1024×768 */}
      <div className="grid gap-s5 lg:grid-cols-[minmax(0,4fr)_minmax(0,6fr)] lg:items-start lg:gap-s6 lg:px-s7 lg:pt-s3 lg:pb-s7 xl:grid-cols-[minmax(0,5fr)_minmax(0,6fr)] xl:gap-s7">
        <div className="pm-media">
          <ProductVisual product={product} sizes="(min-width: 64rem) 28rem, 90vw" alt={imageAlt} />
          <span className="shop-demo" aria-hidden="true">
            {tx(shop.card.demo)}
          </span>
        </div>

        {/* kolona teksta: na telefonu flex sa order (vidi gore i .pm-buy u shop.css) */}
        <div className="pm-body px-gutter lg:px-0">
          <div>
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
          </div>

          {isCoffee && (
            <div className="pm-opts mt-s5 grid gap-s4 border-t border-line pt-s5">
              {product.sizes.length > 1 && (
                <fieldset className="m-0 border-0 p-0">
                  <legend className="mb-s2 p-0 type-label text-muted">{tx(T.size)}</legend>
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

              <fieldset className="m-0 border-0 p-0" aria-describedby={`${uid}-grind-help`}>
                <legend className="mb-s2 p-0 type-label text-muted">{tx(T.grind)}</legend>
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
            </div>
          )}

          {/* cena i dugme; ispod 64rem lepljiva traka na dnu dijaloga */}
          <div ref={buyRef} className="pm-buy">
            <Price
              cents={cents}
              grams={size?.grams}
              showGrams={!!size}
              className="min-w-0 text-muted"
              amountClassName="text-[1.5rem] font-extrabold text-text lg:text-[1.75rem]"
            />
            <Button onClick={add} aria-describedby={titleId} className="flex-none justify-center whitespace-nowrap max-lg:px-6! lg:w-fit">
              <span className="sm:hidden">{tx(T.addToCartShort)}</span>
              <span className="max-sm:hidden">{tx(T.addToCart)}</span>
            </Button>
          </div>

          <p className="pm-note m-0 mt-s4 text-micro text-muted">{tf(site.demo)}</p>

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
        </div>
      </div>
    </Overlay>
  )
}
