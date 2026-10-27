// Poglavlja: koji tekst je u kadru. Tekst je vezan za stanicu kamere (bus 'chapter'),
// ne za piksel skrola: klase .is-on / .is-off, a ulaz i izlaz radi CSS (chapters.css).
// Takođe: mod '3d' | 'static' na <html>, aktivni link u nav-u, dnevna traka nav-a (samo uz formu),
// .futer-on na <html> i donja traka Vorbestellen na 390 (od poglavlja 2 do forme, skrivena dok je forma u vidu).

import { VISINA, telefon, primeniMod, poglavljeIz } from './util.js';
import { init as initStatic } from '../static/fallback.js';

const IZLAZ_MS = 480; // --dur-3

// 05:00: tekst se skloni dok se kriška izvlači i vraća se čim kriška stane (u 0,30–0,36
// u poglavlju 0,25–0,42, timeline.js). „Klopf" postoji samo pre kriške: posle nje izloga nema u kadru.
const KRISKA = [(0.30 - 0.25) / 0.17, (0.36 - 0.25) / 0.17];
const LEAD_POSLE_SVH = 25; // 390: lead ulazi posle ~25svh skrola u istom poglavlju

function prebaci(el, on) {
  if (on) {
    clearTimeout(el._izlaz);
    el.classList.remove('is-off');
    el.classList.add('is-on');
  } else if (el.classList.contains('is-on')) {
    el.classList.remove('is-on');
    el.classList.add('is-off');
    clearTimeout(el._izlaz);
    el._izlaz = setTimeout(() => el.classList.remove('is-off'), IZLAZ_MS + 40);
  }
}

export function init(bus) {
  const root = document.documentElement;
  const sekcije = new Map([...document.querySelectorAll('[data-pogl]')].map((s) => [Number(s.dataset.pogl), s]));
  const koraci = [...document.querySelectorAll('[data-korak]')];
  const linkovi = [...document.querySelectorAll('[data-link]')];
  const nav = document.querySelector('[data-nav]');
  const forma = document.querySelector('[data-sackerl]');

  // UI radi: rezerva iz <head> (statično posle 4 s) više ne treba. Dok mod nije odlučen
  // (scena se učitava), ostaje pretpostavka iz <head>.
  root.classList.add('ui-ready');
  primeniMod(bus.get('mode'));
  bus.on('mode', primeniMod);
  // statični kadrovi (src/static/fallback.js); main.js ga još ne pokreće sam
  initStatic(bus);

  let id = 0;
  let formaUVidu = false;
  let futerUVidu = false;

  const traka = () => root.classList.toggle('traka-on', id >= 2 && id < 7 && !formaUVidu);

  function aktiviraj(novi) {
    id = novi;
    // na desktopu tekst „Wir sperren auf" ostaje pored kese (kadar 06:30 + forma, mockup)
    const vidljivo = new Set([novi]);
    if (novi === 7 && !telefon.matches && !futerUVidu) vidljivo.add(6);
    for (const [n, s] of sekcije) prebaci(s, vidljivo.has(n));

    for (const a of linkovi) {
      const moj = a.dataset.link.split(' ').map(Number).includes(novi);
      if (moj) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    }
    // dnevna traka samo uz formu; futer je večernji kadar
    nav?.classList.toggle('nav--dan', novi === 7 && !futerUVidu);
    traka();
  }

  function naPoglavlje(ch) {
    if (!ch || !sekcije.has(ch.id)) return;
    const faza = typeof ch.faza === 'number' ? ch.faza : 0;
    if (ch.id !== id) aktiviraj(ch.id);

    const s = sekcije.get(ch.id);
    s.classList.toggle('lead-on', faza * VISINA[ch.id] >= LEAD_POSLE_SVH || ch.id === 7);

    if (ch.id === 3) {
      s.classList.toggle('is-skriven', faza > KRISKA[0] && faza < KRISKA[1]);
      s.classList.toggle('klopf-off', faza > KRISKA[0]);
    }
    if (ch.id === 4) {
      const k = faza < 1 / 3 ? 1 : faza < 2 / 3 ? 2 : 3;
      for (const el of koraci) prebaci(el, Number(el.dataset.korak) === k);
    }
  }

  bus.on('chapter', naPoglavlje);
  // rezerva: dok scroll modul ne pošalje 'chapter', poglavlje se računa iz udela
  bus.on('progress', (p) => { if (!bus.get('chapter')) naPoglavlje(poglavljeIz(p)); });
  naPoglavlje(bus.get('chapter') ?? poglavljeIz(bus.get('progress') ?? 0));

  // u statičnom modu (prirodne visine) koraci i poglavlja su svi vidljivi preko CSS-a;
  // ovde se samo prati da li je forma u vidu, zbog donje trake
  if (forma && 'IntersectionObserver' in window) {
    new IntersectionObserver(([e]) => { formaUVidu = e.isIntersecting; traka(); }, { threshold: 0.05 }).observe(forma);
  }
  const futer = document.querySelector('.futer');
  if (futer && 'IntersectionObserver' in window) {
    new IntersectionObserver(([e]) => {
      futerUVidu = e.isIntersecting;
      root.classList.toggle('futer-on', futerUVidu); // sat i lenjir se gase (base.css)
      if (id) aktiviraj(id);
    }, { threshold: 0.25 }).observe(futer);
  }
  telefon.addEventListener('change', () => id && aktiviraj(id));
}
