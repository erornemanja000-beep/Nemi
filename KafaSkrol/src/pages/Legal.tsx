// STUB iz Z1 (doradu radi Z10): jedna stranica za sve pravne slugove iz legal.ts.
import { Navigate } from 'react-router-dom'
import { legalPages } from '../content/legal'
import type { LegalSlug } from '../content/types'
import { useLang } from '../i18n/LangContext'

export default function Legal({ slug }: { slug: LegalSlug }) {
  const { tx } = useLang()
  const page = legalPages.find((p) => p.slug === slug)
  if (!page) return <Navigate to="/" replace />
  return (
    <main id="main" className="min-h-svh bg-bg px-gutter pt-[calc(var(--header-h)+var(--space-7))] pb-s9 text-text">
      <h1 className="type-display m-0 text-h2 leading-none">{tx(page.title)}</h1>
      <p className="mt-s4">{tx(page.intro)}</p>
    </main>
  )
}
