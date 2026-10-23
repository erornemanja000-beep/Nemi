// Pretraga kafa i opreme po imenu, poreklu i notama, uvek na oba jezika (DE „Äthiopien" i EN
// „Ethiopia" nalaze Guji, bez obzira na izabrani jezik). Rezultat vodi na /p/<slug>.
// Broj rezultata i prazan rezultat čita čitač ekrana (role="status").
//   SearchBox:   polje i rezultati (koristi ga i meni na telefonu)
//   SearchPanel: traka odozgo na desktopu (dugme „Open search" u headeru)
import { useId, useMemo, useRef, useState, type ReactNode, type Ref } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { products } from '../content/products'
import { shop } from '../content/shop'
import { site } from '../content/site'
import type { Product } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { Button } from './Button'
import { Icon } from './Icon'
import { Overlay } from './Overlay'
import { Price } from './Price'

/** Mala slova, bez akcenata i umlauta (ä → a, ú → u), ß → ss. */
const normalize = (s: string) => s.normalize('NFD').replace(/\p{M}/gu, '').replace(/ß/g, 'ss').toLowerCase()

/** Prodavnica prikazuje samo proizvode sa cenom (PrAG); pretraga isto. */
const listed = products.filter((p) => p.sizes.length > 0 || p.priceCents != null)

const index = listed.map((p) => ({
  product: p,
  text: normalize(
    [p.name, p.shortName, p.origin]
      .flatMap((v) => (v ? [v.en, v.de] : []))
      .concat(p.notes ? [...p.notes.en, ...p.notes.de] : [])
      .join(' | '),
  ),
}))

/** Svaka reč upita mora da se nađe (u bilo kom polju, na bilo kom jeziku). */
function search(query: string): Product[] {
  const terms = normalize(query).split(/\s+/).filter(Boolean)
  if (terms.length === 0) return []
  return index.filter((e) => terms.every((t) => e.text.includes(t))).map((e) => e.product)
}

type BoxProps = {
  /** zatvara panel ili meni kad je rezultat izabran (fokus tada uzima modal proizvoda) */
  onPick: () => void
  inputRef?: Ref<HTMLInputElement>
  /** dugme pored polja (zatvaranje panela) */
  action?: ReactNode
  className?: string
  /** klase liste rezultata (u panelu se lista skroluje sama) */
  listClassName?: string
}

export function SearchBox({ onPick, inputRef, action, className = '', listClassName = '' }: BoxProps) {
  const { tx, tf } = useLang()
  const navigate = useNavigate()
  const id = useId()
  const [query, setQuery] = useState('')
  const results = useMemo(() => search(query), [query])
  const q = query.trim()
  const status = !q
    ? ''
    : results.length === 0
      ? tf(site.search.empty, { q })
      : results.length === 1
        ? tx(site.search.resultOne)
        : tf(site.search.results, { n: results.length })

  const typeLabel = (p: Product) => shop.filters.type.options.find((o) => o.id === p.type)?.label

  return (
    <div className={`flex min-h-0 flex-col ${className}`}>
      <form
        role="search"
        className="flex items-center gap-s2"
        onSubmit={(e) => {
          // Enter otvara prvi rezultat
          e.preventDefault()
          if (!results[0]) return
          onPick()
          navigate(`/p/${results[0].slug}`)
        }}
      >
        <label htmlFor={`${id}-q`} className="sr-only">
          {tx(site.search.placeholder)}
        </label>
        <div className="relative min-w-0 flex-1">
          <Icon name="search" className="pointer-events-none absolute top-1/2 left-s4 size-5 -translate-y-1/2 text-muted" />
          <input
            ref={inputRef}
            id={`${id}-q`}
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={tx(site.search.placeholder)}
            autoComplete="off"
            spellCheck={false}
            enterKeyHint="search"
            aria-describedby={`${id}-status`}
            aria-controls={`${id}-results`}
            className="chrome-search h-12 w-full rounded-pill border-[1.5px] border-line-strong bg-transparent pr-s4 pl-12 font-text text-body text-text placeholder:text-muted"
          />
        </div>
        {action}
      </form>

      <p id={`${id}-status`} role="status" className="m-0 mt-s3 px-s2 text-small text-muted empty:mt-0">
        {status}
      </p>

      <ul id={`${id}-results`} className={`m-0 mt-s2 list-none p-0 empty:hidden ${listClassName}`}>
        {results.map((p) => {
          const size = p.sizes[0]
          const cents = size?.priceCents ?? p.priceCents
          const meta = p.origin ? tx(p.origin) : tx(typeLabel(p) ?? p.name)
          return (
            <li key={p.slug}>
              <Link
                to={`/p/${p.slug}`}
                onClick={onPick}
                className="flex min-h-tap items-center justify-between gap-s4 rounded-md px-s2 py-s3 text-text no-underline hover:bg-bg focus-visible:bg-bg"
              >
                <span className="min-w-0">
                  <span className="block font-bold">{tx(p.name)}</span>
                  <span className="block text-small text-muted">{meta}</span>
                  {p.notes && <span className="block text-small text-muted">{tx(p.notes).join(', ')}</span>}
                </span>
                {cents != null && (
                  <Price
                    cents={cents}
                    grams={size?.grams}
                    showGrams={!!size}
                    note="none"
                    className="flex-none text-right text-muted [&>span]:justify-end"
                    amountClassName="text-body font-bold text-text"
                  />
                )}
              </Link>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

type Props = { open: boolean; onClose: () => void }

export function SearchPanel({ open, onClose }: Props) {
  const { tx } = useLang()
  const inputRef = useRef<HTMLInputElement>(null)
  const restore = useRef(true)
  const shouldRestore = () => {
    const r = restore.current
    restore.current = true
    return r
  }

  return (
    <Overlay open={open} onClose={onClose} label={tx(site.search.placeholder)} variant="top" initialFocus={inputRef} restoreFocus={shouldRestore}>
      <SearchBox
        inputRef={inputRef}
        onPick={() => {
          restore.current = false
          onClose()
        }}
        className="mx-auto w-full max-w-[48rem] px-gutter pt-s5 pb-s6"
        listClassName="min-h-0 overflow-y-auto"
        action={
          <Button variant="icon" aria-label={tx(site.aria.close)} onClick={onClose}>
            <Icon name="close" />
          </Button>
        }
      />
    </Overlay>
  )
}
