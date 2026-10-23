// STUB iz Z1 (doradu radi Z7): eyebrow, H2 (t-grind, t-pour, t-sip), tekst i CTA. Omotač ima data-anim="text".
import { Button } from '../components/Button'
import type { Chapter } from '../content/types'
import { useLang } from '../i18n/LangContext'

type Props = { chapter: Chapter; className?: string }

export function ChapterText({ chapter, className = '' }: Props) {
  const { tx } = useLang()
  return (
    <div data-anim="text" className={className}>
      <div className="relative z-(--z-content) max-w-[34rem]">
        <p className="type-eyebrow mt-0 mb-s3">{tx(chapter.eyebrow)}</p>
        <h2 id={`t-${chapter.id}`} className="type-display mt-0 mb-s4 text-chapter leading-(--lh-chapter)">
          {tx(chapter.title)}
        </h2>
        <p className="mt-0 mb-s5 max-w-measure">{tx(chapter.text)}</p>
        <Button href={chapter.cta.href}>{tx(chapter.cta.label)}</Button>
      </div>
    </div>
  )
}
