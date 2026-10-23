// Kratka poruka dole na sredini (posle „Add to cart" i demo dugmadi), u regionu aria-live="polite".
// Region je uvek u DOM-u, a poruka se menja: čitač je pročita, i istu poruku dva puta zaredom (novi id).
// Posle 4 s bledi i nestaje. Na telefonu stoji iznad chat balona, da ga ne pokrije.
import { useEffect, useState } from 'react'
import { shop } from '../content/shop'
import type { L } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { clearToast, useToast } from '../lib/cart'
import { isReducedMotion } from '../lib/useMedia'
import './chrome.css'

const VISIBLE_MS = 4000
/** = --dur-fast (izlaz) */
const LEAVE_MS = 200

function ToastItem({ text }: { text: string }) {
  const [leaving, setLeaving] = useState(false)
  useEffect(() => {
    const t1 = window.setTimeout(() => setLeaving(true), VISIBLE_MS)
    const t2 = window.setTimeout(clearToast, VISIBLE_MS + (isReducedMotion() ? 0 : LEAVE_MS))
    return () => {
      window.clearTimeout(t1)
      window.clearTimeout(t2)
    }
  }, [])
  return (
    <p
      data-leaving={leaving}
      className="chrome-toast m-0 max-w-[28rem] rounded-card bg-pp-ink-deep px-s5 py-s3 text-center text-small text-pp-cream-light shadow-float"
    >
      {text}
    </p>
  )
}

export function Toast() {
  const { tx } = useLang()
  const toast = useToast()
  const message: L | null = !toast ? null : toast.message === 'added' ? shop.cart.toast : toast.message
  return (
    <div
      role="status"
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 bottom-[calc(var(--space-4)+3.25rem+var(--space-3)+env(safe-area-inset-bottom))] z-[calc(var(--z-chat)+20)] flex justify-center px-gutter lg:bottom-s6"
    >
      {toast && message && <ToastItem key={toast.id} text={tx(message)} />}
    </div>
  )
}
