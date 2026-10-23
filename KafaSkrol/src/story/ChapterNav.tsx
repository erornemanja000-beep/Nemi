// Strelice (60 px) i tačkice za skok po poglavljima (mockup .arrow, .dots), samo na desktopu.
// Skok ide preko goToChapter(): Story registruje početke GRIND-a, POUR pina i SIP pina, a bez nje
// (stub, reduced motion) skače se na #id sloja. Prva strelica levo i poslednja desno su onemogućene.
import { Icon } from '../components/Icon'
import { chapters } from '../content/chapters'
import type { ChapterId } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { goToChapter } from '../lib/chapterStore'
import './chapters.css'

type Props = { current: ChapterId; className?: string }

const order = chapters.items.map((c) => c.id)

export function ChapterNav({ current, className = '' }: Props) {
  const { tx, tf } = useLang()
  const i = order.indexOf(current)
  const prev = order[i - 1]
  const next = order[i + 1]
  return (
    <div className={`ch-nav phone:hidden ${className}`}>
      <button
        type="button"
        className="ch-arrow ch-arrow--prev"
        aria-label={tx(chapters.nav.prev)}
        disabled={!prev}
        onClick={() => prev && goToChapter(prev)}
      >
        <Icon name="prev" className="size-5" />
      </button>
      <button
        type="button"
        className="ch-arrow ch-arrow--next"
        aria-label={tx(chapters.nav.next)}
        disabled={!next}
        onClick={() => next && goToChapter(next)}
      >
        <Icon name="next" className="size-5" />
      </button>
      <div className="ch-dots">
        {order.map((id, n) => (
          <button
            key={id}
            type="button"
            className="ch-dot"
            aria-label={tf(chapters.nav.dot, { n: n + 1 })}
            aria-current={id === current ? 'true' : undefined}
            onClick={() => goToChapter(id)}
          />
        ))}
      </div>
    </div>
  )
}
