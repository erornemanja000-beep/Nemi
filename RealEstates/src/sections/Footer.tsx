import { useLayoutEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { LangToggle } from './Nav'
import { useLang } from '../i18n/LangContext'
import { photos, unsplashProfile } from '../data/photos'
import { gsap, prefersReducedMotion, scrollToTarget } from '../lib/motion'

export function Footer() {
  const { t } = useLang()
  const root = useRef<HTMLElement>(null)
  const photographers = [...new Map(Object.values(photos).map((p) => [p.user, p])).values()]

  useLayoutEffect(() => {
    if (prefersReducedMotion()) return
    const ctx = gsap.context(() => {
      gsap.fromTo('.footer-letter', { yPercent: 100 }, { yPercent: 0, stagger: 0.06, duration: 1.4, ease: 'expo.out', scrollTrigger: { trigger: '.footer-word', start: 'top 95%' } })
    }, root)
    return () => ctx.revert()
  }, [])

  return (
    <footer ref={root} className="gutter relative overflow-hidden border-t border-sand/10 pb-8 pt-20">
      <div className="grid gap-12 md:grid-cols-4">
        <div className="md:col-span-2">
          <p className="display max-w-[12ch] text-4xl md:text-5xl">{t.footer.tagline}</p>
          <div className="mt-8"><LangToggle /></div>
        </div>
        <div>
          <p className="eyebrow">{t.footer.office}</p>
          <p className="mt-4 text-sand/80">{t.footer.address}</p>
          <a href="mailto:hello@vista-estates.example" className="mt-2 block text-sand/80 hover:text-ember">hello@vista-estates.example</a>
        </div>
        <div>
          <p className="eyebrow">{t.footer.follow}</p>
          <ul className="mt-4 space-y-2 text-sand/80">
            {['Instagram', 'LinkedIn', 'Pinterest'].map((s) => (
              <li key={s}><a href="#" onClick={(e) => e.preventDefault()} className="hover:text-ember">{s} ↗</a></li>
            ))}
          </ul>
        </div>
      </div>

      <div className="footer-word mt-20 flex select-none justify-between overflow-hidden font-serif leading-[0.8] text-sand" aria-hidden="true" style={{ fontSize: 'clamp(80px, 27vw, 520px)' }}>
        {'VISTA'.split('').map((l, i) => (
          <span key={i} className="footer-letter inline-block">{l}</span>
        ))}
      </div>

      <div className="mt-10 border-t border-sand/10 pt-6 text-xs text-sand-muted">
        <p>
          {t.credits.photo}{' '}
          {photographers.map((p, i) => (
            <span key={p.user}>
              <a href={unsplashProfile(p.user)} target="_blank" rel="noreferrer" className="underline decoration-sand/20 underline-offset-2 hover:text-sand">{p.author}</a>
              {i < photographers.length - 1 ? ', ' : ' '}
            </span>
          ))}
          on <a href="https://unsplash.com/?utm_source=vista_estates&utm_medium=referral" target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-sand">Unsplash</a>.
        </p>
        <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} Vista Estates · {t.footer.rights}</p>
          <div className="flex gap-6">
            <Link to="/credits" className="hover:text-sand">{t.footer.credits}</Link>
            <button onClick={() => scrollToTarget(0)} className="hover:text-sand">{t.footer.top} ↑</button>
          </div>
        </div>
      </div>
    </footer>
  )
}
