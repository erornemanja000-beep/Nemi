import { useEffect, useRef, useState } from 'react';
import { useLang } from '../i18n.jsx';
import { frameUrl } from '../worlds.js';
import { reduced } from '../scroll.js';
import { Rich } from './Reveal.jsx';

// A sense world: a scroll film on a WebGL canvas (two chapters, each blended from two neighbouring
// frames, with a transition between them) and one short line per chapter on top.
// `progress.current.q` (0..1) comes from the Portal: it is how far the film has been scrolled.

const VS = `#version 300 es
in vec2 p; out vec2 vUv;
void main(){ vUv = p * .5 + .5; gl_Position = vec4(p, 0., 1.); }`;

const FS = `#version 300 es
precision highp float;
in vec2 vUv; out vec4 o;
uniform sampler2D uA0, uA1, uB0, uB1;
uniform float uMixA, uMixB, uT, uZoomA, uZoomB, uTime, uWarp, uPulse, uBlur, uDark;
uniform int uType;
uniform vec2 uRes, uImg;

float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p){ vec2 i = floor(p), f = fract(p); vec2 u = f*f*(3.-2.*f);
  return mix(mix(hash(i), hash(i+vec2(1,0)), u.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), u.x), u.y); }
float fbm(vec2 p){ float v = 0., a = .5; for(int i=0;i<4;i++){ v += a*noise(p); p *= 2.03; a *= .5; } return v; }
float bayer2(vec2 a){ a = floor(a); return fract(a.x/2. + a.y*a.y*.75); }
float bayer4(vec2 a){ return bayer2(.5*a)*.25 + bayer2(a); }
float bayer8(vec2 a){ return bayer4(.5*a)*.25 + bayer2(a); }
float aspect(){ return uRes.x / uRes.y; }

vec2 cover(vec2 uv, float zoom){
  float sa = aspect(), ia = uImg.x / uImg.y;
  vec2 s = sa > ia ? vec2(1., ia / sa) : vec2(sa / ia, 1.);
  return (uv - .5) * s / zoom + .5;
}
vec3 tap(sampler2D t0, sampler2D t1, float m, vec2 uv){
  uv = clamp(uv, vec2(.001), vec2(.999));
  return mix(texture(t0, uv).rgb, texture(t1, uv).rgb, m);
}
vec3 samp(sampler2D t0, sampler2D t1, float m, vec2 suv, float zoom){
  vec2 uv = cover(suv, zoom);
  // heat haze: steam bends the air
  if (uWarp > .001) {
    float n = fbm(vec2(suv.x * 6., suv.y * 4. - uTime * .35));
    uv += vec2(n - .5, (n - .5) * .6) * .012 * uWarp * smoothstep(.0, .7, 1. - suv.y);
  }
  vec3 c = tap(t0, t1, m, uv);
  if (uBlur > .001) { // rack focus
    vec3 acc = c;
    for (int i = 0; i < 8; i++) {
      float a = float(i) * .785398;
      acc += tap(t0, t1, m, uv + vec2(cos(a), sin(a)) * uBlur * .012);
    }
    c = acc / 9.;
  }
  return c;
}
vec3 A(vec2 uv, float z){ return samp(uA0, uA1, uMixA, uv, uZoomA * z); }
vec3 B(vec2 uv, float z){ return samp(uB0, uB1, uMixB, uv, uZoomB * z); }

void main(){
  vec2 uv = vUv;
  float t = uT;
  vec3 col;
  if (t <= 0.) col = A(uv, 1.);
  else if (uType == 1) { // dither: Bayer pixels grow from the centre
    vec2 cell = floor(gl_FragCoord.xy / 6.);
    float rad = length((uv - .5) * vec2(aspect(), 1.));
    float m = step(bayer8(cell) + .002, t * 1.6 - rad * .6);
    col = mix(A(uv, 1. + t * .06), B(uv, 1.1 - t * .1), m);
  } else if (uType == 2) { // ink: a burning front with a glowing edge
    float n = fbm(uv * vec2(aspect(), 1.) * 3. + 3.1);
    float r = t * 1.2 - .1;
    float m = smoothstep(n - .02, n + .02, r);
    float edge = 1. - smoothstep(0., .035, abs(r - n));
    col = mix(A(uv, 1. + t * .05), B(uv, 1.08 - t * .08), m);
    col = mix(col, col * .25, edge * .6) + edge * vec3(.79, .66, .42) * (1. - smoothstep(.85, 1., t));
  } else if (uType == 3) { // zoom through: A rushes at us with radial blur, B settles
    float k = smoothstep(.0, 1., t);
    vec3 a = vec3(0.);
    for (int i = 0; i < 8; i++) a += A(uv, 1. + k * .9 + float(i) * k * .035);
    a = a / 8. + vec3(1., .92, .8) * k * k * .3;
    col = mix(a, B(uv, 1.22 - .22 * k), smoothstep(.45, .85, t));
  } else if (uType == 4) { // light leak sweeping across
    float d = (uv.x * aspect() * .7 + (1. - uv.y) * .45) / (aspect() * .7 + .45);
    float e = t * 1.4 - .2;
    float m = 1. - smoothstep(e - .08, e + .08, d);
    col = mix(A(uv, 1.), B(uv, 1.06 - .06 * t), m);
    col += vec3(1., .66, .36) * exp(-pow((d - e) / .1, 2.)) * .85;
  } else if (uType == 5) { // slices: bands switch one by one, sliding sideways
    float bi = floor(uv.y * 9.);
    float rr = hash(vec2(bi, 3.));
    float lt = clamp((t - rr * .45) / .55, 0., 1.);
    vec2 u2 = uv + vec2((rr - .5) * .25 * sin(lt * 3.14159), 0.);
    col = lt < .5 ? A(u2, 1.) : B(u2, 1.);
  } else { // dissolve
    col = mix(A(uv, 1. + t * .03), B(uv, 1.03 - t * .03), smoothstep(0., 1., t));
  }
  // heartbeat: a soft double pulse of light and pressure at the edges
  vec2 v = uv - .5;
  float vig = dot(v * vec2(aspect() * .75, 1.), v * vec2(aspect() * .75, 1.));
  col *= 1. - vig * (.55 + uPulse * .35);
  col += col * uPulse * .08;
  col = mix(col, vec3(0.02), uDark);
  col += (hash(uv * uRes + fract(uTime * 7.3) * 91.) - .5) * .035;
  o = vec4(col, 1.);
}`;

function createGL(canvas) {
  const gl = canvas.getContext('webgl2', { antialias: false, alpha: false, powerPreference: 'high-performance' });
  if (!gl) return null;
  const sh = (type, src) => {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  };
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS));
  gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
  gl.bindAttribLocation(prog, 0, 'p');
  gl.linkProgram(prog);
  gl.useProgram(prog);
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
  const U = {};
  ['uA0', 'uA1', 'uB0', 'uB1', 'uMixA', 'uMixB', 'uT', 'uZoomA', 'uZoomB', 'uTime', 'uWarp', 'uPulse', 'uBlur', 'uDark', 'uType', 'uRes', 'uImg']
    .forEach((n) => { U[n] = gl.getUniformLocation(prog, n); });
  const tex = [0, 1, 2, 3].map((i) => {
    const t = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + i);
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, 1, 1, 0, gl.RGB, gl.UNSIGNED_BYTE, new Uint8Array([10, 10, 10]));
    return { t, img: null };
  });
  gl.uniform1i(U.uA0, 0); gl.uniform1i(U.uA1, 1); gl.uniform1i(U.uB0, 2); gl.uniform1i(U.uB1, 3);
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
  return {
    gl, U,
    // bind an image to a texture unit, uploading only when it changed
    bind(unit, img) {
      if (!img || tex[unit].img === img) return;
      gl.activeTexture(gl.TEXTURE0 + unit);
      gl.bindTexture(gl.TEXTURE_2D, tex[unit].t);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
      tex[unit].img = img;
    },
  };
}

// text: accent words in *...*, split into letters for the reveal
function Letters({ text, start = 0 }) {
  let i = start;
  return text.split(/(\*[^*]+\*)/).filter(Boolean).map((part, pi) => {
    const em = part.startsWith('*');
    const t = em ? part.slice(1, -1) : part;
    const words = t.split(/(\s+)/);
    const inner = words.map((w, wi) => {
      if (/^\s+$/.test(w)) return ' ';
      return (
        <span className="wf-word" key={wi}>
          {[...w].map((ch, ci) => <span className="wf-ch" data-ch={ch} style={{ '--i': i++ }} key={ci}>{ch}</span>)}
        </span>
      );
    });
    return em ? <em key={pi}>{inner}</em> : <span key={pi}>{inner}</span>;
  });
}

const POS = ['bl', 'br', 'bl', 'c', 'br', 'c'];
const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789§&';

export default function WorldFilm({ world, progress, index }) {
  const { L, lang } = useLang();
  const canvas = useRef();
  const wrap = useRef();
  const blocks = useRef([]);
  const counter = useRef();
  const bar = useRef();
  const [mobile] = useState(() => innerWidth / innerHeight < 0.9);
  const n = world.chapters.length;

  useEffect(() => {
    const cv = canvas.current;
    let R;
    try { R = createGL(cv); } catch (e) { R = null; }
    if (!R) { cv.classList.add('nogl'); }
    // frames: chapter by chapter, first frames of every chapter first
    const imgs = world.frames.map((N) => new Array(N).fill(null));
    const ok = world.frames.map((N) => new Array(N).fill(false));
    let started = false;
    const load = () => {
      if (started) return;
      started = true;
      const order = [];
      world.frames.forEach((N, c) => order.push([c, 0], [c, N - 1]));
      world.frames.forEach((N, c) => { for (let k = 1; k < N - 1; k++) order.push([c, k]); });
      let next = 0;
      const pump = () => {
        if (next >= order.length) return;
        const [c, k] = order[next++];
        const im = new Image();
        im.decoding = 'async';
        im.onload = () => { ok[c][k] = true; dirty = true; pump(); };
        im.onerror = pump;
        im.src = frameUrl(world.id, c, k, mobile);
        imgs[c][k] = im;
      };
      for (let j = 0; j < 4; j++) pump();
    };
    // nearest loaded frame of a chapter
    const near = (c, k) => {
      for (let d = 0; d < imgs[c].length; d++) {
        if (k - d >= 0 && ok[c][k - d]) return imgs[c][k - d];
        if (k + d < imgs[c].length && ok[c][k + d]) return imgs[c][k + d];
      }
      return null;
    };
    // start loading one screen before the device comes into view
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { load(); io.disconnect(); } }, { rootMargin: '120% 0px' });
    io.observe(wrap.current);

    let dirty = true;
    let last = -1;
    let raf;
    const t0 = performance.now();
    const resize = () => {
      const dpr = Math.min(1.5, devicePixelRatio || 1);
      const w = wrap.current.clientWidth, h = wrap.current.clientHeight;
      cv.width = Math.round(w * dpr);
      cv.height = Math.round(h * dpr);
      if (R) R.gl.viewport(0, 0, cv.width, cv.height);
      dirty = true;
    };
    resize();
    // the screen gets its real size only after the Portal has measured the viewport
    const ro = new ResizeObserver(resize);
    ro.observe(wrap.current);

    const decode = (el) => {
      // scramble every letter for a moment, then settle (LITORALE)
      const chs = el.querySelectorAll('.wf-ch');
      let tick = 0;
      const id = setInterval(() => {
        tick++;
        chs.forEach((c, i) => {
          const settle = 3 + i * 0.6;
          c.textContent = tick > settle ? c.dataset.ch : (c.dataset.ch === ' ' ? ' ' : GLYPHS[(Math.random() * GLYPHS.length) | 0]);
        });
        if (tick > 4 + chs.length * 0.6) clearInterval(id);
      }, 45);
    };

    let active = -1;
    const frame = () => {
      raf = requestAnimationFrame(frame);
      const q = Math.max(0, Math.min(1, progress.current.q));
      const live = world.fx === 'steam' || world.fx === 'pulse';
      if (!dirty && Math.abs(q - last) < 1e-5 && !live) return;
      if (Math.abs(q - last) < 1e-5 && !dirty && live && !progress.current.visible) return;
      last = q;
      dirty = false;
      const time = (performance.now() - t0) / 1000;
      const x = q * n;
      const ci = Math.min(n - 1, Math.floor(x));
      const u = x - ci;
      const isLast = ci === n - 1;
      const play = isLast ? Math.min(1, u / 0.82) : Math.min(1, u / 0.86);
      const N = world.frames[ci];
      const fpos = play * (N - 1);
      const k0 = Math.floor(fpos), k1 = Math.min(N - 1, k0 + 1);
      const tr = !isLast && u > 0.86 ? (u - 0.86) / 0.14 : 0;
      // text blocks: visible in the middle of their chapter (the first one already in the screen)
      const show = (i) => {
        const xi = x - i;
        if (i === 0) return xi < 0.78;
        return xi > 0.06 && xi < (i === n - 1 ? 0.9 : 0.78);
      };
      blocks.current.forEach((el, i) => {
        if (!el) return;
        const on = show(i);
        if (on && !el.classList.contains('in')) {
          el.classList.add('in');
          el.classList.remove('out');
          if (world.fx === 'decode' && !reduced) decode(el.querySelector('.wf-h'));
        } else if (!on && el.classList.contains('in')) {
          el.classList.remove('in');
          el.classList.add('out');
        }
      });
      if (ci !== active) {
        active = ci;
        if (counter.current) counter.current.textContent = `0${ci + 1} / 0${n}`;
      }
      if (bar.current) bar.current.style.transform = `scaleY(${q})`;
      if (!R) return;
      const { gl, U } = R;
      const a0 = near(ci, k0), a1 = near(ci, k1) || a0;
      if (!a0) return;
      R.bind(0, a0);
      R.bind(1, a1);
      if (tr > 0) {
        const b0 = near(ci + 1, 0) || a0;
        const b1 = near(ci + 1, 1) || b0;
        R.bind(2, b0);
        R.bind(3, b1);
      }
      gl.uniform1f(U.uMixA, fpos - k0);
      gl.uniform1f(U.uMixB, tr * 0.6);
      gl.uniform1f(U.uT, tr);
      gl.uniform1i(U.uType, tr > 0 ? world.trans[ci] : 0);
      gl.uniform1f(U.uZoomA, 1.0 + play * 0.05);
      gl.uniform1f(U.uZoomB, 1.0);
      gl.uniform1f(U.uTime, time);
      gl.uniform1f(U.uWarp, world.fx === 'steam' && ci <= 2 ? 1 : 0);
      const beat = (time * 1.25) % 1;
      const pulse = world.fx === 'pulse' ? Math.max(Math.exp(-beat * 9), 0.6 * Math.exp(-Math.max(0, beat - 0.22) * 9) * (beat > 0.22 ? 1 : 0)) : 0;
      gl.uniform1f(U.uPulse, reduced ? 0 : pulse);
      // hotel: every chapter starts slightly out of focus and sharpens (rack focus)
      gl.uniform1f(U.uBlur, world.fx === 'focus' && !(ci === 0 && q === 0) ? 0.45 * Math.max(0, 1 - u / 0.16) : 0);
      gl.uniform1f(U.uDark, isLast ? Math.max(0, (u - 0.86) / 0.14) : 0);
      gl.uniform2f(U.uRes, gl.canvas.width, gl.canvas.height);
      gl.uniform2f(U.uImg, a0.naturalWidth || 1280, a0.naturalHeight || 720);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    };
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); ro.disconnect(); io.disconnect(); };
  }, [world, lang]);

  return (
    <div className={`wf wf-${world.id}`} ref={wrap}>
      <canvas ref={canvas} className="wf-cv" />
      <header className="wf-nav">
        <span className="wf-brand">{L(world.brand)}</span>
        <span className="wf-sense"><i />{L(world.sense)}</span>
      </header>
      <div className="wf-hud" aria-hidden="true">
        <span ref={counter}>01 / 0{n}</span>
        <i><b ref={bar} /></i>
      </div>
      {world.chapters.map((c, i) => (
        <div className={`wf-block wf-${POS[i]}${i === 0 ? ' in' : ''}`} key={`${lang}-${i}`} ref={(el) => { blocks.current[i] = el; }}>
          <p className="wf-eye">0{i + 1} — {L(world.sense).split(' · ')[i % 2 === 0 ? 0 : 1] || L(world.sense)}</p>
          <h2 className="wf-h"><Letters text={L(c.h)} /></h2>
          {c.p && <p className="wf-p"><Rich text={L(c.p)} /></p>}
        </div>
      ))}
      <span className="wf-index" aria-hidden="true">0{index + 1}</span>
    </div>
  );
}
