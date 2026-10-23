// Chat balon dole desno (mockup .chat): pojavljuje se posle 3 s (u mirnoj verziji odmah), bez zvuka i bez
// samostalnog otvaranja (mapa-skrola). Otvara mali demo panel (nemodalan dijalog): Esc ili klik van
// njega ga zatvara i fokus se vraća na balon. Paneli headera (korpa, meni, pretraga) su iznad balona.
import { useEffect, useRef, useState } from 'react'
import { brand, fill } from '../config/site'
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { useReducedMotion } from '../lib/useMedia'
import { Button } from './Button'
import { Icon } from './Icon'
import './chrome.css'

const SHOW_AFTER_MS = 3000

export function ChatBubble() {
  const { tx } = useLang()
  const reduced = useReducedMotion()
  const [timerDone, setTimerDone] = useState(false)
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const bubbleRef = useRef<HTMLButtonElement>(null)
  const closeRef = useRef<HTMLButtonElement>(null)
  const shown = reduced || timerDone

  useEffect(() => {
    const t = window.setTimeout(() => setTimerDone(true), SHOW_AFTER_MS)
    return () => window.clearTimeout(t)
  }, [])

  useEffect(() => {
    if (!open) return
    closeRef.current?.focus({ preventScroll: true })
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return
      setOpen(false)
      bubbleRef.current?.focus({ preventScroll: true })
    }
    const onPointer = (e: PointerEvent) => {
      if (e.target instanceof Node && !rootRef.current?.contains(e.target)) setOpen(false)
    }
    document.addEventListener('keydown', onKey)
    document.addEventListener('pointerdown', onPointer)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.removeEventListener('pointerdown', onPointer)
    }
  }, [open])

  // {email} postaje mailto link; ostatak rečenice ide kroz fill() ({brand}…)
  const [before, after = ''] = tx(site.chat.panel).split('{email}')

  return (
    <div
      ref={rootRef}
      data-shown={shown}
      className="chrome-chat fixed right-s4 bottom-[calc(var(--space-4)+env(safe-area-inset-bottom))] z-(--z-chat) lg:right-gutter lg:bottom-s6"
    >
      {open && (
        <div
          id="chat-panel"
          role="dialog"
          aria-labelledby="chat-title"
          className="chrome-chat-panel absolute right-0 bottom-[calc(100%+var(--space-3))] w-[min(calc(100vw-2*var(--space-4)),20rem)] rounded-card bg-surface p-s5 pt-s3 pr-s2 text-text shadow-float"
        >
          <div className="flex items-center justify-between gap-s2">
            <h2 id="chat-title" className="m-0 text-body font-bold">{tx(site.chat.tooltip)}</h2>
            <Button
              ref={closeRef}
              variant="icon"
              aria-label={tx(site.aria.close)}
              onClick={() => {
                setOpen(false)
                bubbleRef.current?.focus({ preventScroll: true })
              }}
            >
              <Icon name="close" />
            </Button>
          </div>
          <p className="m-0 mt-s1 pr-s3 text-small">
            {fill(before)}
            <a href={`mailto:${brand.email}`} className="font-bold whitespace-nowrap text-accent-text underline underline-offset-2">
              {brand.email}
            </a>
            {fill(after)}
          </p>
        </div>
      )}

      <button
        ref={bubbleRef}
        type="button"
        aria-label={tx(site.chat.open)}
        aria-expanded={open}
        aria-controls={open ? 'chat-panel' : undefined}
        aria-describedby={open ? undefined : 'chat-tip'}
        onClick={() => setOpen((v) => !v)}
        className="chrome-chat-btn grid size-13 cursor-pointer place-items-center rounded-full border-0 bg-pp-ink-deep text-pp-cream-light shadow-float lg:size-14"
      >
        <Icon name={open ? 'close' : 'chat'} />
      </button>
      {!open && (
        <span
          id="chat-tip"
          className="chrome-chat-tip pointer-events-none absolute top-1/2 right-[calc(100%+var(--space-3))] -translate-y-1/2 rounded-pill bg-pp-ink-deep px-s4 py-s2 text-small whitespace-nowrap text-pp-cream-light shadow-soft"
        >
          {tx(site.chat.tooltip)}
        </span>
      )}
    </div>
  )
}
