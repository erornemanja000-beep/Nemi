import { useEffect, useRef, useState } from 'react';
import { useLang } from '../i18n.jsx';
import { CHAPTERS, INTRO, FINALE, MANIFEST, UI } from '../content.js';
import { Words } from '../components/Reveal.jsx';
import MiniSite from '../components/MiniSite.jsx';
import { TOTAL, segAt, frameState, localOf, clockAt, chapterHoldVh, segById } from './timeline.js';
import { images, nearest, prioritize, IMG_SIZE } from './frames.js';
import { createRenderer } from './gl.js';
import { vhPx, scrollToY, scrollToId } from '../scroll.js';

// text beats: [segment, local in, local out]
const BEATS = {
  intro: ['intro', -9, 0.42],
  prologue: ['curtain', 0.34, 0.92],
  voice: ['city', 0.1, 0.48],
  day: ['city', 0.56, 0.97],
  q: ['night', 0.1, 0.46],
  next: ['night', 0.52, 1.12],
  manifest: ['manifest', 0.2, 9],
};
const CH_TEXT = [0.17, 0.9];
const CH_CARD = [0.33, 0.9];

const SCRAMBLE = 'abcdefghijklmnopqrstuvwxyzäöüABCDEFGHIJKLMNOPRSTUVWZ';

export default function Film({ ready }) {
  const { L, lang } = useLang();
  const wrap = useRef();
  const canvas = useRef();
  const hud = useRef();
  const typed = useRef();
  const [noGl, setNoGl] = useState(false);
  const readyRef = useRef(ready);
  readyRef.current = ready;
  const LRef = useRef(L);
  LRef.current = L;

  // typing the wordmark once the preloader is gone
  useEffect(() => {
    if (!ready) return;
    const el = typed.current;
    const word = INTRO.word;
    let i = 0;
    const id = setInterval(() => {
      i++;
      el.textContent = word.slice(0, i);
      if (i >= word.length) { clearInterval(id); el.parentElement.classList.add('typed'); }
    }, 170);
    return () => clearInterval(id);
  }, [ready]);

  useEffect(() => {
    const root = wrap.current;
    let r = null;
    try { r = createRenderer(canvas.current, IMG_SIZE); } catch (e) { console.warn(e); }
    if (!r) { setNoGl(true); }
    const beats = [...root.querySelectorAll('[data-seg]')];
    const rail = [...root.querySelectorAll('.rail-ch')];
    const clock = root.querySelector('.hud-clock');
    const status = root.querySelector('.hud-status');
    const chip = root.querySelector('.hud-chip-label');
    const pct = root.querySelector('.hud-pct');
    const bar = root.querySelector('.hud-bar i');
    const man = root.querySelector('.manifest');
    let manDone = false;

    const mouse = { x: 0.5, y: 0.5, tx: 0.5, ty: 0.5, on: 0, ton: 0 };
    const fine = matchMedia('(pointer: fine)').matches;
    const onMove = (e) => { mouse.tx = e.clientX / innerWidth; mouse.ty = 1 - e.clientY / innerHeight; mouse.ton = fine ? 1 : 0; };
    const onLeave = () => { mouse.ton = 0; };
    addEventListener('pointermove', onMove, { passive: true });
    document.addEventListener('pointerleave', onLeave);
    const onResize = () => r && r.resize();
    addEventListener('resize', onResize);
    if (r) r.resize();

    let intro = 1;
    let raf;
    let lastChap = -2;
    const t0 = performance.now();

    const layerImgs = (l) => {
      const arr = images[l.seq];
      const i0 = Math.max(0, Math.floor(l.f));
      const a = arr[i0] || nearest(l.seq, l.f);
      const b = arr[i0 + 1];
      return { img0: a, img1: b && arr[i0] ? b : a, mix: b && arr[i0] ? l.f - i0 : 0, sk: l.sk, zoom: l.zoom, dark: l.dark ? 1 : 0 };
    };

    const tick = () => {
      raf = requestAnimationFrame(tick);
      const L = LRef.current;
      const rect = root.getBoundingClientRect();
      const vp = vhPx();
      const vh = Math.max(0, Math.min(TOTAL, -rect.top / vp));
      const visible = rect.bottom > 0 && rect.top < innerHeight;
      if (!visible) return;

      // text beats
      for (const el of beats) {
        const l = localOf(el.dataset.seg, vh);
        const a = +el.dataset.in, b = +el.dataset.out;
        const on = l >= a && l < b;
        el.classList.toggle('on', on);
        el.classList.toggle('past', l >= b);
      }
      if (!manDone && man.classList.contains('on')) { manDone = true; decode(man); }

      // HUD
      const seg = segAt(vh);
      const chap = seg.ch ?? -1;
      const inDay = vh >= segById.city.start + segById.city.len * 0.5 && vh < segById.manifest.start;
      hud.current.classList.toggle('show', inDay);
      clock.textContent = clockAt(vh);
      if (chap !== lastChap) {
        rail.forEach((el, k) => el.classList.toggle('act', k === chap));
        chip.textContent = chap >= 0 ? `${String(chap + 1).padStart(2, '0')} — ${L(CHAPTERS[chap].label)}` : '';
        lastChap = chap;
      }
      const fs = frameState(vh);
      const cur = fs.b && fs.t > 0.5 ? fs.b : fs.a;
      const silent = cur.sk > 0.45;
      status.classList.toggle('loud', !silent);
      status.querySelector('b').textContent = silent ? L(UI.silent) : L(UI.live);
      const p = vh / TOTAL;
      pct.textContent = String(Math.round(p * 100)).padStart(2, '0') + ' %';
      bar.style.transform = `scaleX(${p})`;

      // loading priority follows the viewer
      prioritize(cur.seq);

      if (!r) return;
      if (readyRef.current) intro = Math.max(0, intro - 0.025);
      mouse.x += (mouse.tx - mouse.x) * 0.12;
      mouse.y += (mouse.ty - mouse.y) * 0.12;
      mouse.on += (mouse.ton - mouse.on) * 0.06;
      const A = layerImgs(fs.a);
      if (!A.img0) return;
      const B = fs.b ? layerImgs(fs.b) : null;
      r.draw({
        a: A, b: B && B.img0 ? B : null, t: fs.t, type: fs.type,
        time: (performance.now() - t0) / 1000, mouse: [mouse.x, mouse.y], mouseOn: mouse.on, intro,
      });
    };
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerleave', onLeave);
      removeEventListener('resize', onResize);
    };
  }, []);

  // chapter label in the HUD follows the language
  useEffect(() => {
    const chip = wrap.current.querySelector('.hud-chip-label');
    const act = wrap.current.querySelector('.rail-ch.act');
    if (act) {
      const i = [...wrap.current.querySelectorAll('.rail-ch')].indexOf(act);
      chip.textContent = `${String(i + 1).padStart(2, '0')} — ${L(CHAPTERS[i].label)}`;
    }
  }, [lang]);

  const goChapter = (i) => scrollToY(wrap.current.offsetTop + chapterHoldVh(i) * vhPx());

  return (
    <section id="film" className={`film${noGl ? ' no-gl' : ''}`} ref={wrap} style={{ height: `calc(var(--vh) * ${TOTAL + 100})` }}>
      <div className="stage">
        <canvas ref={canvas} className="stage-canvas" aria-hidden="true" />
        {noGl && <div className="stage-fallback" style={{ backgroundImage: `url(${import.meta.env.BASE_URL}seq/city/poster.jpg)` }} />}
        <div className="scrim" />

        {/* intro: the wordmark is typed in silence */}
        <div className="beat b-intro" data-seg={BEATS.intro[0]} data-in={BEATS.intro[1]} data-out={BEATS.intro[2]}>
          <div className="wm"><span ref={typed} /><i className="caret" /></div>
          <p className="phon">{L(INTRO.phon)}</p>
          <div className="cue"><span>{L(UI.scroll)}</span><i /></div>
        </div>

        <div className="beat b-left rv" data-seg={BEATS.prologue[0]} data-in={BEATS.prologue[1]} data-out={BEATS.prologue[2]}>
          <p className="eye">{L(INTRO.prologue.eye)}</p>
          <h2 className="h-xl"><Words lines={L(INTRO.prologue.h)} /></h2>
          <p className="lead">{L(INTRO.prologue.p)}</p>
        </div>

        <div className="beat b-center rv" data-seg={BEATS.voice[0]} data-in={BEATS.voice[1]} data-out={BEATS.voice[2]}>
          <h2 className="h-xxl"><Words lines={L(INTRO.voice)} /></h2>
        </div>

        <div className="beat b-left rv" data-seg={BEATS.day[0]} data-in={BEATS.day[1]} data-out={BEATS.day[2]}>
          <p className="eye">{L(INTRO.day.eye)}</p>
          <h2 className="h-xl"><Words lines={L(INTRO.day.h)} /></h2>
          <p className="lead">{L(INTRO.day.p)}</p>
        </div>

        {CHAPTERS.map((c, i) => (
          <div key={c.id}>
            <div className="beat b-left rv" data-seg={c.id} data-in={CH_TEXT[0]} data-out={CH_TEXT[1]}>
              <p className="eye"><span className="dot" />{c.time} — {String(i + 1).padStart(2, '0')} / {L(c.label)}</p>
              <h2 className="h-xl"><Words lines={L(c.h)} /></h2>
              <p className="lead">{L(c.p)}</p>
            </div>
            <div className="beat b-card" data-seg={c.id} data-in={CH_CARD[0]} data-out={CH_CARD[1]}>
              <MiniSite ch={c} />
              <p className="card-cap">{L(UI.concept)} · {L(c.card.name)}</p>
            </div>
          </div>
        ))}

        <div className="beat b-center rv" data-seg={BEATS.q[0]} data-in={BEATS.q[1]} data-out={BEATS.q[2]}>
          <p className="eye">{L(FINALE.eye)}</p>
          <h2 className="h-xxl"><Words lines={L(FINALE.q)} /></h2>
        </div>
        <div className="beat b-center rv" data-seg={BEATS.next[0]} data-in={BEATS.next[1]} data-out={BEATS.next[2]}>
          <h2 className="h-xxl"><Words lines={L(FINALE.next)} /></h2>
          <p className="lead c">{L(FINALE.p)}</p>
          <div className="btns">
            <a className="btn btn-signal" href="#kontakt" onClick={(e) => { e.preventDefault(); scrollToId('kontakt'); }}>{L(UI.start)}<span>→</span></a>
            <a className="btn btn-ghost" href="#showroom" onClick={(e) => { e.preventDefault(); scrollToId('showroom'); }}>{L(UI.showroom)}</a>
          </div>
        </div>

        <div className="beat b-manifest manifest" data-seg={BEATS.manifest[0]} data-in={BEATS.manifest[1]} data-out={BEATS.manifest[2]}>
          <p className="m-lines">
            {L(MANIFEST.lines).map((ln, i) => (
              <span className="m-line" key={i} data-text={ln}>{ln.replace(/\*/g, '')}</span>
            ))}
          </p>
          <div className="m-cols">
            {MANIFEST.cols.map((c, i) => (
              <div key={i} style={{ '--i': i }}><p className="eye">{L(c.k)}</p><p>{L(c.v)}</p></div>
            ))}
          </div>
        </div>

        {/* HUD: status, clock and the chapter rail */}
        <div className="hud" ref={hud}>
          <div className="hud-tl">
            <span className="hud-status"><i /><b>{L(UI.silent)}</b></span>
            <span className="hud-chip-label" />
            <span className="hud-hint">{L(UI.hint)}</span>
          </div>
          <div className="hud-rail">
            <div className="hud-clock">07:00</div>
            {CHAPTERS.map((c, i) => (
              <button className="rail-ch" key={c.id} onClick={() => goChapter(i)}>
                <span className="rc-t">{c.time}</span><span className="rc-l">{L(c.label)}</span><i />
              </button>
            ))}
          </div>
        </div>
        <div className="hud-bl">
          <span className="hud-pct">00 %</span>
          <span className="hud-bar"><i /></span>
          <a href="#leistungen" onClick={(e) => { e.preventDefault(); scrollToId('leistungen'); }}>{L(UI.skip)} ↓</a>
        </div>
      </div>
    </section>
  );
}

// LITORALE-style decode: dots → scrambled letters → the line, with an echo that collapses
function decode(root) {
  const lines = [...root.querySelectorAll('.m-line')];
  lines.forEach((el, li) => {
    const raw = el.dataset.text;
    const plain = raw.replace(/\*/g, '');
    const emStart = raw.indexOf('*');
    const emEnd = emStart >= 0 ? raw.indexOf('*', emStart + 1) - 1 : -1;
    let step = 0;
    const total = 16;
    setTimeout(() => {
      el.classList.add('go');
      const id = setInterval(() => {
        step++;
        const done = Math.floor((step / total) * plain.length * 1.15);
        let html = '';
        for (let k = 0; k < plain.length; k++) {
          const ch = plain[k];
          let out;
          if (ch === ' ') out = ' ';
          else if (k < done) out = ch;
          else if (step < 4) out = '·';
          else out = SCRAMBLE[(Math.random() * SCRAMBLE.length) | 0];
          const inEm = emStart >= 0 && k >= emStart && k < emEnd;
          html += inEm ? `<em>${out}</em>` : out;
        }
        el.innerHTML = html;
        if (step >= total) { clearInterval(id); el.classList.add('done'); }
      }, 55);
    }, li * 420);
  });
}
