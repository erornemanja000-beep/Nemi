// Tipovi sadržaja (plan, Interfejs 7). Sadržaj je čist podatak: bez JSX-a, bez window-a i bez uvoza
// slika, jer ga uvoze i vite.config.ts i scripts/*.ts (tsconfig.node.json nema DOM tipove).
// Relativni uvozi u src/content i src/config imaju nastavak .ts (Node ih učitava direktno).

export type Lang = 'en' | 'de'

/** Dvojezično polje: prvo EN (podrazumevano), pa DE. */
export type L<T = string> = { en: T; de: T }

export type ChapterId = 'grind' | 'pour' | 'sip'

/** Stanje headera: tri poglavlja priče, pa 'page' za sve ispod priče. */
export type ActiveChapter = ChapterId | 'page'

export type Link = { label: L; href: string }

export type Chapter = {
  id: ChapterId
  /** „Section 1" / „Kapitel 1 · Mahlen" */
  eyebrow: L
  /** H2 (GRIND, POUR, SIP). Verzal daje CSS, ne podatak. */
  title: L
  text: L
  cta: Link
  /** Pozadinska reč (dekor, aria-hidden), ista na oba jezika. */
  word: string
  /** Fusnota uz reč (opciono, tekstovi.md). */
  wordNote?: L
  /** Opis scene (alt postera i aria-label platna). */
  alt: L
}

export type SipCard = {
  /** Origin / Herkunft */
  label: L
  /** Where it grows / Wo er wächst */
  sub: L
  /** slug proizvoda iz products.ts */
  product: string
  /** Red ispod imena, npr. „Ethiopia · 1,950–2,200 m" (sa nelomljivim razmacima). */
  line: L
  /** Kraće ime za telefon (npr. „Pink Bourbon"). */
  shortName?: L
  /**
   * Note na kartici, tačno kao tabela SIP kartica u tekstovi.md. Bez ovoga važe note proizvoda; razlika je
   * Huila na DE („Panela" na kartici, „Panela (Vollrohrzucker)" u prodavnici).
   */
  notes?: L<string[]>
}

export type ProductKind = 'coffee' | 'gear' | 'set'

/** Filter „Brew" (Zubereitung). */
export type BrewGroup = 'espresso' | 'filter'
/** Filter „Flavor" (Geschmack). */
export type FlavorGroup = 'fruity' | 'chocolate'
/** Filter „Roast" (Röstung). Light-medium je i light i medium. */
export type RoastGroup = 'light' | 'medium' | 'medium-dark'
/** Filter „Type" (Kategorie). */
export type TypeGroup = 'coffee' | 'decaf' | 'equipment' | 'set'

/** Izbor mlevenja (tekstovi.md, 5 opcija). */
export type GrindId = 'whole' | 'espresso' | 'filter' | 'french-press' | 'moka'

export type ProductSize = {
  grams: number
  priceCents: number
}

export type Product = {
  slug: string
  kind: ProductKind
  name: L
  /** Kraće ime za telefon. */
  shortName?: L
  /** Oznaka uz ime: „House blend", „Limited lot", „Decaf". */
  tag?: L
  // --- polja kartice proizvoda (tekstovi.md); za opremu i set su prazna ---
  origin?: L
  process?: L
  variety?: L
  /** Visina u metrima; prikaz daje formatAltitude(). */
  altitude?: { min: number; max?: number }
  notes?: L<string[]>
  bestFor?: L
  roast?: L
  /** Farma ili kooperativa (fiktivna, „Farm / co-op (fictional)"). */
  farm?: L
  /** Kratak opis na kartici. */
  description: L
  /** Pakovanja za kafu i set (grami + cena u centima). Oprema ima prazan niz. */
  sizes: ProductSize[]
  /**
   * Cena opreme u centima. null = cena još nije odlučena: takav proizvod se ne prikazuje
   * (PrAG traži cenu), dok korisnik ne da cenu.
   */
  priceCents?: number | null
  // --- grupe za filtere prodavnice ---
  brew: BrewGroup[]
  flavor: FlavorGroup[]
  roastGroups: RoastGroup[]
  type: TypeGroup
  /** Ključ slike u media.ts (bags za kafu i set, gear za opremu). */
  image: string
}

/** Fotografija iz public/media/photos: `<id>-sm.webp` i `<id>-lg.webp`. */
export type PhotoEntry = {
  id: string
  sm: { src: string; width: number; height: number }
  lg: { src: string; width: number; height: number }
  alt: L
  /** Natpis uz sliku, npr. „Symbolbild" kod Kontakta. */
  caption?: L
  credit: { author: string; title?: string; url: string; license: string; licenseUrl: string }
  /** false = fajl još ne postoji: Photo crta obojenu kutiju iste razmere, bez zahteva. */
  ready: boolean
}

export type ImageSize = { src: string; width: number; height: number }

/**
 * Pun kadar i isečak u jedinicama S (stranica kvadrata kadra), od gornjeg levog ugla punog kadra.
 * Isti oblik i brojevi kao `full` i `crop` u seq.json (SeqGeometry u src/lib/sequence.ts).
 */
export type SeqMediaGeometry = {
  full: { W: number; H: number }
  crop: { x0: number; y0: number; w: number; h: number }
}

/** Sekvenca kadrova (public/media/seq/<id>), detalji su u seq.json (plan, Interfejs 4). */
export type SeqMedia = {
  id: ChapterId
  /** Osnovna putanja, npr. „/media/seq/grind". */
  base: string
  /** „/media/seq/grind/seq.json" */
  manifest: string
  /** Poster po nivou: d = desktop, m = telefon (plan, Interfejs 3). */
  poster: { d: ImageSize; m: ImageSize }
  /**
   * Geometrija pre seq.json (i u reduced motion, kad se seq.json ne traži): poster stoji na mestu
   * isečka, pa zamena prvim kadrom nema skoka. Kad seq.json stigne, važi njegov `full` i `crop`.
   */
  geometry: SeqMediaGeometry
  /** true tek kad postoji seq.json (Z2 privremeni kadrovi, kasnije pravi renderi). */
  ready: boolean
  /**
   * Isto kao `placeholder` u seq.json: true za privremene kadrove (Z2). Credits prikazuje red
   * „Until the final renders are in…" dok bar jedna sekvenca nema `placeholder: false`.
   */
  placeholder?: boolean
}

export type VideoSource = { src: string; type: string }

/** Petlja pare (public/media/steam), crna pozadina, mix-blend-mode: screen. */
export type SteamMedia = {
  /** Izvori po prelomnoj tački; prvi izvor koji pregledač ume da pusti pobeđuje (webm, pa mp4). */
  sources: { d: VideoSource[]; m: VideoSource[] }
  width: number
  height: number
  /** Rezerva: WebP kadrovi petlje (`000.webp`…). */
  frames?: { base: string; count: number; width: number; height: number }
  ready: boolean
}

/** Slika proizvoda u više širina (kese: 400 telefon, 600 kartica, 900 prodavnica). */
export type ProductImage = {
  srcs: { width: number; src: string }[]
  /** Razmera kao W / H (kese 1200×1500 → 0.8). */
  ratio: number
  alt: L
  ready: boolean
}

export type MediaManifest = {
  seq: Record<ChapterId, SeqMedia>
  steam: { pour: SteamMedia; sip: SteamMedia }
  photos: Record<string, PhotoEntry>
  bags: Record<string, ProductImage>
  gear: Record<string, ProductImage>
}

export type LegalSlug = 'impressum' | 'datenschutz' | 'agb' | 'versand' | 'widerruf' | 'cookies'

export type LegalPage = {
  slug: LegalSlug
  title: L
  /** Uvodni red „Konzept / Demo …". */
  intro: L
  /** Naslovi onoga što bi stajalo u pravom projektu (`[FEHLT]` spiskovi iz tekstovi.md). */
  items: L<string[]>
}

/** Stavka spiska pravne stranice: naslov, a umesto čipa „not in demo" demo tekst ili link na drugu stranicu. */
export type LegalEntry = {
  title: L
  /** demo tekst (npr. Versand: dostava iz prodavnice) */
  text?: L
  /** link na drugu rutu (npr. Datenschutz → /cookies) */
  href?: string
  /** onemogućeno dugme uz tekst (Widerruf: „Confirm withdrawal") */
  action?: L
}

/** LegalPage + polja stranice (src/content/legal.ts). `items` (naslovi) se pravi iz `entries`. */
export type LegalPageContent = LegalPage & {
  /** document.title, do 60 znakova; {brand} menja fill() */
  docTitle: L
  /** podnaslov ispod naslova (AGB) */
  subtitle?: L
  /** tekst stranice ispod zajedničkog legal.text (Datenschutz), ili umesto njega uz `bodyReplacesText` */
  body?: L
  /** true: `body` stoji umesto zajedničkog legal.text (Cookies) */
  bodyReplacesText?: boolean
  entries: LegalEntry[]
}
