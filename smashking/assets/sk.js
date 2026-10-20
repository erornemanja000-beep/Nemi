/* Smash King – Bildfolgen am Scroll (Smash + King), Funken, Karte, Sprache, Öffnungszeiten, Feuer im Footer. */
(function () {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = (t) => 1 - Math.pow(1 - t, 3);
  const smooth = (t) => t * t * (3 - 2 * t);
  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MOBILE = matchMedia('(max-width: 820px)').matches;   // set kadrova se bira jednom, pri učitavanju
  const SET = MOBILE ? 'm' : 'd';
  const DPR = Math.min(devicePixelRatio || 1, MOBILE ? 2 : 1.75);
  let W = innerWidth, H = innerHeight;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* privatni prozor */ } },
  };

  /* ---------------- Sprache (DE u HTML-u, EN u data-en) ---------------- */
  let lang = 'de';
  function setLang(l) {
    lang = l;
    document.documentElement.lang = l;
    $$('[data-en]').forEach((el) => {
      if (el.dataset.de === undefined) el.dataset.de = el.innerHTML;
      el.innerHTML = l === 'en' ? el.dataset.en : el.dataset.de;
    });
    $('#lang').textContent = l === 'en' ? 'DE' : 'EN';
    store.set('sk-lang', l);
    updateOpen();
  }
  $('#lang').addEventListener('click', () => setLang(lang === 'de' ? 'en' : 'de'));

  /* ---------------- Bildfolgen ---------------- */
  class Seq {
    constructor(sec) {
      this.sec = sec;
      this.stage = $('.stage', sec);
      this.name = sec.dataset.seq;
      this.set = sec.dataset.set || SET;   // data-set="d": isti kadrovi i za telefon (verzija za pregled)
      this.count = +sec.dataset.count;
      this.cover = sec.dataset.fit === 'cover';
      this.cv = $('.seq-canvas', sec);
      this.g = this.cv.getContext('2d');
      this.imgs = new Array(this.count);
      this.state = new Uint8Array(this.count);   // 0 nije, 1 učitava se, 2 spremno
      this.keys = (sec.dataset.keys || '0,0 1,1').split(' ').map((s) => s.split(',').map(Number));
      this.p = 0; this.target = 0; this.drawn = -1; this.top = 0; this.len = 1; this.near = true;
      this.layers = $$('.layer', sec).map((el) => ({ el, from: +el.dataset.from, to: +el.dataset.to, o: -1, own: el.classList.contains('smash-word') }));
    }
    src(i) { return `assets/seq/${this.name}/${this.set}/${String(i + 1).padStart(4, '0')}.webp`; }
    load(i) {
      if (this.state[i]) return Promise.resolve();
      this.state[i] = 1;
      return new Promise((res) => {
        const im = new Image();
        im.decoding = 'async';
        im.onload = () => { this.imgs[i] = im; this.state[i] = 2; if (Math.abs(i - this.target) < 4) this.drawn = -1; res(); };
        im.onerror = () => { this.state[i] = 0; res(); };
        im.src = this.src(i);
      });
    }
    nearest(i) {
      if (this.state[i] === 2) return i;
      for (let d = 1; d < this.count; d++) {
        if (i - d >= 0 && this.state[i - d] === 2) return i - d;
        if (i + d < this.count && this.state[i + d] === 2) return i + d;
      }
      return -1;
    }
    // skrol (0–1) -> pozicija u klipu (0–1), po tačkama iz data-keys
    map(p) {
      const k = this.keys;
      for (let j = 1; j < k.length; j++) {
        if (p <= k[j][0]) return lerp(k[j - 1][1], k[j][1], (p - k[j - 1][0]) / ((k[j][0] - k[j - 1][0]) || 1));
      }
      return 1;
    }
  }
  const SEQS = $$('.story').map((s) => new Seq(s));
  const HERO = SEQS.find((s) => s.name === 'smash');

  function fitCanvas(S) {
    const r = S.cv.getBoundingClientRect();
    const w = Math.round(r.width * DPR), h = Math.round(r.height * DPR);
    if (w && h && (S.cv.width !== w || S.cv.height !== h)) { S.cv.width = w; S.cv.height = h; S.drawn = -1; }
  }
  function drawFrame(S, i) {
    const im = S.imgs[i];
    const g = S.g, cw = g.canvas.width, ch = g.canvas.height, iw = im.naturalWidth, ih = im.naturalHeight;
    let s, x, y;
    if (S.cover) {
      // na kompjuteru je tekst levo, pa kadar malo uvećamo i pomerimo udesno
      const zoom = MOBILE ? 1 : 1.12;
      s = Math.max(cw / iw, ch / ih) * zoom;
      x = clamp(cw * (MOBILE ? .5 : .57) - iw * s / 2, cw - iw * s, 0);
      y = (ch - ih * s) / 2;
    } else {
      s = Math.min(cw / iw, ch / ih);
      x = (cw - iw * s) / 2; y = (ch - ih * s) / 2;
      g.clearRect(0, 0, cw, ch);
    }
    g.drawImage(im, x, y, iw * s, ih * s);
  }

  // red učitavanja: prvo grubo (svaki 8.), pa sve gušće; najviše 6 istovremeno
  const Q = []; let active = 0;
  function enqueue(S, step, from = 0) { for (let i = from; i < S.count; i += step) Q.push([S, i]); pump(); }
  function pump() {
    while (active < 6 && Q.length) {
      const [S, i] = Q.shift();
      if (S.state[i]) continue;
      active++;
      S.load(i).then(() => { active--; pump(); });
    }
  }

  function measure() {
    W = innerWidth; H = innerHeight;
    SEQS.forEach((S) => {
      S.top = S.sec.getBoundingClientRect().top + scrollY;
      S.len = Math.max(1, S.sec.offsetHeight - S.stage.offsetHeight);
      fitCanvas(S);
    });
    fx.resize();
  }
  const progress = (S) => clamp((scrollY - S.top) / S.len);

  function layerAlpha(L, p) {
    const a = L.from <= 0 ? 1 : smooth(clamp((p - L.from) / 0.05));
    const b = L.to >= 1 ? 1 : smooth(clamp((L.to - p) / 0.05));
    return Math.min(a, b);
  }
  function renderLayers(S) {
    for (const L of S.layers) {
      if (L.own) continue;
      const o = layerAlpha(L, S.p);
      if (Math.abs(o - L.o) < 0.002) continue;
      L.o = o;
      L.el.style.opacity = o.toFixed(3);
      const dir = S.p < (L.from + L.to) / 2 ? 1 : -1;
      L.el.style.translate = `0 ${((1 - o) * 26 * dir).toFixed(1)}px`;
      L.el.classList.toggle('off', o < 0.01);
    }
  }

  /* „SMASH!“ se spljošti tačno kad presa udari (kadar ~42 od 121) */
  const smashWrap = $('.smash-word'), smashWord = $('#smashWord');
  let hit = false;
  function renderSmash(p) {
    const a = smooth(clamp((p - .2) / .05)) * (1 - smooth(clamp((p - .43) / .06)));
    const s = ease(clamp((p - .27) / .08));
    const pre = Math.sin(clamp((p - .2) / .07) * Math.PI) * .07;   // malo se istegne pre udarca
    smashWrap.style.opacity = a.toFixed(3);
    smashWrap.classList.toggle('off', a < .01);
    smashWord.style.transform = `scale(${(lerp(1, 1.38, s) - pre * .5).toFixed(3)}, ${(lerp(1, .3, s) + pre).toFixed(3)})`;
    const isHit = s > .995;
    smashWord.classList.toggle('hit', isHit);
    if (isHit && !hit) { hit = true; impact(); }
    if (p < .25) hit = false;
  }
  function impact() {
    if (REDUCED) return;
    const st = HERO.stage;
    st.classList.remove('shake'); void st.offsetWidth; st.classList.add('shake');
    setTimeout(() => st.classList.remove('shake'), 450);
    fx.burst(W * (MOBILE ? .5 : .56), H * (MOBILE ? .5 : .6), MOBILE ? 70 : 120);
    try { if (navigator.userActivation && navigator.userActivation.hasBeenActive) navigator.vibrate && navigator.vibrate(35); } catch (e) { /* nema vibracije */ }
  }

  /* ---------------- Funken (žar u vazduhu + prasak pri udaru) ---------------- */
  const fx = (function () {
    const cv = $('#fx'), g = cv.getContext('2d');
    const P = [];
    let amb = 1;
    const MAX = MOBILE ? 24 : 46;
    function resize() { cv.width = W; cv.height = H; }
    function ember() {
      return { k: 0, x: Math.random() * W, y: H + 10, vx: (Math.random() - .5) * .4, vy: -(.35 + Math.random() * 1.1),
        r: .6 + Math.random() * 1.9, t: 0, life: 260 + Math.random() * 420, ph: Math.random() * 6.28 };
    }
    function burst(x, y, n) {
      for (let i = 0; i < n; i++) {
        const a = Math.PI + Math.random() * Math.PI, sp = 3 + Math.random() * (MOBILE ? 9 : 13);
        P.push({ k: 1, x: x + (Math.random() - .5) * 120, y, vx: Math.cos(a) * sp * 1.25, vy: Math.sin(a) * sp, t: 0, life: 35 + Math.random() * 55, r: .8 + Math.random() * 1.6 });
      }
    }
    function step() {
      if (REDUCED) { g.clearRect(0, 0, W, H); return; }
      g.clearRect(0, 0, W, H);
      g.globalCompositeOperation = 'lighter';
      let embers = 0;
      for (let i = P.length - 1; i >= 0; i--) {
        const p = P[i];
        p.t++;
        if (p.k === 0) {
          embers++;
          p.x += p.vx + Math.sin((p.t + p.ph * 40) / 38) * .35; p.y += p.vy;
          const f = Math.min(1, p.t / 40) * (1 - p.t / p.life);
          const fl = .6 + .4 * Math.sin(p.t * .3 + p.ph);
          g.fillStyle = `rgba(255,${120 + (p.ph * 20 | 0)},40,${(.12 * f * amb).toFixed(3)})`;
          g.beginPath(); g.arc(p.x, p.y, p.r * 4, 0, 6.283); g.fill();
          g.fillStyle = `rgba(255,${190 + (p.ph * 9 | 0)},110,${(.85 * f * fl * amb).toFixed(3)})`;
          g.beginPath(); g.arc(p.x, p.y, p.r, 0, 6.283); g.fill();
        } else {
          p.vx *= .975; p.vy = p.vy * .975 + .28; p.x += p.vx; p.y += p.vy;
          const f = 1 - p.t / p.life;
          g.strokeStyle = `rgba(255,${150 + (f * 90 | 0)},${50 + (f * 60 | 0)},${f.toFixed(3)})`;
          g.lineWidth = p.r; g.lineCap = 'round';
          g.beginPath(); g.moveTo(p.x, p.y); g.lineTo(p.x - p.vx * 2.2, p.y - p.vy * 2.2); g.stroke();
        }
        if (p.t >= p.life || p.y < -20) P.splice(i, 1);
      }
      if (embers < MAX * amb && Math.random() < .35) P.push(ember());
      g.globalCompositeOperation = 'source-over';
    }
    return { resize, burst, step, set amb(v) { amb += (v - amb) * .05; }, get amb() { return amb; } };
  })();

  /* ---------------- Nav, meni, aktivni link ---------------- */
  const nav = $('#nav'), mobileBar = $('#mobileBar');
  const links = $$('#navLinks a').map((a) => ({ a, sec: $(a.getAttribute('href')) }));
  $('#menuBtn').addEventListener('click', () => {
    const open = document.body.classList.toggle('menu-open');
    $('#menuBtn').setAttribute('aria-expanded', open);
  });
  links.forEach(({ a }) => a.addEventListener('click', () => { document.body.classList.remove('menu-open'); $('#menuBtn').setAttribute('aria-expanded', 'false'); }));
  function renderNav() {
    nav.classList.toggle('solid', scrollY > 40);
    mobileBar.classList.toggle('show', scrollY > H * .7 && scrollY + H < document.documentElement.scrollHeight - 160);
    const y = scrollY + H * .45;
    let cur = null;
    links.forEach((l) => { if (l.sec && l.sec.offsetTop <= y) cur = l; });
    links.forEach((l) => l.a.classList.toggle('on', l === cur));
  }

  /* ---------------- Glavna petlja ---------------- */
  let last = -1;
  function frame() {
    for (const S of SEQS) {
      const top = S.top, bottom = S.top + S.sec.offsetHeight;
      S.near = scrollY + H > top - H * .5 && scrollY < bottom + H * .5;
      if (!S.near) continue;
      const t = progress(S);
      S.p = REDUCED ? t : S.p + (t - S.p) * .18;
      if (Math.abs(t - S.p) < .0004) S.p = t;
      S.target = Math.round(S.map(S.p) * (S.count - 1));
      const n = S.nearest(S.target);
      if (n >= 0 && n !== S.drawn) { drawFrame(S, n); S.drawn = n; }
      renderLayers(S);
    }
    if (HERO.near) renderSmash(HERO.p);
    fx.amb = SEQS.some((S) => S.near && scrollY >= S.top - H * .3 && scrollY <= S.top + S.len) ? 1 : .18;
    fx.step();
    if (scrollY !== last) { last = scrollY; renderNav(); }
    requestAnimationFrame(frame);
  }

  /* ---------------- Karte: aktivni burger ---------------- */
  const bItems = $$('.b-item');
  function setBurger(i) { bItems.forEach((li, j) => li.classList.toggle('is-active', i === j)); }
  bItems.forEach((li, i) => {
    const b = $('.b-btn', li);
    b.addEventListener('pointerenter', () => { if (!MOBILE) setBurger(i); });
    b.addEventListener('focus', () => setBurger(i));
    b.addEventListener('click', () => setBurger(i));
  });

  /* ---------------- Reveal ---------------- */
  const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .14 });
  $$('.reveal, .promise-photo').forEach((el) => io.observe(el));

  /* ---------------- Öffnungszeiten (Wien) ---------------- */
  // TODO klijent: potvrditi radno vreme (na starom sajtu stoje tri različite verzije)
  const HOURS = { 0: [11.5, 21], 1: [11.5, 23], 2: [11.5, 23], 3: [11.5, 23], 4: [11.5, 23], 5: [11.5, 23], 6: [11.5, 23] };
  const fmt = (h) => `${String(Math.floor(h)).padStart(2, '0')}:${String(Math.round((h % 1) * 60)).padStart(2, '0')}`;
  function vienna() {
    const parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Vienna', weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).formatToParts(new Date());
    const get = (t) => (parts.find((p) => p.type === t) || {}).value;
    const day = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(get('weekday'));
    return { day, h: +get('hour') + +get('minute') / 60 };
  }
  function updateOpen() {
    const el = $('#openState'); if (!el) return;
    const { day, h } = vienna();
    const [o, c] = HOURS[day];
    const de = lang === 'de';
    let txt, open = false;
    if (h >= o && h < c) { open = true; txt = de ? `Jetzt geöffnet · bis ${fmt(c)}` : `Open now · until ${fmt(c)}`; }
    else if (h < o) txt = de ? `Geschlossen · öffnet um ${fmt(o)}` : `Closed · opens at ${fmt(o)}`;
    else txt = de ? `Geschlossen · morgen ab ${fmt(HOURS[(day + 1) % 7][0])}` : `Closed · opens tomorrow ${fmt(HOURS[(day + 1) % 7][0])}`;
    el.classList.toggle('open', open);
    $('span', el).textContent = txt;
    const rows = $$('#hours > div');
    rows.forEach((r, i) => r.classList.toggle('today', day === 0 ? i === 1 : i === 0));
  }
  setInterval(updateOpen, 60000);

  /* ---------------- Bestellen (dialog) ---------------- */
  const dlg = $('#order');
  $$('[data-order]').forEach((b) => b.addEventListener('click', () => {
    if (dlg.showModal) dlg.showModal(); else location.hash = '#besuch';
  }));
  dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });

  /* ---------------- Karte erst auf Klick (DSGVO) ---------------- */
  const mapLoad = $('#mapLoad');
  if (mapLoad) mapLoad.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.title = 'Karte: Smash King, Viktor-Adler-Markt 53/54';
    f.loading = 'lazy';
    f.src = 'https://www.openstreetmap.org/export/embed.html?bbox=16.3700%2C48.1738%2C16.3830%2C48.1797&layer=mapnik&marker=48.17674%2C16.37641';
    $('#map').replaceChildren(f);
  });

  /* ---------------- Feuer im Footer (WebGL, nach „Shader Fire“ von 21st.dev / radiumcoders) ---------------- */
  (function fire() {
    const cv = $('#fire'); if (!cv || REDUCED) return;
    const gl = cv.getContext('webgl', { alpha: true, premultipliedAlpha: false, antialias: false, depth: false });
    if (!gl) return;
    const VS = 'attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}';
    const FS = `precision highp float;
uniform vec2 R;uniform float T;uniform vec2 M;
float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float n(vec2 p){vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.-2.*f);return mix(h(i),h(i+vec2(1,0)),u.x)+(h(i+vec2(0,1))-h(i))*u.y*(1.-u.x)+(h(i+vec2(1,1))-h(i+vec2(1,0)))*u.x*u.y;}
float fb(vec2 p){float v=0.,a=.5;mat2 m=mat2(1.6,1.2,-1.2,1.6);for(int i=0;i<5;i++){v+=a*n(p);p=m*p;a*=.5;}return v;}
void main(){vec2 uv=gl_FragCoord.xy/R;float as=R.x/R.y;float t=T*.55;float climb=.7;
vec2 q=vec2(uv.x*as*1.85,uv.y*1.55-t*.48);q.x+=sin(uv.y*7.+t*1.6)*.045*(.25+uv.y);
vec2 w1=vec2(fb(q*1.7+vec2(t*.28,t*.22)),fb(q*1.7+vec2(-t*.24,t*.31)+5.2));q+=(w1-.5)*.58;
vec2 w2=vec2(fb(q*3.4-vec2(t*.52,0.)),fb(q*3.4+vec2(0.,t*.44)+2.7));q+=(w2-.5)*.26;
float s=fb(q*2.35),d=fb(q*7.2+vec2(0.,t*1.7));float fl=.9+.1*sin(t*13.+uv.x*9.+s*6.);float f=(s*.68+d*.32)*fl;
float tp=pow(clamp(1.-uv.y/climb,0.,1.),1.35);float co=pow(clamp(1.-uv.y/(climb*.42),0.,1.),2.1);f=f*tp+co*s*.38;
float md=length((uv-M)*vec2(as,1.));f+=exp(-md*6.8)*.3*(.55+.45*s);
f*=smoothstep(0.,.05,uv.y+.015);f=smoothstep(.22,.74,f)*1.05;f=clamp(f,0.,1.);
vec3 c1=vec3(.64,.23,.09),c2=vec3(.83,.41,.16),c3=vec3(1.,.74,.23);
vec3 c=mix(c1,c2,smoothstep(.08,.48,f));c=mix(c,c3,pow(smoothstep(.42,.96,f),1.55));
gl_FragColor=vec4(c*f,f*.95);}`;
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); return gl.getShaderParameter(o, gl.COMPILE_STATUS) ? o : null; };
    const vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, FS);
    if (!vs || !fs) return;
    const pr = gl.createProgram(); gl.attachShader(pr, vs); gl.attachShader(pr, fs); gl.linkProgram(pr);
    if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) return;
    gl.useProgram(pr);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, 'a'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const uR = gl.getUniformLocation(pr, 'R'), uT = gl.getUniformLocation(pr, 'T'), uM = gl.getUniformLocation(pr, 'M');
    const m = { x: .5, y: .1 }, tm = { x: .5, y: .1 };
    let on = false, raf = 0;
    const t0 = performance.now();
    const size = () => { const r = cv.parentElement.getBoundingClientRect(), d = MOBILE ? 1 : Math.min(devicePixelRatio || 1, 1.5); cv.width = Math.max(1, r.width * d | 0); cv.height = Math.max(1, r.height * d | 0); gl.viewport(0, 0, cv.width, cv.height); };
    size(); addEventListener('resize', size);
    addEventListener('pointermove', (e) => { const r = cv.parentElement.getBoundingClientRect(); tm.x = (e.clientX - r.left) / r.width; tm.y = 1 - (e.clientY - r.top) / r.height; }, { passive: true });
    const tick = (now) => {
      if (!on) return;
      m.x += (tm.x - m.x) * .05; m.y += (tm.y - m.y) * .05;
      gl.uniform2f(uR, cv.width, cv.height); gl.uniform1f(uT, (now - t0) / 1000); gl.uniform2f(uM, m.x, m.y);
      gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
      raf = requestAnimationFrame(tick);
    };
    new IntersectionObserver(([e]) => { on = e.isIntersecting; cancelAnimationFrame(raf); if (on) raf = requestAnimationFrame(tick); }).observe(cv.parentElement);
  })();

  /* ---------------- Start ---------------- */
  const saved = store.get('sk-lang');
  if (saved === 'en' || (!saved && /^en\b/i.test(navigator.language || '') && !/^de/i.test(navigator.language || ''))) setLang('en');
  else updateOpen();

  measure();
  addEventListener('resize', () => { measure(); SEQS.forEach((S) => { S.drawn = -1; }); });
  addEventListener('orientationchange', () => setTimeout(measure, 300));
  addEventListener('load', measure);

  // loader čeka grubi set kadrova za prvi ekran (najviše 4,5 s)
  const loader = $('#loader'), bar = $('#loaderBar');
  const first = [];
  for (let i = 0; i < HERO.count; i += 8) first.push(i);
  let done = 0;
  const finish = () => { if (loader.classList.contains('done')) return; bar.style.width = '100%'; setTimeout(() => loader.classList.add('done'), 250); };
  Promise.all(first.map((i) => HERO.load(i).then(() => { done++; bar.style.width = `${Math.round(done / first.length * 100)}%`; }))).then(finish);
  setTimeout(finish, 4500);
  const KING = SEQS.find((s) => s.name === 'king');
  enqueue(KING, 8);
  enqueue(HERO, 2);
  enqueue(KING, 4, 2);
  enqueue(HERO, 1);
  enqueue(KING, 2, 1);
  enqueue(KING, 1);
  requestAnimationFrame(frame);
})();
