// Meni na telefonu (dizajn.md: meni, pretraga i jezik idu u meni): dijalog preko celog ekrana sa
// zarobljenim fokusom i Esc (Overlay). Sadrži pretragu, 5 stavki menija, jezik i „Shop now".
// Na desktopu (lg, 64rem) ga nema: ako se prozor proširi dok je otvoren, zatvara se.
import { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { brand } from '../config/site'
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { lockScroll } from '../lib/motion'
import { Button } from './Button'
import { Icon } from './Icon'
import { LangSwitch } from './LangSwitch'
import { Overlay } from './Overlay'
import { SearchBox } from './SearchPanel'

type Props = { open: boolean; onClose: () => void }

/** Isto kao Tailwind `lg` (header prelazi na desktop raspored). */
const DESKTOP_HEADER_QUERY = '(min-width: 64rem)'

export function MobileMenu({ open, onClose }: Props) {
  const { tx } = useLang()
  const onHome = useLocation().pathname === '/'
  // na pravnim stranicama sidra vode nazad na početnu
  const href = (h: string) => (onHome ? h : `/${h}`)
  const restore = useRef(true)

  /** Zatvaranje bez vraćanja fokusa na dugme menija (link vodi dalje, fokus nastavlja odatle). */
  const closeAway = () => {
    restore.current = false
    onClose()
  }
  /** Link na sidro: skrol se otključava odmah, pre nego što pregledač (ili Lenis) skoči na sekciju. */
  const leave = () => {
    lockScroll(false)
    closeAway()
  }
  const shouldRestore = () => {
    const r = restore.current
    restore.current = true
    return r
  }

  useEffect(() => {
    if (!open) return
    const mql = window.matchMedia(DESKTOP_HEADER_QUERY)
    const onChange = () => mql.matches && onClose()
    mql.addEventListener('change', onChange)
    return () => mql.removeEventListener('change', onChange)
  }, [open, onClose])

  return (
    <Overlay open={open} onClose={onClose} label={tx(site.aria.menu)} variant="sheet" restoreFocus={shouldRestore}>
      {/* isti red kao header: logo levo, zatvaranje tačno gde je bilo dugme menija */}
      <div className="flex h-header flex-none items-center justify-between gap-s4 px-gutter">
        <span aria-hidden="true" className="inline-flex flex-col items-center leading-none">
          <span className="font-text text-logo font-semibold tracking-[.01em] whitespace-nowrap">{brand.name}</span>
          <span className="mt-[.45em] pl-(--tracking-logo-sub) font-label text-logo-sub font-bold tracking-(--tracking-logo-sub) uppercase">{tx(brand.sub)}</span>
        </span>
        <Button variant="icon" aria-label={tx(site.aria.menuClose)} onClick={onClose}>
          <Icon name="close" />
        </Button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-gutter pt-s3 pb-[calc(var(--space-7)+env(safe-area-inset-bottom))]">
        <SearchBox onPick={closeAway} />

        <nav aria-label={tx(site.aria.mainNav)} className="mt-s6">
          <ul className="m-0 list-none border-t border-line p-0">
            {site.nav.map((item) => (
              <li key={item.href} className="border-b border-line">
                <a
                  href={href(item.href)}
                  onClick={leave}
                  className="type-display flex min-h-[3.75rem] items-center text-h2 leading-none text-text no-underline"
                >
                  {tx(item.label)}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="mt-s6 flex flex-wrap items-center justify-between gap-s4">
          <LangSwitch className="-ml-2" />
          <Button href={href(site.shopNow.href)} onClick={leave}>
            {tx(site.shopNow.label)}
          </Button>
        </div>
      </div>
    </Overlay>
  )
}
