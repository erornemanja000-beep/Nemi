// Jedno zajedničko stanje između skrola (GSAP/Lenis) i 3D scene (useFrame).
// Namerno običan objekat, ne React state: menja se 60 puta u sekundi.
export const world = {
  intro: 0, // 0 → 1 kad se znak složi posle učitavanja
  dive: 0, // manifest: znak se rasklopi, kamera ulazi u jezgro, pa tunel
  workIn: 0, // galerija se pojavljuje oko kamere
  work: 0, // okretanje galerije kroz projekte
  outro: 0, // kontakt: znak se ponovo slaže
  outroMode: false, // true kad je vidljiv deo pri dnu (kontakt), a ne vrh strane
  mouse: { x: 0, y: 0 },
  velocity: 0, // brzina skrola (Lenis), za RGB pomak i brzinu tunela
  hover: -1, // projekat pod mišem
  count: 6, // broj projekata u galeriji
  mobile: false,
};

// Scena se crta samo kad se vidi (vrh strane ili kontakt); ostalo pokrivaju puni preseci
const listeners = new Set();
let visible = true;
export function setSceneVisible(v) {
  if (v === visible) return;
  visible = v;
  listeners.forEach((fn) => fn(v));
}
export function onSceneVisible(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export const smoothstep = (a, b, x) => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};
export const lerp = (a, b, t) => a + (b - a) * t;

// ?debug u adresi: stanje scene dostupno u konzoli (za proveru, ne smeta posetiocima)
if (typeof window !== 'undefined' && /[?&]debug\b/.test(window.location.search)) window.__kern = world;
