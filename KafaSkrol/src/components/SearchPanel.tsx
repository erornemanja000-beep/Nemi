// STUB iz Z1 (doradu radi Z8): pretraga kafa i opreme po imenu, poreklu i notama, na oba jezika.
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'

type Props = { open: boolean; onClose: () => void }

export function SearchPanel({ open }: Props) {
  const { tx } = useLang()
  if (!open) return null
  return <div role="dialog" aria-label={tx(site.aria.search)} />
}
