import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { useLang } from '../i18n.jsx';
import { ScrollWords } from './fx.jsx';
import { reducedMotion } from '../hooks/useSmoothScroll.js';

const WORDS = [0.66, 0.95];

// Dok se ovaj presek skroluje, kamera ulazi u jezgro i leti kroz tunel; tekst se pali posle bljeska
export default function Manifesto() {
  const { t } = useLang();
  const root = useRef(null);
  useEffect(() => {
    const el = root.current;
    const inner = el.querySelector('.mani-inner');
    if (reducedMotion()) { gsap.set(inner, { opacity: 1 }); return undefined; }
    const tw = gsap.fromTo(inner, { opacity: 0, scale: 0.96 }, {
      opacity: 1, scale: 1, ease: 'none',
      scrollTrigger: { trigger: el, start: () => `top+=${el.offsetHeight * 0.6} bottom`, end: () => `top+=${el.offsetHeight * 0.68} bottom`, scrub: true },
    });
    return () => { tw.scrollTrigger?.kill(); tw.kill(); };
  }, []);
  return (
    <section className="manifesto" id="manifesto" ref={root}>
      <div className="mani-sticky">
        <div className="wrap mani-inner">
          <p className="label"><b>●</b> {t.manifesto.label}</p>
          <ScrollWords key={t.manifesto.text} text={t.manifesto.text} highlight={t.manifesto.hi} className="mani-text" trigger="#manifesto" range={WORDS} />
        </div>
      </div>
    </section>
  );
}
