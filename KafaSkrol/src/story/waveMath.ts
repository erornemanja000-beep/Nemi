// Geometrija ivica talasa (Z6; izdvojeno u Z12, oblik po Z15 u Z20). Wave.tsx crta po ovome, a Story
// po istoj ivici menja boju headera kad najviša tačka gornje ivice pređe liniju headera (bez DOM-a).
//
// Oblik (Z15, referenca f137): jedan veliki talas preko ekrana (A1 0,10 · U, talasna dužina 1,8 širine),
// a donja ivica ima suprotnu fazu, pa je traka sočivo: oko 35 % visine u sredini, 8–10 % na krajevima
// (1440 × 900). Faza blago klizi sa p, da sočivo „plovi".

export const TAU = Math.PI * 2
/** Amplitude ivice u jedinicama U = min(H, 0,9·W). */
export const A1 = 0.1
export const A2 = 0.015
/** Talasne dužine u širinama ekrana. */
export const L1 = 1.8
export const L2 = 0.45
/** Do ovog p tečnost se razliva nadole; POUR je i ispod nje. */
export const P_FLOOD = 0.12
/** Debljina trake (osnovne linije) dok je traka u ekranu, u udelu visine; sinusoida dodaje ±2·A1·U. */
const BAND = 0.13

export const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)
export const smooth = (a: number, b: number, v: number) => {
  const t = clamp01((v - a) / (b - a))
  return t * t * (3 - 2 * t)
}

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
export function baselines(p: number, s: number, margin: number) {
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
  // donja ivica: ulazi odozdo, pa prati gornju na BAND (sočivo daje sinusoida suprotne faze), izlazi gore
  const bottom = [1 + margin + 0.02, 0.9, 0.47 + BAND, 0.29 + BAND, 0.07 + BAND, -0.15 + BAND, -0.43 + BAND]
  const yB = Math.max(pchip(BOTTOM_P, bottom, p), yT + BAND * 0.75)
  return { yT, yB, flood: false }
}

export type EdgeWave = { ph1: number; ph2: number; tilt: number; amp: number }

/** Faza velikog talasa kad je sredina ekrana najviša tačka gornje (i najniža donje) ivice. */
const LENS_PH = -Math.PI / 2 - Math.PI / L1

export function edgeWaves(p: number) {
  const env = smooth(0, P_FLOOD, p)
  // sočivo blago klizi (±0,3 rad kroz ceo talas); sitna talasanja (A2) klize brže, svako na svoju stranu
  const ph1 = LENS_PH + 0.6 * (p - 0.5)
  // isti nagib gore i dole: sočivo se naginje celo, a debljina na krajevima ostaje ista
  const tilt = 0.04 * Math.sin(Math.PI * p)
  const top: EdgeWave = {
    ph1,
    ph2: 2.3 - TAU * 1.3 * p,
    tilt,
    amp: env,
  }
  const bottom: EdgeWave = {
    ph1: ph1 + Math.PI,
    ph2: 0.4 - TAU * 1.05 * p,
    tilt,
    amp: env,
  }
  return { top, bottom }
}

/** Ivica = osnovna linija + zbir dve sinusoide (faza klizi sa p) + blag nagib. */
export function edgeY(x: number, base: number, w: EdgeWave, W: number, U: number) {
  return (
    base +
    w.amp * U * (A1 * Math.sin((TAU * x) / (L1 * W) + w.ph1) + A2 * Math.sin((TAU * x) / (L2 * W) + w.ph2)) +
    w.amp * w.tilt * U * (x / W - 0.5)
  )
}

/** Margina ispod ekrana (u H) za tečnost koja se razliva i za donju ivicu koja ulazi odozdo. */
export const waveMargin = (U: number, H: number) => ((A1 + A2) * U * 1.6) / Math.max(H, 1) + 0.03

/**
 * Najviša tačka gornje ivice u px Wave sloja (W × H) za p i s = startY / H; isto što Wave crta.
 * Story po njoj menja boju headera.
 */
export function waveTopMin(p: number, s: number, W: number, H: number, samples = 40) {
  const q = clamp01(p)
  const U = Math.min(H, 0.9 * W)
  const yT = baselines(q, s, waveMargin(U, H)).yT * H
  const { top } = edgeWaves(q)
  let min = Infinity
  for (let i = 0; i <= samples; i++) min = Math.min(min, edgeY((i / samples) * W, yT, top, W, U))
  return min
}
