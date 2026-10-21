import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { useLang } from '../i18n.jsx';
import { SplitReveal, Magnetic, Arrow } from './fx.jsx';
import { scrollToHash, reducedMotion } from '../hooks/useSmoothScroll.js';

function useStudioTime() {
  const [time, setTime] = useState('');
  useEffect(() => {
    const f = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Vienna', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
    const tick = () => setTime(f.format(new Date()));
    tick();
    const id = setInterval(tick, 20000);
    return () => clearInterval(id);
  }, []);
  return time;
}

export default function Hero({ ready }) {
  const { t } = useLang();
  const root = useRef(null);
  const time = useStudioTime();
  const lines = t.hero.lines.map((l, i) => (i === t.hero.lines.length - 1 ? <span className="serif accent">{l}</span> : l));

  useEffect(() => {
    if (!ready) return undefined;
    const el = root.current;
    const items = el.querySelectorAll('.hero-in');
    if (reducedMotion()) { gsap.set(items, { opacity: 1, y: 0 }); return undefined; }
    const tw = gsap.fromTo(items, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 1.1, ease: 'expo.out', stagger: 0.08, delay: 0.55 });
    // tekst se blago povlači i bledi dok kamera ulazi u jezgro
    const out = gsap.to(el.querySelector('.hero-inner'), {
      yPercent: -18, opacity: 0, ease: 'none',
      scrollTrigger: { trigger: el, start: 'top top', end: 'bottom 35%', scrub: true },
    });
    return () => { tw.kill(); out.scrollTrigger?.kill(); out.kill(); };
  }, [ready]);

  return (
    <section className="hero" id="top" ref={root}>
      <span className="corner c-tl" aria-hidden="true">+</span>
      <span className="corner c-tr" aria-hidden="true">+</span>
      <span className="corner c-bl" aria-hidden="true">+</span>
      <span className="corner c-br" aria-hidden="true">+</span>
      <div className="hero-inner wrap">
        <div className="hero-top">
          <p className="label hero-in">{t.hero.label}</p>
          <p className="label hero-in hero-status"><span className="dot" />{t.hero.status}<span className="hero-time">CET {time}</span></p>
        </div>
        <div className="hero-main">
          <SplitReveal as="h1" className="hero-title" lines={lines} onLoad play={ready} delay={0.15} />
          <div className="hero-side">
            <p className="lead hero-in">{t.hero.sub}</p>
            <div className="hero-ctas hero-in">
              <Magnetic>
                <a className="btn btn-accent" href="#contact" onClick={(e) => { e.preventDefault(); scrollToHash('#contact'); }}>{t.hero.cta}<Arrow /></a>
              </Magnetic>
              <Magnetic>
                <a className="btn btn-ghost" href="#work" onClick={(e) => { e.preventDefault(); scrollToHash('#work'); }}>{t.hero.cta2}</a>
              </Magnetic>
            </div>
          </div>
        </div>
      </div>
      <p className="hero-scroll label hero-in" aria-hidden="true"><span className="hero-scroll-line" />{t.hero.scroll}</p>
    </section>
  );
}
