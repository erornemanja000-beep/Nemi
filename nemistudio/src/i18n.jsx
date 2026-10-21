import { createContext, useContext, useEffect, useState } from 'react';

// German is the default (nemistudio.at); ?lang=en or the toggle switches to English.
function initialLang() {
  try {
    const q = new URLSearchParams(location.search).get('lang');
    if (q === 'en' || q === 'de') return q;
    const saved = localStorage.getItem('nemi-lang');
    if (saved === 'en' || saved === 'de') return saved;
  } catch (e) { /* storage blocked */ }
  return 'de';
}

const Ctx = createContext({ lang: 'de', setLang: () => {} });

export function LangProvider({ children }) {
  const [lang, setLang] = useState(initialLang);
  useEffect(() => {
    document.documentElement.lang = lang;
    try { localStorage.setItem('nemi-lang', lang); } catch (e) { /* storage blocked */ }
  }, [lang]);
  return <Ctx.Provider value={{ lang, setLang }}>{children}</Ctx.Provider>;
}

export function useLang() {
  const { lang, setLang } = useContext(Ctx);
  // L picks the active language from a { de, en } pair; plain strings pass through
  const L = (x) => (x && typeof x === 'object' && !Array.isArray(x) && 'de' in x ? x[lang] : x);
  return { lang, setLang, L };
}
