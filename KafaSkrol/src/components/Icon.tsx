// SVG ikonice iz mockup.html (viewBox 24, linija 1,8–2 px, currentColor). Uvek aria-hidden:
// značenje nosi aria-label dugmeta ili tekst pored ikonice.
// close i minus nisu u mockupu; nacrtani su istim potezom za meni i korpu.
import type { ReactNode, SVGProps } from 'react'

export type IconName =
  | 'search'
  | 'bag'
  | 'menu'
  | 'close'
  | 'prev'
  | 'next'
  | 'external'
  | 'plus'
  | 'minus'
  | 'chat'
  | 'sparkle'

const line = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.8 } as const
const bold = { fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round' } as const

const icons: Record<IconName, { props: SVGProps<SVGSVGElement>; body: ReactNode }> = {
  search: { props: { ...line, strokeLinecap: 'round' }, body: <><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4.5 4.5" /></> },
  bag: { props: { ...line, strokeLinejoin: 'round' }, body: <><path d="M5 8h14l-1 12H6L5 8Z" /><path d="M9 8V6.5a3 3 0 0 1 6 0V8" /></> },
  menu: { props: { ...line, strokeLinecap: 'round' }, body: <path d="M4 8h16M4 16h16" /> },
  close: { props: { ...line, strokeLinecap: 'round' }, body: <path d="m6 6 12 12M18 6 6 18" /> },
  prev: { props: { ...line, strokeLinecap: 'round', strokeLinejoin: 'round' }, body: <path d="m14.5 5-7 7 7 7" /> },
  next: { props: { ...line, strokeLinecap: 'round', strokeLinejoin: 'round' }, body: <path d="m9.5 5 7 7-7 7" /> },
  external: { props: bold, body: <path d="M7 17 17 7M9 7h8v8" /> },
  plus: { props: bold, body: <path d="M12 5v14M5 12h14" /> },
  minus: { props: bold, body: <path d="M5 12h14" /> },
  chat: {
    props: { ...line, strokeLinejoin: 'round' },
    body: <path d="M4.5 12a7.5 7.5 0 1 1 3.4 6.3L4 19.5l1.3-3.6A7.4 7.4 0 0 1 4.5 12Z" />,
  },
  sparkle: {
    props: {},
    body: <path fill="currentColor" d="M12 0c.6 6.2 5.8 11.4 12 12-6.2.6-11.4 5.8-12 12-.6-6.2-5.8-11.4-12-12C6.2 11.4 11.4 6.2 12 0Z" />,
  },
}

type Props = { name: IconName; className?: string }

export function Icon({ name, className = 'size-[22px]' }: Props) {
  const icon = icons[name]
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" className={className} {...icon.props}>
      {icon.body}
    </svg>
  )
}
