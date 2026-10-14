const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const FINE = matchMedia('(hover: hover) and (pointer: fine)').matches;
const TLD = '{{.at||.com}}';
const hasG = typeof window.gsap !== 'undefined';
const G = hasG ? window.gsap : null;
if (hasG && window.ScrollTrigger) G.registerPlugin(ScrollTrigger);

/* ---------- helpers ---------- */
const slug = (s) => s.toLowerCase().replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
  .normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/&/g, 'und').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'website';
const onColor = (hex) => {
  const n = parseInt(hex.slice(1), 16), c = [n >> 16, (n >> 8) & 255, n & 255].map((v) => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); });
  return (.2126 * c[0] + .7152 * c[1] + .0722 * c[2]) > .32 ? '#111111' : '#FFFFFF';
};
const decode = (s) => { const t = document.createElement('textarea'); t.innerHTML = s; return t.value; };

/* ---------- smooth scroll ---------- */
let lenis = null;
if (hasG && !RM && window.Lenis) {
  lenis = new Lenis({ lerp: .09, wheelMultiplier: 1 });
  lenis.on('scroll', ScrollTrigger.update);
  G.ticker.add((t) => lenis.raf(t * 1000));
  G.ticker.lagSmoothing(0);
}
const goTo = (target) => {
  const el = typeof target === 'string' ? $(target) : target;
  if (!el) return;
  if (lenis) lenis.scrollTo(el, { offset: el.id === 'top' ? 0 : -10, duration: 1.4 });
  else el.scrollIntoView({ behavior: RM ? 'auto' : 'smooth' });
};

/* ---------- events and scroll speed (shared by effects and sound) ---------- */
const bus = new EventTarget();
const emit = (type, detail) => bus.dispatchEvent(new CustomEvent(type, { detail }));
const on = (type, fn) => bus.addEventListener(type, (e) => fn(e.detail));
let smoothVel = 0;
if (!RM) {
  let lastY = scrollY;
  const sample = () => { const y = scrollY; smoothVel += ((y - lastY) - smoothVel) * .18; lastY = y; requestAnimationFrame(sample); };
  requestAnimationFrame(sample);
}
// signed scroll speed in px per frame, smoothed (Lenis' own value when it runs)
const getVel = () => (lenis ? lenis.velocity : smoothVel);
