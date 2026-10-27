// Kamera po krivoj iz Blendera (kamera.json), vođena poglavljima skrola, sa inercijom.
//
// kamera.json (bake_izvoz.py):
//   param     'index': u = indeks tačke / (n-1); kriva je već uzorkovana po skrolu, sa
//             zadržavanjem na kadru svakog poglavlja (chapters[].drzi)
//   points[], targets[]  pozicija kamere i tačka u koju gleda (glTF, Y gore, metri)
//   chapters  [{ id, u, drzi:[u0,u1], pogl, cilj, lens, shift_x, shift_y, tel_cilj, tel_blize,
//             tel_shift_y, stanice? }]; poglavlje 4 ima stanice (Teig, Zeit, Ofen) sa svojim lens/drzi
//   sensor    mm na dužoj strani kadra (podrazumevano 36, Blender sensor fit AUTO)
//   breads    [{ name, pos }] hlebovi za etikete; pivot [x,y,z] osa „torte" za vodoravni drag
//
// Optika i telefon: vrednosti važe tačno u `drzi` opsegu ključnog kadra (poglavlje ili stanica),
// a između dva opsega se pretapaju (smoothstep).
//   desktop  kadar 16:10 iz Blendera ostaje ceo u ekranu (šire: isti vertikalni ugao, uže: isti
//            vodoravni); shift_x/shift_y kao u Blenderu (deo duže strane kadra, + pomera kadar)
//   telefon  (uspravan ekran) kadar 9:16 kao u kvart.py: cilj = tel_cilj, kamera na
//            tel_cilj + (pogl − cilj) · tel_blize, shift_x 0, shift_y = tel_shift_y.
//            Na putu se isto primenjuje kao pomak: cilj' = cilj + d(u), poz' = cilj' + (poz − cilj) · b(u).
//   Shift ide preko setViewOffset (i x i y): filmOffset u three je tačan samo za lens = senzor.
//
// Poglavlje 5 (desktop): kadar se dodatno pomera (view offset) tako da sve četiri tačke hlebova
// budu levo od kolone etiketa (x < BREAD_MAX_X · širina) i desno od teksta (x > BREAD_MIN_X).
// Pomak se računa iz projekcije tačaka (matematika, bez čitanja layout-a) i raste sa s.bw.
//
// `u` (omekšan, 0–1) je izložen: timeline.js vezuje koreografiju za isti u kao kameru, pa kriška
// i kamera nikad ne idu jedna kroz drugu.

import * as THREE from 'three';
import gsap from 'gsap';

const DEG = Math.PI / 180;
const MAX_YAW = 25 * DEG;
const EASE = 'power3.out'; // --ease-camera u tokens.css
const DUR = 0.8;
const REF_WIDE = 16 / 10; // Blender kadar za desktop
const REF_TALL = 9 / 16; // Blender kadar za telefon
const BREAD_MAX_X = 0.6; // 864 px na 1440: kolona etiketa počinje oko 1000 px
const BREAD_MIN_X = 0.22; // levo je tekst poglavlja
const INTERACTIVE = 'a, button, input, select, textarea, label, summary, form, [contenteditable], [data-no-drag]';

const v3 = (a) => new THREE.Vector3(a[0], a[1], a[2]);
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const sstep = (a, b, x) => {
  const t = clamp((x - a) / Math.max(1e-6, b - a), 0, 1);
  return t * t * (3 - 2 * t);
};

export function createCamera(bus, data) {
  const camera = new THREE.PerspectiveCamera(data.fov ?? 30, 1, data.near ?? 0.1, data.far ?? 600);
  const posCurve = new THREE.CatmullRomCurve3(data.points.map(v3), false, 'centripetal');
  const tgtCurve = new THREE.CatmullRomCurve3(data.targets.map(v3), false, 'centripetal');
  const byLength = data.param === 'length';
  const pivot = v3(data.pivot ?? [0, 0, 0]);
  const chapters = [...data.chapters].sort((a, b) => a.id - b.id);
  const breads = (data.breads ?? []).map((b) => v3(b.pos));
  // tačke za etikete (main.js ih pomera na prave hlebove); iste objekte koristi i pomak kadra
  const breadList = (data.breads ?? []).map((b, i) => ({ n: i + 1, name: b.name, pos: breads[i].clone() }));
  const sensor = data.sensor ?? 36;
  camera.filmGauge = sensor;

  // ---- ključni kadrovi: poglavlja, a poglavlje sa stanicama daje po jedan kadar za svaku
  const keys = [];
  for (const c of chapters) {
    const base = {
      lens: c.lens ?? data.lens ?? null,
      fov: c.fov ?? data.fov ?? 30,
      sx: c.shift_x ?? 0,
      sy: c.shift_y ?? 0,
      tsy: c.tel_shift_y ?? c.shift_y ?? 0,
      td: c.tel_cilj && c.cilj ? v3(c.tel_cilj).sub(v3(c.cilj)) : new THREE.Vector3(),
      tb: c.tel_blize ?? 1,
    };
    const list = c.stanice?.length ? c.stanice : [c];
    for (const s of list) {
      const h = s.drzi ?? [s.u ?? c.u, s.u ?? c.u];
      keys.push({ ...base, lens: s.lens ?? base.lens, fov: s.fov ?? base.fov, h0: h[0], h1: h[1] });
    }
  }
  keys.sort((a, b) => a.h0 - b.h0);

  /** Indeksi i težina (i, j, t) za u: t = 0 → kadar i, t = 1 → kadar j. */
  const blend = { i: 0, j: 0, t: 0 };
  function keyAt(u) {
    let i = 0;
    while (i + 1 < keys.length && keys[i + 1].h0 <= u) i++;
    const a = keys[i];
    const b = keys[i + 1];
    blend.i = i;
    blend.j = b ? i + 1 : i;
    blend.t = b && u > a.h1 ? sstep(a.h1, b.h0, u) : 0;
    return blend;
  }

  // s.u / s.yaw / s.bw se omekšavaju (quickTo); kamera se računa samo iz njih.
  const s = { u: uFor(bus.get('chapter') ?? { id: 1, faza: 0 }), uCilj: 0, yaw: 0, bw: 0, fx: 0, fy: 0, fz: 0 };
  s.uCilj = s.u;
  const quick = (prop, dur = DUR) => gsap.quickTo(s, prop, { duration: dur, ease: EASE });
  const qU = quick('u');
  const qYaw = quick('yaw');
  const qBw = quick('bw', 1.2);
  const qFx = quick('fx', 1.2);
  const qFy = quick('fy', 1.2);
  const qFz = quick('fz', 1.2);

  function uFor({ id, faza }) {
    const i = chapters.findIndex((c) => c.id === id);
    if (i < 0) return chapters[0]?.u ?? 0;
    const a = chapters[i].u;
    const b = chapters[i + 1]?.u ?? 1;
    return a + (b - a) * faza;
  }

  function focusBread(n) {
    const p = breads[n - 1];
    if (!p) return;
    qFx(p.x);
    qFy(p.y);
    qFz(p.z);
  }

  const offs = [
    bus.on('chapter', (ch) => {
      s.uCilj = uFor(ch);
      qU(s.uCilj);
      qBw(ch.id === 5 && breads.length ? 1 : 0);
    }),
    bus.on('activeBread', focusBread),
  ];
  if (breads.length) {
    const b0 = breads[(bus.get('activeBread') ?? 1) - 1] ?? breads[0];
    s.fx = b0.x; s.fy = b0.y; s.fz = b0.z;
  }

  // ---- vodoravni drag: „Dreh das Grätzl" (±25°, inercija, vraća se u osu)
  let drag = null;
  let homeCall = null;
  let width = window.innerWidth;
  const body = document.body;
  const prevTouch = body.style.touchAction;
  // Uspravni skrol ostaje skrol, vodoravni potez ide sceni; zum prstima ostaje.
  body.style.touchAction = 'pan-y pinch-zoom';

  function onDown(e) {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    if (e.target instanceof Element && e.target.closest(INTERACTIVE)) return;
    homeCall?.kill();
    drag = { id: e.pointerId, x0: e.clientX, y0: e.clientY, yaw0: s.yaw, on: false, yaw: s.yaw, lx: e.clientX, lt: e.timeStamp, vel: 0 };
  }
  function onMove(e) {
    if (!drag || e.pointerId !== drag.id) return;
    const dx = e.clientX - drag.x0;
    const dy = e.clientY - drag.y0;
    if (!drag.on) {
      if (Math.abs(dy) > 8 && Math.abs(dy) > Math.abs(dx)) { drag = null; return; }
      if (Math.abs(dx) < 8 || Math.abs(dx) < Math.abs(dy) * 1.2) return;
      drag.on = true;
      body.style.userSelect = 'none';
      window.getSelection()?.removeAllRanges();
    }
    // Cela širina ekrana = 50° (od -25° do +25°).
    drag.yaw = clamp(drag.yaw0 - (dx / width) * 2 * MAX_YAW, -MAX_YAW, MAX_YAW);
    const dt = Math.max(1, e.timeStamp - drag.lt);
    drag.vel = 0.8 * drag.vel + 0.2 * ((-(e.clientX - drag.lx) / width) * 2 * MAX_YAW / dt) * 1000;
    drag.lx = e.clientX;
    drag.lt = e.timeStamp;
    qYaw(drag.yaw);
  }
  function onUp(e) {
    if (!drag || e.pointerId !== drag.id) return;
    if (drag.on) {
      body.style.userSelect = '';
      qYaw(clamp(drag.yaw + drag.vel * 0.12, -MAX_YAW, MAX_YAW));
      homeCall = gsap.delayedCall(0.35, () => qYaw(0));
    }
    drag = null;
  }
  const onResize = () => { width = window.innerWidth; };
  window.addEventListener('pointerdown', onDown, { passive: true });
  window.addEventListener('pointermove', onMove, { passive: true });
  window.addEventListener('pointerup', onUp, { passive: true });
  window.addEventListener('pointercancel', onUp, { passive: true });
  window.addEventListener('resize', onResize, { passive: true });

  // ---- izračun kadra (bez čitanja layout-a)
  let vw = 1;
  let vh = 1;
  let tall = false;
  const pos = new THREE.Vector3();
  const tgt = new THREE.Vector3();
  const off = new THREE.Vector3();
  const focus = new THREE.Vector3();
  const lastPos = new THREE.Vector3(Infinity, 0, 0);
  const lastTgt = new THREE.Vector3();
  const yAxis = new THREE.Vector3(0, 1, 0);

  function update() {
    const u = clamp(s.u, 0, 1);
    if (byLength) {
      posCurve.getPointAt(u, pos);
      tgtCurve.getPointAt(u, tgt);
    } else {
      posCurve.getPoint(u, pos);
      tgtCurve.getPoint(u, tgt);
    }
    const k = keyAt(u);
    if (tall) {
      // telefon: cilj pomeren na tel_cilj, kamera bliže (tel_blize), kao kadar 9:16 u Blenderu
      const a = keys[k.i];
      const b = keys[k.j];
      off.copy(a.td).lerp(b.td, k.t);
      const blize = a.tb + (b.tb - a.tb) * k.t;
      pos.sub(tgt).multiplyScalar(blize);
      tgt.add(off);
      pos.add(tgt);
    }
    if (s.bw > 1e-4) {
      // U poglavlju 5 pogled blago klizi ka aktivnom hlebu (25%).
      focus.set(s.fx, s.fy, s.fz);
      tgt.lerp(focus, s.bw * 0.25);
    }
    if (Math.abs(s.yaw) > 1e-5) {
      pos.sub(pivot).applyAxisAngle(yAxis, s.yaw).add(pivot);
      tgt.sub(pivot).applyAxisAngle(yAxis, s.yaw).add(pivot);
    }
    let optChanged = applyOptics();
    const changed = optChanged || pos.distanceToSquared(lastPos) > 1e-8 || tgt.distanceToSquared(lastTgt) > 1e-8;
    if (changed) {
      camera.position.copy(pos);
      camera.lookAt(tgt);
      lastPos.copy(pos);
      lastTgt.copy(tgt);
    }
    if (breadShift()) optChanged = true;
    return changed || optChanged;
  }

  // ---- poglavlje 5: hlebovi levo od kolone etiketa
  const pr = new THREE.Vector3();
  let exX = 0; // dodatni vodoravni pomak kadra u px (+ = sadržaj ide levo)
  function breadShift() {
    let want = 0;
    if (!tall && s.bw > 1e-3 && breadList.length) {
      camera.updateMatrixWorld();
      let mn = Infinity;
      let mx = -Infinity;
      for (const b of breadList) {
        pr.copy(b.pos).project(camera);
        const x = ((pr.x + 1) / 2) * vw + exX; // položaj bez trenutnog pomaka
        if (x < mn) mn = x;
        if (x > mx) mx = x;
      }
      let need = Math.max(0, mx - BREAD_MAX_X * vw);
      need = Math.min(need, Math.max(0, mn - BREAD_MIN_X * vw));
      want = need * Math.min(1, s.bw);
    }
    if (Math.abs(want - exX) < 0.25) return false;
    exX = want;
    applyOptics(true);
    return true;
  }

  // ---- optika (fov + shift)
  const lastOpt = { fov: -1, ox: NaN, oy: NaN };

  // tan(pola vertikalnog ugla) za ključni kadar, tako da referentni kadar Blendera stane u ekran
  function tanHalfV(key, aspect) {
    // tan pola ugla na dužoj strani; bez lens-a iz vertikalnog fov-a kadra 16:10
    const half = key.lens != null ? sensor / 2 / key.lens : Math.tan((key.fov * DEG) / 2) * REF_WIDE;
    if (tall) return half * Math.max(1, REF_TALL / aspect); // uže od 9:16: čuva se vodoravni ugao
    return half / Math.min(aspect, REF_WIDE); // šire od 16:10: čuva se vertikalni ugao
  }

  function applyOptics(force = false) {
    const aspect = vw / Math.max(1, vh);
    const k = keyAt(clamp(s.u, 0, 1));
    const a = keys[k.i];
    const b = keys[k.j];
    const ta = tanHalfV(a, aspect);
    const tb = tanHalfV(b, aspect);
    const fov = (2 * Math.atan(ta + (tb - ta) * k.t)) / DEG;
    let ox;
    let oy;
    if (tall) {
      const refH = aspect < REF_TALL ? vw / REF_TALL : vh; // duža strana kadra 9:16 u pikselima
      ox = 0;
      oy = -(a.tsy + (b.tsy - a.tsy) * k.t) * refH;
    } else {
      const refW = aspect > REF_WIDE ? vh * REF_WIDE : vw;
      ox = (a.sx + (b.sx - a.sx) * k.t) * refW + exX;
      oy = -(a.sy + (b.sy - a.sy) * k.t) * refW;
    }
    if (!force && Math.abs(fov - lastOpt.fov) < 1e-4 && Math.abs(ox - lastOpt.ox) < 0.05 && Math.abs(oy - lastOpt.oy) < 0.05) return false;
    lastOpt.fov = fov;
    lastOpt.ox = ox;
    lastOpt.oy = oy;
    camera.aspect = aspect;
    camera.fov = fov;
    if (Math.abs(ox) > 0.01 || Math.abs(oy) > 0.01) camera.setViewOffset(vw, vh, ox, oy, vw, vh);
    else camera.clearViewOffset();
    camera.updateProjectionMatrix();
    return true;
  }

  function resize(w, h) {
    vw = w;
    vh = h;
    tall = w < h;
    applyOptics(true);
    lastPos.set(Infinity, 0, 0); // sledeći update sigurno crta
  }

  return {
    camera,
    breads: breadList,
    kriska: data.kriska ?? null,
    /** Omekšan položaj na krivoj (0–1), isti koji vodi kameru. */
    get u() { return clamp(s.u, 0, 1); },
    /** Cilj skrola (bez inercije). */
    get uCilj() { return s.uCilj; },
    get tall() { return tall; },
    update,
    resize,
    destroy() {
      offs.forEach((f) => f());
      homeCall?.kill();
      gsap.killTweensOf(s);
      window.removeEventListener('pointerdown', onDown);
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
      window.removeEventListener('pointercancel', onUp);
      window.removeEventListener('resize', onResize);
      body.style.touchAction = prevTouch;
      body.style.userSelect = '';
    },
  };
}
