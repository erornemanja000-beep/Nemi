// Vremenska osa priče GRIND → POUR → SIP (plan-izrade.md, Interfejs 2; storyboard.md 0–8).
// Jedini izvor brojeva za Story.tsx, DevSeq.tsx i scripts/shots.mjs (preko window.__story).
//
// Desktop (od 64rem × 600 px, bez reduced motion): jedna lepljiva scena kroz ceo kontejner #top.
//   Brojevi su u vh skrola od vrha priče. Kontejner je visok END + 100 vh (scena je 100 vh).
// Telefon (odluka direktora 2, mockup-390, mapa-skrola): poglavlja su jedno ispod drugog, bez pina i
//   bez šava. Svako poglavlje ima svoj sat i svoju kraću sekvencu (nivo m) koja se odvija dok je u
//   ekranu. Brojevi su udeli visine ekrana (svh) i vezani su za položaj sloja, pa ne zavise od dužine
//   teksta. Talas je traka preko granice POUR/SIP (oko 60 svh skrola).
import type { ChapterId } from '../content/types'

/** [y, kadar]: y u vh (desktop) ili u udelu ekrana (telefon); između čvorova linearno. */
export type Knot = readonly [y: number, frame: number]

export const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v)
/** 0…1 između a i b (linearno, stegnuto) */
export const span = (a: number, b: number, v: number) => clamp01((v - a) / (b - a))
export const smooth = (a: number, b: number, v: number) => {
  const t = span(a, b, v)
  return t * t * (3 - 2 * t)
}

/** Kadar za y po čvorovima (pre prvog i posle poslednjeg čvora stoji na ivici). */
export function frameAt(knots: readonly Knot[], y: number): number {
  if (y <= knots[0][0]) return knots[0][1]
  for (let i = 0; i < knots.length - 1; i++) {
    const [y0, g0] = knots[i]
    const [y1, g1] = knots[i + 1]
    if (y <= y1) return g0 + ((y - y0) / (y1 - y0)) * (g1 - g0)
  }
  return knots[knots.length - 1][1]
}

/** Obrnuto od frameAt: prvi y na kome je kadar g. */
export function yAtFrame(knots: readonly Knot[], g: number): number {
  if (g <= knots[0][1]) return knots[0][0]
  for (let i = 0; i < knots.length - 1; i++) {
    const [y0, g0] = knots[i]
    const [y1, g1] = knots[i + 1]
    if (g <= g1) return y0 + ((g - g0) / (g1 - g0)) * (y1 - y0)
  }
  return knots[knots.length - 1][0]
}

// =====================================================================================
// Desktop (vh od vrha priče). Tabela iz plana, Interfejs 2.
// =====================================================================================
export const DESK = {
  /** GRIND zakačen, G1–G64 */
  grindPin: [0, 200],
  /** šav: GRIND ide gore, POUR ulazi odozdo, oba platna crtaju G65–G96 */
  seam: [200, 300],
  /** POUR zakačen, G97–G176 */
  pourPin: [300, 540],
  /** talas: POUR G177–G192 + SIP S1–S16 */
  wave: [540, 640],
  /** SIP zakačen, S17–S64 */
  sipPin: [640, 790],
  /** posle ovoga scena odlazi gore, a prodavnica ulazi (kontejner je END + 100 vh) */
  end: 790,
} as const

/** sat G (GRIND i POUR dele vreme) */
export const DESK_G: readonly Knot[] = [
  [0, 1],
  [200, 65],
  [300, 97],
  [540, 177],
  [640, 192],
]
/** sat S (SIP) */
export const DESK_S: readonly Knot[] = [
  [540, 1],
  [640, 17],
  [790, 64],
]

/** opseg svakog poglavlja (za reč u pozadini i učitavanje): od ulaska do izlaska */
export const DESK_RANGE: Record<ChapterId, readonly [number, number]> = {
  grind: [0, 300],
  pour: [200, 640],
  sip: [540, 790],
}

/** početak poglavlja za strelice i tačkice: GRIND, POUR pin, SIP pin */
export const DESK_NAV: Record<ChapterId, number> = { grind: 0, pour: 300, sip: 640 }

/**
 * POUR se tokom talasa „otkači" i ide gore sporije od talasa (storyboard 5, 70–100 %):
 * do DRIFT vh, od p = from do p = 1.
 */
export const DESK_POUR_DRIFT = { vh: 22, from: 0.55 } as const

/** kartice SIP uleću na 45–80 % SIP opsega (540–790 vh), redom 2 → 1 → 0 (Z7) */
export const CARD_RANGE = [0.45, 0.8] as const

// =====================================================================================
// Telefon (udeli visine ekrana, svh). Položaji su vezani za slojeve, ne za vrh stranice.
// =====================================================================================
export const PHONE = {
  /** GRIND: G1 na vrhu stranice → G96 kad donja ivica GRIND sloja stigne na ovaj udeo ekrana */
  grindEndAt: 0.15,
  /** POUR: G65 kad gornja ivica POUR platna uđe na dno ekrana (1,0), G177 na početku talasa */
  pourStartAt: 1,
  /** talas počinje kad je granica POUR/SIP na 80 % ekrana i traje dok granica ne stigne do vrha */
  waveFrom: 0.8,
  waveTo: 0,
  /** SIP: S17 na kraju talasa → S64 posle još ovoliko ekrana skrola */
  sipLength: 0.45,
  /** tekst ulazi kad njegov vrh pređe ovaj udeo ekrana */
  textAt: 0.85,
  /** kartice se pojavljuju kad vrh trake pređe ovaj udeo ekrana */
  cardsAt: 0.88,
} as const

// =====================================================================================
// Događaji na satovima (isti na desktopu i telefonu)
// =====================================================================================
/** para u POUR: od G124 (storyboard 4), pun intenzitet do G132; gasi se do p ≈ 0,2 talasa (Z6) */
export const STEAM_POUR = { from: 124, full: 132, waveOff: 0.2 } as const
/** para u SIP: od S20 (storyboard 6), pun intenzitet do S28 */
export const STEAM_SIP = { from: 20, full: 28 } as const

/**
 * Para: mesto i širina omotača u jedinicama S, od ose (x) i vrha punog kadra (y). Snimci imaju izvor
 * pare pri dnu (A: ~68 % širine, B: ~84 %), pa se taj deo stavlja iznad V60 i iznad šolje.
 * Z22 podešava ove brojeve po pravim kadrovima.
 */
export const STEAM_BOX = {
  pour: { x: -0.33, y: 0.21, w: 0.48 },
  sip: { x: -0.4, y: 0.12, w: 0.48 },
} as const

/** Pozadinska reč klizi ~10 % širine kroz opseg poglavlja (dizajn.md 6). */
export const WORD_SHIFT = 0.1

/** Tekst ulazi (fade + 24 px; trajanje i easing su u story.css iz tokena). Desktop pragovi: */
export const TEXT_IN = {
  /** POUR: kad je šav pređen bar do pola; nazad ispod 30 % */
  pour: { on: 0.5, off: 0.3 },
  /** SIP: kad je talas na 45 %; nazad ispod 25 % */
  sip: { on: 0.45, off: 0.25 },
} as const

/**
 * Ulet kartica (desktop): početni pomeraj (udeo širine/visine ekrana), okret oko Y i Z i veličina.
 * Kartice uleću redom 2 → 1 → 0, svaka u svom delu CARD_RANGE (start, kraj u udelu opsega).
 * Krivu daje --ease-settle (mali odskok), a providnost raste linearno u prvoj trećini.
 */
export const CARD_FLIGHT: Record<0 | 1 | 2, { at: readonly [number, number]; x: number; y: number; ry: number; rz: number; s: number }> = {
  2: { at: [0, 0.55], x: 0.34, y: -0.3, ry: 115, rz: 28, s: 0.7 },
  1: { at: [0.2, 0.75], x: 0.3, y: 0.34, ry: -105, rz: -24, s: 0.72 },
  0: { at: [0.45, 1], x: -0.3, y: 0.36, ry: 100, rz: 18, s: 0.74 },
}

// =====================================================================================
// Učitavanje u delovima (storyboard 8, plan Z12 tačka 3)
// =====================================================================================
/** 0 posle `load`, 1 na 30 % GRIND-a, 2 na ulazu u POUR pin, 3 na 60 % POUR-a */
export type LoadStage = 0 | 1 | 2 | 3
export type LoadStep = {
  stage: LoadStage
  id: ChapterId
  /** raspon u kadrovima sata (from/to) i „svaki n-ti fajl nivoa" (step) */
  req: { from?: number; to?: number; step?: number }
  /** veći ide pre (zajednički red u sequence.ts) */
  priority: number
}
export const LOAD_PLAN: readonly LoadStep[] = [
  { stage: 0, id: 'grind', req: { step: 6 }, priority: 60 },
  { stage: 0, id: 'grind', req: { step: 2 }, priority: 50 },
  { stage: 0, id: 'grind', req: {}, priority: 40 },
  // prelaz mora biti ceo pre 60 % GRIND-a, pa ide ispred ostatka GRIND-a
  { stage: 1, id: 'pour', req: { from: 65, to: 96 }, priority: 45 },
  { stage: 1, id: 'pour', req: { step: 6 }, priority: 30 },
  { stage: 2, id: 'pour', req: {}, priority: 20 },
  { stage: 2, id: 'sip', req: { step: 6 }, priority: 15 },
  { stage: 3, id: 'sip', req: {}, priority: 10 },
]
/** desktop: y (vh) na kome počinje deo 1, 2 i 3 (GRIND 0–300 vh, POUR 200–640 vh) */
export const DESK_LOAD_AT = [0, 90, 300, 464] as const
/** telefon: kadar sata GRIND (deo 1) i sata POUR (delovi 2 i 3) */
export const PHONE_LOAD_AT = { grind: 1 + 0.3 * 95, pourPin: 97, pour60: 65 + 0.6 * 127 } as const

/** dekodirano najviše ±16 kadrova oko trenutnog (odluka direktora: ~4 MB po d kadru) */
export const RETAIN = 16

// =====================================================================================
// Geometrija pre seq.json (Z5): isto kao full/crop u seq.json. Koristi se samo dok media.ts nema
// `geometry` (Z13); posle toga važi media.ts, a čim stigne seq.json, važi on.
// =====================================================================================
export const FALLBACK_GEOMETRY: Record<ChapterId, { full: { W: number; H: number }; crop: { x0: number; y0: number; w: number; h: number } }> = {
  grind: { full: { W: 1, H: 1.25 }, crop: { x0: 0.22, y0: 0, w: 0.56, h: 1.25 } },
  pour: { full: { W: 1, H: 1 }, crop: { x0: 0.26, y0: 0, w: 0.72, h: 1 } },
  sip: { full: { W: 1, H: 1 }, crop: { x0: 0.2, y0: 0, w: 0.64, h: 0.86 } },
}

/** Sidra pre seq.json (seq.json ih zamenjuje): pult, sto i nivo kafe u bokalu na G177. */
export const FALLBACK_ANCHORS = { pult_y: 0.95, sto_y: 0.78, kafa_y: 0.848 } as const
