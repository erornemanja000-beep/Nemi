import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { reduced } from '../scroll.js';

// Small building blocks shared by the four concept websites.

const BASE = import.meta.env.BASE_URL;
export const img = (n) => `${BASE}img/${n}.webp`;
export const vid = (n) => `${BASE}v/${n}.mp4`;
export const poster = (n) => `${BASE}v/${n}.webp`;
// menu / card images can be a photo or a video poster
export const pic = (n) => (n.includes('-') ? img(n) : poster(n));

// `*word*` -> <em>word</em>
export function Rich({ text }) {
  return text.split(/(\*[^*]+\*)/).filter(Boolean).map((p, i) => (p.startsWith('*') ? <em key={i}>{p.slice(1, -1)}</em> : p));
}

// adds .on once the element scrolls into view
export function useOn(ref, margin = '-10%') {
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { el.classList.add('on'); io.disconnect(); } }, { rootMargin: `0px 0px ${margin} 0px` });
    io.observe(el);
    return () => io.disconnect();
  }, []);
}

// headline whose lines slide up out of a mask
export function Lines({ lines, as: Tag = 'h2', className = '' }) {
  const ref = useRef();
  useOn(ref);
  return (
    <Tag ref={ref} className={`k-lines ${className}`}>
      {lines.map((l, i) => (
        <span className="k-ln" key={i}><span style={{ '--i': i }}><Rich text={l} /></span></span>
      ))}
    </Tag>
  );
}

export function Fade({ as: Tag = 'div', className = '', delay = 0, children, ...rest }) {
  const ref = useRef();
  useOn(ref, '-6%');
  return <Tag ref={ref} className={`k-fade ${className}`} style={{ '--d': `${delay}ms` }} {...rest}>{children}</Tag>;
}

// picture that drifts against the scroll inside its frame
export function Parallax({ src, alt = '', amount = 12, className = '', children }) {
  const box = useRef();
  const im = useRef();
  useEffect(() => {
    if (reduced) return;
    const tw = gsap.fromTo(im.current, { yPercent: -amount }, {
      yPercent: amount, ease: 'none',
      scrollTrigger: { trigger: box.current, start: 'top bottom', end: 'bottom top', scrub: true },
    });
    return () => { tw.scrollTrigger && tw.scrollTrigger.kill(); tw.kill(); };
  }, [amount]);
  return (
    <div className={`k-par ${className}`} ref={box}>
      <img ref={im} src={src} alt={alt} loading="lazy" style={{ height: `${100 + amount * 2.2}%`, top: `${-amount * 1.1}%` }} />
      {children}
    </div>
  );
}

// looping background film: loads when near, plays only while visible
export function HeroVideo({ name, className = '', eager = false }) {
  const ref = useRef();
  const [src, setSrc] = useState(eager ? vid(name) : null);
  useEffect(() => {
    const v = ref.current;
    const near = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setSrc(vid(name)); near.disconnect(); } }, { rootMargin: '150% 0px' });
    const vis = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { const p = v.play(); if (p) p.catch(() => {}); } else v.pause();
    });
    near.observe(v);
    vis.observe(v);
    return () => { near.disconnect(); vis.disconnect(); };
  }, [name]);
  return <video ref={ref} className={className} src={src || undefined} poster={poster(name)} muted loop playsInline autoPlay preload={eager ? 'auto' : 'none'} />;
}

export function Marquee({ items, sep = '·', className = '', speed = 40 }) {
  const row = items.map((t, i) => <span key={i}>{t}<i>{sep}</i></span>);
  return (
    <div className={`k-mq ${className}`} aria-hidden="true">
      <div className="k-mq-t" style={{ '--s': `${speed}s` }}>
        <div>{row}</div><div>{row}</div>
      </div>
    </div>
  );
}

// forms in the concepts do not send anything; they say so
export function useDemo() {
  const [done, setDone] = useState(false);
  const submit = (e) => { e.preventDefault(); setDone(true); setTimeout(() => setDone(false), 4200); };
  return [done, submit];
}
export const DEMO = { de: 'Konzept-Demo: Hier würde jetzt die Bestätigung kommen.', en: 'Concept demo: this is where the confirmation would appear.' };

// counts up when it scrolls into view
export function Count({ to, suffix = '', locale = 'de-AT' }) {
  const ref = useRef();
  const [n, setN] = useState(reduced ? to : 0);
  useEffect(() => {
    if (reduced) return;
    const el = ref.current;
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      io.disconnect();
      const o = { v: 0 };
      gsap.to(o, { v: to, duration: 1.8, ease: 'power3.out', onUpdate: () => setN(Math.round(o.v)) });
    });
    io.observe(el);
    return () => io.disconnect();
  }, [to]);
  return <span ref={ref}>{n.toLocaleString(locale)}{suffix}</span>;
}
