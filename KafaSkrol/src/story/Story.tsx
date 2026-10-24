// Priča GRIND → POUR → SIP (Z12). Brojevi skrola su u timeline.ts, raspored u story.css.
//
// Tri režima (isti upiti kao `desk` u index.css i useMedia.ts):
// - Desktop: #top je visok 890 vh, a scena (100 vh) je lepljiva kroz ceo kontejner. Jedan ScrollTrigger
//   bez pin-spacer-a vodi sve: sat G (GRIND i POUR zajedno, šav G65–G96), sat S (SIP), traku sa GRIND i
//   POUR slojem (šav), talas, reči, ulet kartica, paru, boju headera i učitavanje u delovima.
// - Telefon (odluka direktora 2): slojevi jedan ispod drugog, bez pina i bez šava. Svako poglavlje ima
//   svoj sat i nivo m, a sekvenca se odvija dok je sloj u ekranu. Talas je fiksan sloj preko ekrana dok
//   granica POUR/SIP prolazi (≈ 60 svh); SIP zato zalazi ispod POUR-a (--wave-ov).
// - Reduced motion: tri bloka sa posterima <img>, bez platna i bez ijednog zahteva za kadrove, statična
//   ivica talasa između POUR i SIP, bez pare. Tekst i kartice odmah stoje, strelice skaču odmah.
//
// Pravila: menja se samo transform i opacity (slojevi, omotači data-anim, omotači pare) i nekoliko
// atributa; u petlji se ne čita layout (sve mere su iz measure(), pri promeni veličine). Visina priče je
// konačna od prvog crtanja: desktop je u vh, telefon u svh i fiksnim visinama scena.
import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties, type RefObject } from 'react'
import { chapters } from '../content/chapters'
import { media } from '../content/media'
import type { ActiveChapter, Chapter, ChapterId } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { registerChapterNavigator, setActiveChapter } from '../lib/chapterStore'
import { ScrollTrigger, scrollToTarget } from '../lib/motion'
import { createClock, kafaYAt, SEQ_DEBUG, useSequence, type Clock, type SeqGeometry, type Sequence } from '../lib/sequence'
import { useIsPhone, useReducedMotion } from '../lib/useMedia'
import { BackWord } from './BackWord'
import { ChapterNav } from './ChapterNav'
import { ChapterText } from './ChapterText'
import { SceneBackdrop } from './SceneBackdrop'
import { SeqCanvas } from './SeqCanvas'
import { SipCards } from './SipCards'
import { Sparkle } from './Sparkle'
import { Steam } from './Steam'
import * as T from './timeline'
import { Wave, WaveEdgeStatic, type WaveHandle } from './Wave'
import { waveTopMin } from './waveMath'
import './story.css'

const IDS: readonly ChapterId[] = ['grind', 'pour', 'sip']
const byId = Object.fromEntries(chapters.items.map((c) => [c.id, c])) as Record<ChapterId, Chapter>
const pct = (v: number) => `${(v * 100).toFixed(4)}%`

/** Geometrija pre seq.json (i u reduced motion): media.ts, isto kao full/crop u seq.json (Z5, Z13). */
const geometryOf = (id: ChapterId): SeqGeometry => media.seq[id].geometry

/** Zbir offsetTop do pretka (ili do vrha dokumenta). Ne zavisi od transform-a (talas skalira sočivo). */
function offsetWithin(el: HTMLElement | null, ancestor: HTMLElement | null) {
  let y = 0
  let n: HTMLElement | null = el
  while (n && n !== ancestor) {
    y += n.offsetTop
    n = n.offsetParent as HTMLElement | null
  }
  return y
}

/** cubic-bezier(x1, y1, x2, y2) kao funkcija 0…1 (Newton + bisekcija), za --ease-settle iz tokena. */
function bezier(x1: number, y1: number, x2: number, y2: number) {
  const cx = 3 * x1
  const bx = 3 * (x2 - x1) - cx
  const ax = 1 - cx - bx
  const cy = 3 * y1
  const by = 3 * (y2 - y1) - cy
  const ay = 1 - cy - by
  const sx = (t: number) => ((ax * t + bx) * t + cx) * t
  const sy = (t: number) => ((ay * t + by) * t + cy) * t
  return (x: number) => {
    if (x <= 0) return 0
    if (x >= 1) return 1
    let t = x
    for (let i = 0; i < 6; i++) {
      const d = (3 * ax * t + 2 * bx) * t + cx
      const e = sx(t) - x
      if (Math.abs(e) < 1e-5 || Math.abs(d) < 1e-6) break
      t -= e / d
    }
    if (t < 0 || t > 1 || Math.abs(sx(t) - x) > 1e-3) {
      let lo = 0
      let hi = 1
      t = x
      for (let i = 0; i < 24; i++) {
        if (sx(t) < x) lo = t
        else hi = t
        t = (lo + hi) / 2
      }
    }
    return sy(t)
  }
}

/** Kriva iz CSS tokena (npr. --ease-settle), a bez nje vrednost iz tokens.css. */
function easeFromToken(name: string, fallback: [number, number, number, number]) {
  const raw = getComputedStyle(document.documentElement).getPropertyValue(name)
  const m = raw.match(/cubic-bezier\(([^)]+)\)/)
  const n = m ? m[1].split(',').map(Number) : []
  const [a, b, c, d] = n.length === 4 && n.every(Number.isFinite) ? n : fallback
  return bezier(a, b, c, d)
}

// ---------------------------------------------------------------------------------------------
// Delovi slojeva
// ---------------------------------------------------------------------------------------------
type Live = {
  seq: Record<ChapterId, Sequence | null>
  clock: Record<ChapterId, Clock>
  active: Record<ChapterId, boolean>
  /** poster još ne traži (storyboard 8: prvi ekran ostaje u budžetu) */
  defer: Record<ChapterId, boolean>
  steam: { pour: boolean; sip: boolean }
  bags: boolean
}

function Canvas({ id, phone, live, priority = false }: { id: ChapterId; phone: boolean; live: Live | null; priority?: boolean }) {
  const { tx } = useLang()
  const seq = live?.seq[id] ?? null
  const geo = seq?.manifest ?? geometryOf(id)
  const p = media.seq[id].poster[phone ? 'm' : 'd']
  return (
    <>
      <SeqCanvas
        seq={seq}
        clock={live?.clock[id] ?? null}
        poster={{ src: p.src, alt: tx(byId[id].alt), priority }}
        geometry={geometryOf(id)}
        active={live?.active[id] ?? true}
        deferPoster={live?.defer[id] ?? false}
        className={`story-canvas story-canvas--${id}`}
      />
      {id !== 'sip' && (
        <div
          aria-hidden="true"
          className={`story-fade story-fade--${id}`}
          style={{ '--crop-l': pct(geo.crop.x0 / geo.full.W), '--crop-w': pct(geo.crop.w / geo.full.W) } as CSSProperties}
        />
      )}
    </>
  )
}

function SteamHost({ which, active }: { which: 'pour' | 'sip'; active: boolean }) {
  const box = T.STEAM_BOX[which]
  return (
    <div
      data-steam={which}
      className={`steam-host story-steam story-steam--${which}`}
      style={{ '--steam-x': box.x, '--steam-y': box.y, '--steam-w': box.w } as CSSProperties}
    >
      <Steam which={which} active={active} className="w-full" />
    </div>
  )
}

type LayerProps = { phone: boolean; live: Live | null }

function GrindLayer({ phone, live }: LayerProps) {
  return (
    <section id="grind" data-chapter="grind" aria-labelledby="t-grind" className="ch-layer layer-grind">
      <SceneBackdrop chapter="grind" />
      <ChapterText chapter={byId.grind} />
      <div className="ch-stage">
        <BackWord chapter="grind" />
        <Canvas id="grind" phone={phone} live={live} priority />
      </div>
      <ChapterNav current="grind" />
    </section>
  )
}

function PourLayer({ phone, live, clip }: LayerProps & { clip?: RefObject<HTMLDivElement | null> }) {
  return (
    <section id="pour" data-chapter="pour" aria-labelledby="t-pour" className="ch-layer layer-pour">
      <div ref={clip} className="layer-pour__clip">
        <SceneBackdrop chapter="pour" />
        <ChapterText chapter={byId.pour} />
        <div className="ch-stage">
          <BackWord chapter="pour" />
          <Canvas id="pour" phone={phone} live={live} />
          {live && <SteamHost which="pour" active={live.steam.pour} />}
        </div>
        <ChapterNav current="pour" />
      </div>
    </section>
  )
}

function SipLayer({ phone, live, lens }: LayerProps & { lens?: RefObject<HTMLDivElement | null> }) {
  // desktop: tekst je van sočiva, da ga talas ne uveća i ne pomeri (Z25); telefon: u koloni sočiva
  return (
    <section id="sip" data-chapter="sip" aria-labelledby="t-sip" className="ch-layer layer-sip">
      {!phone && <ChapterText chapter={byId.sip} />}
      <div ref={lens} className="layer-sip__lens">
        <SceneBackdrop chapter="sip" />
        {phone && <ChapterText chapter={byId.sip} />}
        <div className="ch-stage">
          <BackWord chapter="sip" />
          <Canvas id="sip" phone={phone} live={live} />
          <Sparkle />
          {live && <SteamHost which="sip" active={live.steam.sip} />}
        </div>
      </div>
      <SipCards loadImages={live ? live.bags : true} />
      <ChapterNav current="sip" />
    </section>
  )
}

// ---------------------------------------------------------------------------------------------
// Dev / ?debug: tačke za scripts/shots.mjs i stanje za proveru
// ---------------------------------------------------------------------------------------------
type StoryPoint = { name: string; y: number }
type StoryBoundary = { from: ActiveChapter; to: ActiveChapter; y: number }
type StoryDebug = {
  mode: 'pinned' | 'flow' | 'still'
  /** položaji skrola (px) za snimke: granice i sredine segmenata (Interfejs 2) */
  points(): StoryPoint[]
  /** skrol (px) na kome header prelazi iz jednog poglavlja u drugo */
  boundaries(): StoryBoundary[]
  /** skrol (px) na koji vode strelice i tačkice */
  nav(): Record<ChapterId, number>
  state(): Record<string, unknown>
}

declare global {
  interface Window {
    __story?: StoryDebug
  }
}

// ---------------------------------------------------------------------------------------------
// Živa priča (desktop i telefon)
// ---------------------------------------------------------------------------------------------
type Flags = {
  active: Record<ChapterId, boolean>
  steam: { pour: boolean; sip: boolean }
  /** dostignut deo učitavanja (timeline LOAD_PLAN); raste, ne opada */
  stage: T.LoadStage
}
const FLAGS0: Flags = { active: { grind: true, pour: true, sip: false }, steam: { pour: false, sip: false }, stage: 0 }

const sameFlags = (a: Flags, b: Flags) =>
  a.stage === b.stage &&
  a.steam.pour === b.steam.pour &&
  a.steam.sip === b.steam.sip &&
  IDS.every((id) => a.active[id] === b.active[id])

/** Mere iz measure() (px). Desktop koristi rootTop, vh, S, W i okvire u slojevima; telefon i ostalo. */
type Metrics = {
  vh: number
  W: number
  S: number
  rootTop: number
  line: number
  pourFrameTop: number
  // telefon (dokument)
  grindBottom: number
  pourTop: number
  pourBottom: number
  pourCanvasTop: number
  pourClipTop: number
  lensTop: number
  sipBottom: number
  textTop: Record<ChapterId, number>
  stripTop: number
}

function LiveStory({ phone }: { phone: boolean }) {
  const root = useRef<HTMLDivElement>(null)
  const track = useRef<HTMLDivElement>(null)
  const probe = useRef<HTMLDivElement>(null)
  const pourClip = useRef<HTMLDivElement>(null)
  const sipLens = useRef<HTMLDivElement>(null)
  const wave = useRef<WaveHandle>(null)

  const grind = useSequence('grind')
  const pour = useSequence('pour')
  const sip = useSequence('sip')
  const seqs = useRef({ grind, pour, sip })
  useLayoutEffect(() => {
    seqs.current = { grind, pour, sip }
  }, [grind, pour, sip])

  // desktop: GRIND i POUR na istom satu G (šav); telefon: svako poglavlje svoj sat
  const [clockA] = useState(() => createClock([], { retain: T.RETAIN }))
  const [clockB] = useState(() => createClock([], { retain: T.RETAIN, initial: 65 }))
  const [clockS] = useState(() => createClock([], { retain: T.RETAIN }))
  const clocks: Record<ChapterId, Clock> = { grind: clockA, pour: phone ? clockB : clockA, sip: clockS }

  const [flags, setFlags] = useState<Flags>(FLAGS0)
  const flagsRef = useRef(flags)
  const [loaded, setLoaded] = useState(() => document.readyState === 'complete')
  /** ponovo izmeri i primeni (seq.json sa sidrima, promena veličine) */
  const refreshRef = useRef<() => void>(() => {})

  useEffect(() => {
    clockA.start()
    clockB.start()
    clockS.start()
    return () => {
      clockA.stop()
      clockB.stop()
      clockS.stop()
    }
  }, [clockA, clockB, clockS])

  useEffect(() => {
    if (loaded) return
    const on = () => setLoaded(true)
    window.addEventListener('load', on, { once: true })
    return () => window.removeEventListener('load', on)
  }, [loaded])

  // ---- učitavanje u delovima (storyboard 8): posle `load`, deo po deo kako skrol napreduje ----
  const issued = useRef(new WeakMap<Sequence, Set<number>>())
  useEffect(() => {
    if (!loaded) return
    const all: Record<ChapterId, Sequence | null> = { grind, pour, sip }
    T.LOAD_PLAN.forEach((step, i) => {
      const s = all[step.id]
      if (!s || step.stage > flags.stage) return
      let done = issued.current.get(s)
      if (!done) issued.current.set(s, (done = new Set()))
      if (done.has(i)) return
      done.add(i)
      void s.request(step.req, step.priority)
    })
  }, [loaded, flags.stage, grind, pour, sip])

  // seq.json je stigao (sidra: kafa_y, pult_y, sto_y; geometrija)
  useEffect(() => {
    refreshRef.current()
  }, [grind, pour, sip])

  useLayoutEffect(() => {
    const el = root.current
    const probeEl = probe.current
    if (!el || !probeEl) return
    const q = <E extends HTMLElement>(sel: string) => el.querySelector<E>(sel)
    const layers = { grind: q('#grind'), pour: q('#pour'), sip: q('#sip') }
    const texts = {
      grind: q('#grind [data-anim="text"]'),
      pour: q('#pour [data-anim="text"]'),
      sip: q('#sip [data-anim="text"]'),
    }
    const words = { grind: q('#grind [data-anim="word"]'), pour: q('#pour [data-anim="word"]'), sip: q('#sip [data-anim="word"]') }
    const cards = [...el.querySelectorAll<HTMLElement>('[data-anim="card"]')]
    const cardsBox = q('.sip-cards')
    const strip = q('.sip-cards__strip')
    const steamPour = q('[data-steam="pour"]')
    const steamSip = q('[data-steam="sip"]')
    const boxes = { grind: q('.story-canvas--grind'), pour: q('.story-canvas--pour'), sip: q('.story-canvas--sip') }
    const settle = easeFromToken('--ease-settle', [0.34, 1.4, 0.64, 1])
    const trackEl = track.current

    // 1. početna stanja PRE prvog čitanja layout-a (inače bi tekst prvo bio vidljiv, pa izbledeo)
    if (texts.grind) texts.grind.dataset.in = '1'
    if (texts.pour) texts.pour.dataset.in = '0'
    if (texts.sip) texts.sip.dataset.in = '0'
    if (phone && cardsBox) cardsBox.dataset.in = '0'
    if (!phone) for (const c of cards) c.style.opacity = '0'

    // 2. mere (samo ovde se čita layout)
    const m: Metrics = {
      vh: 1,
      W: 1,
      S: 1,
      rootTop: 0,
      line: 32,
      pourFrameTop: 0,
      grindBottom: 0,
      pourTop: 0,
      pourBottom: 0,
      pourCanvasTop: 0,
      pourClipTop: 0,
      lensTop: 0,
      sipBottom: 0,
      textTop: { grind: 0, pour: 0, sip: 0 },
      stripTop: 0,
    }
    const anchor = (id: 'pour' | 'sip', key: 'pult_y' | 'sto_y') => {
      const v = seqs.current[id]?.manifest.anchors[key]
      return typeof v === 'number' ? v : T.FALLBACK_ANCHORS[key]
    }
    const measure = () => {
      m.vh = probeEl.offsetHeight || window.innerHeight
      m.W = el.clientWidth || window.innerWidth
      m.S = boxes.grind?.getBoundingClientRect().width || m.vh
      m.rootTop = offsetWithin(el, null)
      m.line = (document.querySelector<HTMLElement>('header')?.offsetHeight ?? 64) / 2
      m.pourFrameTop = offsetWithin(boxes.pour, layers.pour)
      if (phone) {
        const top = (n: HTMLElement | null) => offsetWithin(n, null)
        m.grindBottom = top(layers.grind) + (layers.grind?.offsetHeight ?? 0)
        m.pourTop = top(layers.pour)
        m.pourBottom = m.pourTop + (layers.pour?.offsetHeight ?? 0)
        m.pourCanvasTop = m.pourTop + m.pourFrameTop
        m.pourClipTop = top(pourClip.current)
        m.lensTop = top(sipLens.current)
        m.sipBottom = top(layers.sip) + (layers.sip?.offsetHeight ?? 0)
        for (const id of IDS) m.textTop[id] = top(texts[id])
        m.stripTop = top(strip)
      }
      // --table-y: pult i sto iz sidara (seq.json), u px od vrha pozadine sloja (SceneBackdrop)
      const tableY = (id: 'pour' | 'sip', host: HTMLElement | null, key: 'pult_y' | 'sto_y') => {
        const layer = layers[id]
        if (!layer || !host) return
        layer.style.setProperty('--table-y', `${(offsetWithin(boxes[id], host) + anchor(id, key) * m.S).toFixed(1)}px`)
      }
      tableY('pour', pourClip.current, 'pult_y')
      tableY('sip', sipLens.current, 'sto_y')
      wave.current?.measure()
    }

    // 3. primena za trenutni skrol
    let lastShift = NaN
    let lastWaveP = -1
    let lastChapter: ActiveChapter | '' = ''
    const lastText: Record<ChapterId, string> = { grind: '1', pour: '0', sip: '0' }
    const lastWord: Record<ChapterId, number> = { grind: NaN, pour: NaN, sip: NaN }
    let lastCardsIn = '0'
    let lastSteam = { pour: -1, sip: -1 }
    const lastCard = cards.map(() => -1)
    let sipLive = ''
    let now = { y: 0, g: 1, gPour: 65, s: 1, p: 0 }

    const setText = (id: ChapterId, on: boolean) => {
      const v = on ? '1' : '0'
      const t = texts[id]
      if (t && lastText[id] !== v) {
        t.dataset.in = v
        lastText[id] = v
      }
    }
    const setWord = (id: ChapterId, t: number) => {
      const x = Math.round(-T.WORD_SHIFT * m.W * t * 10) / 10
      const w = words[id]
      if (w && x !== lastWord[id]) {
        w.style.transform = `translate3d(${x}px, 0, 0)`
        lastWord[id] = x
      }
    }
    const setSteam = (which: 'pour' | 'sip', o: number) => {
      const v = Math.round(o * 100) / 100
      if (v === lastSteam[which]) return
      lastSteam = { ...lastSteam, [which]: v }
      const host = which === 'pour' ? steamPour : steamSip
      if (host) host.style.opacity = String(v)
    }
    const setWave = (p: number, startY: number, layout: { pourTop?: number; lensTop?: number; waveTop?: number }) => {
      // na 0 i 1 talas miruje: šalje se samo prelaz, ne svaki skrol
      if ((p <= 0 || p >= 1) && p === lastWaveP) return
      wave.current?.set(p, startY, layout)
      lastWaveP = p
    }
    const commit = (next: Flags) => {
      const cur = flagsRef.current
      const merged: Flags = { ...next, stage: Math.max(cur.stage, next.stage) as T.LoadStage }
      if (sameFlags(cur, merged)) return
      flagsRef.current = merged
      setFlags(merged)
    }
    const setChapter = (c: ActiveChapter) => {
      if (c === lastChapter) return
      lastChapter = c
      setActiveChapter(c)
    }
    const kafa = (g: number) => (seqs.current.pour ? kafaYAt(seqs.current.pour.manifest, g) : null) ?? T.FALLBACK_ANCHORS.kafa_y
    // desktop: koliko POUR ide gore tokom talasa (px), da dno V60 ostane iznad najviše tačke talasa
    const lift = (p: number, startY: number) => {
      if (p <= 0) return 0
      const { dripper, gap, maxVh } = T.DESK_POUR_LIFT
      const crest = waveTopMin(p, startY / m.vh, m.W, m.vh)
      return Math.min((maxVh / 100) * m.vh, Math.max(0, m.pourFrameTop + dripper * m.S + gap * m.vh - crest))
    }
    // desktop: sloj koji se ne vidi (SIP ispod POUR-a pre talasa, POUR isečen posle talasa, GRIND iznad
    // ekrana posle šava) ima opacity 0, pa ga pregledač ne slaže u svakom kadru. Ostaje u DOM-u, čitaču
    // ekrana i redosledu tastature (fokus vodi na poglavlje, onFocus).
    const lastLayer: Record<ChapterId, string> = { grind: '', pour: '', sip: '' }
    const setLayer = (id: ChapterId, on: boolean) => {
      const v = on ? '' : '0'
      const l = layers[id]
      if (l && v !== lastLayer[id]) {
        l.style.opacity = v
        lastLayer[id] = v
      }
    }

    // ---------- desktop ----------
    const applyDesk = (scroll: number) => {
      const vh = m.vh
      const y = ((scroll - m.rootTop) / vh) * 100
      const seam = T.span(T.DESK.seam[0], T.DESK.seam[1], y)
      const p = T.span(T.DESK.wave[0], T.DESK.wave[1], y)
      const g = T.frameAt(T.DESK_G, y)
      const s = T.frameAt(T.DESK_S, y)
      now = { y, g, gPour: g, s, p }
      clockA.set(g)
      clockS.set(s)

      // talas kreće sa linije kafe u bokalu (kafa_y za trenutni G), merene dok POUR još miruje
      const stageTop = -Math.max(0, ((y - T.DESK.end) / 100) * vh)
      const startY = stageTop + m.pourFrameTop + kafa(g) * m.S
      // traka GRIND + POUR (šav), pa POUR ide gore zajedno sa talasom (dripper ostaje iznad tečnosti)
      const drift = lift(p, startY)
      const shift = Math.round((seam * vh + drift) * 100) / 100
      if (shift !== lastShift && trackEl) {
        trackEl.style.transform = `translate3d(0, ${-shift}px, 0)`
        lastShift = shift
      }
      const pourTop = stageTop + vh - shift
      setWave(p, startY, { pourTop })

      // tekst, reči, kartice
      setText('pour', lastText.pour === '1' ? seam >= T.TEXT_IN.pour.off : seam >= T.TEXT_IN.pour.on)
      setText('sip', lastText.sip === '1' ? p >= T.TEXT_IN.sip.off : p >= T.TEXT_IN.sip.on)
      for (const id of IDS) setWord(id, T.span(T.DESK_RANGE[id][0], T.DESK_RANGE[id][1], y))
      const sipLen = T.DESK.sipPin[1] - T.DESK.wave[0]
      const local = T.span(T.DESK.wave[0] + sipLen * T.CARD_RANGE[0], T.DESK.wave[0] + sipLen * T.CARD_RANGE[1], y)
      cards.forEach((card, i) => {
        const n = Number(card.dataset.sipCard) as 0 | 1 | 2
        const f = T.CARD_FLIGHT[n] ?? T.CARD_FLIGHT[0]
        const t = T.span(f.at[0], f.at[1], local)
        const key = Math.round(t * 1000)
        if (key === lastCard[i]) return
        lastCard[i] = key
        if (t >= 1) {
          card.style.transform = ''
          card.style.opacity = ''
          card.style.pointerEvents = ''
          delete card.dataset.flying
          return
        }
        // u letu staklo nema backdrop-filter (zamućenje bi se računalo iznova u svakom kadru, pod okretom
        // u 3D); pali se kad kartica sleti. Providna podloga stakla ostaje ista, pa se prelaz jedva vidi.
        if (t > 0) card.dataset.flying = ''
        else delete card.dataset.flying
        const e = settle(t)
        const k = 1 - e
        card.style.transform =
          `perspective(1200px) translate3d(${(k * f.x * m.W).toFixed(1)}px, ${(k * f.y * vh).toFixed(1)}px, 0) ` +
          `rotateY(${(k * f.ry).toFixed(2)}deg) rotateZ(${(k * f.rz).toFixed(2)}deg) scale(${(f.s + (1 - f.s) * e).toFixed(4)})`
        card.style.opacity = T.clamp01(t * 3).toFixed(3)
        card.style.pointerEvents = 'none'
      })

      // para: POUR od G124, gasi se do p ≈ 0,2; SIP od S20. Samo dok je scena u ekranu: skok preko
      // priče (meni → prodavnica) inače bi na trenutak pustio video koji se odmah prekida.
      const onStage = y > -100 && y < T.DESK.end + 100
      const oPour = onStage ? T.span(T.STEAM_POUR.from, T.STEAM_POUR.full, g) * (1 - T.span(0, T.STEAM_POUR.waveOff, p)) : 0
      const oSip = onStage ? T.span(T.STEAM_SIP.from, T.STEAM_SIP.full, s) : 0
      setSteam('pour', oPour)
      setSteam('sip', oSip)

      // header: granica sloja (ili najviša tačka ivice talasa) preko linije headera
      const line = m.line
      let chapter: ActiveChapter = 'grind'
      if (scroll - m.rootTop >= ((T.DESK.end + 100) / 100) * vh - line) chapter = 'page'
      else if (p >= 1 || (p > 0 && waveTopMin(p, startY / vh, m.W, vh) <= line)) chapter = 'sip'
      else if (vh - seam * vh <= line) chapter = 'pour'
      setChapter(chapter)

      setLayer('grind', y < T.DESK.seam[1])
      setLayer('pour', p < 1)
      setLayer('sip', y >= T.DESK.wave[0])

      const live = y >= T.DESK.wave[0] && y < T.DESK.end + 100 ? '1' : '0'
      if (live !== sipLive) el.dataset.sipLive = sipLive = live

      const stage = (y >= T.DESK_LOAD_AT[3] ? 3 : y >= T.DESK_LOAD_AT[2] ? 2 : y >= T.DESK_LOAD_AT[1] ? 1 : 0) as T.LoadStage
      commit({
        active: { grind: y < T.DESK.seam[1], pour: p < 1, sip: y >= T.DESK.wave[0] },
        steam: { pour: oPour > 0, sip: oSip > 0 },
        stage,
      })
    }

    // ---------- telefon ----------
    const applyPhone = (scroll: number) => {
      const H = m.vh
      const grindP = T.span(0, Math.max(1, m.grindBottom - T.PHONE.grindEndAt * H), scroll - m.rootTop)
      const gGrind = 1 + grindP * 95
      const B = m.pourBottom - scroll // granica POUR/SIP u ekranu (px)
      const p = T.span(T.PHONE.waveFrom * H, T.PHONE.waveTo * H, B)
      const s0 = m.pourCanvasTop - T.PHONE.pourStartAt * H
      const s1 = m.pourBottom - T.PHONE.waveFrom * H
      const gPour = p > 0 ? 177 + p * 15 : 65 + T.span(s0, s1, scroll) * 112
      const s = p < 1 ? 1 + p * 15 : 17 + T.span(m.pourBottom, m.pourBottom + T.PHONE.sipLength * H, scroll) * 47
      now = { y: scroll, g: gGrind, gPour, s, p }
      clockA.set(gGrind)
      clockB.set(gPour)
      clockS.set(s)

      // talas: fiksan sloj preko ekrana, POUR i sočivo SIP klize ispod
      const pourTop = m.pourClipTop - scroll
      const startY = m.pourCanvasTop - scroll + kafa(gPour) * m.S
      setWave(p, startY, { waveTop: 0, pourTop, lensTop: m.lensTop - scroll })

      const textOn = (id: ChapterId) => {
        const top = m.textTop[id] - scroll
        return lastText[id] === '1' ? top < 0.98 * H : top <= T.PHONE.textAt * H
      }
      setText('pour', textOn('pour'))
      setText('sip', textOn('sip'))
      setWord('grind', T.span(m.rootTop, m.grindBottom, scroll))
      setWord('pour', T.span(m.pourTop - H, m.pourBottom, scroll))

      // kartice se pojavljuju jednom, kad traka uđe u ekran
      if (lastCardsIn === '0' && cardsBox && m.stripTop - scroll <= T.PHONE.cardsAt * H) {
        cardsBox.dataset.in = lastCardsIn = '1'
      }

      // para samo dok je njen sloj u ekranu (vidi desktop)
      const pourIn = m.pourTop - scroll < H && B > 0
      const sipIn = B < H && m.sipBottom - scroll > 0
      const oPour = pourIn ? T.span(T.STEAM_POUR.from, T.STEAM_POUR.full, gPour) * (1 - T.span(0, T.STEAM_POUR.waveOff, p)) : 0
      const oSip = sipIn ? T.span(T.STEAM_SIP.from, T.STEAM_SIP.full, s) : 0
      setSteam('pour', oPour)
      setSteam('sip', oSip)

      const line = m.line
      let chapter: ActiveChapter = 'grind'
      if (m.sipBottom - scroll <= line) chapter = 'page'
      else if (p >= 1 || B <= line || (p > 0 && waveTopMin(p, startY / H, m.W, H) <= line)) chapter = 'sip'
      else if (m.pourTop - scroll <= line) chapter = 'pour'
      setChapter(chapter)

      const live = B < H && m.sipBottom - scroll > 0 ? '1' : '0'
      if (live !== sipLive) el.dataset.sipLive = sipLive = live

      const stage = (gPour >= T.PHONE_LOAD_AT.pour60 ? 3 : gPour >= T.PHONE_LOAD_AT.pourPin ? 2 : gGrind >= T.PHONE_LOAD_AT.grind ? 1 : 0) as T.LoadStage
      commit({ active: { grind: true, pour: true, sip: true }, steam: { pour: oPour > 0, sip: oSip > 0 }, stage })
    }

    const apply = (scroll = window.scrollY) => (phone ? applyPhone(scroll) : applyDesk(scroll))

    // ---- jedan ScrollTrigger za ceo kontejner (bez pin-a): vodi apply dok je priča u ekranu ----
    measure()
    apply()
    const st = ScrollTrigger.create({
      trigger: el,
      start: 'top bottom',
      end: 'bottom top',
      onUpdate: (self) => apply(self.scroll()),
      onRefresh: (self) => {
        measure()
        lastWaveP = -1
        apply(self.scroll())
      },
    })
    refreshRef.current = () => {
      measure()
      lastWaveP = -1
      apply()
    }

    // visina se menja (jezik, fontovi): ScrollTrigger ponovo meri sve (i sekcije ispod)
    let roTimer = 0
    let lastH = el.offsetHeight
    const ro = new ResizeObserver(() => {
      const h = el.offsetHeight
      if (h === lastH) return
      lastH = h
      window.clearTimeout(roTimer)
      roTimer = window.setTimeout(() => ScrollTrigger.refresh(), 120)
    })
    ro.observe(el)

    // ---- strelice i tačkice: početak GRIND-a, POUR pina i SIP pina ----
    const navY = (id: ChapterId) =>
      phone ? { grind: m.rootTop, pour: m.pourTop, sip: m.pourBottom }[id] : m.rootTop + (T.DESK_NAV[id] / 100) * m.vh
    const offNav = registerChapterNavigator((id) => scrollToTarget(navY(id)))

    // ---- tastatura na desktopu: fokus u pokrivenom sloju vodi na to poglavlje (kartice: posle uleta) ----
    const cardsDone = T.DESK.wave[0] + (T.DESK.sipPin[1] - T.DESK.wave[0]) * T.CARD_RANGE[1] + 4
    const onFocus = (e: FocusEvent) => {
      if (phone || !(e.target instanceof HTMLElement)) return
      const id = e.target.closest<HTMLElement>('[data-chapter]')?.dataset.chapter as ChapterId | undefined
      if (!id) return
      const y = now.y
      const front: ChapterId = y < (T.DESK.seam[0] + T.DESK.seam[1]) / 2 ? 'grind' : y < (T.DESK.wave[0] + T.DESK.wave[1]) / 2 ? 'pour' : 'sip'
      let to: number | null = null
      if (e.target.closest('.sip-card-slot')) {
        if (y < cardsDone || y > T.DESK.end) to = cardsDone
      } else if (id !== front) to = T.DESK_NAV[id]
      if (to !== null) scrollToTarget(m.rootTop + (to / 100) * m.vh, true)
    }
    el.addEventListener('focusin', onFocus)

    // ---- otvaranje sa #grind, #pour ili #sip: Home skače na sloj, a ovde se ispravlja na početak poglavlja ----
    const hash = window.location.hash.slice(1)
    let hashFrame = 0
    if (hash === 'grind' || hash === 'pour' || hash === 'sip') {
      hashFrame = requestAnimationFrame(() => {
        hashFrame = requestAnimationFrame(() => scrollToTarget(navY(hash), true))
      })
    }

    // ---- provera (dev ili ?debug) ----
    if (SEQ_DEBUG) {
      const vhPx = (v: number) => m.rootTop + (v / 100) * m.vh
      window.__story = {
        mode: phone ? 'flow' : 'pinned',
        points() {
          if (!phone) {
            const D = T.DESK
            const mid = (a: readonly [number, number]) => (a[0] + a[1]) / 2
            const marks: [string, number][] = [
              ['grind-start', D.grindPin[0]], ['grind-mid', mid(D.grindPin)], ['seam-start', D.seam[0]], ['seam-mid', mid(D.seam)],
              ['pour-start', D.pourPin[0]], ['pour-mid', mid(D.pourPin)], ['wave-start', D.wave[0]], ['wave-mid', mid(D.wave)],
              ['sip-start', D.sipPin[0]], ['sip-mid', mid(D.sipPin)], ['sip-end', D.sipPin[1]],
            ]
            return marks.map(([name, v]) => ({ name, y: Math.round(vhPx(v)) }))
          }
          const H = m.vh
          const s0 = m.pourCanvasTop - T.PHONE.pourStartAt * H
          const s1 = m.pourBottom - T.PHONE.waveFrom * H
          const marks: [string, number][] = [
            ['grind-start', m.rootTop],
            ['grind-mid', m.rootTop + (m.grindBottom - T.PHONE.grindEndAt * H) / 2],
            ['pour-start', s0],
            ['pour-mid', (s0 + s1) / 2],
            ['wave-start', s1],
            ['wave-mid', m.pourBottom - ((T.PHONE.waveFrom + T.PHONE.waveTo) / 2) * H],
            ['sip-start', m.pourBottom],
            ['sip-mid', m.pourBottom + (T.PHONE.sipLength / 2) * H],
            ['sip-end', m.pourBottom + T.PHONE.sipLength * H],
          ]
          return marks.map(([name, v]) => ({ name, y: Math.max(0, Math.round(v)) }))
        },
        boundaries() {
          const line = m.line
          // POUR → SIP: prvi skrol na kome ivica talasa (ili granica) pređe liniju headera
          const sipAt = () => {
            for (let i = 0; i <= 1000; i++) {
              const p = i / 1000
              if (phone) {
                const H = m.vh
                const scroll = m.pourBottom - (T.PHONE.waveFrom + (T.PHONE.waveTo - T.PHONE.waveFrom) * p) * H
                const startY = m.pourCanvasTop - scroll + kafa(177 + p * 15) * m.S
                if (m.pourBottom - scroll <= line || (p > 0 && waveTopMin(p, startY / H, m.W, H) <= line)) return scroll
              } else {
                const startY = m.pourFrameTop + kafa(177 + p * 15) * m.S
                const len = T.DESK.wave[1] - T.DESK.wave[0]
                if (p > 0 && waveTopMin(p, startY / m.vh, m.W, m.vh) <= line) return vhPx(T.DESK.wave[0] + p * len)
              }
            }
            return NaN
          }
          const r = (v: number) => Math.round(v)
          return phone
            ? [
                { from: 'grind', to: 'pour', y: r(m.pourTop - line) },
                { from: 'pour', to: 'sip', y: r(sipAt()) },
                { from: 'sip', to: 'page', y: r(m.sipBottom - line) },
              ]
            : [
                { from: 'grind', to: 'pour', y: r(vhPx(T.DESK.seam[1]) - line) },
                { from: 'pour', to: 'sip', y: r(sipAt()) },
                { from: 'sip', to: 'page', y: r(vhPx(T.DESK.end + 100) - line) },
              ]
        },
        nav: () => ({ grind: Math.round(navY('grind')), pour: Math.round(navY('pour')), sip: Math.round(navY('sip')) }),
        state: () => ({
          mode: phone ? 'flow' : 'pinned',
          ...now,
          chapter: lastChapter,
          clocks: { grind: clockA.current, pour: (phone ? clockB : clockA).current, sip: clockS.current },
          flags: flagsRef.current,
          metrics: { ...m },
          wave: wave.current?.inspect().phase,
        }),
      }
    }

    return () => {
      st.kill()
      ro.disconnect()
      window.clearTimeout(roTimer)
      cancelAnimationFrame(hashFrame)
      offNav()
      el.removeEventListener('focusin', onFocus)
      refreshRef.current = () => {}
      if (SEQ_DEBUG) delete window.__story
      if (trackEl) trackEl.style.transform = ''
      for (const c of cards) {
        c.style.transform = ''
        c.style.opacity = ''
        c.style.pointerEvents = ''
        delete c.dataset.flying
      }
      for (const id of IDS) {
        const w = words[id]
        if (w) w.style.transform = ''
        layers[id]?.style.removeProperty('opacity')
      }
    }
  }, [phone, clockA, clockB, clockS])

  const live: Live = {
    seq: { grind, pour, sip },
    clock: clocks,
    active: flags.active,
    defer: { grind: false, pour: flags.stage < 1, sip: flags.stage < 2 },
    steam: flags.steam,
    bags: flags.stage >= 3,
  }
  const waveEl = <Wave ref={wave} pourClip={pourClip} sipLens={sipLens} variant={phone ? 'phone' : 'desktop'} />
  const probeEl = (
    <div ref={probe} aria-hidden="true" className={`pointer-events-none invisible absolute top-0 left-0 w-px ${phone ? 'h-svh' : 'h-screen'}`} />
  )

  if (phone) {
    return (
      <div id="top" ref={root} className="story story--flow story--live" data-sip-live="0">
        {probeEl}
        <GrindLayer phone live={live} />
        <PourLayer phone live={live} clip={pourClip} />
        <SipLayer phone live={live} lens={sipLens} />
        <div className="story__wave-fixed">{waveEl}</div>
      </div>
    )
  }
  return (
    <div id="top" ref={root} className="story story--pinned story--live" data-sip-live="0" style={{ height: `${T.DESK.end + 100}vh` }}>
      {probeEl}
      <div className="story__stage">
        <div ref={track} className="story__track">
          <GrindLayer phone={false} live={live} />
          <PourLayer phone={false} live={live} clip={pourClip} />
        </div>
        <SipLayer phone={false} live={live} lens={sipLens} />
        {waveEl}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------------------------
// Mirna verzija (reduced motion): tri bloka sa posterima, statična ivica talasa, bez pare
// ---------------------------------------------------------------------------------------------
function StillStory({ phone }: { phone: boolean }) {
  const root = useRef<HTMLDivElement>(null)
  const pourClip = useRef<HTMLDivElement>(null)
  const sipLens = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    const el = root.current
    if (!el) return
    const layers = IDS.map((id) => el.querySelector<HTMLElement>(`#${id}`))
    const tops = { layers: [0, 0, 0], bottom: 0, line: 32 }
    const measure = () => {
      tops.layers = layers.map((l) => offsetWithin(l, null))
      tops.bottom = offsetWithin(el, null) + el.offsetHeight
      tops.line = (document.querySelector<HTMLElement>('header')?.offsetHeight ?? 64) / 2
      const S = el.querySelector<HTMLElement>('.story-canvas--grind')?.getBoundingClientRect().width ?? 0
      const set = (i: 1 | 2, host: HTMLElement | null, v: number) => {
        const box = el.querySelector<HTMLElement>(`.story-canvas--${IDS[i]}`)
        layers[i]?.style.setProperty('--table-y', `${(offsetWithin(box, host) + v * S).toFixed(1)}px`)
      }
      set(1, pourClip.current, T.FALLBACK_ANCHORS.pult_y)
      set(2, sipLens.current, T.FALLBACK_ANCHORS.sto_y)
    }
    let frame = 0
    let last = ''
    const update = () => {
      frame = 0
      const y = window.scrollY + tops.line
      let c: ActiveChapter = 'grind'
      if (y >= tops.bottom) c = 'page'
      else if (y >= tops.layers[2]) c = 'sip'
      else if (y >= tops.layers[1]) c = 'pour'
      if (c !== last) setActiveChapter((last = c))
    }
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update)
    }
    const onResize = () => {
      measure()
      onScroll()
    }
    measure()
    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onResize)
    const ro = new ResizeObserver(onResize)
    ro.observe(el)
    // strelice i tačkice skaču odmah na blok
    const off = registerChapterNavigator((id) => scrollToTarget(tops.layers[IDS.indexOf(id)], true))
    if (SEQ_DEBUG) {
      window.__story = {
        mode: 'still',
        points: () => IDS.map((id, i) => ({ name: `${id}-start`, y: tops.layers[i] })),
        boundaries: () => [
          { from: 'grind', to: 'pour', y: Math.round(tops.layers[1] - tops.line) },
          { from: 'pour', to: 'sip', y: Math.round(tops.layers[2] - tops.line) },
          { from: 'sip', to: 'page', y: Math.round(tops.bottom - tops.line) },
        ],
        nav: () => ({ grind: tops.layers[0], pour: tops.layers[1], sip: tops.layers[2] }),
        state: () => ({ mode: 'still', chapter: last, tops: { ...tops } }),
      }
    }
    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onResize)
      ro.disconnect()
      off()
      if (SEQ_DEBUG) delete window.__story
    }
  }, [phone])

  return (
    <div id="top" ref={root} className={`story story--still ${phone ? 'story--flow' : ''}`}>
      <GrindLayer phone={phone} live={null} />
      <PourLayer phone={phone} live={null} clip={pourClip} />
      <WaveEdgeStatic className="story__edge" />
      <SipLayer phone={phone} live={null} lens={sipLens} />
    </div>
  )
}

export function Story() {
  const reduced = useReducedMotion()
  const phone = useIsPhone()
  if (reduced) return <StillStory phone={phone} />
  return <LiveStory key={phone ? 'flow' : 'pinned'} phone={phone} />
}
