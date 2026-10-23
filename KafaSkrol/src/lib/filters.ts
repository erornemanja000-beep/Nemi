// Filteri prodavnice „Find your cup" (Z9). Čiste funkcije, bez DOM-a i React-a:
//   - unutar grupe važi „ili", između grupa „i";
//   - prazna grupa ne filtrira ništa;
//   - set i oprema nemaju brew/flavor/roast grupe, pa ispadaju čim je aktivan Brew, Flavor ili Roast;
//   - Type Coffee = kafe sa kofeinom (5), Decaf = Pause (1);
//   - u prodavnici je samo ono što ima cenu (oprema sa priceCents: null se ne prikazuje, PrAG).
// Filter iz linka: ?brew=filter|espresso (filtersFromSearch). Filter iz drugih sekcija: događaj
// SHOP_FILTER_EVENT na window, sa detail { brew } (odluka direktora, z13-izmene.md).
import type { BrewGroup, FlavorGroup, L, Product, RoastGroup, TypeGroup } from '../content/types.ts'
import type { SortId } from '../content/shop.ts'

export type FilterState = {
  brew: BrewGroup[]
  flavor: FlavorGroup[]
  roast: RoastGroup[]
  type: TypeGroup[]
}

export type FilterGroupId = keyof FilterState

export const EMPTY_FILTERS: FilterState = { brew: [], flavor: [], roast: [], type: [] }

const BREW_IDS: readonly BrewGroup[] = ['espresso', 'filter']

/** Grupe mreže, redom: kafe (sa decaf), set, oprema. Natpisi su shop.filters.type.options. */
export type ShopGroupId = 'coffee' | 'set' | 'equipment'
export const SHOP_GROUPS: readonly ShopGroupId[] = ['coffee', 'set', 'equipment']

/** Događaj na window: Brew guide i druge sekcije biraju filter prodavnice bez ponovnog učitavanja. */
export const SHOP_FILTER_EVENT = 'kafa:shop-filter'
export type ShopFilterDetail = { brew: BrewGroup }

const isBrew = (v: unknown): v is BrewGroup => typeof v === 'string' && (BREW_IDS as readonly string[]).includes(v)

/** Da li proizvod sme u prodavnicu: kafa i set sa pakovanjem, oprema samo sa cenom. */
export function isListed(p: Product): boolean {
  if (p.kind === 'gear') return p.priceCents != null
  return p.sizes.length > 0
}

/** Oznake na kartici i u modalu: prženje, za šta, tag („House blend", „Limited lot", „Decaf"). */
export function productTags(p: Product): L[] {
  return [p.roast, p.bestFor, p.tag].filter((t): t is L => !!t)
}

/** Najniža cena (centi): prvo pakovanje kafe/seta ili cena opreme. Za sortiranje. */
export function basePrice(p: Product): number {
  if (p.kind === 'gear') return p.priceCents ?? Number.POSITIVE_INFINITY
  return Math.min(...p.sizes.map((s) => s.priceCents))
}

/** Grupa mreže kojoj proizvod pripada. */
export function shopGroup(p: Product): ShopGroupId {
  if (p.kind === 'coffee') return 'coffee'
  return p.kind === 'set' ? 'set' : 'equipment'
}

const anyOf = <T>(active: readonly T[], values: readonly T[]) => active.length === 0 || values.some((v) => active.includes(v))

/** Da li proizvod prolazi sve aktivne grupe filtera. */
export function matches(p: Product, f: FilterState): boolean {
  return (
    anyOf(f.brew, p.brew) &&
    anyOf(f.flavor, p.flavor) &&
    anyOf(f.roast, p.roastGroups) &&
    (f.type.length === 0 || f.type.includes(p.type))
  )
}

/**
 * Sortiranje. „Newest roast": sve kafe se prže istog dana (lastRoastDate), pa ostaje redosled iz
 * products.ts. Kod iste cene redosled iz products.ts ostaje (sort je stabilan).
 */
export function sortProducts(list: readonly Product[], sort: SortId): Product[] {
  const out = [...list]
  if (sort === 'price-asc') out.sort((a, b) => basePrice(a) - basePrice(b))
  if (sort === 'price-desc') out.sort((a, b) => basePrice(b) - basePrice(a))
  return out
}

/** Proizvodi u prodavnici posle filtera i sortiranja. */
export function filterProducts(all: readonly Product[], f: FilterState, sort: SortId = 'newest'): Product[] {
  return sortProducts(
    all.filter((p) => isListed(p) && matches(p, f)),
    sort,
  )
}

/** Mreža po grupama (Coffee, Sets, Equipment), bez praznih grupa. */
export function groupProducts(list: readonly Product[]): { id: ShopGroupId; items: Product[] }[] {
  return SHOP_GROUPS.map((id) => ({ id, items: list.filter((p) => shopGroup(p) === id) })).filter((g) => g.items.length > 0)
}

export function hasActiveFilters(f: FilterState): boolean {
  return f.brew.length + f.flavor.length + f.roast.length + f.type.length > 0
}

/** Uključuje ili isključuje vrednost u grupi (vrednosti dolaze iz shop.filters.*.options). */
export function toggleFilter(f: FilterState, group: FilterGroupId, value: string): FilterState {
  const list: readonly string[] = f[group]
  const next = list.includes(value) ? list.filter((v) => v !== value) : [...list, value]
  return { ...f, [group]: next } as FilterState
}

/** Ključ stanja (za fade mreže pri promeni). */
export function filterKey(f: FilterState, sort: SortId): string {
  return [f.brew, f.flavor, f.roast, f.type].map((g) => [...g].sort().join(',')).join('|') + `|${sort}`
}

/** ?brew=filter|espresso → izabran Brew; sve ostalo se ignoriše. */
export function brewFromSearch(search: string): BrewGroup | null {
  const value = new URLSearchParams(search).get('brew')
  return isBrew(value) ? value : null
}

/** Početno stanje iz URL-a (location.search). */
export function filtersFromSearch(search: string): FilterState {
  const brew = brewFromSearch(search)
  return brew ? { ...EMPTY_FILTERS, brew: [brew] } : EMPTY_FILTERS
}

/** detail događaja SHOP_FILTER_EVENT → novo stanje (ostale grupe se brišu), ili null za neispravan detail. */
export function filtersFromEvent(detail: unknown): FilterState | null {
  const brew = (detail as Partial<ShopFilterDetail> | null)?.brew
  return isBrew(brew) ? { ...EMPTY_FILTERS, brew: [brew] } : null
}
