// Dugmad iz mockup.html:
//   solid   = .btn (tamna pilula, CTA poglavlja i sekcija; prsten na obojenim poglavljima)
//   outline = .pill (pilula u headeru, boje prate data-chapter)
//   round   = .glass-card__add (okruglo 44 px, „+" na kartici)
//   icon    = .icon-btn (44 px, pretraga, korpa, meni)
// Sa `href` je <a>, sa `to` je <Link> (ruta u aplikaciji), inače <button type="button">.
import type { ComponentPropsWithRef, ReactNode } from 'react'
import { Link } from 'react-router-dom'

export type ButtonVariant = 'solid' | 'outline' | 'round' | 'icon'

const label = 'font-label text-label font-bold leading-none tracking-(--tracking-button) uppercase no-underline'

const variants: Record<ButtonVariant, string> = {
  solid:
    `inline-flex items-center gap-[.6em] min-h-12 px-7 rounded-pill bg-btn text-btn-text ${label} ` +
    'shadow-[0_0_0_1px_var(--color-btn-ring),var(--shadow-btn)] cursor-pointer ' +
    'transition-[translate,background-color] duration-(--dur-fast) ease-out hover:-translate-y-px motion-reduce:hover:translate-y-0 ' +
    'disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0 [&_svg]:size-4',
  outline:
    `inline-flex items-center justify-center min-h-tap px-[1.6rem] rounded-pill border-[1.5px] border-pill-border bg-pill text-pill-text ${label} ` +
    'cursor-pointer transition-colors duration-(--dur-fast) ease-out',
  round:
    'grid place-items-center size-tap flex-none rounded-full border-0 bg-pp-ink-deep text-pp-cream-light shadow-btn cursor-pointer ' +
    'disabled:cursor-not-allowed disabled:opacity-60 [&_svg]:size-[18px]',
  icon: 'relative inline-grid place-items-center size-tap rounded-pill border-0 bg-transparent cursor-pointer no-underline [&_svg]:size-[22px]',
}

/** Klase dugmeta, za elemente koji nisu Button (npr. <label> ili <summary>). */
// oxlint-disable-next-line react/only-export-components -- klase se dele sa <Link> i <label>
export const buttonClass = (variant: ButtonVariant = 'solid', extra = '') => `${variants[variant]} ${extra}`.trim()

type Base = { variant?: ButtonVariant; className?: string; children: ReactNode }
type AsButton = Base & Omit<ComponentPropsWithRef<'button'>, 'className' | 'children'> & { href?: never; to?: never }
type AsAnchor = Base & Omit<ComponentPropsWithRef<'a'>, 'className' | 'children'> & { href: string; to?: never }
type AsLink = Base & Omit<ComponentPropsWithRef<typeof Link>, 'className' | 'children'> & { to: string; href?: never }

export type ButtonProps = AsButton | AsAnchor | AsLink

export function Button(props: ButtonProps) {
  const { variant = 'solid', className = '', children, ...rest } = props
  const cls = buttonClass(variant, className)
  if (rest.to !== undefined) {
    return (
      <Link {...(rest as Omit<AsLink, keyof Base>)} className={cls}>
        {children}
      </Link>
    )
  }
  if (rest.href !== undefined) {
    return (
      <a {...(rest as Omit<AsAnchor, keyof Base>)} className={cls}>
        {children}
      </a>
    )
  }
  return (
    <button type="button" {...(rest as Omit<AsButton, keyof Base>)} className={cls}>
      {children}
    </button>
  )
}
