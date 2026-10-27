// Čestice: dim iz dimnjaka pekare i brašno u enterijeru (poglavlja 4–5).
// Sve se kreće u vertex shaderu (uTime), CPU ne dira bafere posle pravljenja.
// Sprite je mek krug nacrtan u canvasu (bez slike). Na telefonu upola manje čestica.

import * as THREE from 'three';

const COUNT = { dim: 140, brasno: 360 };

function softSprite() {
  const s = 64;
  const c = document.createElement('canvas');
  c.width = c.height = s;
  const g = c.getContext('2d');
  const grd = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  grd.addColorStop(0, 'rgba(255,255,255,1)');
  grd.addColorStop(0.4, 'rgba(255,255,255,0.55)');
  grd.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grd;
  g.fillRect(0, 0, s, s);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.NoColorSpace; // samo alfa
  return t;
}

function seeds(n) {
  const a = new Float32Array(n * 4);
  for (let i = 0; i < a.length; i++) a[i] = Math.random();
  const g = new THREE.BufferGeometry();
  // pozicija je nebitna (računa se u shaderu), ali three je traži za broj tačaka
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  g.setAttribute('aSeed', new THREE.BufferAttribute(a, 4));
  return g;
}

const COMMON_VS = /* glsl */ `
  attribute vec4 aSeed;
  uniform float uTime, uScale, uAmount;
  varying float vAlpha;
`;

export function createParticles(scene, { mobile = false } = {}) {
  const k = mobile ? 0.5 : 1;
  const sprite = softSprite();
  const uScale = { value: 400 }; // px po metru na udaljenosti 1 (postavlja se iz kamere)
  const uTime = { value: 0 };

  // ---- dim
  const dimU = {
    uTime,
    uScale,
    uAmount: { value: 1 },
    uOrigin: { value: new THREE.Vector3(0, 10, 0) },
    uWind: { value: new THREE.Vector3(0.9, 0, -0.35) },
    uColor: { value: new THREE.Color('#56607a') },
    uMap: { value: sprite },
  };
  const dimMat = new THREE.ShaderMaterial({
    uniforms: dimU,
    transparent: true,
    depthWrite: false,
    vertexShader: /* glsl */ `${COMMON_VS}
      uniform vec3 uOrigin, uWind;
      void main() {
        float age = fract(uTime * 0.06 + aSeed.x);
        float a2 = age * age;
        vec3 p = uOrigin;
        p.y += age * 3.2;
        p += uWind * (a2 * 4.5 + age * 1.5);
        p.x += sin(uTime * 0.7 + aSeed.y * 6.28) * 0.35 * age + (aSeed.z - 0.5) * 0.25;
        p.z += cos(uTime * 0.5 + aSeed.w * 6.28) * 0.35 * age + (aSeed.w - 0.5) * 0.25;
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * mv;
        float size = mix(0.35, 2.6, age) * (0.7 + 0.6 * aSeed.y);
        gl_PointSize = size * uScale / max(0.1, -mv.z);
        vAlpha = smoothstep(0.0, 0.12, age) * pow(1.0 - age, 1.6) * uAmount * 0.42;
      }`,
    fragmentShader: /* glsl */ `
      uniform sampler2D uMap; uniform vec3 uColor;
      varying float vAlpha;
      void main() {
        float a = texture2D(uMap, gl_PointCoord).a * vAlpha;
        if (a < 0.004) discard;
        gl_FragColor = vec4(uColor, a);
      }`,
  });
  const dim = new THREE.Points(seeds(Math.round(COUNT.dim * k)), dimMat);
  dim.name = 'Dim';
  dim.frustumCulled = false;
  scene.add(dim);

  // ---- brašno (prah u toploj svetlosti enterijera)
  const brU = {
    uTime,
    uScale,
    uAmount: { value: 0 },
    uMin: { value: new THREE.Vector3(-1, 0, -1) },
    uSize: { value: new THREE.Vector3(2, 2, 2) },
    uColor: { value: new THREE.Color('#ffd9a8') },
    uMap: { value: sprite },
  };
  const brMat = new THREE.ShaderMaterial({
    uniforms: brU,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    vertexShader: /* glsl */ `${COMMON_VS}
      uniform vec3 uMin, uSize;
      void main() {
        // sporo lebdi i pada, pa se vraća na vrh (fract)
        vec3 q = aSeed.xyz;
        q.y = fract(q.y - uTime * (0.012 + 0.02 * aSeed.w));
        q.x = fract(q.x + sin(uTime * 0.21 + aSeed.w * 6.28) * 0.02);
        q.z = fract(q.z + cos(uTime * 0.17 + aSeed.x * 6.28) * 0.02);
        vec3 p = uMin + q * uSize;
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        gl_Position = projectionMatrix * mv;
        gl_PointSize = max(1.0, (0.012 + 0.02 * aSeed.w) * uScale / max(0.05, -mv.z));
        float edge = smoothstep(0.0, 0.15, q.y) * smoothstep(1.0, 0.8, q.y);
        float tw = 0.6 + 0.4 * sin(uTime * (1.0 + aSeed.x * 2.0) + aSeed.z * 30.0);
        vAlpha = edge * tw * uAmount * 0.5;
      }`,
    fragmentShader: /* glsl */ `
      uniform sampler2D uMap; uniform vec3 uColor;
      varying float vAlpha;
      void main() {
        float a = texture2D(uMap, gl_PointCoord).a * vAlpha;
        if (a < 0.004) discard;
        gl_FragColor = vec4(uColor, a); // aditivno: three množi sa alfom
      }`,
  });
  const brasno = new THREE.Points(seeds(Math.round(COUNT.brasno * k)), brMat);
  brasno.name = 'Brasno';
  brasno.frustumCulled = false;
  brasno.visible = false;
  scene.add(brasno);

  const nightSmoke = new THREE.Color('#56607a'); // noću blago osvetljen iz grada
  const daySmoke = new THREE.Color('#9aa0a8');
  let changed = true;

  return {
    dim,
    brasno,
    uniforms: { dim: dimU, brasno: brU },
    /** Odakle ide dim (vrh dimnjaka). */
    setChimney(v) {
      dimU.uOrigin.value.copy(v);
      changed = true;
    },
    /** Prostor u kome lebdi brašno (THREE.Box3). */
    setInterior(box) {
      if (!box || box.isEmpty()) return;
      brU.uMin.value.copy(box.min);
      box.getSize(brU.uSize.value);
      changed = true;
    },
    /** Jačina dima 0–1 i boja po danu. */
    setDim(v, dan = 0) {
      dimU.uAmount.value = v;
      dimU.uColor.value.copy(nightSmoke).lerp(daySmoke, dan);
      dim.visible = v > 0.001;
      changed = true;
    },
    /** Količina brašna 0–1 (poglavlja 4–5, puf u 3). */
    setBrasno(v) {
      brU.uAmount.value = v;
      brasno.visible = v > 0.001;
      changed = true;
    },
    /** Svakog kadra: vreme i razmera tačaka iz projekcije (bez čitanja layout-a). */
    update(time, camera, heightPx) { // heightPx: visina bafera u pikselima uređaja
      uTime.value = time;
      uScale.value = heightPx * 0.5 * camera.projectionMatrix.elements[5];
      const c = changed;
      changed = false;
      // 2: promena (crtaj odmah), 1: čestice se kreću same (crta se ređe), 0: ništa
      return c ? 2 : dim.visible || brasno.visible ? 1 : 0;
    },
    destroy() {
      scene.remove(dim, brasno);
      dim.geometry.dispose();
      brasno.geometry.dispose();
      dimMat.dispose();
      brMat.dispose();
      sprite.dispose();
    },
  };
}
