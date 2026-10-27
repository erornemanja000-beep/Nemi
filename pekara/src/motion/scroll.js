// Skrol → bus: `progress` (0–1) i `chapter` ({ id, faza }) iz sekcija <section data-pogl="1..7">.
// U '3d' modu ide Lenis (glatki točkić) vezan za GSAP ticker; u 'static' modu i sa
// prefers-reduced-motion je to običan skrol browsera, a događaji ostaju isti (sat, tekstovi).
//
// Layout (pozicije sekcija) se čita samo na ScrollTrigger refresh (resize, load, pinovi),
// nikad u petlji skrola.
//
// Promena veličine (okretanje telefona) menja visine sekcija, pa isti scrollY pada u drugo
// poglavlje. Zato se pri resize-u pamti poslednje mesto pre promene ({ id, faza }) i posle
// refresh-a se skrol vraća na isto mesto u novom layout-u.

import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import 'lenis/dist/lenis.css';

gsap.registerPlugin(ScrollTrigger);

// Udeli iz mapa-skrola.md, kad sekcije još ne postoje u HTML-u.
const FALLBACK_STARTS = [0, 0.09, 0.25, 0.42, 0.6, 0.72, 0.88];
const BREADS = 4;

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

export function initScroll(bus, { smooth = false } = {}) {
  let lenis = null;
  let tickerFn = null;
  let bounds = []; // [{ id, top }] sortirano po top
  let maxScroll = 1;
  let lastBread = 0;
  let lastId = 0;
  let lastFaza = -1;
  let saved = null; // { id, faza } pre resize-a, dok refresh ne vrati skrol
  let lastW = window.innerWidth;
  let lastH = window.innerHeight;
  let resizeTimer = 0;

  function measure() {
    const y = window.scrollY;
    const sections = [...document.querySelectorAll('[data-pogl]')];
    bounds = sections
      .map((el) => {
        // Kad ScrollTrigger pinuje sekciju, prava pozicija u dokumentu je na .pin-spacer omotaču.
        const box = el.parentElement?.classList.contains('pin-spacer') ? el.parentElement : el;
        return { id: Number(el.dataset.pogl), top: box.getBoundingClientRect().top + y };
      })
      .filter((b) => b.id >= 1 && b.id <= 7)
      .sort((a, b) => a.top - b.top);
    maxScroll = Math.max(1, ScrollTrigger.maxScroll(window));
  }

  function chapterAt(y, progress) {
    if (bounds.length) {
      let i = 0;
      while (i + 1 < bounds.length && bounds[i + 1].top <= y + 1) i++;
      const start = bounds[i].top;
      const end = i + 1 < bounds.length ? bounds[i + 1].top : maxScroll;
      return { id: bounds[i].id, faza: end > start ? clamp01((y - start) / (end - start)) : 1 };
    }
    let i = 0;
    while (i + 1 < FALLBACK_STARTS.length && FALLBACK_STARTS[i + 1] <= progress) i++;
    const start = FALLBACK_STARTS[i];
    const end = FALLBACK_STARTS[i + 1] ?? 1;
    return { id: i + 1, faza: clamp01((progress - start) / (end - start)) };
  }

  function update(y) {
    if (saved) return; // posle resize-a, a pre refresh-a: stari bounds ne važe
    const progress = clamp01(y / maxScroll);
    bus.set('progress', progress);

    const ch = chapterAt(y, progress);
    if (ch.id !== lastId || Math.abs(ch.faza - lastFaza) > 1e-4) {
      lastId = ch.id;
      lastFaza = ch.faza;
      bus.set('chapter', ch);
    }

    // Aktivni hleb prati skrol u poglavlju 5. Postavlja se samo kad se izračunata vrednost
    // promeni, pa UI (npr. prevlačenje etiketa na telefonu) može slobodno da ga menja između.
    if (ch.id === 5) {
      const n = 1 + Math.min(BREADS - 1, Math.floor(ch.faza * BREADS));
      if (n !== lastBread) {
        lastBread = n;
        bus.set('activeBread', n);
      }
    } else {
      lastBread = 0;
    }
  }

  const master = ScrollTrigger.create({
    start: 0,
    end: 'max',
    onUpdate: (self) => update(self.scroll()),
  });

  const onResize = () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    // samo visina (traka adrese na telefonu) ne menja layout sekcija
    if (w === lastW && Math.abs(h - lastH) < 160) return;
    lastW = w;
    lastH = h;
    if (!saved && lastId) saved = { id: lastId, faza: Math.max(0, lastFaza) };
    // rezerva: ako ScrollTrigger sam ne osveži, osveži ovde (inače bi update ostao zaključan)
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => saved && ScrollTrigger.refresh(), 900);
  };
  window.addEventListener('resize', onResize, { passive: true });

  function restore() {
    const want = saved;
    saved = null;
    const i = bounds.findIndex((b) => b.id === want.id);
    if (i < 0) return;
    const start = bounds[i].top;
    const end = i + 1 < bounds.length ? bounds[i + 1].top : maxScroll;
    const y = Math.round(Math.min(maxScroll, start + want.faza * Math.max(0, end - start)));
    if (Math.abs(y - window.scrollY) < 2) return;
    if (lenis) {
      lenis.resize(); // Lenis inače seče na staru visinu stranice (svoj ResizeObserver kasni)
      lenis.scrollTo(y, { immediate: true, force: true });
    }
    else window.scrollTo({ top: y, behavior: 'instant' });
    ScrollTrigger.update();
  }

  const onRefresh = () => {
    measure();
    if (saved) restore();
    update(window.scrollY);
  };
  ScrollTrigger.addEventListener('refresh', onRefresh);
  measure();
  update(window.scrollY);

  // Mod menja visine sekcija (CSS .mode-3d / .mode-static), u oba smera: ponovo izmeri posle
  // primene stilova (sledeći kadar), da `chapter` i `progress` odgovaraju novom layout-u.
  let refreshRaf = 0;
  const offMode = bus.on('mode', () => {
    cancelAnimationFrame(refreshRaf);
    refreshRaf = requestAnimationFrame(() => ScrollTrigger.refresh());
  });

  function scrollTo(target, opts = {}) {
    if (lenis) {
      lenis.scrollTo(target, opts);
      return;
    }
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const behavior = reduced || opts.immediate ? 'auto' : 'smooth';
    if (typeof target === 'number') window.scrollTo({ top: target, behavior });
    else {
      const el = typeof target === 'string' ? document.querySelector(target) : target;
      el?.scrollIntoView({ behavior, block: 'start' });
    }
  }
  bus.set('scrollTo', scrollTo);

  function setSmooth(on) {
    if (on && !lenis) {
      lenis = new Lenis({ autoRaf: false, lerp: 0.1, smoothWheel: true });
      lenis.on('scroll', ScrollTrigger.update);
      tickerFn = (time) => lenis.raf(time * 1000);
      gsap.ticker.add(tickerFn);
      gsap.ticker.lagSmoothing(0);
    } else if (!on && lenis) {
      gsap.ticker.remove(tickerFn);
      gsap.ticker.lagSmoothing(500, 33);
      lenis.destroy();
      lenis = null;
      tickerFn = null;
    }
  }
  setSmooth(smooth);

  return {
    setSmooth,
    refresh: () => ScrollTrigger.refresh(),
    destroy() {
      offMode();
      cancelAnimationFrame(refreshRaf);
      setSmooth(false);
      ScrollTrigger.removeEventListener('refresh', onRefresh);
      window.removeEventListener('resize', onResize);
      clearTimeout(resizeTimer);
      master.kill();
    },
  };
}
