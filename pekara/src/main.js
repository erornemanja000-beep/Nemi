// Krume: ulaz. Odlučuje mod ('3d' | 'static'), pokreće skrol, scenu i kameru i UI module.
//
// '3d'     WebGL radi, nema prefers-reduced-motion, probni FPS prolazi → scena + kamera + Lenis
// 'static' bez WebGL-a, reduced motion ili spor uređaj → samo običan skrol (sat i tekstovi rade)
//
// Mod je i na <html data-mode="3d|static"> za CSS. Dok se ne odluči, atribut ne postoji.
// Za test: ?mode=3d ili ?mode=static preskače proveru (npr. headless browser bez GPU-a).

import bus from './core/bus.js';
import { initScroll } from './motion/scroll.js';

const BASE = import.meta.env.BASE_URL;
// Putanje do modela i tekstura su u src/scene/world.js (ASSETS).
const CAMERA_DATA = `${BASE}data/kamera.json`; // put kamere iz Blendera (bake_izvoz.py)
const MIN_FPS = 20;
const UI_ORDER = ['nav', 'clock', 'chapters', 'labels', 'form'];

const reducedMq = matchMedia('(prefers-reduced-motion: reduce)');
const forced = new URLSearchParams(location.search).get('mode');

let scroll = null;
let three = null; // { renderer, camera }
let starting = null;

function setMode(mode) {
  document.documentElement.dataset.mode = mode;
  bus.set('mode', mode);
  // statični kadrovi (programer C: drugi poziv init-a ne radi ništa)
  if (mode === 'static') import('./static/fallback.js').then((m) => m.init(bus)).catch((err) => console.error('[static]', err));
}

function webglAvailable() {
  try {
    const c = document.createElement('canvas');
    // Softverski WebGL (major performance caveat) se računa kao „nema WebGL-a".
    const opts = { failIfMajorPerformanceCaveat: forced !== '3d' };
    const gl = c.getContext('webgl2', opts) || c.getContext('webgl', opts);
    if (!gl) return false;
    gl.getExtension('WEBGL_lose_context')?.loseContext();
    return true;
  } catch {
    return false;
  }
}

function getCanvas() {
  let canvas = document.getElementById('scena');
  if (!canvas) {
    // Rezerva dok index.html nema canvas: fiksni sloj iza sadržaja.
    canvas = document.createElement('canvas');
    canvas.id = 'scena';
    canvas.setAttribute('aria-hidden', 'true');
    canvas.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;display:block;z-index:-1';
    document.body.prepend(canvas);
  }
  return canvas;
}

// UI moduli (programer C). Uvoze se samo oni koji postoje, svaki dobija bus.
const uiModules = import.meta.glob('./ui/*.js');
async function initUI() {
  for (const name of UI_ORDER) {
    const load = uiModules[`./ui/${name}.js`];
    if (!load) continue;
    try {
      const mod = await load();
      mod.init?.(bus);
    } catch (err) {
      console.error(`[ui/${name}]`, err);
    }
  }
}

function stop3D() {
  if (!three) return;
  three.timeline?.destroy?.();
  three.offs?.forEach((f) => f());
  three.particles?.destroy();
  three.sky?.destroy();
  three.world?.destroy();
  three.camera?.destroy();
  three.renderer?.destroy();
  bus.set('scena', null);
  three = null;
  scroll?.setSmooth(false);
}

async function start3D() {
  const [{ createRenderer }, { createCamera }, { createWorld }, { createSky }, { createParticles }] = await Promise.all([
    import('./scene/renderer.js'),
    import('./motion/camera.js'),
    import('./scene/world.js'),
    import('./scene/sky.js'),
    import('./scene/particles.js'),
  ]);
  const res = await fetch(CAMERA_DATA);
  if (!res.ok) throw new Error(`kamera.json: ${res.status}`);
  const data = await res.json();

  three = {};
  const rend = (three.renderer = createRenderer(bus, getCanvas()));
  three.camera = createCamera(bus, data);
  rend.attach(three.camera);
  three.sky = createSky(rend.scene, { far: data.far ?? 600 });
  rend.setSky(three.sky);
  three.world = createWorld(bus, rend, { kriska: data.kriska, dim: data.dim });
  await three.world.load();
  if (!three) return;
  three.particles = createParticles(rend.scene, { mobile: rend.mobile });
  wireScene(three);
  await startTimeline(three.api); // prvi kadar već u stanju koreografije
  await rend.compile();

  if (forced !== '3d') {
    const fps = await rend.probe(30);
    if (fps < MIN_FPS) throw new Error(`probni FPS ${fps.toFixed(1)} < ${MIN_FPS}`);
  }
  if (!three) return; // u međuvremenu prebačeno u statično
  rend.start();
  scroll.setSmooth(true);
  setMode('3d');
  if (import.meta.env.DEV) window.__krume = three; // samo dev server: provera iz konzole
}

function wireScene(t) {
  const { renderer: rend, camera: cam, world, sky, particles } = t;
  particles.setChimney(world.chimney());
  particles.uniforms.dim.uWind.value.copy(world.wind());
  let flourAt = null;
  const placeFlour = (where) => {
    if (where === flourAt && where !== 'reload') return;
    const box = world.flourBox(where === 'reload' ? flourAt ?? 'sto' : where);
    if (where !== 'reload') flourAt = where;
    if (box) particles.setInterior(box);
  };
  placeFlour('otvor');

  // Etikete: tačke hlebova prate prave hlebove (Hleb_1..4) i njihovo uveličanje.
  const syncBreads = () => {
    cam.breads.forEach((b) => world.api.hlebTacka(b.n, b.pos));
  };
  t.offs = [
    bus.on('enterijer', () => {
      placeFlour('reload');
      syncBreads();
      rend.post.zarTacka(world.zarTacka());
      rend.invalidate();
    }),
  ];

  rend.addUpdater((time) => (world.update(time) ? 2 : 1)); // 1: prozori i lampe trepere
  rend.addUpdater((time) => particles.update(time, cam.camera, rend.heightPx));

  const st = { dan: 0, vece: 0, dim: 1 };
  const w = world.api;
  /** Jedan objekat za timeline.js (world api + nebo, čestice, post-obrada, takt). */
  t.api = {
    ...w,
    mobile: rend.mobile,
    kriskaData: cam.kriska, // u_izvuci, u_spusti, u_napolju iz kamera.json
    /** Omekšan položaj na krivoj kamere (0–1): koreografija ide po njemu. */
    getU: () => cam.u,
    addUpdater: rend.addUpdater,
    invalidate: rend.invalidate,
    // dan menja i lightmap, i nebo/maglu, i boju dima
    dan(v) {
      st.dan = v;
      w.dan(v);
      sky.set(v, st.vece);
      particles.setDim(st.dim, v);
    },
    vece(v) {
      st.vece = v;
      sky.set(st.dan, v);
    },
    dim(v) {
      st.dim = v;
      particles.setDim(v, st.dan);
    },
    brasno: (v) => particles.setBrasno(v),
    /** Gde lebdi brašno: 'otvor' (presek, pogl. 3) ili 'sto' (enterijer). */
    brasnoMesto: placeFlour,
    syncBreads,
    tilt: rend.post.tilt,
    blur: rend.post.blur,
    zar: rend.post.zar,
    svetlo: rend.post.svetlo,
    fokus: rend.post.fokus,
    bloom: rend.post.bloom,
    drawStats: rend.drawStats,
    sky,
    particles,
  };
  bus.set('scena', t.api);
}

async function startTimeline(api) {
  const mod = await import('./motion/timeline.js');
  if (!three) return;
  three.timeline = mod.init(bus, api);
}

function decide() {
  const want3D = forced === '3d' || (forced !== 'static' && !reducedMq.matches && webglAvailable());
  if (!want3D) {
    stop3D();
    setMode('static');
    return;
  }
  if (three || starting) return;
  starting = start3D()
    .catch((err) => {
      console.info('[krume] statični prikaz:', err.message);
      stop3D();
      setMode('static');
    })
    .finally(() => {
      starting = null;
    });
}

async function boot() {
  bus.set('activeBread', 1);
  await initUI();
  // Skrol odmah, bez Lenisa: sat i tekstovi rade i dok se scena učitava.
  scroll = initScroll(bus, { smooth: false });
  decide();
  // Korisnik uključi/isključi smanjeno kretanje dok je stranica otvorena.
  reducedMq.addEventListener('change', decide);
}

boot();
