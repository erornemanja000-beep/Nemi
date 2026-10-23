import { useCallback, useSyncExternalStore } from 'react'

/** Desktop raspored priče: od 64rem (1024 px) širine i 600 px visine (plan, Interfejs 1).
    Isti upit je @custom-variant desk u src/index.css i predučitavanje postera u index.html. */
export const DESKTOP_QUERY = '(min-width: 64rem) and (min-height: 600px)'
export const PHONE_QUERY = `not all and ${DESKTOP_QUERY}`
export const REDUCED_QUERY = '(prefers-reduced-motion: reduce)'
export const FINE_POINTER_QUERY = '(hover: hover) and (pointer: fine)'

const matches = (query: string) => typeof window !== 'undefined' && window.matchMedia(query).matches

// --- obične funkcije, za kod van React-a (sequence.ts, motion.ts) ---
export const isReducedMotion = () => matches(REDUCED_QUERY)
export const isPhone = () => !matches(DESKTOP_QUERY)
export const isFinePointer = () => matches(FINE_POINTER_QUERY)

type NetworkInformationLike = EventTarget & { saveData?: boolean }
const connection = (): NetworkInformationLike | undefined =>
  typeof navigator === 'undefined' ? undefined : (navigator as Navigator & { connection?: NetworkInformationLike }).connection

/** Save-Data (navigator.connection.saveData, Chromium). Gde ga nema, uvek false. */
export const isSaveData = () => connection()?.saveData === true

// --- hook-ovi ---
export function useMediaQuery(query: string): boolean {
  const subscribe = useCallback(
    (onChange: () => void) => {
      const mql = window.matchMedia(query)
      mql.addEventListener('change', onChange)
      return () => mql.removeEventListener('change', onChange)
    },
    [query],
  )
  const get = useCallback(() => window.matchMedia(query).matches, [query])
  return useSyncExternalStore(subscribe, get, () => false)
}

export const useReducedMotion = () => useMediaQuery(REDUCED_QUERY)
/** Telefonski raspored = sve što nije desktop (i nizak ekran na laptopu). */
export const useIsPhone = () => !useMediaQuery(DESKTOP_QUERY)
export const useFinePointer = () => useMediaQuery(FINE_POINTER_QUERY)

function subscribeSaveData(onChange: () => void) {
  const c = connection()
  c?.addEventListener('change', onChange)
  return () => c?.removeEventListener('change', onChange)
}

export const useSaveData = () => useSyncExternalStore(subscribeSaveData, isSaveData, () => false)
