import { useRef, type ComponentPropsWithoutRef, type ReactNode } from 'react'
import { gsap, prefersReducedMotion } from '../../lib/motion'

type Props = {
  children: ReactNode
  href?: string
  variant?: 'solid' | 'outline' | 'ghost'
  strength?: number
  className?: string
} & Omit<ComponentPropsWithoutRef<'button'>, 'className' | 'children'>

const styles = {
  solid: 'bg-ember text-ink hover:bg-sand',
  outline: 'border border-sand/30 text-sand hover:border-sand',
  ghost: 'text-sand',
}

/** Magnetic pull toward the pointer + rolling label (after 21st.dev “Magnetic Button”). */
export function MagneticButton({ children, href, variant = 'solid', strength = 0.35, className = '', ...rest }: Props) {
  const wrap = useRef<HTMLSpanElement>(null)
  const inner = useRef<HTMLSpanElement>(null)

  const onMove = (e: React.PointerEvent) => {
    if (e.pointerType !== 'mouse' || prefersReducedMotion() || !wrap.current) return
    const r = wrap.current.getBoundingClientRect()
    const x = (e.clientX - r.left - r.width / 2) * strength
    const y = (e.clientY - r.top - r.height / 2) * strength
    gsap.to(wrap.current, { x, y, duration: 0.6, ease: 'power3.out' })
    gsap.to(inner.current, { x: x * 0.4, y: y * 0.4, duration: 0.6, ease: 'power3.out' })
  }
  const onLeave = () => {
    gsap.to([wrap.current, inner.current], { x: 0, y: 0, duration: 1, ease: 'elastic.out(1, 0.4)' })
  }

  const label = (
    <span ref={inner} className="roll">
      <span>{children}</span>
      <span aria-hidden="true">{children}</span>
    </span>
  )
  const cls = `group relative inline-flex items-center justify-center gap-2 rounded-full px-7 py-4 text-sm font-medium tracking-wide transition-colors duration-500 ${styles[variant]} ${className}`

  return (
    <span ref={wrap} className="inline-block will-change-transform" onPointerMove={onMove} onPointerLeave={onLeave} data-cursor="magnet">
      {href ? (
        <a href={href} className={cls}>
          {label}
        </a>
      ) : (
        <button className={cls} {...rest}>
          {label}
        </button>
      )}
    </span>
  )
}
