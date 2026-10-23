// STUB iz Z1 (doradu radi Z8): jedan fiksni header, boje prate aktivno poglavlje (data-chapter).
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { brand } from '../config/site'
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { openCart, useCart } from '../lib/cart'
import { useActiveChapter } from '../lib/chapterStore'
import { Button } from './Button'
import { Icon } from './Icon'
import { LangSwitch } from './LangSwitch'
import { MobileMenu } from './MobileMenu'

export function Header() {
  const { tx, tf } = useLang()
  const chapter = useActiveChapter()
  const { count } = useCart()
  const [menuOpen, setMenuOpen] = useState(false)
  const onHome = useLocation().pathname === '/'
  // na pravnim stranicama sidra vode nazad na početnu
  const href = (h: string) => (onHome ? h : `/${h}`)

  return (
    <>
      <a className="skip-link" href="#main">{tx(site.skip.content)}</a>
      <header
        data-chapter={chapter}
        className="fixed inset-x-0 top-0 z-(--z-header) flex h-header items-center gap-s4 px-gutter text-text transition-colors duration-(--dur-base) ease-in-out"
      >
        <Link to="/" aria-label={tf(site.logoLabel)} className="mr-auto inline-flex min-h-tap flex-col items-center justify-center leading-none no-underline">
          <span className="whitespace-nowrap font-text text-logo font-semibold tracking-[.01em]">{brand.name}</span>
          <span className="mt-[.45em] pl-(--tracking-logo-sub) font-label text-logo-sub font-bold tracking-(--tracking-logo-sub) uppercase">{tx(brand.sub)}</span>
        </Link>
        <nav aria-label={tx(site.aria.mainNav)} className="absolute left-1/2 hidden -translate-x-1/2 lg:block">
          <ul className="m-0 flex list-none gap-[clamp(.5rem,1.4vw,1.75rem)] p-0">
            {site.nav.map((item) => (
              <li key={item.href}>
                <a href={href(item.href)} className="inline-flex min-h-tap items-center px-2 font-label text-label font-bold tracking-(--tracking-nav) uppercase hover:underline">
                  {tx(item.label)}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <div className="flex items-center gap-s1">
          <LangSwitch className="max-lg:hidden" />
          <Button variant="outline" href={href(site.shopNow.href)} className="mx-s2 max-lg:hidden">
            {tx(site.shopNow.label)}
          </Button>
          <Button variant="icon" onClick={openCart} aria-label={count === 1 ? tx(site.aria.cartOne) : tf(site.aria.cart, { n: count })}>
            <Icon name="bag" />
            {count > 0 && (
              <span aria-hidden="true" className="absolute top-1 right-0.5 h-[18px] min-w-[18px] rounded-pill bg-pp-ink-deep px-[5px] text-center font-label text-[11px] leading-[18px] font-bold text-pp-cream-light">
                {count}
              </span>
            )}
          </Button>
          <Button variant="icon" className="lg:hidden" aria-label={tx(site.aria.menuOpen)} aria-expanded={menuOpen} onClick={() => setMenuOpen(true)}>
            <Icon name="menu" />
          </Button>
        </div>
      </header>
      <MobileMenu open={menuOpen} onClose={() => setMenuOpen(false)} />
    </>
  )
}
