// Generated from scripts/photos.json — Unsplash photos used on the site and their photographers.
export const photos = {
  "villa-cypress": { alt: "Contemporary white villa with timber accents and a lit pool at dusk", author: "Avi Werde", user: "aviwerde", id: "hHz4yrvxwlA" },
  "villa-mediterranean": { alt: "Mediterranean-style white villa under a clear blue sky", author: "Frames For Your Heart", user: "framesforyourheart", id: "mR1CIDduGLc" },
  "glass-house": { alt: "Modern glass-walled pool house beside a swimming pool", author: "Florian Schmidinger", user: "fensterschmidinger", id: "b_79nOqf95I" },
  "villa-coast": { alt: "White and grey modern villa with an infinity pool", author: "Frames For Your Heart", user: "framesforyourheart", id: "2d4lAQAlbDA" },
  "villa-render": { alt: "Modern villa with layered terraces and a pool", author: "Salman Saqib", user: "salmansaqib", id: "z6UAWpQAhXs" },
  "residence-pink": { alt: "Apartment building with glass balconies reflecting a pink sky", author: "Tobias Wilden", user: "tobiasw", id: "4453DIQWtsQ" },
  "tower-oslo": { alt: "Low-angle view of a high-rise residential tower", author: "Marlene Céline Nordvik", user: "zarlinaa", id: "5q1KnUjtjaM" },
  "living-beige": { alt: "Light living room with a beige sofa and armchair", author: "Francesca Tosolini", user: "fromitaly", id: "tHkJAMcO3QE" },
  "penthouse-dark": { alt: "Dark penthouse living room with tall windows", author: "Blvck Paris", user: "blvckparis", id: "ckBxIZmpXJE" },
  "bedroom-stair": { alt: "Penthouse bedroom with fireplace and spiral staircase", author: "KKY", user: "kkykkky", id: "h30xW8X5CP4" },
  "sea-view": { alt: "Empty room with floor-to-ceiling windows facing the sea", author: "Vangel Dimo", user: "vangeldimo", id: "qFbauOaA9UY" },
  "double-height": { alt: "Double-height living room with a sculptural chandelier", author: "Aalo Lens", user: "aalolens", id: "Ez7fz5mavj0" },
  "kitchen-marble": { alt: "Modern kitchen with marble island and bar stools", author: "Medea Dzagnidze", user: "medeadza", id: "1jy1WNfqHos" },
  "salon-chandelier": { alt: "Modern living room with a chandelier", author: "Valton Myrtaj", user: "valtonmyrtaj", id: "mmAo_lkAOiY" },
  "skyline-golden": { alt: "City skyline across the river at golden hour", author: "Mike Chavarri", user: "mikechv", id: "kZokA2VTKn4" },
  "cliffs": { alt: "Aerial view of a town on limestone cliffs above the sea", author: "Daniel R.", user: "misterjackdaniel", id: "y2HU2cdyGBg" },
  "valley": { alt: "Village in a forested mountain valley at golden hour", author: "Daniel R.", user: "misterjackdaniel", id: "2-0pjPRny4k" },
  "harbour": { alt: "Coastal town with colourful buildings by the ocean", author: "Hugh Whyte", user: "opixels", id: "KIfVGXf6Kzc" },
  "hills-night": { alt: "City lights at night with snow-capped mountains behind", author: "Venti Views", user: "ventiviews", id: "ZvMx2yxg_N0" },
  "agent-1": { alt: "Portrait of an agent in a suit holding keys", author: "Aleksandra Sapozhnikova", user: "rruprrup", id: "E5iwKLsLdyY" },
  "agent-2": { alt: "Portrait of an agent in a blue suit seated on a chair", author: "Eric Ardito", user: "ericardito", id: "MFYc1q-rV8k" },
  "agent-3": { alt: "Portrait of an agent in a grey jacket", author: "Christina @ wocintechchat.com", user: "wocintechchat", id: "0Zx1bDv5BNY" },
  "agent-4": { alt: "Portrait of an agent in a grey blazer", author: "Phạm Duy Quang", user: "phamduyquang", id: "QGr6H7pri-Q" },
} as const

export type PhotoName = keyof typeof photos

export const unsplashProfile = (user: string) => `https://unsplash.com/@${user}?utm_source=vista_estates&utm_medium=referral`
export const unsplashPhoto = (id: string) => `https://unsplash.com/photos/${id}?utm_source=vista_estates&utm_medium=referral`
