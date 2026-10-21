import { useState } from 'react';
import { useLang } from '../i18n.jsx';
import { scrollToId } from '../scroll.js';
import { GYM as C } from './copy.js';
import { Fade, Parallax, HeroVideo, Marquee, img } from './kit.jsx';

// Puls Studio: black, acid lime and Anton. Loud, fast, no decoration that does not move.

const ids = ['gym-plan', 'gym-coaches', 'gym-prices'];
const go = (id) => (e) => { e.preventDefault(); scrollToId(id); };

// a believable week: the same rhythm every day, shifted a little
const TIMES = ['06:30', '09:00', '12:15', '17:30', '18:45', '20:00'];
const COACH = ['Mira', 'Luka', 'Jonas'];
function day(d) {
  return TIMES.slice(d === 5 ? 1 : 0, d === 5 ? 5 : 6).map((t, i) => {
    const c = (i + d * 2) % C.classes.length;
    const spots = (i * 7 + d * 5) % 13;
    return { t, n: C.classes[c], coach: COACH[(i + d) % 3], lvl: 1 + ((c + d) % 3), spots };
  });
}

export function GymHero() {
  const { L } = useLang();
  return (
    <div className="site gy gy-hero">
      <HeroVideo name="gym" className="gy-hero-v" />
      <div className="gy-hero-shade" />
      <header className="gy-nav">
        <a className="gy-logo" href="#gym" onClick={go('gym')}>{C.brand}<i /><small>{L(C.sub)}</small></a>
        <nav>{L(C.nav).map((n, i) => <a key={n} href={`#${ids[i]}`} onClick={go(ids[i])}>{n}</a>)}</nav>
        <a className="gy-btn sm" href="#gym-prices" onClick={go('gym-prices')}>{L(C.cta)}</a>
      </header>
      <p className="gy-live"><i />LIVE · {L(C.live)}</p>
      <h1 className="gy-h1">{L(C.h).map((l, i) => <span key={i}>{l}</span>)}</h1>
      <div className="gy-hero-b">
        <p>{L(C.p)}</p>
        <div className="gy-btns">
          <a className="gy-btn" href="#gym-prices" onClick={go('gym-prices')}>{L(C.btn)} →</a>
          <a className="gy-btn ghost" href="#gym-plan" onClick={go('gym-plan')}>{L(C.btn2)}</a>
        </div>
      </div>
      <p className="gy-side">EST. 2019 — LINZ — 24/7</p>
    </div>
  );
}

export function GymBody() {
  const { L } = useLang();
  const [d, setD] = useState(0);
  const P = C.plan;
  return (
    <div className="site gy">
      <div className="gy-bands" aria-hidden="true">
        <Marquee items={L(C.marquee)} sep="✱" className="gy-mq a" speed={22} />
        <Marquee items={L(C.marquee)} sep="✱" className="gy-mq b" speed={28} />
      </div>

      <section id="gym-plan" className="gy-plan">
        <div className="gy-plan-head">
          <h2 className="gy-h2">{L(P.h)}</h2>
          <div className="gy-days" role="tablist">
            {L(P.days).map((x, i) => (
              <button key={x} role="tab" aria-selected={d === i} className={d === i ? 'on' : ''} onClick={() => setD(i)}>{x}</button>
            ))}
          </div>
        </div>
        <ul className="gy-rows" key={d}>
          {day(d).map((r, i) => (
            <li key={r.t} style={{ '--i': i }}>
              <span className="gy-t">{r.t}</span>
              <b className="gy-n">{r.n}</b>
              <span className="gy-c">{r.coach}</span>
              <span className="gy-lvl" aria-label={`Level ${r.lvl}`}>{[1, 2, 3].map((k) => <i key={k} className={k <= r.lvl ? 'on' : ''} />)}</span>
              <span className={`gy-s${r.spots ? '' : ' full'}`}>{r.spots ? `${r.spots} ${L(P.spots)}` : L(P.full)}</span>
              <button className="gy-book" type="button">{L(P.book)}</button>
            </li>
          ))}
        </ul>
      </section>

      <section id="gym-coaches" className="gy-coaches">
        <h2 className="gy-h2">{L(C.coaches.h)}</h2>
        <div className="gy-cards">
          {C.coaches.items.map((c, i) => (
            <Fade as="figure" key={c.n} className="gy-card" delay={i * 100}>
              <img src={img(c.img)} alt={c.n} loading="lazy" />
              <figcaption>
                <b>{c.n}</b>
                <span>{L(c.r)}</span>
                <q>{L(c.q)}</q>
              </figcaption>
            </Fade>
          ))}
        </div>
      </section>

      <section className="gy-nums">
        {C.nums.map((n, i) => (
          <Fade key={n.v} className="gy-num" delay={i * 80}><b>{n.v}</b><span>{L(n.t)}</span></Fade>
        ))}
      </section>

      <section id="gym-prices" className="gy-prices">
        <h2 className="gy-h2">{L(C.prices.h)}</h2>
        <div className="gy-tiers">
          {C.prices.tiers.map((t, i) => (
            <Fade key={t.n} className={`gy-tier${t.hot ? ' hot' : ''}`} delay={i * 100}>
              {t.hot && <span className="gy-pop">{L(C.prices.pop)}</span>}
              <h3>{t.n}</h3>
              <p className="gy-price"><b>{t.v}</b><span>€ {L(C.prices.per)}</span></p>
              <ul>{L(t.f).map((f) => <li key={f}>{f}</li>)}</ul>
              <button className={`gy-btn${t.hot ? ' dark' : ' ghost'}`} type="button">{L(C.prices.pick)}</button>
            </Fade>
          ))}
        </div>
        <p className="gy-note">{L(C.prices.note)}</p>
      </section>

      <section className="gy-end">
        <Parallax src={img('gym-dumbbell')} amount={12} className="gy-end-bg" />
        <h2 className="gy-end-h">{L(C.end).map((l) => <span key={l}>{l}</span>)}</h2>
        <a className="gy-btn" href="#gym-prices" onClick={go('gym-prices')}>{L(C.endBtn)} →</a>
      </section>

      <footer className="gy-foot">
        <span className="gy-logo">{C.brand}<i /></span>
        <p>{L(C.foot)}</p>
      </footer>
    </div>
  );
}
