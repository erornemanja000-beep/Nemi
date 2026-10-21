// WebGL2 renderer for the film: two scenes (A, B), each blended from two neighbouring frames,
// plus the "silent line drawing → colour" look and the transitions between scenes.

const VS = `#version 300 es
in vec2 p; out vec2 vUv;
void main(){ vUv = p * .5 + .5; gl_Position = vec4(p, 0., 1.); }`;

const FS = `#version 300 es
precision highp float;
in vec2 vUv; out vec4 o;
uniform sampler2D uA0, uA1, uB0, uB1;
uniform float uMixA, uMixB, uSkA, uSkB, uZoomA, uZoomB, uDarkA, uDarkB, uT, uTime, uMouseOn, uIntro;
uniform int uType;
uniform vec2 uRes, uImg, uMouse;

const vec3 INK = vec3(.043, .043, .047);
const vec3 BONE = vec3(.937, .918, .886);
const vec3 SIGNAL = vec3(1., .353, .141);

float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p){ vec2 i = floor(p), f = fract(p); vec2 u = f*f*(3.-2.*f);
  return mix(mix(hash(i), hash(i+vec2(1,0)), u.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), u.x), u.y); }
float fbm(vec2 p){ float v = 0., a = .5; for(int i=0;i<4;i++){ v += a*noise(p); p *= 2.03; a *= .5; } return v; }
float bayer2(vec2 a){ a = floor(a); return fract(a.x/2. + a.y*a.y*.75); }
float bayer4(vec2 a){ return bayer2(.5*a)*.25 + bayer2(a); }
float bayer8(vec2 a){ return bayer4(.5*a)*.25 + bayer2(a); }
float lum(vec3 c){ return dot(c, vec3(.299, .587, .114)); }

float aspect(){ return uRes.x / uRes.y; }
vec2 cover(vec2 uv, float zoom){
  float sa = aspect(), ia = uImg.x / uImg.y;
  vec2 s = sa > ia ? vec2(1., ia / sa) : vec2(sa / ia, 1.);
  return (uv - .5) * s / zoom + .5;
}
vec3 samp(sampler2D t0, sampler2D t1, float m, vec2 uv){
  uv = clamp(uv, vec2(.001), vec2(.999));
  return mix(texture(t0, uv).rgb, texture(t1, uv).rgb, m);
}

// one scene: frame blend, silent line drawing, colour reveal (noise front + cursor torch)
vec3 scene(sampler2D t0, sampler2D t1, float m, float sk, float zoom, float dark, vec2 suv, float seed){
  vec2 uv = cover(suv, zoom);
  vec3 col = samp(t0, t1, m, uv);
  if (sk > .001) {
    vec2 px = 1.6 / uImg;
    float tl = lum(samp(t0,t1,m, uv+px*vec2(-1, 1))), tc = lum(samp(t0,t1,m, uv+px*vec2(0, 1))), tr = lum(samp(t0,t1,m, uv+px*vec2(1, 1)));
    float ml = lum(samp(t0,t1,m, uv+px*vec2(-1, 0))),                                           mr = lum(samp(t0,t1,m, uv+px*vec2(1, 0)));
    float bl = lum(samp(t0,t1,m, uv+px*vec2(-1,-1))), bc = lum(samp(t0,t1,m, uv+px*vec2(0,-1))), br = lum(samp(t0,t1,m, uv+px*vec2(1,-1)));
    float gx = (tr + 2.*mr + br) - (tl + 2.*ml + bl);
    float gy = (tl + 2.*tc + tr) - (bl + 2.*bc + br);
    float e = length(vec2(gx, gy));
    float line = smoothstep(.11, .42, e) * .85;
    // blueprint paper: ink, a whisper of the picture, a faint grid, bone lines
    vec2 g = abs(fract(suv * vec2(aspect(), 1.) * 18.) - .5);
    float grid = (1. - smoothstep(.0, .025, min(g.x, g.y))) * .035;
    vec3 sketch = INK + lum(col) * .09 + grid + line * BONE * .9;
    float r = (1. - sk) * 1.15;
    float n = fbm(suv * vec2(aspect(), 1.) * 2.4 + seed);
    float mask = smoothstep(n - .045, n + .045, r);
    float edge = (1. - smoothstep(0., .022, abs(r - n))) * step(.01, r) * step(r, 1.12);
    vec2 d = (suv - uMouse) * vec2(aspect(), 1.);
    float torch = (1. - smoothstep(.05, .26, length(d))) * uMouseOn;
    mask = max(mask, torch * .92);
    col = mix(sketch, col, mask) + edge * SIGNAL * .8;
  }
  return mix(col, INK, dark);
}

vec3 sceneA(vec2 uv, float z){ return scene(uA0, uA1, uMixA, uSkA, uZoomA * z, uDarkA, uv, 1.7); }
vec3 sceneB(vec2 uv, float z){ return scene(uB0, uB1, uMixB, uSkB, uZoomB * z, uDarkB, uv, 7.3); }

void main(){
  vec2 uv = vUv;
  float t = uT;
  vec3 col;
  if (t <= 0.) col = sceneA(uv, 1.);
  else if (t >= 1.) col = sceneB(uv, 1.);
  else if (uType == 1) { // dither: Bayer pixels from the centre outwards
    vec2 cell = floor(gl_FragCoord.xy / 7.);
    float rad = length((uv - .5) * vec2(aspect(), 1.));
    float th = t * 1.55 - rad * .55;
    float m = step(bayer8(cell) + .002, th);
    col = mix(sceneA(uv, 1. + t * .08), sceneB(uv, 1.12 - t * .12), m);
  } else if (uType == 2) { // ink: a burning noise front with a glowing edge
    float n = fbm(uv * vec2(aspect(), 1.) * 3. + 3.1);
    float r = t * 1.2 - .1;
    float m = smoothstep(n - .02, n + .02, r);
    float edge = 1. - smoothstep(0., .035, abs(r - n));
    col = mix(sceneA(uv, 1. + t * .05), sceneB(uv, 1.08 - t * .08), m);
    col = mix(col, col * .3, edge * .5) + edge * SIGNAL * .95 * (1. - smoothstep(.85, 1., t));
  } else if (uType == 3) { // zoom through: A rushes towards us with radial blur, B settles in
    float k = smoothstep(.0, 1., t);
    vec3 a = vec3(0.);
    for (int i = 0; i < 8; i++) { float s = 1. + k * .9 + float(i) * k * .035; a += sceneA(uv, s); }
    a /= 8.;
    a += vec3(1., .92, .8) * k * k * .35;
    vec3 b = sceneB(uv, 1.22 - .22 * k);
    col = mix(a, b, smoothstep(.45, .85, t));
  } else if (uType == 4) { // light wipe: a warm leak sweeps across
    float d = (uv.x * aspect() * .7 + (1. - uv.y) * .45) / (aspect() * .7 + .45);
    float e = t * 1.4 - .2;
    float m = 1. - smoothstep(e - .06, e + .06, d);
    col = mix(sceneA(uv, 1.), sceneB(uv, 1.06 - .06 * t), m);
    col += vec3(1., .62, .32) * exp(-pow((d - e) / .09, 2.)) * .9;
  } else if (uType == 5) { // slices: bands switch one by one, sliding sideways
    float bands = 11.;
    float bi = floor(uv.y * bands);
    float rr = hash(vec2(bi, 3.));
    float lt = clamp((t - rr * .45) / .55, 0., 1.);
    float shift = (rr - .5) * .22 * sin(lt * 3.14159);
    vec2 u2 = uv + vec2(shift, 0.);
    col = lt < .5 ? sceneA(u2, 1.) : sceneB(u2, 1.);
    col.r = mix(col.r, (lt < .5 ? sceneA(u2 + vec2(.006, 0.), 1.) : sceneB(u2 + vec2(.006, 0.), 1.)).r, abs(shift) * 4.);
  } else if (uType == 6) { // to black
    col = mix(sceneA(uv, 1. + t * .1), INK, smoothstep(0., 1., t));
  } else {
    col = mix(sceneA(uv, 1.), sceneB(uv, 1.), t);
  }

  // cursor light, vignette, grain
  vec2 d = (uv - uMouse) * vec2(aspect(), 1.);
  col += vec3(1., .78, .55) * exp(-dot(d, d) / .05) * .06 * uMouseOn;
  vec2 v = uv - .5;
  col *= 1. - dot(v, v) * .55;
  col = mix(col, INK, uIntro);
  col += (hash(uv * uRes + fract(uTime * 7.3) * 91.) - .5) * .045;
  o = vec4(col, 1.);
}`;

export function createRenderer(canvas, imgSize) {
  const gl = canvas.getContext('webgl2', { antialias: false, alpha: false, powerPreference: 'high-performance', preserveDrawingBuffer: false });
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
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  gl.useProgram(prog);

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);

  const U = {};
  const n = gl.getProgramParameter(prog, gl.ACTIVE_UNIFORMS);
  for (let i = 0; i < n; i++) { const { name } = gl.getActiveUniform(prog, i); U[name] = gl.getUniformLocation(prog, name); }

  // four texture units: A0, A1, B0, B1
  const tex = [];
  const bound = [null, null, null, null];
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
  ['uA0', 'uA1', 'uB0', 'uB1'].forEach((name, i) => {
    const t = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + i);
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([11, 11, 12, 255]));
    gl.uniform1i(U[name], i);
    tex.push(t);
  });
  gl.uniform2f(U.uImg, imgSize[0], imgSize[1]);

  function setImage(unit, img) {
    if (!img || bound[unit] === img) return;
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, tex[unit]);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
    bound[unit] = img;
  }

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, innerWidth < 800 ? 2 : 1.5);
    const w = Math.round(canvas.clientWidth * dpr);
    const h = Math.round(canvas.clientHeight * dpr);
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    gl.viewport(0, 0, w, h);
    gl.uniform2f(U.uRes, w, h);
  }

  // s: { a:{img0,img1,mix,sk,zoom,dark}, b:{...}|null, t, type, time, mouse:[x,y], mouseOn, intro }
  function draw(s) {
    setImage(0, s.a.img0); setImage(1, s.a.img1);
    gl.uniform1f(U.uMixA, s.a.mix); gl.uniform1f(U.uSkA, s.a.sk); gl.uniform1f(U.uZoomA, s.a.zoom); gl.uniform1f(U.uDarkA, s.a.dark);
    if (s.b) {
      setImage(2, s.b.img0); setImage(3, s.b.img1);
      gl.uniform1f(U.uMixB, s.b.mix); gl.uniform1f(U.uSkB, s.b.sk); gl.uniform1f(U.uZoomB, s.b.zoom); gl.uniform1f(U.uDarkB, s.b.dark);
    }
    gl.uniform1f(U.uT, s.b ? s.t : 0);
    gl.uniform1i(U.uType, s.type);
    gl.uniform1f(U.uTime, s.time);
    gl.uniform2f(U.uMouse, s.mouse[0], s.mouse[1]);
    gl.uniform1f(U.uMouseOn, s.mouseOn);
    gl.uniform1f(U.uIntro, s.intro);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  return { gl, resize, draw };
}
