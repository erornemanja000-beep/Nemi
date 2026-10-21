import { createElement, useLayoutEffect, useRef, type ElementType } from 'react'
import { gsap, prefersReducedMotion } from '../../lib/motion'

type Props = {
  text: string
  as?: ElementType
  className?: string
  /** 'scroll' reveals when the element enters the viewport; 'manual' waits for a `vista:reveal` event on window. */
  trigger?: 'scroll' | 'manual'
  delay?: number
  stagger?: number
  italicWords?: number[]
  id?: string
}

/** Masked word-by-word reveal (pattern after 21st.dev “Vertical Cut Reveal” / paceui “Reveal Text”, rebuilt on GSAP). */
export function SplitText({ text, as = 'h2', className, trigger = 'scroll', delay = 0, stagger = 0.06, italicWords = [], id }: Props) {
  const ref = useRef<HTMLElement>(null)

  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    const words = el.querySelectorAll<HTMLElement>('.split-word')
    if (prefersReducedMotion()) {
      gsap.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.6, scrollTrigger: trigger === 'scroll' ? { trigger: el, start: 'top 90%' } : undefined })
      return
    }
    const ctx = gsap.context(() => {
      gsap.set(words, { yPercent: 110, rotate: 4 })
      const play = () => gsap.to(words, { yPercent: 0, rotate: 0, duration: 1.2, stagger, delay, ease: 'expo.out' })
      if (trigger === 'scroll') {
        gsap.to(words, { yPercent: 0, rotate: 0, duration: 1.2, stagger, delay, ease: 'expo.out', scrollTrigger: { trigger: el, start: 'top 85%' } })
      } else {
        window.addEventListener('vista:reveal', play, { once: true })
        return () => window.removeEventListener('vista:reveal', play)
      }
    }, el)
    return () => ctx.revert()
  }, [text, trigger, delay, stagger])

  const parts = text.split(' ')
  return createElement(
    as,
    { ref, id, className, 'aria-label': text },
    parts.map((w, i) => (
      <span key={i} className="split-mask" aria-hidden="true">
        <span className={`split-word${italicWords.includes(i) ? ' italic' : ''}`}>{w}</span>
        {i < parts.length - 1 ? ' ' : ''}
      </span>
    )),
  )
}
