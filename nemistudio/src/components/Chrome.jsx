import { useEffect, useState } from 'react';
import { useLang } from '../i18n.jsx';
import { NAV, UI } from '../content.js';
import { scrollToId, stop, resume } from '../scroll.js';
import { loadedCount, onProgress } from '../film/frames.js';
import { SEQ } from '../film/timeline.js';

export function Logo({ small }) {
  return (
    <span className={`logo${small ? ' sm' : ''}`} aria-label="Nemi Studio">
      <span className="logo-w">nem<span className="logo-i">ı<i /></span></span>
      <span className="logo-s">studio</span>
    </span>
  );
}

export function Nav() {
  const { L, lang, setLang } = useLang();
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const on = () => setScrolled(scrollY > 40);
    addEventListener('scroll', on, { passive: true });
    return () => removeEventListener('scroll', on);
  }, []);
  useEffect(() => { (open ? stop : resume)(); }, [open]);
  const go = (id) => (e) => { e.preventDefault(); setOpen(false); setTimeout(() => scrollToId(id), open ? 300 : 0); };
  return (
    <>
      <header className={`nav${scrolled ? ' scrolled' : ''}${open ? ' open' : ''}`}>
        <a href="#film" onClick={go('film')} className="nav-logo"><Logo /></a>
        <nav className="nav-links">
          {NAV.map((n, i) => (
            <a key={n.id} href={`#${n.id}`} onClick={go(n.id)}><sup>{String(i + 1).padStart(2, '0')}</sup>{L(n)}</a>
          ))}
        </nav>
        <div className="nav-right">
          <div className="lang" role="group" aria-label="Sprache / Language">
            <button className={lang === 'de' ? 'act' : ''} onClick={() => setLang('de')}>DE</button>
            <button className={lang === 'en' ? 'act' : ''} onClick={() => setLang('en')}>EN</button>
          </div>
          <a className="btn btn-line nav-cta" href="#kontakt" onClick={go('kontakt')}>{L(UI.start)}</a>
          <button className="nav-burger" aria-expanded={open} onClick={() => setOpen(!open)} aria-label={L(open ? UI.close : UI.menu)}>
            <i /><i />
          </button>
        </div>
      </header>
      <div className={`menu${open ? ' open' : ''}`} aria-hidden={!open}>
        <nav>
          {NAV.map((n, i) => (
            <a key={n.id} href={`#${n.id}`} onClick={go(n.id)} style={{ '--i': i }}><sup>{String(i + 1).padStart(2, '0')}</sup>{L(n)}</a>
          ))}
        </nav>
        <a className="btn btn-signal" href="#kontakt" onClick={go('kontakt')}>{L(UI.start)}<span>→</span></a>
      </div>
    </>
  );
}

// the glass pill at the bottom, always one click from the contact form
export function Pill() {
  const { L } = useLang();
  const [hide, setHide] = useState(false);
  useEffect(() => {
    const el = document.getElementById('kontakt');
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setHide(e.isIntersecting), { rootMargin: '0px 0px -30% 0px' });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <div className={`pill${hide ? ' hide' : ''}`}>
      <span className="pill-dot" />
      <span className="pill-t">{L(UI.call)}</span>
      <a className="btn btn-signal sm" href="#kontakt" onClick={(e) => { e.preventDefault(); scrollToId('kontakt'); }}>{L(UI.start)}</a>
    </div>
  );
}

// counts the first sequences in, then lifts like a curtain
export function Preloader({ onDone }) {
  const { L } = useLang();
  const [pct, setPct] = useState(0);
  const [gone, setGone] = useState(false);
  useEffect(() => {
    const need = SEQ.curtain + 12;
    let fonts = false;
    let shown = 0;
    document.fonts.ready.then(() => { fonts = true; });
    const t0 = performance.now();
    const id = setInterval(() => {
      const have = loadedCount('curtain') + Math.min(12, loadedCount('city'));
      const real = Math.min(1, have / need) * (fonts ? 1 : 0.95);
      // never faster than ~1.4 s, so the counter reads as a count
      const cap = Math.min(1, (performance.now() - t0) / 1400);
      shown += (Math.min(real, cap) - shown) * 0.25;
      if (real >= 1 && cap >= 1 && shown > 0.985) shown = 1;
      setPct(shown);
      if (shown >= 1) {
        clearInterval(id);
        setTimeout(() => { setGone(true); onDone(); }, 250);
      }
    }, 50);
    const off = onProgress(() => {});
    return () => { clearInterval(id); off(); };
  }, []);
  return (
    <div className={`pre${gone ? ' gone' : ''}`} aria-hidden={gone}>
      <div className="pre-num">{String(Math.round(pct * 100)).padStart(3, '0')}</div>
      <div className="pre-bar"><i style={{ transform: `scaleX(${pct})` }} /></div>
      <div className="pre-l">{L(UI.loading)}</div>
    </div>
  );
}
