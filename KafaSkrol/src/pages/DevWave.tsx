// Dev harness za talas i paru (Z6), samo u `npm run dev` na /dev/wave.
// Terakota POUR sloj sa lažnom linijom kafe u bokalu (na startY iz kafa_y) je iznad braon SIP sloja sa
// siluetom šolje i natpisom. Skrol vodi progress talasa (ScrollTrigger), a para stoji preko obe pozadine,
// u omotačima kojima se menja opacity, kao u priči (klasa steam-host).
//
// Parametri: ?p=0.3 (stalan progress, bez skrola) · ?steam=0 (para bez fajlova: ready = false) · ?panel=0
//            ?wave=0 (bez talasa, osnova za merenje vremena kadra)
// U konzoli: __devWave.scrollTo(p), __devWave.stats(), __devWave.inspect()
import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { media } from '../content/media'
import type { SteamMedia } from '../content/types'
import { setActiveChapter } from '../lib/chapterStore'
import { getLenis, ScrollTrigger } from '../lib/motion'
import { useIsPhone, useReducedMotion } from '../lib/useMedia'
import { Steam } from '../story/Steam'
import { Wave, WaveEdgeStatic, type WaveHandle, type WaveState } from '../story/Wave'

declare global {
  interface Window {
    __devWave?: {
      scrollTo(p: number): Promise<number>
      stats(): { calls: number; avgSetMs: number; maxSetMs: number; p: number; startY: number }
      resetStats(): void
      inspect(): WaveState | null
      steam(): { which: string; paused: boolean | null; src: string }[]
    }
  }
}

const params = new URLSearchParams(window.location.search)
const FIXED_P = params.has('p') ? Math.min(1, Math.max(0, Number(params.get('p')) || 0)) : null
const NO_STEAM = params.get('steam') === '0'
const SHOW_PANEL = params.get('panel') !== '0'
/** ?wave=0: bez talasa (osnova za poređenje vremena kadra) */
const NO_WAVE = params.get('wave') === '0'

const clamp01 = (v: number) => Math.min(1, Math.max(0, v))
const smooth = (a: number, b: number, v: number) => {
  const t = clamp01((v - a) / (b - a))
  return t * t * (3 - 2 * t)
}

/** Para bez fajlova (provera: nema zahteva ni 404). */
const steamOff = (m: SteamMedia): SteamMedia => ({ ...m, ready: false })

type Frame = { W: number; H: number; S: number; top: number; axis: number }

function frameFor(W: number, H: number, phone: boolean): Frame {
  // desktop: S = visina scene, osa na 58 % širine; telefon: S = min(100vw, 62svh), ispod headera
  if (!phone) return { W, H, S: H, top: 0, axis: W * 0.58 }
  const S = Math.min(W, H * 0.62)
  return { W, H, S, top: 64, axis: W * 0.5 }
}

export default function DevWave() {
  const reduced = useReducedMotion()
  const phone = useIsPhone()
  return reduced ? <ReducedView /> : <LiveView key={phone ? 'phone' : 'desktop'} phone={phone} />
}

function LiveView({ phone }: { phone: boolean }) {
  const scene = useRef<HTMLDivElement>(null)
  const range = useRef<HTMLDivElement>(null)
  const pourClip = useRef<HTMLDivElement>(null)
  const sipLens = useRef<HTMLDivElement>(null)
  const coffee = useRef<HTMLDivElement>(null)
  const pourSteam = useRef<HTMLDivElement>(null)
  const sipSteam = useRef<HTMLDivElement>(null)
  const panel = useRef<HTMLPreElement>(null)
  const wave = useRef<WaveHandle>(null)
  const [frame, setFrame] = useState<Frame>(() => frameFor(window.innerWidth, window.innerHeight, phone))
  const [steamOn, setSteamOn] = useState({ pour: true, sip: false })
  const kafa = useRef<number[]>([0.84])
  /** ponovo primeni poslednji p (npr. kad stigne seq.json) */
  const reapply = useRef<() => void>(() => {})
  const stats = useRef({ calls: 0, total: 0, max: 0, p: 0, startY: 0 })
  const frameRef = useRef(frame)
  useLayoutEffect(() => {
    frameRef.current = frame
  }, [frame])

  // kafa_y za G177–G192 iz pour/seq.json (isti izvor koji koristi Story)
  useEffect(() => {
    let cancelled = false
    fetch(media.seq.pour.manifest)
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => {
        const v = j?.anchors?.kafa_y?.values
        if (!cancelled && Array.isArray(v) && v.length) {
          kafa.current = v
          reapply.current()
        }
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])

  // mere scene samo pri promeni veličine
  useLayoutEffect(() => {
    const el = scene.current
    if (!el) return
    const ro = new ResizeObserver(([e]) => {
      const { width, height } = e.contentRect
      setFrame(frameFor(width, height, phone))
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [phone])

  useEffect(() => {
    const jugTop = () => frameRef.current.top + frameRef.current.S * 0.56
    let last = { pour: true, sip: false }

    const apply = (p: number) => {
      const f = frameRef.current
      const k = kafa.current
      const g = p * (k.length - 1)
      const i = Math.min(Math.floor(g), k.length - 1)
      const ky = k[i] + (k[Math.min(i + 1, k.length - 1)] - k[i]) * (g - i)
      const startY = f.top + ky * f.S
      const t0 = performance.now()
      wave.current?.set(p, startY)
      const dt = performance.now() - t0
      const s = stats.current
      s.calls++
      s.total += dt
      s.max = Math.max(s.max, dt)
      s.p = p
      s.startY = startY
      if (coffee.current) coffee.current.style.transform = `translate3d(0, ${(startY - jugTop()).toFixed(1)}px, 0)`
      if (pourSteam.current) pourSteam.current.style.opacity = (1 - smooth(0.45, 0.85, p)).toFixed(3)
      // kao u priči: para u SIP-u počinje od S20, a to je posle talasa (S1–S16), pa ovde tek na p = 1
      if (sipSteam.current) sipSteam.current.style.opacity = p >= 1 ? '1' : '0'
      const next = { pour: p < 0.95, sip: p >= 1 }
      if (next.pour !== last.pour || next.sip !== last.sip) {
        last = next
        setSteamOn(next)
      }
      setActiveChapter(p < 0.55 ? 'pour' : 'sip')
      if (panel.current) {
        panel.current.textContent =
          `p ${p.toFixed(3)}  startY ${startY.toFixed(1)}  ${phone ? 'phone' : 'desktop'}\n` +
          `set() ${(s.total / Math.max(s.calls, 1)).toFixed(3)} ms avg · ${s.max.toFixed(2)} max · ${s.calls}`
      }
    }

    let st: ScrollTrigger | null = null
    reapply.current = () => apply(FIXED_P ?? st?.progress ?? 0)
    if (FIXED_P !== null) {
      apply(FIXED_P)
    } else if (range.current) {
      st = ScrollTrigger.create({
        trigger: range.current,
        start: 'top top',
        end: 'bottom top',
        onUpdate: (self) => apply(self.progress),
        onRefresh: (self) => {
          wave.current?.measure()
          apply(self.progress)
        },
      })
      apply(st.progress)
    }

    window.__devWave = {
      async scrollTo(p: number) {
        const el = range.current
        if (!el) return 0
        const r = el.getBoundingClientRect()
        const y = Math.round(r.top + window.scrollY + clamp01(p) * r.height)
        const lenis = getLenis()
        if (lenis) lenis.scrollTo(y, { immediate: true, force: true })
        else window.scrollTo(0, y)
        ScrollTrigger.update()
        await new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(res)))
        return y
      },
      stats() {
        const s = stats.current
        return { calls: s.calls, avgSetMs: s.total / Math.max(s.calls, 1), maxSetMs: s.max, p: s.p, startY: s.startY }
      },
      resetStats() {
        stats.current = { ...stats.current, calls: 0, total: 0, max: 0 }
      },
      inspect: () => wave.current?.inspect() ?? null,
      steam: () =>
        [...document.querySelectorAll<HTMLVideoElement>('.steam video')].map((v) => ({
          which: v.closest<HTMLElement>('[data-steam]')?.dataset.steam ?? '?',
          paused: v.paused,
          src: v.currentSrc,
        })),
    }
    return () => {
      st?.kill()
      reapply.current = () => {}
      delete window.__devWave
    }
  }, [phone])

  const { S, top, axis } = frame
  const px = (v: number) => `${v.toFixed(1)}px`
  const pourSrc = NO_STEAM ? steamOff(media.steam.pour) : undefined
  const sipSrc = NO_STEAM ? steamOff(media.steam.sip) : undefined
  const len = phone ? '80svh' : '100svh'

  return (
    <main id="main" className="bg-pp-ink-deep">
      {/* sticky scena + 40svh pre talasa + talas + 60svh posle */}
      <div className="relative" style={{ height: `calc(100svh + 40svh + ${len} + 60svh)` }}>
        <div ref={range} aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-[40svh]" style={{ height: len }} />
        <div ref={scene} className="sticky top-0 h-svh overflow-hidden">
          {/* ---------- SIP (ispod) ---------- */}
          <section data-chapter="sip" aria-label="SIP" className="layer-sip absolute inset-0 text-text">
            <div ref={sipLens} className="layer-sip__lens absolute inset-0 bg-bg">
              <div className="absolute inset-x-0 bottom-0 bg-floor" style={{ top: px(top + S * 0.78) }} />
              {/* silueta šolje */}
              <div className="absolute" style={{ left: px(axis - S * 0.15), top: px(top + S * 0.44), width: px(S * 0.3), height: px(S * 0.36) }}>
                <div className="absolute inset-0 rounded-b-[28%] rounded-t-[6px] bg-placeholder" />
                <div className="absolute rounded-full border-[10px] border-placeholder" style={{ right: px(-S * 0.08), top: '18%', width: px(S * 0.13), height: '46%' }} />
                <div className="absolute inset-x-0 top-0 h-[9%] rounded-[50%] bg-placeholder-line" />
              </div>
              <div className="absolute rounded-[50%] bg-pp-ink-deep/35 blur-md" style={{ left: px(axis - S * 0.18), top: px(top + S * 0.79), width: px(S * 0.36), height: px(S * 0.03) }} />
              <div className="absolute left-gutter max-w-[22rem] desk:left-inset" style={{ top: phone ? px(top + S + 24) : '34%' }}>
                <p className="m-0 type-eyebrow text-text">Section 3</p>
                <h2 className="m-0 mt-s3 type-display text-chapter leading-[0.92] text-text">Sip</h2>
                <p className="m-0 mt-s4 text-body text-muted">Kroz talas se vidi živ SIP sloj, a posle p = 1 je čist.</p>
              </div>
            </div>
            <div ref={sipSteam} data-steam="sip" className="steam-host absolute" style={{ left: px(axis - S * 0.24), top: px(top + S * 0.12), width: px(S * 0.48), opacity: 0 }}>
              <Steam which="sip" active={steamOn.sip} className="w-full" source={sipSrc} />
            </div>
          </section>

          {/* ---------- POUR (iznad, seče ga talas) ---------- */}
          <section data-chapter="pour" aria-label="POUR" className="layer-pour absolute inset-0 text-text">
            <div ref={pourClip} className="layer-pour__clip absolute inset-0 bg-bg">
              <div className="absolute inset-x-0 bottom-0 bg-surface" style={{ top: px(top + S * 0.95) }} />
              {/* V60 (trapez) */}
              <div
                className="absolute bg-placeholder [clip-path:polygon(0_0,100%_0,66%_100%,34%_100%)]"
                style={{ left: px(axis - S * 0.13), top: px(top + S * 0.42), width: px(S * 0.26), height: px(S * 0.12) }}
              />
              {/* bokal sa lažnom linijom kafe na startY */}
              <div
                className="absolute overflow-hidden rounded-b-[18%] rounded-t-[8px] bg-placeholder/70"
                style={{ left: px(axis - S * 0.12), top: px(top + S * 0.56), width: px(S * 0.24), height: px(S * 0.39) }}
              >
                <div ref={coffee} className="absolute inset-x-0 top-0 h-full bg-[#4a2c1d]">
                  <div className="h-[2px] bg-[#c48a57]" />
                </div>
              </div>
              <div className="absolute left-gutter max-w-[22rem] desk:left-inset" style={{ top: phone ? px(top + S + 24) : '22%' }}>
                <p className="m-0 type-eyebrow text-text">Section 2</p>
                <h2 className="m-0 mt-s3 type-display text-chapter leading-[0.92] text-text">Pour</h2>
                <p className="m-0 mt-s4 text-body text-muted">Talas kreće sa linije kafe u bokalu (kafa_y).</p>
              </div>
              <div ref={pourSteam} data-steam="pour" className="steam-host absolute" style={{ left: px(axis - S * 0.27), top: px(top + S * 0.06), width: px(S * 0.54) }}>
                <Steam which="pour" active={steamOn.pour} className="w-full" source={pourSrc} />
              </div>
            </div>
          </section>

          {!NO_WAVE && <Wave ref={wave} pourClip={pourClip} sipLens={sipLens} variant={phone ? 'phone' : 'desktop'} />}
        </div>
      </div>
      <section className="flex h-[60svh] items-center justify-center bg-pp-cream text-pp-ink">
        <p className="m-0 type-label">posle priče</p>
      </section>
      {SHOW_PANEL && (
        <pre
          ref={panel}
          className="pointer-events-none fixed bottom-s3 left-s3 z-30 m-0 rounded-sm bg-pp-ink-deep/85 px-s3 py-s2 font-label text-micro whitespace-pre text-pp-cream-light"
        />
      )}
    </main>
  )
}

/** Reduced motion: dva bloka sa posterima/siluetama, između njih statična ivica, bez pare i talasa. */
function ReducedView() {
  useEffect(() => {
    setActiveChapter('pour')
  }, [])
  return (
    <main id="main">
      <section data-chapter="pour" aria-label="POUR" className="relative flex min-h-svh items-center bg-bg px-gutter text-text desk:pl-inset">
        <div className="max-w-[22rem]">
          <p className="m-0 type-eyebrow">Section 2</p>
          <h2 className="m-0 mt-s3 type-display text-chapter leading-[0.92]">Pour</h2>
          <p className="m-0 mt-s4 text-body text-muted">Reduced motion: nema talasa ni pare, samo rez sa statičnom ivicom.</p>
        </div>
        <div className="absolute bottom-0 left-[58%] h-[40svh] w-[24svh] -translate-x-1/2 rounded-t-[8px] bg-placeholder/70" />
        <div className="absolute top-[20svh] left-[58%] w-[50svh] -translate-x-1/2" data-steam="pour">
          <Steam which="pour" active className="w-full" />
        </div>
      </section>
      <WaveEdgeStatic />
      <section data-chapter="sip" aria-label="SIP" className="relative flex min-h-svh items-center bg-bg px-gutter text-text desk:pl-inset">
        <div className="max-w-[22rem]">
          <p className="m-0 type-eyebrow">Section 3</p>
          <h2 className="m-0 mt-s3 type-display text-chapter leading-[0.92]">Sip</h2>
        </div>
        <div className="absolute top-[30svh] left-[58%] h-[36svh] w-[30svh] -translate-x-1/2 rounded-b-[28%] bg-placeholder" />
      </section>
    </main>
  )
}
