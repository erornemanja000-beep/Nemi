import { useEffect, useRef, useState } from 'react';
import { useLang } from '../i18n.jsx';
import { SERVICES, PROCESS, FACTS, FAQ, CONTACT, FOOT, INDUSTRIES, UI, SIXTH } from '../content.js';
import { reduced } from '../scroll.js';
import { RevealHeading, Up } from './Reveal.jsx';
import { Logo, replayIntro } from './Chrome.jsx';
import { scrollToId, scrollToY } from '../scroll.js';

const BASE = import.meta.env.BASE_URL;

// the sixth sense: a line that decodes itself out of noise (LITORALE), then the name explained
const NOISE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz§&·';
export function Sixth() {
  const { L, lang } = useLang();
  const ref = useRef();
  useEffect(() => {
    const el = ref.current;
    const chs = [...el.querySelectorAll('.sx-ch')];
    if (reduced) { el.classList.add('on'); return; }
    let id;
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      io.disconnect();
      el.classList.add('on');
      let tick = 0;
      id = setInterval(() => {
        tick++;
        chs.forEach((c, i) => {
          const at = 2 + i * 0.45;
          if (tick < at - 1.5) c.textContent = '·';
          else if (tick < at) c.textContent = NOISE[(Math.random() * NOISE.length) | 0];
          else c.textContent = c.dataset.ch;
          c.classList.toggle('set', tick >= at);
        });
        if (tick > 3 + chs.length * 0.45) clearInterval(id);
      }, 40);
    }, { rootMargin: '0px 0px -25% 0px' });
    io.observe(el);
    return () => { io.disconnect(); clearInterval(id); };
  }, [lang]);
  let k = 0;
  return (
    <section className="sec sec-dark sixth" id="sinn">
      <div className="wrap">
        <p className="eye"><span className="dot" />{L(SIXTH.eye)}</p>
        <h2 className="sx-h" ref={ref} key={lang}>
          {L(SIXTH.h).split(/(\*[^*]+\*)/).filter(Boolean).map((part, pi) => {
            const em = part.startsWith('*');
            const txt = em ? part.slice(1, -1) : part;
            // letters grouped per word so lines only break between words
            const words = txt.split(/(\s+)/).filter(Boolean).map((w, wi) => (/^\s+$/.test(w) ? ' ' : (
              <span className="sx-w" key={wi}>
                {[...w].map((ch) => <span className="sx-ch" data-ch={ch} key={k++}>·</span>)}
              </span>
            )));
            return em ? <em key={pi}>{words}</em> : <span key={pi}>{words}</span>;
          })}
        </h2>
        <Up as="p" className="lead sx-p" delay={400}>{L(SIXTH.p)}</Up>
      </div>
    </section>
  );
}

// services as an index: hovering a row floats a picture that follows the cursor
export function Services() {
  const { L } = useLang();
  const prev = useRef();
  const [img, setImg] = useState(null);
  useEffect(() => {
    const el = prev.current;
    let x = innerWidth / 2, y = innerHeight / 2, tx = x, ty = y, raf;
    const mv = (e) => { tx = e.clientX; ty = e.clientY; };
    const loop = () => { x += (tx - x) * 0.14; y += (ty - y) * 0.14; el.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%) rotate(${(tx - x) * 0.03}deg)`; raf = requestAnimationFrame(loop); };
    addEventListener('pointermove', mv, { passive: true });
    raf = requestAnimationFrame(loop);
    return () => { removeEventListener('pointermove', mv); cancelAnimationFrame(raf); };
  }, []);
  return (
    <section id="leistungen" className="sec sec-dark">
      <div className="wrap">
        <div className="sec-head">
          <p className="eye">{L(SERVICES.eye)}</p>
          <RevealHeading lines={L(SERVICES.h)} className="h-xl" />
        </div>
        <ol className="svc" onPointerLeave={() => setImg(null)}>
          {SERVICES.items.map((s, i) => (
            <Up as="li" key={s.n} delay={i * 60} className="svc-row" onPointerEnter={() => setImg(s.img)}>
              <span className="svc-n">{s.n}</span>
              <span className="svc-t">{L(s.t)}</span>
              <span className="svc-d">{L(s.d)}</span>
              <span className="svc-arr">↗</span>
            </Up>
          ))}
        </ol>
      </div>
      <div className={`svc-prev${img ? ' on' : ''}`} ref={prev} aria-hidden="true">
        {SERVICES.items.map((s) => (
          <img key={s.img} src={BASE + s.img} alt="" className={img === s.img ? 'act' : ''} loading="lazy" />
        ))}
      </div>
    </section>
  );
}

export function Process() {
  const { L } = useLang();
  return (
    <section id="ablauf" className="sec sec-dark proc">
      <div className="wrap proc-grid">
        <div className="proc-head">
          <p className="eye">{L(PROCESS.eye)}</p>
          <RevealHeading lines={L(PROCESS.h)} className="h-xl" />
        </div>
        <ol className="proc-steps">
          {PROCESS.steps.map((s, i) => (
            <Up as="li" key={i} className="proc-step">
              <span className="proc-n">{String(i + 1).padStart(2, '0')}</span>
              <div>
                <h3>{L(s.t)}</h3>
                <p>{L(s.d)}</p>
              </div>
            </Up>
          ))}
        </ol>
      </div>
      <div className="wrap facts">
        {FACTS.map((f, i) => (
          <Up key={i} className="fact" delay={i * 80}>
            <b>{L(f.v)}</b><span>{L(f.u)}</span>
            <p>{L(f.d)}</p>
          </Up>
        ))}
      </div>
    </section>
  );
}

export function Faq() {
  const { L } = useLang();
  const [open, setOpen] = useState(0);
  return (
    <section id="faq" className="sec sec-dark faq">
      <div className="wrap faq-grid">
        <div>
          <p className="eye">{L(FAQ.eye)}</p>
          <RevealHeading lines={L(FAQ.h)} className="h-xl" />
          <p className="lead">{L(FAQ.p)}</p>
        </div>
        <div className="faq-list">
          {FAQ.items.map((f, i) => (
            <div className={`faq-item${open === i ? ' open' : ''}`} key={i}>
              <button onClick={() => setOpen(open === i ? -1 : i)} aria-expanded={open === i}>
                <span>{L(f.q)}</span><i />
              </button>
              <div className="faq-a"><p>{L(f.a)}</p></div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function Contact() {
  const { L } = useLang();
  const [copied, setCopied] = useState(false);
  const [sent, setSent] = useState(false);
  const f = CONTACT.f;
  const submit = (e) => {
    e.preventDefault();
    const d = new FormData(e.target);
    const body = [
      `${L(f.name)}: ${d.get('name')}`,
      `${L(f.email)}: ${d.get('email')}`,
      `${L(f.biz)}: ${d.get('business') || '-'}`,
      `${L(f.ind)}: ${d.get('industry') || '-'}`,
      '',
      d.get('message') || '',
    ].join('\n');
    location.href = `mailto:${CONTACT.mail}?subject=${encodeURIComponent('Website · ' + (d.get('business') || d.get('name')))}&body=${encodeURIComponent(body)}`;
    setSent(true);
  };
  const copy = () => {
    navigator.clipboard?.writeText(CONTACT.mail).then(() => { setCopied(true); setTimeout(() => setCopied(false), 1800); });
  };
  return (
    <section id="kontakt" className="sec sec-dark contact">
      <div className="wrap contact-grid">
        <div>
          <p className="eye">{L(CONTACT.eye)}</p>
          <RevealHeading lines={L(CONTACT.h)} className="h-xl" />
          <p className="lead">{L(CONTACT.p)}</p>
          <div className="mail">
            <small>{L(CONTACT.direct)}</small>
            <a href={`mailto:${CONTACT.mail}`}>{CONTACT.mail}</a>
            <button onClick={copy}>{copied ? L(CONTACT.copied) : L(CONTACT.copy)}</button>
          </div>
        </div>
        <form className="form" onSubmit={submit} name="kontakt">
          <label><span>{L(f.name)}</span><input name="name" required autoComplete="name" /></label>
          <label><span>{L(f.email)}</span><input name="email" type="email" required autoComplete="email" /></label>
          <label><span>{L(f.biz)}</span><input name="business" autoComplete="organization" /></label>
          <label><span>{L(f.ind)}</span>
            <select name="industry" defaultValue="">
              <option value="" disabled>{L(f.pick)}</option>
              {L(INDUSTRIES).map((x) => <option key={x}>{x}</option>)}
              <option>{L(f.other)}</option>
            </select>
          </label>
          <label className="full"><span>{L(f.msg)}</span><textarea name="message" rows={4} /></label>
          <button className="btn btn-signal full" type="submit">{L(f.send)}<span>→</span></button>
          {sent && <p className="form-ok full">{L(f.sent)}</p>}
        </form>
      </div>
    </section>
  );
}

export function Footer() {
  const { L } = useLang();
  const [credits, setCredits] = useState(false);
  return (
    <footer className="foot">
      <div className="wrap foot-top">
        <RevealHeading lines={L(FOOT.big)} className="h-xxl" />
        <a className="btn btn-signal" href="#kontakt" onClick={(e) => { e.preventDefault(); scrollToId('kontakt'); }}>{L(UI.start)}<span>→</span></a>
      </div>
      <div className="foot-mark" aria-hidden="true">nemi</div>
      <div className="wrap foot-bar">
        <Logo small />
        <span>© 2026 Nemi Studio</span>
        <a href={`${BASE}impressum.html`}>{L(FOOT.legal)}</a>
        <a href={`${BASE}datenschutz.html`}>{L(FOOT.privacy)}</a>
        <button onClick={() => setCredits(!credits)}>{L(FOOT.credits)}</button>
        <button onClick={replayIntro}>▶ {L(UI.replay)}</button>
        <button onClick={() => scrollToY(0)}>{L(FOOT.top)} ↑</button>
      </div>
      {credits && <p className="wrap foot-credits">{L(FOOT.creditText)}</p>}
    </footer>
  );
}
