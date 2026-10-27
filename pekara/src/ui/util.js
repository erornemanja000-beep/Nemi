// Zajedničko za UI module: mapa skrola (visine poglavlja) i provere ekrana/moda.

// Visine poglavlja u svh (studio/pekara/skice/mapa-skrola.md); 7 bez futera.
export const VISINA = { 1: 100, 2: 180, 3: 180, 4: 200, 5: 130, 6: 180, 7: 100 };

// Početak poglavlja u udelu skrola (mapa), samo kao rezerva dok ne stigne 'chapter'.
export const POCETAK = [0, 0.09, 0.25, 0.42, 0.6, 0.72, 0.88];

export const telefon = matchMedia('(max-width: 700px)');
export const smanjiPokret = matchMedia('(prefers-reduced-motion: reduce)');

export const je3d = () => document.documentElement.classList.contains('mode-3d');

export const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);

// { id, faza } iz udela celog sajta (kad 'chapter' još nije stigao)
export function poglavljeIz(p) {
  let i = 0;
  while (i + 1 < POCETAK.length && POCETAK[i + 1] <= p) i++;
  const kraj = POCETAK[i + 1] ?? 1;
  return { id: i + 1, faza: clamp((p - POCETAK[i]) / (kraj - POCETAK[i])) };
}

// '3d' / 'static' → klasa na <html>. undefined znači „još se ne zna": ostaje pretpostavka iz <head>.
export function primeniMod(mode) {
  if (mode !== '3d' && mode !== 'static') return false;
  const r = document.documentElement;
  r.classList.toggle('mode-3d', mode === '3d');
  r.classList.toggle('mode-static', mode !== '3d');
  return true;
}
