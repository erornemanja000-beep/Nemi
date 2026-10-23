// Sekvence kadrova i zajednički sat (plan-izrade.md, Interfejs 4 i 5; storyboard.md 2 i 8).
// Uzor je freiraum-premium/src/assets/premium.js (Seq, Player, loadSeq), uz tri razlike:
//   1. Jedan sat ublažava vreme JEDNOM za sva platna koja ga dele (GRIND i POUR su na satu G), pa se
//      tokom šava G65–G96 platna ne razilaze. U preklopu oba crtaju isti kadar koji je spreman u obe.
//   2. Kadrovi stižu kao komprimovani Blob (fetch). Dekodirano je najviše ±24 kadra oko trenutnog
//      (ImageBitmap + close()), ostali čekaju kao Blob.
//   3. Jedan red učitavanja za sve sekvence: najviše 6 zahteva odjednom, prioriteti, bez duplikata.
// Platno je src/story/SeqCanvas.tsx. Stanje za proveru: window.__seqStats (dev ili ?debug).
import gsap from 'gsap'
import { useEffect, useState } from 'react'
import { media } from '../content/media'
import type { ChapterId } from '../content/types'
import { isPhone, REDUCED_QUERY, useIsPhone, useReducedMotion, useSaveData } from './useMedia'

// ---------- seq.json (Interfejs 4) ----------
export type SetName = 'l' | 'd' | 'm'
/** Nivo: `px` = pikseli za S; fajl k (od 1) prikazuje globalni kadar g_od + (k − 1) · every. */
export type SeqSet = { px: number; w: number; h: number; count: number; every: number }
export type SeqStep = { name: string; from: number; to: number }
/** Pun kadar i isečak u jedinicama S (stranica kvadrata kadra), od gornjeg levog ugla punog kadra. */
export type SeqGeometry = {
  full: { W: number; H: number }
  crop: { x0: number; y0: number; w: number; h: number }
}
export type SeqAnchors = {
  osa_x?: number
  otvor?: { x: number; y: number }
  ivica_v60?: { x: number; y: number; rx: number; ry: number }
  pult_y?: number
  sto_y?: number
  /** nivo kafe u bokalu po kadru, od kadra `from` (POUR, G177–G192) */
  kafa_y?: { from: number; values: number[] }
  [name: string]: unknown
}
export type SeqManifest = SeqGeometry & {
  id: ChapterId
  version: string
  /** false = pravi render */
  placeholder: boolean
  /** „G" (grind i pour) ili „S" (sip) */
  clock: string
  g_od: number
  g_do: number
  fps: number
  sets: { l?: SeqSet; d: SeqSet; m: SeqSet }
  /** relativne putanje po nivou, npr. d: „d/0001.webp" */
  poster: { l?: string; d: string; m: string }
  steps: SeqStep[]
  anchors: SeqAnchors
  /** osnovna putanja iz media.ts (ne iz seq.json), npr. „/media/seq/grind" */
  base: string
}

export type SeqStats = {
  set: SetName
  count: number
  /** poslatih zahteva (bez duplikata) */
  requested: number
  loaded: number
  failed: number
  /** dekodirano sada (ImageBitmap) */
  decoded: number
  /** najviše dekodiranih odjednom od početka */
  decodedMax: number
  inflight: number
  /** globalni kadrovi redom kojim su zahtevi poslati (prvih 400) */
  order: number[]
}

/** Zahtev za kadrove: lista globalnih kadrova, ili raspon (G) sa „svaki n-ti fajl nivoa" (step). */
export type FrameRequest = { frames: readonly number[] } | { from?: number; to?: number; step?: number }

export type Drawable = ImageBitmap | HTMLImageElement

const MAX_PARALLEL = 6
const MAX_DECODING = 2 // po sekvenci; createImageBitmap dekodira van glavne niti
/** dekodirano najviše ±24 globalna kadra oko trenutnog (na m, gde je every 2, to je 25 fajlova) */
export const RETAIN = 24
const URGENT = 1e6
/** Desktop: nivo l tek kad je S u CSS px × min(DPR, 2) veće od ovoga (storyboard 8). */
const L_THRESHOLD = 1250
/** ublažavanje sata po kadru od 60 Hz, kao Player u premium.js */
const EASE = 0.22
const FRAME_MS = 1000 / 60
const ORDER_LOG = 400

export const SEQ_DEBUG =
  import.meta.env.DEV || (typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('debug'))

const statsRegistry: Record<string, SeqStats> = {}

declare global {
  interface Window {
    __seqStats?: Record<string, SeqStats>
  }
}

if (SEQ_DEBUG && typeof window !== 'undefined') window.__seqStats = statsRegistry

const warn = (msg: string) => console.warn(`[seq] ${msg}`)
const pad = (n: number) => String(n).padStart(4, '0')

// ---------- manifest ----------
const num = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v)
const posNum = (v: unknown): v is number => num(v) && v > 0
const posInt = (v: unknown): v is number => posNum(v) && Number.isInteger(v)
const isObj = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v)

function parseSet(v: unknown): SeqSet | null {
  if (!isObj(v)) return null
  const { px, w, h, count, every } = v
  return posInt(px) && posInt(w) && posInt(h) && posInt(count) && posInt(every) ? { px, w, h, count, every } : null
}

/** Proverava obavezna polja iz Interfejsa 4. Vraća manifest ili opis greške. Polja units/generator se zanemaruju. */
function parseManifest(id: ChapterId, base: string, json: unknown): SeqManifest | string {
  if (!isObj(json)) return 'nije JSON objekat'
  if (json.id !== id) return `id je „${String(json.id)}"`
  const { g_od, g_do, full, crop, sets, poster, steps, anchors, clock } = json
  if (typeof clock !== 'string' || !clock) return 'clock'
  if (!posInt(g_od) || !posInt(g_do) || g_do < g_od) return 'g_od / g_do'
  if (!isObj(full)) return 'full'
  const { W, H } = full
  if (!posNum(W) || !posNum(H)) return 'full'
  if (!isObj(crop)) return 'crop'
  const { x0, y0, w, h } = crop
  if (!num(x0) || !num(y0) || !posNum(w) || !posNum(h)) return 'crop'
  if (!isObj(sets)) return 'sets'
  const d = parseSet(sets.d)
  const m = parseSet(sets.m)
  const l = sets.l === undefined ? undefined : parseSet(sets.l)
  if (!d || !m || l === null) return 'sets (d, m, opciono l)'
  for (const [name, s] of [['l', l], ['d', d], ['m', m]] as const) {
    if (s && g_od + (s.count - 1) * s.every > g_do) return `sets.${name}: count × every ide preko g_do`
  }
  if (!isObj(poster) || typeof poster.d !== 'string' || typeof poster.m !== 'string') return 'poster'
  const posterL = typeof poster.l === 'string' ? poster.l : undefined
  if (!Array.isArray(steps)) return 'steps'
  const parsedSteps: SeqStep[] = []
  for (const s of steps as unknown[]) {
    if (!isObj(s) || typeof s.name !== 'string' || !num(s.from) || !num(s.to)) return 'steps'
    parsedSteps.push({ name: s.name, from: s.from, to: s.to })
  }
  if (!isObj(anchors)) return 'anchors'
  return {
    id,
    base,
    version: typeof json.version === 'string' ? json.version : '',
    placeholder: json.placeholder !== false,
    clock,
    g_od,
    g_do,
    fps: posNum(json.fps) ? json.fps : 30,
    full: { W, H },
    crop: { x0, y0, w, h },
    sets: l ? { l, d, m } : { d, m },
    poster: posterL ? { l: posterL, d: poster.d, m: poster.m } : { d: poster.d, m: poster.m },
    steps: parsedSteps,
    anchors: anchors as SeqAnchors,
  }
}

const manifests = new Map<ChapterId, Promise<SeqManifest | null>>()

/**
 * Čita seq.json sekvence (putanja iz media.ts) i proverava obavezna polja. Kad ne uspe, vraća null
 * i piše console.warn (nikad console.error). Rezultat se pamti za celu sesiju.
 * Sekvenca sa `ready: false` u media.ts vraća null bez zahteva.
 */
export function loadManifest(id: ChapterId): Promise<SeqManifest | null> {
  const cached = manifests.get(id)
  if (cached) return cached
  const entry = media.seq[id]
  if (!entry?.ready) return Promise.resolve(null)
  const p = fetch(entry.manifest, { cache: 'no-cache' })
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return res.json() as Promise<unknown>
    })
    .then((json) => {
      const m = parseManifest(id, entry.base, json)
      if (typeof m === 'string') throw new Error(`neispravno polje: ${m}`)
      return m
    })
    .catch((err: unknown) => {
      warn(`${id}: seq.json nije učitan (${err instanceof Error ? err.message : String(err)}); ostaje poster`)
      return null
    })
  manifests.set(id, p)
  return p
}

export type PickOptions = {
  /** telefonski raspored; podrazumevano isPhone() */
  phone?: boolean
  /** S u CSS px; podrazumevano 100vh (desktop) */
  size?: number
  dpr?: number
}

/** Telefon: m. Desktop: l ako postoji i S × min(DPR, 2) > 1250, inače d. */
export function pickSet(manifest: SeqManifest, opts: PickOptions = {}): SetName {
  if (opts.phone ?? isPhone()) return 'm'
  const size = opts.size ?? window.innerHeight
  const dpr = Math.min(opts.dpr ?? (window.devicePixelRatio || 1), 2)
  return manifest.sets.l && size * dpr > L_THRESHOLD ? 'l' : 'd'
}

/** Pun URL postera za nivo (poster je isečak, iste veličine kao kadrovi tog nivoa). */
export function posterUrl(manifest: SeqManifest, set: SetName) {
  return `${manifest.base}/${manifest.poster[set] ?? manifest.poster.d}`
}

/** Nivo kafe u bokalu (S, od vrha punog kadra) za kadar g, sa linearnim prelazom između kadrova. */
export function kafaYAt(manifest: SeqManifest, g: number): number | null {
  const k = manifest.anchors.kafa_y
  if (!k || !num(k.from) || !Array.isArray(k.values) || !k.values.length) return null
  const x = Math.min(Math.max(g - k.from, 0), k.values.length - 1)
  const i = Math.floor(x)
  const a = k.values[i]
  const b = k.values[Math.min(i + 1, k.values.length - 1)]
  return a + (b - a) * (x - i)
}

// ---------- dekodiranje ----------
const imageUrls = new WeakMap<HTMLImageElement, string>()

/** Rezerva za pregledače bez createImageBitmap(Blob) (Safari < 15): <img> iz blob: URL-a (CSP img-src blob:). */
function viaImage(blob: Blob): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(blob)
    const img = new Image()
    img.decoding = 'async'
    img.onload = () => {
      img.onload = img.onerror = null
      imageUrls.set(img, url)
      img.decode().catch(() => undefined).then(() => resolve(img))
    }
    img.onerror = () => {
      img.onload = img.onerror = null
      URL.revokeObjectURL(url)
      reject(new Error('slika se ne dekodira'))
    }
    img.src = url
  })
}

function toDrawable(blob: Blob): Promise<Drawable> {
  if (typeof createImageBitmap !== 'function') return viaImage(blob)
  return createImageBitmap(blob).catch(() => viaImage(blob))
}

function closeDrawable(d: Drawable | undefined) {
  if (!d) return
  if (d instanceof HTMLImageElement) {
    const url = imageUrls.get(d)
    if (url) URL.revokeObjectURL(url)
    d.removeAttribute('src')
  } else {
    d.close()
  }
}

// ---------- sekvenca ----------
const NONE = 0
const QUEUED = 1
const LOADING = 2
const LOADED = 3
const FAILED = 4

type Job = { seq: Sequence; k: number; priority: number; base: number; order: number }
type Waiter = { left: Set<number>; resolve: () => void }

/**
 * Jedna sekvenca na jednom nivou. Svi kadrovi su globalni (sat G ili S); fajl k prikazuje
 * kadar first + k · every. Kadar koji vrati 404 se preskače: has/isReady su false, pa platno
 * i sat uzimaju najbliži učitani.
 */
export class Sequence {
  readonly id: ChapterId
  readonly manifest: SeqManifest
  readonly set: SetName
  readonly info: SeqSet
  /** prvi i poslednji globalni kadar koji ovaj nivo ima kao fajl */
  readonly first: number
  readonly last: number
  readonly stats: SeqStats
  disposed = false

  private readonly state: Uint8Array
  private readonly blobs: (Blob | undefined)[]
  private readonly bitmaps: (Drawable | undefined)[]
  private readonly jobs: (Job | undefined)[]
  private readonly decoded = new Set<number>()
  private readonly decoding = new Set<number>()
  private readonly listeners = new Set<() => void>()
  private readonly waiters: Waiter[] = []
  private readonly abort = new AbortController()
  private urgent: Job | null = null
  private lo = -1
  private hi = -1
  private center = -1

  // zajednički red za sve sekvence
  private static queue: Job[] = []
  private static inflight = 0
  private static order = 0

  constructor(manifest: SeqManifest, set: SetName) {
    const name: SetName = manifest.sets[set] ? set : 'd'
    const info = manifest.sets[name] ?? manifest.sets.d
    this.id = manifest.id
    this.manifest = manifest
    this.set = name
    this.info = info
    this.first = manifest.g_od
    this.last = manifest.g_od + (info.count - 1) * info.every
    this.state = new Uint8Array(info.count)
    this.blobs = new Array<Blob | undefined>(info.count)
    this.bitmaps = new Array<Drawable | undefined>(info.count)
    this.jobs = new Array<Job | undefined>(info.count)
    this.stats = { set: name, count: info.count, requested: 0, loaded: 0, failed: 0, decoded: 0, decodedMax: 0, inflight: 0, order: [] }
    statsRegistry[this.id] = this.stats
  }

  // --- kadrovi i fajlovi ---
  /** najbliži fajl (0…count−1) za globalni kadar g */
  index(g: number) {
    return Math.min(this.info.count - 1, Math.max(0, Math.round((g - this.first) / this.info.every)))
  }
  /** globalni kadar fajla k */
  frame(k: number) {
    return this.first + k * this.info.every
  }
  /** fajl koji tačno prikazuje kadar g, ili −1 */
  private exact(g: number) {
    const k = (g - this.first) / this.info.every
    return Number.isInteger(k) && k >= 0 && k < this.info.count ? k : -1
  }
  /** g stegnut na kadrove koje nivo ima */
  clampG(g: number) {
    return Math.min(this.last, Math.max(this.first, g))
  }
  /** sekvenca pokriva kadar g (g_od…g_do iz seq.json) */
  covers(g: number) {
    return g >= this.manifest.g_od && g <= this.manifest.g_do
  }
  private fileUrl(k: number) {
    return `${this.manifest.base}/${this.set}/${pad(k + 1)}.webp`
  }
  /** URL fajla za kadar g (najbliži fajl nivoa) */
  url(g: number) {
    return this.fileUrl(this.index(g))
  }
  /** nivo ima fajl za tačno ovaj kadar i on nije pao (404) */
  has(g: number) {
    const k = this.exact(g)
    return k >= 0 && this.state[k] !== FAILED
  }
  /** fajl za kadar g je stigao (Blob) */
  isLoaded(g: number) {
    const k = this.exact(g)
    return k >= 0 && this.state[k] === LOADED
  }
  /** kadar g je dekodiran i može odmah da se nacrta */
  isReady(g: number) {
    const k = this.exact(g)
    return k >= 0 && this.bitmaps[k] !== undefined
  }
  bitmap(g: number): Drawable | null {
    const k = this.exact(g)
    return k >= 0 ? (this.bitmaps[k] ?? null) : null
  }
  /** najbliži dekodiran kadar (globalni) za g, ili null */
  nearestReady(g: number): number | null {
    const k0 = this.index(g)
    let best = -1
    let bestD = Infinity
    for (const k of this.decoded) {
      const d = Math.abs(k - k0)
      if (d < bestD || (d === bestD && k < best)) {
        best = k
        bestD = d
      }
    }
    return best < 0 ? null : this.frame(best)
  }

  // --- učitavanje ---
  /**
   * Stavlja kadrove u zajednički red (veći prioritet ide pre; isti prioritet redom zahteva).
   * Kadar koji je već u redu dobija veći od dva prioriteta, a učitan ili na putu se preskače.
   * Vraća obećanje koje se ispuni kad svi traženi kadrovi stignu ili padnu.
   */
  request(req: FrameRequest = {}, priority = 0): Promise<void> {
    if (this.disposed) return Promise.resolve()
    const left = new Set<number>()
    for (const k of this.resolve(req)) {
      const s = this.state[k]
      if (s === LOADED || s === FAILED) continue
      left.add(k)
      Sequence.enqueue(this, k, priority)
    }
    Sequence.pump()
    if (!left.size) return Promise.resolve()
    return new Promise((resolve) => this.waiters.push({ left, resolve }))
  }

  private resolve(req: FrameRequest): number[] {
    const out: number[] = []
    if ('frames' in req) {
      for (const g of req.frames) {
        const k = this.index(g)
        if (!out.includes(k)) out.push(k)
      }
      return out
    }
    const { every, count } = this.info
    const k0 = Math.max(0, Math.ceil(((req.from ?? this.first) - this.first) / every))
    const k1 = Math.min(count - 1, Math.floor(((req.to ?? this.last) - this.first) / every))
    const step = Math.max(1, Math.round(req.step ?? 1))
    for (let k = k0; k <= k1; k += step) out.push(k)
    return out
  }

  private static enqueue(seq: Sequence, k: number, priority: number) {
    const s = seq.state[k]
    if (s !== NONE && s !== QUEUED) return
    const job = seq.jobs[k]
    if (job) {
      if (priority === URGENT) job.priority = URGENT
      else {
        job.base = Math.max(job.base, priority)
        if (job.priority !== URGENT) job.priority = job.base
      }
      return
    }
    const next: Job = { seq, k, priority, base: priority === URGENT ? -1 : priority, order: ++Sequence.order }
    seq.jobs[k] = next
    seq.state[k] = QUEUED
    Sequence.queue.push(next)
  }

  private static pump() {
    const q = Sequence.queue
    while (Sequence.inflight < MAX_PARALLEL && q.length) {
      let bi = 0
      for (let i = 1; i < q.length; i++) {
        const a = q[i]
        const b = q[bi]
        if (a.priority > b.priority || (a.priority === b.priority && a.order < b.order)) bi = i
      }
      const job = q[bi]
      q[bi] = q[q.length - 1]
      q.pop()
      const { seq, k } = job
      seq.jobs[k] = undefined
      if (seq.urgent === job) seq.urgent = null
      Sequence.inflight++
      void seq.fetchFile(k, job.priority === URGENT).finally(() => {
        Sequence.inflight--
        Sequence.pump()
      })
    }
  }

  private async fetchFile(k: number, urgent: boolean) {
    this.state[k] = LOADING
    this.stats.requested++
    this.stats.inflight++
    if (this.stats.order.length < ORDER_LOG) this.stats.order.push(this.frame(k))
    try {
      const res = await fetch(this.fileUrl(k), { signal: this.abort.signal, priority: urgent ? 'high' : 'low' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const blob = await res.blob()
      // SPA rezerva bi vratila index.html sa 200 umesto slike
      if (blob.type.startsWith('text/')) throw new Error(`tip ${blob.type}`)
      if (this.disposed) return
      this.blobs[k] = blob
      this.state[k] = LOADED
      this.stats.loaded++
      this.settle(k)
      if (k >= this.lo && k <= this.hi) this.pumpDecode()
    } catch (err) {
      if (this.disposed) return
      this.fail(k, err instanceof Error ? err.message : String(err))
    } finally {
      this.stats.inflight--
    }
  }

  private fail(k: number, why: string) {
    this.state[k] = FAILED
    this.stats.failed++
    warn(`${this.id}: ${this.set}/${pad(k + 1)}.webp (kadar ${this.frame(k)}) nije učitan (${why}); koristi se najbliži učitani kadar`)
    this.settle(k)
    this.notify()
  }

  private settle(k: number) {
    for (let i = this.waiters.length - 1; i >= 0; i--) {
      const w = this.waiters[i]
      if (w.left.delete(k) && !w.left.size) {
        this.waiters.splice(i, 1)
        w.resolve()
      }
    }
  }

  /** hitan zahtev za kadar na kome je sat, kad u blizini nema ničeg učitanog (jedan po sekvenci) */
  private want(k: number) {
    const prev = this.urgent
    if (prev && prev.k === k) return
    if (prev && this.jobs[prev.k] === prev) {
      if (prev.base < 0) {
        const q = Sequence.queue
        const i = q.indexOf(prev)
        if (i >= 0) q.splice(i, 1)
        this.jobs[prev.k] = undefined
        this.state[prev.k] = NONE
      } else {
        prev.priority = prev.base
      }
    }
    this.urgent = null
    Sequence.enqueue(this, k, URGENT)
    this.urgent = this.jobs[k] ?? null
    Sequence.pump()
  }

  private loadedNear(k: number, r: number) {
    for (let i = Math.max(0, k - r); i <= Math.min(this.info.count - 1, k + r); i++) {
      if (this.state[i] === LOADED || this.state[i] === LOADING) return true
    }
    return false
  }

  // --- dekodiranje oko trenutnog kadra ---
  /**
   * Drži dekodirane samo kadrove u [g − radius, g + radius] (globalni kadrovi), ostale zatvara
   * (ImageBitmap.close()) i ostavlja kao Blob. Bliži kadrovi se dekodiraju prvi.
   */
  retain(g: number, radius = RETAIN) {
    if (this.disposed) return
    const { every, count } = this.info
    const c = this.clampG(g)
    const center = this.index(c)
    const lo = Math.min(count - 1, Math.max(0, Math.ceil((c - radius - this.first) / every)))
    const hi = Math.min(count - 1, Math.max(0, Math.floor((c + radius - this.first) / every)))
    if (lo === this.lo && hi === this.hi && center === this.center) return
    this.lo = lo
    this.hi = hi
    this.center = center
    for (const k of this.decoded) if (k < lo || k > hi) this.closeAt(k)
    this.stats.decoded = this.decoded.size
    this.pumpDecode()
    if (this.state[center] <= QUEUED && !this.loadedNear(center, 2)) this.want(center)
  }

  /** zatvara sve dekodirane kadrove (platno je daleko od ekrana); Blob-ovi ostaju */
  release() {
    for (const k of this.decoded) this.closeAt(k)
    this.stats.decoded = 0
    this.lo = this.hi = this.center = -1
  }

  private closeAt(k: number) {
    closeDrawable(this.bitmaps[k])
    this.bitmaps[k] = undefined
    this.decoded.delete(k)
  }

  private pumpDecode() {
    if (this.disposed || this.lo < 0) return
    while (this.decoding.size < MAX_DECODING) {
      let best = -1
      let bestD = Infinity
      for (let k = this.lo; k <= this.hi; k++) {
        if (this.state[k] !== LOADED || this.bitmaps[k] || this.decoding.has(k)) continue
        const d = Math.abs(k - this.center)
        if (d < bestD) {
          best = k
          bestD = d
        }
      }
      if (best < 0) return
      this.decode(best)
    }
  }

  private decode(k: number) {
    const blob = this.blobs[k]
    if (!blob) return
    this.decoding.add(k)
    toDrawable(blob).then(
      (img) => {
        this.decoding.delete(k)
        if (this.disposed || k < this.lo || k > this.hi) {
          closeDrawable(img)
        } else {
          this.bitmaps[k] = img
          this.decoded.add(k)
          this.stats.decoded = this.decoded.size
          this.stats.decodedMax = Math.max(this.stats.decodedMax, this.decoded.size)
          this.notify()
        }
        this.pumpDecode()
      },
      (err: unknown) => {
        this.decoding.delete(k)
        if (this.disposed) return
        this.blobs[k] = undefined
        this.fail(k, `dekodiranje: ${err instanceof Error ? err.message : String(err)}`)
        this.pumpDecode()
      },
    )
  }

  // --- događaji i kraj ---
  /** poziva se kad se dekodira novi kadar ili kadar padne */
  onChange(fn: () => void) {
    this.listeners.add(fn)
    return () => {
      this.listeners.delete(fn)
    }
  }

  private notify() {
    for (const fn of this.listeners) fn()
  }

  dispose() {
    if (this.disposed) return
    this.disposed = true
    this.abort.abort()
    const q = Sequence.queue
    for (let i = q.length - 1; i >= 0; i--) if (q[i].seq === this) q.splice(i, 1)
    this.release()
    this.blobs.fill(undefined)
    for (const w of this.waiters) w.resolve()
    this.waiters.length = 0
    this.listeners.clear()
    if (statsRegistry[this.id] === this.stats) delete statsRegistry[this.id]
    Sequence.pump()
  }
}

/** Sekvenca na nivou `set` (pickSet). Ništa se ne učitava dok se ne pozove request() ili retain(). */
export function createSequence(manifest: SeqManifest, set: SetName) {
  return new Sequence(manifest, set)
}

// ---------- zajednički sat ----------
export type Clock = {
  /** cilj: globalni kadar (sme da bude razlomak) */
  readonly target: number
  /** ublažena vrednost koju platna crtaju */
  readonly current: number
  readonly running: boolean
  set(g: number): void
  /** odmah na kadar, bez ublažavanja */
  jump(g: number): void
  add(seq: Sequence): void
  remove(seq: Sequence): void
  /**
   * Platno je u ekranu: sat svaki tik drži dekodirane kadrove oko trenutnog (retain) i zove draw.
   * Vraća odjavu (platno van ekrana).
   */
  attach(seq: Sequence, draw: () => void): () => void
  /**
   * Kadar koji platno sekvence treba da crta, ili null (ostaje ono što je nacrtano). Kad sekvencu
   * u istom trenutku pokriva još jedno vidljivo platno (preklop G65–G96), to je najbliži kadar koji
   * je dekodiran u OBE, pa šav ostaje bez skoka.
   */
  frameFor(seq: Sequence): number | null
  subscribe(fn: (clock: Clock) => void): () => void
  start(): void
  stop(): void
}

export type ClockOptions = {
  /** ublažavanje po kadru od 60 Hz (0,22 kao premium.js); 1 = bez ublažavanja */
  ease?: number
  /** ±kadrova oko trenutnog koji ostaju dekodirani */
  retain?: number
  initial?: number
}

/**
 * Jedan sat za platna koja dele vreme (G: grind i pour; S: sip). Ublažava cilj jednom, preko
 * gsap.ticker-a, i radi samo dok je pokrenut i dok ima vidljivo platno ili pretplatnika.
 * U reduced motion cilj se preuzima odmah.
 */
export function createClock(sequences: readonly Sequence[] = [], options: ClockOptions = {}): Clock {
  const ease = options.ease ?? EASE
  const radius = options.retain ?? RETAIN
  let target = options.initial ?? sequences[0]?.first ?? 1
  let current = target
  let running = true
  let ticking = false
  let dirty = true
  const members = new Set<Sequence>()
  const visible = new Map<Sequence, { draw: () => void; off: () => void }>()
  const subs = new Set<(clock: Clock) => void>()
  let cache: Map<Sequence, number | null> | null = null
  const reduced = typeof window !== 'undefined' ? window.matchMedia(REDUCED_QUERY) : null
  const touch = () => {
    dirty = true
  }

  function compute(seq: Sequence): number | null {
    if (seq.disposed) return null
    const t = seq.clampG(Math.round(current))
    const group = [seq]
    let lo = seq.first
    let hi = seq.last
    for (const s of visible.keys()) {
      if (s === seq || s.disposed || !s.covers(t)) continue
      group.push(s)
      lo = Math.max(lo, s.first)
      hi = Math.min(hi, s.last)
    }
    if (group.length === 1) return seq.nearestReady(t)
    const ready = (g: number) => g >= lo && g <= hi && group.every((s) => s.isReady(g))
    for (let d = 0; t - d >= lo || t + d <= hi; d++) {
      if (ready(t - d)) return t - d
      if (d && ready(t + d)) return t + d
    }
    return null
  }

  function tick(_time: number, dt: number) {
    const before = current
    if (reduced?.matches || ease >= 1) current = target
    else {
      const a = 1 - Math.pow(1 - ease, Math.min(Math.max(dt, 0), 100) / FRAME_MS)
      current += (target - current) * a
      if (Math.abs(target - current) < 0.02) current = target
    }
    if (current === before && !dirty) return
    dirty = false
    const t = Math.round(current)
    for (const seq of visible.keys()) seq.retain(t, radius)
    cache = new Map()
    try {
      for (const v of visible.values()) v.draw()
      for (const fn of subs) fn(api)
    } finally {
      cache = null
    }
  }

  function sync() {
    const want = running && (visible.size > 0 || subs.size > 0)
    if (want && !ticking) {
      // posle pauze (ništa nije bilo u ekranu) sat ne pušta „sustizanje", nego staje na cilj
      current = target
      dirty = true
      gsap.ticker.add(tick)
      ticking = true
    } else if (!want && ticking) {
      gsap.ticker.remove(tick)
      ticking = false
    }
  }

  function add(seq: Sequence) {
    if (members.has(seq)) return
    const other = members.values().next().value
    if (SEQ_DEBUG && other && other.manifest.clock !== seq.manifest.clock) {
      warn(`${seq.id} (sat ${seq.manifest.clock}) na satu ${other.manifest.clock}`)
    }
    members.add(seq)
  }

  function detach(seq: Sequence) {
    const v = visible.get(seq)
    if (!v) return
    v.off()
    visible.delete(seq)
    dirty = true
    sync()
  }

  const api: Clock = {
    get target() {
      return target
    },
    get current() {
      return current
    },
    get running() {
      return running
    },
    set(g) {
      if (Number.isFinite(g)) target = g
    },
    jump(g) {
      if (!Number.isFinite(g)) return
      target = current = g
      dirty = true
    },
    add,
    remove(seq) {
      detach(seq)
      members.delete(seq)
    },
    attach(seq, draw) {
      add(seq)
      visible.get(seq)?.off()
      visible.set(seq, { draw, off: seq.onChange(touch) })
      dirty = true
      sync()
      return () => {
        if (visible.get(seq)?.draw === draw) detach(seq)
      }
    },
    frameFor(seq) {
      if (!cache) return compute(seq)
      const hit = cache.get(seq)
      if (hit !== undefined) return hit
      const g = compute(seq)
      cache.set(seq, g)
      return g
    },
    subscribe(fn) {
      subs.add(fn)
      sync()
      return () => {
        subs.delete(fn)
        sync()
      }
    },
    start() {
      running = true
      sync()
    },
    stop() {
      running = false
      sync()
    },
  }
  for (const s of sequences) add(s)
  return api
}

// ---------- React ----------
/**
 * Sekvenca za poglavlje: učita seq.json, izabere nivo (pickSet; na desktopu ponovo posle promene
 * veličine) i napravi Sequence. Sa reduced motion, Save-Data ili `ready: false` vraća null i ne šalje
 * nijedan zahtev (ni seq.json), pa SeqCanvas prikazuje samo poster. Sekvenca se gasi (dispose) pri
 * promeni nivoa i pri unmount-u.
 */
export function useSequence(id: ChapterId, enabled = true): Sequence | null {
  const reduced = useReducedMotion()
  const saveData = useSaveData()
  const phone = useIsPhone()
  const on = enabled && !reduced && !saveData && media.seq[id].ready
  const [manifest, setManifest] = useState<SeqManifest | null>(null)
  const [setName, setSetName] = useState<SetName | null>(null)
  const [seq, setSeq] = useState<Sequence | null>(null)

  useEffect(() => {
    if (!on) return
    let live = true
    void loadManifest(id).then((m) => {
      if (live) setManifest(m)
    })
    return () => {
      live = false
    }
  }, [id, on])

  useEffect(() => {
    if (!on || !manifest) return
    const update = () => setSetName(pickSet(manifest, { phone }))
    update()
    if (phone) return
    let timer = 0
    const onResize = () => {
      window.clearTimeout(timer)
      timer = window.setTimeout(update, 250)
    }
    window.addEventListener('resize', onResize)
    return () => {
      window.clearTimeout(timer)
      window.removeEventListener('resize', onResize)
    }
  }, [on, manifest, phone])

  useEffect(() => {
    if (!on || !manifest || !setName) return
    const s = createSequence(manifest, setName)
    // oxlint-disable-next-line react/set-state-in-effect -- spoljni resurs (fetch, ImageBitmap) nastaje u efektu, da bi ga cleanup ugasio i u StrictMode-u
    setSeq(s)
    return () => {
      s.dispose()
      setSeq((cur) => (cur === s ? null : cur))
    }
  }, [on, manifest, setName])

  return on && seq && !seq.disposed ? seq : null
}
