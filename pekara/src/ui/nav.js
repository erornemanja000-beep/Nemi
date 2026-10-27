// Navigacija: meni na 390, unutrašnji linkovi (preko bus 'scrollTo', da rade i sa Lenisom),
// hint-ovi „Dreh das Grätzl" i „Klopf ans Fenster.".
// Bus: set('knock', broj tapova) tap na „Klopf ans Fenster." (3D kratko pojača sjaj pekare).
// Zvuka nema (odluka direktora, tekstovi.md), pa ni prekidača „Ton an".

import { je3d } from './util.js';

const INTERAKTIVNO = 'a, button, input, select, textarea, label, form, [data-no-drag]';

export function init(bus) {
  const root = document.documentElement;
  const meni = document.querySelector('[data-meni]');
  const meniBtn = document.querySelector('[data-meni-btn]');

  // ---------- meni (390) ----------
  function zatvori(vratiFokus = true) {
    if (!meni || meni.hidden) return;
    meni.hidden = true;
    meniBtn.setAttribute('aria-expanded', 'false');
    root.classList.remove('meni-otvoren');
    if (vratiFokus) meniBtn.focus();
  }
  meniBtn?.addEventListener('click', () => {
    if (!meni.hidden) return zatvori();
    meni.hidden = false;
    meniBtn.setAttribute('aria-expanded', 'true');
    root.classList.add('meni-otvoren');
    meni.querySelector('a')?.focus();
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') zatvori(); });
  matchMedia('(min-width: 701px)').addEventListener('change', (e) => e.matches && zatvori(false));

  // ---------- unutrašnji linkovi ----------
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey) return;
    const cilj = document.querySelector(a.getAttribute('href'));
    if (!cilj) return;
    e.preventDefault();
    zatvori(false);
    const skrol = bus.get('scrollTo');
    if (typeof skrol === 'function') skrol(cilj.id === 'top' ? 0 : cilj);
    else cilj.scrollIntoView({ block: 'start' });
    // fokus ide na naslov cilja, bez dodatnog skrola
    const fokus = cilj.querySelector('[data-sackerl] input, h1, h2') ?? cilj;
    if (!fokus.matches('input')) fokus.setAttribute('tabindex', '-1');
    fokus.focus({ preventScroll: true });
    history.replaceState(null, '', a.getAttribute('href'));
  });

  // ---------- „Klopf ans Fenster." (05:00): jednom, nestaje posle prvog tapa ----------
  const klopf = document.querySelector('[data-klopf]');
  let tapovi = 0;
  klopf?.addEventListener('click', () => {
    bus.set('knock', ++tapovi);
    klopf.hidden = true;
    document.getElementById('t3')?.setAttribute('tabindex', '-1');
    document.getElementById('t3')?.focus({ preventScroll: true });
  });

  // ---------- „Dreh das Grätzl": nestaje posle prvog vodoravnog povlačenja ----------
  const dreh = document.querySelector('[data-hint-dreh]');
  if (dreh) {
    let start = null;
    const kraj = () => { start = null; };
    const pomeri = (e) => {
      if (!start || e.pointerId !== start.id) return;
      const dx = Math.abs(e.clientX - start.x);
      if (dx > 24 && dx > Math.abs(e.clientY - start.y)) {
        dreh.classList.add('je-skriven');
        removeEventListener('pointerdown', dole);
        removeEventListener('pointermove', pomeri);
      }
    };
    const dole = (e) => {
      if (!je3d() || e.target.closest(INTERAKTIVNO)) return;
      start = { id: e.pointerId, x: e.clientX, y: e.clientY };
    };
    addEventListener('pointerdown', dole, { passive: true });
    addEventListener('pointermove', pomeri, { passive: true });
    addEventListener('pointerup', kraj, { passive: true });
    addEventListener('pointercancel', kraj, { passive: true });
  }
}
