import { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Environment, Lightformer, MeshTransmissionMaterial, PerformanceMonitor } from '@react-three/drei';
import { world, onSceneVisible, smoothstep, lerp } from './state.js';
import { wordmarkTexture, glowTexture, drawSite } from './textures.js';
import { reducedMotion } from '../hooks/useSmoothScroll.js';

const BG = new THREE.Color('#0a0a0b');
const IMG = `${import.meta.env.BASE_URL}img/`;

/* Kvalitet: transmisija ponovo crta scenu u bafer, pa su samples i rezolucija ono što košta */
function pickTier() {
  const small = Math.min(window.innerWidth, window.innerHeight) < 700 || matchMedia('(pointer: coarse)').matches;
  return small
    ? { name: 'low', samples: 3, maxDpr: 1.5, streaks: 420, tex: 1024, transScale: 0.5, aa: false }
    : { name: 'high', samples: 6, maxDpr: 1.75, streaks: 900, tex: 1600, transScale: 1, aa: true };
}

/* ---------------- K znak: tri staklena dela oko jezgra ---------------- */
// Oblici prate logo (mreža 48, centar 24/24, y nagore), 0.1 jedinice po polju
const P = (x, y) => new THREE.Vector2((x - 24) * 0.1, (24 - y) * 0.1);
const PIECES = [
  { pts: [P(11, 9), P(17, 9), P(17, 39), P(11, 39)], dive: [[-3.4, -0.6, 3.1], [0.3, 1.2, 0.5]], intro: [[-2.6, 0.2, -5], [0, -1.6, 0.2]] },
  { pts: [P(22.6, 21.2), P(34.2, 9), P(41.8, 9), P(27.2, 24.4)], dive: [[3.2, 2.9, 2.7], [0.8, -0.6, 1.0]], intro: [[2.8, 3.6, -6], [1.2, 0.2, 0.8]] },
  { pts: [P(22.6, 26.8), P(27.2, 24.4), P(41.8, 39), P(34.2, 39)], dive: [[3.4, -2.7, 2.9], [-0.7, 0.5, -0.9]], intro: [[2.8, -3.6, -6], [-1.2, -0.2, -0.8]] },
];
const MARK_SHIFT = -0.24; // ceo znak centriran oko jezgra

function usePieceGeometries() {
  return useMemo(() => PIECES.map((p) => {
    const g = new THREE.ExtrudeGeometry(new THREE.Shape(p.pts), {
      depth: 0.5, bevelEnabled: true, bevelThickness: 0.09, bevelSize: 0.065, bevelSegments: 6, curveSegments: 1,
    });
    g.computeBoundingBox();
    const c = new THREE.Vector3();
    g.boundingBox.getCenter(c);
    g.translate(-c.x, -c.y, -c.z);
    g.computeVertexNormals();
    return { geometry: g, center: c };
  }), []);
}

function Glass({ tier }) {
  return (
    <MeshTransmissionMaterial
      transmission={1}
      thickness={0.75}
      roughness={0.04}
      ior={1.5}
      chromaticAberration={0.22}
      anisotropy={0.2}
      distortion={0.12}
      distortionScale={0.4}
      temporalDistortion={0.05}
      clearcoat={1}
      clearcoatRoughness={0.1}
      color="#fff8f2"
      attenuationColor="#ffd7c2"
      attenuationDistance={2.4}
      samples={tier.samples}
      transmissionSampler
      resolution={32}
      backsideResolution={32}
    />
  );
}

function KMark({ tier }) {
  const pieces = usePieceGeometries();
  const group = useRef();
  const refs = useRef([]);
  useFrame((state, dt) => {
    const d = world.d;
    if (!d || !group.current) return;
    const g = group.current;
    const t = state.clock.elapsedTime;
    // cela grupa: položaj, veličina, lagano lebdenje i nagib za mišem
    g.position.x = THREE.MathUtils.damp(g.position.x, d.groupX, 4, dt);
    g.position.y = THREE.MathUtils.damp(g.position.y, d.groupY + Math.sin(t * 0.6) * 0.05, 4, dt);
    g.scale.setScalar(THREE.MathUtils.damp(g.scale.x, d.groupScale, 4, dt));
    const rx = -world.mouse.y * 0.22 + Math.sin(t * 0.35) * 0.05;
    const ry = world.mouse.x * 0.42 + Math.sin(t * 0.27) * 0.12 - 0.18;
    g.rotation.x = THREE.MathUtils.damp(g.rotation.x, rx, 3, dt);
    g.rotation.y = THREE.MathUtils.damp(g.rotation.y, ry, 3, dt);
    pieces.forEach((p, i) => {
      const m = refs.current[i];
      if (!m) return;
      const def = PIECES[i];
      const a = d.scatter; // 1 = rasuto (pre intro animacije)
      const e = d.explode; // 1 = rasklopljeno (skrol)
      for (let k = 0; k < 3; k++) {
        const axis = 'xyz'[k];
        m.position[axis] = p.center[axis] + (k === 0 ? MARK_SHIFT : 0) + def.intro[0][k] * a + def.dive[0][k] * e;
        m.rotation[axis] = def.intro[1][k] * a + def.dive[1][k] * e;
      }
    });
  });
  return (
    <group ref={group}>
      {pieces.map((p, i) => (
        <mesh key={i} ref={(el) => { refs.current[i] = el; }} geometry={p.geometry}>
          <Glass tier={tier} />
        </mesh>
      ))}
      <Core />
      <Halo />
    </group>
  );
}

/* ---------------- Jezgro: užarena kugla + sjaj + svetlo ---------------- */
const coreVert = /* glsl */`
  varying vec3 vN; varying vec3 vV; varying vec3 vP;
  void main() {
    vN = normalize(normalMatrix * normal);
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    vV = normalize(-mv.xyz); vP = position;
    gl_Position = projectionMatrix * mv;
  }`;
const coreFrag = /* glsl */`
  uniform float uTime;
  varying vec3 vN; varying vec3 vV; varying vec3 vP;
  float hash(vec3 p) { return fract(sin(dot(p, vec3(12.9898, 78.233, 37.719))) * 43758.5453); }
  float noise(vec3 p) {
    vec3 i = floor(p); vec3 f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(hash(i), hash(i + vec3(1,0,0)), f.x), mix(hash(i + vec3(0,1,0)), hash(i + vec3(1,1,0)), f.x), f.y),
               mix(mix(hash(i + vec3(0,0,1)), hash(i + vec3(1,0,1)), f.x), mix(hash(i + vec3(0,1,1)), hash(i + vec3(1,1,1)), f.x), f.y), f.z);
  }
  void main() {
    float f = pow(1.0 - max(dot(vN, vV), 0.0), 1.6);
    float n = noise(vP * 5.0 + vec3(0.0, uTime * 0.6, uTime * 0.3)) * 0.5 + noise(vP * 11.0 - uTime * 0.4) * 0.25;
    vec3 hot = vec3(1.0, 0.86, 0.62);
    vec3 ember = vec3(1.0, 0.36, 0.14);
    vec3 col = mix(hot, ember, clamp(f * 1.15 + n * 0.35, 0.0, 1.0));
    gl_FragColor = vec4(col * (1.25 + n * 0.3), 1.0);
  }`;

const corePos = new THREE.Vector3();
function Core() {
  const mesh = useRef();
  const near = useRef(0);
  const sprite = useRef();
  const light = useRef();
  const coreMat = useRef();
  const glow = useMemo(() => glowTexture(), []);
  const uniforms = useMemo(() => ({ uTime: { value: 0 } }), []);
  useFrame((state) => {
    const d = world.d;
    if (!d) return;
    const t = state.clock.elapsedTime;
    if (coreMat.current) coreMat.current.uniforms.uTime.value = t;
    mesh.current.getWorldPosition(corePos).project(state.camera);
    const dist = Math.hypot(corePos.x - world.mouse.x, corePos.y + world.mouse.y);
    near.current = THREE.MathUtils.damp(near.current, 1 - smoothstep(0.05, 0.6, dist), 4, state.delta || 0.016);
    const pulse = 1 + Math.sin(t * 1.7) * 0.03 + near.current * 0.08;
    const v = d.core;
    mesh.current.scale.setScalar(Math.max(0.0001, 0.36 * pulse * v));
    sprite.current.scale.setScalar(3.4 * pulse * (0.4 + 0.6 * v) * (1 + near.current * 0.35));
    sprite.current.material.opacity = Math.min(1, (0.85 + near.current * 0.3) * v);
    light.current.intensity = (9 + near.current * 7) * v;
    mesh.current.visible = sprite.current.visible = v > 0.005;
  });
  return (
    <group position={[0, 0, 0.25]}>
      <mesh ref={mesh}>
        <sphereGeometry args={[1, 48, 48]} />
        <shaderMaterial ref={coreMat} vertexShader={coreVert} fragmentShader={coreFrag} uniforms={uniforms} toneMapped={false} />
      </mesh>
      <sprite ref={sprite}>
        <spriteMaterial map={glow} transparent depthWrite={false} blending={THREE.AdditiveBlending} toneMapped={false} />
      </sprite>
      <pointLight ref={light} color="#ff6a2c" distance={7} decay={1.6} />
    </group>
  );
}

/* ---------------- Topli oreol iza znaka ----------------
   Neproziran (ulazi u prolaz transmisije), pa staklo ima šta da prelama; ivice su boje pozadine */
const haloFrag = /* glsl */`
  uniform vec3 uBg; uniform float uI;
  varying vec2 vUv;
  void main() {
    float d = length(vUv - 0.5) * 2.0;
    float g = pow(1.0 - smoothstep(0.0, 1.0, d), 2.2);
    vec3 col = mix(uBg, vec3(1.0, 0.33, 0.12) * 0.7, g * uI);
    gl_FragColor = vec4(col, 1.0);
    #include <colorspace_fragment>
  }`;
const haloVert = /* glsl */`varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;

function Halo() {
  const mat = useRef();
  const uniforms = useMemo(() => ({ uBg: { value: BG.clone() }, uI: { value: 0 } }), []);
  // r3f kopira uniforme u materijal, pa se menja ono što je na materijalu
  const mesh = useRef();
  useFrame(() => {
    const d = world.d;
    if (!d || !mat.current) return;
    mat.current.uniforms.uI.value = d.core * (0.75 + 0.25 * d.backdrop);
    // neproziran je, pa bi bez ovoga zaklanjao tunel i galeriju
    mesh.current.visible = d.core > 0.01;
  });
  return (
    <mesh ref={mesh} position={[0, 0, -4.4]}>
      <planeGeometry args={[9.5, 9.5]} />
      <shaderMaterial ref={mat} vertexShader={haloVert} fragmentShader={haloFrag} uniforms={uniforms} toneMapped={false} />
    </mesh>
  );
}

/* ---------------- Natpis KERN iza znaka (staklo ga lomi) ---------------- */
function Backdrop() {
  const mesh = useRef();
  const [tex, setTex] = useState(() => wordmarkTexture());
  useEffect(() => {
    let off = false;
    document.fonts?.ready.then(() => { if (!off) setTex(wordmarkTexture()); });
    return () => { off = true; };
  }, []);
  useEffect(() => () => tex.dispose(), [tex]);
  const z = -3.2;
  const w = 6.6;
  useFrame(() => {
    const d = world.d;
    if (!d || !mesh.current) return;
    mesh.current.material.color.setScalar(d.backdrop * 0.03);
    mesh.current.visible = d.backdrop > 0.01;
    mesh.current.position.x = d.groupX * 1.25;
    mesh.current.position.y = d.groupY * 1.2;
    mesh.current.scale.setScalar((d.groupScale / 0.85) * (world.mobile ? 0.6 : 1));
  });
  return (
    <mesh ref={mesh} position={[0, 0, z]}>
      <planeGeometry args={[w, w * (640 / 2048)]} />
      <meshBasicMaterial map={tex} alphaTest={0.5} toneMapped={false} />
    </mesh>
  );
}

/* ---------------- Tunel svetla posle ulaska u jezgro ---------------- */
function Warp({ count }) {
  const mesh = useRef();
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const data = useMemo(() => {
    const a = [];
    for (let i = 0; i < count; i++) {
      const r = 0.9 + Math.pow(Math.random(), 0.7) * 6.5;
      const th = Math.random() * Math.PI * 2;
      a.push({ x: Math.cos(th) * r, y: Math.sin(th) * r, z: -Math.random() * 70, s: 0.6 + Math.random() * 1.2 });
    }
    return a;
  }, [count]);
  useEffect(() => {
    const c = new THREE.Color();
    data.forEach((_, i) => {
      const warm = Math.random();
      c.setRGB(1, warm < 0.25 ? 0.42 : 0.92, warm < 0.25 ? 0.2 : 0.86);
      mesh.current.setColorAt(i, c);
    });
    mesh.current.instanceColor.needsUpdate = true;
  }, [data]);
  useFrame((state, dt) => {
    const d = world.d;
    if (!d) return;
    const m = mesh.current;
    m.visible = d.warp > 0.005;
    if (!m.visible) return;
    m.material.opacity = d.warp;
    const camZ = state.camera.position.z;
    const speed = (reducedMotion() ? 4 : 22) * (0.4 + d.warp) + Math.min(60, Math.abs(world.velocity) * 0.9);
    const stretch = 0.6 + speed * 0.05;
    data.forEach((p, i) => {
      p.z += dt * speed * p.s;
      if (p.z > camZ + 1) p.z -= 72;
      dummy.position.set(p.x, p.y, p.z);
      dummy.scale.set(0.018, 0.018, stretch * p.s);
      dummy.updateMatrix();
      m.setMatrixAt(i, dummy.matrix);
    });
    m.instanceMatrix.needsUpdate = true;
  });
  return (
    <instancedMesh ref={mesh} args={[null, null, count]} frustumCulled={false}>
      <boxGeometry args={[1, 1, 1]} />
      <meshBasicMaterial transparent depthWrite={false} blending={THREE.AdditiveBlending} toneMapped={false} />
    </instancedMesh>
  );
}

/* ---------------- Galerija: konceptni sajtovi na unutrašnjosti valjka ---------------- */
const planeVert = /* glsl */`
  uniform float uVel; uniform float uTime;
  varying vec2 vUv;
  void main() {
    vUv = uv;
    vec3 p = position;
    p.y += sin(uv.x * 3.14159) * uVel * 0.004;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
  }`;
const planeFrag = /* glsl */`
  uniform sampler2D uTex; uniform float uAlpha; uniform float uVel; uniform float uHi; uniform vec2 uSize;
  varying vec2 vUv;
  void main() {
    vec2 uv = vec2(1.0 - vUv.x, vUv.y); // gledamo iznutra
    vec2 zuv = (uv - 0.5) * (1.0 - uHi * 0.04) + 0.5;
    float s = clamp(uVel * 0.0009, -0.02, 0.02);
    vec3 col = vec3(texture2D(uTex, zuv + vec2(s, 0.0)).r, texture2D(uTex, zuv).g, texture2D(uTex, zuv - vec2(s, 0.0)).b);
    vec2 p = (uv - 0.5) * uSize;
    float r = 0.07;
    vec2 q = abs(p) - uSize * 0.5 + r;
    float d = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
    float mask = 1.0 - smoothstep(0.0, 0.012, d);
    col *= mix(0.42, 1.0, uHi);
    gl_FragColor = vec4(col, uAlpha * mask);
    #include <colorspace_fragment>
  }`;

const galleryLive = () => (world.d?.gallery || 0) > 0.6 && !world.outroMode;

function useSiteTextures(projects, texW) {
  const [textures, setTextures] = useState(null);
  useEffect(() => {
    let off = false;
    const H = Math.round(texW / 1.5);
    const made = projects.map(() => {
      const c = document.createElement('canvas');
      c.width = texW; c.height = H;
      const t = new THREE.CanvasTexture(c);
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = 8;
      return t;
    });
    const imgs = projects.map((p) => {
      const im = new Image();
      im.decoding = 'async';
      im.src = `${IMG}${p.key}-${texW > 1100 ? 1600 : 800}.webp`;
      return im;
    });
    const paint = () => {
      if (off) return;
      projects.forEach((p, i) => {
        drawSite(made[i].image, imgs[i].complete && imgs[i].naturalWidth ? imgs[i] : null, p.theme);
        made[i].needsUpdate = true;
      });
    };
    paint();
    setTextures(made);
    Promise.all(imgs.map((im) => im.decode().catch(() => {}))).then(() => document.fonts?.ready).then(paint);
    return () => { off = true; made.forEach((t) => t.dispose()); };
  }, [projects, texW]);
  return textures;
}

function Gallery({ projects, tier, onPick }) {
  const group = useRef();
  const mats = useRef([]);
  const { size, camera, gl } = useThree();
  const textures = useSiteTextures(projects, tier.tex);
  const n = projects.length;
  // širina ploče se računa iz vidnog ugla da stane i na uspravan telefon
  const aspect = size.width / size.height;
  const hfov = 2 * Math.atan(Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * aspect);
  const R = aspect < 1 ? 4.2 : 6;
  const theta = Math.min(0.56, hfov * (aspect < 1 ? 0.8 : 0.42));
  const spacing = theta * 1.32;
  const h = (R * theta) / 1.5;
  const geos = useMemo(() => projects.map((_, i) => {
    const c = Math.PI - i * spacing; // centar ploče i; π je ispred kamere
    return new THREE.CylinderGeometry(R, R, h, 48, 1, true, c - theta / 2, theta);
  }), [projects, R, h, theta, spacing]);
  useEffect(() => () => geos.forEach((g) => g.dispose()), [geos]);
  // uniformi se prave jednom, inače bi svaki render vratio providnost na 0
  const uniforms = useMemo(() => (textures ? projects.map((_, i) => ({
    uTex: { value: textures[i] }, uAlpha: { value: 0 }, uVel: { value: 0 }, uHi: { value: 0 },
    uTime: { value: 0 }, uSize: { value: new THREE.Vector2(R * theta, h) },
  })) : null), [textures, projects, R, theta, h]);
  world.count = n;

  useFrame((state, dt) => {
    const d = world.d;
    if (!d || !group.current) return;
    const g = group.current;
    g.visible = d.gallery > 0.002;
    if (!g.visible) return;
    g.position.copy(state.camera.position);
    const x = world.work * (n - 1);
    const f = x - Math.floor(x);
    const stepped = Math.floor(x) + smoothstep(0.3, 0.7, f);
    const target = stepped * spacing + (1 - d.gallery) * 0.9;
    g.rotation.y = THREE.MathUtils.damp(g.rotation.y, target, 6, dt);
    const active = Math.round(world.work * (n - 1));
    mats.current.forEach((m, i) => {
      if (!m) return;
      const u = m.uniforms;
      u.uAlpha.value = d.gallery;
      u.uVel.value = THREE.MathUtils.damp(u.uVel.value, world.velocity, 5, dt);
      const hi = i === active || i === world.hover ? 1 : 0;
      u.uHi.value = THREE.MathUtils.damp(u.uHi.value, hi, 5, dt);
    });
  });

  if (!uniforms) return null;
  return (
    <group ref={group}>
      {projects.map((p, i) => (
        <mesh
          key={p.key}
          geometry={geos[i]}
          onPointerOver={(e) => {
            if (!galleryLive()) return;
            e.stopPropagation(); world.hover = i; document.documentElement.dataset.cursor3d = 'View';
          }}
          onPointerOut={() => { world.hover = -1; delete document.documentElement.dataset.cursor3d; }}
          onClick={(e) => {
            if (!galleryLive() || e.nativeEvent.target.closest?.('a, button, input, label')) return;
            e.stopPropagation(); onPick?.(i);
          }}
        >
          <shaderMaterial
            ref={(el) => { mats.current[i] = el; }}
            vertexShader={planeVert}
            fragmentShader={planeFrag}
            transparent
            depthWrite={false}
            side={THREE.BackSide}
            uniforms={uniforms[i]}
          />
        </mesh>
      ))}
    </group>
  );
}

/* ---------------- Režiser: od skrola pravi sve izvedene vrednosti scene ---------------- */
function Director({ flashRef }) {
  const { camera, size } = useThree();
  useFrame((_, dt) => {
    const aspect = size.width / size.height;
    const portrait = aspect < 0.9;
    world.mobile = portrait;
    const baseFovR = THREE.MathUtils.degToRad((portrait ? 48 : 38) / 2);
    const halfW = Math.tan(baseFovR) * 8 * aspect;
    const baseX = portrait ? 0 : halfW * 0.55;
    const baseY = portrait ? 1.05 : 0.1;
    const baseScale = portrait ? Math.min(0.78, halfW * 0.4) : Math.min(0.85, halfW * 0.2);
    const baseZ = 8;
    const baseFov = portrait ? 48 : 38;
    const intro = world.intro;
    const d = world.d || (world.d = {});
    if (!world.outroMode) {
      const dv = world.dive;
      d.scatter = 1 - intro;
      d.explode = smoothstep(0.02, 0.44, dv);
      d.groupX = lerp(baseX, 0, smoothstep(0, 0.3, dv));
      d.groupY = lerp(baseY, 0, smoothstep(0, 0.3, dv));
      d.groupScale = baseScale * (0.86 + 0.14 * intro);
      d.camZ = lerp(lerp(2.6, baseZ, intro), 0.95, smoothstep(0.08, 0.6, dv));
      d.core = (1 - smoothstep(0.5, 0.58, dv)) * smoothstep(0, 0.5, intro);
      d.backdrop = (1 - smoothstep(0.04, 0.3, dv)) * smoothstep(0.2, 1, intro);
      d.flash = smoothstep(0.42, 0.52, dv) * (1 - smoothstep(0.53, 0.63, dv));
      d.fov = baseFov + 26 * smoothstep(0.25, 0.6, dv) * (1 - smoothstep(0.2, 1, world.workIn));
      d.warp = smoothstep(0.52, 0.72, dv) * (1 - smoothstep(0.35, 0.9, world.workIn));
      d.gallery = smoothstep(0.2, 1, world.workIn);
    } else {
      const o = world.outro;
      d.scatter = 0;
      d.explode = 1 - smoothstep(0.05, 0.9, o);
      d.groupX = baseX;
      d.groupY = portrait ? 1.1 : 0;
      d.groupScale = baseScale;
      d.camZ = baseZ;
      d.core = smoothstep(0.3, 0.9, o);
      d.backdrop = 0;
      d.flash = 0;
      d.warp = 0;
      d.gallery = 0;
      d.fov = baseFov;
    }
    // kamera: z prati skrol, x/y blago prate miša (samo dok je znak u kadru)
    const par = d.camZ > 4 ? 1 : 0;
    camera.position.z = THREE.MathUtils.damp(camera.position.z, d.camZ, 5, dt);
    camera.position.x = THREE.MathUtils.damp(camera.position.x, world.mouse.x * 0.25 * par, 2.5, dt);
    camera.position.y = THREE.MathUtils.damp(camera.position.y, -world.mouse.y * 0.15 * par, 2.5, dt);
    camera.lookAt(camera.position.x * 0.5, camera.position.y * 0.5, camera.position.z - 10);
    const fov = THREE.MathUtils.damp(camera.fov, d.fov, 5, dt);
    if (Math.abs(fov - camera.fov) > 0.01) { camera.fov = fov; camera.updateProjectionMatrix(); }
    if (flashRef.current) {
      const f = d.flash.toFixed(3);
      if (flashRef.current.dataset.v !== f) { flashRef.current.dataset.v = f; flashRef.current.style.opacity = f; }
    }
  }, -1);
  return null;
}

function Lights() {
  return (
    <>
      <ambientLight intensity={0.25} />
      <directionalLight position={[3, 4, 6]} intensity={1.2} />
      {/* studijsko osvetljenje bez preuzimanja HDR fajla */}
      <Environment resolution={256} frames={1}>
        <Lightformer intensity={4} position={[0, 5, 4]} scale={[12, 4, 1]} color="#fff4e6" />
        <Lightformer intensity={2.6} position={[-6, 1, 3]} scale={[4, 9, 1]} color="#c9dcff" />
        <Lightformer intensity={2.4} position={[6, -2, 2]} scale={[5, 6, 1]} color="#ffb98c" />
        <Lightformer intensity={1.4} position={[0, -4, -3]} scale={[9, 3, 1]} color="#ffffff" />
      </Environment>
    </>
  );
}

export default function Scene({ projects, onPick, running }) {
  const [tier] = useState(pickTier);
  const [dpr, setDpr] = useState(Math.min(window.devicePixelRatio || 1, tier.maxDpr));
  const [active, setActive] = useState(true);
  const flashRef = useRef(null);
  const wrap = useRef(null);
  useEffect(() => onSceneVisible((v) => {
    setActive(v);
    if (wrap.current) wrap.current.style.visibility = v ? 'visible' : 'hidden';
  }), []);
  useEffect(() => {
    const move = (e) => {
      world.mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      world.mouse.y = (e.clientY / window.innerHeight) * 2 - 1;
    };
    window.addEventListener('pointermove', move, { passive: true });
    return () => window.removeEventListener('pointermove', move);
  }, []);
  const portrait = typeof window !== 'undefined' && window.innerWidth / window.innerHeight < 0.9;
  return (
    <>
      <div className="world" ref={wrap} aria-hidden="true">
        <Canvas
          dpr={dpr}
          frameloop={!active ? 'never' : running ? 'always' : 'demand'}
          eventSource={document.getElementById('root')}
          eventPrefix="client"
          camera={{ position: [0, 0, 8], fov: portrait ? 48 : 38, near: 0.05, far: 120 }}
          gl={{ antialias: tier.aa, powerPreference: 'high-performance', alpha: false }}
          onCreated={({ gl, scene }) => {
            scene.background = BG;
            gl.transmissionResolutionScale = tier.transScale;
            gl.toneMapping = THREE.ACESFilmicToneMapping;
            gl.toneMappingExposure = 1.05;
          }}
        >
          <PerformanceMonitor onDecline={() => setDpr((v) => Math.max(1, v - 0.25))} />
          <Director flashRef={flashRef} />
          <Suspense fallback={null}>
            <Lights />
            <Backdrop />
            <KMark tier={tier} />
            <Warp count={tier.streaks} />
            <Gallery projects={projects} tier={tier} onPick={onPick} />
          </Suspense>
        </Canvas>
      </div>
      <div className="flash" ref={flashRef} aria-hidden="true" />
    </>
  );
}
