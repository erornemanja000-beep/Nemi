type Props = { className?: string; draw?: boolean; withWord?: boolean }

/** Vector redraw of the Canva-generated mark: a V whose inner strokes form a roof, with a setting sun. */
export function Logo({ className = '', draw = false, withWord = true }: Props) {
  const stroke = draw ? { strokeDasharray: 1, strokeDashoffset: 1 } : undefined
  return (
    <svg viewBox={withWord ? '0 0 352 64' : '0 0 64 64'} className={className} role="img" aria-label="Vista Estates">
      <g fill="none" stroke="currentColor" strokeLinejoin="miter">
        <path className="logo-path" pathLength={1} style={stroke} d="M6 10 L32 58 L58 10" strokeWidth="4" />
        <path className="logo-path" pathLength={1} style={stroke} d="M17 22 L32 9 L47 22" strokeWidth="2" />
        <path className="logo-path" pathLength={1} style={stroke} d="M2 10 H14 M50 10 H62" strokeWidth="2" />
      </g>
      <circle className="logo-sun" cx="32" cy="24" r="4.2" fill="#E07A3F" />
      {withWord && (
        <text x="80" y="42" fill="currentColor" fontFamily="Instrument Serif, serif" fontSize="25" letterSpacing="5.5">
          VISTA ESTATES
        </text>
      )}
    </svg>
  )
}
