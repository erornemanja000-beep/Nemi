// Talas tečne kafe POUR → SIP (Z6). Storyboard 5, plan Interfejs 6.
//
// Ugovor sa Story (Z12):
// - <Wave ref pourClip sipLens variant /> je sloj preko POUR i SIP scene (position: absolute, inset 0).
// - ref.set(p, startY): p 0–1 je napredak talasa, startY je linija kafe u bokalu (kafa_y) u px viewporta.
// - Wave menja SAMO: clip-path na pourClip (.layer-pour__clip), transform i will-change na sipLens
//   (.layer-sip__lens) i svoj SVG. Ništa ne čita iz layout-a u petlji: dimenzije i položaji se mere pri
//   promeni veličine (ResizeObserver), pri ulasku u talas i na ref.measure().
// - Pozadina POUR-a mora biti UNUTAR pourClip (inače isečen deo ne otkriva SIP), a pozadina SIP-a
//   unutar sipLens ili ispod njega.
// - Ako se POUR ili SIP sloj pomera tokom talasa (npr. POUR „ide gore sporije od talasa" na 70–100 %,
//   ili telefon bez pina), Story šalje trenutne gornje ivice: ref.set(p, startY, { pourTop, lensTop }).
//   Bez toga važe izmerene vrednosti, što je tačno za sticky scenu.
//
// Šta se vidi (sve u px Wave sloja, H = visina, W = širina):
// - p = 0: ravna linija tačno na startY (amplituda 0), pa se tanka tamna linija pojavi do p ≈ 0,03.
// - 0–0,12: gornja ivica se diže, a tečnost se razliva nadole do dna ekrana; ispod nje je još POUR.
// - 0,12–0,3: donja ivica ulazi odozdo, ispod nje je čist SIP. Iznad gornje ivice je POUR.
// - 0,3–0,7: traka debljine 18–35 % visine prolazi sredinom; kroz nju se vidi živ SIP (scale 1,04, ton).
// - 0,7–1: traka izlazi gore, ostaje SIP. Na p = 1 POUR je isečen iznad ekrana (ostaje tako).
import { useEffect, useImperativeHandle, useRef, useState, type Ref, type RefObject } from 'react'
import './wave.css'

export type WaveVariant = 'desktop' | 'phone'

/** Gornje (i leve) ivice layout kutija u px viewporta u ovom trenutku. Sve je opciono. */
export type WaveLayout = {
  waveTop?: number
  pourTop?: number
  lensTop?: number
}

/** Poslednja izračunata ivica, u px Wave sloja (za proveru u dev harness-u i Playwright-u). */
export type WaveState = {
  p: number
  startY: number
  width: number
  height: number
  /** gornja ivica Wave sloja u viewportu pri poslednjem merenju */
  waveTop: number
  phase: 'before' | 'flood' | 'band' | 'after'
  xs: number[]
  top: number[]
  bottom: number[]
}

export type WaveHandle = {
  set(progress: number, startY: number, layout?: WaveLayout): void
  /** Ponovo izmeri (npr. posle ScrollTrigger.refresh ili promene rasporeda). */
  measure(): void
  inspect(): WaveState
}

type WaveProps = {
  pourClip: RefObject<HTMLElement | null>
  sipLens: RefObject<HTMLElement | null>
  variant: WaveVariant
  className?: string
  ref?: Ref<WaveHandle>
}

// ---------- Geometrija (storyboard 5) ----------
const TAU = Math.PI * 2
/** Amplitude ivice u jedinicama U = min(H, 0,9·W): na desktopu je to 4 % i 1,5 % vh. */
const A1 = 0.04
const A2 = 0.015
/** Talasne dužine u širinama ekrana (1,2 i 0,45 vw). */
const L1 = 1.2
const L2 = 0.45
/** Do ovog p tečnost se razliva nadole; POUR je i ispod nje. */
const P_FLOOD = 0.12

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)
const smooth = (a: number, b: number, v: number) => {
  const t = clamp01((v - a) / (b - a))
  return t * t * (3 - 2 * t)
}
const frac = (v: number) => v - Math.floor(v)

/** Monotona kubna interpolacija (PCHIP): glatka brzina bez prebačaja između ključeva. */
function pchip(xs: readonly number[], ys: readonly number[], x: number): number {
  const n = xs.length
  if (x <= xs[0]) return ys[0]
  if (x >= xs[n - 1]) return ys[n - 1]
  let i = 0
  while (x > xs[i + 1]) i++
  const d = (k: number) => (ys[k + 1] - ys[k]) / (xs[k + 1] - xs[k])
  const slope = (k: number) => {
    if (k === 0) return d(0)
    if (k === n - 1) return d(n - 2)
    const a = d(k - 1)
    const b = d(k)
    if (a * b <= 0) return 0
    const h0 = xs[k] - xs[k - 1]
    const h1 = xs[k + 1] - xs[k]
    const w1 = 2 * h1 + h0
    const w2 = h1 + 2 * h0
    return (w1 + w2) / (w1 / a + w2 / b)
  }
  const h = xs[i + 1] - xs[i]
  const t = (x - xs[i]) / h
  const t2 = t * t
  const t3 = t2 * t
  return (
    (2 * t3 - 3 * t2 + 1) * ys[i] +
    (t3 - 2 * t2 + t) * h * slope(i) +
    (-2 * t3 + 3 * t2) * ys[i + 1] +
    (t3 - t2) * h * slope(i + 1)
  )
}

const TOP_P = [0, 0.15, 0.3, 0.5, 0.7, 0.85, 1] as const
const BOTTOM_P = [P_FLOOD, 0.2, 0.3, 0.5, 0.7, 0.85, 1] as const

/** Osnovne linije ivica u jedinicama H. `s` je startY / H. */
function baselines(p: number, s: number, margin: number) {
  // gornja ivica: od linije kafe do sredine ekrana, pa napolje iznad vrha (uvek naniže → monotono)
  const top = [s, s + (0.47 - s) * 0.42, 0.47, 0.29, 0.07, -0.15, -0.43]
  for (let i = 1; i < top.length; i++) top[i] = Math.min(top[i], top[i - 1] - 0.03)
  const yT = pchip(TOP_P, top, p)
  if (p < P_FLOOD) {
    // tečnost se razliva nadole, do ispod dna ekrana
    const t = p / P_FLOOD
    const ease = 0.5 - 0.5 * Math.cos(Math.PI * t)
    return { yT, yB: s + (1 + margin - s) * ease, flood: true }
  }
  // donja ivica: ulazi odozdo, debljina trake 18 % (p 0,3) → 35 % (p 0,5) → izlazi gore
  const bottom = [1 + margin + 0.02, 0.9, 0.65, 0.63, 0.35, 0.05, -0.2]
  const yB = Math.max(pchip(BOTTOM_P, bottom, p), yT + 0.12)
  return { yT, yB, flood: false }
}

type EdgeWave = { ph1: number; ph2: number; tilt: number; amp: number }

function edgeWaves(p: number) {
  const env = smooth(0, 0.12, p)
  const top: EdgeWave = {
    ph1: 0.9 + TAU * 0.55 * p,
    ph2: 2.3 - TAU * 1.3 * p,
    tilt: 0.08 * Math.sin(Math.PI * p),
    amp: env,
  }
  const bottom: EdgeWave = {
    ph1: 3.4 + TAU * 0.7 * p,
    ph2: 0.4 - TAU * 1.05 * p,
    tilt: -0.025 * Math.sin(Math.PI * p),
    amp: env * 0.85,
  }
  return { top, bottom }
}

/** Ivica = osnovna linija + zbir dve sinusoide (faza klizi sa p) + blag nagib. */
function edgeY(x: number, base: number, w: EdgeWave, W: number, U: number) {
  return (
    base +
    w.amp * U * (A1 * Math.sin((TAU * x) / (L1 * W) + w.ph1) + A2 * Math.sin((TAU * x) / (L2 * W) + w.ph2)) +
    w.amp * w.tilt * U * (x / W - 0.5)
  )
}

// odsjaji koji klize duž gornje ivice: početak (u širinama), brzina (širina po celom talasu), dužina (px)
const GLINTS = [
  { u: 0.08, v: 0.55, rx: 22 },
  { u: 0.36, v: -0.42, rx: 14 },
  { u: 0.57, v: 0.7, rx: 28 },
  { u: 0.74, v: -0.6, rx: 17 },
  { u: 0.93, v: 0.46, rx: 11 },
]

const f1 = (v: number) => (Math.round(v * 10) / 10).toString()

// ---------- Motor talasa (van React-a, bez čitanja layout-a u set) ----------
type Els = {
  /** meri se ovaj koren (oba korena imaju isti položaj i veličinu) */
  root: HTMLDivElement
  roots: HTMLDivElement[]
  svgs: SVGSVGElement[]
  fills: SVGPathElement[]
  lines: SVGGElement
  topPaths: SVGPathElement[]
  bottomPaths: SVGPathElement[]
  glints: SVGEllipseElement[]
}

function createEngine(els: Els, variant: WaveVariant, pourRef: WaveProps['pourClip'], lensRef: WaveProps['sipLens']) {
  const segments = variant === 'phone' ? 24 : 44
  const glints = GLINTS.slice(0, els.glints.length)
  const geo = {
    W: 0,
    H: 0,
    top: 0,
    left: 0,
    pourTop: 0,
    pourLeft: 0,
    lensTop: 0,
    lensLeft: 0,
    lensW: 0,
    lensH: 0,
    pourW: 0,
    pourH: 0,
    lensScale: 1.04,
  }
  let measured = false
  let dirty = true
  let active = false
  let mode: WaveState['phase'] | '' = ''
  let lastP = -1
  let lastS = NaN
  let lastLayout: WaveLayout | undefined
  let lastLineAlpha = -1
  const state: WaveState = { p: 0, startY: 0, width: 0, height: 0, waveTop: 0, phase: 'before', xs: [], top: [], bottom: [] }

  const num = (style: CSSStyleDeclaration, name: string, fallback: number) => {
    const v = parseFloat(style.getPropertyValue(name))
    return Number.isFinite(v) ? v : fallback
  }

  function measure() {
    const r = els.root.getBoundingClientRect()
    geo.W = r.width
    geo.H = r.height
    geo.top = r.top
    geo.left = r.left
    const pour = pourRef.current
    if (pour) {
      const pr = pour.getBoundingClientRect()
      geo.pourTop = pr.top
      geo.pourLeft = pr.left
      geo.pourW = pr.width
      geo.pourH = pr.height
    }
    const lens = lensRef.current
    if (lens) {
      // sopstveni scale ne sme da uđe u meru
      const prev = lens.style.transform
      if (prev) lens.style.transform = ''
      const lr = lens.getBoundingClientRect()
      if (prev) lens.style.transform = prev
      geo.lensTop = lr.top
      geo.lensLeft = lr.left
      geo.lensW = lr.width
      geo.lensH = lr.height
    }
    const cs = getComputedStyle(els.root)
    geo.lensScale = num(cs, '--wave-lens-scale', 1.04)
    if (geo.W > 0 && geo.H > 0) for (const svg of els.svgs) svg.setAttribute('viewBox', `0 0 ${f1(geo.W)} ${f1(geo.H)}`)
    measured = geo.W > 0 && geo.H > 0
    dirty = false
  }

  function resetTargets() {
    const pour = pourRef.current
    const lens = lensRef.current
    if (pour) pour.style.removeProperty('clip-path')
    if (lens) {
      lens.style.removeProperty('transform')
      lens.style.removeProperty('will-change')
    }
  }

  function setMode(next: WaveState['phase']) {
    if (next === mode) return
    const on = next === 'flood' || next === 'band'
    for (const r of els.roots) r.style.visibility = on ? 'visible' : 'hidden'
    const lens = lensRef.current
    if (!on) {
      if (lens) {
        lens.style.removeProperty('transform')
        lens.style.removeProperty('will-change')
      }
      if (next === 'before') pourRef.current?.style.removeProperty('clip-path')
    } else if (lens && !active) {
      lens.style.willChange = 'transform'
    }
    active = on
    mode = next
  }

  function render(p: number, startY: number, layout?: WaveLayout) {
    const { W, H } = geo
    const U = Math.min(H, 0.9 * W)
    const waveTop = layout?.waveTop ?? geo.top
    const sLocal = startY - waveTop
    const s = H > 0 ? sLocal / H : 0
    const margin = ((A1 + A2) * U * 1.6) / Math.max(H, 1) + 0.03
    const base = baselines(p, s, margin)
    const waves = edgeWaves(p)
    const yT = base.yT * H
    const yB = base.yB * H

    // tačke ivica (jedan segment van ekrana sa obe strane, da se krajevi linija ne vide)
    const step = W / segments
    const n = segments + 3
    const xs = new Array<number>(n)
    const top = new Array<number>(n)
    const bottom = new Array<number>(n)
    for (let i = 0; i < n; i++) {
      const x = (i - 1) * step
      xs[i] = x
      const t = edgeY(x, yT, waves.top, W, U)
      top[i] = t
      bottom[i] = Math.max(edgeY(x, yB, waves.bottom, W, U), t)
    }
    state.p = p
    state.startY = startY
    state.width = W
    state.height = H
    state.waveTop = waveTop
    state.xs = xs
    state.top = top
    state.bottom = bottom

    const phase: WaveState['phase'] = p <= 0 ? 'before' : p >= 1 ? 'after' : base.flood ? 'flood' : 'band'
    state.phase = phase
    setMode(phase)
    if (phase === 'before') return

    // ---- POUR: vidljiv iznad gornje ivice (i ispod tečnosti dok se razliva) ----
    // Poligon je u koordinatama pourClip i ograničen na njegovu kutiju (±1 px): manja maska je jeftinija,
    // a sve van kutije je tokom talasa ionako isečeno.
    const pour = pourRef.current
    if (pour) {
      const dy = waveTop - (layout?.pourTop ?? geo.pourTop)
      const dx = geo.left - geo.pourLeft
      const L = -1
      const R = f1(geo.pourW + 1)
      const B = f1(geo.pourH + 1)
      const pts: string[] = [`${L}px ${L}px`, `${R}px ${L}px`, `${R}px ${f1(top[n - 1] + dy)}px`]
      for (let i = n - 1; i >= 0; i--) pts.push(`${f1(xs[i] + dx)}px ${f1(top[i] + dy)}px`)
      pts.push(`${L}px ${f1(top[0] + dy)}px`)
      if (phase === 'flood') {
        // „prorez" levo od kutije nema površinu, pa su gornji i donji deo jedan poligon
        pts.push(`${L}px ${f1(bottom[0] + dy)}px`)
        for (let i = 0; i < n; i++) pts.push(`${f1(xs[i] + dx)}px ${f1(bottom[i] + dy)}px`)
        pts.push(`${R}px ${f1(bottom[n - 1] + dy)}px`, `${R}px ${B}px`, `${L}px ${B}px`)
      }
      pour.style.setProperty('clip-path', `polygon(${pts.join(',')})`)
    }
    if (phase === 'after') return

    // ---- SVG traka ----
    let dTop = ''
    let dBottom = ''
    let dBack = ''
    for (let i = 0; i < n; i++) {
      const cmd = i === 0 ? 'M' : 'L'
      dTop += `${cmd}${f1(xs[i])} ${f1(top[i])}`
      dBottom += `${cmd}${f1(xs[i])} ${f1(bottom[i])}`
    }
    for (let i = n - 1; i >= 0; i--) dBack += `L${f1(xs[i])} ${f1(bottom[i])}`
    const dFill = `${dTop}${dBack}Z`
    for (const el of els.fills) el.setAttribute('d', dFill)
    for (const el of els.topPaths) el.setAttribute('d', dTop)
    for (const el of els.bottomPaths) el.setAttribute('d', dBottom)

    // linija se pojavi (p 0 → 0,03), da ne stoji preko POUR-a dok talas još nije počeo
    const lineAlpha = Math.round(smooth(0, 0.03, p) * 100) / 100
    if (lineAlpha !== lastLineAlpha) {
      els.lines.setAttribute('opacity', String(lineAlpha))
      lastLineAlpha = lineAlpha
    }

    // odsjaji klize duž gornje ivice, 3 px ispod meniskusa
    const pad = 40
    glints.forEach((g, i) => {
      const t = frac(g.u + g.v * p)
      const x = t * (W + 2 * pad) - pad
      const y = edgeY(x, yT, waves.top, W, U) + 3
      const slope = (edgeY(x + 2, yT, waves.top, W, U) - edgeY(x - 2, yT, waves.top, W, U)) / 4
      const deg = (Math.atan(slope) * 180) / Math.PI
      const el = els.glints[i]
      el.setAttribute('transform', `translate(${f1(x)} ${f1(y)}) rotate(${f1(deg)})`)
      el.setAttribute('opacity', (lineAlpha * 0.85 * Math.pow(Math.sin(Math.PI * t), 0.6)).toFixed(2))
    })

    // ---- SIP sočivo: scale oko sredine trake. Ton daje ispuna trake: filter na sočivu je izmeren kao
    // najskuplji deo talasa (ceo SIP sloj se ponovo filtrira u svakom kadru), pa ga nema. ----
    const lens = lensRef.current
    if (lens && geo.lensW > 0) {
      const L = smooth(0, 0.15, p) * (1 - smooth(0.62, 1, p))
      const k = 1 + (geo.lensScale - 1) * L
      const center = Math.min(Math.max((yT + Math.min(yB, H)) / 2, 0), H)
      const lensTop = layout?.lensTop ?? geo.lensTop
      const cx = W / 2 + geo.left - geo.lensLeft
      const cy = center + waveTop - lensTop
      const tx = (1 - k) * (cx - geo.lensW / 2)
      const ty = (1 - k) * (cy - geo.lensH / 2)
      lens.style.transform = `translate3d(${tx.toFixed(2)}px, ${ty.toFixed(2)}px, 0) scale(${k.toFixed(4)})`
    }
  }

  return {
    set(progress: number, startY: number, layout?: WaveLayout) {
      const p = clamp01(Number.isFinite(progress) ? progress : 0)
      const sameLayout =
        lastLayout?.pourTop === layout?.pourTop && lastLayout?.lensTop === layout?.lensTop && lastLayout?.waveTop === layout?.waveTop
      if (p === lastP && startY === lastS && sameLayout && !dirty) return
      const entering = p > 0 && p < 1 && !active
      if (dirty || entering || !measured) measure()
      lastP = p
      lastS = startY
      lastLayout = layout
      if (!measured) return
      render(p, startY, layout)
    },
    measure() {
      measure()
      if (lastP >= 0 && measured) render(lastP, lastS, lastLayout)
    },
    /** Posle ResizeObserver-a: layout je već izračunat, pa je merenje jeftino. */
    resized() {
      dirty = true
      if (lastP >= 0) {
        measure()
        if (measured) render(lastP, lastS, lastLayout)
      }
    },
    inspect(): WaveState {
      return { ...state, xs: [...state.xs], top: [...state.top], bottom: [...state.bottom] }
    },
    dispose() {
      resetTargets()
      for (const r of els.roots) r.style.visibility = ''
    },
  }
}

type Engine = ReturnType<typeof createEngine>

let uid = 0
const EMPTY: WaveState = { p: 0, startY: 0, width: 0, height: 0, waveTop: 0, phase: 'before', xs: [], top: [], bottom: [] }

export function Wave({ pourClip, sipLens, variant, className = '', ref }: WaveProps) {
  const rootRef = useRef<HTMLDivElement>(null)
  const tintRef = useRef<HTMLDivElement>(null)
  const engine = useRef<Engine | null>(null)
  const pending = useRef<Parameters<WaveHandle['set']> | null>(null)
  const [id] = useState(() => `wave-${++uid}`)
  const glintCount = variant === 'phone' ? 3 : 5

  useImperativeHandle(
    ref,
    () => ({
      set: (p, startY, layout) => {
        if (engine.current) engine.current.set(p, startY, layout)
        else pending.current = [p, startY, layout]
      },
      measure: () => engine.current?.measure(),
      inspect: () => engine.current?.inspect() ?? EMPTY,
    }),
    [],
  )

  useEffect(() => {
    const root = rootRef.current
    const tint = tintRef.current
    if (!root || !tint) return
    const q = <T extends Element>(sel: string) => [...tint.querySelectorAll<T>(sel), ...root.querySelectorAll<T>(sel)]
    const e = createEngine(
      {
        root,
        roots: [tint, root],
        svgs: q<SVGSVGElement>('[data-w="svg"]'),
        fills: q<SVGPathElement>('[data-w="fill"]'),
        lines: q<SVGGElement>('[data-w="lines"]')[0],
        topPaths: q<SVGPathElement>('[data-w="top"]'),
        bottomPaths: q<SVGPathElement>('[data-w="bottom"]'),
        glints: q<SVGEllipseElement>('[data-w="glint"]'),
      },
      variant,
      pourClip,
      sipLens,
    )
    engine.current = e
    if (pending.current) {
      e.set(...pending.current)
      pending.current = null
    }
    const ro = new ResizeObserver(() => e.resized())
    ro.observe(root)
    if (pourClip.current) ro.observe(pourClip.current)
    if (sipLens.current) ro.observe(sipLens.current)
    return () => {
      ro.disconnect()
      e.dispose()
      if (engine.current === e) engine.current = null
    }
  }, [variant, pourClip, sipLens])

  return (
    <>
      {/* telo tečnosti (gradijent); mešanje je na korenu, da radi i kad Story da z-index */}
      <div ref={tintRef} className={`wave wave--tint ${className}`} data-variant={variant} aria-hidden="true">
        <svg className="wave__svg" data-w="svg" preserveAspectRatio="none" focusable="false">
          <defs>
            <linearGradient id={`${id}-fill`} x1="0" y1="0" x2="0" y2="1">
              <stop className="wave__stop--top" offset="0" />
              <stop className="wave__stop--mid" offset="0.45" />
              <stop className="wave__stop--bottom" offset="1" />
            </linearGradient>
          </defs>
          <path data-w="fill" fill={`url(#${id}-fill)`} />
        </svg>
      </div>
      {/* ivice, sjaj površine i odsjaji */}
      <div ref={rootRef} className={`wave wave--lines ${className}`} data-variant={variant} aria-hidden="true">
        <svg className="wave__svg" data-w="svg" preserveAspectRatio="none" focusable="false">
          <g data-w="lines" opacity="0">
            <path data-w="top" className="wave__line wave__sheen" transform="translate(0 16)" />
            <path data-w="bottom" className="wave__line wave__glow" transform="translate(0 -7)" />
            <path data-w="bottom" className="wave__line wave__under" />
            <path data-w="top" className="wave__line wave__shine-soft" transform="translate(0 3)" />
            <path data-w="top" className="wave__line wave__shine" transform="translate(0 3)" />
            <path data-w="top" className="wave__line wave__meniscus" />
          </g>
          <g>
            {GLINTS.slice(0, glintCount).map((g, i) => (
              <ellipse key={i} data-w="glint" className="wave__glint" rx={g.rx} ry="1.3" opacity="0" />
            ))}
          </g>
        </svg>
      </div>
    </>
  )
}

// ---------- Statična ivica (reduced motion) ----------
// Rez između POUR i SIP bloka sa dekorativnom trakom boje talasa (storyboard 5: „nema talasa").
const STATIC_W = 1440
const STATIC_H = 120
function staticEdge(base: number, a1: number, a2: number, ph1: number, ph2: number) {
  const pts: [number, number][] = []
  for (let i = 0; i <= 48; i++) {
    const x = (i / 48) * STATIC_W
    pts.push([x, base + a1 * Math.sin((TAU * x) / (L1 * STATIC_W) + ph1) + a2 * Math.sin((TAU * x) / (L2 * STATIC_W) + ph2)])
  }
  return pts
}
const sTop = staticEdge(44, 14, 5, 0.9, 2.3)
const sBottom = staticEdge(86, 11, 4, 3.4, 0.4)
const line = (pts: [number, number][]) => pts.map(([x, y], i) => `${i ? 'L' : 'M'}${f1(x)} ${f1(y)}`).join('')
const back = (pts: [number, number][]) => [...pts].reverse().map(([x, y]) => `L${f1(x)} ${f1(y)}`).join('')
const STATIC_TOP = line(sTop)
const STATIC_BOTTOM = line(sBottom)
const STATIC_POUR = `M0 0L${STATIC_W} 0${back(sTop)}Z`
const STATIC_BAND = `${STATIC_TOP}${back(sBottom)}Z`

export function WaveEdgeStatic({ className = '' }: { className?: string }) {
  const [id] = useState(() => `wave-static-${++uid}`)
  return (
    <div className={`wave-static ${className}`} aria-hidden="true">
      <svg viewBox={`0 0 ${STATIC_W} ${STATIC_H}`} preserveAspectRatio="none" focusable="false">
        <defs>
          <linearGradient id={`${id}-fill`} x1="0" y1="0" x2="0" y2="1">
            <stop className="wave__stop--top" offset="0" />
            <stop className="wave__stop--mid" offset="0.45" />
            <stop className="wave__stop--bottom" offset="1" />
          </linearGradient>
        </defs>
        <rect className="wave-static__sip" width={STATIC_W} height={STATIC_H} />
        <path className="wave-static__pour" d={STATIC_POUR} />
        <path className="wave-static__tint" d={STATIC_BAND} fill={`url(#${id}-fill)`} />
        <path className="wave__line wave__under" d={STATIC_BOTTOM} />
        <path className="wave__line wave__shine" d={STATIC_TOP} transform="translate(0 3)" />
        <path className="wave__line wave__meniscus" d={STATIC_TOP} />
      </svg>
    </div>
  )
}
