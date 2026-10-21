import { useEffect, useRef, useState } from 'react'
import { gsap } from '../../lib/motion'
import { useFinePointer, useReducedMotion } from '../../lib/useReducedMotion'

/**
 * Dot + ring cursor. Elements can set data-cursor="View" (or any label) to grow the ring
 * and show a word inside it; data-cursor="magnet" just enlarges the ring.
 */
export function Cursor() {
  const fine = useFinePointer()
  const reduced = useReducedMotion()
  const dot = useRef<HTMLDivElement>(null)
  const ring = useRef<HTMLDivElement>(null)
  const [label, setLabel] = useState('')

  useEffect(() => {
    if (!fine || reduced) return
    document.documentElement.classList.add('has-cursor')
    const xDot = gsap.quickTo(dot.current, 'x', { duration: 0.12, ease: 'power3.out' })
    const yDot = gsap.quickTo(dot.current, 'y', { duration: 0.12, ease: 'power3.out' })
    const xRing = gsap.quickTo(ring.current, 'x', { duration: 0.55, ease: 'power3.out' })
    const yRing = gsap.quickTo(ring.current, 'y', { duration: 0.55, ease: 'power3.out' })
    let current = ''
    gsap.set([ring.current, dot.current], { xPercent: -50, yPercent: -50, opacity: 0 })
    let seen = false
    const sizeFor = (v: string) => (v && v !== 'link' && v !== 'magnet' ? 92 : v ? 64 : 40)

    const move = (e: PointerEvent) => {
      if (!seen) {
        seen = true
        gsap.set([dot.current, ring.current], { x: e.clientX, y: e.clientY })
        gsap.to([dot.current, ring.current], { opacity: 1, duration: 0.4 })
      }
      xDot(e.clientX)
      yDot(e.clientY)
      xRing(e.clientX)
      yRing(e.clientY)
      const target = (e.target as HTMLElement | null)?.closest<HTMLElement>('[data-cursor], a, button, input, textarea, select, label')
      const next = target ? target.dataset.cursor ?? 'link' : ''
      if (next !== current) {
        current = next
        const isLabel = next && next !== 'link' && next !== 'magnet'
        setLabel(isLabel ? next : '')
        gsap.to(ring.current, { width: sizeFor(next), height: sizeFor(next), backgroundColor: isLabel ? 'rgba(224,122,63,0.92)' : 'rgba(224,122,63,0)', duration: 0.5, ease: 'expo.out' })
        gsap.to(dot.current, { scale: next ? 0 : 1, duration: 0.3 })
      }
    }
    const down = () => gsap.to(ring.current, { scale: 0.85, duration: 0.2 })
    const up = () => gsap.to(ring.current, { scale: 1, duration: 0.4 })
    const leave = () => gsap.to([dot.current, ring.current], { opacity: 0, duration: 0.3 })
    const enter = () => gsap.to([dot.current, ring.current], { opacity: 1, duration: 0.3 })

    window.addEventListener('pointermove', move)
    window.addEventListener('pointerdown', down)
    window.addEventListener('pointerup', up)
    document.addEventListener('pointerleave', leave)
    document.addEventListener('pointerenter', enter)
    return () => {
      document.documentElement.classList.remove('has-cursor')
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerdown', down)
      window.removeEventListener('pointerup', up)
      document.removeEventListener('pointerleave', leave)
      document.removeEventListener('pointerenter', enter)
    }
  }, [fine, reduced])

  if (!fine || reduced) return null
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-[90]">
      <div ref={ring} className="fixed left-0 top-0 flex h-10 w-10 items-center justify-center rounded-full border border-ember/80">
        <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink">{label}</span>
      </div>
      <div ref={dot} className="fixed left-0 top-0 h-1.5 w-1.5 rounded-full bg-ember" />
    </div>
  )
}
