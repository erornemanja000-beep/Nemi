import { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useLang } from '../i18n.jsx';
import { SplitReveal } from './fx.jsx';

// Prekidač Kleinbetrieb / Unternehmen: ista studija, drugačiji odgovor
export default function Scale() {
  const { t } = useLang();
  const [mode, setMode] = useState('small');
  const s = t.scale;
  const data = mode === 'small'
    ? { title: s.smallTitle, text: s.smallText, points: s.smallPoints }
    : { title: s.largeTitle, text: s.largeText, points: s.largePoints };
  return (
    <section className="scale section solid" id="scale">
      <div className="wrap">
        <header className="sec-head">
          <p className="label"><b>●</b> {s.label}</p>
          <SplitReveal className="h1" lines={s.title} />
        </header>
        <div className="scale-toggle" role="tablist" aria-label={s.label}>
          {[['small', s.small], ['large', s.large]].map(([k, label]) => (
            <button key={k} type="button" role="tab" aria-selected={mode === k} className={mode === k ? 'is-on' : ''} onClick={() => setMode(k)}>
              {mode === k && <motion.span layoutId="scale-pill" className="scale-pill" transition={{ type: 'spring', stiffness: 380, damping: 32 }} />}
              <span className="scale-label">{label}</span>
            </button>
          ))}
        </div>
        <div className="scale-body" role="tabpanel">
          <AnimatePresence mode="wait">
            <motion.div
              key={mode + t.scale.small}
              className="scale-grid"
              initial={{ opacity: 0, y: 30, filter: 'blur(6px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, y: -20, filter: 'blur(6px)' }}
              transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="scale-copy">
                <h3 className="h2">{data.title}</h3>
                <p className="lead">{data.text}</p>
              </div>
              <ul className="scale-points">
                {data.points.map((pt, i) => (
                  <motion.li key={pt} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.12 + i * 0.07, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}>
                    <span className="label">{String(i + 1).padStart(2, '0')}</span>{pt}
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          </AnimatePresence>
          <div className={`scale-visual is-${mode}`} aria-hidden="true">
            {Array.from({ length: 9 }).map((_, i) => <span key={i} style={{ '--i': i }} />)}
          </div>
        </div>
      </div>
    </section>
  );
}
