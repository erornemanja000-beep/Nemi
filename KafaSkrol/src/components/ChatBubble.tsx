// STUB iz Z1 (doradu radi Z8): balon dole desno; pojavljuje se posle 3 s i otvara demo panel.
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { Icon } from './Icon'

export function ChatBubble() {
  const { tx } = useLang()
  return (
    <button
      type="button"
      aria-label={tx(site.chat.open)}
      className="fixed right-s4 bottom-[calc(var(--space-4)+env(safe-area-inset-bottom))] z-(--z-chat) grid size-13 cursor-pointer place-items-center rounded-full border-0 bg-pp-ink-deep text-pp-cream-light shadow-float lg:right-gutter lg:bottom-s6 lg:size-14"
    >
      <Icon name="chat" />
    </button>
  )
}
