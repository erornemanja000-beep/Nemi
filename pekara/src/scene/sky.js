// Nebo: gradijent (zenit → horizont) na velikoj sferi oko kamere, od noći ka zori i jutru.
// uDan 0 = noć 04:00, 0,5 = zora 06:30, 1 = jutro 07:00; uVece 0–1 vraća nebo u veče (futer).
// Magla scene uzima boju horizonta, pa se kuće u daljini tope u nebo kao u Cycles kadrovima.
//
// Boje su izmerene u probnim renderima i proverene uz tekst (dizajn.md, kontrast):
// noć #12243b iza teksta, 06:30 #203d5f / #2f4f74, futer #0b1524. Brašno ostaje ≥ 4,5:1.

import * as THREE from 'three';

const C = (hex) => new THREE.Color(hex);
// [zenit, horizont, sjaj zore]
const NOC = [C('#0f1a2e'), C('#14263f'), C('#14263f')];
const ZORA = [C('#203d5f'), C('#2f4f74'), C('#a9806a')];
const JUTRO = [C('#3e5677'), C('#5d6f89'), C('#b49b86')];
const VECE = [C('#0b1524'), C('#121f33'), C('#121f33')];

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

export function createSky(scene, { far = 600 } = {}) {
  const uniforms = {
    uZenit: { value: NOC[0].clone() },
    uHorizont: { value: NOC[1].clone() },
    uSjaj: { value: NOC[2].clone() },
    uSjajJacina: { value: 0 },
    uIstok: { value: new THREE.Vector3(0.55, 0.05, -0.83).normalize() }, // gde sviće (iza bloka)
  };
  const mat = new THREE.ShaderMaterial({
    uniforms,
    side: THREE.BackSide,
    depthWrite: false,
    depthTest: false,
    fog: false,
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = normalize((modelMatrix * vec4(position, 0.0)).xyz);
        vec4 p = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
        gl_Position = p.xyww; // uvek na dalekoj ravni
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uZenit, uHorizont, uSjaj, uIstok;
      uniform float uSjajJacina;
      varying vec3 vDir;
      void main() {
        vec3 d = normalize(vDir);
        float h = smoothstep(-0.02, 0.55, d.y);
        vec3 c = mix(uHorizont, uZenit, h);
        float s = pow(max(dot(d, uIstok), 0.0), 3.0) * (1.0 - h);
        c = mix(c, uSjaj, s * uSjajJacina);
        gl_FragColor = vec4(c, 1.0);
      }`,
  });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(far * 0.5, 24, 12), mat);
  mesh.name = 'Nebo';
  mesh.renderOrder = -1;
  mesh.frustumCulled = false;
  scene.add(mesh);

  const fogColor = NOC[1].clone();
  scene.fog = new THREE.Fog(fogColor, 90, 260);
  scene.background = fogColor;

  const st = { dan: 0, vece: 0 };
  const tmp = [new THREE.Color(), new THREE.Color(), new THREE.Color()];

  function apply() {
    const d = st.dan;
    // noć → zora (0–0,5) → jutro (0,5–1), pa ka večeri
    const [a, b, t] = d < 0.5 ? [NOC, ZORA, d / 0.5] : [ZORA, JUTRO, (d - 0.5) / 0.5];
    for (let i = 0; i < 3; i++) tmp[i].copy(a[i]).lerp(b[i], t).lerp(VECE[i], st.vece);
    uniforms.uZenit.value.copy(tmp[0]);
    uniforms.uHorizont.value.copy(tmp[1]);
    uniforms.uSjaj.value.copy(tmp[2]);
    // sjaj zore je najjači oko 06:30 i blag (nebo iza teksta ne sme da posvetli)
    uniforms.uSjajJacina.value = Math.sin(Math.PI * clamp01(d * 1.2)) * 0.55 * (1 - st.vece);
    fogColor.copy(tmp[1]);
  }
  apply();

  return {
    mesh,
    uniforms,
    get dan() { return st.dan; },
    get vece() { return st.vece; },
    /** dan 0–1 (noć → jutro), vece 0–1 (futer) */
    set(dan, vece = st.vece) {
      dan = clamp01(dan);
      vece = clamp01(vece);
      if (dan === st.dan && vece === st.vece) return false;
      st.dan = dan;
      st.vece = vece;
      apply();
      return true;
    },
    /** Sfera prati kameru (bez paralakse). */
    follow(camera) {
      mesh.position.copy(camera.position);
    },
    destroy() {
      scene.remove(mesh);
      mesh.geometry.dispose();
      mat.dispose();
    },
  };
}
