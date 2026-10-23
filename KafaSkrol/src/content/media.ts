// Mediji u public/media (plan, Interfejs 3). Kod čita putanje SAMO odavde.
// Novi renderi: zameni folder u public/media i prebaci `ready` ovde (README, „Renderi").
// Fotografije i para: fajlovi i licence iz studio/kafa-skrol/izvori.md (mediji, 23.10.2026).
// Alt tekstovi fotografija su privremeni opisi slike; konačne daju Z3 i Z11.
import type { ChapterId, MediaManifest, PhotoEntry, ProductImage, SeqMedia, SteamMedia } from './types.ts'

const UNSPLASH = { license: 'Unsplash License', licenseUrl: 'https://unsplash.com/license' }
const PEXELS = { license: 'Pexels License', licenseUrl: 'https://www.pexels.com/license/' }

function photo(
  id: string,
  sm: [number, number],
  lg: [number, number],
  alt: PhotoEntry['alt'],
  credit: PhotoEntry['credit'],
  caption?: PhotoEntry['caption'],
): PhotoEntry {
  const base = `/media/photos/${id}`
  return {
    id,
    sm: { src: `${base}-sm.webp`, width: sm[0], height: sm[1] },
    lg: { src: `${base}-lg.webp`, width: lg[0], height: lg[1] },
    alt,
    caption,
    credit,
    ready: true,
  }
}

const photos: Record<string, PhotoEntry> = {
  'shop-1': photo('shop-1', [480, 600], [900, 1125],
    { en: 'Glass jars filled with coffee beans', de: 'Gläser voller Kaffeebohnen' },
    { author: 'Clint Bustrillos', url: 'https://unsplash.com/photos/clear-glass-jar-filled-with-coffee-bean-lot-XgVHdER_fG4', ...UNSPLASH }),
  'shop-bg-1': photo('shop-bg-1', [480, 720], [900, 1350],
    { en: 'A pile of roasted coffee beans on a light background', de: 'Geröstete Kaffeebohnen auf hellem Grund' },
    { author: 'Cemrecan Yurtman', url: 'https://unsplash.com/photos/a-pile-of-coffee-beans-on-a-white-background-G4RS0NGIS8I', ...UNSPLASH }),
  'shop-bg-2': photo('shop-bg-2', [828, 778], [1920, 1805],
    { en: 'Coffee beans scattered on a light surface, seen from above', de: 'Verstreute Kaffeebohnen von oben' },
    { author: 'Mockup Graphics', url: 'https://unsplash.com/photos/brown-coffee-beans-on-white-surface-m7ijvnNGaV0', ...UNSPLASH }),
  'onama-1': photo('onama-1', [828, 806], [1920, 1868],
    { en: 'Freshly roasted beans turning in the cooling tray of a roaster', de: 'Frisch geröstete Bohnen im Kühlsieb eines Röstofens' },
    { author: 'Khanh Do', url: 'https://unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-QrrFbQp085M', ...UNSPLASH }),
  'onama-2': photo('onama-2', [828, 552], [1920, 1280],
    { en: 'Roasted coffee beans in a roasting machine', de: 'Geröstete Kaffeebohnen in einer Röstmaschine' },
    { author: 'Ichsan Chairul', url: 'https://unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-machine-iwcZmTKFo0w', ...UNSPLASH }),
  'guide-1': photo('guide-1', [828, 501], [1920, 1162],
    { en: 'Coffee beans being weighed on a digital scale', de: 'Kaffeebohnen auf einer digitalen Waage' },
    { author: 'User_Pascal', url: 'https://unsplash.com/photos/coffee-beans-are-being-weighed-on-a-digital-scale-dZAb0Km1ELY', ...UNSPLASH }),
  'guide-2': photo('guide-2', [828, 745], [1776, 1599],
    { en: 'A dripper on a carafe, standing on a scale', de: 'Handfilter auf einer Kanne, auf einer Waage' },
    { author: 'Jason An', url: 'https://unsplash.com/photos/a-cup-of-coffee-sitting-on-top-of-a-scale-S9QYhiZ0tFE', ...UNSPLASH }),
  // izvor je KONTAKT-2 (odluka direktora 5): stvaran bečki lokal, zato natpis „Symbolbild"
  'kontakt-1': photo('kontakt-1', [480, 716], [900, 1342],
    { en: 'Empty café courtyard in Vienna after the rain', de: 'Leerer Cafégarten in Wien nach dem Regen' },
    { author: 'Anna Holodna', url: 'https://www.pexels.com/photo/view-of-an-empty-cafe-patio-16862543/', ...PEXELS },
    { en: 'Symbolic image', de: 'Symbolbild' }),
}

/** Kese iz Blender rendera (storyboard 6): 400 telefon, 600 kartica, 900 prodavnica; render 1200×1500. */
function bag(id: 'origin' | 'flavor' | 'roast'): ProductImage {
  return {
    srcs: [400, 600, 900].map((width) => ({ width, src: `/media/bags/kesa-${id}-${width}.webp` })),
    ratio: 1200 / 1500,
    alt: { en: 'Coffee bag (demo label)', de: 'Kaffeepackung (Demo-Etikett)' },
    ready: false,
  }
}

/** Opciono: mirni Blender snimci opreme (plan, Interfejs 3). Bez njih kartica crta CSS siluetu. */
function gear(id: 'grinder' | 'dripper' | 'kettle', alt: ProductImage['alt']): ProductImage {
  return {
    srcs: [
      { width: 480, src: `/media/photos/gear-${id}-sm.webp` },
      { width: 900, src: `/media/photos/gear-${id}-lg.webp` },
    ],
    ratio: 1200 / 1500,
    alt,
    ready: false,
  }
}

/** Sekvenca kadrova; `ready` tek kad postoji seq.json (Z2, kasnije pravi renderi). */
function seq(id: ChapterId, poster: SeqMedia['poster'], ready: boolean): SeqMedia {
  const base = `/media/seq/${id}`
  return { id, base, manifest: `${base}/seq.json`, poster, ready }
}

const SEQ_READY = { grind: false, pour: false, sip: false }

/** Para: odluka direktora 4. webm je prvi izvor, mp4 drugi; A ide u POUR, B u SIP. */
function steam(name: 'steam-cup-a' | 'steam-cup-b', width: number, height: number): SteamMedia {
  const sources = [
    { src: `/media/steam/${name}.webm`, type: 'video/webm' },
    { src: `/media/steam/${name}.mp4`, type: 'video/mp4' },
  ]
  return {
    // jedna rezolucija za oba nivoa; drugi fajl za telefon se dodaje ovde, bez izmene koda
    sources: { d: sources, m: sources },
    width,
    height,
    frames: { base: `/media/steam/${name}-seq`, count: 30, width, height },
    ready: true,
  }
}

export const media: MediaManifest = {
  seq: {
    // poster GRIND = G1, predučitava ga index.html (iste putanje!)
    grind: seq('grind', {
      d: { src: '/media/seq/grind/d/0001.webp', width: 672, height: 1500 },
      m: { src: '/media/seq/grind/m/0001.webp', width: 448, height: 1000 },
    }, SEQ_READY.grind),
    // poster POUR = G150, isečak 0,72 × 1 S
    pour: seq('pour', {
      d: { src: '/media/seq/pour/poster-d.webp', width: 864, height: 1200 },
      m: { src: '/media/seq/pour/poster-m.webp', width: 576, height: 800 },
    }, SEQ_READY.pour),
    // poster SIP = S64; isečak SIP-a određuje Z2 („po probi"), dimenzije uskladiti sa seq.json
    sip: seq('sip', {
      d: { src: '/media/seq/sip/d/0064.webp', width: 1200, height: 1200 },
      m: { src: '/media/seq/sip/poster-m.webp', width: 800, height: 800 },
    }, SEQ_READY.sip),
  },
  steam: {
    pour: steam('steam-cup-a', 1200, 660),
    sip: steam('steam-cup-b', 1000, 626),
  },
  photos,
  bags: {
    origin: bag('origin'),
    flavor: bag('flavor'),
    roast: bag('roast'),
  },
  gear: {
    grinder: gear('grinder', { en: 'Burr grinder', de: 'Kaffeemühle' }),
    dripper: gear('dripper', { en: 'Ceramic dripper', de: 'Handfilter aus Keramik' }),
    kettle: gear('kettle', { en: 'Gooseneck kettle', de: 'Schwanenhals-Wasserkocher' }),
  },
}

/** Credits: izvori snimka pare (Mixkit 43935, izvori.md). */
export const steamCredit = {
  title: 'Demonstration video of a steaming cup of coffee',
  author: 'Mixkit',
  url: 'https://mixkit.co/free-stock-video/demonstration-video-of-a-steaming-cup-of-coffee-43935/',
  /** licenca proverena na stranici klipa 23.10.2026 (izvori.md) */
  license: 'Mixkit Stock Video Free License',
}
