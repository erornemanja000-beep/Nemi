import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { useLang } from '../i18n.jsx';
import { Mark } from './Logo.jsx';
import { scrollToHash, reducedMotion } from '../hooks/useSmoothScroll.js';
import credits from '../credits.json';

function Clock() {
  const [time, setTime] = useState('');
  useEffect(() => {
    const f = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Vienna', hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23' });
    const tick = () => setTime(f.format(new Date()));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);
  return <span className="clock">{time} CET</span>;
}

export default function Footer() {
  const { t } = useLang();
  const word = useRef(null);
  const [showCredits, setShowCredits] = useState(false);

  useEffect(() => {
    if (reducedMotion()) return undefined;
    const letters = word.current.querySelectorAll('span');
    const tw = gsap.fromTo(letters, { yPercent: 105 }, {
      yPercent: 0, ease: 'expo.out', duration: 1.2, stagger: 0.06,
      scrollTrigger: { trigger: word.current, start: 'top 95%', once: true },
    });
    return () => { tw.scrollTrigger?.kill(); tw.kill(); };
  }, []);

  const links = [['#work', t.nav.work], ['#services', t.nav.services], ['#process', t.nav.process], ['#faq', t.nav.faq], ['#contact', t.nav.contact]];
  const go = (e, href) => { e.preventDefault(); scrollToHash(href); };

  return (
    <footer className="footer">
      <div className="wrap">
        <div className="foot-top">
          <p className="foot-about">{t.footer.about}</p>
          <button type="button" className="badge" onClick={() => scrollToHash('#top')} aria-label={t.footer.top}>
            <svg className="badge-ring" viewBox="0 0 200 200" aria-hidden="true">
              <defs><path id="badge-circle" d="M100,100 m-78,0 a78,78 0 1,1 156,0 a78,78 0 1,1 -156,0" /></defs>
              <text><textPath href="#badge-circle">{t.footer.badge.repeat(2)}</textPath></text>
            </svg>
            <Mark className="badge-mark" />
          </button>
        </div>
        <div className="foot-cols">
          <div>
            <p className="label">{t.footer.nav}</p>
            <ul>{links.map(([h, l]) => <li key={h}><a href={h} onClick={(e) => go(e, h)}>{l}</a></li>)}</ul>
          </div>
          <div>
            <p className="label">{t.footer.time}</p>
            <p><Clock /></p>
            <p className="foot-note">{t.hero.status}</p>
          </div>
          <div>
            <p className="label">{t.footer.credits}</p>
            <button type="button" className="link-btn" onClick={() => setShowCredits((v) => !v)} aria-expanded={showCredits}>Unsplash ↗</button>
            {showCredits && (
              <ul className="credits">
                <li>{t.footer.creditsText}</li>
                {credits.map((c) => <li key={c.id}><a href={c.url} target="_blank" rel="noopener noreferrer">{c.photographer}</a></li>)}
              </ul>
            )}
          </div>
        </div>
      </div>
      <p className="foot-word" ref={word} aria-label="KERN">
        {'KERN'.split('').map((ch, i) => <span key={i} aria-hidden="true">{ch}</span>)}
      </p>
      <div className="wrap foot-legal">
        <span>© 2026 KERN Studio. {t.footer.rights}</span>
        <span className="draft">{t.footer.draft}</span>
      </div>
    </footer>
  );
}
