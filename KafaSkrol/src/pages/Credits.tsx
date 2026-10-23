// STUB iz Z1 (doradu radi Z10): fotografije iz media.ts, snimak pare, fontovi i licence.
import { credits } from '../content/legal'
import { media } from '../content/media'
import { useLang } from '../i18n/LangContext'

export default function Credits() {
  const { tx } = useLang()
  return (
    <main id="main" className="min-h-svh bg-bg px-gutter pt-[calc(var(--header-h)+var(--space-7))] pb-s9 text-text">
      <h1 className="type-display m-0 text-h2 leading-none">{tx(credits.title)}</h1>
      <ul className="mt-s5 p-0 pl-s5">
        {Object.values(media.photos).map((p) => (
          <li key={p.id}>
            {p.credit.author}, {p.credit.license}
          </li>
        ))}
      </ul>
    </main>
  )
}
