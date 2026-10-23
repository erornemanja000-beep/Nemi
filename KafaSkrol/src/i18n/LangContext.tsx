// Jezik (uzor: RealEstates/src/i18n/LangContext.tsx). Podrazumevano EN, izbor se pamti u
// localStorage (storageKeys.lang). Pri promeni jezika menja <html lang>, document.title i meta description.
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fill, storageKeys } from '../config/site'
import { site } from '../content/site'
import type { L, Lang } from '../content/types'

type Ctx = {
  lang: Lang
  setLang: (l: Lang) => void
  /** Bira polje za trenutni jezik: tx({ en: 'Cart', de: 'Warenkorb' }). */
  tx: <T>(value: L<T>) => T
  /** tx + fill: menja {brand}, {email}… i dodatne oznake ({n}, {q}). */
  tf: (value: L, vars?: Record<string, string | number>) => string
}

const LangContext = createContext<Ctx | null>(null)

function initialLang(): Lang {
  try {
    const saved = localStorage.getItem(storageKeys.lang)
    if (saved === 'en' || saved === 'de') return saved
  } catch {
    /* storage nije dostupan */
  }
  return 'en'
}

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(initialLang)

  useEffect(() => {
    document.documentElement.lang = lang
    document.title = fill(site.seo.title[lang])
    document.querySelector('meta[name="description"]')?.setAttribute('content', fill(site.seo.description[lang]))
  }, [lang])

  const value = useMemo<Ctx>(
    () => ({
      lang,
      setLang: (l) => {
        setLangState(l)
        try {
          localStorage.setItem(storageKeys.lang, l)
        } catch {
          /* storage nije dostupan */
        }
      },
      tx: (v) => v[lang],
      tf: (v, vars) => fill(v[lang], vars),
    }),
    [lang],
  )
  return <LangContext.Provider value={value}>{children}</LangContext.Provider>
}

// hook ide uz svoj Provider (kao RealEstates); fast refresh za ovaj fajl nije bitan
// oxlint-disable-next-line react/only-export-components
export function useLang() {
  const ctx = useContext(LangContext)
  if (!ctx) throw new Error('useLang must be used inside LangProvider')
  return ctx
}
