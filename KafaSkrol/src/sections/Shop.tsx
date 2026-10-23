// Prodavnica „Find your cup" (#find-your-cup, Z9). Raspored iz skice („7 · Prodavnica"), tekst iz
// shop.ts, boje i razmaci iz tokena:
//   traka „Versandkostenfrei ab € 45" + „Konzept / Demo" · naslov, podnaslov, tekst sa CTA na #tasting-set
//   i SHOP-1 · filteri Brew, Flavor, Roast, Type (čipovi; na telefonu horizontalne trake) · broj, reset i
//   sortiranje · grupe Coffee, Sets, Equipment sa brojem · prazno stanje · blok o dostavi sa dugmetom na /versand.
// Filter iz linka: ?brew=filter|espresso pri učitavanju (i kad se search promeni u aplikaciji).
// Filter iz drugih sekcija: window događaj SHOP_FILTER_EVENT ('kafa:shop-filter', detail { brew }).
// Kartice se pojavljuju preko reveal.ts; promena filtera ili sortiranja daje fade mreže (WAAPI, samo
// opacity; u reduced motion odmah).
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
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

  // filter iz drugih sekcija (Brew guide): ostale grupe se brišu, kao pri otvaranju sa ?brew=
  useEffect(() => {
    const onFilter = (e: Event) => {
      const next = filtersFromEvent((e as CustomEvent<unknown>).detail)
      if (next) setFilters(next)
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

  // fade mreže posle promene filtera ili sortiranja (pre iscrtavanja, da nova mreža ne trepne)
  const key = filterKey(filters, sort)
  const lastKey = useRef(key)
  useLayoutEffect(() => {
    if (key === lastKey.current) return
    lastKey.current = key
    const el = gridRef.current
    if (!el || isReducedMotion() || typeof el.animate !== 'function') return
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
        <div className="mt-s5 grid gap-s5 lg:mt-s6 lg:grid-cols-12 lg:items-end lg:gap-s7">
          <div className="lg:col-span-7">
            <h2 id="t-shop" tabIndex={-1} className="type-display m-0 text-h2 leading-none focus:outline-none">
              {tx(shop.title)}
            </h2>
            <p className="m-0 mt-s3 max-w-[34rem] text-[1.125rem] leading-snug font-semibold">{tx(shop.subtitle)}</p>
            <p className="m-0 mt-s3 max-w-[34rem]">
              {tx(shop.text)}{' '}
              <a href={shop.cta.href} className="inline-flex min-h-tap items-center gap-1 font-bold whitespace-nowrap text-accent-text underline underline-offset-4">
                {tx(shop.cta.label)}
                <Icon name="next" className="size-4" />
              </a>
            </p>
          </div>
          <div className="lg:col-span-5">
            <Photo
              id="shop-1"
              sizes="(min-width: 64rem) 34vw, 100vw"
              className="aspect-[16/10] h-auto w-full rounded-card object-cover object-[50%_62%] lg:aspect-[5/4]"
            />
          </div>
        </div>

        {/* filteri */}
        <div className="mt-s6 grid gap-s4 border-y border-line py-s4 lg:mt-s7 lg:grid-cols-[1fr_1.15fr_1.35fr_1.4fr] lg:gap-s5 lg:py-s5">
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
                {g.help && <p className="m-0 mt-s2 text-micro text-muted">{tx(g.help)}</p>}
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

        {/* mreža po grupama */}
        <div ref={revealRef}>
          <div ref={gridRef} className="mt-s5">
            {groups.map((g) => (
              <section key={g.id} aria-labelledby={`shop-group-${g.id}`} className="mt-s6 first:mt-0 lg:mt-s7">
                <h3 id={`shop-group-${g.id}`} className="m-0 mb-s3 type-label text-text">
                  {tx(groupLabel[g.id])} · {g.items.length}
                </h3>
                <ul role="list" className={`shop-grid ${g.id === 'equipment' ? 'shop-grid--strip' : ''}`}>
                  {g.items.map((p) => (
                    <li key={p.slug} data-reveal className="min-w-0">
                      <ProductCard product={p} roast={roast} />
                    </li>
                  ))}
                </ul>
              </section>
            ))}

            {list.length === 0 && (
              <div className="grid justify-items-center gap-s4 rounded-card bg-surface px-s5 py-s7 text-center">
                <Photo id="shop-bg-1" sizes="8rem" className="aspect-square h-auto w-32 rounded-full object-cover object-top" />
                <p className="m-0 text-h3 font-bold">{tx(F.empty)}</p>
                <Button onClick={reset}>{tx(F.reset)}</Button>
              </div>
            )}
          </div>
        </div>

        {/* dostava i preuzimanje */}
        <div className="mt-s8 grid overflow-hidden rounded-card bg-surface lg:mt-s9 lg:grid-cols-2">
          <div className="order-2 p-s5 lg:order-1 lg:p-s7">
            <h3 className="type-display m-0 text-[1.75rem] leading-none">{tx(shop.shippingInfo.title)}</h3>
            <p className="m-0 mt-s3 max-w-[34rem]">{tx(shop.shippingInfo.text)}</p>
            <Button to={shop.shippingInfo.cta.href} className="mt-s5">
              {tx(shop.shippingInfo.cta.label)}
            </Button>
          </div>
          <div className="order-1 lg:order-2" aria-hidden="true">
            <Photo id="shop-bg-2" sizes="(min-width: 64rem) 45vw, 100vw" className="shop-ship-photo" />
          </div>
        </div>
      </div>
    </section>
  )
}
