import { AnimatePresence, motion } from 'motion/react';
import { useLang } from '../i18n.jsx';
import { SplitReveal } from './fx.jsx';
import { world } from '../world/state.js';
import { scrollToY } from '../hooks/useSmoothScroll.js';

const IMG = `${import.meta.env.BASE_URL}img/`;

export function pickProject(i) {
  const [a, b] = world.workRange || [0, 0];
  if (b <= a) return;
  scrollToY(a + ((b - a) * i) / Math.max(1, world.count - 1) + 2);
}

// Galerija sama je u 3D sceni (Scene.jsx); ovde su naslov, podaci o projektu u centru i indeks
export default function Work({ active, webgl }) {
  const { t } = useLang();
  const list = t.projects;
  const p = list[active] || list[0];
  const n = list.length;

  if (!webgl) {
    return (
      <section className="work work-static section" id="work">
        <div className="wrap">
          <header className="sec-head">
            <p className="label"><b>●</b> {t.work.label}</p>
            <SplitReveal className="h1" lines={t.work.title} />
          </header>
          <div className="work-grid">
            {list.map((x) => (
              <article className="work-card" key={x.key}>
                <img src={`${IMG}${x.key}-800.webp`} alt="" loading="lazy" width="800" height="533" />
                <h3>{x.name}</h3>
                <p className="label">{x.kind} · {x.what}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="work" id="work" style={{ '--n': n }}>
      <div className="work-stage">
        <header className={`work-head wrap${active > 0 ? ' is-away' : ''}`}>
          <p className="label"><b>●</b> {t.work.label}</p>
          <SplitReveal className="h1" lines={t.work.title} />
          <p className="work-note">{t.work.note}</p>
        </header>

        <div className="work-info wrap" aria-live="polite">
          <AnimatePresence mode="wait">
            <motion.div
              key={p.key}
              className="work-card-info"
              initial={{ opacity: 0, y: 26 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -18 }}
              transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
            >
              <p className="work-count label"><b>{String(active + 1).padStart(2, '0')}</b> / {String(n).padStart(2, '0')} <span className="pill">{t.work.concept}</span></p>
              <h3 className="work-name">{p.name}</h3>
              <p className="work-meta">{p.kind} · {p.what}</p>
              <ul className="work-tags">{p.tags.map((tag) => <li key={tag}>{tag}</li>)}</ul>
            </motion.div>
          </AnimatePresence>
        </div>

        <ol className="work-index" aria-label={t.work.label}>
          {list.map((x, i) => (
            <li key={x.key}>
              <button type="button" className={i === active ? 'is-active' : ''} onClick={() => pickProject(i)}>
                <span>{String(i + 1).padStart(2, '0')}</span>{x.name}
              </button>
            </li>
          ))}
        </ol>

        <div className="work-progress" aria-hidden="true">
          <span style={{ transform: `scaleX(${(active + 1) / n})` }} />
        </div>
      </div>
    </section>
  );
}
