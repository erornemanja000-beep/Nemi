import { useRef } from 'react';
import { useLang } from '../i18n.jsx';
import { posterUrl } from '../film/frames.js';

// A concept website for one industry, drawn as a small browser window.
export default function MiniSite({ ch, tilt = true, className = '' }) {
  const { L } = useLang();
  const c = ch.card;
  const ref = useRef();
  const move = (e) => {
    if (!tilt) return;
    const r = ref.current.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    ref.current.style.setProperty('--rx', `${-y * 8}deg`);
    ref.current.style.setProperty('--ry', `${x * 10}deg`);
    ref.current.style.setProperty('--gx', `${(x + 0.5) * 100}%`);
    ref.current.style.setProperty('--gy', `${(y + 0.5) * 100}%`);
  };
  const leave = () => { ref.current.style.setProperty('--rx', '0deg'); ref.current.style.setProperty('--ry', '0deg'); };
  return (
    <div className={`mini ${className}`} data-style={c.style} ref={ref} onPointerMove={move} onPointerLeave={leave}>
      <div className="mini-bar">
        <i /><i /><i />
        <span className="mini-url">{c.url}</span>
      </div>
      <div className="mini-page">
        <div className="mini-nav">
          <b>{L(c.name)}</b>
          <span className="mini-links">{L(c.nav).map((n) => <span key={n}>{n}</span>)}</span>
          <span className="mini-cta">{L(c.cta)}</span>
        </div>
        <div className="mini-hero" style={{ backgroundImage: `url(${posterUrl(ch.seq)})` }}>
          <div className="mini-copy">
            <small>{L(c.eye)}</small>
            <strong>{L(c.h)}</strong>
            <span className="mini-btn">{L(c.b)}</span>
          </div>
        </div>
        <div className="mini-feats">{L(c.f).map((f) => <span key={f}>{f}</span>)}</div>
      </div>
      <div className="mini-glare" />
    </div>
  );
}
