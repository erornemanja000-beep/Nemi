const base = import.meta.env.BASE_URL

/** Responsive source set for the WebP pairs produced by scripts/fetch-photos.mjs. */
export function img(name: string, portrait = false) {
  const [sm, lg] = portrait ? [480, 900] : [828, 1920]
  return {
    src: `${base}images/${name}-lg.webp`,
    srcSet: `${base}images/${name}-sm.webp ${sm}w, ${base}images/${name}-lg.webp ${lg}w`,
  }
}
