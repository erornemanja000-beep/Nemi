import { useEffect, useMemo, useRef, useState } from 'react'
import { SplitText } from '../components/ui/SplitText'
import { formatPrice, useLang } from '../i18n/LangContext'
import { gsap, prefersReducedMotion } from '../lib/motion'

type SliderProps = { id: string; label: string; value: number; min: number; max: number; step: number; display: string; onChange: (v: number) => void }

function Slider({ id, label, value, min, max, step, display, onChange }: SliderProps) {
  const fill = ((value - min) / (max - min)) * 100
  return (
    <div className="border-t border-sand/15 py-6">
      <div className="mb-5 flex items-baseline justify-between gap-4">
        <label htmlFor={id} className="text-sm text-sand-muted">{label}</label>
        <output htmlFor={id} className="font-serif text-2xl tabular-nums md:text-3xl">{display}</output>
      </div>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} style={{ '--fill': `${fill}%` } as React.CSSProperties} data-cursor="Drag" />
    </div>
  )
}

export function Mortgage() {
  const { t, lang } = useLang()
  const [price, setPrice] = useState(3200000)
  const [down, setDown] = useState(30)
  const [years, setYears] = useState(25)
  const [rate, setRate] = useState(3.6)
  const out = useRef<HTMLSpanElement>(null)
  const shown = useRef({ v: 0 })
  const locale = lang === 'de' ? 'de-DE' : 'en-GB'

  const { monthly, totalInterest, loan } = useMemo(() => {
    const loan = price * (1 - down / 100)
    const r = rate / 100 / 12
    const n = years * 12
    const monthly = r === 0 ? loan / n : (loan * r) / (1 - Math.pow(1 + r, -n))
    return { monthly, loan, totalInterest: monthly * n - loan }
  }, [price, down, years, rate])

  useEffect(() => {
    gsap.to(shown.current, {
      v: monthly,
      duration: prefersReducedMotion() ? 0 : 0.9,
      ease: 'power3.out',
      overwrite: true,
      onUpdate: () => {
        if (out.current) out.current.textContent = formatPrice(shown.current.v, lang)
      },
    })
  }, [monthly, lang])

  const share = loan / (loan + totalInterest)
  const C = 2 * Math.PI * 46

  return (
    <section id="mortgage" aria-labelledby="mortgage-title" className="gutter section-y relative overflow-hidden">
      <div className="breath right-[-10%] top-[10%] h-[45vw] w-[45vw] bg-dusk" />
      <p className="eyebrow">{t.mortgage.eyebrow}</p>
      <SplitText as="h2" id="mortgage-title" text={t.mortgage.title} className="display mt-6 max-w-[14ch] text-5xl md:text-7xl" />
      <div className="relative mt-16 grid gap-12 md:mt-20 md:grid-cols-[1.2fr_1fr] md:gap-[6vw]">
        <div>
          <Slider id="m-price" label={t.mortgage.price} value={price} min={500000} max={10000000} step={50000} display={formatPrice(price, lang)} onChange={setPrice} />
          <Slider id="m-down" label={t.mortgage.down} value={down} min={10} max={70} step={1} display={`${down}% · ${formatPrice((price * down) / 100, lang)}`} onChange={setDown} />
          <Slider id="m-years" label={t.mortgage.years} value={years} min={5} max={35} step={1} display={`${years} ${t.mortgage.yearsUnit}`} onChange={setYears} />
          <Slider id="m-rate" label={t.mortgage.rate} value={rate} min={1} max={8} step={0.1} display={`${rate.toLocaleString(locale, { minimumFractionDigits: 1 })}%`} onChange={setRate} />
        </div>
        <div className="flex flex-col items-start justify-center rounded-[2px] border border-sand/15 bg-stone-900/70 p-8 backdrop-blur md:p-12">
          <p className="eyebrow">{t.mortgage.monthly}</p>
          <p className="mt-4 font-serif text-[16vw] leading-none text-sand tabular-nums md:text-[5.4vw]" aria-live="polite">
            <span ref={out}>{formatPrice(monthly, lang)}</span>
          </p>
          <div className="mt-10 flex w-full items-center gap-8">
            <svg viewBox="0 0 100 100" className="h-28 w-28 shrink-0 -rotate-90" aria-hidden="true">
              <circle cx="50" cy="50" r="46" fill="none" stroke="#e07a3f" strokeWidth="6" />
              <circle cx="50" cy="50" r="46" fill="none" stroke="#c8a46a" strokeWidth="6" strokeDasharray={C} strokeDashoffset={C * (1 - share)} style={{ transition: 'stroke-dashoffset 1s cubic-bezier(.16,1,.3,1)' }} />
            </svg>
            <dl className="grid gap-3 text-sm">
              <div className="flex items-center gap-3"><span className="h-2 w-2 rounded-full bg-gold" /><dt className="text-sand-muted">{t.mortgage.principal}</dt><dd className="ml-auto tabular-nums">{formatPrice(loan, lang)}</dd></div>
              <div className="flex items-center gap-3"><span className="h-2 w-2 rounded-full bg-ember" /><dt className="text-sand-muted">{t.mortgage.total}</dt><dd className="ml-auto tabular-nums">{formatPrice(totalInterest, lang)}</dd></div>
            </dl>
          </div>
          <p className="mt-8 text-xs text-sand-muted">{t.mortgage.note}</p>
        </div>
      </div>
    </section>
  )
}
