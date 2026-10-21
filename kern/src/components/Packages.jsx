import { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'motion/react';
import { useLang } from '../i18n.jsx';
import { SplitReveal, Magnetic, Arrow, finePointer } from './fx.jsx';
import { scrollToHash } from '../hooks/useSmoothScroll.js';

// Kartica se naginje u 3D za mišem, a odsjaj prati kursor
function TiltCard({ children, className }) {
  const ref = useRef(null);
  const px = useMotionValue(0.5);
  const py = useMotionValue(0.5);
  const rx = useSpring(useTransform(py, [0, 1], [7, -7]), { stiffness: 180, damping: 18 });
  const ry = useSpring(useTransform(px, [0, 1], [-9, 9]), { stiffness: 180, damping: 18 });
  const gx = useTransform(px, (v) => `${v * 100}%`);
  const gy = useTransform(py, (v) => `${v * 100}%`);
  const move = (e) => {
    if (!finePointer()) return;
    const r = ref.current.getBoundingClientRect();
    px.set((e.clientX - r.left) / r.width);
    py.set((e.clientY - r.top) / r.height);
  };
  const leave = () => { px.set(0.5); py.set(0.5); };
  return (
    <motion.article ref={ref} className={className} onMouseMove={move} onMouseLeave={leave} style={{ rotateX: rx, rotateY: ry, '--gx': gx, '--gy': gy }}>
      {children}
    </motion.article>
  );
}

export default function Packages() {
  const { t } = useLang();
  const p = t.packages;
  return (
    <section className="packages section paper" id="packages">
      <div className="wrap">
        <header className="sec-head">
          <p className="label"><b>●</b> {p.label}</p>
          <SplitReveal className="h1" lines={p.title} />
          <p className="lead">{p.lead}</p>
        </header>
        <div className="pk-grid">
          {p.items.map((it, i) => (
            <TiltCard key={it.name} className={`pk${i === 1 ? ' pk-featured' : ''}`}>
              {i === 1 && <span className="pk-badge">{p.featured}</span>}
              <p className="label">{String(i + 1).padStart(2, '0')}</p>
              <h3 className="pk-name">{it.name}</h3>
              <p className="pk-for">{it.for}</p>
              <p className="pk-price"><span className="pk-from">{p.from}</span>{new Intl.NumberFormat(t.estimate.locale, { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(it.price)}<span className="pk-net">{p.net}</span></p>
              <p className="pk-time"><span className="label">⏱</span> {it.time}</p>
              <ul className="pk-points">{it.points.map((pt) => <li key={pt}>{pt}</li>)}</ul>
              <Magnetic strength={0.2}>
                <a className={`btn ${i === 1 ? 'btn-accent' : 'btn-dark'}`} href="#contact" onClick={(e) => { e.preventDefault(); scrollToHash('#contact'); }}>{p.cta}<Arrow /></a>
              </Magnetic>
            </TiltCard>
          ))}
        </div>
        <p className="pk-care">{p.care}</p>
      </div>
    </section>
  );
}
