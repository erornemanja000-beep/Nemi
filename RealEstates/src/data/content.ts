// All listings, people and reviews below are fictional examples.
import type { PhotoName } from './photos'

export type Lang = 'en' | 'de'
export type L10n = Record<Lang, string>

export type PlanRoom = { x: number; y: number; w: number; h: number; label: L10n }

export type Property = {
  slug: string
  name: string
  kind: L10n
  area: string
  price: number
  size: number
  beds: number
  baths: number
  year: number
  cover: PhotoName
  gallery: PhotoName[]
  summary: L10n
  plan: PlanRoom[]
}

const room = (x: number, y: number, w: number, h: number, en: string, de: string): PlanRoom => ({ x, y, w, h, label: { en, de } })

const villaPlan = [
  room(0, 0, 46, 38, 'Living', 'Wohnen'),
  room(46, 0, 28, 38, 'Kitchen', 'Küche'),
  room(74, 0, 26, 24, 'Study', 'Arbeiten'),
  room(74, 24, 26, 14, 'Bath', 'Bad'),
  room(0, 38, 32, 32, 'Master suite', 'Hauptsuite'),
  room(32, 38, 22, 32, 'Bedroom', 'Schlafzimmer'),
  room(54, 38, 22, 32, 'Bedroom', 'Schlafzimmer'),
  room(76, 38, 24, 32, 'Terrace', 'Terrasse'),
]
const penthousePlan = [
  room(0, 0, 58, 42, 'Great room', 'Salon'),
  room(58, 0, 42, 26, 'Kitchen', 'Küche'),
  room(58, 26, 42, 16, 'Dining', 'Essen'),
  room(0, 42, 36, 28, 'Master suite', 'Hauptsuite'),
  room(36, 42, 26, 28, 'Bedroom', 'Schlafzimmer'),
  room(62, 42, 38, 28, 'Roof terrace', 'Dachterrasse'),
]
const apartmentPlan = [
  room(0, 0, 54, 40, 'Living', 'Wohnen'),
  room(54, 0, 46, 22, 'Kitchen', 'Küche'),
  room(54, 22, 46, 18, 'Bath', 'Bad'),
  room(0, 40, 50, 30, 'Bedroom', 'Schlafzimmer'),
  room(50, 40, 50, 30, 'Loggia', 'Loggia'),
]

export const properties: Property[] = [
  {
    slug: 'villa-solenne',
    name: 'Villa Solenne',
    kind: { en: 'Villa', de: 'Villa' },
    area: 'Cliffside',
    price: 4850000,
    size: 520,
    beds: 5,
    baths: 6,
    year: 2023,
    cover: 'villa-coast',
    gallery: ['villa-coast', 'sea-view', 'kitchen-marble', 'bedroom-stair'],
    summary: {
      en: 'A cliff-edge villa with an infinity pool that dissolves into the horizon. Five suites, each oriented to the sunset.',
      de: 'Eine Villa an der Klippe mit Infinity-Pool, der in den Horizont übergeht. Fünf Suiten, jede zum Sonnenuntergang ausgerichtet.',
    },
    plan: villaPlan,
  },
  {
    slug: 'aurea-penthouse',
    name: 'Aurea Penthouse',
    kind: { en: 'Penthouse', de: 'Penthouse' },
    area: 'Skyline District',
    price: 6400000,
    size: 380,
    beds: 4,
    baths: 4,
    year: 2024,
    cover: 'penthouse-dark',
    gallery: ['penthouse-dark', 'double-height', 'salon-chandelier', 'skyline-golden'],
    summary: {
      en: 'Two floors at the top of the district, a double-height salon and a 140 m² roof terrace above the city lights.',
      de: 'Zwei Etagen ganz oben, ein Salon mit doppelter Raumhöhe und eine 140 m² große Dachterrasse über den Lichtern der Stadt.',
    },
    plan: penthousePlan,
  },
  {
    slug: 'cypress-house',
    name: 'The Cypress House',
    kind: { en: 'Villa', de: 'Villa' },
    area: 'Pinewood Hills',
    price: 3200000,
    size: 410,
    beds: 4,
    baths: 5,
    year: 2021,
    cover: 'villa-cypress',
    gallery: ['villa-cypress', 'living-beige', 'kitchen-marble', 'valley'],
    summary: {
      en: 'Timber, white render and a lit pool between the pines. Quiet, private and fifteen minutes from the harbour.',
      de: 'Holz, weißer Putz und ein beleuchteter Pool zwischen Pinien. Ruhig, privat und fünfzehn Minuten vom Hafen.',
    },
    plan: villaPlan,
  },
  {
    slug: 'glasshaus',
    name: 'Glasshaus Pavilion',
    kind: { en: 'Villa', de: 'Villa' },
    area: 'Old Harbour',
    price: 2750000,
    size: 290,
    beds: 3,
    baths: 3,
    year: 2022,
    cover: 'glass-house',
    gallery: ['glass-house', 'living-beige', 'double-height', 'harbour'],
    summary: {
      en: 'A glass pavilion set around the pool, with walls that slide away entirely in summer.',
      de: 'Ein Glaspavillon rund um den Pool, dessen Wände sich im Sommer vollständig öffnen lassen.',
    },
    plan: villaPlan,
  },
  {
    slug: 'casa-blanca-mare',
    name: 'Casa Blanca Mare',
    kind: { en: 'Villa', de: 'Villa' },
    area: 'Marina Quarter',
    price: 3950000,
    size: 460,
    beds: 5,
    baths: 5,
    year: 2019,
    cover: 'villa-mediterranean',
    gallery: ['villa-mediterranean', 'villa-render', 'salon-chandelier', 'cliffs'],
    summary: {
      en: 'Whitewashed Mediterranean lines, arched loggias and a garden that steps down to the marina.',
      de: 'Weiß gekalkte mediterrane Linien, gewölbte Loggien und ein Garten, der zur Marina hinabführt.',
    },
    plan: villaPlan,
  },
  {
    slug: 'north-tower-residence',
    name: 'North Tower Residence',
    kind: { en: 'Apartment', de: 'Apartment' },
    area: 'Skyline District',
    price: 1450000,
    size: 165,
    beds: 2,
    baths: 2,
    year: 2025,
    cover: 'tower-oslo',
    gallery: ['tower-oslo', 'residence-pink', 'living-beige', 'hills-night'],
    summary: {
      en: 'A corner residence on the 31st floor with a wraparound loggia and concierge service.',
      de: 'Eine Eckwohnung im 31. Stock mit umlaufender Loggia und Concierge-Service.',
    },
    plan: apartmentPlan,
  },
]

export type Neighborhood = { name: string; photo: PhotoName; pin: [number, number]; blurb: L10n; listings: number }

export const neighborhoods: Neighborhood[] = [
  { name: 'Cliffside', photo: 'cliffs', pin: [74, 30], listings: 12, blurb: { en: 'Limestone cliffs, private coves and the longest sunsets on the coast.', de: 'Kalksteinklippen, private Buchten und die längsten Sonnenuntergänge der Küste.' } },
  { name: 'Old Harbour', photo: 'harbour', pin: [46, 58], listings: 9, blurb: { en: 'Colourful facades, fishing boats and restored captain’s houses.', de: 'Bunte Fassaden, Fischerboote und restaurierte Kapitänshäuser.' } },
  { name: 'Skyline District', photo: 'skyline-golden', pin: [30, 38], listings: 21, blurb: { en: 'Glass towers, rooftop pools and the city’s best restaurants.', de: 'Glastürme, Rooftop-Pools und die besten Restaurants der Stadt.' } },
  { name: 'Pinewood Hills', photo: 'valley', pin: [18, 16], listings: 7, blurb: { en: 'Forested ridges and modern villas a short drive from the sea.', de: 'Bewaldete Hügel und moderne Villen, nur eine kurze Fahrt vom Meer.' } },
  { name: 'Marina Quarter', photo: 'hills-night', pin: [60, 74], listings: 14, blurb: { en: 'Yacht berths, promenades and evenings that never quite end.', de: 'Liegeplätze, Promenaden und Abende, die nie ganz enden.' } },
]

export type Agent = { name: string; role: L10n; photo: PhotoName; phone: string; email: string; langs: string }

export const agents: Agent[] = [
  { name: 'Elena Marković', role: { en: 'Founding Partner', de: 'Gründungspartnerin' }, photo: 'agent-1', phone: '+00 100 200 301', email: 'elena@vista-estates.example', langs: 'EN · DE · IT' },
  { name: 'Julian Hart', role: { en: 'Head of Villas', de: 'Leiter Villen' }, photo: 'agent-2', phone: '+00 100 200 302', email: 'julian@vista-estates.example', langs: 'EN · FR' },
  { name: 'Amara Okafor', role: { en: 'Penthouse Specialist', de: 'Penthouse-Spezialistin' }, photo: 'agent-3', phone: '+00 100 200 303', email: 'amara@vista-estates.example', langs: 'EN · DE' },
  { name: 'Mai Tran', role: { en: 'Client Advisor', de: 'Kundenberaterin' }, photo: 'agent-4', phone: '+00 100 200 304', email: 'mai@vista-estates.example', langs: 'EN · VI · DE' },
]

export type Review = { quote: L10n; name: string; place: string }

export const reviews: Review[] = [
  { name: 'Sophie & Mark L.', place: 'Villa, Cliffside', quote: { en: 'They found the house before we knew we were looking for it.', de: 'Sie fanden das Haus, bevor wir wussten, dass wir danach suchten.' } },
  { name: 'Daniel K.', place: 'Penthouse, Skyline District', quote: { en: 'Discreet, fast and unusually honest about every flaw.', de: 'Diskret, schnell und ungewöhnlich ehrlich bei jedem Mangel.' } },
  { name: 'Ingrid F.', place: 'Residence, Marina Quarter', quote: { en: 'The viewing felt like a film. The paperwork felt like nothing at all.', de: 'Die Besichtigung fühlte sich an wie ein Film. Der Papierkram wie gar nichts.' } },
  { name: 'Omar & Lina S.', place: 'Villa, Pinewood Hills', quote: { en: 'Seven months of searching ended in one afternoon with Julian.', de: 'Sieben Monate Suche endeten an einem Nachmittag mit Julian.' } },
  { name: 'Clara M.', place: 'Apartment, Old Harbour', quote: { en: 'Every question answered within the hour, in German.', de: 'Jede Frage innerhalb einer Stunde beantwortet, auf Deutsch.' } },
  { name: 'Thomas B.', place: 'Villa, Cliffside', quote: { en: 'They negotiated 6% off without us ever meeting the seller.', de: 'Sie haben 6 % verhandelt, ohne dass wir den Verkäufer je trafen.' } },
  { name: 'Yuki A.', place: 'Penthouse, Skyline District', quote: { en: 'Elena knew the building’s history better than the developer.', de: 'Elena kannte die Geschichte des Gebäudes besser als der Bauträger.' } },
  { name: 'Ravi & Anna P.', place: 'Villa, Marina Quarter', quote: { en: 'Calm, precise and genuinely kind. We would buy again tomorrow.', de: 'Ruhig, präzise und wirklich freundlich. Wir würden morgen wieder kaufen.' } },
]

export const rooms: { photo: PhotoName; name: L10n }[] = [
  { photo: 'double-height', name: { en: 'The Salon', de: 'Der Salon' } },
  { photo: 'kitchen-marble', name: { en: 'The Kitchen', de: 'Die Küche' } },
  { photo: 'living-beige', name: { en: 'The Lounge', de: 'Die Lounge' } },
  { photo: 'bedroom-stair', name: { en: 'The Suite', de: 'Die Suite' } },
  { photo: 'sea-view', name: { en: 'The View', de: 'Der Ausblick' } },
]
