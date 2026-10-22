import { useEffect, useRef } from 'react';

// Splits headline lines into words for the blur-in reveal. `*word*` becomes the italic accent.
export function Words({ lines, start = 0 }) {
  let i = start;
  return lines.map((line, li) => (
    <span className="ln" key={li}>
      {line.split(/(\*[^*]+\*)/).filter(Boolean).flatMap((part, pi) => {
        const em = part.startsWith('*');
        const text = em ? part.slice(1, -1) : part;
        return text.split(/(\s+)/).filter((w) => w.length).map((w, wi) => {
          if (/^\s+$/.test(w)) return ' ';
          const el = (
            <span className="w" style={{ '--i': i }} key={`${pi}-${wi}`}>
              {em ? <em>{w}</em> : w}
            </span>
          );
          i++;
          return el;
        });
      })}
    </span>
  ));
}

// body text: `*word*` becomes a highlighted key word, underlined once it scrolls into view
let kwIO;
const watch = (el) => {
  if (!el || el.classList.contains('on')) return;
  kwIO = kwIO || new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('on'); kwIO.unobserve(e.target); }
  }), { rootMargin: '0px 0px -12% 0px' });
  kwIO.observe(el);
};
export function Rich({ text }) {
  return text.split(/(\*[^*]+\*)/).filter(Boolean).map((part, i) => (part.startsWith('*') ? <em className="kw" ref={watch} key={i}>{part.slice(1, -1)}</em> : part));
}

// a heading that reveals when it scrolls into view (outside the film)
export function RevealHeading({ as: Tag = 'h2', lines, className = '' }) {
  const ref = useRef();
  useEffect(() => {
    const el = ref.current;
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { el.classList.add('on'); io.disconnect(); } }, { rootMargin: '0px 0px -12% 0px' });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return <Tag ref={ref} className={`rv ${className}`}><Words lines={lines} /></Tag>;
}

// any block that fades up into view
export function Up({ as: Tag = 'div', className = '', children, delay = 0, ...rest }) {
  const ref = useRef();
  useEffect(() => {
    const el = ref.current;
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { el.classList.add('on'); io.disconnect(); } }, { rootMargin: '0px 0px -8% 0px' });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return <Tag ref={ref} className={`up ${className}`} style={{ '--d': delay + 'ms' }} {...rest}>{children}</Tag>;
}
