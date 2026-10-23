// Osnovne linije ivica talasa (Z6, izdvojeno u Z12): Wave.tsx crta po njima, a Story (Z12) po gornjoj
// liniji menja boju headera kad ivica pređe liniju headera, bez čitanja iz DOM-a.

/** Do ovog p tečnost se razliva nadole; POUR je i ispod nje. */
export const P_FLOOD = 0.12

const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)

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
  // donja ivica: ulazi odozdo, debljina trake 18 % (p 0,3) → 35 % (p 0,5) → izlazi gore
  const bottom = [1 + margin + 0.02, 0.9, 0.65, 0.63, 0.35, 0.05, -0.2]
  const yB = Math.max(pchip(BOTTOM_P, bottom, p), yT + 0.12)
  return { yT, yB, flood: false }
}

/**
 * Osnovna linija gornje ivice (bez sinusoida) u udelu visine Wave sloja, za p 0–1 i s = startY / H.
 */
export function waveTopAt(p: number, s: number) {
  return baselines(clamp01(p), s, 0).yT
}
