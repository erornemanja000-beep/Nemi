// Sekcije ispod prodavnice: pretplata, Probierset, O nama, Brew guide, Kontakt, footer (tekstovi.md).
// STUB iz Z1: samo naslovi. Z11 prenosi ostatak.
import type { L } from './types.ts'

export const sections = {
  subscription: { title: { en: 'Never run out of beans', de: 'Nie mehr ohne Bohnen' } satisfies L },
  tastingSet: { title: { en: 'Not sure yet? Try four.', de: 'Noch unsicher? Probier vier.' } satisfies L },
  about: { title: { en: 'A roastery with chairs', de: 'Eine Rösterei mit Sesseln' } satisfies L },
  brewGuide: { title: { en: 'Three steps, three minutes', de: 'Drei Schritte, drei Minuten' } satisfies L },
  contact: { title: { en: 'Come by', de: 'Komm vorbei' } satisfies L },
  footer: {
    copyright: { en: '© 2026 {brand} (Konzept / Concept)', de: '© 2026 {brand} (Konzept / Concept)' } satisfies L,
  },
}
