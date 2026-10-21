import { useLayoutEffect, useRef } from 'react'
import { gsap, prefersReducedMotion } from '../../lib/motion'

type Props = { value: number; decimals?: number; prefix?: string; suffix?: string; locale: string }

export function Counter({ value, decimals = 0, prefix = '', suffix = '', locale }: Props) {
  const ref = useRef<HTMLSpanElement>(null)
  const fmt = (n: number) => prefix + n.toLocaleString(locale, { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + suffix

  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    if (prefersReducedMotion()) {
      el.textContent = fmt(value)
      return
    }
    const obj = { n: 0 }
    el.textContent = fmt(0)
    const tween = gsap.to(obj, {
      n: value,
      duration: 2.4,
      ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 88%' },
      onUpdate: () => {
        el.textContent = fmt(obj.n)
      },
    })
    return () => {
      tween.scrollTrigger?.kill()
      tween.kill()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, locale])

  return (
    <span ref={ref} aria-label={fmt(value)}>
      {fmt(value)}
    </span>
  )
}
