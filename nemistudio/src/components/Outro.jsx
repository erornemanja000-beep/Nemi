import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { useLang } from '../i18n.jsx';
import { OUTRO } from '../content.js';
import { WORLDS } from '../worlds.js';
import { Words } from './Reveal.jsx';
import { goSite } from './Chrome.jsx';
import { reduced, vhPx } from '../scroll.js';

// After the last website the camera pulls back: the hotel was one window among four.
const PULL = 1.4; // scroll length of the pull-back, in viewport heights
const SHOT = { cafe: 4, law: 4, gym: 2, hotel: 6 }; // the chapter that stands for each world

export default function Outro() {
  const { L } = useLang();
  const sec = useRef();
  const grid = useRef();
  const head = useRef();
  const [H, setH] = useState(900);
  useLayoutEffect(() => {
    const m = () => setH(Math.round(vhPx() * 100));
    m();
    addEventListener('resize', m);
    return () => removeEventListener('resize', m);
  }, []);
  useEffect(() => {
    const g = grid.current;
    const last = g.lastElementChild;
    let raf;
    let prev = -1;
    const frame = () => {
      raf = requestAnimationFrame(frame);
      const r = sec.current.getBoundingClientRect();
      const dist = r.height - H;
      const p = reduced ? 1 : Math.min(1, Math.max(0, -r.top / dist));
      if (Math.abs(p - prev) < 1e-4) return;
      prev = p;
      // the last card's rest position (layout box, unaffected by transforms)
      const W = innerWidth;
      const cx = last.offsetLeft + last.offsetWidth / 2;
      const cy = last.offsetTop + last.offsetHeight / 2;
      const s0 = Math.max(W / last.offsetWidth, H / last.offsetHeight) * 1.02;
      const q = Math.min(1, p / 0.85);
      const e = q < 0.5 ? 4 * q * q * q : 1 - Math.pow(-2 * q + 2, 3) / 2;
      const k = Math.pow(s0, 1 - e);
      const t = (s0 - k) / (s0 - 1);
      const gx = g.offsetLeft + cx;
      const gy = g.offsetTop + cy;
      g.style.transformOrigin = `${cx}px ${cy}px`;
      g.style.transform = `translate(${(W / 2 - gx) * (1 - t)}px, ${(H / 2 - gy) * (1 - t)}px) scale(${k})`;
      g.style.setProperty('--t', t.toFixed(3));
      head.current.classList.toggle('on', p > 0.62);
    };
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, [H]);
  return (
    <section id="showroom" className="outro" ref={sec} style={{ height: H * (1 + PULL) }} data-site="0">
      <div className="outro-sticky" style={{ height: H }}>
        <div className="outro-head rv" ref={head}>
          <p className="eye"><span className="dot" />{L(OUTRO.eye)}</p>
          <h2 className="h-xl"><Words lines={L(OUTRO.h)} /></h2>
          <p className="lead">{L(OUTRO.p)}</p>
        </div>
        <div className="outro-grid" ref={grid}>
          {WORLDS.map((s, i) => (
            <a key={s.id} href={`#${s.id}`} className="ocard" style={{ '--i': i }} onClick={(e) => { e.preventDefault(); goSite(s.id); }}>
              <span className="ocard-bar"><i /><i /><i /><span>{L(s.brand)}</span></span>
              <span className="ocard-im"><img src={`${import.meta.env.BASE_URL}w/${s.id}/${SHOT[s.id]}/d/15.webp`} alt="" loading="lazy" /></span>
              <span className="ocard-cap">
                <b>0{i + 1} · {L(s.sense)}</b>
                <em>{L(s.name)}</em>
                <span className="ocard-go">{L(OUTRO.open)} ↗</span>
              </span>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
