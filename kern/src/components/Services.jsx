import { useRef, useState } from 'react';
import { motion, useAnimationFrame, useMotionValue, useSpring, useTransform, AnimatePresence } from 'motion/react';
import { useLang } from '../i18n.jsx';
import { SplitReveal, finePointer } from './fx.jsx';
import { world } from '../world/state.js';
import { reducedMotion } from '../hooks/useSmoothScroll.js';

const IMG = `${import.meta.env.BASE_URL}img/`;

/* Traka sa delatnostima: ide sama, ubrzava i menja smer sa skrolom */
function Marquee({ items }) {
  const x = useMotionValue(0);
  const track = useRef(null);
  const dir = useRef(-1);
  useAnimationFrame((_, delta) => {
    if (reducedMotion() || !track.current) return;
    const v = world.velocity;
    if (Math.abs(v) > 0.5) dir.current = v > 0 ? -1 : 1;
    const speed = (40 + Math.min(600, Math.abs(v) * 28)) * dir.current;
    const half = track.current.scrollWidth / 2;
    let nx = x.get() + (speed * delta) / 1000;
    if (nx <= -half) nx += half;
    if (nx > 0) nx -= half;
    x.set(nx);
  });
  const row = items.map((it) => <span key={it} className="mq-item">{it}<i aria-hidden="true">✦</i></span>);
  return (
    <div className="marquee" aria-label={items.join(', ')}>
      <motion.div className="mq-track" ref={track} style={{ x }} aria-hidden="true">{row}{row}</motion.div>
    </div>
  );
}

export default function Services() {
  const { t } = useLang();
  const [hover, setHover] = useState(-1);
  const list = useRef(null);
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 160, damping: 22, mass: 0.6 });
  const sy = useSpring(my, { stiffness: 160, damping: 22, mass: 0.6 });
  // slika se blago naginje u pravcu kretanja
  const vx = useMotionValue(0);
  const rot = useSpring(useTransform(vx, [-40, 40], [-8, 8]), { stiffness: 120, damping: 18 });
  const move = (e) => {
    if (!finePointer()) return;
    const r = list.current.getBoundingClientRect();
    vx.set(e.clientX - r.left - mx.get());
    mx.set(e.clientX - r.left);
    my.set(e.clientY - r.top);
  };
  const items = t.services.items;
  return (
    <section className="services section solid" id="services">
      <Marquee items={t.marquee} />
      <div className="wrap">
        <header className="sec-head">
          <p className="label"><b>●</b> {t.services.label}</p>
          <SplitReveal className="h1" lines={t.services.title} />
          <p className="lead">{t.services.lead}</p>
        </header>
        <div className="svc-wrap" ref={list} onMouseMove={move} onMouseLeave={() => setHover(-1)}>
        <ul className="svc-list">
          {items.map((s, i) => (
            <li key={s.key} className={`svc${hover === i ? ' is-hover' : ''}${hover > -1 && hover !== i ? ' is-dim' : ''}`} onMouseEnter={() => setHover(i)} data-cursor="">
              <span className="svc-no label">{String(i + 1).padStart(2, '0')}</span>
              <h3 className="svc-name">{s.name}</h3>
              <p className="svc-text">{s.text}</p>
              <img className="svc-thumb" src={`${IMG}${s.key}-800.webp`} alt="" loading="lazy" width="800" height="533" />
            </li>
          ))}
        </ul>
          <motion.div className="svc-float" style={{ x: sx, y: sy, rotate: rot }} aria-hidden="true">
            <AnimatePresence>
              {hover > -1 && (
                <motion.img
                  key={items[hover].key}
                  src={`${IMG}${items[hover].key}-800.webp`}
                  alt=""
                  initial={{ clipPath: 'inset(100% 0 0 0)', scale: 1.2 }}
                  animate={{ clipPath: 'inset(0% 0 0 0)', scale: 1 }}
                  exit={{ clipPath: 'inset(0 0 100% 0)', scale: 1.05 }}
                  transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                />
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
