// STUB iz Z1 (doradu radi Z8): prekidač EN · DE, koristi se u headeru, meniju i footeru.
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { buttonClass } from './Button'

export function LangSwitch({ className = '' }: { className?: string }) {
  const { lang, setLang, tx } = useLang()
  return (
    <button
      type="button"
      className={buttonClass('icon', `w-auto px-2 font-label text-label font-bold tracking-(--tracking-nav) ${className}`)}
      aria-label={tx(site.lang.label)}
      onClick={() => setLang(lang === 'en' ? 'de' : 'en')}
    >
      <span aria-hidden="true">
        <span className={lang === 'en' ? '' : 'opacity-60'}>EN</span> · <span className={lang === 'de' ? '' : 'opacity-60'}>DE</span>
      </span>
    </button>
  )
}
