// Stranica /credits (Z3 tačka 2): ko je napravio fotografije, video pare i fontove.
// Redovi fotografija su iz media.photos (samo fajlovi koji postoje, ready: true), sa autorom, linkom i
// licencom iz photo.credit i natpisima iz legal.ts (credits.photos). Para: media.steamCredit.
// Desktop: tabela (Foto · Urheber · Quelle · Lizenz). Telefon: isti redovi kao lista, bez tabele od
// četiri kolone na 390 px. Spoljni linkovi imaju rel="noopener noreferrer".
// Red o privremenim kadrovima: dok media.ts nema polje SeqMedia.placeholder (dodaje ga Z13), red stoji;
// kad sve sekvence dobiju placeholder: false, nestaje sam.
import { useRef, type ReactNode } from 'react'
import { Button } from '../components/Button'
import { Icon } from '../components/Icon'
import { fill } from '../config/site'
import { credits } from '../content/legal'
import { media, steamCredit } from '../content/media'
import type { L } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { Footer } from '../sections/Footer'
import { PageMeta } from './Legal'

type RowText = { photo: L; usedIn: L; source: string }
type Row = {
  id: string
  photo: L
  usedIn: L
  note?: L
  author: string
  source: { label: string; title?: string; href: string }
  license: { label: string; href?: string }
}

const photoTexts = credits.photos as Record<string, RowText | undefined>

const rows: Row[] = Object.values(media.photos).flatMap((p) => {
  const text = photoTexts[p.id]
  if (!p.ready || !text) return []
  return [
    {
      id: p.id,
      photo: text.photo,
      usedIn: text.usedIn,
      author: p.credit.author,
      source: { label: text.source, href: p.credit.url },
      license: { label: p.credit.license, href: p.credit.licenseUrl },
    },
  ]
})

if (media.steam.pour.ready || media.steam.sip.ready) {
  rows.push({
    id: 'steam',
    photo: credits.steam.photo,
    usedIn: credits.steam.usedIn,
    note: credits.steam.note,
    author: steamCredit.author,
    source: { label: credits.steam.source, title: steamCredit.title, href: steamCredit.url },
    license: { label: steamCredit.license },
  })
}

const hasPlaceholders = Object.values(media.seq).some((s) => !('placeholder' in s) || s.placeholder !== false)

const linkClass = 'inline-flex min-h-tap items-center gap-1 underline underline-offset-[3px] hover:text-accent-text'

/** Spoljni link; ikonica ide u red teksta (i kad se dug naslov prelomi), visina reda ≥ 44 px. */
function External({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a href={href} rel="noopener noreferrer" className="inline-block py-[11px] underline underline-offset-[3px] hover:text-accent-text">
      {children}
      <Icon name="external" className="ml-1 inline size-3.5 align-[-1px]" />
    </a>
  )
}

function Source({ row }: { row: Row }) {
  const { lang } = useLang()
  // originalni naslov klipa se ne prevodi, menjaju se samo navodnici
  const title = row.source.title && (lang === 'de' ? `„${row.source.title}“` : `“${row.source.title}”`)
  return (
    <External href={row.source.href}>
      {row.source.label}
      {title && `: ${title}`}
    </External>
  )
}

function License({ row }: { row: Row }) {
  return row.license.href ? <External href={row.license.href}>{row.license.label}</External> : <>{row.license.label}</>
}

export default function Credits() {
  const { lang, tx } = useLang()
  const heading = useRef<HTMLHeadingElement>(null)
  const col = credits.columns

  const photoCell = (row: Row) => (
    <>
      <span className="block font-bold">{tx(row.photo)}</span>
      <span className="block text-muted">{tx(row.usedIn)}</span>
      {row.note && <span className="mt-s1 block text-muted">{tx(row.note)}</span>}
    </>
  )

  return (
    <>
      <PageMeta title={fill(credits.docTitle[lang])} heading={heading} />
      <main id="main" className="bg-bg px-gutter pt-[calc(var(--header-h)+var(--space-7))] pb-s9 text-text">
        <article aria-labelledby="t-credits" className="mx-auto max-w-[64rem]">
          <h1 id="t-credits" ref={heading} tabIndex={-1} className="type-display m-0 text-h2 leading-none outline-none">
            {tx(credits.title)}
          </h1>
          <p className="mt-s3 mb-0 font-bold">{tx(credits.subtitle)}</p>
          <p className="mt-s4 mb-0 max-w-[40rem]">{tx(credits.text)}</p>

          <p className="mt-s6 mb-s3 text-small text-muted">{tx(credits.note)}</p>

          {/* desktop i tablet: tabela */}
          <table className="hidden w-full border-collapse text-left text-small md:table">
            <thead>
              <tr className="border-b border-line-strong">
                {[col.photo, col.author, col.source, col.license].map((c) => (
                  <th key={c.en} scope="col" className="type-eyebrow py-s2 pr-s4 align-bottom font-bold">
                    {tx(c)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-b border-line align-top">
                  <td className="py-s3 pr-s4">{photoCell(row)}</td>
                  <td className="py-s3 pr-s4">{row.author}</td>
                  <td className="py-s1 pr-s4">
                    <Source row={row} />
                  </td>
                  <td className="py-s1">
                    <License row={row} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* telefon: lista, svaki red sa natpisima polja */}
          <ul className="m-0 list-none border-b border-line p-0 text-small md:hidden">
            {rows.map((row) => (
              <li key={row.id} className="border-t border-line py-s3">
                <p className="m-0">{photoCell(row)}</p>
                <dl className="mt-s2 mb-0 grid grid-cols-[auto_1fr] items-center gap-x-s3">
                  <dt className="text-muted">{tx(col.author)}</dt>
                  <dd className="m-0 py-s2">{row.author}</dd>
                  <dt className="text-muted">{tx(col.source)}</dt>
                  <dd className="m-0">
                    <Source row={row} />
                  </dd>
                  <dt className="text-muted">{tx(col.license)}</dt>
                  <dd className="m-0">
                    <License row={row} />
                  </dd>
                </dl>
              </li>
            ))}
          </ul>

          <p className="mt-s6 mb-0 max-w-[40rem]">{tx(credits.fonts.text)}</p>
          <p className="mt-s2 mb-0 flex flex-wrap items-center gap-x-s3">
            <span>{tx(credits.fonts.linksLabel)}</span>
            {credits.fonts.files.map((f, i) => (
              <span key={f.href} className="inline-flex items-center gap-x-s3">
                {i > 0 && <span aria-hidden="true">·</span>}
                <a href={f.href} className={linkClass}>
                  {f.name}
                </a>
              </span>
            ))}
          </p>

          <p className="mt-s5 mb-0 max-w-[40rem]">
            {tx(credits.renders.text)}
            {hasPlaceholders && <> {tx(credits.renders.placeholder)}</>}
          </p>

          <Button to={credits.back.href} variant="outline" className="mt-s7">
            {tx(credits.back.label)}
          </Button>
        </article>
      </main>
      <Footer />
    </>
  )
}
