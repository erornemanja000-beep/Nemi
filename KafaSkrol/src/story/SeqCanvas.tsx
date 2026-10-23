// Platno sekvence (plan, Interfejs 5). Kutija razmere full.W : full.H; poster i platno stoje na mestu
// isečka (crop), pa zamena postera prvim kadrom nema skoka.
// - Poster <img> je ispod platna dok se ne nacrta prvi kadar (GRIND: poster = G1, isti URL kao
//   predučitavanje u index.html). Posle toga ostaje u DOM-u providan, zbog alt teksta; platno je aria-hidden.
// - Crta samo dok je u ekranu (IntersectionObserver), kadar daje zajednički sat (createClock).
//   Veličina se pamti iz ResizeObserver-a; u petlji se ne čita layout.
// - DPR najviše 2, i nikad više piksela nego što fajl nivoa ima.
// - Reduced motion i Save-Data: samo poster, bez platna i bez zahteva za kadrove.
// - `active` (Story, Z12): platno je u ekranu, ali pokriveno (SIP ispod POUR-a pre talasa, POUR isečen
//   posle talasa), pa ne crta i ne traži kadrove. IntersectionObserver ne vidi pokrivenost.
// - `deferPoster` (Story, Z12): poster se još ne traži (prvi ekran ostaje u budžetu); umesto njega
//   stoji prazna kutija sa istim alt tekstom (role="img").
// - Bez `geometry` i bez manifesta (reduced motion, Save-Data, pre seq.json) poster popunjava kutiju
//   (object-contain). Zato Story prosleđuje `geometry` (isti brojevi kao full i crop u seq.json).
import { useEffect, useRef, type CSSProperties } from 'react'
import { SEQ_DEBUG, type Clock, type SeqGeometry, type Sequence } from '../lib/sequence'
import { useReducedMotion, useSaveData } from '../lib/useMedia'

export type SeqPoster = {
  src: string
  alt: string
  /** prvi ekran (LCP): eager + fetchpriority high */
  priority?: boolean
}

type Props = {
  /** null dok seq.json ne stigne, i uvek u reduced motion / Save-Data */
  seq: Sequence | null
  clock: Clock | null
  poster: SeqPoster
  /** pun kadar i isečak dok seq.json ne stigne (i u reduced motion); posle važi seq.manifest */
  geometry?: SeqGeometry
  /** poziva se jednom, kad platno prvi put zameni poster */
  onFirstFrame?: () => void
  /** false: platno ne crta (pokriveno drugim slojem); podrazumevano true */
  active?: boolean
  /** true: poster se još ne učitava (vidi gore) */
  deferPoster?: boolean
  className?: string
  style?: CSSProperties
}

const pct = (v: number) => `${v * 100}%`

export function SeqCanvas({ seq, clock, poster, geometry, onFirstFrame, active = true, deferPoster = false, className = '', style }: Props) {
  const reduced = useReducedMotion()
  const saveData = useSaveData()
  const live = !reduced && !saveData && seq !== null && clock !== null
  // seq.json je merodavan čim stigne; `geometry` važi samo do tada (poster na pravom mestu pre manifesta)
  const geo = seq?.manifest ?? geometry ?? null

  useEffect(() => {
    if (!SEQ_DEBUG || !geometry || !seq) return
    const m = seq.manifest
    const a = [geometry.full.W, geometry.full.H, geometry.crop.x0, geometry.crop.y0, geometry.crop.w, geometry.crop.h]
    const b = [m.full.W, m.full.H, m.crop.x0, m.crop.y0, m.crop.w, m.crop.h]
    if (a.some((v, i) => Math.abs(v - b[i]) > 1e-6)) {
      console.warn(`[seq] ${seq.id}: geometry iz media.ts se razlikuje od seq.json (poster će skočiti); uskladiti media.ts`)
    }
  }, [geometry, seq])
  const rootRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const posterRef = useRef<HTMLImageElement>(null)
  const firstFrame = useRef(onFirstFrame)
  /** poster je sakriven ispod nacrtanog platna (važi i za poster koji se pojavi kasnije, deferPoster) */
  const covered = useRef(false)
  const activeRef = useRef(active)
  /** efekt platna menja ovo, da `active` ne pravi platno iznova */
  const onActive = useRef<() => void>(() => {})

  useEffect(() => {
    firstFrame.current = onFirstFrame
  })

  useEffect(() => {
    activeRef.current = active
    onActive.current()
  }, [active])

  const posterMounted = (img: HTMLImageElement | null) => {
    posterRef.current = img
    if (img) img.style.opacity = covered.current ? '0' : ''
  }

  useEffect(() => {
    const root = rootRef.current
    const canvas = canvasRef.current
    if (!live || !root || !canvas || !seq || !clock) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const fileW = seq.info.w
    let cssW = 0
    let cssH = 0
    let visible = false
    let detach: (() => void) | null = null
    let drawn: number | null = null
    let fresh = true // platno je prazno (novo ili promenjena veličina)
    let announced = false

    const showPoster = (on: boolean) => {
      covered.current = !on
      const img = posterRef.current
      if (img) img.style.opacity = on ? '' : '0'
    }

    // u ekranu i nije pokriveno: sat drži kadrove oko trenutnog i zove draw
    const sync = () => {
      const want = visible && activeRef.current
      if (want && !detach) detach = clock.attach(seq, draw)
      else if (!want && detach) {
        detach()
        detach = null
      }
    }
    onActive.current = sync

    const draw = () => {
      if (!visible || !cssW) return
      const g = clock.frameFor(seq)
      if (g === null || (g === drawn && !fresh)) return
      const bmp = seq.bitmap(g)
      if (!bmp) return
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(bmp, 0, 0, canvas.width, canvas.height)
      drawn = g
      fresh = false
      if (SEQ_DEBUG) canvas.dataset.g = String(g)
      if (!covered.current) showPoster(false)
      if (!announced) {
        announced = true
        firstFrame.current?.()
      }
    }

    const fit = () => {
      if (!cssW || !cssH) return
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      const scale = Math.min(dpr, fileW / cssW)
      const w = Math.max(1, Math.round(cssW * scale))
      const h = Math.max(1, Math.round(cssH * scale))
      if (canvas.width === w && canvas.height === h) return
      // imageSmoothingQuality ostaje podrazumevan ('low', bilinearno): umanjenje je 0,5–1, a 'high'
      // je uz 4× usporen CPU skoro duplo skuplji po kadru (izmereno na /dev/seq)
      canvas.width = w
      canvas.height = h
      fresh = true
      draw()
      // nova veličina briše platno; dok se kadar ne nacrta ponovo, vidi se poster
      if (fresh && covered.current) showPoster(true)
    }

    const ro = new ResizeObserver((entries) => {
      const box = entries[entries.length - 1].contentRect
      cssW = box.width
      cssH = box.height
      fit()
    })
    ro.observe(canvas)

    // DPR se menja kad se prozor prebaci na drugi ekran (ResizeObserver to ne javlja)
    let dprQuery: MediaQueryList | null = null
    function onDpr() {
      watchDpr()
      fit()
    }
    function watchDpr() {
      dprQuery?.removeEventListener('change', onDpr)
      dprQuery = window.matchMedia(`(resolution: ${window.devicePixelRatio || 1}dppx)`)
      dprQuery.addEventListener('change', onDpr)
    }
    watchDpr()

    // u ekranu: crta se (-1px: kutija koja samo dodiruje ivicu ekrana se ne računa)
    const inView = new IntersectionObserver(
      (entries) => {
        visible = entries[entries.length - 1].isIntersecting
        sync()
      },
      { rootMargin: '-1px 0px' },
    )
    // daleko od ekrana: dekodirani kadrovi se zatvaraju (Blob-ovi ostaju)
    const nearView = new IntersectionObserver(
      (entries) => {
        if (!entries[entries.length - 1].isIntersecting) seq.release()
      },
      { rootMargin: '100% 0px' },
    )
    inView.observe(root)
    nearView.observe(root)

    return () => {
      inView.disconnect()
      nearView.disconnect()
      ro.disconnect()
      dprQuery?.removeEventListener('change', onDpr)
      onActive.current = () => {}
      detach?.()
      seq.release()
      showPoster(true)
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      delete canvas.dataset.g
    }
  }, [live, seq, clock])

  const rect: CSSProperties | undefined = geo
    ? {
        left: pct(geo.crop.x0 / geo.full.W),
        top: pct(geo.crop.y0 / geo.full.H),
        width: pct(geo.crop.w / geo.full.W),
        height: pct(geo.crop.h / geo.full.H),
      }
    : undefined

  return (
    <div
      ref={rootRef}
      data-seq-canvas={seq?.id}
      className={`[contain:layout] ${className}`}
      style={geo ? { aspectRatio: `${geo.full.W} / ${geo.full.H}`, ...style } : style}
    >
      {deferPoster ? (
        <span role="img" aria-label={poster.alt} className={geo ? 'absolute block' : 'block h-full w-full'} style={rect} />
      ) : (
        <img
          ref={posterMounted}
          src={poster.src}
          alt={poster.alt}
          decoding="async"
          loading={poster.priority ? 'eager' : 'lazy'}
          fetchPriority={poster.priority ? 'high' : 'auto'}
          draggable={false}
          className={geo ? 'absolute block max-w-none select-none' : 'block h-full w-full select-none object-contain'}
          style={rect}
        />
      )}
      {live && <canvas ref={canvasRef} aria-hidden="true" className="pointer-events-none absolute block" style={rect} />}
    </div>
  )
}
