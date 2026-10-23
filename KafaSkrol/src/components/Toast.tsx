// STUB iz Z1 (doradu radi Z8): poruka posle „Add to cart", aria-live="polite".
import { useEffect } from 'react'
import { shop } from '../content/shop'
import { useLang } from '../i18n/LangContext'
import { clearToast, useToast } from '../lib/cart'

export function Toast() {
  const { tx } = useLang()
  const toast = useToast()
  useEffect(() => {
    if (!toast) return
    const t = window.setTimeout(clearToast, 4000)
    return () => window.clearTimeout(t)
  }, [toast])
  return (
    <div aria-live="polite" className="pointer-events-none fixed inset-x-0 bottom-s6 z-(--z-chat) flex justify-center px-gutter">
      {toast && <p className="m-0 rounded-pill bg-pp-ink-deep px-s5 py-s3 text-small text-pp-cream-light shadow-float">{tx(shop.cart.toast)}</p>}
    </div>
  )
}
