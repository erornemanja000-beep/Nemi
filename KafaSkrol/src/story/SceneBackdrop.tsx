// Svetlo i sto iza scene: meki gradijent iz smera key svetla (gore levo) i traka stola na
// var(--table-y) (POUR pult, SIP pod kao .chapter--sip u mockup-u). --table-y postavlja Story na sloj
// iz pult_y / sto_y; bez nje važi vrednost iz mockupa (chapters.css). Ide prvi u sloju, ispod svega.
import type { ChapterId } from '../content/types'
import './chapters.css'

type Props = { chapter: ChapterId; className?: string }

export function SceneBackdrop({ chapter, className = '' }: Props) {
  return <div aria-hidden="true" className={`scene-backdrop scene-backdrop--${chapter} ${className}`} />
}
