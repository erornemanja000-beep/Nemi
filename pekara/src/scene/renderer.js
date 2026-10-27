// WebGL scena na fiksnom <canvas id="scena">.
// Zapečeno svetlo (Cycles bake) se prikazuje kao MeshBasicMaterial bez svetala (world.js):
// albedo × dekodirani lightmap, pa AgX u samom materijalu. renderer.toneMapping ostaje
// NoToneMapping namerno: sa EffectComposer-om three ne radi tone mapping u render target, a nebo,
// magla i čestice su zadati kao boje ekrana i ne smeju kroz AgX. Izlaz je sRGB u FinalPass-u.
//
// Post-obrada (EffectComposer, HalfFloat):
//   RenderPass → UnrealBloom (prag na najvećem kanalu posle AgX-a: hvata lampe, izlog i žar, ne
//   fasade; isključen ispod 768 px) → FinalPass: tilt-shift (jedan blur pas u pola rezolucije +
//   maska), žar peći (topli sjaj iz otvora peći preko ~40% kadra + topla vinjeta), pretapanje u
//   svetlo (kraj koraka Ofen), vinjeta, sRGB izlaz.
//
// Petlja ide na GSAP ticker-u. Kad se kamera ili scena menjaju, crta se svaki tik; kad se
// kreću samo čestice i treperenje, najviše ~30 kadrova u sekundi. Pauza kad je tab skriven,
// canvas van vida ili je mod 'static'.

import * as THREE from 'three';
import gsap from 'gsap';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { Pass, FullScreenQuad } from 'three/examples/jsm/postprocessing/Pass.js';

// Prag 0,88: hvata jezgro izloga i žara (topli tone mapping ide do ~1,18 u crvenom) i prozore,
// ne ulične lampe (stišane u world.js) ni fasade.
const BLOOM = { strength: 0.32, radius: 0.5, threshold: 0.88 };
const BLOOM_MIN_WIDTH = 768; // ispod ovoga nema bloom-a (telefon)
const IDLE_FPS = 30;

export function isMobile() {
  return matchMedia('(pointer: coarse)').matches || Math.min(screen.width, screen.height) < 600;
}

const QUAD_VS = /* glsl */ `
  varying vec2 vUv;
  void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

/** Tilt-shift + žar + vinjeta + izlaz u sRGB, u jednom pasu (plus blur u pola rezolucije). */
class FinalPass extends Pass {
  constructor({ taps }) {
    super();
    this.half = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, depthBuffer: false });
    this.blurMat = new THREE.ShaderMaterial({
      defines: { TAPS: taps },
      uniforms: { tDiffuse: { value: null }, uTexel: { value: new THREE.Vector2(1, 1) }, uRadius: { value: 1 } },
      vertexShader: QUAD_VS,
      fragmentShader: /* glsl */ `
        uniform sampler2D tDiffuse; uniform vec2 uTexel; uniform float uRadius;
        varying vec2 vUv;
        void main() {
          // disk sa zlatnim uglom: mek blur iz jednog pasa
          vec3 acc = texture2D(tDiffuse, vUv).rgb;
          float wsum = 1.0;
          for (int i = 1; i <= TAPS; i++) {
            float fi = float(i);
            float r = sqrt(fi / float(TAPS)) * uRadius;
            float a = fi * 2.39996;
            vec2 o = vec2(cos(a), sin(a)) * r * uTexel;
            float w = 1.0 - 0.5 * (fi / float(TAPS));
            acc += texture2D(tDiffuse, vUv + o).rgb * w;
            wsum += w;
          }
          gl_FragColor = vec4(acc / wsum, 1.0);
        }`,
      depthTest: false,
      depthWrite: false,
    });
    this.u = {
      tDiffuse: { value: null },
      tBlur: { value: this.half.texture },
      uTilt: { value: 1 },
      uBlur: { value: 0 },
      uFocus: { value: 0.52 },
      uBand: { value: 0.16 },
      uZar: { value: 0 },
      uZarBoja: { value: new THREE.Color('#ff7a2a') },
      uZarCentar: { value: new THREE.Vector2(0.5, 0.5) },
      uSvetlo: { value: 0 },
      uSvetloBoja: { value: new THREE.Color('#ffe2b8') },
      uVinjeta: { value: 0.22 },
      uAspect: { value: 1 },
    };
    this.finalMat = new THREE.ShaderMaterial({
      uniforms: this.u,
      vertexShader: QUAD_VS,
      fragmentShader: /* glsl */ `
        uniform sampler2D tDiffuse, tBlur;
        uniform float uTilt, uBlur, uFocus, uBand, uZar, uVinjeta, uAspect, uSvetlo;
        uniform vec3 uZarBoja, uSvetloBoja;
        uniform vec2 uZarCentar;
        varying vec2 vUv;
        void main() {
          vec3 c = texture2D(tDiffuse, vUv).rgb;
          float m = clamp(uBlur + uTilt * smoothstep(uBand, uBand + 0.32, abs(vUv.y - uFocus)), 0.0, 1.0);
          if (m > 0.001) c = mix(c, texture2D(tBlur, vUv).rgb, m);
          vec2 q = (vUv - 0.5) * vec2(uAspect, 1.0);
          float r = length(q) / length(vec2(uAspect, 1.0) * 0.5);
          // žar peći: sjaj iz otvora peći (uZarCentar) zahvata ~40% kadra; dodaje se kao svetlo
          // (screen), pa tamni delovi dobijaju toplinu, a svetli ne izgore u belo
          vec2 dz = (vUv - uZarCentar) * vec2(uAspect, 1.0);
          float rz = length(dz) / length(vec2(uAspect, 1.0) * 0.5);
          float g = uZar * (exp(-rz * rz * 5.5) + 0.04);
          c = 1.0 - (1.0 - min(c, 1.0)) * (1.0 - min(uZarBoja * g, 0.95)) + max(c - 1.0, 0.0);
          // topla vinjeta: ivice tamne i crvenkaste dok žar gori
          float vin = (uVinjeta + uZar * 0.45) * smoothstep(0.4, 1.05, r);
          c *= 1.0 - vin * mix(vec3(1.0), vec3(0.55, 0.8, 1.0), uZar);
          // pretapanje u svetlo (kraj koraka Ofen → izlog)
          c = mix(c, uSvetloBoja, uSvetlo);
          vec4 o = sRGBTransferOETF(vec4(max(c, 0.0), 1.0));
          // malo šuma protiv traka u gradijentu neba
          float n = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
          o.rgb += (n - 0.5) / 255.0;
          gl_FragColor = o;
        }`,
      depthTest: false,
      depthWrite: false,
    });
    this.quad = new FullScreenQuad(this.blurMat);
  }

  setSize(w, h) {
    this.half.setSize(Math.max(1, w >> 1), Math.max(1, h >> 1));
    this.blurMat.uniforms.uTexel.value.set(2 / w, 2 / h);
    // radijus u pikselima pola rezolucije, srazmeran visini (isti izgled na svakom ekranu)
    this.blurMat.uniforms.uRadius.value = Math.max(2, (h / 2) * 0.006);
    this.u.uAspect.value = w / Math.max(1, h);
  }

  render(renderer, writeBuffer, readBuffer) {
    const u = this.u;
    if (u.uTilt.value > 0.001 || u.uBlur.value > 0.001) {
      this.blurMat.uniforms.tDiffuse.value = readBuffer.texture;
      // jači opšti blur (forma u poglavlju 7) širi disk
      this.blurMat.uniforms.uRadius.value = Math.max(2, (this.half.height) * 0.006) * (1 + 1.5 * u.uBlur.value);
      renderer.setRenderTarget(this.half);
      this.quad.material = this.blurMat;
      this.quad.render(renderer);
    }
    u.tDiffuse.value = readBuffer.texture;
    renderer.setRenderTarget(this.renderToScreen ? null : writeBuffer);
    this.quad.material = this.finalMat;
    this.quad.render(renderer);
  }

  dispose() {
    this.half.dispose();
    this.blurMat.dispose();
    this.finalMat.dispose();
    this.quad.dispose();
  }
}

export function createRenderer(bus, canvas) {
  const mobile = isMobile();
  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: false, // AA ide preko MSAA u render target-u composer-a (desktop)
    alpha: false,
    powerPreference: 'high-performance',
  });
  const dpr = Math.min(window.devicePixelRatio || 1, mobile ? 1.5 : 2);
  renderer.setPixelRatio(dpr);
  renderer.toneMapping = THREE.NoToneMapping; // AgX je u materijalima (world.js), vidi gore
  renderer.localClippingEnabled = true; // tramvaj izlazi iz ivice daske
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#14263f');

  let cam = null; // modul kamere (createCamera)
  let sky = null;
  let composer = null;
  let bloom = null;
  let final = null;
  let w = 1;
  let h = 1;
  let dirty = true;
  let running = false;
  let inView = true;
  let destroyed = false;
  let staticMode = bus.get('mode') === 'static';
  let lastDraw = -1;
  let bloomStrength = BLOOM.strength;
  const updaters = [];

  function bloomAllowed() {
    return w >= BLOOM_MIN_WIDTH;
  }

  function buildComposer(camera) {
    const rt = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, samples: mobile ? 0 : 4 });
    composer = new EffectComposer(renderer, rt);
    composer.setPixelRatio(dpr);
    composer.addPass(new RenderPass(scene, camera));
    bloom = new UnrealBloomPass(new THREE.Vector2(w, h), BLOOM.strength, BLOOM.radius, BLOOM.threshold);
    // Prag na najvećem kanalu, ne na luminansi: topla emisija posle AgX-a (~0,9; 0,6; 0,3) prelazi
    // prag u crvenom i dobija sjaj; zapečene fasade ostaju ispod (i danju).
    const hp = bloom.materialHighPassFilter;
    hp.fragmentShader = hp.fragmentShader.replace('float v = luminance( texel.xyz );', 'float v = max( texel.r, max( texel.g, texel.b ) );');
    hp.uniforms.smoothWidth.value = 0.08;
    hp.needsUpdate = true;
    composer.addPass(bloom);
    final = new FinalPass({ taps: mobile ? 10 : 14 });
    composer.addPass(final);
    composer.setSize(w, h);
  }

  function syncBloom() {
    if (!bloom) return;
    bloom.enabled = bloomAllowed() && bloomStrength > 0.001;
    bloom.strength = bloomStrength;
  }

  // ---- etikete hlebova: projekcija u ekranske koordinate (CSS px, viewport)
  const ndc = new THREE.Vector3();
  let rect = { left: 0, top: 0 };
  let lastLabels = [];

  function projectLabels() {
    if (!cam?.breads.length) return;
    let changed = lastLabels.length !== cam.breads.length;
    const labels = cam.breads.map((b, i) => {
      ndc.copy(b.pos).project(cam.camera);
      const x = rect.left + ((ndc.x + 1) / 2) * w;
      const y = rect.top + ((1 - ndc.y) / 2) * h;
      const visible = ndc.z > -1 && ndc.z < 1 && ndc.x > -1.05 && ndc.x < 1.05 && ndc.y > -1.05 && ndc.y < 1.05;
      const old = lastLabels[i];
      if (!old || old.visible !== visible || Math.abs(old.x - x) > 0.5 || Math.abs(old.y - y) > 0.5) changed = true;
      return { n: b.n, name: b.name, x, y, visible };
    });
    if (changed) {
      lastLabels = labels;
      bus.set('labels', labels);
    }
  }

  // ---- petlja (na GSAP ticker-u, isti takt kao Lenis i quickTo)
  // updater(time, dt) vraća 0 (ništa), 1 (samo se animira: može ređe) ili 2 (promena: crtaj odmah)
  function step(time, dt) {
    let need = dirty ? 2 : 0;
    if (cam.update()) need = 2;
    for (const fn of updaters) {
      const r = fn(time, dt);
      if (r > need) need = r;
    }
    return need;
  }

  const zarNdc = new THREE.Vector3();
  let zarTacka = null;
  function draw(time) {
    sky?.follow(cam.camera);
    if (zarTacka && final.u.uZar.value > 0.001) {
      zarNdc.copy(zarTacka).project(cam.camera);
      if (zarNdc.z < 1) final.u.uZarCentar.value.set(Math.min(1.2, Math.max(-0.2, zarNdc.x * 0.5 + 0.5)), Math.min(1.2, Math.max(-0.2, zarNdc.y * 0.5 + 0.5)));
    }
    composer.render();
    lastDraw = time;
    dirty = false;
  }

  function frame(time, deltaMs) {
    if (!cam || !composer || staticMode) return;
    const need = step(time, deltaMs / 1000);
    if (need === 2) {
      draw(time);
      projectLabels();
    } else if (need === 1 && time - lastDraw >= 1 / IDLE_FPS - 0.004) {
      draw(time);
    }
  }

  function setRunning(on) {
    on = on && inView && !document.hidden && !destroyed && !staticMode && !!cam;
    if (on === running) return;
    running = on;
    if (on) {
      dirty = true;
      gsap.ticker.add(frame);
    } else gsap.ticker.remove(frame);
  }

  const onVisibility = () => setRunning(true);
  document.addEventListener('visibilitychange', onVisibility);
  const io = new IntersectionObserver((entries) => {
    inView = entries[entries.length - 1].isIntersecting;
    setRunning(true);
  });
  io.observe(canvas);

  // [data-mode=static]: #scena se ne renderuje
  const offMode = bus.on('mode', (m) => {
    staticMode = m === 'static';
    setRunning(true);
  });

  function resize(width, height) {
    w = Math.max(1, Math.round(width));
    h = Math.max(1, Math.round(height));
    renderer.setSize(w, h, false);
    composer?.setSize(w, h);
    syncBloom();
    cam?.resize(w, h);
    const r = canvas.getBoundingClientRect(); // samo na resize, ne u petlji
    rect = { left: r.left, top: r.top };
    dirty = true;
  }
  const ro = new ResizeObserver((entries) => {
    const box = entries[entries.length - 1].contentRect;
    resize(box.width || window.innerWidth, box.height || window.innerHeight);
  });
  ro.observe(canvas);

  /** Probni FPS: crta n kadrova zaredom (sa celom post-obradom) i vraća prosek. */
  function probe(n = 30) {
    return new Promise((resolve) => {
      const skip = 5; // prvi kadrovi nose upload tekstura
      let i = 0;
      let t0 = 0;
      const tick = (t) => {
        if (destroyed || !cam) return resolve(0);
        step(t / 1000, 16);
        draw(t / 1000);
        i++;
        if (i === skip) t0 = t;
        if (i >= n) return resolve(((n - skip) * 1000) / Math.max(1, t - t0));
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }

  /** Post-obrada (za timeline.js). Sve vrednosti 0–1 osim bloom (jačina). */
  const post = {
    tilt(v) { if (final) final.u.uTilt.value = v; dirty = true; },
    blur(v) { if (final) final.u.uBlur.value = v; dirty = true; },
    zar(v) { if (final) final.u.uZar.value = v; dirty = true; },
    /** Tačka u svetu iz koje sija žar (otvor peći); projektuje se pri crtanju dok žar gori. */
    zarTacka(v3) { zarTacka = v3 ? v3.clone() : null; dirty = true; },
    svetlo(v) { if (final) final.u.uSvetlo.value = v; dirty = true; },
    fokus(y, band) {
      if (!final) return;
      final.u.uFocus.value = y;
      if (band != null) final.u.uBand.value = band;
      dirty = true;
    },
    bloom(strength) { bloomStrength = strength; syncBloom(); dirty = true; },
    get bloomOn() { return !!bloom?.enabled; },
  };

  return {
    renderer,
    scene,
    mobile,
    dpr,
    post,
    probe,
    getCamera: () => cam?.camera,
    /** Za proveru: draw call-ovi scene (bez post-obrade) i celog kadra, trouglovi, memorija. */
    drawStats() {
      if (!cam || !composer) return null;
      const info = renderer.info;
      info.autoReset = false;
      info.reset();
      renderer.setRenderTarget(composer.renderTarget1);
      renderer.render(scene, cam.camera);
      renderer.setRenderTarget(null);
      const sceneCalls = info.render.calls;
      const triangles = info.render.triangles;
      info.reset();
      composer.render();
      const frameCalls = info.render.calls;
      info.autoReset = true;
      return { sceneCalls, frameCalls, triangles, textures: info.memory.textures, geometries: info.memory.geometries, programs: info.programs?.length };
    },
    /** Visina bafera u pikselima uređaja (za veličinu čestica). */
    get heightPx() { return h * dpr; },
    setSky(s) { sky = s; dirty = true; },
    addUpdater(fn) {
      updaters.push(fn);
      return () => updaters.splice(updaters.indexOf(fn) >>> 0, 1);
    },
    invalidate() { dirty = true; },
    /** Shaderi se kompajliraju pre prvog kadra, da probni FPS meri crtanje, a ne kompajliranje. */
    async compile() {
      if (cam) await renderer.compileAsync(scene, cam.camera);
      dirty = true;
    },
    /** Poveže modul kamere. */
    attach(camModule) {
      cam = camModule;
      if (!composer) buildComposer(cam.camera);
      const r = canvas.getBoundingClientRect();
      resize(r.width || window.innerWidth, r.height || window.innerHeight);
    },
    start() {
      setRunning(true);
    },
    destroy() {
      destroyed = true;
      setRunning(false);
      ro.disconnect();
      io.disconnect();
      offMode();
      document.removeEventListener('visibilitychange', onVisibility);
      composer?.renderTarget1.dispose();
      composer?.renderTarget2.dispose();
      bloom?.dispose();
      final?.dispose();
      renderer.dispose();
      renderer.forceContextLoss();
    },
  };
}
