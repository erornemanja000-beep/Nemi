// STUB iz Z1 (doradu radi Z10): kolone, newsletter, „Vertrag widerrufen", Gewährleistungslabel, Credits.
import { Link } from 'react-router-dom'
import { LangSwitch } from '../components/LangSwitch'
import { credits, legalPages } from '../content/legal'
import { sections } from '../content/sections'
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'

export function Footer() {
  const { tx, tf } = useLang()
  return (
    <footer id="footer" className="bg-surface px-gutter pt-s8 pb-[calc(var(--space-9)+env(safe-area-inset-bottom))] text-text">
      <p className="m-0 text-small">{tx(site.demo)}</p>
      <ul className="mt-s4 flex list-none flex-wrap gap-x-s4 p-0 text-small">
        {legalPages.map((p) => (
          <li key={p.slug}>
            <Link to={`/${p.slug}`} className="inline-flex min-h-tap items-center underline">{tx(p.title)}</Link>
          </li>
        ))}
        <li>
          <Link to="/credits" className="inline-flex min-h-tap items-center underline">{tx(credits.title)}</Link>
        </li>
      </ul>
      <div className="mt-s4 flex items-center gap-s4">
        <p className="m-0 text-small text-muted">{tf(sections.footer.copyright)}</p>
        <LangSwitch />
      </div>
    </footer>
  )
}
