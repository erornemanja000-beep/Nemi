// Tekst poglavlja (mockup .chapter__content): eyebrow, H2 (t-grind, t-pour, t-sip), tekst i CTA.
// Omotač ima data-anim="text": Story (Z12) pomera samo njega (fade + 24 px). U .ch-layer na desktopu
// stoji apsolutno, levo na --chapter-inset i sa sredinom na 49 % visine (chapters.css).
import { Button } from '../components/Button'
import type { Chapter } from '../content/types'
import { useLang } from '../i18n/LangContext'
import './chapters.css'

type Props = { chapter: Chapter; className?: string }

export function ChapterText({ chapter, className = '' }: Props) {
  const { tx } = useLang()
  return (
    <div data-anim="text" className={`ch-text ${className}`}>
      <div className="ch-text__inner">
        <p className="type-eyebrow mt-0 mb-s3">{tx(chapter.eyebrow)}</p>
        <h2 id={`t-${chapter.id}`} className="type-display mt-0 mb-s3 text-chapter leading-(--lh-chapter) sm:mb-s4">
          {tx(chapter.title)}
        </h2>
        <p className="mt-0 mb-s5 max-w-measure">{tx(chapter.text)}</p>
        <Button href={chapter.cta.href}>{tx(chapter.cta.label)}</Button>
      </div>
    </div>
  )
}
