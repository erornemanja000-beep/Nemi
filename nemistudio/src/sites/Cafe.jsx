import { useEffect, useRef, useState } from 'react';
import { useLang } from '../i18n.jsx';
import { scrollToId } from '../scroll.js';
import { CAFE as C } from './copy.js';
import { Rich, Lines, Fade, Parallax, HeroVideo, Marquee, useDemo, DEMO, img, pic } from './kit.jsx';

// Café Mila: warm cream and espresso, Fraunces, a little handmade.

const ids = ['cafe-karte', 'cafe-about', 'cafe-besuch'];
const go = (id) => (e) => { e.preventDefault(); scrollToId(id); };

function Ring({ text }) {
  return (
    <div className="cf-ring" aria-hidden="true">
      <svg viewBox="0 0 200 200">
        <defs><path id="cf-circle" d="M100,100 m-78,0 a78,78 0 1,1 156,0 a78,78 0 1,1 -156,0" /></defs>
        <text><textPath href="#cf-circle" textLength="486" lengthAdjust="spacing">{text}</textPath></text>
      </svg>
      <span className="cf-ring-c">✻</span>
    </div>
  );
}

export function CafeHero() {
  const { L } = useLang();
  return (
    <div className="site cf cf-hero">
      <HeroVideo name="cafe" className="cf-hero-v" eager />
      <div className="cf-hero-shade" />
      <header className="cf-nav">
        <a className="cf-logo" href="#cafe" onClick={go('cafe')}>{C.brand}<small>{L(C.sub)}</small></a>
        <nav>{L(C.nav).map((n, i) => <a key={n} href={`#${ids[i]}`} onClick={go(ids[i])}>{n}</a>)}</nav>
        <a className="cf-btn sm" href="#cafe-besuch" onClick={go('cafe-besuch')}>{L(C.cta)}</a>
      </header>
      <div className="cf-hero-c">
        <p className="cf-open"><i />{L(C.open)}</p>
        <h1 className="cf-h1">{L(C.h).map((l, i) => <span key={i}><Rich text={l} /></span>)}</h1>
        <div className="cf-hero-b">
          <p>{L(C.p)}</p>
          <div className="cf-btns">
            <a className="cf-btn" href="#cafe-karte" onClick={go('cafe-karte')}>{L(C.menuBtn)}</a>
            <a className="cf-btn line" href="#cafe-besuch" onClick={go('cafe-besuch')}>{L(C.cta)}</a>
          </div>
        </div>
      </div>
      <p className="cf-eye">{L(C.eye)}</p>
      <Ring text={L(C.ring)} />
    </div>
  );
}

// a photo of the dish follows the pointer over the menu
function MenuHover({ src }) {
  const ref = useRef();
  useEffect(() => {
    const el = ref.current;
    let x = innerWidth / 2, y = innerHeight / 2, tx = x, ty = y, raf;
    const mv = (e) => { tx = e.clientX; ty = e.clientY; };
    const loop = () => {
      x += (tx - x) * 0.16; y += (ty - y) * 0.16;
      el.style.transform = `translate(${x + 30}px, ${y}px) translateY(-50%) rotate(${(tx - x) * 0.04}deg)`;
      raf = requestAnimationFrame(loop);
    };
    addEventListener('pointermove', mv, { passive: true });
    raf = requestAnimationFrame(loop);
    return () => { removeEventListener('pointermove', mv); cancelAnimationFrame(raf); };
  }, []);
  return <div className={`cf-hover${src ? ' on' : ''}`} ref={ref} aria-hidden="true">{src && <img src={pic(src)} alt="" key={src} />}</div>;
}

function Reviews() {
  const { L } = useLang();
  const [i, setI] = useState(0);
  const n = C.reviews.items.length;
  useEffect(() => { const t = setInterval(() => setI((v) => (v + 1) % n), 5200); return () => clearInterval(t); }, [n]);
  return (
    <section className="site cf cf-rev">
      <p className="cf-k">{L(C.reviews.eye)} · ★★★★★</p>
      <div className="cf-rev-q">
        {C.reviews.items.map((r, k) => (
          <blockquote key={k} className={k === i ? 'on' : ''} aria-hidden={k !== i}>
            <p>„{L(r.q)}“</p>
            <cite>{r.a}</cite>
          </blockquote>
        ))}
      </div>
      <div className="cf-rev-dots">
        {C.reviews.items.map((_, k) => <button key={k} className={k === i ? 'on' : ''} onClick={() => setI(k)} aria-label={`${k + 1}`} />)}
      </div>
    </section>
  );
}

export function CafeBody() {
  const { L, lang } = useLang();
  const [hover, setHover] = useState(null);
  const [done, submit] = useDemo();
  const F = C.visit.form;
  return (
    <div className="site cf">
      <Marquee items={L(C.marquee)} sep="✻" className="cf-mq" speed={46} />

      <section id="cafe-karte" className="cf-menu">
        <div className="cf-menu-head">
          <p className="cf-k">{L(C.menu.eye)}</p>
          <Lines lines={L(C.menu.h)} className="cf-h2" />
          <Fade as="p" className="cf-p">{L(C.menu.p)}</Fade>
        </div>
        <div className="cf-menu-list" onPointerLeave={() => setHover(null)}>
          {C.menu.cats.map((c) => (
            <Fade className="cf-cat" key={L(c.t)}>
              <h3>{L(c.t)}</h3>
              <ul>
                {c.items.map((it) => (
                  <li key={L(it.n)} onPointerEnter={() => setHover(it.img)}>
                    <span className="cf-item">
                      <b>{L(it.n)}</b>
                      {it.d && <small>{L(it.d)}</small>}
                    </span>
                    <i />
                    <span className="cf-price">{lang === 'en' ? it.p.replace(',', '.') : it.p}</span>
                  </li>
                ))}
              </ul>
            </Fade>
          ))}
        </div>
        <MenuHover src={hover} />
      </section>

      <section id="cafe-about" className="cf-about">
        <div className="cf-about-head">
          <p className="cf-k">{L(C.about.eye)}</p>
          <Lines lines={L(C.about.h)} className="cf-h2" />
          <Fade as="p" className="cf-p">{L(C.about.p)}</Fade>
        </div>
        <div className="cf-gal">
          {C.about.pics.map((p, i) => (
            <figure key={p.img} className={`cf-g${i}`}>
              <Parallax src={img(p.img)} amount={10} />
              <figcaption>{L(p.c)}</figcaption>
            </figure>
          ))}
        </div>
        <div className="cf-facts">
          {C.about.facts.map((f) => (
            <Fade key={f.v} className="cf-fact"><b>{f.v}</b><span>{L(f.t)}</span></Fade>
          ))}
        </div>
      </section>

      <Reviews />

      <section id="cafe-besuch" className="cf-visit">
        <div className="cf-visit-head">
          <p className="cf-k">{L(C.visit.eye)}</p>
          <Lines lines={L(C.visit.h)} className="cf-h2" />
        </div>
        <div className="cf-visit-grid">
          <Fade className="cf-hours">
            {C.visit.hours.map((h) => <p key={h.t}><span>{L(h.d)}</span><b>{h.t}</b></p>)}
          </Fade>
          <Fade className="cf-addr" delay={80}>
            <p>{C.visit.addr[0]}<br />{C.visit.addr[1]}</p>
            <small>{L(C.visit.way)}</small>
            <div className="cf-map" aria-hidden="true"><i /><span>Mila</span></div>
          </Fade>
          <Fade as="form" className="cf-res" delay={160} onSubmit={submit}>
            <h3>{L(F.t)}</h3>
            <label><span>{L(F.date)}</span><input type="date" required /></label>
            <label><span>{L(F.time)}</span>
              <select defaultValue="09:00">{['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00'].map((t) => <option key={t}>{t}</option>)}</select>
            </label>
            <label><span>{L(F.ppl)}</span>
              <select defaultValue="2">{[1, 2, 3, 4, 5, 6].map((t) => <option key={t}>{t}</option>)}</select>
            </label>
            <button className="cf-btn" type="submit">{L(F.send)} →</button>
            {done && <p className="k-demo">{L(DEMO)}</p>}
          </Fade>
        </div>
      </section>

      <footer className="cf-foot">
        <div className="cf-foot-mark" aria-hidden="true">{C.brand}</div>
        <p>{L(C.foot)}</p>
      </footer>
    </div>
  );
}
