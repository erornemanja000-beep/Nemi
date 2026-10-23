// Korpa (plan, Interfejs 8). STUB iz Z1 sa konačnim imenima i potpisima; doradu radi Z8.
// Sve sume su u centima. Dostava u Austriji: € 4,50 ispod € 45, od € 45 (uključivo) besplatna.
// Čuva se u localStorage pod storageKeys.cart. addToCart sam prikazuje toast (Toast.tsx).
import { useSyncExternalStore } from 'react'
import { storageKeys } from '../config/site'
import { products } from '../content/products'
import type { GrindId } from '../content/types'

export const SHIPPING_CENTS = 450
export const FREE_SHIPPING_FROM_CENTS = 4500

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

/** Cena jednog komada: veličina kafe/seta ili cena opreme. null = proizvod ili veličina ne postoji. */
export function unitPrice(slug: string, grams: number | null): number | null {
  const p = products.find((x) => x.slug === slug)
  if (!p) return null
  if (grams === null) return p.priceCents ?? null
  return p.sizes.find((s) => s.grams === grams)?.priceCents ?? null
}

function load(): CartLine[] {
  try {
    const raw = JSON.parse(localStorage.getItem(storageKeys.cart) ?? '[]') as unknown
    if (!Array.isArray(raw)) return []
    return raw.filter(
      (l): l is CartLine =>
        typeof l?.slug === 'string' && Number.isInteger(l?.qty) && l.qty > 0 && unitPrice(l.slug, l.grams ?? null) !== null,
    )
  } catch {
    return []
  }
}

let state: CartState = { lines: typeof window === 'undefined' ? [] : load(), open: false }
let summary = summarize(state)
const listeners = new Set<() => void>()

function summarize(s: CartState): CartSummary {
  const lines = s.lines.map((l) => {
    const unitCents = unitPrice(l.slug, l.grams) ?? 0
    return { ...l, key: lineKey(l), unitCents, lineCents: unitCents * l.qty }
  })
  const subtotalCents = lines.reduce((sum, l) => sum + l.lineCents, 0)
  const free = subtotalCents === 0 || subtotalCents >= FREE_SHIPPING_FROM_CENTS
  const shippingCents = free ? 0 : SHIPPING_CENTS
  return {
    lines,
    count: lines.reduce((n, l) => n + l.qty, 0),
    subtotalCents,
    shippingCents,
    toFreeShippingCents: free ? 0 : FREE_SHIPPING_FROM_CENTS - subtotalCents,
    totalCents: subtotalCents + shippingCents,
    open: s.open,
  }
}

function commit(next: CartState) {
  const linesChanged = next.lines !== state.lines
  state = next
  summary = summarize(state)
  if (linesChanged) {
    try {
      localStorage.setItem(storageKeys.cart, JSON.stringify(state.lines))
    } catch {
      /* storage nije dostupan */
    }
  }
  listeners.forEach((l) => l())
}

export function addToCart(slug: string, grams: number | null, grind: GrindId | null, qty = 1) {
  if (unitPrice(slug, grams) === null) return
  const key = lineKey({ slug, grams, grind })
  const found = state.lines.find((l) => lineKey(l) === key)
  const lines = found
    ? state.lines.map((l) => (l === found ? { ...l, qty: l.qty + qty } : l))
    : [...state.lines, { slug, grams, grind, qty }]
  commit({ ...state, lines })
  showToast('added')
}

export function setQty(key: string, qty: number) {
  const lines = qty <= 0
    ? state.lines.filter((l) => lineKey(l) !== key)
    : state.lines.map((l) => (lineKey(l) === key ? { ...l, qty } : l))
  commit({ ...state, lines })
}

export const removeLine = (key: string) => setQty(key, 0)
export const openCart = () => commit({ ...state, open: true })
export const closeCart = () => commit({ ...state, open: false })

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export const useCart = () => useSyncExternalStore(subscribe, () => summary, () => summary)

// --- toast (Toast.tsx ga prikazuje sa aria-live="polite") ---
export type ToastKind = 'added'
let toast: { kind: ToastKind; id: number } | null = null
let toastId = 0
const toastListeners = new Set<() => void>()

export function showToast(kind: ToastKind) {
  toast = { kind, id: ++toastId }
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
