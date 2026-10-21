import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { content } from './content.js';

const LangContext = createContext(null);

function initialLang() {
  try {
    const saved = localStorage.getItem('kern-lang');
    if (saved === 'de' || saved === 'en') return saved;
  } catch { /* privater modus */ }
  // engleski je glavni jezik; nemački samo ako ga pregledač traži
  return /^de\b/i.test(navigator.language || '') ? 'de' : 'en';
}

export function LangProvider({ children }) {
  const [lang, setLang] = useState(initialLang);

  useEffect(() => {
    document.documentElement.lang = lang;
    try { localStorage.setItem('kern-lang', lang); } catch { /* egal */ }
  }, [lang]);

  const toggle = useCallback(() => setLang((l) => (l === 'de' ? 'en' : 'de')), []);
  const value = useMemo(() => ({ lang, toggle, t: content[lang] }), [lang, toggle]);
  return <LangContext.Provider value={value}>{children}</LangContext.Provider>;
}

export const useLang = () => useContext(LangContext);
