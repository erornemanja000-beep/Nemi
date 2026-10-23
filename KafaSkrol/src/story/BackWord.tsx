// Ogromna pozadinska reč (mockup .word): ukras iza predmeta, aria-hidden. Longberry ima --fs-word,
// Percolate i Frother na desktopu --fs-word-xl (na telefonu --fs-word, kao mockup). Frother se na
// telefonu ne prikazuje. Omotač ima data-anim="word" (Story ga pomera kroz pin, ~10 % širine);
// položaj u sceni je u chapters.css (.ch-stage .ch-word--<poglavlje>).
import { chapters } from '../content/chapters'
import type { ChapterId } from '../content/types'
import './chapters.css'

type Props = { chapter: ChapterId; className?: string }

export function BackWord({ chapter, className = '' }: Props) {
  const word = chapters.items.find((c) => c.id === chapter)?.word
  if (!word) return null
  const size = chapter === 'grind' ? 'text-backword' : 'text-backword desk:text-backword-xl'
  return (
    <div
      data-anim="word"
      aria-hidden="true"
      className={`ch-word ch-word--${chapter} ${chapter === 'sip' ? 'phone:hidden' : ''} ${className}`}
    >
      <p className={`type-word m-0 whitespace-nowrap text-word ${size}`}>{word}</p>
    </div>
  )
}
