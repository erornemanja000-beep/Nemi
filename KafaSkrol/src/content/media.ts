// Mediji u public/media (plan, Interfejs 3). Kod čita putanje SAMO odavde.
// Novi renderi: zameni folder u public/media i prebaci `ready` ovde (README, „Renderi").
// Fotografije i para: fajlovi, autori i licence iz studio/kafa-skrol/izvori.md (mediji, 23.10.2026).
// Alt tekstovi su iz tekstovi.md (dopune Z3, 1a–1d). Natpisi za stranicu Credits su u legal.ts (credits).
import type { ChapterId, MediaManifest, PhotoEntry, ProductImage, SeqMedia, SteamMedia } from './types.ts'

const UNSPLASH = { license: 'Unsplash License', licenseUrl: 'https://unsplash.com/license' }
const PEXELS = { license: 'Pexels License', licenseUrl: 'https://www.pexels.com/license/' }
/** alt="" za dekorativne fotografije (Z3: pozadine prodavnice) */
const DECOR = { en: '', de: '' }

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
    {
      en: 'A row of glass jars with clip lids, full of roasted coffee beans, on a dark background. Only the front jar is sharp.',
      de: 'Eine Reihe Gläser mit Bügelverschluss voller gerösteter Kaffeebohnen vor dunklem Hintergrund. Nur das vorderste ist scharf.',
    },
    { author: 'Clint Bustrillos', url: 'https://unsplash.com/photos/clear-glass-jar-filled-with-coffee-bean-lot-XgVHdER_fG4', ...UNSPLASH }),
  'shop-bg-1': photo('shop-bg-1', [480, 720], [900, 1350],
    // pozadina prodavnice = dekor, alt="" (Z3). Ako postane sadržaj: „A heap of roasted coffee beans on a cream
    // background." / „Ein Häufchen gerösteter Kaffeebohnen auf cremefarbenem Grund."
    DECOR,
    { author: 'Cemrecan Yurtman', url: 'https://unsplash.com/photos/a-pile-of-coffee-beans-on-a-white-background-G4RS0NGIS8I', ...UNSPLASH }),
  'shop-bg-2': photo('shop-bg-2', [828, 778], [1920, 1805],
    // pozadina prodavnice = dekor, alt="" (Z3). Ako postane sadržaj: „Roasted coffee beans scattered on a cream
    // surface, seen from above." / „Geröstete Kaffeebohnen, locker verstreut auf hellem Grund, von oben."
    DECOR,
    { author: 'Mockup Graphics', url: 'https://unsplash.com/photos/brown-coffee-beans-on-white-surface-m7ijvnNGaV0', ...UNSPLASH }),
  'onama-1': photo('onama-1', [828, 806], [1920, 1868],
    {
      en: 'Freshly roasted beans in the round cooling tray of a roaster. A steel arm stirs them over the perforated floor.',
      de: 'Frisch geröstete Bohnen im runden Kühlsieb einer Röstmaschine. Ein Rührarm aus Stahl bewegt sie über den gelochten Boden.',
    },
    { author: 'Khanh Do', url: 'https://unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-QrrFbQp085M', ...UNSPLASH }),
  'onama-2': photo('onama-2', [828, 552], [1920, 1280],
    {
      en: "Close-up of roasted beans in a roaster's cooling tray, with a steel stirring arm passing through.",
      de: 'Nahaufnahme: geröstete Bohnen im Kühlsieb einer Röstmaschine, ein Rührarm aus Stahl zieht hindurch.',
    },
    { author: 'Ichsan Chairul', url: 'https://unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-machine-iwcZmTKFo0w', ...UNSPLASH }),
  'guide-1': photo('guide-1', [828, 501], [1920, 1162],
    {
      en: 'Whole roasted beans in a white ceramic dosing cup on a black scale. A dark grinder stands next to it.',
      de: 'Ganze geröstete Bohnen in einem weißen Dosierbecher aus Keramik auf einer schwarzen Waage. Daneben steht eine dunkle Kaffeemühle.',
    },
    { author: 'User_Pascal', url: 'https://unsplash.com/photos/coffee-beans-are-being-weighed-on-a-digital-scale-dZAb0Km1ELY', ...UNSPLASH }),
  'guide-2': photo('guide-2', [828, 745], [1776, 1599],
    {
      en: 'From above: a white dripper with a pleated paper filter on a digital scale, the wet grounds blooming. Next to it, a wooden scoop of ground coffee.',
      de: 'Von oben: ein weißer Handfilter mit gefaltetem Papierfilter auf einer digitalen Waage, das nasse Kaffeemehl quillt auf. Daneben ein Holzlöffel mit Kaffeemehl.',
    },
    { author: 'Jason An', url: 'https://unsplash.com/photos/a-cup-of-coffee-sitting-on-top-of-a-scale-S9QYhiZ0tFE', ...UNSPLASH }),
  // izvor je KONTAKT-2 (odluka direktora 5): stvaran bečki lokal, zato čip „Symbolbild" (caption);
  // figcaption je sections.contact.photoCaption. EN „Illustrative photo" po Z3 (rezerva iz plana: „Symbolic image").
  'kontakt-1': photo('kontakt-1', [480, 716], [900, 1342],
    {
      en: 'An empty café courtyard in Vienna after rain: white chairs and tables, a folded striped parasol, wet paving stones.',
      de: 'Ein leerer Gastgarten in einem Wiener Innenhof nach dem Regen: weiße Stühle und Tische, ein zusammengeklappter gestreifter Sonnenschirm, nasses Pflaster.',
    },
    { author: 'Anna Holodna', url: 'https://www.pexels.com/photo/view-of-an-empty-cafe-patio-16862543/', ...PEXELS },
    { en: 'Illustrative photo', de: 'Symbolbild' }),
}

/**
 * Kese iz Blender rendera (storyboard 6): 400 telefon, 600 kartica, 900 prodavnica; render 1200×1500.
 * Šest kafa deli tri kese po boji (etiketa bez imena kafe, Z4). Ključ je `image` u products.ts:
 *   origin (terakota): Guji, Nyeri · flavor (tirkiz): Huila Pink Bourbon, Tarrazú Honey, Probierset ·
 *   roast (breskva): On Repeat, Pause. SIP kartice: Origin = Guji, Flavor = Huila, Roast = On Repeat.
 * Alt je iz Z3 (1c) i opisuje boju; na SIP kartici i kartici prodavnice ide alt="", u modalu shop.modal.imageAlt.
 * Alt opisuje pravi render (bags.py sa etiketom brenda, 24.10.2026).
 */
function bag(id: 'origin' | 'flavor' | 'roast', alt: ProductImage['alt']): ProductImage {
  return {
    // render 900 x 1125, isečen na kesu i senku (750 x 900); senka meko bledi do desne ivice
    srcs: [400, 600, 750].map((width) => ({ width, src: `/media/bags/kesa-${id}-${width}.webp` })),
    ratio: 750 / 900,
    alt,
    ready: true,
  }
}

/**
 * Opciono: mirni Blender snimci opreme (plan, Interfejs 3). Bez njih kartica crta CSS siluetu (aria-hidden).
 * Alt je iz Z3 (1d), pisan po opisu proizvoda: proveriti kad render stigne. Ako dripper stoji na bokalu,
 * kartica mora da kaže da li je bokal uključen ([FEHLT: Lieferumfang Dripper], tekstovi.md).
 */
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
function seq(id: ChapterId, poster: SeqMedia['poster'], geometry: SeqMedia['geometry']): SeqMedia {
  const base = `/media/seq/${id}`
  return { id, base, manifest: `${base}/seq.json`, poster, geometry, ready: SEQ_READY[id], placeholder: SEQ_PLACEHOLDER[id] }
}

// seq.json postoji za sve tri (Z2 privremeni kadrovi, 23.10.2026)
const SEQ_READY: Record<ChapterId, boolean> = { grind: true, pour: true, sip: true }
// isto kao `placeholder` u seq.json; pravi render (Z21) ima false, pa red o privremenim kadrovima u Credits nestaje
const SEQ_PLACEHOLDER: Record<ChapterId, boolean> = { grind: false, pour: false, sip: false }

/**
 * Pun kadar i isečak u jedinicama S (Z5), isto kao `full` i `crop` u seq.json. Pravi render koji ih
 * promeni menja i ove brojeve (SeqCanvas u dev-u upozorava kad se razlikuju).
 */
const geo = (W: number, H: number, x0: number, y0: number, w: number, h: number): SeqMedia['geometry'] => ({
  full: { W, H },
  crop: { x0, y0, w, h },
})

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
    }, geo(1, 1.25, 0.22, 0, 0.56, 1.25)),
    // poster POUR = G150, isečak 0,72 × 1 S
    pour: seq('pour', {
      d: { src: '/media/seq/pour/poster-d.webp', width: 864, height: 1200 },
      m: { src: '/media/seq/pour/poster-m.webp', width: 576, height: 800 },
    }, geo(1, 1, 0.26, 0, 0.72, 1)),
    // SIP je pravi render (Z21, scripts/pack_seq.py): poster = S64, isečak 0,80 × 0,86 S (senka ide udesno do
    // ivice kadra, pa isečak ide do 1,0 S, a senka bledi 0,80 → 1,0 S; privremeni kadrovi su imali 0,64)
    sip: seq('sip', {
      d: { src: '/media/seq/sip/d/0064.webp', width: 960, height: 1032 },
      m: { src: '/media/seq/sip/poster-m.webp', width: 640, height: 688 },
    }, geo(1, 1, 0.2, 0, 0.8, 0.86)),
  },
  steam: {
    pour: steam('steam-cup-a', 1200, 660),
    sip: steam('steam-cup-b', 1000, 626),
  },
  photos,
  bags: {
    origin: bag('origin', {
      en: 'Stand-up coffee bag, 250\u00a0g, cream with a coral-red wave label.',
      de: 'Stehende Kaffeepackung, 250\u00a0g, cremefarben mit korallenroter Wellen-Etikette.',
    }),
    flavor: bag('flavor', {
      en: 'Stand-up coffee bag, 250\u00a0g, beige with a turquoise wave label.',
      de: 'Stehende Kaffeepackung, 250\u00a0g, beige mit türkisfarbener Wellen-Etikette.',
    }),
    roast: bag('roast', {
      en: 'Stand-up coffee bag, 250\u00a0g, peach with a salmon wave label.',
      de: 'Stehende Kaffeepackung, 250\u00a0g, pfirsichfarben mit lachsfarbener Wellen-Etikette.',
    }),
  },
  gear: {
    grinder: gear('grinder', {
      en: 'Electric burr grinder in stainless steel with a glass hopper.',
      de: 'Elektrische Kaffeemühle aus Edelstahl mit Bohnenbehälter aus Glas.',
    }),
    dripper: gear('dripper', {
      en: 'Ceramic cone dripper on a glass carafe.',
      de: 'Kegelförmiger Handfilter aus Keramik auf einer Glaskanne.',
    }),
    kettle: gear('kettle', {
      en: 'Electric gooseneck kettle with a long, thin spout, on its base.',
      de: 'Elektrischer Schwanenhals-Wasserkocher mit langem, dünnem Ausguss, auf dem Sockel.',
    }),
  },
}

/** Credits: izvori snimka pare (Mixkit 43935, izvori.md). */
export const steamCredit = {
  title: 'Demonstration video of a steaming cup of coffee',
  author: 'Mixkit',
  url: 'https://mixkit.co/free-stock-video/demonstration-video-of-a-steaming-cup-of-coffee-43935/',
  /** licenca proverena na stranici klipa 23.10.2026 (izvori.md) */
  license: 'Mixkit Stock Video Free License',
  /** tekst licence na mixkit.co (isti link kao u studio/kafa-skrol/stock-video.md), proveren 23.10.2026 */
  licenseUrl: 'https://mixkit.co/license/modal/videoFree/',
}
