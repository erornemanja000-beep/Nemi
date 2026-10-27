// „Dein Sackerl für morgen": ime je obavezno, Stück 1–40, poruka zahvalnosti iz tekstovi.md
// (bez glagola, pa je ispravna i za 1 komad). Koncept: ništa se ne šalje.

const MIN = 1;
const MAX = 40;
const FEHLER_NAME = 'Bitte gib deinen Namen an, damit wir das Sackerl beschriften können.';
const FEHLER_STUECK = 'Bitte zwischen 1 und 40 Stück.';
const PECAT = 'Krume · Für dich';

export function init() {
  const forma = document.querySelector('[data-sackerl]');
  if (!forma) return;
  const brot = forma.querySelector('#f-brot');
  const stueck = forma.querySelector('#f-stueck');
  const name = forma.querySelector('#f-name');
  const danke = forma.querySelector('[data-danke]');
  const napomena = forma.querySelector('[data-napomena]');
  const pecat = forma.querySelector('[data-pecat]');

  function greska(polje, poruka) {
    const p = document.getElementById(`${polje.id}-fehler`);
    if (poruka) {
      p.textContent = poruka;
      p.hidden = false;
      polje.setAttribute('aria-invalid', 'true');
      polje.setAttribute('aria-describedby', p.id);
    } else {
      p.textContent = '';
      p.hidden = true;
      polje.removeAttribute('aria-invalid');
      polje.removeAttribute('aria-describedby');
    }
  }

  const broj = () => {
    const v = Number(stueck.value);
    return Number.isInteger(v) && v >= MIN && v <= MAX ? v : null;
  };

  function resetuj() {
    if (danke.textContent) {
      danke.textContent = '';
      napomena.hidden = false;
      pecat.textContent = PECAT;
      pecat.classList.remove('je-reserviert');
    }
  }

  forma.addEventListener('click', (e) => {
    const b = e.target.closest('[data-schritt]');
    if (!b) return;
    const v = (broj() ?? MIN) + Number(b.dataset.schritt);
    stueck.value = String(Math.min(MAX, Math.max(MIN, v)));
    greska(stueck, null);
    resetuj();
  });

  forma.addEventListener('input', (e) => {
    if (e.target === name && name.value.trim()) greska(name, null);
    if (e.target === stueck && broj() !== null) greska(stueck, null);
    resetuj();
  });

  forma.addEventListener('submit', (e) => {
    e.preventDefault();
    const ime = name.value.trim();
    const n = broj();
    greska(name, ime ? null : FEHLER_NAME);
    greska(stueck, n === null ? FEHLER_STUECK : null);
    if (!ime) return name.focus();
    if (n === null) return stueck.focus();

    danke.textContent = `Reserviert, ${ime}: ${n} × ${brot.value}, morgen ab 6:30. (Konzept: Hier käme die Bestellung bei der Bäckerei an.)`;
    napomena.hidden = true; // ista rečenica je već u poruci
    pecat.textContent = 'Reserviert';
    pecat.classList.add('je-reserviert');
  });
}
