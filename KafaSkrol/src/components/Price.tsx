// Cena sa Grundpreisom u istom redu i napomenom o PDV-u (PAngV/PrAG, tekstovi.md):
//   € 17,90 · 250 g · € 71,60/kg
//   inkl. MwSt., zzgl. Versand
// Grundpreis se uvek računa iz cene i grama (format.ts), nikad se ne upisuje.
import { shop } from '../content/shop'
import { useLang } from '../i18n/LangContext'
import { formatGrams, formatPrice, formatUnitPrice } from '../lib/format'

type Props = {
  cents: number
  /** grami pakovanja; bez njih (oprema) nema Grundpreisa */
  grams?: number
  /** prikaži i veličinu pakovanja („250 g") ispred Grundpreisa */
  showGrams?: boolean
  /** full = „incl. VAT, plus shipping", short = „incl. VAT", none = bez napomene */
  note?: 'full' | 'short' | 'none'
  className?: string
  /** klase za iznos (veličina i debljina zavise od mesta) */
  amountClassName?: string
}

export function Price({ cents, grams, showGrams = false, note = 'full', className = '', amountClassName = 'text-[1.25rem] font-extrabold' }: Props) {
  const { lang, tx } = useLang()
  const unit = grams ? [showGrams ? formatGrams(grams, lang) : null, formatUnitPrice(cents, grams, lang)].filter(Boolean).join(' · ') : null
  return (
    <p className={`m-0 leading-[1.2] ${className}`}>
      <span className="flex flex-wrap items-baseline gap-x-2">
        <strong className={`whitespace-nowrap leading-[1.1] ${amountClassName}`}>{formatPrice(cents, lang)}</strong>
        {unit && <span className="whitespace-nowrap text-micro">{unit}</span>}
      </span>
      {note !== 'none' && <span className="mt-[3px] block text-micro">{tx(shop.priceNote[note])}</span>}
    </p>
  )
}
