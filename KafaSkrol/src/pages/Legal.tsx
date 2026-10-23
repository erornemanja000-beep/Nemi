// Jedna stranica za sve pravne slugove iz legal.ts (demo stub, Z3 tačka 3). Naslov, podnaslov (AGB),
// uvod „Konzept / Demo", zajednički tekst (Cookies ga menja svojim, Datenschutz dodaje svoj ispod),
// pa spisak „What goes here": svaka stavka ima demo tekst, link, onemogućeno dugme ili čip „not in demo".
// [FEHLT] se ne prikazuje doslovno. Napomene (uvod, demo tekst stavke) su na telefonu 16 px, od md 14 px.
// Footer (linkovi na ostale pravne stranice) dodaje App.tsx.
// PageMeta (deli ga i Credits.tsx): naslov kartice, header u stanju „page", vrh stranice i fokus na H1.
import { useEffect, useLayoutEffect, useRef, type RefObject } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { Button } from '../components/Button'
import { fill } from '../config/site'
import { legal, legalPages } from '../content/legal'
import type { LegalEntry, LegalSlug } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { setActiveChapter } from '../lib/chapterStore'
import { scrollToTarget } from '../lib/motion'

/**
 * Za stranice van početne: document.title, header u stanju „page" i skok na vrh (BrowserRouter ne
 * vraća skrol sam). Naslov piše samo ova stranica (LangProvider ne piše naslov), a početna upisuje svoj
 * kad se na nju vrati. `heading` dobija fokus, da čitač ekrana pročita novu stranicu (i da fokus ne
 * ostane na linku u footeru, koji je isti na svim stranicama).
 */
export function PageMeta({ title, heading }: { title: string; heading: RefObject<HTMLElement | null> }) {
  useLayoutEffect(() => {
    setActiveChapter('page')
    scrollToTarget(0, true)
    return () => scrollToTarget(0, true)
  }, [])

  // fokus u običnom efektu: PageMeta stoji pre <h1> u stablu, pa u njegovom layout efektu ref naslova
  // još nije postavljen (React postavlja ref-ove redom, posle layout efekata ranijih komponenti)
  useEffect(() => {
    heading.current?.focus({ preventScroll: true })
  }, [heading])

  useEffect(() => {
    document.title = title
  }, [title])

  return null
}

const chip = 'inline-flex items-center rounded-pill border border-line-strong px-s2 py-[3px] font-label text-micro leading-none font-bold tracking-(--tracking-nav) uppercase text-muted'

function Entry({ entry }: { entry: LegalEntry }) {
  const { tx } = useLang()
  const done = Boolean(entry.text || entry.href || entry.action)
  return (
    <li className="border-t border-line py-s4">
      <h3 className="m-0 flex flex-wrap items-center gap-x-s3 gap-y-s1 text-h3 font-extrabold">
        {entry.href ? (
          <Link to={entry.href} className="inline-flex min-h-tap items-center underline underline-offset-[3px] hover:text-accent-text">
            {tx(entry.title)}
          </Link>
        ) : (
          tx(entry.title)
        )}
        {!done && <span className={chip}>{tx(legal.missing)}</span>}
      </h3>
      {entry.text && <p className="mt-s2 mb-0 max-w-[40rem] md:text-small">{tx(entry.text)}</p>}
      {entry.action && (
        <Button disabled className="mt-s3">
          {tx(entry.action)}
        </Button>
      )}
    </li>
  )
}

export default function Legal({ slug }: { slug: LegalSlug }) {
  const { lang, tx } = useLang()
  const heading = useRef<HTMLHeadingElement>(null)
  const page = legalPages.find((p) => p.slug === slug)
  if (!page) return <Navigate to="/" replace />
  // Cookies: svoj tekst umesto zajedničkog; ostale (Datenschutz) dodaju svoj ispod zajedničkog (legal.ts)
  const ownTextOnly = Boolean(page.body && page.bodyReplacesText)

  return (
    <>
      <PageMeta title={fill(page.docTitle[lang])} heading={heading} />
      <main id="main" className="bg-bg px-gutter pt-[calc(var(--header-h)+var(--space-7))] pb-s9 text-text">
        <article aria-labelledby="t-legal" className="mx-auto max-w-[48rem]">
          <h1 id="t-legal" ref={heading} tabIndex={-1} className="type-display m-0 text-h2 leading-none outline-none">
            {tx(page.title)}
          </h1>
          {page.subtitle && <p className="mt-s3 mb-0 font-bold hyphens-auto">{tx(page.subtitle)}</p>}
          <p className="mt-s5 mb-0 inline-block rounded-sm border border-dashed border-line-strong px-s4 py-s3 font-bold md:text-small">{tx(page.intro)}</p>
          {!ownTextOnly && <p className="mt-s5 mb-0 max-w-[40rem]">{tx(legal.text)}</p>}
          {page.body && <p className="mt-s4 mb-0 max-w-[40rem]">{tx(page.body)}</p>}

          <h2 className="type-eyebrow mt-s7 mb-s2">{tx(legal.listTitle)}</h2>
          <ul className="m-0 list-none border-b border-line p-0">
            {page.entries.map((entry) => (
              <Entry key={entry.title.en} entry={entry} />
            ))}
          </ul>

          <Button to={legal.back.href} variant="outline" className="mt-s7">
            {tx(legal.back.label)}
          </Button>
        </article>
      </main>
    </>
  )
}
