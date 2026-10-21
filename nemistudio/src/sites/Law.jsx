import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { useLang } from '../i18n.jsx';
import { scrollToId, reduced } from '../scroll.js';
import { LAW as C } from './copy.js';
import { Rich, Lines, Fade, Parallax, HeroVideo, Count, useDemo, DEMO, img } from './kit.jsx';

// Kanzlei Aurum: navy, ivory and a thin gold line. Cormorant Garamond, quiet and exact.

const ids = ['law-areas', 'law-team', 'law-steps', 'law-contact'];
const go = (id) => (e) => { e.preventDefault(); scrollToId(id); };
const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI'];

export function LawHero() {
  const { L } = useLang();
  return (
    <div className="site lw lw-hero">
      <HeroVideo name="law" className="lw-hero-v" />
      <div className="lw-hero-shade" />
      <header className="lw-nav">
        <a className="lw-logo" href="#law" onClick={go('law')}>
          <span className="lw-mark" aria-hidden="true">A</span>
          <span>{C.brand}<small>{L(C.sub)}</small></span>
        </a>
        <nav>{L(C.nav).map((n, i) => <a key={n} href={`#${ids[i]}`} onClick={go(ids[i])}>{n}</a>)}</nav>
        <a className="lw-btn line sm" href="#law-contact" onClick={go('law-contact')}>{L(C.cta)}</a>
      </header>
      <div className="lw-hero-c">
        <p className="lw-eye"><i />{L(C.eye)}</p>
        <h1 className="lw-h1">{L(C.h).map((l, i) => <span key={i}><Rich text={l} /></span>)}</h1>
        <p className="lw-p">{L(C.p)}</p>
        <div className="lw-btns">
          <a className="lw-btn" href="#law-contact" onClick={go('law-contact')}>{L(C.btn)}</a>
          <a className="lw-link" href="#law-areas" onClick={go('law-areas')}>{L(C.btn2)} ↓</a>
        </div>
      </div>
      <div className="lw-stats">
        {C.stats.map((s) => (
          <div key={s.v}><b><Count to={s.v} suffix={s.s} /></b><span>{L(s.t)}</span></div>
        ))}
      </div>
    </div>
  );
}

// the statement brightens word by word as it scrolls through the screen
function Statement() {
  const { L } = useLang();
  const ref = useRef();
  const text = L(C.statement.h);
  useEffect(() => {
    if (reduced) return;
    const words = ref.current.querySelectorAll('.lw-sw');
    const tw = gsap.fromTo(words, { opacity: 0.14 }, {
      opacity: 1, stagger: 0.1, ease: 'none',
      scrollTrigger: { trigger: ref.current, start: 'top 80%', end: 'bottom 45%', scrub: true },
    });
    return () => { tw.scrollTrigger && tw.scrollTrigger.kill(); tw.kill(); };
  }, [text]);
  let k = 0;
  return (
    <section className="lw-state">
      <h2 ref={ref} className="lw-state-h">
        {text.split(/(\*[^*]+\*)/).filter(Boolean).map((part, pi) => {
          const em = part.startsWith('*');
          return (em ? part.slice(1, -1) : part).split(/\s+/).filter(Boolean).map((w) => {
            k++;
            return <span key={`${pi}-${k}`} className="lw-sw">{em ? <em>{w}</em> : w} </span>;
          });
        })}
      </h2>
      <Fade as="p" className="lw-state-p">{L(C.statement.p)}</Fade>
    </section>
  );
}

export function LawBody() {
  const { L } = useLang();
  const [open, setOpen] = useState(0);
  const [done, submit] = useDemo();
  const K = C.contact;
  return (
    <div className="site lw">
      <Statement />

      <section id="law-areas" className="lw-areas">
        <div className="lw-areas-pic">
          <Parallax src={img('law-sign')} amount={14} />
          <span className="lw-frame" aria-hidden="true" />
        </div>
        <div className="lw-areas-list">
          <p className="lw-eye"><i />{L(C.areas.eye)}</p>
          {C.areas.items.map((a, i) => (
            <div className={`lw-area${open === i ? ' open' : ''}`} key={i}>
              <button onClick={() => setOpen(open === i ? -1 : i)} aria-expanded={open === i}>
                <span className="lw-rn">{ROMAN[i]}.</span>
                <span className="lw-at">{L(a.t)}</span>
                <span className="lw-plus" aria-hidden="true" />
              </button>
              <div className="lw-ad"><p>{L(a.d)}</p></div>
            </div>
          ))}
        </div>
      </section>

      <section id="law-team" className="lw-team">
        <div className="lw-team-head">
          <p className="lw-eye dark"><i />{L(C.team.eye)}</p>
          <Lines lines={L(C.team.h)} className="lw-h2" />
        </div>
        <div className="lw-people">
          {C.team.people.map((p, i) => (
            <Fade as="figure" key={p.n} className="lw-person" delay={i * 90}>
              <div className="lw-ph"><img src={img(p.img)} alt={p.n} loading="lazy" /></div>
              <figcaption>
                <b>{p.n}</b>
                <span>{L(p.r)}</span>
                <small>{p.l}</small>
              </figcaption>
            </Fade>
          ))}
        </div>
      </section>

      <section className="lw-quote">
        <Parallax src={img('law-pen')} amount={10} className="lw-quote-bg" />
        <Fade as="blockquote"><Rich text={L(C.quote)} /></Fade>
      </section>

      <section id="law-steps" className="lw-steps">
        {C.steps.map((s, i) => (
          <Fade key={i} className="lw-step" delay={i * 120}>
            <span className="lw-sn">0{i + 1}</span>
            <h3>{L(s.t)}</h3>
            <p>{L(s.d)}</p>
          </Fade>
        ))}
      </section>

      <section id="law-contact" className="lw-contact">
        <div>
          <p className="lw-eye"><i />{L(K.eye)}</p>
          <Lines lines={L(K.h)} className="lw-h2" />
          <div className="lw-addr">
            <p>Schottenring 14<br />1010 Wien</p>
            <p>office@kanzlei-aurum.at</p>
            <p>{L(K.hours)}</p>
          </div>
        </div>
        <Fade as="form" className="lw-form" onSubmit={submit}>
          <label><span>{L(K.name)}</span><input required /></label>
          <label><span>{L(K.reach)}</span><input required /></label>
          <label><span>{L(K.area)}</span>
            <select defaultValue="">{[<option key="x" value="" disabled>—</option>, ...C.areas.items.map((a) => <option key={L(a.t)}>{L(a.t)}</option>)]}</select>
          </label>
          <label><span>{L(K.msg)}</span><textarea rows={3} /></label>
          <button className="lw-btn" type="submit">{L(K.send)}</button>
          {done && <p className="k-demo">{L(DEMO)}</p>}
        </Fade>
      </section>

      <footer className="lw-foot">
        <span className="lw-mark" aria-hidden="true">A</span>
        <p>{L(C.foot)}</p>
      </footer>
    </div>
  );
}
