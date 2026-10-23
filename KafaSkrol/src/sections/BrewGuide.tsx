// STUB iz Z1 (doradu radi Z10).
import { sections } from '../content/sections'
import { useLang } from '../i18n/LangContext'

export function BrewGuide() {
  const { tx } = useLang()
  return (
    <section id="brew-guide" aria-labelledby="t-brew-guide" className="scroll-mt-header bg-bg px-gutter py-s9 text-text">
      <h2 id="t-brew-guide" className="type-display m-0 text-h2 leading-none">{tx(sections.brewGuide.title)}</h2>
    </section>
  )
}
