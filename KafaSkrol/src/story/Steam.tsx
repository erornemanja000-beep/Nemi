// Para iznad bokala (POUR) i šolje (SIP). Z6, plan Interfejs 6, odluka direktora 4.
//
// - Izvori su iz media.ts: webm prvi, mp4 drugi; A (`pour`) i B (`sip`), nivo d/m po prelomnoj tački.
// - <video> muted, playsInline, loop, preload="none", aria-hidden, mix-blend-mode: screen (crna je čista).
// - Pušta se samo kad je `active`, kad je u ekranu, kad je kartica vidljiva, van reduced motion,
//   bez Save-Data i kad je medij `ready`. Bez `ready` (ili u reduced/Save-Data) ne crta ništa i ne šalje
//   nijedan zahtev. Sa preload="none" ni prikazan video ne traži fajl dok prvi put ne treba da svira.
// - Ako pregledač odbije play() (NotAllowedError, npr. iOS u režimu štednje baterije), prelazi na
//   WebP kadrove iz `frames` (30 kadrova petlje) na malom platnu, sa pretapanjem između kadrova.
// - Opacity menja Story na omotaču. Taj omotač mora imati klasu `steam-host` (vidi wave.css).
// - Kad ne svira (nije aktivna, nije u ekranu ili je potpuno isečena), para se ne vidi
//   (visibility: hidden). Story zato prvo spusti opacity omotača, pa tek onda `active = false`.
import { useEffect, useRef, useState } from 'react'
import { media } from '../content/media'
import type { SteamMedia } from '../content/types'
import { useIsPhone, useReducedMotion, useSaveData } from '../lib/useMedia'
import './wave.css'

type SteamProps = {
  which: 'pour' | 'sip'
  active: boolean
  className?: string
  /** Samo za dev harness: zamena za media.steam[which] (npr. `ready: false`). */
  source?: SteamMedia
}

export function Steam({ which, active, className = '', source }: SteamProps) {
  const m = source ?? media.steam[which]
  const reduced = useReducedMotion()
  const saveData = useSaveData()
  const phone = useIsPhone()
  if (!m.ready || reduced || saveData) return null
  return <SteamPlayer key={phone ? 'm' : 'd'} m={m} level={phone ? 'm' : 'd'} active={active} className={className} />
}

type PlayerProps = { m: SteamMedia; level: 'd' | 'm'; active: boolean; className: string }

function SteamPlayer({ m, level, active, className }: PlayerProps) {
  const rootRef = useRef<HTMLDivElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const activeRef = useRef(active)
  const syncRef = useRef<() => void>(() => {})
  const [mode, setMode] = useState<'video' | 'frames'>('video')
  const frames = m.frames

  // Odluka „svira ili ne" na jednom mestu: aktivno, u ekranu, kartica vidljiva.
  useEffect(() => {
    const root = rootRef.current
    const videoEl = videoRef.current
    if (!root) return
    let visible = false
    let player: FramePlayer | null = null

    const want = () => activeRef.current && visible && document.visibilityState === 'visible'

    const sync = () => {
      const on = want()
      // kad ne svira, koren je visibility: hidden (wave.css), pa sloj videa izlazi iz kompozitora;
      // ugašen video ispod maske talasa inače košta svaki kadar (izmereno u Z6)
      root.dataset.on = on ? '1' : '0'
      if (mode === 'frames') {
        if (!player && on && frames && canvasRef.current) player = createFramePlayer(canvasRef.current, frames, level)
        player?.run(on)
        return
      }
      const video = videoRef.current
      if (!video) return
      if (on && video.paused) {
        video.muted = true
        video.play().catch((err: unknown) => {
          const name = err instanceof DOMException ? err.name : ''
          // AbortError: pauza je stigla pre nego što je play() krenuo, to je u redu
          if (name === 'AbortError') return
          if (name === 'NotAllowedError' && frames) {
            setMode('frames')
            return
          }
          console.warn('[steam] video se ne pušta:', name || err)
        })
      } else if (!on && !video.paused) {
        video.pause()
      }
    }
    syncRef.current = sync

    const io = new IntersectionObserver(
      (entries) => {
        visible = entries[entries.length - 1].isIntersecting
        sync()
      },
      { rootMargin: '10% 0px' },
    )
    io.observe(root)
    document.addEventListener('visibilitychange', sync)
    return () => {
      io.disconnect()
      document.removeEventListener('visibilitychange', sync)
      syncRef.current = () => {}
      player?.dispose()
      videoEl?.pause()
    }
  }, [mode, frames, level])

  // `active` menja Story; ne pravi novi IntersectionObserver, samo ponovo odlučuje
  useEffect(() => {
    activeRef.current = active
    syncRef.current()
  }, [active])

  // muted kao atribut (ne samo svojstvo), jer ga neki pregledači traže za puštanje bez dodira
  useEffect(() => {
    const v = videoRef.current
    if (v) {
      v.defaultMuted = true
      v.setAttribute('muted', '')
    }
  }, [mode])

  const sources = m.sources[level]
  return (
    <div ref={rootRef} className={`steam ${className}`} data-on="0" style={{ aspectRatio: `${m.width} / ${m.height}` }} aria-hidden="true">
      {mode === 'video' ? (
        <video
          ref={videoRef}
          className="steam__media"
          width={m.width}
          height={m.height}
          muted
          playsInline
          loop
          preload="none"
          disablePictureInPicture
          tabIndex={-1}
          aria-hidden="true"
        >
          {sources.map((s) => (
            <source key={s.src} src={s.src} type={s.type} />
          ))}
        </video>
      ) : (
        <canvas ref={canvasRef} className="steam__media" />
      )}
    </div>
  )
}

// ---------- Rezerva: WebP kadrovi petlje na platnu ----------
type FramePlayer = { run(on: boolean): void; dispose(): void }

/** Petlja traje kao video (5 s); 30 kadrova je svaki 4. kadar, pa se susedni pretapaju. */
const LOOP_SECONDS = 5
const DRAW_FPS = 15

function createFramePlayer(canvas: HTMLCanvasElement, frames: NonNullable<SteamMedia['frames']>, level: 'd' | 'm'): FramePlayer {
  const scale = level === 'm' ? 0.5 : 0.75
  canvas.width = Math.round(frames.width * scale)
  canvas.height = Math.round(frames.height * scale)
  const ctx = canvas.getContext('2d')
  const images: (HTMLImageElement | null)[] = new Array(frames.count).fill(null)
  let loading = false
  let disposed = false
  let raf = 0
  let lastDraw = 0
  let t0 = 0

  const url = (i: number) => `${frames.base}/${String(i).padStart(3, '0')}.webp`

  async function load() {
    if (loading) return
    loading = true
    // po 4 zahteva, redom, da prvi kadrovi stignu prvi
    let next = 0
    const worker = async () => {
      while (!disposed && next < frames.count) {
        const i = next++
        const img = new Image()
        img.src = url(i)
        try {
          await img.decode()
          images[i] = img
        } catch {
          // kadar koji ne stigne se preskače (crta se najbliži učitani)
        }
      }
    }
    await Promise.all([worker(), worker(), worker(), worker()])
  }

  const nearest = (i: number) => {
    for (let d = 0; d < frames.count; d++) {
      const img = images[(i - d + frames.count) % frames.count]
      if (img) return img
    }
    return null
  }

  function draw(now: number) {
    raf = requestAnimationFrame(draw)
    if (now - lastDraw < 1000 / DRAW_FPS - 2) return
    lastDraw = now
    if (!ctx) return
    const pos = (((now - t0) / 1000) % LOOP_SECONDS) / LOOP_SECONDS * frames.count
    const i = Math.floor(pos)
    const a = nearest(i)
    const b = nearest((i + 1) % frames.count)
    if (!a) return
    ctx.globalAlpha = 1
    ctx.drawImage(a, 0, 0, canvas.width, canvas.height)
    if (b && b !== a) {
      ctx.globalAlpha = pos - i
      ctx.drawImage(b, 0, 0, canvas.width, canvas.height)
    }
  }

  return {
    run(on) {
      if (on && !raf) {
        void load()
        if (!t0) t0 = performance.now()
        raf = requestAnimationFrame(draw)
      } else if (!on && raf) {
        cancelAnimationFrame(raf)
        raf = 0
      }
    },
    dispose() {
      disposed = true
      cancelAnimationFrame(raf)
      raf = 0
    },
  }
}
