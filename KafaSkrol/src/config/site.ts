// Brend i podešavanja. Ime brenda, e-mail adrese i demo telefon postoje SAMO ovde:
// tekstovi u src/content koriste oznake {brand}, {email}, {wholesale} i {phone}, a menja ih fill().
// Fajl je čist podatak (bez DOM-a), jer ga uvoze i vite.config.ts i scripts/*.ts.
import type { L } from '../content/types.ts'

export const brand = {
  /** Privremeno radno ime (tekstovi.md). Promena imena = ovaj red + ponovni render kesa (etiketa). */
  name: 'POUR / PLAY',
  sub: { en: 'Specialty Coffee · Vienna', de: 'Specialty Coffee · Wien' } satisfies L,
  /** Domen .example je rezervisan, pa poruka ne stiže nikome (demo). */
  email: 'hallo@pourplay.example',
  wholesale: 'wholesale@pourplay.example',
  /** Demo broj (tekstovi.md), nije stvaran. */
  phone: '+43 1 000 00 00',
  phoneHref: 'tel:+4310000000',
}

/** Prekidači: svaki se gasi jednim redom. */
export const features = {
  /** Lenis samo na desktopu sa mišem i van reduced motion (odluka direktora 1). */
  smoothScroll: true,
  /** Zrno filma preko stranice (src/components/Grain.tsx). */
  grain: true,
}

/** Ključevi za localStorage. Kolačića nema. */
export const storageKeys = {
  lang: 'kafa-lang',
  cart: 'kafa-cart',
} as const

const tokens: Record<string, string> = {
  brand: brand.name,
  email: brand.email,
  wholesale: brand.wholesale,
  phone: brand.phone,
}

/**
 * Menja oznake {brand}, {email}, {wholesale} i {phone} u tekstu, i dodatne oznake iz `vars`
 * (npr. fill(text, { n: 3 }) za „{n} products"). Nepoznata oznaka ostaje kakva jeste.
 */
export function fill(text: string, vars: Record<string, string | number> = {}): string {
  return text.replace(/\{(\w+)\}/g, (match, key: string) => {
    if (key in vars) return String(vars[key])
    if (key in tokens) return tokens[key]
    return match
  })
}
