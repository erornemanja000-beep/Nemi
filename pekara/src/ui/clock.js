// Sat u navigaciji: 04:00 → 06:30 po mapi skrola, pa staje (tekstovi.md, odluka direktora).
// Vreme ide kroz poglavlje od njegovog vremena ka vremenu sledećeg i skače u koracima od
// 5 minuta (cifre ne trepere); lenjir 04–07 je kontinualan.
// U 'static' modu (reduced motion, bez WebGL-a) sat skače po poglavljima, bez međuvremena.

import { je3d, poglavljeIz } from './util.js';

// minuti od ponoći na početku poglavlja 1–7 (+ kraj); 6 i 7 stoje na 06:30
const VREME = [240, 270, 300, 315, 360, 390, 390, 390];
const OD = 240;
const RASPON = 180; // lenjir 04:00 → 07:00

const fmt = (min) => `${String(Math.floor(min / 60)).padStart(2, '0')}:${String(min % 60).padStart(2, '0')}`;

export function init(bus) {
  const zeit = document.querySelector('[data-uhr]');
  const lenjir = document.querySelector('[data-lenjir]');
  if (!zeit || !lenjir) return;

  let tekst = zeit.textContent;
  let p = -1;

  function prikazi({ id, faza }) {
    const i = Math.min(Math.max(id, 1), 7) - 1;
    const f = je3d() && typeof faza === 'number' ? faza : 0;
    const min = VREME[i] + (VREME[i + 1] - VREME[i]) * f;
    const t = fmt(Math.floor((min + 1e-6) / 5) * 5);
    if (t !== tekst) zeit.textContent = tekst = t;
    const np = Math.round(((min - OD) / RASPON) * 1000) / 1000;
    if (np !== p) lenjir.style.setProperty('--p', String((p = np)));
  }

  bus.on('chapter', (ch) => ch && prikazi(ch));
  bus.on('progress', (pr) => { if (!bus.get('chapter')) prikazi(poglavljeIz(pr)); });
  bus.on('mode', () => prikazi(bus.get('chapter') ?? { id: 1, faza: 0 }));
  prikazi(bus.get('chapter') ?? poglavljeIz(bus.get('progress') ?? 0));
}
