import { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useLang } from '../i18n.jsx';
import { SplitReveal } from './fx.jsx';

export default function Faq() {
  const { t } = useLang();
  const [open, setOpen] = useState(0);
  return (
    <section className="faq section solid" id="faq">
      <div className="wrap faq-grid">
        <header className="faq-head">
          <p className="label"><b>●</b> {t.faq.label}</p>
          <SplitReveal className="h1" lines={[t.faq.title[0], <span className="serif accent" key="s">{t.faq.title[1]}</span>]} />
        </header>
        <ul className="faq-list">
          {t.faq.items.map((it, i) => {
            const on = open === i;
            return (
              <li key={it.q} className={`faq-item${on ? ' is-open' : ''}`}>
                <h3>
                  <button type="button" aria-expanded={on} aria-controls={`faq-${i}`} id={`faq-q-${i}`} onClick={() => setOpen(on ? -1 : i)}>
                    <span>{it.q}</span>
                    <span className="faq-icon" aria-hidden="true" />
                  </button>
                </h3>
                <AnimatePresence initial={false}>
                  {on && (
                    <motion.div
                      id={`faq-${i}`}
                      role="region"
                      aria-labelledby={`faq-q-${i}`}
                      className="faq-a"
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
                    >
                      <p>{it.a}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
