import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { motion, useMotionValue, useSpring } from 'motion/react';
import { reducedMotion } from '../hooks/useSmoothScroll.js';

gsap.registerPlugin(ScrollTrigger);

export const finePointer = () => typeof matchMedia !== 'undefined' && matchMedia('(hover: hover) and (pointer: fine)').matches;

/* ---------- Tekst se otkriva red po red iza maske (na skrol ili odmah) ---------- */
export function SplitReveal({ as: Tag = 'h2', lines, className = '', delay = 0, onLoad = false, play = true }) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el || reducedMotion()) return undefined;
    const inner = el.querySelectorAll('.split-inner');
    gsap.set(inner, { yPercent: 110, rotate: 3 });
    if (onLoad) {
      if (!play) return undefined;
      const tw = gsap.to(inner, { yPercent: 0, rotate: 0, duration: 1.1, ease: 'expo.out', stagger: .08, delay });
      return () => tw.kill();
    }
    const tw = gsap.to(inner, {
      yPercent: 0, rotate: 0, duration: 1, ease: 'expo.out', stagger: .07, delay,
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
    });
    return () => { tw.scrollTrigger?.kill(); tw.kill(); };
    // namerno bez `lines`: novi niz pri svakom renderu ne sme ponovo da pokrene animaciju
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [delay, onLoad, play, lines.length]);
  return (
    <Tag ref={ref} className={className}>
      {lines.map((line, i) => (
        <span className="split-line" key={i}><span className="split-inner">{line}</span></span>
      ))}
    </Tag>
  );
}

/* ---------- Pasus koji se „upali“ reč po reč dok se skroluje ---------- */
// range: [od, do] kao deo visine okidača (npr. [.6, .95] = od 60 % do 95 % preseka)
export function ScrollWords({ text, className = '', highlight = [], trigger, range }) {
  const ref = useRef(null);
  const words = text.split(' ');
  useEffect(() => {
    const el = ref.current;
    if (!el || reducedMotion()) return undefined;
    const spans = el.querySelectorAll('.w');
    const trg = trigger ? document.querySelector(trigger) : el;
    const st = range
      ? { trigger: trg, start: () => `top+=${trg.offsetHeight * range[0]} bottom`, end: () => `top+=${trg.offsetHeight * range[1]} bottom`, scrub: 0.6 }
      : { trigger: trg, start: 'top 78%', end: 'bottom 45%', scrub: 0.6 };
    const tw = gsap.fromTo(spans, { opacity: 0.12 }, { opacity: 1, ease: 'none', stagger: 0.05, scrollTrigger: st });
    return () => { tw.scrollTrigger?.kill(); tw.kill(); };
  }, [text, trigger, range]);
  return (
    <p ref={ref} className={className}>
      {words.map((w, i) => {
        const clean = w.replace(/[.,:;!?–—]/g, '');
        return <span key={i} className={`w${highlight.includes(clean) ? ' w-hi' : ''}`}>{w} </span>;
      })}
    </p>
  );
}

/* ---------- Slova se „promešaju“ pa slože (hover na linkovima) ---------- */
const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+';
export function Scramble({ text, className = '' }) {
  const [out, setOut] = useState(text);
  const raf = useRef(0);
  useEffect(() => setOut(text), [text]);
  const run = () => {
    if (reducedMotion()) return;
    cancelAnimationFrame(raf.current);
    const start = performance.now();
    const step = (now) => {
      const p = Math.min(1, (now - start) / 420);
      const shown = Math.floor(p * text.length);
      setOut(text.split('').map((c, i) => (i < shown || c === ' ' ? c : GLYPHS[(Math.random() * GLYPHS.length) | 0])).join(''));
      if (p < 1) raf.current = requestAnimationFrame(step);
    };
    raf.current = requestAnimationFrame(step);
  };
  useEffect(() => () => cancelAnimationFrame(raf.current), []);
  return <span className={className} onMouseEnter={run} aria-label={text}><span aria-hidden="true">{out}</span></span>;
}

/* ---------- Magnetno dugme: prati kursor par piksela ---------- */
export function Magnetic({ children, strength = .35, className = '' }) {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const sx = useSpring(x, { stiffness: 220, damping: 16, mass: .4 });
  const sy = useSpring(y, { stiffness: 220, damping: 16, mass: .4 });
  const move = (e) => {
    if (!finePointer()) return;
    const r = ref.current.getBoundingClientRect();
    x.set((e.clientX - (r.left + r.width / 2)) * strength);
    y.set((e.clientY - (r.top + r.height / 2)) * strength);
  };
  const leave = () => { x.set(0); y.set(0); };
  return (
    <motion.span ref={ref} className={`magnetic ${className}`} style={{ x: sx, y: sy, display: 'inline-flex' }} onMouseMove={move} onMouseLeave={leave}>
      {children}
    </motion.span>
  );
}

/* ---------- Kursor: tačka + krug koji kasni, raste nad linkovima, piše „View“ nad projektima ---------- */
export function Cursor() {
  const [on, setOn] = useState(false);
  const [mode, setMode] = useState('');
  const [label, setLabel] = useState('');
  const x = useMotionValue(-100);
  const y = useMotionValue(-100);
  const rx = useSpring(x, { stiffness: 420, damping: 36, mass: .5 });
  const ry = useSpring(y, { stiffness: 420, damping: 36, mass: .5 });
  useEffect(() => {
    if (!finePointer()) return undefined;
    setOn(true);
    document.documentElement.classList.add('has-cursor');
    const move = (e) => {
      x.set(e.clientX); y.set(e.clientY);
      const t = e.target.closest?.('[data-cursor], a, button, input, textarea, label');
      const in3d = document.documentElement.dataset.cursor3d;
      if (!t && in3d) { setMode('label'); setLabel(in3d); return; }
      if (!t) { setMode(''); setLabel(''); return; }
      setMode(t.dataset.cursor ? 'label' : (t.matches('input, textarea') ? 'text' : 'link'));
      setLabel(t.dataset.cursor || '');
    };
    const leave = () => { x.set(-100); y.set(-100); };
    window.addEventListener('pointermove', move, { passive: true });
    document.addEventListener('pointerleave', leave);
    return () => {
      window.removeEventListener('pointermove', move);
      document.removeEventListener('pointerleave', leave);
      document.documentElement.classList.remove('has-cursor');
    };
  }, [x, y]);
  if (!on) return null;
  return (
    <>
      <motion.div className="cursor-dot" style={{ x, y }} aria-hidden="true" />
      <motion.div className={`cursor-ring is-${mode || 'idle'}`} style={{ x: rx, y: ry }} aria-hidden="true">
        <span>{label}</span>
      </motion.div>
    </>
  );
}

/* ---------- Brojač koji odbrojava kad uđe u ekran ---------- */
export function Counter({ to, suffix = '', prefix = '', decimals = 0 }) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    const fmt = (v) => `${prefix}${v.toFixed(decimals)}${suffix}`;
    if (reducedMotion()) { el.textContent = fmt(to); return undefined; }
    const o = { v: 0 };
    el.textContent = fmt(0);
    const tw = gsap.to(o, {
      v: to, duration: 1.8, ease: 'expo.out', onUpdate: () => { el.textContent = fmt(o.v); },
      scrollTrigger: { trigger: el, start: 'top 90%', once: true },
    });
    return () => { tw.scrollTrigger?.kill(); tw.kill(); };
  }, [to, suffix, prefix, decimals]);
  return <span ref={ref} />;
}

export function Arrow({ className = 'arrow' }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M4 10h12M11 5l5 5-5 5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
