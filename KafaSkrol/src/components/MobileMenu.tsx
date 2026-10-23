// STUB iz Z1 (doradu radi Z8: dijalog sa zarobljenim fokusom, Esc, pretraga, jezik, „Shop now").
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { Button } from './Button'
import { Icon } from './Icon'
import { LangSwitch } from './LangSwitch'

type Props = { open: boolean; onClose: () => void }

export function MobileMenu({ open, onClose }: Props) {
  const { tx } = useLang()
  if (!open) return null
  return (
    <div role="dialog" aria-modal="true" aria-label={tx(site.aria.menu)} className="fixed inset-0 z-(--z-chat) bg-surface p-gutter text-text" data-lenis-prevent>
      <div className="flex justify-end">
        <Button variant="icon" aria-label={tx(site.aria.menuClose)} onClick={onClose}>
          <Icon name="close" />
        </Button>
      </div>
      <ul className="m-0 list-none p-0">
        {site.nav.map((item) => (
          <li key={item.href}>
            <a href={item.href} onClick={onClose} className="flex min-h-tap items-center font-label text-label font-bold tracking-(--tracking-nav) uppercase">
              {tx(item.label)}
            </a>
          </li>
        ))}
      </ul>
      <LangSwitch />
    </div>
  )
}
