import { useEffect, useRef, useState } from 'react';
import { useLang } from '../i18n.jsx';
import { NAV, UI, BAR } from '../content.js';
import { WORLDS } from '../worlds.js';
import { scrollToId, scrollToY, stop, resume, reduced } from '../scroll.js';

export function Logo({ small }) {
  return (
    <span className={`logo${small ? ' sm' : ''}`} aria-label="Nemi Studio">
      <span className="logo-w">nem<span className="logo-i">ı<i /></span></span>
      <span className="logo-s">studio</span>
    </span>
  );
}

// jump to the moment a site's screen fills the viewport (the end of its dive)
export function goSite(id) {
  const el = document.getElementById(id);
  if (!el) return;
  // straight to the moment the screen fills the window (the end of the dive)
  const top = el.getBoundingClientRect().top + scrollY;
  scrollToY(top + el.firstElementChild.offsetHeight * 1.6 + 2);
}

// ---------------------------------------------------------------- video intro
const KEY = 'nemi-intro-v4';
// any button can ask the app to play the film again
export const replayIntro = () => dispatchEvent(new Event('nemi:intro'));
export function ReplayButton({ className = '' }) {
  const { L } = useLang();
  return (
    <button className={`replay ${className}`} onClick={replayIntro}>
      <span className="replay-i" aria-hidden="true">▶</span>{L(UI.replay)}
    </button>
  );
}
export function shouldPlayIntro() {
  const q = new URLSearchParams(location.search).get('intro');
  if (q === '1') return true;
  if (q === '0' || reduced) return false;
  try { return !sessionStorage.getItem(KEY); } catch (e) { return true; }
}

export function VideoIntro({ onDone }) {
  const { L, lang } = useLang();
  const ref = useRef();
  const [muted, setMuted] = useState(true);
  const [blocked, setBlocked] = useState(false);
  const [pct, setPct] = useState(0);
  const [out, setOut] = useState(false);
  const [portrait] = useState(() => innerWidth / innerHeight < 0.9);
  const base = import.meta.env.BASE_URL;
  const src = `${base}v/intro-${portrait ? '9x16' : '16x9'}${lang === 'en' ? '-en' : ''}.mp4?v=4`;
  const done = useRef(false);
  const finish = () => {
    if (done.current) return;
    done.current = true;
    setOut(true);
    const v = ref.current;
    // fade the music out with the picture
    if (v && !v.muted) { const t0 = performance.now(); const f = () => { const k = 1 - (performance.now() - t0) / 900; v.volume = Math.max(0, k); if (k > 0) requestAnimationFrame(f); }; f(); }
    setTimeout(onDone, 950);
  };
  useEffect(() => {
    try { sessionStorage.setItem(KEY, '1'); } catch (e) { /* storage blocked */ }
    const v = ref.current;
    const p = v.play();
    if (p) p.catch(() => setBlocked(true));
    const key = (e) => { if (e.key === 'Escape' || e.key === 'Enter') finish(); };
    addEventListener('keydown', key);
    return () => removeEventListener('keydown', key);
  }, []);
  const toggle = () => { const v = ref.current; v.muted = !v.muted; setMuted(v.muted); if (v.paused) v.play(); };
  const play = () => { const v = ref.current; v.play().then(() => setBlocked(false)).catch(() => finish()); };
  return (
    <div className={`vi${out ? ' out' : ''}`} role="dialog" aria-label="Intro">
      <video
        ref={ref} src={src} poster={`${base}v/intro.jpg?v=4`} muted playsInline preload="auto"
        onTimeUpdate={(e) => setPct(e.target.currentTime / (e.target.duration || 25))}
        onEnded={finish} onError={finish}
      />
      {blocked && (
        <button className="vi-play" onClick={play}><span>▶</span>{L(UI.play)}</button>
      )}
      <div className="vi-ui">
        <button className="vi-b" onClick={toggle} aria-pressed={!muted}>
          <span className={`vi-eq${muted ? '' : ' on'}`} aria-hidden="true"><i /><i /><i /><i /></span>
          {L(muted ? UI.sound : UI.mute)}
        </button>
        <div className="vi-bar"><i style={{ transform: `scaleX(${pct})` }} /></div>
        <button className="vi-b" onClick={finish}>{L(UI.skip)} →</button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------- the Nemi bar
// One quiet pill at the bottom that says where you are (which concept), with the index,
// the language switch and the way to the contact form.
export function NemiBar({ show }) {
  const { L, lang, setLang } = useLang();
  const [cur, setCur] = useState(0);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const els = [...document.querySelectorAll('[data-site]')];
    const io = new IntersectionObserver((es) => {
      es.forEach((e) => { if (e.isIntersecting) setCur(+e.target.dataset.site); });
    }, { rootMargin: '-50% 0px -50% 0px' });
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);
  useEffect(() => { (open ? stop : resume)(); }, [open]);
  useEffect(() => {
    if (!open) return;
    const k = (e) => { if (e.key === 'Escape') setOpen(false); };
    addEventListener('keydown', k);
    return () => removeEventListener('keydown', k);
  }, [open]);
  const site = WORLDS[cur - 1];
  const jump = (fn) => (e) => { e.preventDefault(); setOpen(false); setTimeout(fn, 320); };
  return (
    <>
      <div className={`bar${show ? ' in' : ''}${open ? ' open' : ''}`}>
        <a className="bar-logo" href="#top" onClick={jump(() => scrollToY(0))} aria-label="Nemi Studio"><Logo small /></a>
        <button className="bar-where" onClick={() => setOpen(!open)} aria-expanded={open}>
          {site ? (
            <>
              <span className="bar-n">0{cur}<small>/04</small></span>
              <span className="bar-t" key={site.id}>{L(site.name).split(' & ')[0]}<em>{L(site.sense)}</em></span>
            </>
          ) : (
            <span className="bar-t" key="nemi">{L(BAR.start)}<em>{L(BAR.index)}</em></span>
          )}
          <span className="bar-burger" aria-hidden="true"><i /><i /></span>
        </button>
        <div className="bar-lang" role="group" aria-label="Sprache / Language">
          <button className={lang === 'de' ? 'act' : ''} onClick={() => setLang('de')}>DE</button>
          <button className={lang === 'en' ? 'act' : ''} onClick={() => setLang('en')}>EN</button>
        </div>
        <a className="btn btn-signal sm bar-cta" href="#kontakt" onClick={jump(() => scrollToId('kontakt'))}>
          <span className="bar-cta-t">{L(UI.start)}</span><span>→</span>
        </a>
      </div>
      <div className={`idx${open ? ' open' : ''}`} aria-hidden={!open} onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}>
        <div className="idx-in">
          <p className="eye">{L(BAR.index)}</p>
          <ol className="idx-sites">
            {WORLDS.map((s, i) => (
              <li key={s.id} style={{ '--i': i }}>
                <a href={`#${s.id}`} onClick={jump(() => goSite(s.id))} className={cur === i + 1 ? 'act' : ''}>
                  <span>0{i + 1}</span><b>{L(s.sense)}</b><em>{L(s.name)}</em>
                </a>
              </li>
            ))}
          </ol>
          <nav className="idx-nemi">
            {NAV.map((n, i) => (
              <a key={n.id} href={`#${n.id}`} onClick={jump(() => scrollToId(n.id))} style={{ '--i': i + 4 }}>{L(n)}</a>
            ))}
            <a href="#top" className="idx-replay" onClick={jump(replayIntro)} style={{ '--i': NAV.length + 4 }}><span aria-hidden="true">▶ </span>{L(UI.replay)}</a>
          </nav>
          <div className="idx-lang">
            <button className={lang === 'de' ? 'act' : ''} onClick={() => setLang('de')}>Deutsch</button>
            <button className={lang === 'en' ? 'act' : ''} onClick={() => setLang('en')}>English</button>
          </div>
        </div>
      </div>
    </>
  );
}
