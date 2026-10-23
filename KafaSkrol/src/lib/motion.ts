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
/** Otvoreni paneli koji drže skrol zaključanim, redom otvaranja (poslednji je na vrhu); lockScroll(). */
const scrollLocks: symbol[] = []
const raf = (time: number) => lenis?.raf(time * 1000)

/** Pokreće Lenis i vezuje ga za gsap.ticker, da ScrollTrigger ostane usklađen. */
export function startSmoothScroll(): Lenis | null {
  if (lenis || !features.smoothScroll || isReducedMotion() || !isFinePointer()) return lenis
  // anchors: Lenis sam skroluje do #sidra (poštuje scroll-margin-top sekcije). Lenis 1.3.27 ne radi
  // preventDefault, pa skoči i pregledač, ali Lenis vrati položaj u rAF-u pre crtanja: skok se ne vidi,
  // a hash, istorija i fokus ostaju kao kod običnog sidra (izmereno u Z13: svi linkovi menija na 1440
  // stanu tačno ispod headera). Klik koji posle skrola menja raspored (filter iz Brew guide-a) zove
  // scrollToTarget sam i radi stopPropagation, da Lenis ne skroluje drugi put.
  lenis = new Lenis({ anchors: true, autoRaf: false })
  lenis.on('scroll', ScrollTrigger.update)
  gsap.ticker.add(raf)
  gsap.ticker.lagSmoothing(0)
  // pokrenut dok je panel otvoren (npr. reduced motion isključen usred korpe): ostaje zaustavljen
  if (scrollLocks.length > 0) lenis.stop()
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

function applyScrollLock() {
  const locked = scrollLocks.length > 0
  if (lenis) {
    if (locked) lenis.stop()
    else lenis.start()
  }
  document.documentElement.style.overflow = locked ? 'hidden' : ''
}

/**
 * Zaključava skrol stranice (meni, korpa, modal). Panel koji se sam skroluje dobija data-lenis-prevent.
 * Broji otvorene panele: skrol se otključava tek kad se zatvori i poslednji (korpa preko modala ne
 * otključa stranicu ispod modala).
 * - lockScroll(true) vraća funkciju koja oslobađa baš taj panel; poziva se tačno jednom (Overlay).
 * - lockScroll(false) oslobađa panel na vrhu odmah, pre nego što pregledač ili Lenis skoči na #sidro
 *   (link u meniju ili korpi). Kasniji poziv funkcije tog panela tada ne radi ništa.
 */
export function lockScroll(locked: boolean): () => void {
  if (!locked) {
    if (scrollLocks.pop()) applyScrollLock()
    return () => {}
  }
  const id = Symbol('scroll-lock')
  scrollLocks.push(id)
  if (scrollLocks.length === 1) applyScrollLock()
  return () => {
    const i = scrollLocks.indexOf(id)
    if (i === -1) return
    scrollLocks.splice(i, 1)
    if (scrollLocks.length === 0) applyScrollLock()
  }
}

/** Fontovi menjaju visine teksta, pa ScrollTrigger posle njih ponovo meri pozicije. */
export function refreshAfterFonts() {
  if (typeof document === 'undefined' || !document.fonts) return
  document.fonts.ready.then(() => ScrollTrigger.refresh())
}

export { gsap, ScrollTrigger }
