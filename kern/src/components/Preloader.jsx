import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { useLang } from '../i18n.jsx';
import { reducedMotion } from '../hooks/useSmoothScroll.js';

// Uvod: brojač 000 → 100 dok se učitavaju fontovi i scena, pa zavesa ide gore
export default function Preloader({ onDone }) {
  const { t } = useLang();
  const root = useRef(null);
  const num = useRef(null);
  const bar = useRef(null);

  useEffect(() => {
    const el = root.current;
    const o = { v: 0 };
    let ready = false;
    let finished = false;
    const loaded = new Promise((res) => (document.readyState === 'complete' ? res() : window.addEventListener('load', res, { once: true })));
    Promise.all([document.fonts?.ready, loaded, new Promise((r) => setTimeout(r, 400))]).then(() => { ready = true; });
    const set = () => {
      const v = Math.round(o.v);
      num.current.textContent = String(v).padStart(3, '0');
      bar.current.style.transform = `scaleX(${o.v / 100})`;
    };
    const finish = () => {
      if (finished) return;
      finished = true;
      const tl = gsap.timeline({ onComplete: () => { el.style.display = 'none'; } });
      tl.to(el.querySelectorAll('.pl-fade'), { opacity: 0, y: -14, duration: 0.45, ease: 'power2.in', stagger: 0.04 })
        .to(el.querySelector('.pl-mark'), { scale: 0.6, opacity: 0, duration: 0.5, ease: 'power3.in' }, '<')
        .add(() => onDone?.(), '-=0.1')
        .to(el, { clipPath: 'inset(0 0 100% 0)', duration: 1.05, ease: 'expo.inOut' }, '-=0.15');
    };
    if (reducedMotion()) {
      o.v = 100; set();
      const id = setTimeout(finish, 300);
      return () => clearTimeout(id);
    }
    // do 90 % ide samo, ostatak čeka fontove i stranu
    const tw = gsap.to(o, {
      v: 90, duration: 1.6, ease: 'power2.inOut', onUpdate: set,
      onComplete: () => {
        const wait = () => {
          if (!ready) { setTimeout(wait, 80); return; }
          gsap.to(o, { v: 100, duration: 0.45, ease: 'power2.out', onUpdate: set, onComplete: finish });
        };
        wait();
      },
    });
    const pieces = el.querySelectorAll('.pl-mark path, .pl-mark circle');
    gsap.fromTo(pieces, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.9, ease: 'expo.out', stagger: 0.12, delay: 0.15 });
    return () => tw.kill();
  }, [onDone]);

  return (
    <div className="preloader" ref={root} role="status" aria-label="Loading">
      <div className="pl-bar"><span ref={bar} /></div>
      <svg className="pl-mark" viewBox="0 0 48 48" aria-hidden="true">
        <path fill="currentColor" d="M11 9h6v30h-6z" />
        <path fill="currentColor" d="M22.6 21.2 34.2 9h7.6L27.2 24.4z" />
        <path fill="currentColor" d="M22.6 26.8l4.6-2.4L41.8 39h-7.6z" />
        <circle cx="24" cy="24" r="4.6" fill="var(--accent)" />
      </svg>
      <p className="pl-text label pl-fade">{t.loader}</p>
      <p className="pl-num pl-fade" ref={num} aria-hidden="true">000</p>
    </div>
  );
}
