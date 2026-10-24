// Jedan fiksni header (mockup.html, dizajn.md): boje prate aktivno poglavlje (data-chapter iz
// useActiveChapter(), prelaz --dur-base). Van početne (osim modala /p/:slug i /dev/* u dev-u) je uvek
// „page" (krem).
//   desktop (lg): logo, 5 stavki menija u sredini, EN · DE, pilula „Shop now", pretraga, korpa sa brojem
//   telefon (64 px): logo, korpa i meni (meni nosi pretragu, jezik i „Shop now")
// Širine (izmereno, EN je duži): logo ~225 px, meni ~500 px, desni deo ~330 px. Zato je meni tačno na
// sredini ekrana (mockup) tek od 90rem; ispod toga stoji na sredini između logoa i ikonica. Ispod 80rem
// (1024–1279 px) meni je zbijeniji, a pilula „Shop now" se ne prikazuje (isto sidro kao „Coffee").
// Providan je samo na vrhu stranice (scrollY ≤ 20 px). Posle toga, i tokom priče, ima pozadinu poglavlja
// (prelaz --dur-base) i liniju, jer sadržaj priče prolazi ispod njega (Z25).
// Tanka linija ispod posle 20 px skrola. Dva skip linka: sadržaj (#main) i prodavnica (#find-your-cup).
import { useCallback, useEffect, useState, type MouseEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { brand, pageHref } from '../config/site'
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { openCart, useCart } from '../lib/cart'
import { useActiveChapter } from '../lib/chapterStore'
import { scrollToTarget } from '../lib/motion'
import { Button } from './Button'
import { Icon } from './Icon'
import { LangSwitch } from './LangSwitch'
import { MobileMenu } from './MobileMenu'
import { SearchPanel } from './SearchPanel'
import './chrome.css'

const LINE_AFTER_PX = 20

/** true posle prvih 20 px skrola (linija ispod headera). */
function useScrolled() {
  const [scrolled, setScrolled] = useState(() => typeof window !== 'undefined' && window.scrollY > LINE_AFTER_PX)
  useEffect(() => {
    let frame = 0
    const update = () => {
      frame = 0
      setScrolled(window.scrollY > LINE_AFTER_PX)
    }
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      cancelAnimationFrame(frame)
    }
  }, [])
  return scrolled
}

export function Header() {
  const { tx, tf } = useLang()
  const active = useActiveChapter()
  const { count } = useCart()
  const scrolled = useScrolled()
  const { pathname } = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const closeMenu = useCallback(() => setMenuOpen(false), [])
  const closeSearch = useCallback(() => setSearchOpen(false), [])

  const onHome = pathname === '/'
  // modal proizvoda (/p/:slug) stoji preko početne, pa header i dalje prati priču; isto i dev harness-i
  // (/dev/*, samo u dev-u), da se POUR i SIP mogu porediti sa mockupom
  const overHome = onHome || pathname.startsWith('/p/') || (import.meta.env.DEV && pathname.startsWith('/dev/'))
  const chapter = overHome ? active : 'page'
  // providan samo na samom vrhu stranice (zrna padaju odozgo iza menija); čim se skroluje, i tokom
  // priče, ima pozadinu poglavlja i liniju, da tekst, mlin, talas i kartice ne idu preko menija (Z25)
  const solid = scrolled
  // na pravnim stranicama sidra vode nazad na početnu (pod base-om, npr. /Nemi/kafaskrol/#about)
  const href = (h: string) => (onHome ? h : pageHref(`/${h}`))

  // logo na početnoj vodi na vrh (Link na istu rutu ne bi ništa uradio)
  const onLogo = (e: MouseEvent) => {
    if (!onHome) return
    e.preventDefault()
    scrollToTarget(0)
  }

  return (
    <>
      <a className="skip-link" href="#main">
        {tx(site.skip.content)}
      </a>
      {onHome && (
        <a className="skip-link" href="#find-your-cup">
          {tx(site.skip.shop)}
        </a>
      )}
      <header
        data-chapter={chapter}
        data-solid={solid}
        data-scrolled={scrolled}
        className="chrome-header fixed inset-x-0 top-0 z-(--z-header) flex h-header items-center gap-s4 px-gutter text-text transition-colors duration-(--dur-base) ease-in-out"
      >
        <Link to="/" onClick={onLogo} aria-label={tf(site.logoLabel)} className="mr-auto inline-flex min-h-tap flex-col items-center justify-center leading-none no-underline">
          <span className="font-text text-logo font-semibold tracking-[.01em] whitespace-nowrap">{brand.name}</span>
          <span className="mt-[.45em] pl-(--tracking-logo-sub) font-label text-logo-sub font-bold tracking-(--tracking-logo-sub) uppercase">{tx(brand.sub)}</span>
        </Link>

        <nav
          aria-label={tx(site.aria.mainNav)}
          className="hidden lg:flex lg:min-w-0 lg:flex-1 lg:justify-center min-[90rem]:absolute min-[90rem]:left-1/2 min-[90rem]:-translate-x-1/2"
        >
          <ul className="m-0 flex list-none gap-1 p-0 xl:gap-[clamp(.5rem,1.4vw,1.75rem)]">
            {site.nav.map((item) => (
              <li key={item.href}>
                <a
                  href={href(item.href)}
                  className="inline-flex min-h-tap items-center px-1.5 font-label xl:px-2 text-label font-bold tracking-(--tracking-nav) whitespace-nowrap uppercase no-underline decoration-[1.5px] underline-offset-[6px] hover:underline"
                >
                  {tx(item.label)}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="flex items-center gap-s1">
          <LangSwitch className="max-lg:hidden" />
          <Button variant="outline" href={href(site.shopNow.href)} className="mr-s3 ml-s2 max-xl:hidden">
            {tx(site.shopNow.label)}
          </Button>
          <Button
            variant="icon"
            className="max-lg:hidden"
            aria-label={tx(site.aria.search)}
            aria-haspopup="dialog"
            aria-expanded={searchOpen}
            onClick={() => setSearchOpen(true)}
          >
            <Icon name="search" />
          </Button>
          <Button variant="icon" onClick={openCart} aria-haspopup="dialog" aria-label={count === 1 ? tx(site.aria.cartOne) : tf(site.aria.cart, { n: count })}>
            <Icon name="bag" />
            {count > 0 && (
              <span aria-hidden="true" className="chrome-badge">
                {count > 99 ? '99+' : count}
              </span>
            )}
          </Button>
          <Button variant="icon" className="lg:hidden" aria-label={tx(site.aria.menuOpen)} aria-haspopup="dialog" aria-expanded={menuOpen} onClick={() => setMenuOpen(true)}>
            <Icon name="menu" />
          </Button>
        </div>
      </header>
      <MobileMenu open={menuOpen} onClose={closeMenu} />
      <SearchPanel open={searchOpen} onClose={closeSearch} />
    </>
  )
}
