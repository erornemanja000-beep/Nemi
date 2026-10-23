// GSAP + ScrollTrigger + Lenis (uzor: RealEstates/src/lib/motion.ts).
// Lenis radi samo kad je features.smoothScroll uključen, kad je pokazivač precizan (miš) i van
// reduced motion (odluka direktora 1). Na telefonu i sa reduced motion ostaje izvorni skrol.
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'
import { features } from '../config/site'
import { isFinePointer, isReducedMotion } from './useMedia'

gsap.registerPlugin(ScrollTrigger)

export const prefersReducedMotion = isReducedMotion

let lenis: Lenis | null = null
const raf = (time: number) => lenis?.raf(time * 1000)

/** Pokreće Lenis i vezuje ga za gsap.ticker, da ScrollTrigger ostane usklađen. */
export function startSmoothScroll(): Lenis | null {
  if (lenis || !features.smoothScroll || isReducedMotion() || !isFinePointer()) return lenis
  // anchors: Lenis sam skroluje do #sidra (poštuje scroll-margin-top sekcije)
  lenis = new Lenis({ anchors: true, autoRaf: false })
  lenis.on('scroll', ScrollTrigger.update)
  gsap.ticker.add(raf)
  gsap.ticker.lagSmoothing(0)
  return lenis
}

/** Gasi Lenis (npr. kad korisnik uključi reduced motion dok je stranica otvorena). */
export function stopSmoothScroll() {
  if (!lenis) return
  gsap.ticker.remove(raf)
  gsap.ticker.lagSmoothing(500, 33)
  lenis.destroy()
  lenis = null
}

export const getLenis = () => lenis

/** Skrol do broja, selektora (#sidro) ili elementa. Sa Lenis-om glatko, bez njega izvorno. */
export function scrollToTarget(target: string | number | HTMLElement, immediate = false) {
  const smooth = !immediate && !isReducedMotion()
  if (lenis) {
    lenis.scrollTo(target, { immediate: !smooth })
    return
  }
  const behavior: ScrollBehavior = smooth ? 'smooth' : 'auto'
  if (typeof target === 'number') {
    window.scrollTo({ top: target, behavior })
    return
  }
  const el = typeof target === 'string' ? document.querySelector(target) : target
  el?.scrollIntoView({ behavior })
}

/** Zaključava skrol stranice (meni, korpa, modal). Panel koji se sam skroluje dobija data-lenis-prevent. */
export function lockScroll(locked: boolean) {
  if (lenis) {
    if (locked) lenis.stop()
    else lenis.start()
  }
  document.documentElement.style.overflow = locked ? 'hidden' : ''
}

/** Fontovi menjaju visine teksta, pa ScrollTrigger posle njih ponovo meri pozicije. */
export function refreshAfterFonts() {
  if (typeof document === 'undefined' || !document.fonts) return
  document.fonts.ready.then(() => ScrollTrigger.refresh())
}

export { gsap, ScrollTrigger }
