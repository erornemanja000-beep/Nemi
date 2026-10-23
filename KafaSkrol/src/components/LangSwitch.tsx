// Prekidač jezika EN · DE (header na desktopu, meni na telefonu, footer). Jedno dugme menja jezik;
// aria-label (tekstovi.md) kaže koji je jezik sada i na koji se prelazi. Izabrani jezik je podvučen,
// drugi je u prigušenoj boji poglavlja (--color-text-muted, ≥ 4,5:1 na svakoj podlozi).
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { buttonClass } from './Button'

export function LangSwitch({ className = '' }: { className?: string }) {
  const { lang, setLang, tx } = useLang()
  const part = (l: 'en' | 'de') =>
    lang === l ? 'text-text underline decoration-[1.5px] underline-offset-[5px]' : 'text-muted'
  return (
    <button
      type="button"
      className={buttonClass('icon', `w-auto px-2 font-label text-label font-bold tracking-(--tracking-nav) ${className}`)}
      aria-label={tx(site.lang.label)}
      onClick={() => setLang(lang === 'en' ? 'de' : 'en')}
    >
      <span aria-hidden="true" className="whitespace-nowrap">
        <span lang="en" className={part('en')}>EN</span>
        <span className="text-muted"> · </span>
        <span lang="de" className={part('de')}>DE</span>
      </span>
    </button>
  )
}
