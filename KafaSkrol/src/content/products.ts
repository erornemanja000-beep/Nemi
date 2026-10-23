// Proizvodi (tekstovi.md: 6 kafa, Probierset, 3 komada opreme). Sve je izmišljeno za demo.
// Cene su u centima; Grundpreis se uvek računa (format.ts), nikad se ne upisuje.
// Nelomljivi razmak (U+00A0) ide između broja i jedinice („60 %", „250 g"); proverava check-content.ts.
// Grupe za filtere (Z9): unutar grupe „ili", između grupa „i". Huila je i light i medium (tekstovi.md, Z3 tačka 5).
// `image` je ključ kese u media.bags (kafa i set) ili opreme u media.gear; mapa kesa je u media.ts.
import type { Product } from './types.ts'

const COFFEE_SIZES = (g250: number, kg1: number) => [
  { grams: 250, priceCents: g250 },
  { grams: 1000, priceCents: kg1 },
]

const espressoFilter = { en: 'Espresso & filter', de: 'Espresso & Filter' }

export const products: Product[] = [
  {
    slug: 'on-repeat',
    kind: 'coffee',
    name: { en: 'On Repeat', de: 'On Repeat' },
    tag: { en: 'House blend', de: 'Hausmischung' },
    origin: {
      en: 'Brazil, Cerrado Mineiro 60\u00a0% + Colombia, Huila 40\u00a0%',
      de: 'Brasilien, Cerrado Mineiro 60\u00a0% + Kolumbien, Huila 40\u00a0%',
    },
    process: { en: 'Natural + washed', de: 'Natural + gewaschen' },
    // tekstovi.md: „blend" u koloni sorte; mešavina nema jednu sortu ni visinu
    variety: { en: 'Blend', de: 'Blend' },
    notes: { en: ['Milk chocolate', 'Hazelnut', 'Caramel'], de: ['Milchschokolade', 'Haselnuss', 'Karamell'] },
    bestFor: { en: 'Espresso', de: 'Espresso' },
    roast: { en: 'Medium-dark', de: 'Mittel-dunkel' },
    // nema jednu farmu (tekstovi.md)
    description: {
      en: 'Our everyday espresso. Sweet and round, made for a flat white or a Melange.',
      de: 'Unser Espresso für jeden Tag. Süß und rund, gemacht für Flat White und Melange.',
    },
    sizes: COFFEE_SIZES(1350, 4890),
    brew: ['espresso'],
    flavor: ['chocolate'],
    roastGroups: ['medium-dark'],
    type: 'coffee',
    image: 'roast',
  },
  {
    slug: 'guji',
    kind: 'coffee',
    name: { en: 'Guji', de: 'Guji' },
    origin: { en: 'Ethiopia, Oromia, Guji', de: 'Äthiopien, Oromia, Guji' },
    process: { en: 'Washed', de: 'Gewaschen' },
    variety: { en: 'Heirloom (local varieties)', de: 'Heirloom (lokale Varietäten)' },
    altitude: { min: 1950, max: 2200 },
    notes: { en: ['Jasmine', 'Bergamot', 'White peach'], de: ['Jasmin', 'Bergamotte', 'Weißer Pfirsich'] },
    bestFor: { en: 'Filter', de: 'Filter' },
    roast: { en: 'Light', de: 'Hell' },
    farm: { en: 'Tesfa Hills Cooperative', de: 'Tesfa Hills Cooperative' },
    description: {
      en: 'Floral and light, almost like tea with fruit. Our pick for the pour-over recipe.',
      de: 'Blumig und leicht, fast wie Tee mit Frucht. Unser Tipp für das Handfilter-Rezept.',
    },
    sizes: COFFEE_SIZES(1790, 6490),
    brew: ['filter'],
    flavor: ['fruity'],
    roastGroups: ['light'],
    type: 'coffee',
    image: 'origin',
  },
  {
    slug: 'nyeri',
    kind: 'coffee',
    name: { en: 'Nyeri', de: 'Nyeri' },
    origin: { en: 'Kenya, Nyeri', de: 'Kenia, Nyeri' },
    process: { en: 'Washed', de: 'Gewaschen' },
    variety: { en: 'SL28, SL34', de: 'SL28, SL34' },
    altitude: { min: 1700, max: 1900 },
    notes: {
      en: ['Blackcurrant', 'Blood orange', 'Cane sugar'],
      de: ['Schwarze Johannisbeere', 'Blutorange', 'Rohrzucker'],
    },
    bestFor: { en: 'Filter', de: 'Filter' },
    roast: { en: 'Light', de: 'Hell' },
    farm: { en: 'Kiburu Factory', de: 'Kiburu Factory' },
    description: {
      en: 'Juicy, with a clear acidity. For anyone who likes their coffee lively.',
      de: 'Saftig, mit klarer Säure. Für alle, die es lebendig mögen.',
    },
    sizes: COFFEE_SIZES(1950, 6990),
    brew: ['filter'],
    flavor: ['fruity'],
    roastGroups: ['light'],
    type: 'coffee',
    image: 'origin',
  },
  {
    slug: 'huila-pink-bourbon',
    kind: 'coffee',
    name: { en: 'Huila Pink Bourbon', de: 'Huila Pink Bourbon' },
    shortName: { en: 'Pink Bourbon', de: 'Pink Bourbon' },
    tag: { en: 'Limited lot', de: 'Limitiertes Lot' },
    origin: { en: 'Colombia, Huila', de: 'Kolumbien, Huila' },
    process: { en: 'Washed', de: 'Gewaschen' },
    variety: { en: 'Pink Bourbon', de: 'Pink Bourbon' },
    altitude: { min: 1750, max: 1850 },
    notes: {
      en: ['Hibiscus', 'Pink grapefruit', 'Panela'],
      de: ['Hibiskus', 'Rosa Grapefruit', 'Panela (Vollrohrzucker)'],
    },
    bestFor: { en: 'Filter & espresso', de: 'Filter & Espresso' },
    roast: { en: 'Light-medium', de: 'Hell-mittel' },
    farm: { en: 'Finca Tres Quebradas', de: 'Finca Tres Quebradas' },
    description: {
      en: 'A rare variety with a floral, tart finish. Small lot, while it lasts.',
      de: 'Seltene Varietät mit blumig-herbem Abgang. Kleines Lot, solange es reicht.',
    },
    sizes: COFFEE_SIZES(2600, 9390),
    brew: ['filter', 'espresso'],
    flavor: ['fruity'],
    roastGroups: ['light', 'medium'],
    type: 'coffee',
    image: 'flavor',
  },
  {
    slug: 'tarrazu-honey',
    kind: 'coffee',
    name: { en: 'Tarrazú Honey', de: 'Tarrazú Honey' },
    origin: { en: 'Costa Rica, Tarrazú', de: 'Costa Rica, Tarrazú' },
    process: { en: 'Honey', de: 'Honey' },
    variety: { en: 'Caturra, Catuaí', de: 'Caturra, Catuaí' },
    altitude: { min: 1600, max: 1800 },
    notes: { en: ['Apricot', 'Honey', 'Almond'], de: ['Marille', 'Honig', 'Mandel'] },
    bestFor: espressoFilter,
    roast: { en: 'Medium', de: 'Mittel' },
    farm: { en: 'Beneficio Cerro Azulejo', de: 'Beneficio Cerro Azulejo' },
    description: {
      en: 'Some of the fruit stays on the bean while it dries. That makes it sweet, as espresso and as filter.',
      de: 'Beim Trocknen bleibt etwas Fruchtfleisch an der Bohne. Das macht ihn süß, als Espresso und als Filter.',
    },
    sizes: COFFEE_SIZES(1850, 6690),
    brew: ['espresso', 'filter'],
    // i čokoladna grupa, zbog badema (tekstovi.md)
    flavor: ['fruity', 'chocolate'],
    roastGroups: ['medium'],
    type: 'coffee',
    image: 'flavor',
  },
  {
    slug: 'pause',
    kind: 'coffee',
    name: { en: 'Pause', de: 'Pause' },
    tag: { en: 'Decaf', de: 'Entkoffeiniert' },
    origin: { en: 'Colombia, Caldas', de: 'Kolumbien, Caldas' },
    process: { en: 'Sugarcane decaf', de: 'Zuckerrohr-Methode' },
    variety: { en: 'Castillo, Caturra', de: 'Castillo, Caturra' },
    altitude: { min: 1400, max: 1700 },
    notes: { en: ['Date', 'Milk chocolate', 'Hazelnut'], de: ['Dattel', 'Milchschokolade', 'Haselnuss'] },
    bestFor: espressoFilter,
    roast: { en: 'Medium', de: 'Mittel' },
    farm: { en: 'Kooperative Alto Caldas', de: 'Kooperative Alto Caldas' },
    description: {
      en: 'Decaffeinated with the sugarcane method. Sweet and mellow, for the cup after 6 pm.',
      de: 'Entkoffeiniert mit der Zuckerrohr-Methode. Süß und mild, für die Tasse nach 18 Uhr.',
    },
    sizes: COFFEE_SIZES(1900, 6890),
    brew: ['espresso', 'filter'],
    flavor: ['chocolate'],
    roastGroups: ['medium'],
    type: 'decaf',
    image: 'roast',
  },
  {
    // Probierset: 4 × 100 g filter kafe (tekstovi.md). Opis je tekst Probierseta bez rečenice o ceni;
    // ceo tekst sa cenom pravi sections.tastingSet.text.
    slug: 'tasting-set',
    kind: 'set',
    name: { en: 'Tasting set', de: 'Probierset' },
    description: {
      en: "Guji, Nyeri, Huila Pink Bourbon and Tarrazú Honey side by side, with a card for your notes. Brew them one after another and you'll know what you like.",
      de: 'Guji, Nyeri, Huila Pink Bourbon und Tarrazú Honey nebeneinander, mit einer Karte für deine Notizen. Brüh sie nacheinander, dann weißt du, was dir schmeckt.',
    },
    sizes: [{ grams: 400, priceCents: 2900 }],
    // set ispada kad je aktivan Brew, Flavor ili Roast filter (Z9)
    brew: [],
    flavor: [],
    roastGroups: [],
    type: 'set',
    image: 'flavor',
  },
  {
    slug: 'burr-grinder',
    kind: 'gear',
    name: { en: 'Burr Grinder', de: 'Kaffeemühle' },
    description: {
      en: 'Electric, stainless steel, glass hopper. Grinds from espresso fine to French press coarse.',
      de: 'Elektrisch, Edelstahl, Bohnenbehälter aus Glas. Mahlt von fein für Espresso bis grob für French Press.',
    },
    sizes: [],
    // [FEHLT: Preis Mühle] (tekstovi.md): bez cene se ne prikazuje (PrAG), dok korisnik ne odluči
    priceCents: null,
    brew: [],
    flavor: [],
    roastGroups: [],
    type: 'equipment',
    image: 'grinder',
  },
  {
    slug: 'ceramic-dripper',
    kind: 'gear',
    name: { en: 'Ceramic Dripper', de: 'Handfilter aus Keramik' },
    description: {
      en: 'Cone with a 60° angle, for 1–2 cups. Fits size 02 paper filters.',
      de: 'Kegelform mit 60°-Winkel, für 1–2 Tassen. Passt für Papierfilter Größe 02.',
    },
    sizes: [],
    // [FEHLT: Preis Dripper] (tekstovi.md): bez cene se ne prikazuje (PrAG), dok korisnik ne odluči
    priceCents: null,
    brew: [],
    flavor: [],
    roastGroups: [],
    type: 'equipment',
    image: 'dripper',
  },
  {
    slug: 'gooseneck-kettle',
    kind: 'gear',
    name: { en: 'Gooseneck Kettle', de: 'Schwanenhals-Wasserkocher' },
    description: {
      en: 'Electric, set to the degree. Holds 93\u00a0°C while you pour.',
      de: 'Elektrisch, gradgenau einstellbar. Hält 93\u00a0°C, während du gießt.',
    },
    sizes: [],
    priceCents: 16900,
    brew: [],
    flavor: [],
    roastGroups: [],
    type: 'equipment',
    image: 'kettle',
  },
]

/** Proizvod po slug-u (undefined za nepoznat slug). */
export function productBySlug(slug: string): Product | undefined {
  return products.find((p) => p.slug === slug)
}
