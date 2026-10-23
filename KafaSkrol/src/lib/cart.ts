// Korpa (plan, Interfejs 8). Sve sume su u centima. Dostava (Austrija) je iz sadržaja,
// shop.shipping: feeCents ispod freeFromCents, od freeFromCents (uključivo) besplatna.
// Čuva se u localStorage pod storageKeys.cart; druga kartica pregledača dobija izmene preko `storage`.
// addToCart sam prikazuje toast (Toast.tsx), openCart ga skida. Stanje „otvorena" se ne čuva.
import { useSyncExternalStore } from 'react'
import { storageKeys } from '../config/site'
import { products } from '../content/products'
import { shop } from '../content/shop'
import type { GrindId, L } from '../content/types'

/** Najveća količina jedne stavke (demo, zaštita od greške u kucanju). */
export const MAX_QTY = 99

export type CartLine = {
  slug: string
  /** grami pakovanja; null za opremu */
  grams: number | null
  /** mlevenje; null za opremu i set */
  grind: GrindId | null
  qty: number
}

type CartState = { lines: CartLine[]; open: boolean }

export type CartSummary = {
  lines: (CartLine & { key: string; unitCents: number; lineCents: number })[]
  count: number
  subtotalCents: number
  shippingCents: number
  toFreeShippingCents: number
  totalCents: number
  open: boolean
}

const lineKey = (l: Pick<CartLine, 'slug' | 'grams' | 'grind'>) => `${l.slug}|${l.grams ?? ''}|${l.grind ?? ''}`

const GRINDS = new Set<string>(shop.grinds.map((g) => g.id))

/** Cena jednog komada: veličina kafe/seta ili cena opreme. null = proizvod ili veličina ne postoji. */
export function unitPrice(slug: string, grams: number | null): number | null {
  const p = products.find((x) => x.slug === slug)
  if (!p) return null
  if (grams === null) return p.priceCents ?? null
  return p.sizes.find((s) => s.grams === grams)?.priceCents ?? null
}

/** Stavke iz localStorage; sve što ne odgovara današnjem sadržaju (stari slug, cena, mlevenje) ispada. */
function load(): CartLine[] {
  try {
    const raw = JSON.parse(localStorage.getItem(storageKeys.cart) ?? '[]') as unknown
    if (!Array.isArray(raw)) return []
    const lines: CartLine[] = []
    for (const l of raw as Partial<CartLine>[]) {
      if (typeof l?.slug !== 'string' || !Number.isInteger(l.qty) || (l.qty ?? 0) < 1) continue
      const grams = typeof l.grams === 'number' ? l.grams : null
      if (unitPrice(l.slug, grams) === null) continue
      const grind = typeof l.grind === 'string' && GRINDS.has(l.grind) ? l.grind : null
      lines.push({ slug: l.slug, grams, grind, qty: Math.min(l.qty as number, MAX_QTY) })
    }
    return lines
  } catch {
    return []
  }
}

function summarize(s: CartState): CartSummary {
  const lines = s.lines.map((l) => {
    const unitCents = unitPrice(l.slug, l.grams) ?? 0
    return { ...l, key: lineKey(l), unitCents, lineCents: unitCents * l.qty }
  })
  const subtotalCents = lines.reduce((sum, l) => sum + l.lineCents, 0)
  const { feeCents, freeFromCents } = shop.shipping
  const free = subtotalCents === 0 || subtotalCents >= freeFromCents
  const shippingCents = free ? 0 : feeCents
  return {
    lines,
    count: lines.reduce((n, l) => n + l.qty, 0),
    subtotalCents,
    shippingCents,
    toFreeShippingCents: free ? 0 : freeFromCents - subtotalCents,
    totalCents: subtotalCents + shippingCents,
    open: s.open,
  }
}

let state: CartState = { lines: typeof window === 'undefined' ? [] : load(), open: false }
let summary = summarize(state)
const listeners = new Set<() => void>()

function commit(next: CartState, persist = true) {
  const linesChanged = next.lines !== state.lines
  state = next
  summary = summarize(state)
  if (linesChanged && persist) {
    try {
      localStorage.setItem(storageKeys.cart, JSON.stringify(state.lines))
    } catch {
      /* storage nije dostupan */
    }
  }
  listeners.forEach((l) => l())
}

// izmena korpe u drugoj kartici
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === storageKeys.cart || e.key === null) commit({ ...state, lines: load() }, false)
  })
}

export function addToCart(slug: string, grams: number | null, grind: GrindId | null, qty = 1) {
  if (unitPrice(slug, grams) === null || qty < 1) return
  const key = lineKey({ slug, grams, grind })
  const found = state.lines.find((l) => lineKey(l) === key)
  const lines = found
    ? state.lines.map((l) => (l === found ? { ...l, qty: Math.min(l.qty + qty, MAX_QTY) } : l))
    : [...state.lines, { slug, grams, grind, qty: Math.min(qty, MAX_QTY) }]
  commit({ ...state, lines })
  showToast('added')
}

/** Nova količina stavke (ključ iz useCart().lines[].key); 0 ili manje uklanja stavku. */
export function setQty(key: string, qty: number) {
  const lines =
    qty <= 0
      ? state.lines.filter((l) => lineKey(l) !== key)
      : state.lines.map((l) => (lineKey(l) === key ? { ...l, qty: Math.min(Math.round(qty), MAX_QTY) } : l))
  commit({ ...state, lines })
}

export const removeLine = (key: string) => setQty(key, 0)
/** Otvara korpu i skida toast: korpa pokazuje stavku, a toast bi na telefonu pokrio njeno dno (Z14). */
export function openCart() {
  commit({ ...state, open: true })
  clearToast()
}
export const closeCart = () => {
  if (state.open) commit({ ...state, open: false })
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export const useCart = () => useSyncExternalStore(subscribe, () => summary, () => summary)

// --- toast (Toast.tsx ga prikazuje u regionu aria-live="polite") ---
/** 'added' = shop.cart.toast. Ostale poruke (npr. demo pretplata, Z10) šalju svoj dvojezični tekst. */
export type ToastKind = 'added'
export type ToastMessage = ToastKind | L
let toast: { message: ToastMessage; id: number } | null = null
let toastId = 0
const toastListeners = new Set<() => void>()

/** Prikazuje poruku oko 4 s. Ista poruka dva puta zaredom se ponovo čita (novi id). */
export function showToast(message: ToastMessage) {
  toast = { message, id: ++toastId }
  toastListeners.forEach((l) => l())
}

export function clearToast() {
  toast = null
  toastListeners.forEach((l) => l())
}

function subscribeToast(listener: () => void) {
  toastListeners.add(listener)
  return () => toastListeners.delete(listener)
}

export const useToast = () => useSyncExternalStore(subscribeToast, () => toast, () => toast)
