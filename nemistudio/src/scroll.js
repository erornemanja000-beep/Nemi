// Smooth scrolling (Lenis) driven by the GSAP ticker, shared by the film and the sections.
import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
export let lenis = null;

// --vh in px, refreshed only when the width changes (phone toolbars must not resize the film)
let lastW = 0;
export function setVh() {
  if (innerWidth === lastW && lastW) return;
  lastW = innerWidth;
  document.documentElement.style.setProperty('--vh', innerHeight / 100 + 'px');
}
export const vhPx = () => {
  if (!lastW) setVh();
  return parseFloat(document.documentElement.style.getPropertyValue('--vh')) || innerHeight / 100;
};

export function initScroll() {
  setVh();
  addEventListener('resize', () => { setVh(); ScrollTrigger.refresh(); });
  if (!reduced) {
    lenis = new Lenis({ lerp: 0.085, wheelMultiplier: 0.9, touchMultiplier: 1.4, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
  }
  gsap.ticker.lagSmoothing(0);
}

export function scrollToY(y, immediate = false) {
  if (lenis) lenis.scrollTo(y, { immediate, duration: immediate ? 0 : 1.6, easing: (t) => 1 - Math.pow(1 - t, 4) });
  else scrollTo({ top: y, behavior: immediate ? 'auto' : 'smooth' });
}

export function scrollToId(id) {
  const el = document.getElementById(id);
  if (!el) return;
  scrollToY(el.getBoundingClientRect().top + scrollY);
}

export const stop = () => lenis && lenis.stop();
export const resume = () => lenis && lenis.start();
