import { useEffect, useMemo, useState } from 'react';
import { motion, useSpring, useTransform } from 'motion/react';
import { useLang } from '../i18n.jsx';
import { SplitReveal, Magnetic, Arrow } from './fx.jsx';
import { scrollToHash } from '../hooks/useSmoothScroll.js';

// Okvirne cene (EUR neto) po tržišnim podacima iz istraživanja; studio ih menja ovde
const BASE = { one: { price: 1900, weeks: 2, perPage: 0 }, site: { price: 4900, weeks: 4, perPage: 290 }, shop: { price: 8900, weeks: 7, perPage: 290 } };
const EXTRA = { brand: [2400, 2], lang: [900, 0.5], book: [700, 0.5], motion: [2900, 2], seo: [800, 0.5], copy: [600, 1] };
const MAX_PAGES = 30;

function Money({ value, locale }) {
  const spring = useSpring(value, { stiffness: 90, damping: 20 });
  useEffect(() => { spring.set(value); }, [value, spring]);
  const fmt = useMemo(() => new Intl.NumberFormat(locale, { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }), [locale]);
  const text = useTransform(spring, (v) => fmt.format(Math.round(v / 10) * 10));
  return <motion.span>{text}</motion.span>;
}

export default function Estimate() {
  const { t } = useLang();
  const e = t.estimate;
  const [type, setType] = useState('site');
  const [pages, setPages] = useState(5);
  const [extras, setExtras] = useState(() => new Set(['seo']));
  const kind = e.types.find((x) => x.k === type);

  const pick = (k) => {
    setType(k);
    const inc = e.types.find((x) => x.k === k).pages;
    setPages((p) => (k === 'one' ? 1 : Math.max(inc, p)));
  };
  const toggle = (k) => setExtras((s) => { const n = new Set(s); if (n.has(k)) n.delete(k); else n.add(k); return n; });

  const { low, high, wMin, wMax } = useMemo(() => {
    const b = BASE[type];
    const extraPages = Math.max(0, pages - kind.pages);
    let price = b.price + extraPages * b.perPage;
    let weeks = b.weeks + extraPages * 0.15;
    extras.forEach((k) => { price += EXTRA[k][0]; weeks += EXTRA[k][1]; });
    return { low: price, high: Math.round((price * 1.2) / 100) * 100, wMin: Math.ceil(weeks), wMax: Math.ceil(weeks * 1.3) };
  }, [type, pages, extras, kind]);

  return (
    <section className="estimate section solid" id="estimate">
      <div className="wrap">
        <header className="sec-head">
          <p className="label"><b>●</b> {e.label}</p>
          <SplitReveal className="h1" lines={e.title} />
          <p className="lead">{e.lead}</p>
        </header>
        <div className="est-grid">
          <div className="est-controls">
            <fieldset className="est-group">
              <legend className="label">{e.type}</legend>
              <div className="est-types">
                {e.types.map((x) => (
                  <button key={x.k} type="button" className={type === x.k ? 'is-on' : ''} aria-pressed={type === x.k} onClick={() => pick(x.k)}>
                    {type === x.k && <motion.span layoutId="est-type" className="est-pill" transition={{ type: 'spring', stiffness: 380, damping: 32 }} />}
                    <span>{x.name}</span>
                  </button>
                ))}
              </div>
            </fieldset>

            <fieldset className="est-group" disabled={type === 'one'}>
              <legend className="label">{e.pages} <span className="est-val">{pages}</span> <span className="est-inc">({kind.pages} {e.included})</span></legend>
              <input
                className="est-range"
                type="range"
                min={kind.pages}
                max={type === 'one' ? 1 : MAX_PAGES}
                value={pages}
                onChange={(ev) => setPages(+ev.target.value)}
                style={{ '--p': type === 'one' ? 0 : (pages - kind.pages) / (MAX_PAGES - kind.pages) }}
                aria-label={e.pages}
              />
            </fieldset>

            <fieldset className="est-group">
              <legend className="label">{e.extras}</legend>
              <div className="est-extras">
                {e.extraItems.map((x) => {
                  const on = extras.has(x.k);
                  return (
                    <button key={x.k} type="button" className={`est-extra${on ? ' is-on' : ''}`} aria-pressed={on} onClick={() => toggle(x.k)}>
                      <span className="est-check" aria-hidden="true">
                        <motion.svg viewBox="0 0 16 16" initial={false} animate={{ opacity: on ? 1 : 0, scale: on ? 1 : 0.5 }}><path d="M3 8.5l3 3 7-7" /></motion.svg>
                      </span>
                      {x.name}
                    </button>
                  );
                })}
              </div>
            </fieldset>
          </div>

          <div className="est-result" aria-live="polite">
            <p className="label">{e.result}</p>
            <p className="est-price"><Money value={low} locale={e.locale} /><span className="est-dash">–</span><Money value={high} locale={e.locale} /></p>
            <p className="est-net">{e.net}</p>
            <div className="est-time">
              <p className="label">{e.timeline}: <b>{wMin}–{wMax} {e.weeks}</b></p>
              <div className="est-weeks" aria-hidden="true">
                {Array.from({ length: 20 }).map((_, i) => (
                  <span key={i} className={i < wMin ? 'on' : i < wMax ? 'maybe' : ''} />
                ))}
              </div>
            </div>
            <Magnetic strength={0.2}>
              <a className="btn btn-accent" href="#contact" onClick={(ev) => { ev.preventDefault(); scrollToHash('#contact'); }}>{e.cta}<Arrow /></a>
            </Magnetic>
            <p className="est-note">{e.note}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
