// Footer (skica: sekcija 11). Tamna traka u ulogama SIP poglavlja (data-chapter="sip": espresso,
// svetao krem tekst; kontrasti su u dizajn.md). Redom:
//   1. newsletter: samo e-mail i kućica koja nije štiklirana; greške preko aria-describedby, uspeh je
//      demo poruka (role="status"). Ništa se ne šalje: nema action-a ni mrežnog zahteva.
//   2. logo i jezik, pa tri kolone linkova iz sections.footer (telefon: logo preko cele širine, kolone u dve).
//   3. dugme „Vertrag widerrufen" na /widerruf i mesto za Gewährleistungslabel (obeležen placeholder),
//      pa stalna napomena „Konzept / Demo", copyright i Credits.
// Razmak ispod je ≥ 72 px (--space-9 = 96 px), da chat balon ne pokrije poslednje dugme.
// Sidra (#about…) vode na početnu kad footer stoji na pravnoj stranici, kao u headeru.
import { useId, useState, type ChangeEvent, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Button } from '../components/Button'
import { LangSwitch } from '../components/LangSwitch'
import { brand } from '../config/site'
import { credits } from '../content/legal'
import { sections } from '../content/sections'
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'

const footer = sections.footer
const nl = footer.newsletter

/** Ista provera kao forma u RealEstates: nešto@nešto.xx, bez razmaka. */
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

const linkClass = 'inline-flex min-h-tap items-center no-underline hover:underline underline-offset-[3px]'

type Field = 'email' | 'consent'

function Newsletter() {
  const { tx } = useLang()
  const id = useId()
  const ids = { title: `${id}-t`, email: `${id}-e`, emailErr: `${id}-ee`, consentErr: `${id}-ce` }
  const [errors, setErrors] = useState<Record<Field, boolean>>({ email: false, consent: false })
  const [sent, setSent] = useState(false)

  const submit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    const data = new FormData(form)
    const next = {
      email: !EMAIL_RE.test(String(data.get('email') ?? '').trim()),
      consent: data.get('consent') === null,
    }
    setErrors(next)
    const first = (Object.keys(next) as Field[]).find((k) => next[k])
    if (first) {
      setSent(false)
      form.querySelector<HTMLElement>(`[name="${first}"]`)?.focus()
      return
    }
    // demo: ništa se ne šalje, forma se samo prazni
    form.reset()
    setSent(true)
  }

  // greška polja nestaje čim se polje promeni; nova provera je na sledećem slanju
  const change = (e: ChangeEvent<HTMLInputElement>) => {
    const field = e.currentTarget.name as Field
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: false }))
    if (sent) setSent(false)
  }

  return (
    <div className="grid gap-s5 border-b border-line pb-s7 md:grid-cols-[1fr_1.4fr] md:items-start md:gap-s7">
      <h2 id={ids.title} className="type-display m-0 text-[clamp(1.5rem,1.2rem+1.2vw,2rem)] leading-none">
        {tx(nl.title)}
      </h2>
      <form noValidate aria-labelledby={ids.title} onSubmit={submit}>
        <label htmlFor={ids.email} className="type-label mb-s2 block">
          {tx(nl.email)}
        </label>
        <div className="flex flex-wrap gap-s3">
          <input
            id={ids.email}
            name="email"
            type="email"
            inputMode="email"
            autoComplete="email"
            aria-invalid={errors.email || undefined}
            aria-describedby={errors.email ? ids.emailErr : undefined}
            onChange={change}
            className="min-h-12 min-w-0 flex-[1_1_14rem] rounded-pill border-[1.5px] border-muted bg-transparent px-s5 font-text text-body text-text"
          />
          <Button type="submit">{tx(nl.button)}</Button>
        </div>
        {errors.email && (
          <p id={ids.emailErr} className="mt-s2 mb-0 text-small font-bold text-accent-text">
            {tx(nl.errors.email)}
          </p>
        )}
        <label className="mt-s4 flex min-h-tap cursor-pointer items-start gap-s3 md:text-small">
          <input
            name="consent"
            type="checkbox"
            aria-invalid={errors.consent || undefined}
            aria-describedby={errors.consent ? ids.consentErr : undefined}
            onChange={change}
            className="mt-[2px] size-5 flex-none cursor-pointer accent-accent-text"
          />
          <span>{tx(nl.consent)}</span>
        </label>
        {errors.consent && (
          <p id={ids.consentErr} className="mt-s1 mb-0 text-small font-bold text-accent-text">
            {tx(nl.errors.consent)}
          </p>
        )}
        {/* demo red; posle ispravne prijave isti tekst je potvrda. Prazan role="status" stoji stalno u
            DOM-u, da čitač pročita tekst kad se upiše. */}
        {!sent && <p className="mt-s3 mb-0 text-small text-muted">{tx(nl.demo)}</p>}
        <p role="status" className="mt-s3 mb-0 text-small font-bold text-accent-text empty:mt-0">
          {sent ? tx(nl.demo) : null}
        </p>
      </form>
    </div>
  )
}

export function Footer() {
  const { tx, tf } = useLang()
  const onHome = useLocation().pathname === '/'
  // na pravnim stranicama sidra vode nazad na početnu (kao Header)
  const href = (h: string) => (h.startsWith('#') && !onHome ? `/${h}` : h)

  return (
    <footer
      id="footer"
      data-chapter="sip"
      className="scroll-mt-header bg-bg px-gutter pt-s8 pb-[calc(var(--space-9)+env(safe-area-inset-bottom))] text-text md:pt-s9"
    >
      <div className="mx-auto max-w-site">
        <Newsletter />

        <div className="mt-s7 grid grid-cols-2 gap-x-s5 gap-y-s7 lg:grid-cols-[1.4fr_1fr_1fr_1.2fr]">
          <div className="col-span-2 flex flex-col items-start lg:col-span-1">
            <a href={onHome ? '#top' : '/'} aria-label={tf(site.logoLabel)} className="inline-flex min-h-tap flex-col justify-center leading-none no-underline">
              <span className="whitespace-nowrap font-text text-logo font-semibold tracking-[.01em]">{brand.name}</span>
              <span className="mt-[.45em] font-label text-logo-sub font-bold tracking-(--tracking-logo-sub) uppercase">{tx(brand.sub)}</span>
            </a>
            <LangSwitch className="mt-s3 -ml-2" />
          </div>

          {footer.columns.map((col, i) => {
            const titleId = `footer-col-${i}`
            return (
              <nav key={titleId} aria-labelledby={titleId}>
                <h2 id={titleId} className="type-eyebrow m-0 mb-s2">
                  {tf(col.title)}
                </h2>
                <ul className="m-0 list-none p-0">
                  {col.links.map((l) => {
                    const label = 'short' in l && l.short ? (
                      <>
                        <span className="md:hidden">{tx(l.short)}</span>
                        <span className="max-md:hidden">{tx(l.label)}</span>
                      </>
                    ) : (
                      tx(l.label)
                    )
                    return (
                      <li key={`${l.href}-${l.label.en}`}>
                        {l.href.startsWith('/') ? (
                          <Link to={l.href} className={linkClass}>
                            {label}
                          </Link>
                        ) : (
                          <a href={href(l.href)} className={linkClass}>
                            {label}
                          </a>
                        )}
                      </li>
                    )
                  })}
                </ul>
              </nav>
            )
          })}
        </div>

        {/* dugme za opoziv i Gewährleistungslabel levo: chat balon (dole desno) ih ne pokriva */}
        <div className="mt-s7 border-t border-line pt-s6">
          <div className="flex flex-wrap items-center gap-s4">
            <Button variant="outline" to={footer.withdraw.href}>
              {tx(footer.withdraw.label)}
            </Button>
            <div role="note" aria-label={tx(footer.guarantee.aria)} className="max-w-[26rem] rounded-sm border-[1.5px] border-muted px-s4 py-s3 text-small">
              <span className="md:hidden">{tx(footer.guarantee.short)}</span>
              <span className="max-md:hidden">{tx(footer.guarantee.text)}</span>
            </div>
          </div>
          <p className="mt-s5 mb-0 max-w-[44rem] rounded-sm border border-dashed border-muted px-s4 py-s3 text-small font-bold">{tx(site.demo)}</p>
          <p className="mt-s3 mb-0 flex flex-wrap items-center gap-x-s4 text-small text-muted">
            <span>{tf(footer.copyright)}</span>
            <Link to="/credits" className={linkClass}>
              {tx(credits.link)}
            </Link>
          </p>
        </div>
      </div>
    </footer>
  )
}
