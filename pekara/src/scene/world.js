// Svet scene: grad (blok + ulica) i enterijer pekare iz Blendera, sa zapečenim svetlom.
//
// Materijal: MeshBasicMaterial + onBeforeCompile.
//   albedo  baseColorTexture na uv (sRGB → linearno)
//   svetlo  lightmap na uv1, kodiran gamom 4: L = max * pow(texel, 4) (max iz scene.userData.krume)
//           noć → dan je mix dekodiranih L (uDan); enterijer ima samo noćni
//   boja    albedo × L (+ sjaj prozora), pa AgX u samom materijalu (tonemapping_pars iz three).
// Tone mapping je u materijalu, a ne na kraju lanca: nebo, magla i čestice su već zadate kao
// boje ekrana (dizajn.md), pa ne smeju kroz AgX. Magla ide posle AgX-a (isti red kao u three).
//
// Prozori: materijali sa userData.prozor; atribut `_wake` (u three `_wake`) je vreme buđenja.
// Sjaj #ffc27e × 2,2 gde je _wake < uTalas; pekara (_wake ≈ 0) svetli uvek (uIzlog).
// Svetleći delovi su deca `<ime>_ziv` (lampice, lampe, staklo izloga, tramvaj).
//
// „Ein Fenster brennt": AgX ispira zasićenu narandžastu u belo, pa pekara (sve pod čvorom Kriska:
// izlog, vrata, tabla, prozori stana iznad, lampice, staklo) i žar peći ne idu kroz AgX, nego kroz
// topli tone mapping (krumeWarm): svetlina → rampa #e8792b (ivica) → #ffb066 (jezgro). Udeo tople
// rampe raste sa svetlinom, pa tamni zidovi pekare ostaju AgX, a samo ono što svetli postaje toplo.
// Jezgro izlaza prelazi 1,0 u crvenom, pa ga bloom (prag na najvećem kanalu) hvata; ulične lampe
// su stišane (LAMP_GAIN) da ostanu ispod praga i slabije od pekare.
//
// Statični mesh-evi se spajaju po materijalu (manje draw call-ova); pokretni čvorovi ostaju.
// Upravljanje (za timeline.js): `api` na dnu createWorld. Vrednosti su 0–1 osim ako piše drugačije.

import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
// Jedan dekoder: glTF varijanta (WASM, manja). Vite deli isti fajl sa referencom iz DRACOLoader-a.
import DRACO_JS from 'three/examples/jsm/libs/draco/gltf/draco_wasm_wrapper.js?url';
import DRACO_WASM from 'three/examples/jsm/libs/draco/gltf/draco_decoder.wasm?url';

const BASE = import.meta.env.BASE_URL;

/**
 * SVE putanje do modela i tekstura na jednom mestu.
 * Lightmap ime: `${lightmap}-${noc|dan}-${atlas}[-m].webp`, npr. textures/grad-noc-0-m.webp.
 * Telefon uzima `-m` (1024); desktop puni (2048), osim ako je LIGHTMAP_DESKTOP_M.
 */
export const ASSETS = {
  grad: {
    model: `${BASE}models/grad.glb`,
    modelM: `${BASE}models/grad-m.glb`,
    lightmap: `${BASE}textures/grad`,
    dan: true,
  },
  enterijer: {
    model: `${BASE}models/enterijer.glb`,
    modelM: `${BASE}models/enterijer-m.glb`,
    lightmap: `${BASE}textures/enterijer`,
    dan: false, // enterijer ima samo noćni lightmap
  },
};
// Lightmap-ovi su mekani: i na desktopu može 1024 (-m) ako memorija ili FPS pate.
const LIGHTMAP_DESKTOP_M = false;

export function lightmapUrl(base, kind, atlas, mobile) {
  return `${base}-${kind}-${atlas ?? 0}${mobile ? '-m' : ''}.webp`;
}

const WINDOW_COLOR = new THREE.Color('#ffc27e').multiplyScalar(2.2); // linearno, pre AgX-a
const LAMP_GAIN = 0.5; // ulične lampe: ispod praga bloom-a, slabije od izloga
const PEK_Y = 4.6; // visina prizemlja pekare (m): toplo svetlo ispod, stan iznad samo kroz prozore
// Staklo izloga: toplo umesto plavičastog (#ffb066 linearno), malo gušće da oboji izlog.
const IZLOG_STAKLO = { color: new THREE.Color('#ffb066'), opacity: 0.24 };
const ENT_STAKLO = new THREE.Color('#f3dcc0'); // staklo vitrine u enterijeru: toplo neutralno
const DEG = Math.PI / 180;

// pokretni čvorovi: ne spajaju se
const DYNAMIC = /^(Kriska|Tramvaj|Figura_|Lampa_\d+_ziv|Dim_|PecVrata|Testo|Hleb_|Korpa_testo_)/;

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const smooth = (a, b, x) => {
  const t = clamp01((x - a) / (b - a));
  return t * t * (3 - 2 * t);
};

// ---- dohvatanje: 404 i HTML odgovor (SPA fallback dev servera) znače „fali", bez izuzetka
async function fetchOk(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    if ((res.headers.get('content-type') || '').includes('text/html')) return null;
    return res;
  } catch {
    return null;
  }
}

async function fetchGlb(url) {
  const res = await fetchOk(url);
  if (!res) return null;
  const buf = await res.arrayBuffer();
  if (buf.byteLength < 12) return null;
  const m = new Uint8Array(buf, 0, 4);
  return m[0] === 0x67 && m[1] === 0x6c && m[2] === 0x54 && m[3] === 0x46 ? buf : null; // 'glTF'
}

async function fetchLightmap(url) {
  const res = await fetchOk(url);
  if (!res) return null;
  try {
    const blob = await res.blob();
    // kao GLTFLoader: bez okretanja, bez konverzije boja (podatak, ne slika)
    const bmp = await createImageBitmap(blob, { premultiplyAlpha: 'none', colorSpaceConversion: 'none' });
    const tex = new THREE.Texture(bmp);
    tex.flipY = false;
    tex.colorSpace = THREE.NoColorSpace; // kodiran gamom 4, dekodira se u shaderu
    tex.channel = 1; // uv1
    tex.generateMipmaps = true;
    tex.minFilter = THREE.LinearMipmapLinearFilter;
    tex.needsUpdate = true;
    return tex;
  } catch {
    return null;
  }
}

// AgX iz three (isti kod kao renderer.toneMapping = AgXToneMapping), ubačen u materijal.
const AGX_PARS = THREE.ShaderChunk.tonemapping_pars_fragment;
// Topli tone mapping za pekaru i žar (vidi vrh fajla). Ulaz linearni HDR, izlaz linearni ekran.
const WARM_PARS = /* glsl */ `
  vec3 krumeWarm( vec3 c ) {
    float l = dot( c, vec3( 0.2126, 0.7152, 0.0722 ) );
    float t = 1.0 - exp( -1.5 * l );
    vec3 ivica = vec3( 0.807, 0.191, 0.024 );  // #e8792b
    vec3 jezgro = vec3( 1.0, 0.434, 0.133 );   // #ffb066
    return mix( ivica, jezgro, smoothstep( 0.35, 0.95, t ) ) * t * 1.18;
  }
  float krumeLum( vec3 c ) { return dot( c, vec3( 0.2126, 0.7152, 0.0722 ) ); }`;
const LM_RE = /vec4 lightMapTexel = texture2D\( lightMap, vLightMapUv \);\s*reflectedLight\.indirectDiffuse \+= lightMapTexel\.rgb \* lightMapIntensity \* RECIPROCAL_PI;/;

export function createWorld(bus, rend, opts = {}) {
  const { renderer, scene, mobile } = rend;
  const kriskaData = { pocetak: [1.5, 0, -1.5], smer: [-0.707, 0, 0.707], izvuci: 4.5, spusti: 9.5, ...(opts.kriska ?? {}) };

  // Jedna instanca po svetu (main.js drži najviše jedan svet), sa jednim dekoderom (glTF WASM).
  const draco = new DRACOLoader().setDecoderPath({ js: DRACO_JS, wasm: DRACO_WASM }).setWorkerLimit(2);
  const loader = new GLTFLoader().setDRACOLoader(draco);

  // Zajedničke uniforme (deli se referencom).
  const U = {
    uDan: { value: 0 },
    uTalas: { value: 0 },
    uTime: { value: 0 },
    uIzlog: { value: 1 }, // sjaj pekare: prozor, lampice, staklo
    uLampe: { value: 0 },
    uTram: { value: 1 },
    uZar: { value: 1 }, // emisija žara u peći
    uProzorBoja: { value: WINDOW_COLOR.clone() },
    // tlocrt pekare (min x, min z, max x, max z): noćno svetlo oko nje (trotoar) dobija topli ton
    uPekBox: { value: new THREE.Vector4(1e4, 1e4, -1e4, -1e4) },
    // unutrašnjost peći (min, max u svetu): kad se vrata otvore, žar osvetli svod (uPecSvetlo)
    uPecMin: { value: new THREE.Vector3(1e4, 1e4, 1e4) },
    uPecMax: { value: new THREE.Vector3(-1e4, -1e4, -1e4) },
    uPecSvetlo: { value: 0 },
  };
  // po setu (grad / enterijer): max za dekodiranje i pojačanje (enterijer se stišava u pogl. 5)
  const SET_U = {};

  const missing = [];
  const roots = {}; // grad, enterijer
  const nodes = {}; // ime → Object3D (prvi pogodak)
  const rest = new Map(); // Object3D → { p, q, s } početna poza
  const materials = new Set();
  const lmTextures = new Set();
  const tramPlanes = [new THREE.Plane(new THREE.Vector3(1, 0, 0), 1e4), new THREE.Plane(new THREE.Vector3(-1, 0, 0), 1e4)];
  const board = new THREE.Box3();
  const stats = { drawStatic: 0, merged: 0 };
  let enterijerLoading = null;
  let dirty = true;
  let destroyed = false;
  const state = {
    izvuci: 0, spusti: 0, pecVrata: 0, tramvaj: 0, figure: 0, korpe: 0, mesenje: 0, naraslo: 0,
    hlebBaza: 1, hleb: [0, 0, 0, 0],
  };

  // ---- materijali
  function patch(mat, kind, setName, { wake = false, pek = false, mat: matte = false } = {}) {
    const su = SET_U[setName];
    mat.onBeforeCompile = (sh) => {
      Object.assign(sh.uniforms, U, su);
      let vs = sh.vertexShader;
      let fs = sh.fragmentShader;
      const pars = [
        'uniform float uDan, uTalas, uTime, uIzlog, uLampe, uTram, uZar, uLmGain;',
        'uniform vec3 uProzorBoja; uniform vec2 uLmMax;',
        kind === 'baked' ? 'uniform sampler2D uLmDan;' : '',
        kind === 'baked' && setName === 'grad' ? 'uniform vec4 uPekBox; varying vec3 vKW;' : '',
        kind === 'baked' && setName === 'enterijer' ? 'uniform vec3 uPecMin, uPecMax; uniform float uPecSvetlo; varying vec3 vKW;' : '',
        wake ? 'varying float vWake; varying float vSeed;' : '',
        kind === 'lamp' ? 'varying float vLSeed;' : '',
        pek ? 'varying float vPekY;' : '',
        AGX_PARS,
        WARM_PARS,
      ].join('\n');
      fs = fs.replace('#include <common>', `#include <common>\n${pars}`);

      if (wake) {
        vs = vs
          .replace('#include <common>', '#include <common>\nattribute float _wake;\nvarying float vWake;\nvarying float vSeed;')
          .replace(
            '#include <begin_vertex>',
            // seme po prozoru: _wake je isti za ceo prozor, pa je i heš isti
            '#include <begin_vertex>\nvWake = _wake;\nvSeed = fract(sin(floor(_wake * 997.0) * 91.345 + 3.7) * 43758.5453);',
          );
      }
      if (kind === 'baked') {
        vs = vs
          .replace('#include <common>', '#include <common>\nvarying vec3 vKW;')
          .replace('#include <project_vertex>', '#include <project_vertex>\nvKW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
      }
      if (pek) {
        // visina u svetu: toplo svetlo samo u prizemlju pekare
        vs = vs
          .replace('#include <common>', '#include <common>\nvarying float vPekY;')
          .replace('#include <project_vertex>', '#include <project_vertex>\nvPekY = (modelMatrix * vec4(transformed, 1.0)).y;');
      }
      if (kind === 'lamp') {
        // seme po lampi iz položaja objekta (lampe nisu spojene)
        vs = vs
          .replace('#include <common>', '#include <common>\nvarying float vLSeed;')
          .replace('#include <begin_vertex>', '#include <begin_vertex>\nvLSeed = fract(sin(dot(modelMatrix[3].xz, vec2(12.9898, 78.233))) * 43758.5453);');
      }

      if (kind === 'baked') {
        const lm = `
          vec3 lmN = uLmMax.x * pow( texture2D( lightMap, vLightMapUv ).rgb, vec3( 4.0 ) );
          vec3 lmD = uLmMax.y * pow( texture2D( uLmDan, vLightMapUv ).rgb, vec3( 4.0 ) );
          ${setName === 'grad' ? `
          // noćno svetlo oko pekare (izlog na trotoaru, fasada iznad) je toplo, kao u Cycles kadru
          vec2 pd2 = max( max( uPekBox.xy - vKW.xz, vKW.xz - uPekBox.zw ), 0.0 );
          float pz = ( 1.0 - smoothstep( 0.3, 5.0, length( pd2 ) ) ) * ( 1.0 - smoothstep( 2.5, 6.5, vKW.y ) ) * min( uIzlog, 1.0 );
          lmN *= mix( vec3( 1.0 ), vec3( 1.3, 0.8, 0.42 ), pz );` : `
          // žar osvetli svod i pod peći dok su vrata otvorena (lightmap je pečen sa zatvorenim)
          vec3 pIn = step( uPecMin, vKW ) * step( vKW, uPecMax );
          float pecW = pIn.x * pIn.y * pIn.z * uPecSvetlo;
          lmN += vec3( 2.4, 0.75, 0.18 ) * pecW * ( 0.55 + 0.45 * sin( uTime * 5.0 + vKW.x * 3.0 ) * sin( uTime * 1.7 ) );`}
          ${matte ? `
          // testo i hleb: mat, bez sjaja (bake nosi odsjaj, pa se svetli vrhovi lightmap-a sabijaju)
          float lmL = krumeLum( lmN );
          lmN *= 1.0 / ( 1.0 + 0.7 * max( lmL - 0.7, 0.0 ) );
          diffuseColor.rgb *= vec3( 1.0, 0.95, 0.87 );` : ''}
          reflectedLight.indirectDiffuse += mix( lmN, lmD, uDan ) * uLmGain;`;
        if (!LM_RE.test(fs)) console.warn('[krume] lightmap chunk se promenio u three, dekodiranje nije ubačeno');
        fs = fs.replace(LM_RE, lm);
      }

      let emis = '';
      if (kind === 'lamp') {
        // pale se jedna po jedna (seme), dok se pale trepere; upaljene samo blago dišu
        emis = `
          float lOn = clamp((uLampe - vLSeed * 0.45) / 0.18, 0.0, 1.0);
          float fl = step(0.35, fract(sin(floor(uTime * 18.0) + vLSeed * 71.0) * 4375.85));
          float warm = lOn * mix(fl, 1.0, smoothstep(0.7, 1.0, lOn));
          outgoingLight *= warm * (0.96 + 0.04 * sin(uTime * 2.3 + vLSeed * 30.0)) * ${LAMP_GAIN.toFixed(3)};`;
      } else if (kind === 'izlog') emis = 'outgoingLight *= uIzlog;';
      else if (kind === 'tram') emis = 'outgoingLight *= uTram;';
      else if (kind === 'zar') emis = 'outgoingLight *= uZar * (0.92 + 0.08 * sin(uTime * 7.0) * sin(uTime * 2.3));';
      // udeo tople rampe umesto AgX-a (0 = čist AgX)
      let warmW = '0.0';
      if (kind === 'izlog' || kind === 'zar') warmW = '1.0';
      else if (pek && kind === 'baked') warmW = `smoothstep(0.18 + 0.6 * uDan, 0.9 + 0.6 * uDan, krumeLum(outgoingLight)) * (1.0 - smoothstep(${(PEK_Y - 0.4).toFixed(2)}, ${PEK_Y.toFixed(2)}, vPekY)) * min(uIzlog, 1.0)`;
      if (wake) {
        warmW = `max(${warmW}, pek * smoothstep(0.12, 0.7, krumeLum(outgoingLight)))`;
        emis += `
          float pek = 1.0 - step(0.02, vWake);
          float on = max(pek * uIzlog, smoothstep(vWake, vWake + 0.035, uTalas));
          // jedan topao prozor treperi (pekara), ostali vrlo blago
          float tr = 1.0 + (0.05 + 0.07 * pek) * sin(uTime * (1.3 + vSeed * 2.1) + vSeed * 40.0) * sin(uTime * (0.37 + vSeed) + vSeed * 9.0);
          float lik = mix(mix(0.7, 1.1, vSeed), 0.6, pek); // pekara: niže, da AgX ne ispere narandžastu
          outgoingLight += uProzorBoja * on * tr * lik * (1.0 - 0.3 * uDan * (1.0 - pek));`;
      }
      if (emis || warmW !== '0.0') {
        const w = warmW !== '0.0' ? `float kWarm = ${warmW};` : '';
        fs = fs.replace('#include <opaque_fragment>', `${emis}\n${w}\n#include <opaque_fragment>`);
      }
      fs = fs.replace(
        '#include <tonemapping_fragment>',
        warmW !== '0.0'
          ? 'gl_FragColor.rgb = mix( AgXToneMapping( gl_FragColor.rgb ), krumeWarm( gl_FragColor.rgb ), kWarm );'
          : 'gl_FragColor.rgb = AgXToneMapping( gl_FragColor.rgb );',
      );
      sh.vertexShader = vs;
      sh.fragmentShader = fs;
    };
    // Ključ keša programa: različiti patch-evi ne smeju da dele program.
    mat.customProgramCacheKey = () => `krume:${setName}:${kind}:${wake ? 'w' : ''}:${pek ? 'p' : ''}:${matte ? 'm' : ''}`;
    materials.add(mat);
    return mat;
  }

  function kindOf(src, mesh) {
    const name = src.name || '';
    const strength = src.emissiveIntensity ?? 1;
    const emissive = !!(src.emissive && src.emissive.getHex() !== 0 && strength > 0);
    if (/^lampa$/i.test(name)) return 'lamp';
    if (/^lampica/i.test(name)) return 'izlog';
    if (/^tram_/i.test(name)) return 'tram';
    if (/zar/i.test(name)) return 'zar';
    if (emissive) return 'emis';
    if (src.transparent && !src.map) return 'glass';
    if (src.map && mesh.geometry.getAttribute('uv1')) return 'baked';
    return 'flat';
  }

  const matCache = new Map(); // izvorni materijal (+ varijanta) → MeshBasicMaterial

  function convert(src, mesh, setName, lightmaps, variant = '') {
    const key = src.uuid + variant;
    if (matCache.has(key)) return matCache.get(key);
    const kind = kindOf(src, mesh);
    let m;
    if (kind === 'baked') {
      const atlas = src.userData?.atlas ?? mesh.userData?.atlas ?? 0;
      const lm = lightmaps.get(atlas) ?? lightmaps.get(0);
      m = new THREE.MeshBasicMaterial({ map: src.map });
      if (lm) {
        m.lightMap = lm.noc; // daje USE_LIGHTMAP i vLightMapUv (uv1); dekodiranje je u shaderu
        m.userData.lmDan = lm.dan;
      }
      const wake = !!src.userData?.prozor && !!mesh.geometry.getAttribute('_wake');
      patch(m, lm ? 'baked' : 'flat', setName, { wake, pek: variant === 'pek', mat: variant === 'mat' });
      if (lm) {
        const prev = m.onBeforeCompile;
        m.onBeforeCompile = (sh, r) => {
          prev(sh, r);
          sh.uniforms.uLmDan = { value: lm.dan };
        };
      }
    } else if (['lamp', 'izlog', 'tram', 'zar', 'emis'].includes(kind)) {
      const strength = src.emissiveIntensity ?? 1;
      m = new THREE.MeshBasicMaterial({
        color: src.emissive.clone().multiplyScalar(strength),
        map: src.emissiveMap ?? null,
      });
      patch(m, kind, setName);
    } else if (kind === 'glass') {
      const izlog = /izlog|staklo$/i.test(src.name) && setName === 'grad';
      m = new THREE.MeshBasicMaterial({ color: src.color.clone(), opacity: src.opacity, transparent: true, depthWrite: false });
      if (izlog) {
        m.color.copy(IZLOG_STAKLO.color);
        m.opacity = Math.max(src.opacity, IZLOG_STAKLO.opacity);
      } else if (setName === 'enterijer') m.color.copy(ENT_STAKLO);
      patch(m, izlog ? 'izlog' : 'flat', setName);
    } else {
      m = new THREE.MeshBasicMaterial({ color: src.color?.clone() ?? new THREE.Color(1, 1, 1), map: src.map ?? null });
      patch(m, 'flat', setName);
    }
    m.name = src.name;
    m.side = src.side;
    if (kind !== 'glass') {
      m.transparent = src.transparent;
      m.opacity = src.opacity;
    }
    m.alphaTest = src.alphaTest;
    m.vertexColors = false;
    if (variant === 'tram') {
      m.clippingPlanes = tramPlanes;
      const k = m.customProgramCacheKey();
      m.customProgramCacheKey = () => `${k}:clip`;
    }
    matCache.set(key, m);
    return m;
  }

  async function loadLightmaps(setName, set, atlases) {
    const map = new Map();
    const useM = mobile || LIGHTMAP_DESKTOP_M;
    await Promise.all(
      [...atlases].map(async (a) => {
        const get = async (kind) => {
          let t = useM ? await fetchLightmap(lightmapUrl(set.lightmap, kind, a, true)) : null;
          if (!t) t = await fetchLightmap(lightmapUrl(set.lightmap, kind, a, false));
          if (!t) missing.push(lightmapUrl(set.lightmap, kind, a, false).replace(BASE, ''));
          return t;
        };
        const [noc, dan0] = await Promise.all([get('noc'), set.dan ? get('dan') : null]);
        if (!noc) return;
        const dan = dan0 ?? noc;
        lmTextures.add(noc).add(dan);
        map.set(a, { noc, dan });
      }),
    );
    return map;
  }

  function register(root) {
    root.traverse((o) => {
      if (o.name && !nodes[o.name]) nodes[o.name] = o;
      rest.set(o, { p: o.position.clone(), q: o.quaternion.clone(), s: o.scale.clone() });
    });
  }

  function isDynamic(o) {
    for (let p = o; p; p = p.parent) if (p.name && DYNAMIC.test(p.name)) return true;
    return false;
  }

  function underTram(o) {
    for (let p = o; p; p = p.parent) if (/^Tramvaj/.test(p.name)) return true;
    return false;
  }

  function underMatte(o) {
    for (let p = o; p; p = p.parent) if (/^(Testo|Hleb_|Korpa_testo_|Brasno$|Platno_vekne)/.test(p.name)) return true;
    return false;
  }

  function underKriska(o) {
    for (let p = o; p; p = p.parent) if (p.name === 'Kriska') return true;
    return false;
  }

  /** Spaja statične mesh-eve istog materijala u jedan (geometrija u koordinatama korena). */
  function mergeStatics(root) {
    root.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(root.matrixWorld).invert();
    const groups = new Map();
    const statics = [];
    root.traverse((o) => {
      if (!o.isMesh || isDynamic(o) || o.geometry.morphAttributes.position) return;
      statics.push(o);
    });
    for (const o of statics) {
      const g = o.geometry;
      const sig = Object.keys(g.attributes).filter((n) => n !== 'normal').sort().join(',') + (g.index ? ':i' : '');
      const key = `${o.material.uuid}|${sig}`;
      if (!groups.has(key)) groups.set(key, { mat: o.material, list: [] });
      groups.get(key).list.push(o);
    }
    let made = 0;
    for (const { mat, list } of groups.values()) {
      if (list.length < 2) continue;
      const geos = list.map((o) => {
        const g = o.geometry.clone();
        g.deleteAttribute('normal');
        g.morphAttributes = {};
        g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv, o.matrixWorld));
        return g;
      });
      const merged = mergeGeometries(geos, false);
      geos.forEach((g) => g.dispose());
      if (!merged) continue;
      const mesh = new THREE.Mesh(merged, mat);
      mesh.name = `spojeno_${mat.name}`;
      mesh.matrixAutoUpdate = false;
      mesh.renderOrder = mat.transparent ? 1 : 0;
      root.add(mesh);
      made++;
      for (const o of list) {
        // deca koja se ne spajaju (npr. Lampa_N_ziv) prelaze na koren sa istom pozicijom
        for (const c of [...o.children]) root.attach(c);
        o.removeFromParent();
        o.geometry.dispose();
        stats.merged++;
      }
    }
    return made;
  }

  // pokretni čvorovi moraju da ažuriraju matrice (statični su zaključani)
  function lock(root) {
    root.updateMatrixWorld(true);
    root.traverse((o) => {
      if (o === root) return;
      o.matrixAutoUpdate = isDynamic(o);
    });
  }

  async function loadSet(name) {
    const set = ASSETS[name];
    let url = null;
    let buf = null;
    if (mobile) {
      buf = await fetchGlb(set.modelM);
      if (buf) url = set.modelM;
    }
    if (!buf) {
      buf = await fetchGlb(set.model);
      if (buf) url = set.model;
    }
    if (!buf) {
      missing.push(set.model.replace(BASE, ''));
      return null;
    }
    const gltf = await loader.parseAsync(buf, url.slice(0, url.lastIndexOf('/') + 1));
    if (destroyed) return null;
    const info = gltf.scene.userData?.krume ?? {};
    const nocMax = info.noc_max ?? 1;
    SET_U[name] = {
      uLmMax: { value: new THREE.Vector2(nocMax, info.dan_max ?? nocMax) },
      uLmGain: { value: 1 },
    };

    const atlases = new Set();
    gltf.scene.traverse((o) => {
      if (!o.isMesh || !o.geometry.getAttribute('uv1')) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      mats.forEach((m) => atlases.add(m.userData?.atlas ?? o.userData?.atlas ?? 0));
    });
    const lightmaps = atlases.size ? await loadLightmaps(name, set, atlases) : new Map();
    if (destroyed) return null;

    const srcMats = new Set();
    gltf.scene.traverse((o) => {
      if (!o.isMesh) return;
      if (/^Dim_/.test(o.name)) {
        o.visible = false; // dim je u particles.js; čvorovi služe samo kao pozicije
        return;
      }
      // pekara (kriška) dobija svoje materijale sa toplim tone mapping-om
      // testo, hlebovi i brašno: mat varijanta (bez sjaja)
      const variant = underTram(o) ? 'tram' : name === 'grad' && underKriska(o) ? 'pek' : name === 'enterijer' && underMatte(o) ? 'mat' : '';
      if (Array.isArray(o.material)) {
        o.material = o.material.map((m) => (srcMats.add(m), convert(m, o, name, lightmaps, variant)));
      } else {
        srcMats.add(o.material);
        o.material = convert(o.material, o, name, lightmaps, variant);
      }
      o.frustumCulled = true;
    });
    srcMats.forEach((m) => m.dispose());

    gltf.scene.name = name;
    register(gltf.scene);
    if (name === 'grad') {
      const tlo = nodes.Tlo;
      if (tlo) board.setFromObject(tlo);
      else board.setFromObject(gltf.scene);
      tramPlanes[0].constant = -board.min.x; // x ≥ min
      tramPlanes[1].constant = board.max.x; // x ≤ max
      if (nodes.Kriska) {
        const kb = new THREE.Box3().setFromObject(nodes.Kriska);
        U.uPekBox.value.set(kb.min.x, kb.min.z, kb.max.x, kb.max.z);
      }
    }
    if (name === 'enterijer' && nodes.Pec && nodes.PecVrata) {
      // unutrašnjost: telo peći iza ravni vrata (vrata gledaju u +z)
      const pb = new THREE.Box3().setFromObject(nodes.Pec);
      const vb = new THREE.Box3().setFromObject(nodes.PecVrata);
      // pod: nivo žara (ispod je drvo, ono ostaje tamno)
      const floorY = nodes.Zar ? new THREE.Box3().setFromObject(nodes.Zar).min.y - 0.08 : pb.min.y + 0.05;
      U.uPecMin.value.set(pb.min.x + 0.15, floorY, pb.min.z + 0.15);
      U.uPecMax.value.set(pb.max.x - 0.15, pb.max.y - 0.1, vb.min.z - 0.08);
    }
    // izlog pekare: staklo i lampice u Kriska_ziv slušaju uIzlog
    mergeStatics(gltf.scene);
    lock(gltf.scene);
    if (mobile) [4, 5, 6].forEach((i) => nodes[`Figura_${i}`] && (nodes[`Figura_${i}`].visible = false));
    scene.add(gltf.scene);
    roots[name] = gltf.scene;
    let draws = 0;
    gltf.scene.traverse((o) => {
      if (o.isMesh) draws += Array.isArray(o.material) ? o.material.length : 1;
    });
    stats[`draws_${name}`] = draws;
    applyAll();
    dirty = true;
    return gltf.scene;
  }

  // Jedno upozorenje po fajlu koji fali.
  function warnMissing() {
    if (!missing.length) return;
    console.warn(`[krume] fali: ${missing.join(', ')}`);
    missing.length = 0;
  }

  /** Grad odmah. Bez grada nema 3D-a (main.js prelazi u statično). */
  async function load() {
    const root = await loadSet('grad');
    warnMissing();
    if (!root && !destroyed) throw new Error('grad.glb nije učitan');
  }

  /** Enterijer odloženo (poglavlje ≥ 2). */
  function loadEnterijer() {
    if (!enterijerLoading) {
      enterijerLoading = loadSet('enterijer')
        .then(async (root) => {
          if (root && !destroyed) {
            root.visible = state.enterijer ?? false;
            const was = root.visible;
            root.visible = true; // kompajliraj i dok je sakriven
            await renderer.compileAsync(scene, rend.getCamera());
            root.visible = was;
            bus.emit('enterijer', root);
          }
          warnMissing();
          return root;
        })
        .catch((err) => {
          console.warn('[krume] enterijer nije učitan:', err.message);
          return null;
        });
    }
    return enterijerLoading;
  }

  const offChapter = bus.on('chapter', (ch) => {
    if (ch && ch.id >= 2) loadEnterijer();
  });

  // ---- pokreti (proceduralno; GLB nema animacije)
  const tmpV = new THREE.Vector3();
  const tmpV2 = new THREE.Vector3();
  const tmpQ = new THREE.Quaternion();
  const axisX = new THREE.Vector3(1, 0, 0);
  const axisY = new THREE.Vector3(0, 1, 0);
  const kSmer = new THREE.Vector3().fromArray(kriskaData.smer).normalize();
  // vrata pekare: ispred zakošenog ugla, na trotoaru (kriška izlazi u tom pravcu)
  const door = new THREE.Vector3().fromArray(kriskaData.pocetak).addScaledVector(kSmer, 1.4);
  door.y = 0;

  function applyKriska() {
    const o = nodes.Kriska;
    if (!o) return;
    const r = rest.get(o);
    o.position.copy(r.p).addScaledVector(kSmer, smooth(0, 1, state.izvuci) * kriskaData.izvuci);
    o.position.y -= smooth(0, 1, state.spusti) * kriskaData.spusti;
    o.visible = state.spusti < 0.999; // ispod daske se ne crta
  }

  function applyTramvaj() {
    const o = nodes.Tramvaj;
    if (!o) return;
    const r = rest.get(o);
    // ulazi sa jedne ivice daske i izlazi na drugoj (clipping ravni na ivicama)
    const half = 9;
    const from = board.isEmpty() ? r.p.x + 40 : board.max.x + half;
    const to = board.isEmpty() ? r.p.x - 40 : board.min.x - half;
    o.position.copy(r.p);
    o.position.x = from + (to - from) * state.tramvaj;
    o.visible = state.tramvaj > 0.001 && state.tramvaj < 0.999;
  }

  function applyPecVrata() {
    const o = nodes.PecVrata;
    if (!o) return;
    const r = rest.get(o);
    const max = o.userData?.otvoreno_rad ?? 85 * DEG;
    tmpQ.setFromAxisAngle(axisX, smooth(0, 1, state.pecVrata) * max);
    o.quaternion.copy(r.q).multiply(tmpQ);
  }

  function applyTesto() {
    nodes.Testo?.traverse((m) => {
      if (!m.isMesh || !m.morphTargetDictionary) return;
      const d = m.morphTargetDictionary;
      if (d.mesenje != null) m.morphTargetInfluences[d.mesenje] = state.mesenje;
      if (d.naraslo != null) m.morphTargetInfluences[d.naraslo] = state.naraslo;
    });
  }

  function applyKorpe() {
    for (const [name, o] of Object.entries(nodes)) {
      if (!name.startsWith('Korpa_testo_')) continue;
      const r = rest.get(o);
      const k = 1 + ((o.userData?.skala_naraslo ?? 1.35) - 1) * smooth(0, 1, state.korpe);
      o.scale.copy(r.s).multiplyScalar(k);
    }
  }

  function applyHlebovi() {
    for (let n = 1; n <= 4; n++) {
      const o = nodes[`Hleb_${n}`];
      if (!o) continue;
      const r = rest.get(o);
      const t = smooth(0, 1, state.hleb[n - 1]);
      // prava veličina je mala za kadar: u pogl. 5 svi rastu (hlebBaza), aktivni još malo i izlazi napred
      o.scale.copy(r.s).multiplyScalar(state.hlebBaza * (1 + (mobile ? 0.45 : 0.28) * t));
      o.position.copy(r.p);
      if (!mobile) o.position.z += 0.16 * t; // ka kameri (kamera gleda u -z)
      o.position.y += 0.02 * t;
    }
  }

  // figure sa kesama idu ka vratima pekare; ostale samo prošetaju
  function applyFigure() {
    for (let i = 1; i <= 6; i++) {
      const o = nodes[`Figura_${i}`];
      if (!o) continue;
      if (mobile && i > 3) {
        o.visible = false;
        continue;
      }
      const r = rest.get(o);
      o.visible = state.figure > 0.001;
      const t = smooth((i - 1) * 0.06, 0.7 + (i - 1) * 0.05, state.figure);
      tmpV.copy(door).sub(r.p);
      tmpV.y = 0;
      const dist = tmpV.length();
      const walk = Math.max(0, Math.min(7, dist - 1.3 - i * 0.45));
      tmpV.normalize();
      const s = walk * t;
      o.position.copy(r.p).addScaledVector(tmpV, s);
      o.position.y = r.p.y + Math.abs(Math.sin(s * 3.2)) * 0.035 * (t > 0 && t < 1 ? 1 : 0);
      if (walk > 0.05) {
        // lice ka pravcu hoda (model gleda u +z)
        tmpQ.setFromAxisAngle(axisY, Math.atan2(tmpV.x, tmpV.z));
        o.quaternion.copy(tmpQ);
      } else o.quaternion.copy(r.q);
    }
  }

  function applyAll() {
    applyKriska();
    applyTramvaj();
    applyPecVrata();
    applyTesto();
    applyKorpe();
    applyHlebovi();
    applyFigure();
  }

  const mark = (fn) => (...a) => {
    fn(...a);
    dirty = true;
  };

  /** Upravljanje svetom. Pozivi su jeftini; timeline.js ih zove samo kad se udeo promeni. */
  const api = {
    uniforms: U,
    nodes,
    stats,
    /** Lightmap noć → dan (0–1). */
    dan: mark((v) => { U.uDan.value = clamp01(v); }),
    /** Prag talasa prozora (0 = samo pekara, 1 = svi). */
    talas: mark((v) => { U.uTalas.value = clamp01(v); }),
    /** Sjaj pekare (prozor, lampice, staklo); može > 1 za kratak blesak. */
    izlog: mark((v) => { U.uIzlog.value = Math.max(0, v); }),
    lampe: mark((v) => { U.uLampe.value = clamp01(v); }),
    /** Emisija žara u peći (1 = kao u Blenderu). */
    zarEmisija: mark((v) => { U.uZar.value = Math.max(0, v); }),
    /** Svetlo žara na svodu peći (0 = vrata zatvorena). */
    pecSvetlo: mark((v) => { U.uPecSvetlo.value = Math.max(0, v); }),
    /** Pojačanje zapečenog svetla enterijera (1 = kao u Blenderu). */
    enterijerSvetlo: mark((v) => { if (SET_U.enterijer) SET_U.enterijer.uLmGain.value = v; }),
    enterijer: mark((on) => {
      state.enterijer = !!on;
      if (roots.enterijer) roots.enterijer.visible = !!on;
    }),
    kriska: mark((izvuci, spusti) => {
      state.izvuci = clamp01(izvuci);
      state.spusti = clamp01(spusti);
      applyKriska();
    }),
    pecVrata: mark((t) => { state.pecVrata = clamp01(t); applyPecVrata(); }),
    testo: mark((mesenje, naraslo = state.naraslo) => {
      state.mesenje = clamp01(mesenje);
      state.naraslo = clamp01(naraslo);
      applyTesto();
    }),
    tramvaj: mark((t) => { state.tramvaj = clamp01(t); applyTramvaj(); }),
    figure: mark((t) => { state.figure = clamp01(t); applyFigure(); }),
    korpe: mark((t) => { state.korpe = clamp01(t); applyKorpe(); }),
    /** baza: uveličanje svih hlebova (1 = prava veličina); akt: [4] koliko je koji hleb izašao. */
    hlebovi: mark((baza, akt) => {
      state.hlebBaza = Math.max(0.01, baza);
      for (let i = 0; i < 4; i++) state.hleb[i] = clamp01(akt?.[i] ?? 0);
      applyHlebovi();
    }),
    /** Tačka za etiketu hleba n (vrh hleba u svetu). */
    hlebTacka(n, out) {
      const o = nodes[`Hleb_${n}`];
      if (!o) return null;
      o.updateWorldMatrix(true, true);
      const box = new THREE.Box3().setFromObject(o);
      if (box.isEmpty()) return o.getWorldPosition(out);
      box.getCenter(out);
      out.y = box.max.y;
      return out;
    },
  };

  /** Otvor peći (sredina žara) u svetu, za sjaj u post-obradi; null ako enterijer nije učitan. */
  function zarTacka() {
    // sredina otvora peći (vrata u zatvorenom položaju), malo ka žaru
    const v = nodes.PecVrata;
    const z = nodes.Zar ?? nodes.Pec;
    if (!v && !z) return null;
    const box = new THREE.Box3();
    if (v) {
      const r = rest.get(v);
      const q = v.quaternion.clone();
      if (r) v.quaternion.copy(r.q);
      v.updateWorldMatrix(true, true);
      box.setFromObject(v);
      v.quaternion.copy(q);
      v.updateWorldMatrix(true, true);
    } else box.setFromObject(z);
    const c = box.getCenter(new THREE.Vector3());
    if (v && z) c.lerp(new THREE.Box3().setFromObject(z).getCenter(tmpV), 0.2);
    return c;
  }

  /** Dimnjak pekare: prvi čvor dima (Dim_11_0), ili rezerva. */
  function chimney(out = new THREE.Vector3()) {
    const d = nodes.Dim_11_0;
    if (d) {
      d.updateWorldMatrix(true, false);
      return d.getWorldPosition(out).add(tmpV2.set(0, -0.4, 0));
    }
    if (opts.dim) return out.fromArray(opts.dim);
    return out.set(9, 23.5, -8.7);
  }

  /** Pravac vetra za dim (iz poslednjeg čvora dima), jedinični vodoravni. */
  function wind(out = new THREE.Vector3()) {
    const a = nodes.Dim_11_0;
    const b = nodes.Dim_11_8;
    if (!a || !b) return out.set(0.9, 0, -0.35).normalize();
    out.subVectors(b.position, a.position);
    out.y = 0;
    return out.normalize();
  }

  /** Prostori za brašno: 'sto' (enterijer, oko testa) i 'otvor' (presek ispred pekare). */
  function flourBox(which = 'sto') {
    const box = new THREE.Box3();
    if (which === 'sto' && nodes.Testo) {
      nodes.Testo.getWorldPosition(tmpV);
      return box.setFromCenterAndSize(tmpV.clone().add(new THREE.Vector3(-0.6, 0.6, -0.8)), new THREE.Vector3(3.2, 1.6, 3));
    }
    // otvor: u zakošenom uglu, gde kriška izlazi
    const c = new THREE.Vector3().fromArray(kriskaData.pocetak).addScaledVector(kSmer, 1.2);
    c.y = 2.2;
    return box.setFromCenterAndSize(c, new THREE.Vector3(4, 3.6, 4));
  }

  return {
    api,
    load,
    loadEnterijer,
    chimney,
    wind,
    zarTacka,
    flourBox,
    /** Vraća true ako se nešto promenilo od prošlog kadra (setter-i). */
    update(time) {
      U.uTime.value = time;
      const d = dirty;
      dirty = false;
      return d;
    },
    destroy() {
      destroyed = true;
      offChapter();
      const texs = new Set();
      Object.values(roots).forEach((r) => {
        scene.remove(r);
        r.traverse((o) => {
          if (!o.isMesh) return;
          o.geometry.dispose();
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          mats.forEach((m) => m.map && texs.add(m.map));
        });
      });
      materials.forEach((m) => m.dispose());
      texs.forEach((t) => t.dispose());
      lmTextures.forEach((t) => t.dispose());
      draco.dispose();
    },
  };
}
