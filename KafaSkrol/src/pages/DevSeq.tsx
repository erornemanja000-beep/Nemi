// Harness za sekvence (samo dev, /dev/seq). GRIND i POUR scena su jedna ispod druge, bez razmaka, na
// zajedničkom satu G. Skrol je linearno vezan za G1–G192 po segmentima iz plana (Interfejs 2):
// GRIND pin → prelaz (obe scene, šav) → POUR pin → talas. Panel dole levo: G, nivo i brojači.
// Desktop brojevi su iz src/story/timeline.ts (Z12). Telefon u priči nema šav (odluka direktora 2),
// pa telefonski čvorovi ovde važe samo za harness (proveravaju zajednički sat na nivou m).
// Za Playwright: window.__devSeq.scrollToG(g) i window.__devSeq.state().
// Reduced motion i Save-Data: dva statična bloka sa posterima, bez zahteva za kadrove.
import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { chapters } from '../content/chapters'
import { media } from '../content/media'
import { useLang } from '../i18n/LangContext'
import { ScrollTrigger, scrollToTarget } from '../lib/motion'
import { createClock, useSequence, type FrameRequest, type Sequence } from '../lib/sequence'
import { useIsPhone, useReducedMotion, useSaveData } from '../lib/useMedia'
import { SeqCanvas } from '../story/SeqCanvas'
import { DESK_G, LOAD_PLAN, RETAIN, type Knot } from '../story/timeline'

/** [vh (telefon: svh) od vrha, G na početku segmenta]; poslednji red je kraj talasa */
const KNOTS: Record<'desktop' | 'phone', readonly Knot[]> = {
  desktop: DESK_G,
  phone: [[0, 1], [150, 65], [250, 97], [430, 177], [510, 192]],
}

function gAt(knots: readonly Knot[], y: number) {
  for (let i = 0; i < knots.length - 1; i++) {
    const [y0, g0] = knots[i]
    const [y1, g1] = knots[i + 1]
    if (y <= y1 || i === knots.length - 2) return g0 + ((Math.min(Math.max(y, y0), y1) - y0) / (y1 - y0)) * (g1 - g0)
  }
  return knots[0][1]
}

function yAt(knots: readonly Knot[], g: number) {
  for (let i = 0; i < knots.length - 1; i++) {
    const [y0, g0] = knots[i]
    const [y1, g1] = knots[i + 1]
    if (g <= g1 || i === knots.length - 2) return y0 + ((Math.min(Math.max(g, g0), g1) - g0) / (g1 - g0)) * (y1 - y0)
  }
  return 0
}

/** 0…1: koliko je POUR scena izašla preko GRIND scene (segment prelaza) */
function seamAt(knots: readonly Knot[], y: number) {
  const [a] = knots[1]
  const [b] = knots[2]
  return Math.min(Math.max((y - a) / (b - a), 0), 1)
}

// učitavanje u delovima (storyboard 8, LOAD_PLAN iz timeline.ts), posle `load`; veći broj ide pre.
// Harness traži sve delove odmah (bez pragova skrola), redom prioriteta.
type Plan = readonly (readonly [FrameRequest, number])[]
const planFor = (id: 'grind' | 'pour'): Plan => LOAD_PLAN.filter((s) => s.id === id).map((s) => [s.req, s.priority] as const)
const GRIND_PLAN = planFor('grind')
const POUR_PLAN = planFor('pour')

function useLoadPlan(seq: Sequence | null, plan: Plan) {
  useEffect(() => {
    if (!seq) return
    const go = () => {
      for (const [req, priority] of plan) void seq.request(req, priority)
    }
    if (document.readyState === 'complete') {
      go()
      return
    }
    window.addEventListener('load', go, { once: true })
    return () => window.removeEventListener('load', go)
  }, [seq, plan])
}

type DevSeqApi = {
  scrollToG: (g: number) => void
  state: () => { target: number; current: number; phone: boolean; drawn: Record<'grind' | 'pour', number | null> }
}

declare global {
  interface Window {
    __devSeq?: DevSeqApi
  }
}

const drawnG = (id: 'grind' | 'pour') => {
  const g = document.querySelector<HTMLCanvasElement>(`[data-seq-canvas="${id}"] canvas`)?.dataset.g
  return g ? Number(g) : null
}

// S i osa x (storyboard 1): desktop S = 100svh, osa na 58 % širine; telefon S = min(100vw, 62svh), osa na sredini.
// GRIND kvadrat je dnom uz granicu scena (produžetak 0,25 S ispod nje seče overflow), POUR uz vrh.
const BOX = 'absolute left-[calc(var(--axis)-var(--s)/2)] w-(--s)'

export default function DevSeq() {
  const { tx } = useLang()
  const phone = useIsPhone()
  const reduced = useReducedMotion()
  const saveData = useSaveData()
  const still = reduced || saveData
  const grind = useSequence('grind')
  const pour = useSequence('pour')
  const [clock] = useState(() => createClock([], { retain: RETAIN }))
  const track = useRef<HTMLDivElement>(null)
  const stage = useRef<HTMLDivElement>(null)
  const panel = useRef<HTMLPreElement>(null)
  const knots = KNOTS[phone ? 'phone' : 'desktop']

  useLoadPlan(grind, GRIND_PLAN)
  useLoadPlan(pour, POUR_PLAN)

  useEffect(() => {
    clock.start()
    return () => clock.stop()
  }, [clock])

  // skrol → G i pomeranje scena (samo transform)
  useEffect(() => {
    const el = track.current
    const st = stage.current
    if (still || !el || !st) return
    const total = knots[knots.length - 1][0]
    const apply = (p: number) => {
      const y = p * total
      clock.set(gAt(knots, y))
      st.style.transform = `translate3d(0, ${-seamAt(knots, y) * 50}%, 0)`
    }
    const trigger = ScrollTrigger.create({
      trigger: el,
      start: 'top top',
      end: 'bottom bottom',
      onUpdate: (self) => apply(self.progress),
      onRefresh: (self) => apply(self.progress),
    })
    apply(trigger.progress)
    window.__devSeq = {
      scrollToG: (g) => scrollToTarget(trigger.start + (yAt(knots, g) / total) * (trigger.end - trigger.start), true),
      state: () => ({ target: clock.target, current: clock.current, phone, drawn: { grind: drawnG('grind'), pour: drawnG('pour') } }),
    }
    return () => {
      trigger.kill()
      delete window.__devSeq
      st.style.transform = ''
    }
  }, [still, knots, clock, phone])

  // panel (10 puta u sekundi, van petlje animacije)
  useEffect(() => {
    const id = window.setInterval(() => {
      const el = panel.current
      if (!el) return
      const stats = window.__seqStats ?? {}
      const line = (k: 'grind' | 'pour') => {
        const s = stats[k]
        if (!s) return `${k.padEnd(5)}  ${still ? 'samo poster' : 'nema sekvence'}`
        const g = drawnG(k)
        return `${k.padEnd(5)}  nivo ${s.set}  zatraženo ${s.requested}/${s.count}  učitano ${s.loaded}  dekodirano ${s.decoded} (max ${s.decodedMax})  greške ${s.failed}  crta ${g ?? '–'}`
      }
      el.textContent = [
        `G ${clock.target.toFixed(1)} → ${clock.current.toFixed(1)}   ${phone ? 'telefon' : 'desktop'}   DPR ${window.devicePixelRatio}${reduced ? '   reduced motion' : ''}${saveData ? '   Save-Data' : ''}`,
        line('grind'),
        line('pour'),
      ].join('\n')
    }, 100)
    return () => window.clearInterval(id)
  }, [clock, phone, reduced, saveData, still])

  const level = phone ? 'm' : 'd'
  const grindPoster = { src: media.seq.grind.poster[level].src, alt: tx(chapters.items[0].alt), priority: true }
  const pourPoster = { src: media.seq.pour.poster[level].src, alt: tx(chapters.items[1].alt) }

  const panelEl = (
    <pre
      ref={panel}
      aria-hidden="true"
      className="pointer-events-none fixed bottom-2 left-2 z-30 m-0 max-w-[calc(100vw-1rem)] overflow-hidden whitespace-pre-wrap rounded-sm bg-pp-ink-deep/85 p-2 text-[11px] leading-snug text-pp-cream-light [font-family:ui-monospace,monospace]"
    />
  )

  if (still) {
    return (
      <main id="main">
        <h1 className="sr-only">DevSeq</h1>
        <section data-chapter="grind" className="grid h-svh place-items-center bg-bg">
          <SeqCanvas seq={null} clock={null} poster={grindPoster} className="h-[80svh] w-[90vw]" />
        </section>
        <section data-chapter="pour" className="grid h-svh place-items-center bg-bg">
          <SeqCanvas seq={null} clock={null} poster={pourPoster} className="h-[80svh] w-[90vw]" />
        </section>
        {panelEl}
      </main>
    )
  }

  return (
    <main id="main" className="[--axis:50%] [--s:min(100vw,62svh)] desk:[--axis:58%] desk:[--s:100svh]">
      <h1 className="sr-only">DevSeq</h1>
      {/* desktop: dužina iz timeline.ts (poslednji čvor sata G + 100 vh scene); telefon: čvorovi harness-a */}
      <div ref={track} className="h-[610svh] desk:h-(--track-h)" style={{ '--track-h': `${DESK_G[DESK_G.length - 1][0] + 100}svh` } as CSSProperties}>
        <div className="sticky top-0 h-svh overflow-hidden">
          <div ref={stage} className="will-change-transform">
            <section id="dev-grind" data-chapter="grind" className="relative h-svh overflow-hidden bg-bg">
              <SeqCanvas seq={grind} clock={clock} poster={grindPoster} className={`${BOX} top-[calc(100%-var(--s))]`} />
            </section>
            <section id="dev-pour" data-chapter="pour" className="relative h-svh overflow-hidden bg-bg">
              <SeqCanvas seq={pour} clock={clock} poster={pourPoster} className={`${BOX} top-0`} />
            </section>
          </div>
        </div>
      </div>
      {panelEl}
    </main>
  )
}
