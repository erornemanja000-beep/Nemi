// Scroll-scrubbed video, done the way Apple product pages do it: every video
// is exported as a numbered run of JPEG frames and painted onto a <canvas>.
// Seeking a <video> element by scroll stutters; swapping decoded images does not.

export type SequenceInfo = { count: number; width: number; height: number }
export type Manifest = Record<string, SequenceInfo>

/**
 * Phones in portrait get their own frame set (media/seq-m): fewer frames, centre-cropped to
 * portrait. That is all a phone screen shows of a 16:9 frame anyway, at a quarter of the memory.
 */
export const PHONE = matchMedia('(max-width: 900px) and (orientation: portrait)').matches
const BASE = PHONE ? './media/seq-m' : './media/seq'

export class FrameSequence {
  readonly frames: (HTMLImageElement | null)[]
  /** Still shown until the first frame arrives (same picture as frame 0 or the last frame). */
  poster: HTMLImageElement | null = null
  frame = 0
  private loadedCount = 0
  private onProgress = new Set<() => void>()

  constructor(
    readonly name: string,
    readonly info: SequenceInfo,
  ) {
    this.frames = new Array(info.count).fill(null)
  }

  get count() {
    return this.info.count
  }

  get progress() {
    return this.loadedCount / this.info.count
  }

  url(i: number) {
    return `${BASE}/${this.name}/${String(i + 1).padStart(3, '0')}.jpg`
  }

  /** Frame order that makes a coarse version of the clip usable early: every 8th, then 4th, 2nd, rest. */
  loadOrder(): number[] {
    const order: number[] = []
    const seen = new Set<number>()
    for (const step of [8, 4, 2, 1]) {
      for (let i = 0; i < this.count; i += step) {
        if (!seen.has(i)) {
          seen.add(i)
          order.push(i)
        }
      }
    }
    if (!seen.has(this.count - 1)) order.push(this.count - 1)
    return order
  }

  store(i: number, img: HTMLImageElement) {
    if (this.frames[i]) return
    this.frames[i] = img
    this.loadedCount++
    this.onProgress.forEach((fn) => fn())
  }

  subscribe(fn: () => void) {
    this.onProgress.add(fn)
  }

  /** The requested frame, or the closest frame that has already loaded. */
  image(i = this.frame): HTMLImageElement | null {
    const idx = Math.max(0, Math.min(this.count - 1, Math.round(i)))
    if (this.frames[idx]) return this.frames[idx]
    for (let d = 1; d < this.count; d++) {
      const a = this.frames[idx - d]
      if (a) return a
      const b = this.frames[idx + d]
      if (b) return b
    }
    return this.poster
  }
}

/** Loads frames for many sequences through one queue so the first clips win the bandwidth. */
export class FrameLoader {
  private queue: { seq: FrameSequence; i: number }[] = []
  private active = 0

  constructor(private concurrency = 6) {}

  enqueue(seq: FrameSequence) {
    for (const i of seq.loadOrder()) this.queue.push({ seq, i })
    this.pump()
  }

  /** Move a sequence to the front, e.g. when the visitor scrolls ahead of the loader. */
  prioritise(seq: FrameSequence) {
    const mine = this.queue.filter((q) => q.seq === seq)
    if (!mine.length) return
    this.queue = [...mine, ...this.queue.filter((q) => q.seq !== seq)]
  }

  private pump() {
    while (this.active < this.concurrency && this.queue.length) {
      const job = this.queue.shift()!
      if (job.seq.frames[job.i]) continue
      this.active++
      const img = new Image()
      img.decoding = 'async'
      img.src = job.seq.url(job.i)
      img
        .decode()
        .then(() => job.seq.store(job.i, img))
        .catch(() => {})
        .finally(() => {
          this.active--
          this.pump()
        })
    }
  }
}

/** A full-bleed canvas that paints images with object-fit: cover behaviour. */
export class CoverCanvas {
  private ctx: CanvasRenderingContext2D
  private last: HTMLImageElement | null = null
  private w = 0
  private h = 0

  constructor(readonly el: HTMLCanvasElement) {
    this.ctx = el.getContext('2d', { alpha: false })!
    this.resize()
  }

  resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, PHONE ? 1.5 : 2)
    const rect = this.el.getBoundingClientRect()
    this.w = Math.max(1, Math.round(rect.width * dpr))
    this.h = Math.max(1, Math.round(rect.height * dpr))
    this.el.width = this.w
    this.el.height = this.h
    this.ctx.imageSmoothingQuality = 'high'
    const img = this.last
    this.last = null
    if (img) this.draw(img)
  }

  draw(img: HTMLImageElement | null, zoom = 1) {
    if (!img || (img === this.last && zoom === 1)) return
    this.last = img
    const iw = img.naturalWidth
    const ih = img.naturalHeight
    const scale = Math.max(this.w / iw, this.h / ih) * zoom
    const dw = iw * scale
    const dh = ih * scale
    this.ctx.drawImage(img, (this.w - dw) / 2, (this.h - dh) / 2, dw, dh)
  }
}

export async function loadManifest(): Promise<Manifest> {
  const res = await fetch(`${BASE}/manifest.json`)
  return res.json()
}

export function loadImage(src: string): Promise<HTMLImageElement> {
  const img = new Image()
  img.decoding = 'async'
  img.src = src
  return img.decode().then(() => img)
}
