import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useLang } from '../i18n.jsx';
import { Logo } from './Logo.jsx';
import { Magnetic, Scramble, Arrow } from './fx.jsx';
import { scrollToHash, lockScroll } from '../hooks/useSmoothScroll.js';

export default function Nav() {
  const { t, toggle } = useLang();
  const [hidden, setHidden] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let last = window.scrollY;
    const on = () => {
      const y = window.scrollY;
      setScrolled(y > 40);
      if (Math.abs(y - last) > 6) { setHidden(y > last && y > 160); last = y; }
    };
    window.addEventListener('scroll', on, { passive: true });
    return () => window.removeEventListener('scroll', on);
  }, []);

  useEffect(() => {
    lockScroll(open);
    document.documentElement.classList.toggle('menu-open', open);
    const esc = (e) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('keydown', esc);
    return () => window.removeEventListener('keydown', esc);
  }, [open]);

  const links = [
    { href: '#work', label: t.nav.work, sup: '06' },
    { href: '#services', label: t.nav.services, sup: '06' },
    { href: '#process', label: t.nav.process, sup: '04' },
    { href: '#faq', label: t.nav.faq },
  ];
  const go = (e, href) => { e.preventDefault(); setOpen(false); setTimeout(() => scrollToHash(href), open ? 350 : 0); };

  return (
    <>
      <header className={`nav${hidden && !open ? ' is-hidden' : ''}${scrolled ? ' is-scrolled' : ''}`}>
        <a className="nav-logo" href="#top" onClick={(e) => go(e, '#top')} aria-label="KERN">
          <Logo />
        </a>
        <nav className="nav-links" aria-label="Main">
          {links.map((l) => (
            <a key={l.href} href={l.href} onClick={(e) => go(e, l.href)}>
              <Scramble text={l.label} />{l.sup && <sup>{l.sup}</sup>}
            </a>
          ))}
        </nav>
        <div className="nav-end">
          <button className="nav-lang" type="button" onClick={toggle} aria-label={t.nav.langLabel}>{t.nav.lang}</button>
          <Magnetic strength={0.25}>
            <a className="btn btn-accent nav-cta" href="#contact" onClick={(e) => go(e, '#contact')}>
              {t.nav.contact}<Arrow />
            </a>
          </Magnetic>
          <button className={`nav-burger${open ? ' is-open' : ''}`} type="button" onClick={() => setOpen((v) => !v)} aria-expanded={open} aria-controls="mobile-menu" aria-label={open ? t.nav.close : t.nav.menu}>
            <span /><span />
          </button>
        </div>
      </header>

      <AnimatePresence>
        {open && (
          <motion.div
            id="mobile-menu"
            className="menu"
            initial={{ clipPath: 'inset(0 0 100% 0)' }}
            animate={{ clipPath: 'inset(0 0 0% 0)' }}
            exit={{ clipPath: 'inset(0 0 100% 0)' }}
            transition={{ duration: 0.7, ease: [0.76, 0, 0.24, 1] }}
          >
            <nav className="menu-links">
              {[...links, { href: '#contact', label: t.nav.contact }].map((l, i) => (
                <div className="menu-line" key={l.href}>
                  <motion.a
                    href={l.href}
                    onClick={(e) => go(e, l.href)}
                    initial={{ y: '110%' }}
                    animate={{ y: 0 }}
                    exit={{ y: '110%' }}
                    transition={{ duration: 0.7, delay: 0.15 + i * 0.06, ease: [0.16, 1, 0.3, 1] }}
                  >
                    <span className="label">{String(i + 1).padStart(2, '0')}</span>{l.label}
                  </motion.a>
                </div>
              ))}
            </nav>
            <button className="menu-lang" type="button" onClick={toggle}>{t.nav.lang}</button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
