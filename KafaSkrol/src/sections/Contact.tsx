// STUB iz Z1 (doradu radi Z10).
import { sections } from '../content/sections'
import { useLang } from '../i18n/LangContext'

export function Contact() {
  const { tx } = useLang()
  return (
    <section id="contact" aria-labelledby="t-contact" className="scroll-mt-header bg-bg px-gutter py-s9 text-text">
      <h2 id="t-contact" className="type-display m-0 text-h2 leading-none">{tx(sections.contact.title)}</h2>
    </section>
  )
}
