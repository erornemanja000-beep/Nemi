// Overlay: zajednička ljuska modalnih panela (korpa, meni, pretraga i modal proizvoda). Daje zatamnjenu
// pozadinu, role="dialog" + aria-modal, zarobljen fokus, Esc, zaključan skrol stranice (lockScroll, broji
// otvorene panele), data-lenis-prevent (panel se skroluje sam) i povratak fokusa na dugme koje je panel
// otvorilo. Izgled i ulaz/izlaz su u chrome.css (.chrome-overlay, .chrome-panel).
import { useEffect, useRef, useState, type ReactNode, type RefObject } from 'react'
import { lockScroll } from '../lib/motion'
import { isReducedMotion } from '../lib/useMedia'
import './chrome.css'

/** Trajanje izlaza panela = --dur-base (tokens.css). */
const EXIT_MS = 360

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

const focusables = (root: HTMLElement) =>
  Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter((el) => el.getClientRects().length > 0)

type OverlayProps = {
  open: boolean
  /** Esc, klik na zatamnjenu pozadinu (i dugme za zatvaranje u panelu) */
  onClose: () => void
  /** naziv dijaloga: aria-label ili id naslova u panelu */
  label?: string
  labelledBy?: string
  /** drawer = korpa (desno), sheet = meni na telefonu (ceo ekran), top = pretraga (traka odozgo) */
  variant: 'drawer' | 'sheet' | 'top'
  /** dobija fokus pri otvaranju; inače prvi fokusabilan element u panelu */
  initialFocus?: RefObject<HTMLElement | null>
  /**
   * Pita se pri zatvaranju. false kad fokus preuzima neko drugi: link na sidro (pregledač nastavlja od
   * sekcije) ili rezultat pretrage (fokus uzima modal proizvoda).
   */
  restoreFocus?: () => boolean
  className?: string
  children: ReactNode
}

export function Overlay({ open, onClose, label, labelledBy, variant, initialFocus, restoreFocus, className = '', children }: OverlayProps) {
  const panelRef = useRef<HTMLDivElement>(null)
  // panel ostaje u DOM-u dok traje izlaz (data-state="closed"), pa se skida
  const [mounted, setMounted] = useState(open)
  if (open && !mounted) setMounted(true)

  const latest = useRef({ onClose, restoreFocus, initialFocus })
  useEffect(() => {
    latest.current = { onClose, restoreFocus, initialFocus }
  })

  useEffect(() => {
    if (open || !mounted) return
    const t = window.setTimeout(() => setMounted(false), isReducedMotion() ? 0 : EXIT_MS)
    return () => window.clearTimeout(t)
  }, [open, mounted])

  useEffect(() => {
    const panel = panelRef.current
    if (!open || !panel) return
    const opener = document.activeElement instanceof HTMLElement ? document.activeElement : null
    // svaki panel drži svoje zaključavanje; ako ga je link na sidro već pustio (lockScroll(false)), unlock ne radi ništa
    const unlock = lockScroll(true)
    const first = latest.current.initialFocus?.current ?? focusables(panel)[0] ?? panel
    first.focus({ preventScroll: true })

    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        latest.current.onClose()
        return
      }
      if (e.key !== 'Tab') return
      const list = focusables(panel)
      if (list.length === 0) {
        e.preventDefault()
        panel.focus({ preventScroll: true })
        return
      }
      const active = document.activeElement
      const firstEl = list[0]
      const lastEl = list[list.length - 1]
      if (e.shiftKey && (active === firstEl || !panel.contains(active))) {
        e.preventDefault()
        lastEl.focus()
      } else if (!e.shiftKey && (active === lastEl || !panel.contains(active))) {
        e.preventDefault()
        firstEl.focus()
      }
    }
    // fokus koji ipak pobegne (klik van panela, čitač ekrana) vraća se u panel
    const onFocusIn = (e: FocusEvent) => {
      if (e.target instanceof Node && !panel.contains(e.target)) (focusables(panel)[0] ?? panel).focus({ preventScroll: true })
    }
    document.addEventListener('keydown', onKey)
    document.addEventListener('focusin', onFocusIn)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.removeEventListener('focusin', onFocusIn)
      unlock()
      if (latest.current.restoreFocus?.() !== false && opener?.isConnected) opener.focus({ preventScroll: true })
    }
  }, [open])

  if (!mounted) return null
  return (
    <div className="chrome-overlay" data-variant={variant} data-state={open ? 'open' : 'closed'} inert={!open}>
      <div className="chrome-backdrop" aria-hidden="true" onClick={onClose} />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-label={label}
        aria-labelledby={labelledBy}
        tabIndex={-1}
        className={`chrome-panel ${className}`}
        data-lenis-prevent
      >
        {children}
      </div>
    </div>
  )
}
