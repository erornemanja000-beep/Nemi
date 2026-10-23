// STUB iz Z1 (doradu radi Z7): ogromna pozadinska reč (dekor, aria-hidden).
import { chapters } from '../content/chapters'
import type { ChapterId } from '../content/types'

type Props = { chapter: ChapterId; className?: string }

export function BackWord({ chapter, className = '' }: Props) {
  const word = chapters.items.find((c) => c.id === chapter)?.word
  return (
    <p aria-hidden="true" className={`type-word pointer-events-none m-0 whitespace-nowrap text-backword text-word select-none ${className}`}>
      {word}
    </p>
  )
}
