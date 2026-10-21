import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { useLang } from '../i18n.jsx';
import { scrollToId, reduced } from '../scroll.js';
import { HOTEL as C } from './copy.js';
import { Rich, Lines, Fade, Parallax, HeroVideo, useDemo, DEMO, img, pic } from './kit.jsx';

// Hotel Alba: linen, sage and Bodoni. Slow, airy, arches.

const ids = ['hotel-rooms', 'hotel-spa', 'hotel-dine', 'hotel-where'];
const go = (id) => (e) => { e.preventDefault(); scrollToId(id); };

function BookBar({ className = '' }) {
  const { L } = useLang();
  const [done, submit] = useDemo();
  const B = C.book;
  return (
    <form className={`ht-book ${className}`} onSubmit={submit}>
      <label><span>{L(B.in)}</span><b>{L(B.inV)}</b></label>
      <label><span>{L(B.out)}</span><b>{L(B.outV)}</b></label>
      <label><span>{L(B.guests)}</span><b>{L(B.gV)}</b></label>
      <button className="ht-btn" type="submit">{L(B.go)}</button>
      {done && <p className="k-demo">{L(DEMO)}</p>}
    </form>
  );
}

export function HotelHero() {
  const { L } = useLang();
  return (
    <div className="site ht ht-hero">
      <HeroVideo name="hotel" className="ht-hero-v" />
      <div className="ht-hero-shade" />
      <header className="ht-nav">
        <nav className="l">{L(C.nav).slice(0, 2).map((n, i) => <a key={n} href={`#${ids[i]}`} onClick={go(ids[i])}>{n}</a>)}</nav>
        <a className="ht-logo" href="#hotel" onClick={go('hotel')}>{C.brand}<small>{L(C.sub)}</small></a>
        <nav className="r">
          {L(C.nav).slice(2).map((n, i) => <a key={n} href={`#${ids[i + 2]}`} onClick={go(ids[i + 2])}>{n}</a>)}
          <a className="ht-btn sm" href="#hotel-book" onClick={go('hotel-book')}>{L(C.cta)}</a>
        </nav>
      </header>
      <div className="ht-hero-c">
        <p className="ht-eye">{L(C.eye)}</p>
        <h1 className="ht-h1">{L(C.h).map((l, i) => <span key={i}><Rich text={l} /></span>)}</h1>
      </div>
      <BookBar className="ht-hero-book" />
    </div>
  );
}

// the spa picture opens from a small circle to the full frame
function SpaReveal() {
  const box = useRef();
  const im = useRef();
  useEffect(() => {
    if (reduced) { im.current.style.clipPath = 'none'; return; }
    const tw = gsap.fromTo(im.current, { clipPath: 'circle(14% at 50% 50%)' }, {
      clipPath: 'circle(75% at 50% 50%)', ease: 'none',
      scrollTrigger: { trigger: box.current, start: 'top 75%', end: 'center 40%', scrub: true },
    });
    return () => { tw.scrollTrigger && tw.scrollTrigger.kill(); tw.kill(); };
  }, []);
  return (
    <div className="ht-spa-pic" ref={box}>
      <div className="ht-spa-im" ref={im}><img src={img('hotel-spa')} alt="" loading="lazy" /></div>
    </div>
  );
}

export function HotelBody() {
  const { L } = useLang();
  const R = C.rooms;
  return (
    <div className="site ht">
      <section className="ht-intro">
        <div className="ht-arch"><Parallax src={img('hotel-milky')} amount={10} /></div>
        <div>
          <Lines lines={L(C.intro.h)} className="ht-h2" />
          <Fade as="p" className="ht-p">{L(C.intro.p)}</Fade>
        </div>
      </section>

      <section id="hotel-rooms" className="ht-rooms">
        <div className="ht-rooms-head">
          <p className="ht-k">{L(R.eye)}</p>
          <Lines lines={L(R.h)} className="ht-h2" />
        </div>
        <div className="ht-rail">
          {R.items.map((r, i) => (
            <Fade as="article" key={r.v} className="ht-room" delay={i * 90}>
              <div className="ht-room-pic"><img src={pic(r.img)} alt={L(r.n)} loading="lazy" /></div>
              <h3>{L(r.n)}</h3>
              <p>{L(r.d)}</p>
              <p className="ht-from">{L(R.from)} <b>{r.v} €</b> {L(R.night)}</p>
            </Fade>
          ))}
        </div>
      </section>

      <section id="hotel-spa" className="ht-spa">
        <SpaReveal />
        <div className="ht-spa-t">
          <p className="ht-k">{L(C.spa.eye)}</p>
          <Lines lines={L(C.spa.h)} className="ht-h2" />
          <Fade as="p" className="ht-p">{L(C.spa.p)}</Fade>
        </div>
      </section>

      <section id="hotel-dine" className="ht-dine">
        <div className="ht-dine-t">
          <p className="ht-k">{L(C.dine.eye)}</p>
          <Lines lines={L(C.dine.h)} className="ht-h2" />
          <Fade as="p" className="ht-p">{L(C.dine.p)}</Fade>
          <Fade as="ul" className="ht-list">{L(C.dine.list).map((x) => <li key={x}>{x}</li>)}</Fade>
        </div>
        <Parallax src={img('hotel-pool')} amount={12} className="ht-dine-pic" />
      </section>

      <section id="hotel-where" className="ht-where">
        <p className="ht-k">{L(C.where.eye)}</p>
        <div className="ht-where-g">
          {C.where.items.map((w, i) => (
            <Fade key={i} className="ht-w" delay={i * 100}>
              <b>{w.v}<small>{L(w.u)}</small></b>
              <span>{L(w.t)}</span>
            </Fade>
          ))}
        </div>
      </section>

      <section id="hotel-book" className="ht-end">
        <Lines lines={L(C.end.h)} className="ht-h2 c" />
        <Fade as="p" className="ht-p c">{L(C.end.p)}</Fade>
        <BookBar className="ht-end-book" />
      </section>

      <footer className="ht-foot">
        <div className="ht-foot-mark" aria-hidden="true">{C.brand}</div>
        <p>{L(C.foot)}</p>
      </footer>
    </div>
  );
}
