// Mali event bus + zajedničko stanje za sve module (scena, kamera, skrol, UI).
//
// Događaji / ključevi stanja:
//   progress     0–1, udeo skrola cele stranice
//   chapter      { id: 1–7, faza: 0–1 } aktivno poglavlje i koliko je prođeno
//   mode         '3d' | 'static' (undefined dok se ne odluči: UI tada prikazuje statično)
//   activeBread  1–4, aktivni hleb u poglavlju 5
//   labels       [{ n, name, x, y, visible }] ekranske koordinate hlebova (CSS px u odnosu na viewport)
//   scrollTo     funkcija (target, opts) za skrol na sekciju; radi i sa i bez Lenisa
//
// set(key, val) čuva vrednost i emituje događaj istog imena.
// Za primitivne vrednosti nema emitovanja ako se vrednost nije promenila.

const listeners = new Map();
const state = new Map();

export function on(evt, fn) {
  let set = listeners.get(evt);
  if (!set) listeners.set(evt, (set = new Set()));
  set.add(fn);
  return () => off(evt, fn);
}

export function off(evt, fn) {
  listeners.get(evt)?.delete(fn);
}

export function emit(evt, data) {
  const set = listeners.get(evt);
  if (!set) return;
  for (const fn of [...set]) {
    try {
      fn(data);
    } catch (err) {
      console.error(`[bus] ${evt}:`, err);
    }
  }
}

export function get(key) {
  return state.get(key);
}

export function set(key, val) {
  const old = state.get(key);
  const primitive = val === null || (typeof val !== 'object' && typeof val !== 'function');
  if (primitive && Object.is(old, val)) return;
  state.set(key, val);
  emit(key, val);
}

const bus = { on, off, emit, get, set };
export default bus;
