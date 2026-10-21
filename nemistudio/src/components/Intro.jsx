import { useEffect, useRef, useState } from 'react';
import { useLang } from '../i18n.jsx';
import { isPortrait } from '../film/frames.js';

// The opening: an eye, the pupil suddenly widens, the camera dives in,
// and history rushes past in an endless zoom: how people have always wanted to be seen.
const BASE = import.meta.env.BASE_URL + 'intro/';
const EYE_N = 31;
const ERAS = [
  { de: ['Urzeit', 'Der Anfang'], en: ['Prehistory', 'The beginning'] },
  { de: ['Steinzeit', 'Handabdrücke'], en: ['Stone Age', 'Hand prints'] },
  { de: ['Höhlen', 'Die ersten Bilder'], en: ['Caves', 'The first pictures'] },
  { de: ['Feuer', 'Geschichten am Abend'], en: ['Fire', 'Stories at night'] },
  { de: ['Ägypten', 'Hieroglyphen'], en: ['Egypt', 'Hieroglyphs'] },
  { de: ['Antike', 'In Stein gemeißelt'], en: ['Antiquity', 'Carved in stone'] },
  { de: ['1450', 'Buchdruck'], en: ['1450', 'Printing press'] },
  { de: ['1492', 'Neue Welt'], en: ['1492', 'A new world'] },
  { de: ['1910', 'Die Stadt'], en: ['1910', 'The city'] },
  { de: ['1925', 'Radio'], en: ['1925', 'Radio'] },
  { de: ['1955', 'Fernsehen'], en: ['1955', 'Television'] },
  { de: ['1990', 'Computer'], en: ['1990', 'Computers'] },
  { de: ['Heute', 'Online'], en: ['Today', 'Online'] },
];
const LINES = {
  de: ['Seit es Menschen gibt,', 'wollen sie *gesehen* werden.', 'Heute beginnt es mit deiner Website.'],
  en: ['Since the first humans,', 'we have wanted to be *seen*.', 'Today it starts with your website.'],
};
const SKIP = { de: 'Intro überspringen', en: 'Skip intro' };

// timing (seconds)
const T_IN = 0.35, T_HOLD = 1.6, T_DIL = 2.2, T_DIVE = 2.9;
const SLOT0 = 0.42, SLOT1 = 0.27;
const slotDur = (i) => SLOT0 + (SLOT1 - SLOT0) * (i / (ERAS.length - 1));
const SLOTS_END = T_DIVE + ERAS.reduce((a, _, i) => a + slotDur(i), 0);
const T_TEXT = SLOTS_END + 0.15, T_OUT = T_TEXT + 1.9, T_END = T_OUT + 0.6;
const ZOOM = 2.8;

// pupil centre (image coords, y from top) and radius (fraction of image height) per eye frame
function pupil(f) {
  const k = Math.max(0, Math.min(1, (f - 24) / 6));
  return { x: 0.44, y: 0.59 - 0.075 * k, r: 0.096 + 0.04 * Math.max(0, Math.min(1, (f - 16) / 14)) };
}
const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const lerp = (a, b, t) => a + (b - a) * t;

const REEL = /[?&]reel=1/.test(location.search);

export function shouldPlayIntro() {
  if (REEL) return true;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
  if (/[?&]intro=0/.test(location.search)) return false;
  if (/[?&]intro=1/.test(location.search)) return true;
  try { return !sessionStorage.getItem('nemi-intro'); } catch (e) { return true; }
}

export default function Intro({ onDone }) {
  const { L, lang } = useLang();
  const cv = useRef();
  const capBig = useRef();
  const capSmall = useRef();
  const textRef = useRef();
  const [phase, setPhase] = useState('load'); // load → play → out
  const langRef = useRef(lang);
  langRef.current = lang;

  useEffect(() => {
    const canvas = cv.current;
    const ctx = canvas.getContext('2d');
    const v = isPortrait() ? 'm' : 'd';
    const eye = Array.from({ length: EYE_N }, (_, i) => { const im = new Image(); im.src = `${BASE}eye/${v}/${String(i + 1).padStart(3, '0')}.webp`; return im; });
    const hist = ERAS.map((_, i) => { const im = new Image(); im.src = `${BASE}h/${String(i + 1).padStart(2, '0')}.webp`; return im; });
    const ok = (im) => im.complete && im.naturalWidth > 0;
    let W = 0, H = 0, dpr = 1;
    const resize = () => {
      dpr = Math.min(devicePixelRatio || 1, 1.5);
      W = innerWidth; H = innerHeight;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    addEventListener('resize', resize);

    let raf, t0 = 0, started = false, done = false, lastSlot = -1, lastLang = '';
    const startAt = performance.now();
    const finish = () => {
      if (done) return;
      done = true;
      try { sessionStorage.setItem('nemi-intro', '1'); } catch (e) { /* storage blocked */ }
      setPhase('out');
      setTimeout(onDone, 650);
    };
    const skip = () => finish();
    window.__nemiSkipIntro = skip;
    const onKey = (e) => { if (e.key === 'Escape' || e.key === ' ' || e.key === 'Enter') skip(); };
    addEventListener('keydown', onKey);

    // cover-fit an image whose point (ax, ay) (0..1) sits at screen (px, py), scaled by s on top of cover
    function drawAt(im, ax, ay, px, py, s, alpha = 1) {
      const iw = im.naturalWidth, ih = im.naturalHeight;
      const c = Math.max(W / iw, H / ih) * s;
      ctx.globalAlpha = alpha;
      ctx.drawImage(im, px - ax * iw * c, py - ay * ih * c, iw * c, ih * c);
      ctx.globalAlpha = 1;
    }
    const diag = () => Math.hypot(W, H) / 2;
    // pixel scale at which an image covers the screen and a circle of radius diag (round windows stay full circles)
    const base = (im) => Math.max(W / im.naturalWidth, H / im.naturalHeight, (2 * diag()) / Math.min(im.naturalWidth, im.naturalHeight));
    function drawBase(im, px, py, k, alpha = 1) {
      const c = base(im) * k;
      const iw = im.naturalWidth, ih = im.naturalHeight;
      ctx.globalAlpha = alpha;
      ctx.drawImage(im, px - iw * c / 2, py - ih * c / 2, iw * c, ih * c);
      ctx.globalAlpha = 1;
    }

    // an image seen through a round window of radius r at (cx, cy)
    function windowed(im, cx, cy, r, alpha = 1) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();
      drawBase(im, cx, cy, r / diag(), alpha);
      ctx.restore();
      // a thin bright rim, like light catching an iris
      ctx.strokeStyle = `rgba(239,234,226,${0.35 * alpha})`;
      ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.stroke();
    }

    const frame = (now) => {
      raf = requestAnimationFrame(frame);
      if (!started) {
        // start when the eye and the first eras are in, or after 4 s whatever we have
        const ready = eye.every(ok) && hist.slice(0, 4).every(ok);
        if (ready || now - startAt > 4000) { started = true; t0 = now; setPhase('play'); }
        else return;
      }
      // window.__introTime freezes the clock (used to check single moments)
      const t = window.__introTime ?? (now - t0) / 1000;
      ctx.fillStyle = '#0b0b0c';
      ctx.fillRect(0, 0, W, H);

      if (t < T_DIVE) {
        // ---- the eye ----
        let f;
        if (t < T_HOLD) f = lerp(0, 17, clamp01((t - T_IN * 0.5) / (T_HOLD - T_IN * 0.5)));
        else f = lerp(17, EYE_N - 1, ease(clamp01((t - T_HOLD) / (T_DIL - T_HOLD))));
        const im = eye[Math.round(f)];
        const p = pupil(f);
        // zoom: gentle, then a dive into the pupil
        const iw = im.naturalWidth || 1280, ih = im.naturalHeight || 720;
        const c1 = Math.max(W / iw, H / ih);
        const A1x = W / 2 + (p.x - 0.5) * iw * c1, A1y = H / 2 + (p.y - 0.5) * ih * c1;
        const rBase = p.r * ih * c1;
        const dil = 1 + 0.75 * ease(clamp01((t - T_HOLD - 0.25) / (T_DIL - T_HOLD)));
        let S;
        if (t < T_DIL) S = lerp(1, 1.9, ease(clamp01((t - T_HOLD + 0.2) / (T_DIL - T_HOLD + 0.2)))) * lerp(1, 1.06, clamp01(t / T_HOLD));
        else {
          const k = clamp01((t - T_DIL) / (T_DIVE - T_DIL));
          const sEnd = diag() / (rBase * dil);
          S = 1.9 * 1.06 * Math.pow(sEnd / (1.9 * 1.06), k * k);
        }
        const m = clamp01((S - 1) / 3);
        const cx = lerp(A1x, W / 2, ease(m)), cy = lerp(A1y, H / 2, ease(m));
        const alpha = clamp01(t / T_IN);
        if (ok(im)) drawAt(im, p.x, p.y, cx, cy, S, alpha);
        // the pupil widens (black disc with a soft edge)
        const r = rBase * S * dil;
        if (dil > 1.01) {
          const g = ctx.createRadialGradient(cx, cy, r * 0.75, cx, cy, r * 1.08);
          g.addColorStop(0, 'rgba(5,5,6,1)');
          g.addColorStop(1, 'rgba(5,5,6,0)');
          ctx.fillStyle = g;
          ctx.beginPath(); ctx.arc(cx, cy, r * 1.08, 0, Math.PI * 2); ctx.fill();
        }
        // the first era appears inside the pupil
        const inA = clamp01((t - (T_DIL - 0.15)) / 0.45);
        if (inA > 0 && ok(hist[0])) windowed(hist[0], cx, cy, r * (0.93 + 0.07 * clamp01((t - T_DIL) / (T_DIVE - T_DIL))), inA);
        setCaption(-1, t);
      } else if (t < SLOTS_END + 0.6) {
        // ---- history: endless zoom through round windows ----
        let acc = T_DIVE, i = 0;
        while (i < ERAS.length - 1 && t > acc + slotDur(i)) { acc += slotDur(i); i++; }
        const u = clamp01((t - acc) / slotDur(i));
        const last = i === ERAS.length - 1;
        const cur = hist[i];
        const s = Math.pow(ZOOM, u);
        if (ok(cur)) drawBase(cur, W / 2, H / 2, s);
        if (!last) {
          const nx = hist[i + 1];
          const R = diag() * Math.pow(ZOOM, u - 1);
          if (ok(nx)) windowed(nx, W / 2, H / 2, R);
        } else {
          // the last era (a website reflected in glasses) dissolves into ink
          const k = clamp01((t - acc - slotDur(i) * 0.4) / 0.7);
          ctx.fillStyle = `rgba(11,11,12,${ease(k)})`;
          ctx.fillRect(0, 0, W, H);
        }
        // subtle vignette
        const vg = ctx.createRadialGradient(W / 2, H / 2, diag() * 0.45, W / 2, H / 2, diag());
        vg.addColorStop(0, 'rgba(11,11,12,0)');
        vg.addColorStop(1, 'rgba(11,11,12,0.55)');
        ctx.fillStyle = vg;
        ctx.fillRect(0, 0, W, H);
        // the label follows whichever era fills most of the screen
        setCaption(t > T_TEXT - 0.35 ? -2 : Math.min(ERAS.length - 1, u > 0.55 ? i + 1 : i), t);
      } else {
        setCaption(-2, t);
      }

      // closing lines over ink (driven by the clock, not CSS, so a frozen clock renders them exactly)
      const tl = textRef.current;
      const show = (el, a, b) => {
        const k = ease(clamp01((t - a) / 0.8)) * (1 - ease(clamp01((t - b) / 0.5)));
        el.style.opacity = k;
        el.style.filter = `blur(${(1 - k) * 12}px)`;
        el.style.transform = `translateY(${(1 - k) * 14}px)`;
      };
      show(tl.children[0], T_TEXT, REEL ? 99 : T_OUT);
      show(tl.children[1], T_TEXT + 1.0, REEL ? 99 : T_OUT);
      if (REEL && t > T_OUT) endCard(clamp01((t - T_OUT) / 0.9));
      if (!REEL && t > T_END) finish();
    };

    // end card for the exported reel: the wordmark and the address
    function endCard(k) {
      ctx.fillStyle = '#0b0b0c';
      ctx.globalAlpha = ease(k);
      ctx.fillRect(0, 0, W, H);
      const size = Math.min(W * 0.28, H * 0.2);
      ctx.fillStyle = '#efeae2';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'alphabetic';
      ctx.font = `600 ${size}px "Geist Variable", sans-serif`;
      ctx.letterSpacing = `${-size * 0.06}px`;
      ctx.fillText('nemi', W / 2, H / 2 + size * 0.2);
      const mw = ctx.measureText('nemi').width;
      ctx.fillStyle = '#ff5a24';
      ctx.beginPath();
      ctx.arc(W / 2 + mw / 2 - size * 0.1, H / 2 + size * 0.2 - size * 0.74, size * 0.07, 0, Math.PI * 2);
      ctx.fill();
      ctx.letterSpacing = `${size * 0.012}px`;
      ctx.fillStyle = 'rgba(239,234,226,0.7)';
      ctx.font = `400 ${size * 0.11}px "Geist Mono Variable", monospace`;
      ctx.fillText('NEMISTUDIO.AT', W / 2, H / 2 + size * 0.62);
      ctx.globalAlpha = 1;
      if (k > 0) tl.style.opacity = 1 - ease(k);
    }

    function setCaption(i, t) {
      const lang = langRef.current;
      if (i === lastSlot && lang === lastLang) return;
      lastSlot = i; lastLang = lang;
      const box = capBig.current.parentElement;
      if (i < 0) { box.classList.remove('on'); return; }
      box.classList.add('on');
      capBig.current.textContent = ERAS[i][lang][0];
      capSmall.current.textContent = ERAS[i][lang][1];
      box.style.setProperty('--p', String((i + 1) / ERAS.length));
    }

    raf = requestAnimationFrame(frame);
    return () => {
      cancelAnimationFrame(raf);
      removeEventListener('resize', resize);
      removeEventListener('keydown', onKey);
      delete window.__nemiSkipIntro;
    };
  }, []);

  const lines = LINES[lang];
  const em = (s) => s.split(/(\*[^*]+\*)/).map((p, k) => (p.startsWith('*') ? <em key={k}>{p.slice(1, -1)}</em> : p));
  return (
    <div className={`intro ${phase}`} aria-label="Intro">
      <canvas ref={cv} className="intro-cv" aria-hidden="true" />
      <div className="intro-cap">
        <b ref={capBig} />
        <span ref={capSmall} />
        <i className="intro-prog" />
      </div>
      <div className="intro-text" ref={textRef}>
        <p className="l1">{em(lines[0])}<br />{em(lines[1])}</p>
        <p className="l2">{em(lines[2])}</p>
      </div>
      {phase === 'load' && <div className="intro-load"><i /></div>}
      {!REEL && <button className="intro-skip" onClick={() => window.__nemiSkipIntro && window.__nemiSkipIntro()}>{L(SKIP)} →</button>}
    </div>
  );
}
