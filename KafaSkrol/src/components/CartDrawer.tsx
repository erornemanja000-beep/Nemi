// STUB iz Z1 (doradu radi Z8): stavke, +/−, međuzbir, dostava, ukupno, onemogućeno dugme porudžbine.
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { closeCart, useCart } from '../lib/cart'
import { formatPrice } from '../lib/format'
import { Button } from './Button'
import { Icon } from './Icon'

export function CartDrawer() {
  const { lang, tx } = useLang()
  const cart = useCart()
  if (!cart.open) return null
  return (
    <div role="dialog" aria-modal="true" aria-label={tx(site.aria.cartTitle)} className="fixed inset-y-0 right-0 z-(--z-chat) w-[min(100%,26rem)] bg-surface p-gutter text-text shadow-float" data-lenis-prevent>
      <div className="flex justify-end">
        <Button variant="icon" aria-label={tx(site.aria.close)} onClick={closeCart}>
          <Icon name="close" />
        </Button>
      </div>
      <p>{cart.count} · {formatPrice(cart.totalCents, lang)}</p>
    </div>
  )
}
