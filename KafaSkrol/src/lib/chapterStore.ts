// Aktivno poglavlje (plan, Interfejs 6). Story (Z12) ga postavlja dok se skroluje, Header ga čita
// za boje (data-chapter), a ChapterNav skače preko goToChapter().
// U dev-u (ili sa ?debug): window.__chapter('pour') ručno menja stanje, window.__chapter() ga čita.
import { useSyncExternalStore } from 'react'
import type { ActiveChapter, ChapterId } from '../content/types'
import { scrollToTarget } from './motion'

let active: ActiveChapter = 'grind'
const listeners = new Set<() => void>()

export function setActiveChapter(next: ActiveChapter) {
  if (next === active) return
  active = next
  listeners.forEach((l) => l())
}

export const getActiveChapter = () => active

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export const useActiveChapter = () => useSyncExternalStore(subscribe, getActiveChapter, getActiveChapter)

// --- skok na poglavlje ---
export type ChapterNavigator = (id: ChapterId) => void
let chapterNavigator: ChapterNavigator | null = null

/** Story registruje kako se skače na početak poglavlja (GRIND, POUR pin, SIP pin). Vraća odjavu. */
export function registerChapterNavigator(fn: ChapterNavigator) {
  chapterNavigator = fn
  return () => {
    if (chapterNavigator === fn) chapterNavigator = null
  }
}

/** Skok na poglavlje. Bez registrovane priče (npr. stub, reduced motion) skače na #id sloja. */
export function goToChapter(id: ChapterId) {
  if (chapterNavigator) chapterNavigator(id)
  else scrollToTarget(`#${id}`)
}

declare global {
  interface Window {
    __chapter?: (next?: ActiveChapter) => ActiveChapter
  }
}

if (typeof window !== 'undefined' && (import.meta.env.DEV || new URLSearchParams(window.location.search).has('debug'))) {
  window.__chapter = (next) => {
    if (next) setActiveChapter(next)
    return active
  }
}
