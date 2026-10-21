import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useLang } from '../i18n.jsx';
import { SplitReveal, Counter } from './fx.jsx';

gsap.registerPlugin(ScrollTrigger);

// Levo stoji broj koraka i krug napretka, desno se smenjuju koraci
export default function Process() {
  const { t } = useLang();
  const [active, setActive] = useState(0);
  const root = useRef(null);
  const ring = useRef(null);
  const steps = t.process.steps;

  useEffect(() => {
    const el = root.current;
    const items = el.querySelectorAll('.step');
    const ts = [...items].map((item, i) => ScrollTrigger.create({
      trigger: item, start: 'top 60%', end: 'bottom 60%',
      onToggle: (s) => { if (s.isActive) setActive(i); },
    }));
    const prog = ScrollTrigger.create({
      trigger: el.querySelector('.steps'), start: 'top 60%', end: 'bottom 60%',
      onUpdate: (s) => { if (ring.current) ring.current.style.strokeDashoffset = String(1 - s.progress); },
    });
    return () => { ts.forEach((x) => x.kill()); prog.kill(); };
  }, [steps.length]);

  return (
    <section className="process section solid" id="process" ref={root}>
      <div className="wrap process-grid">
        <div className="process-side">
          <div className="process-sticky">
            <p className="label"><b>●</b> {t.process.label}</p>
            <SplitReveal className="h1" lines={t.process.title} />
            <div className="process-dial" aria-hidden="true">
              <svg viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="54" pathLength="1" className="dial-bg" />
                <circle cx="60" cy="60" r="54" pathLength="1" className="dial-fg" ref={ring} />
              </svg>
              <span className="dial-num" key={active}>{String(active + 1).padStart(2, '0')}</span>
            </div>
          </div>
        </div>
        <ol className="steps">
          {steps.map((s, i) => (
            <li key={s.name} className={`step${i === active ? ' is-active' : ''}`}>
              <span className="step-no">{String(i + 1).padStart(2, '0')}</span>
              <h3 className="h2">{s.name}</h3>
              <p className="lead">{s.text}</p>
            </li>
          ))}
        </ol>
      </div>

      <div className="wrap standards">
        <p className="label"><b>●</b> {t.standards.label}</p>
        <p className="std-text">{t.standards.text}</p>
        <ul className="std-grid">
          {t.standards.items.map((s) => (
            <li key={s.name}>
              <span className="std-num"><Counter to={s.to} prefix={s.prefix || ''} suffix={s.suffix} decimals={s.decimals || 0} /></span>
              <span className="std-name">{s.name}</span>
              <span className="std-note">{s.note}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
