// Etikete hlebova (06:00 Brot des Tages).
// Desktop: tanke linije od leve ivice etikete do hleba; tačku šalje 3D preko bus 'labels'
//   ([{ n, x, y, visible }] u CSS px viewporta, svaki frejm). Linije se jednom „docrtaju".
// 390: vodoravni niz sa scroll-snap; prevlačenje menja aktivni hleb (bus.set('activeBread')),
//   a kad 3D promeni hleb, niz se pomeri na njegovu etiketu. Linije se ne crtaju.
// 'static': bez aktivnog stanja i bez linija (CSS); na 390 niz pomera samo prst.

import { telefon, smanjiPokret, je3d } from './util.js';

const KRAK = 42; // vodoravni krak linije (px)
const ODMAK = 8; // razmak od ivice etikete
const RUB = 8; // tačka bliže ivici ekrana od ovoga se ne crta

export function init(bus) {
  const sek = document.querySelector('[data-pogl="5"]');
  const lista = sek?.querySelector('[data-etikete]');
  if (!lista) return;
  const etikete = [...lista.querySelectorAll('[data-hleb]')];
  const svg = sek.querySelector('[data-linije]');
  const grupe = svg ? [...svg.querySelectorAll('g[data-hleb]')] : [];
  const tacke = [...sek.querySelectorAll('[data-tacke] i')];

  // ---------- aktivni hleb ----------
  let aktivan = 0;
  function postavi(n) {
    aktivan = n;
    etikete.forEach((li, i) => {
      if (je3d() && i + 1 === n) li.setAttribute('aria-current', 'true');
      else li.removeAttribute('aria-current');
    });
    grupe.forEach((g, i) => g.classList.toggle('on', i + 1 === n));
    tacke.forEach((t, i) => t.classList.toggle('on', i + 1 === n));
    sidra = null; // visina aktivne etikete se menja (opis), pa se sidra ponovo mere
  }

  // ---------- desktop: linije ----------
  let sidra = null; // [{x, y}] početak linije uz svaku etiketu, bez transform-a ulaza
  const izmeri = () => {
    sidra = etikete.map((li) => ({
      x: lista.offsetLeft + li.offsetLeft - ODMAK,
      y: lista.offsetTop + li.offsetTop + 14,
    }));
  };
  addEventListener('resize', () => { sidra = null; }, { passive: true });

  // Crta liniju samo kad je tačka u ekranu i levo od kraka: inače bi linija prešla preko
  // etikete ili otišla van ekrana. Sidra se mere u koordinatama .pogl__in (u 3D fiksan, 0,0 = viewport).
  function crtaj(niz) {
    if (!svg || !Array.isArray(niz) || telefon.matches || !je3d() || !sek.classList.contains('is-on')) return;
    if (!sidra) izmeri();
    const W = innerWidth;
    const H = innerHeight;
    for (const { n, x, y, visible } of niz) {
      const g = grupe[n - 1];
      const s = sidra[n - 1];
      if (!g || !s) continue;
      const ok = visible !== false && Number.isFinite(x) && Number.isFinite(y)
        && x >= RUB && x <= W - RUB && y >= RUB && y <= H - RUB && x < s.x - KRAK - RUB;
      g.classList.toggle('vidljiv', ok);
      if (!ok) continue;
      const d = `M${s.x} ${s.y}H${s.x - KRAK}L${x.toFixed(1)} ${y.toFixed(1)}`;
      for (const p of g.querySelectorAll('path')) p.setAttribute('d', d);
      const c = g.querySelector('circle');
      c.setAttribute('cx', x.toFixed(1));
      c.setAttribute('cy', y.toFixed(1));
      c.setAttribute('r', g.classList.contains('on') ? '6' : '5');
    }
  }
  bus.on('labels', crtaj);

  // linije se docrtaju prvi put kad poglavlje 5 uđe u kadar; motor šalje 'labels' samo kad se
  // tačke pomere, pa se pri ulazu crta poslednji poznati niz
  let bioId = 0;
  bus.on('chapter', (ch) => {
    const ulaz = ch?.id === 5 && bioId !== 5;
    bioId = ch?.id ?? 0;
    if (!ulaz || !svg) return;
    if (!svg.classList.contains('crtaj')) {
      sidra = null;
      requestAnimationFrame(() => svg.classList.add('crtaj'));
    }
    requestAnimationFrame(() => crtaj(bus.get('labels')));
  });
  addEventListener('resize', () => requestAnimationFrame(() => crtaj(bus.get('labels'))), { passive: true });

  // ---------- 390: niz sa scroll-snap ----------
  let programski = false;
  let tajmer = 0;
  const korak = () => (etikete[1] ? etikete[1].offsetLeft - etikete[0].offsetLeft : lista.clientWidth);

  function naEtiketu(n) {
    const li = etikete[n - 1];
    if (!li || !telefon.matches) return;
    programski = true;
    lista.scrollTo({ left: li.offsetLeft - etikete[0].offsetLeft, behavior: smanjiPokret.matches ? 'auto' : 'smooth' });
    clearTimeout(tajmer);
    tajmer = setTimeout(() => { programski = false; }, 700);
  }

  lista.addEventListener('scroll', () => {
    if (!telefon.matches) return;
    const n = Math.min(etikete.length, Math.max(1, Math.round(lista.scrollLeft / korak()) + 1));
    if (programski) {
      clearTimeout(tajmer);
      tajmer = setTimeout(() => { programski = false; }, 150);
      return;
    }
    if (n === aktivan) return;
    postavi(n);
    bus.set('activeBread', n);
  }, { passive: true });

  // u 'static' modu niz pomera samo prst (skrol stranice ne vuče niz u stranu)
  bus.on('activeBread', (n) => {
    if (n === aktivan || !je3d()) return;
    postavi(n);
    naEtiketu(n);
  });
  bus.on('mode', () => postavi(aktivan || 1));

  postavi(bus.get('activeBread') ?? 1);
}
