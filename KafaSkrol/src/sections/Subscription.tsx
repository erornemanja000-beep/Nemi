// STUB iz Z1 (doradu radi Z10): pretplata (dve opcije, poklon) i #tasting-set.
import { sections } from '../content/sections'
import { useLang } from '../i18n/LangContext'

export function Subscription() {
  const { tx } = useLang()
  return (
    <section id="subscription" aria-labelledby="t-subscription" className="scroll-mt-header bg-bg px-gutter py-s9 text-text">
      <h2 id="t-subscription" className="type-display m-0 text-h2 leading-none">{tx(sections.subscription.title)}</h2>
      <div id="tasting-set" className="mt-s7 scroll-mt-header">
        <h3 className="m-0 text-h3 font-extrabold">{tx(sections.tastingSet.title)}</h3>
      </div>
    </section>
  )
}
