// Prodavnica „Find your cup" (#find-your-cup, Z9). Raspored iz skice („7 · Prodavnica"), tekst iz
// shop.ts, boje i razmaci iz tokena:
//   traka „Versandkostenfrei ab € 45" + „Konzept / Demo" · naslov, podnaslov, tekst sa CTA na #tasting-set
//   i SHOP-1 · filteri Brew, Flavor, Roast, Type (čipovi; na telefonu horizontalne trake) · broj, reset i
//   sortiranje · grupe Coffee, Sets, Equipment sa brojem · prazno stanje · blok o dostavi sa dugmetom na /versand.
// Filter iz linka: ?brew=filter|espresso pri učitavanju (i kad se search promeni u aplikaciji).
// Filter iz drugih sekcija: window događaj SHOP_FILTER_EVENT ('kafa:shop-filter', detail { brew }).
// Kartice se pojavljuju preko reveal.ts; promena filtera ili sortiranja daje fade mreže (WAAPI, samo
// opacity; u reduced motion odmah).
import { useEffect, useLayoutEffect, useMemo, useRef, useState, type CSSProperties } from 'react'
import { useLocation } from 'react-router-dom'
import { Button } from '../components/Button'
import { Icon } from '../components/Icon'
import { Photo } from '../components/Photo'
import { ProductCard } from '../components/ProductCard'
import { products } from '../content/products'
import { shop, type SortId } from '../content/shop'
import { site } from '../content/site'
import type { L } from '../content/types'
import { useLang } from '../i18n/LangContext'
import {
  brewFromSearch,
  EMPTY_FILTERS,
  filterKey,
  filterProducts,
  filtersFromEvent,
  filtersFromSearch,
  groupProducts,
  hasActiveFilters,
  SHOP_FILTER_EVENT,
  toggleFilter,
  type FilterGroupId,
  type FilterState,
  type ShopGroupId,
} from '../lib/filters'
import { lastRoastDate } from '../lib/format'
import { useReveal } from '../lib/reveal'
import { isReducedMotion } from '../lib/useMedia'
import './shop.css'

type ChipGroup = {
  id: FilterGroupId
  label: L
  options: { id: string; label: L }[]
  /** „All" (samo Brew, tekstovi.md) */
  all?: L
  help?: L
}

const F = shop.filters
const chipGroups: ChipGroup[] = [
  { id: 'brew', label: F.brew.label, options: F.brew.options, all: F.brew.all },
  { id: 'flavor', label: F.flavor.label, options: F.flavor.options },
  { id: 'roast', label: F.roast.label, options: F.roast.options, help: F.roast.help },
  { id: 'type', label: F.type.label, options: F.type.options },
]

/** Naslovi grupa u mreži = natpisi Type filtera (shop.ts). */
const groupLabel: Record<ShopGroupId, L> = {
  coffee: F.type.options.find((o) => o.id === 'coffee')!.label,
  set: F.type.options.find((o) => o.id === 'set')!.label,
  equipment: F.type.options.find((o) => o.id === 'equipment')!.label,
}

/** Koliko dugo mreža posle filtera zadržava staru visinu: fade (360 ms) + Lenis skok do prodavnice (~1,2 s). */
const HOLD_MS = 1600

/** Trajanje tokena u ms (--dur-base je 1ms u reduced motion). */
function tokenMs(name: string, fallback: number): number {
  const value = parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name))
  return Number.isFinite(value) ? value : fallback
}

export function Shop() {
  const { tx, tf } = useLang()
  const location = useLocation()
  const [filters, setFilters] = useState<FilterState>(() => filtersFromSearch(location.search))
  const [sort, setSort] = useState<SortId>('newest')
  const roast = useMemo(() => lastRoastDate(), [])
  const list = useMemo(() => filterProducts(products, filters, sort), [filters, sort])
  const groups = groupProducts(list)
  const active = hasActiveFilters(filters)
  const revealRef = useReveal<HTMLDivElement>()
  const gridRef = useRef<HTMLDivElement>(null)
  const titleRef = useRef<HTMLHeadingElement>(null)

  // filter iz drugih sekcija (Brew guide): ostale grupe se brišu, kao pri otvaranju sa ?brew=.
  // Fokus prelazi na naslov prodavnice (skrol radi pošiljalac), da tastatura nastavi odavde.
  useEffect(() => {
    const onFilter = (e: Event) => {
      const next = filtersFromEvent((e as CustomEvent<unknown>).detail)
      if (!next) return
      setFilters(next)
      titleRef.current?.focus({ preventScroll: true })
    }
    window.addEventListener(SHOP_FILTER_EVENT, onFilter)
    return () => window.removeEventListener(SHOP_FILTER_EVENT, onFilter)
  }, [])

  // ?brew= kad se adresa promeni bez ponovnog učitavanja (npr. <Link to="/?brew=filter#find-your-cup">);
  // stanje se usklađuje u renderu (React: „adjusting state when a prop changes"), bez efekta
  const [lastSearch, setLastSearch] = useState(location.search)
  if (location.search !== lastSearch) {
    setLastSearch(location.search)
    const brew = brewFromSearch(location.search)
    if (brew) setFilters({ ...EMPTY_FILTERS, brew: [brew] })
  }

  // Posle promene filtera ili sortiranja (pre iscrtavanja, da nova mreža ne trepne):
  //  - mreža koja se smanjuje zadržava staru visinu (min-height) HOLD_MS, pa se ne pomera ništa ispod
  //    prodavnice dok traje skok na #find-your-cup (Lenis iz Brew guide-a) ili fade;
  //  - fade mreže (samo opacity, --dur-base; u reduced motion bez fade-a).
  const key = filterKey(filters, sort)
  const lastKey = useRef(key)
  // poslednja iscrtana visina mreže (ResizeObserver; prati i jezik, širinu i zadržanu visinu)
  const shownHeight = useRef(0)
  const holdTimer = useRef(0)
  useEffect(() => {
    const el = gridRef.current
    if (!el || typeof ResizeObserver === 'undefined') return
    const ro = new ResizeObserver(() => {
      shownHeight.current = el.offsetHeight
    })
    ro.observe(el)
    return () => {
      ro.disconnect()
      window.clearTimeout(holdTimer.current)
    }
  }, [])
  useLayoutEffect(() => {
    const el = gridRef.current
    if (!el || key === lastKey.current) return
    lastKey.current = key
    const shown = shownHeight.current
    el.style.minHeight = ''
    if (el.offsetHeight < shown) {
      el.style.minHeight = `${shown}px`
      window.clearTimeout(holdTimer.current)
      holdTimer.current = window.setTimeout(() => {
        el.style.minHeight = ''
      }, HOLD_MS)
    }
    if (isReducedMotion() || typeof el.animate !== 'function') return
    el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: tokenMs('--dur-base', 360), easing: 'cubic-bezier(0.22, 1, 0.36, 1)' })
  }, [key])

  const toggle = (group: FilterGroupId, value: string) => setFilters((f) => toggleFilter(f, group, value))
  const reset = () => setFilters(EMPTY_FILTERS)
  const count = list.length === 1 ? tx(F.countOne) : tf(F.count, { n: list.length })

  return (
    <section id="find-your-cup" aria-labelledby="t-shop" className="scroll-mt-header bg-bg px-gutter py-s8 text-text lg:py-s9">
      <div className="mx-auto max-w-site">
        {/* traka: dostava + demo */}
        <p className="m-0 flex flex-wrap items-center gap-x-s3 gap-y-s2 text-small font-semibold">
          <span>{tx(shop.bar)}</span>
          <span className="shop-demo-note">{tx(site.demoShort)}</span>
        </p>

        {/* naslov i SHOP-1 */}
        <div className="mt-s5 grid gap-s5 lg:mt-s6 lg:grid-cols-12 lg:items-start lg:gap-s7">
          <div className="lg:col-span-7">
            <h2
              ref={titleRef}
              id="t-shop"
              tabIndex={-1}
              className="type-display m-0 text-[length:var(--fs-section,clamp(2.5rem,1.5rem+4vw,4.5rem))] leading-none focus:outline-none"
            >
              {tx(shop.title)}
            </h2>
            <p className="m-0 mt-s3 max-w-[34rem] text-[1.125rem] leading-snug font-semibold">{tx(shop.subtitle)}</p>
            <p className="m-0 mt-s3 max-w-[34rem]">{tx(shop.text)}</p>
            <a href={shop.cta.href} className="mt-s1 inline-flex min-h-tap items-center gap-1 font-bold text-accent-text underline underline-offset-4">
              {tx(shop.cta.label)}
              <Icon name="next" className="size-4" />
            </a>
          </div>
          <div className="lg:col-span-5">
            <Photo
              id="shop-1"
              sizes="(min-width: 64rem) 34vw, 100vw"
              className="aspect-[16/10] h-auto w-full rounded-card object-cover object-[50%_62%] lg:aspect-[5/4]"
            />
          </div>
        </div>

        {/* filteri: telefon = grupe jedna ispod druge (trake), od 64rem grupe u redu i u novi red kad ne staju */}
        <div className="mt-s6 grid gap-s4 border-y border-line py-s4 lg:mt-s7 lg:flex lg:flex-wrap lg:gap-x-s7 lg:gap-y-s4 lg:py-s5">
          {chipGroups.map((g) => {
            const selected: readonly string[] = filters[g.id]
            const labelId = `shop-filter-${g.id}`
            return (
              <div key={g.id} role="group" aria-labelledby={labelId} className="min-w-0">
                <p id={labelId} className="m-0 mb-s2 type-label text-muted">
                  {tx(g.label)}
                </p>
                <div className="shop-strip">
                  {g.all && (
                    <button type="button" className="shop-chip" aria-pressed={selected.length === 0} onClick={() => setFilters((f) => ({ ...f, [g.id]: [] }))}>
                      {tx(g.all)}
                    </button>
                  )}
                  {g.options.map((o) => (
                    <button key={o.id} type="button" className="shop-chip" aria-pressed={selected.includes(o.id)} onClick={() => toggle(g.id, o.id)}>
                      {tx(o.label)}
                    </button>
                  ))}
                </div>
                {/* od 64rem pomoćni tekst ne širi grupu: širok je koliko čipovi (w-0 + min-w-full) */}
                {g.help && <p className="m-0 mt-s2 text-micro text-muted lg:w-0 lg:min-w-full">{tx(g.help)}</p>}
              </div>
            )
          })}
        </div>

        {/* broj, reset, sortiranje */}
        <div className="mt-s4 flex flex-wrap items-center justify-between gap-x-s4 gap-y-s2">
          <div className="flex flex-wrap items-center gap-x-s3">
            <p role="status" className="m-0 text-small font-bold">
              {count}
            </p>
            {active && (
              <button type="button" onClick={reset} className="inline-flex min-h-tap cursor-pointer items-center border-0 bg-transparent p-0 text-small font-semibold text-accent-text underline underline-offset-4">
                {tx(F.reset)}
              </button>
            )}
          </div>
          <label className="flex items-center gap-s2">
            <span className="type-label text-muted">{tx(F.sort.label)}</span>
            <span className="shop-select">
              <select value={sort} onChange={(e) => setSort(e.target.value as SortId)}>
                {F.sort.options.map((o) => (
                  <option key={o.id} value={o.id}>
                    {tx(o.label)}
                  </option>
                ))}
              </select>
              <Icon name="next" className="shop-select__icon" />
            </span>
          </label>
        </div>

        {/* mreža po grupama (shop.css): grupa sa jednom karticom zauzima jednu kolonu, pa na telefonu
            Sets i Equipment stoje jedna pored druge; oprema sa više kartica je na telefonu traka */}
        <div ref={revealRef}>
          <div ref={gridRef} className="shop-groups mt-s5">
            {groups.map((g) => (
              <section
                key={g.id}
                aria-labelledby={`shop-group-${g.id}`}
                className="shop-group"
                style={{ '--span': Math.min(g.items.length, 3), '--span-sm': g.items.length > 1 ? 2 : 1 } as CSSProperties}
              >
                <h3 id={`shop-group-${g.id}`} className="m-0 mb-s3 type-label text-text">
                  {tx(groupLabel[g.id])} · {g.items.length}
                </h3>
                <ul role="list" className={`shop-grid ${g.id === 'equipment' && g.items.length > 1 ? 'shop-grid--strip' : ''}`}>
                  {g.items.map((p) => (
                    <li key={p.slug} data-reveal className="min-w-0">
                      <ProductCard product={p} roast={roast} />
                    </li>
                  ))}
                </ul>
              </section>
            ))}

            {list.length === 0 && (
              <div className="col-span-full grid justify-items-center gap-s4 rounded-card bg-surface px-s5 py-s7 text-center">
                <Photo id="shop-bg-1" sizes="8rem" className="aspect-square h-auto w-32 rounded-full object-cover object-top" />
                <p className="m-0 text-h3 font-bold">{tx(F.empty)}</p>
                <Button onClick={reset}>{tx(F.reset)}</Button>
              </div>
            )}
          </div>
        </div>

        {/* dostava i preuzimanje */}
        <div className="mt-s8 grid border-t border-line lg:mt-s9 lg:grid-cols-2 lg:gap-s7">
          <div className="pt-s6 lg:py-s7">
            <h3 className="type-display m-0 text-[1.75rem] leading-none">{tx(shop.shippingInfo.title)}</h3>
            <p className="m-0 mt-s3 max-w-[34rem]">{tx(shop.shippingInfo.text)}</p>
            <Button to={shop.shippingInfo.cta.href} className="mt-s5">
              {tx(shop.shippingInfo.cta.label)}
            </Button>
          </div>
          {/* dekor: visina je rezervisana (telefon 2:1, desktop visina teksta), da sidra ispod ne kasne;
              na desktopu odmaknut od razdelnika, da ga zrna ne dodiruju */}
          <div className="shop-ship-media mt-s5 lg:my-s6" aria-hidden="true">
            <Photo id="shop-bg-2" sizes="(min-width: 64rem) 45vw, 100vw" />
          </div>
        </div>
      </div>
    </section>
  )
}
