// Brend i podešavanja. Ime brenda, e-mail adrese i demo telefon postoje SAMO ovde:
// tekstovi u src/content koriste oznake {brand}, {email}, {wholesale} i {phone}, a menja ih fill().
// Fajl je čist podatak (bez DOM-a), jer ga uvoze i vite.config.ts i scripts/*.ts.
import type { L } from '../content/types.ts'

export const brand = {
  /** Izmišljeno ime za demo (korisnik, 23.10.2026): zrno i kuvalo, kao u priči. Proverom nije nađena firma tog imena.
   *  Promena imena = ovaj red + etiketa (studio/kafa-skrol/dizajn/etiketa.html) + ponovni render kesa. */
  name: 'KORN / KANNE',
  sub: { en: 'Specialty Coffee · Vienna', de: 'Specialty Coffee · Wien' } satisfies L,
  /** Domen .example je rezervisan, pa poruka ne stiže nikome (demo). */
  email: 'hallo@kornkanne.example',
  wholesale: 'wholesale@kornkanne.example',
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

// Base (vite.config.ts, KAFA_BASE): „/" na Netlify-ju, „/Nemi/kafaskrol/" za GitHub Pages (npm run build:gh).
// U Node-u (vite.config.ts, scripts/*.ts) import.meta.env ne postoji, pa je base „/" i putanje ostaju iste.
const BASE = (import.meta as { env?: { BASE_URL?: string } }).env?.BASE_URL ?? '/'

/** Putanja do fajla iz public/ pod base-om: asset('/media/x.webp') → „/Nemi/kafaskrol/media/x.webp". */
export const asset = (p: string) => BASE + p.replace(/^\//, '')

/** Ruta za običan <a href> (rezerva bez JS-a, puno učitavanje): pageHref('/#about') → „/Nemi/kafaskrol/#about".
 *  <Link> i navigate() ne traže ovo, jer base dodaje ruter (basename). */
export const pageHref = asset

/** basename za BrowserRouter: base bez završne „/" („/" kad je base „/"). */
export const routerBasename = BASE.replace(/\/$/, '') || '/'

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
