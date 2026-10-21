import { useEffect } from 'react';
import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { world } from '../world/state.js';

gsap.registerPlugin(ScrollTrigger);

export const reducedMotion = () => typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;

let lenis = null;

// Lenis daje „težak“ skrol, GSAP ScrollTrigger čita istu poziciju
export function useSmoothScroll(enabled) {
  useEffect(() => {
    if (!enabled || reducedMotion()) return undefined;
    lenis = new Lenis({ duration: 1.15, easing: (t) => 1 - Math.pow(1 - t, 4), touchMultiplier: 1.4 });
    lenis.on('scroll', (e) => { ScrollTrigger.update(); world.velocity = e.velocity; });
    const tick = (time) => { lenis.raf(time * 1000); if (!lenis.isScrolling) world.velocity *= 0.9; };
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    return () => {
      gsap.ticker.remove(tick);
      lenis.destroy();
      lenis = null;
    };
  }, [enabled]);
}

export function scrollToHash(hash) {
  const el = document.querySelector(hash);
  if (!el) return;
  if (lenis) lenis.scrollTo(el, { offset: 0, duration: 1.4 });
  else el.scrollIntoView({ behavior: reducedMotion() ? 'auto' : 'smooth' });
}

export function lockScroll(lock) {
  if (!lenis) return;
  if (lock) lenis.stop();
  else lenis.start();
}

export function scrollToY(y) {
  if (lenis) lenis.scrollTo(y, { duration: 1.3 });
  else window.scrollTo({ top: y, behavior: reducedMotion() ? 'auto' : 'smooth' });
}
