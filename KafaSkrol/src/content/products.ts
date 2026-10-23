// Proizvodi (tekstovi.md: 6 kafa, 3 komada opreme, Probierset). STUB iz Z1: jedna kafa i jedna oprema.
// Z11 dodaje ostale. Cene su u centima; Grundpreis se uvek računa (format.ts), nikad se ne upisuje.
import type { Product } from './types.ts'

export const products: Product[] = [
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
    sizes: [
      { grams: 250, priceCents: 1790 },
      { grams: 1000, priceCents: 6490 },
    ],
    brew: ['filter'],
    flavor: ['fruity'],
    roastGroups: ['light'],
    type: 'coffee',
    image: 'origin',
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
