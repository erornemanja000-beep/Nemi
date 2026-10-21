import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Logo } from '../components/ui/Logo'
import { useLang } from '../i18n/LangContext'
import { gsap, lockScroll, prefersReducedMotion, scrollToTarget } from '../lib/motion'

export function LangToggle({ className = '' }: { className?: string }) {
  const { lang, setLang } = useLang()
  return (
    <div className={`flex items-center gap-1 font-mono text-[11px] tracking-[0.18em] ${className}`} role="group" aria-label="Language">
      {(['en', 'de'] as const).map((l) => (
        <button
          key={l}
          onClick={() => setLang(l)}
          aria-pressed={lang === l}
          className={`rounded-full px-2.5 py-1.5 uppercase transition-colors ${lang === l ? 'bg-sand text-ink' : 'text-sand-muted hover:text-sand'}`}
        >
          {l}
        </button>
      ))}
    </div>
  )
}

export function Nav() {
  const { t } = useLang()
  const header = useRef<HTMLElement>(null)
  const menu = useRef<HTMLDivElement>(null)
  const [open, setOpen] = useState(false)
  const [solid, setSolid] = useState(false)
  const location = useLocation()
  const onHome = location.pathname === '/' || location.pathname.startsWith('/property')

  const links = [
    ['#properties', t.nav.properties],
    ['#areas', t.nav.areas],
    ['#process', t.nav.process],
    ['#team', t.nav.team],
    ['#contact', t.nav.contact],
  ] as const

  // hide on scroll down, reveal on scroll up
  useEffect(() => {
    let last = window.scrollY
    const onScroll = () => {
      const y = window.scrollY
      setSolid(y > 80)
      if (!header.current || open) return
      const hide = y > last && y > 300
      gsap.to(header.current, { yPercent: hide ? -110 : 0, duration: 0.6, ease: 'power3.out', overwrite: true })
      last = y
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [open])

  useLayoutEffect(() => {
    if (!menu.current) return
    lockScroll(open)
    if (prefersReducedMotion()) {
      gsap.set(menu.current, { autoAlpha: open ? 1 : 0 })
      return
    }
    if (open) {
      gsap.set(menu.current, { autoAlpha: 1 })
      gsap.fromTo(menu.current, { clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)', duration: 0.9, ease: 'expo.inOut' })
      gsap.fromTo(menu.current.querySelectorAll('.menu-link'), { yPercent: 110 }, { yPercent: 0, stagger: 0.06, delay: 0.35, duration: 1 })
    } else {
      gsap.to(menu.current, { clipPath: 'inset(0 0 100% 0)', duration: 0.7, ease: 'expo.inOut', onComplete: () => gsap.set(menu.current, { autoAlpha: 0 }) })
    }
  }, [open])

  const go = (hash: string) => (e: React.MouseEvent) => {
    if (!onHome) return
    e.preventDefault()
    setOpen(false)
    scrollToTarget(hash)
  }

  return (
    <>
      <a href="#main" className="sr-only z-[120] rounded bg-sand px-4 py-2 text-ink focus:not-sr-only focus:fixed focus:left-4 focus:top-4">
        {t.nav.skip}
      </a>
      <header
        ref={header}
        className={`gutter fixed inset-x-0 top-0 z-[70] flex items-center justify-between py-4 transition-[background-color,backdrop-filter] duration-500 md:py-5 ${solid && !open ? 'bg-ink/70 backdrop-blur-md' : ''}`}
      >
        <Link to="/" aria-label="Vista Estates — home" className="text-sand" onClick={() => onHome && scrollToTarget(0)}>
          <Logo className="h-8 w-auto md:h-9" />
        </Link>
        <nav aria-label="Primary" className="hidden items-center gap-8 lg:flex">
          {links.map(([href, label]) => (
            <a key={href} href={onHome ? href : `#/${href}`} onClick={go(href)} className="group relative text-sm text-sand/85 hover:text-sand">
              {label}
              <span className="absolute -bottom-1 left-0 h-px w-full origin-right scale-x-0 bg-ember transition-transform duration-500 ease-[var(--ease-expo)] group-hover:origin-left group-hover:scale-x-100" />
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <LangToggle />
          <button
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            aria-controls="mobile-menu"
            className="flex h-11 items-center gap-3 rounded-full border border-sand/25 px-4 text-sm lg:hidden"
          >
            <span>{open ? t.nav.close : t.nav.menu}</span>
            <span className="relative block h-2.5 w-4" aria-hidden="true">
              <span className={`absolute left-0 top-0 h-px w-full bg-sand transition-transform duration-500 ${open ? 'translate-y-[5px] rotate-45' : ''}`} />
              <span className={`absolute bottom-0 left-0 h-px w-full bg-sand transition-transform duration-500 ${open ? '-translate-y-[4px] -rotate-45' : ''}`} />
            </span>
          </button>
        </div>
      </header>
      <div ref={menu} id="mobile-menu" className="gutter invisible fixed inset-0 z-[65] flex flex-col justify-end bg-stone-900 pb-12 pt-28 opacity-0 lg:hidden">
        <div className="breath left-[-20%] top-[10%] h-[60vw] w-[60vw] bg-ember" />
        <nav aria-label="Mobile" className="relative flex flex-col gap-2">
          {links.map(([href, label], i) => (
            <span key={href} className="split-mask">
              <a href={onHome ? href : `#/${href}`} onClick={go(href)} tabIndex={open ? 0 : -1} className="menu-link display block text-[13vw] leading-[1.05]">
                <span className="mr-4 align-top font-mono text-xs text-ember">0{i + 1}</span>
                {label}
              </a>
            </span>
          ))}
        </nav>
      </div>
    </>
  )
}
